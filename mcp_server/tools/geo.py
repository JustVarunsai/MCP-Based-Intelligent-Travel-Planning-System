from typing import Any

import httpx

from mcp_server._app import mcp
from mcp_server.config import config
from mcp_server.tools._throttle import throttle, make_lru

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "https://router.project-osrm.org/route/v1"

_OSRM_PROFILES = {"driving": "driving", "walking": "foot", "cycling": "bike"}


@make_lru()
def _geocode_cached(query: str) -> tuple[float, float, str] | None:
    throttle("nominatim")
    try:
        resp = httpx.get(
            NOMINATIM_URL,
            params={"q": query, "format": "json", "limit": 1},
            headers={"User-Agent": config.USER_AGENT},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError:
        return None
    if not data:
        return None
    r = data[0]
    return float(r["lat"]), float(r["lon"]), r.get("display_name", "")


@mcp.tool()
def geocode(query: str) -> dict[str, Any]:
    """Resolve a place name or address to latitude/longitude coordinates."""
    result = _geocode_cached(query.strip())
    if not result:
        return {"error": f"No results for '{query}'"}
    lat, lon, name = result
    return {"query": query, "latitude": lat, "longitude": lon, "display_name": name}


@mcp.tool()
def route(
    from_latitude: float,
    from_longitude: float,
    to_latitude: float,
    to_longitude: float,
    mode: str = "driving",
) -> dict[str, Any]:
    """Distance (km) and travel time (minutes) between two coordinate pairs. mode is one of driving, walking, cycling."""
    profile = _OSRM_PROFILES.get(mode, "driving")
    url = (
        f"{OSRM_URL}/{profile}/"
        f"{from_longitude},{from_latitude};{to_longitude},{to_latitude}"
    )
    throttle("osrm")
    try:
        resp = httpx.get(url, params={"overview": "false"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as e:
        return {"error": f"OSRM request failed: {e}"}
    routes = data.get("routes") or []
    if not routes:
        return {"error": "No route found"}
    r = routes[0]
    return {
        "mode": mode,
        "distance_km": round(r["distance"] / 1000, 2),
        "duration_minutes": round(r["duration"] / 60, 1),
        "from": [from_latitude, from_longitude],
        "to": [to_latitude, to_longitude],
    }
