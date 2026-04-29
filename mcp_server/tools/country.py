"""
Country information + currency conversion tools.
- REST Countries: country facts (capital, currency, languages, timezones).
- Frankfurter: live FX rates (no key required).
"""
from typing import Any

import httpx

from mcp_server._app import mcp
from mcp_server.config import config

REST_COUNTRIES_URL = "https://restcountries.com/v3.1"
FRANKFURTER_URL = "https://api.frankfurter.dev/v1"


@mcp.tool()
def country_info(name_or_code: str) -> dict[str, Any]:
    """
    Look up basic country information.

    Args:
        name_or_code: Common name (e.g. "France") or ISO 2/3 code (e.g. "FR", "FRA").

    Returns:
        Dict with capital, currencies, languages, timezones, region, population, flag.
    """
    q = name_or_code.strip()
    endpoint = "alpha" if len(q) in (2, 3) and q.isalpha() else "name"
    try:
        resp = httpx.get(
            f"{REST_COUNTRIES_URL}/{endpoint}/{q}",
            headers={"User-Agent": config.USER_AGENT},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as e:
        return {"error": f"REST Countries request failed: {e}"}

    if not data:
        return {"error": f"No country found for '{name_or_code}'"}
    c = data[0] if isinstance(data, list) else data

    currencies = c.get("currencies") or {}
    return {
        "name": (c.get("name") or {}).get("common"),
        "official_name": (c.get("name") or {}).get("official"),
        "capital": (c.get("capital") or [None])[0],
        "region": c.get("region"),
        "subregion": c.get("subregion"),
        "languages": list((c.get("languages") or {}).values()),
        "currencies": [
            {"code": code, "name": v.get("name"), "symbol": v.get("symbol")}
            for code, v in currencies.items()
        ],
        "timezones": c.get("timezones") or [],
        "population": c.get("population"),
        "flag": c.get("flag"),
        "calling_code": (
            f"{(c.get('idd') or {}).get('root', '')}"
            f"{((c.get('idd') or {}).get('suffixes') or [''])[0]}"
        ),
    }


@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict[str, Any]:
    """
    Convert an amount from one currency to another using live FX rates.

    Args:
        amount: Numeric amount to convert.
        from_currency: 3-letter ISO code (e.g. "USD").
        to_currency: 3-letter ISO code (e.g. "EUR").

    Returns:
        Dict with converted amount, rate, and date.
    """
    fc = from_currency.upper().strip()
    tc = to_currency.upper().strip()
    if fc == tc:
        return {"amount": amount, "from": fc, "to": tc, "converted": amount, "rate": 1.0}
    try:
        resp = httpx.get(
            f"{FRANKFURTER_URL}/latest",
            params={"base": fc, "symbols": tc, "amount": amount},
            headers={"User-Agent": config.USER_AGENT},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as e:
        return {"error": f"Frankfurter request failed: {e}"}

    rates = data.get("rates") or {}
    converted = rates.get(tc)
    if converted is None:
        return {"error": f"No rate for {fc}->{tc}"}

    return {
        "amount": amount,
        "from": fc,
        "to": tc,
        "converted": round(converted, 4),
        "rate": round(converted / amount, 6) if amount else None,
        "date": data.get("date"),
    }
