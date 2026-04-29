from typing import Any

import httpx

from mcp_server._app import mcp
from mcp_server.config import config

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


@mcp.tool()
def get_weather(latitude: float, longitude: float, days: int = 7) -> dict[str, Any]:
    """Daily weather forecast for the given coordinates. days is 1-16, default 7. Returns daily max/min temperature in C and precipitation in mm."""
    if not (-90 <= latitude <= 90):
        return {"error": f"latitude {latitude} out of range"}
    if not (-180 <= longitude <= 180):
        return {"error": f"longitude {longitude} out of range"}
    days = max(1, min(16, int(days)))

    try:
        resp = httpx.get(
            OPEN_METEO_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "forecast_days": days,
                "timezone": "auto",
            },
            headers={"User-Agent": config.USER_AGENT},
            timeout=10,
        )
        resp.raise_for_status()
        payload = resp.json()
    except httpx.HTTPError as e:
        return {"error": f"Open-Meteo request failed: {e}"}

    daily = payload.get("daily", {}) or {}
    dates = daily.get("time", []) or []
    tmax = daily.get("temperature_2m_max", []) or []
    tmin = daily.get("temperature_2m_min", []) or []
    rain = daily.get("precipitation_sum", []) or []

    if dates:
        avg_high = sum(tmax) / len(tmax) if tmax else 0
        avg_low = sum(tmin) / len(tmin) if tmin else 0
        rainy = sum(1 for v in rain if (v or 0) >= 1.0)
        summary = (
            f"{days}-day forecast: avg high {avg_high:.1f}°C, avg low {avg_low:.1f}°C, "
            f"{rainy} rainy day(s)."
        )
    else:
        summary = "No forecast data returned."

    return {
        "latitude": payload.get("latitude", latitude),
        "longitude": payload.get("longitude", longitude),
        "timezone": payload.get("timezone", "auto"),
        "summary": summary,
        "daily": [
            {
                "date": d,
                "temp_max_c": tmax[i] if i < len(tmax) else None,
                "temp_min_c": tmin[i] if i < len(tmin) else None,
                "precipitation_mm": rain[i] if i < len(rain) else None,
            }
            for i, d in enumerate(dates)
        ],
    }
