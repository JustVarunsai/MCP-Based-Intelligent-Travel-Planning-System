"""
Places tool — find tourist attractions and amenities near a coordinate
using the OpenStreetMap Overpass API. No key required.
"""
from typing import Any

import httpx

from mcp_server._app import mcp
from mcp_server.config import config
from mcp_server.tools._throttle import throttle

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


@mcp.tool()
def find_attractions(
    latitude: float,
    longitude: float,
    radius_m: int = 1500,
    limit: int = 25,
) -> dict[str, Any]:
    """
    Find tourist attractions within a radius of a coordinate.

    Categories included: tourism (attraction/museum/viewpoint/gallery/artwork),
    historic, and amenity=place_of_worship.

    Args:
        latitude, longitude: Center point.
        radius_m: Search radius in metres. Default 1500.
        limit: Maximum attractions to return (default 25, hard cap 100).

    Returns:
        Dict with center coords, radius, and a list of attractions
        (name, latitude, longitude, kind, tags).
    """
    radius_m = max(100, min(10000, int(radius_m)))
    limit = max(1, min(100, int(limit)))

    query = f"""
    [out:json][timeout:15];
    (
      node(around:{radius_m},{latitude},{longitude})["tourism"~"attraction|museum|viewpoint|gallery|artwork|zoo|theme_park"];
      node(around:{radius_m},{latitude},{longitude})["historic"];
      node(around:{radius_m},{latitude},{longitude})["amenity"="place_of_worship"];
    );
    out center {limit};
    """.strip()

    throttle("overpass", min_gap=2.0)
    try:
        resp = httpx.post(
            OVERPASS_URL,
            data={"data": query},
            headers={"User-Agent": config.USER_AGENT},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as e:
        return {"error": f"Overpass request failed: {e}"}

    attractions = []
    for el in (data.get("elements") or [])[:limit]:
        tags = el.get("tags") or {}
        name = tags.get("name") or tags.get("name:en")
        if not name:
            continue
        kind = (
            tags.get("tourism")
            or tags.get("historic")
            or tags.get("amenity")
            or "attraction"
        )
        attractions.append({
            "name": name,
            "latitude": el.get("lat") or (el.get("center") or {}).get("lat"),
            "longitude": el.get("lon") or (el.get("center") or {}).get("lon"),
            "kind": kind,
            "wikidata": tags.get("wikidata"),
            "wikipedia": tags.get("wikipedia"),
            "opening_hours": tags.get("opening_hours"),
        })

    return {
        "center": {"latitude": latitude, "longitude": longitude},
        "radius_m": radius_m,
        "count": len(attractions),
        "attractions": attractions,
    }
