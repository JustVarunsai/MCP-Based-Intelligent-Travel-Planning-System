"""
Utilities for parsing structured data from agent responses.
"""
import json
import re
from typing import Optional


def extract_json_from_text(text: str) -> Optional[dict]:
    """
    Try to find and parse a JSON object embedded in markdown or plain text.
    Handles cases where the model wraps JSON in code fences.
    """
    # try code-fenced JSON first
    pattern = r"```(?:json)?\s*(\{[\s\S]*?\})\s*```"
    match = re.search(pattern, text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # try raw JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # try to find the outermost { ... }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    return None


def extract_cost_breakdown(itinerary: dict) -> dict:
    """
    Build a cost breakdown dict from a TripItinerary-like structure.
    Returns e.g. {"Activities": 300, "Food": 200, "Transport": 150, ...}
    """
    breakdown = {}
    for day in itinerary.get("daily_plans", []):
        for act in day.get("activities", []):
            breakdown["Activities"] = breakdown.get("Activities", 0) + act.get("cost_usd", 0)
        for meal in day.get("meals", []):
            breakdown["Food"] = breakdown.get("Food", 0) + meal.get("cost_usd", 0)

    # add accommodation as remaining budget minus activity costs
    total = itinerary.get("total_estimated_cost_usd", 0)
    accounted = sum(breakdown.values())
    if total > accounted:
        breakdown["Accommodation & Other"] = round(total - accounted, 2)

    return breakdown


def extract_daily_costs(itinerary: dict) -> list:
    """
    Return a list of {"day": N, "cost": X} from structured itinerary.
    """
    return [
        {"day": d["day_number"], "cost": d.get("total_cost_usd", 0)}
        for d in itinerary.get("daily_plans", [])
    ]
