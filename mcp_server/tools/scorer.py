"""
Itinerary scorer — deterministic, computable rubric (NO LLM-as-judge).

Scores an itinerary 0–100 across six criteria:
  1. Geographic coherence — sum of haversine distances between consecutive stops.
  2. Time feasibility    — sum(activity_minutes) per day <= waking_hours.
  3. Budget adherence    — actual_cost vs target; quadratic penalty for over-budget.
  4. Diversity           — Shannon entropy across activity categories.
  5. Pacing              — variance of daily activity counts.
  6. Opening-hours       — % of activities with non-empty opening_hours info.

This is intentionally a closed-form scorer — no calls to LLM, no calls to APIs.
Every criterion is unit-testable.
"""
from typing import Any
from math import log, sqrt

from mcp_server._app import mcp
from mcp_server.tools.optimizer import _haversine_km


def _coherence_score(daily_plans: list[dict]) -> tuple[float, dict]:
    """Lower total inter-stop distance = better. Normalised by # stops."""
    total_km = 0.0
    legs = 0
    for day in daily_plans:
        coords = []
        for act in day.get("activities", []) or []:
            lat = act.get("latitude")
            lon = act.get("longitude")
            if lat is not None and lon is not None:
                coords.append((float(lat), float(lon)))
        for i in range(len(coords) - 1):
            total_km += _haversine_km(coords[i], coords[i + 1])
            legs += 1
    avg_leg = (total_km / legs) if legs else 0.0
    # 0 km/leg → 100; 5 km/leg → 50; 10+ km/leg → 0
    score = max(0.0, min(100.0, 100 - (avg_leg / 10) * 100))
    return score, {"total_km": round(total_km, 2), "avg_leg_km": round(avg_leg, 2), "legs": legs}


def _feasibility_score(daily_plans: list[dict], waking_hours: float = 14.0) -> tuple[float, dict]:
    """Sum of activity_minutes for each day must fit within waking_hours."""
    flagged_days = 0
    for day in daily_plans:
        total_min = sum(int(a.get("duration_minutes", 60) or 60) for a in (day.get("activities") or []))
        if total_min > waking_hours * 60:
            flagged_days += 1
    if not daily_plans:
        return 0.0, {"flagged_days": 0, "total_days": 0}
    pct_ok = 1 - (flagged_days / len(daily_plans))
    return pct_ok * 100, {"flagged_days": flagged_days, "total_days": len(daily_plans)}


def _budget_score(estimated_cost: float, target_budget: float) -> tuple[float, dict]:
    """100 if within budget, quadratic penalty for overrun, soft penalty for >20% under."""
    if target_budget <= 0:
        return 50.0, {"reason": "no target budget"}
    ratio = estimated_cost / target_budget
    if ratio <= 1.0:
        score = 100 - max(0, (0.8 - ratio) * 50)  # mild penalty for >20% under
    else:
        score = max(0, 100 - ((ratio - 1) ** 2) * 200)
    return score, {"estimated": estimated_cost, "target": target_budget, "ratio": round(ratio, 2)}


def _diversity_score(daily_plans: list[dict]) -> tuple[float, dict]:
    """Shannon entropy over activity categories — higher = more varied."""
    counts: dict[str, int] = {}
    for day in daily_plans:
        for act in (day.get("activities") or []):
            kind = (act.get("kind") or act.get("category") or "general").lower()
            counts[kind] = counts.get(kind, 0) + 1
    total = sum(counts.values())
    if total == 0:
        return 0.0, {"unique_kinds": 0}
    if len(counts) <= 1:
        # only one category → zero diversity
        return 0.0, {"unique_kinds": len(counts)}
    entropy = -sum((c / total) * log(c / total) for c in counts.values())
    max_entropy = log(min(len(counts), total))
    score = (entropy / max_entropy * 100) if max_entropy > 0 else 0.0
    return score, {"unique_kinds": len(counts), "entropy": round(entropy, 3)}


def _pacing_score(daily_plans: list[dict]) -> tuple[float, dict]:
    """Low variance of daily activity counts = better pacing."""
    counts = [len(d.get("activities") or []) for d in daily_plans]
    if not counts:
        return 0.0, {}
    mean = sum(counts) / len(counts)
    if mean == 0:
        return 0.0, {"counts": counts}
    var = sum((c - mean) ** 2 for c in counts) / len(counts)
    stdev_norm = sqrt(var) / mean  # coefficient of variation
    score = max(0.0, min(100.0, 100 - stdev_norm * 100))
    return score, {"counts": counts, "stdev_norm": round(stdev_norm, 3)}


def _opening_hours_score(daily_plans: list[dict]) -> tuple[float, dict]:
    """% of activities that include opening hours info."""
    total = 0
    with_hours = 0
    for day in daily_plans:
        for act in (day.get("activities") or []):
            total += 1
            if act.get("opening_hours") or act.get("hours"):
                with_hours += 1
    if total == 0:
        return 0.0, {"total": 0}
    return (with_hours / total) * 100, {"with_hours": with_hours, "total": total}


@mcp.tool()
def score_itinerary(itinerary: dict[str, Any]) -> dict[str, Any]:
    """
    Score an itinerary 0–100 across six deterministic criteria.

    Args:
        itinerary: Dict matching the TripItinerary schema.
                   Required: daily_plans (list).
                   Optional: total_estimated_cost_usd, total_budget_usd.

    Returns:
        Dict with overall score, per-criterion sub-scores, and a list of issues.
    """
    daily_plans = itinerary.get("daily_plans") or []
    target = float(itinerary.get("total_budget_usd") or 0)
    estimated = float(itinerary.get("total_estimated_cost_usd") or 0)

    coh_score, coh_meta = _coherence_score(daily_plans)
    fea_score, fea_meta = _feasibility_score(daily_plans)
    bud_score, bud_meta = _budget_score(estimated, target)
    div_score, div_meta = _diversity_score(daily_plans)
    pac_score, pac_meta = _pacing_score(daily_plans)
    oh_score, oh_meta = _opening_hours_score(daily_plans)

    weights = {
        "coherence": 0.20,
        "feasibility": 0.25,
        "budget": 0.20,
        "diversity": 0.10,
        "pacing": 0.15,
        "opening_hours": 0.10,
    }
    overall = (
        coh_score * weights["coherence"]
        + fea_score * weights["feasibility"]
        + bud_score * weights["budget"]
        + div_score * weights["diversity"]
        + pac_score * weights["pacing"]
        + oh_score * weights["opening_hours"]
    )

    issues = []
    if fea_meta.get("flagged_days"):
        issues.append(f"{fea_meta['flagged_days']} day(s) over the waking-hour budget")
    if bud_meta.get("ratio", 1) > 1.1:
        issues.append(f"Estimated cost {bud_meta['ratio']}x target budget")
    if coh_meta.get("avg_leg_km", 0) > 8:
        issues.append("Stops are spread out — consider tighter clusters")

    return {
        "overall_score": round(overall, 1),
        "verdict": (
            "excellent" if overall >= 80
            else "good" if overall >= 65
            else "ok" if overall >= 50
            else "needs revision"
        ),
        "weights": weights,
        "criteria": {
            "coherence": {"score": round(coh_score, 1), **coh_meta},
            "feasibility": {"score": round(fea_score, 1), **fea_meta},
            "budget": {"score": round(bud_score, 1), **bud_meta},
            "diversity": {"score": round(div_score, 1), **div_meta},
            "pacing": {"score": round(pac_score, 1), **pac_meta},
            "opening_hours": {"score": round(oh_score, 1), **oh_meta},
        },
        "issues": issues,
    }
