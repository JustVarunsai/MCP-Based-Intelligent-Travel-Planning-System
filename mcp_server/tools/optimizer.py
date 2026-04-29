"""
Day-route optimizer — orders a list of stops for minimum total travel time.
Uses nearest-neighbour heuristic with optional 2-opt swap improvement.
This is a deterministic algorithm — no LLM, no external API calls.
"""
from typing import Any
from math import radians, sin, cos, asin, sqrt

from mcp_server._app import mcp


def _haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Great-circle distance between two (lat, lon) points in km."""
    lat1, lon1 = radians(a[0]), radians(a[1])
    lat2, lon2 = radians(b[0]), radians(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(h))


def _nearest_neighbour(coords: list[tuple[float, float]], start: int = 0) -> list[int]:
    """Greedy nearest-neighbour ordering of indices, starting from `start`."""
    n = len(coords)
    visited = [False] * n
    order = [start]
    visited[start] = True
    for _ in range(n - 1):
        last = order[-1]
        best = -1
        best_d = float("inf")
        for j in range(n):
            if visited[j]:
                continue
            d = _haversine_km(coords[last], coords[j])
            if d < best_d:
                best_d = d
                best = j
        order.append(best)
        visited[best] = True
    return order


def _tour_length_km(order: list[int], coords: list[tuple[float, float]]) -> float:
    return sum(
        _haversine_km(coords[order[i]], coords[order[i + 1]])
        for i in range(len(order) - 1)
    )


def _two_opt(order: list[int], coords: list[tuple[float, float]], max_iter: int = 100) -> list[int]:
    """One pass of 2-opt swap to escape local minima."""
    best = order[:]
    improved = True
    iters = 0
    while improved and iters < max_iter:
        improved = False
        iters += 1
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best)):
                if j - i == 1:
                    continue
                new = best[:i] + best[i:j][::-1] + best[j:]
                if _tour_length_km(new, coords) < _tour_length_km(best, coords) - 1e-9:
                    best = new
                    improved = True
    return best


@mcp.tool()
def optimize_day_route(
    stops: list[dict[str, Any]],
    start_index: int = 0,
) -> dict[str, Any]:
    """
    Order a list of stops to minimise total travel distance.
    Uses nearest-neighbour ordering followed by 2-opt local search.

    Args:
        stops: List of dicts, each with at least:
               {"name": str, "latitude": float, "longitude": float}
        start_index: Index of the starting stop (default 0).

    Returns:
        Dict with the input stops re-ordered, total distance (km),
        and per-leg distances. Returns input unchanged if fewer than 2 stops.
    """
    if not stops or len(stops) < 2:
        return {
            "ordered": stops,
            "total_distance_km": 0.0,
            "legs": [],
            "notes": "Need at least 2 stops to optimise.",
        }

    coords = []
    for s in stops:
        try:
            coords.append((float(s["latitude"]), float(s["longitude"])))
        except (KeyError, TypeError, ValueError):
            return {"error": "Each stop needs numeric latitude/longitude"}

    if not (0 <= start_index < len(stops)):
        start_index = 0

    nn = _nearest_neighbour(coords, start=start_index)
    final = _two_opt(nn, coords) if len(stops) >= 4 else nn

    ordered = [stops[i] for i in final]
    legs = [
        {
            "from": stops[final[i]].get("name", f"stop {final[i]}"),
            "to": stops[final[i + 1]].get("name", f"stop {final[i + 1]}"),
            "distance_km": round(_haversine_km(coords[final[i]], coords[final[i + 1]]), 2),
        }
        for i in range(len(final) - 1)
    ]
    total = round(sum(l["distance_km"] for l in legs), 2)

    return {
        "ordered": ordered,
        "total_distance_km": total,
        "legs": legs,
        "algorithm": "nearest-neighbour + 2-opt",
    }
