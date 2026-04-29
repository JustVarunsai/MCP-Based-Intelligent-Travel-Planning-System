"""
MCP Resource: live FX rates as a readable URI.

URI:    travel://currency/rates
Format: JSON. Single GET — no parameters.
Backend: Frankfurter (free, no key).
"""
import httpx

from mcp_server._app import mcp
from mcp_server.config import config

FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"


@mcp.resource("travel://currency/rates", mime_type="application/json")
def currency_rates() -> str:
    """Latest FX rates with USD as the base currency."""
    try:
        resp = httpx.get(
            FRANKFURTER_URL,
            params={"base": "USD"},
            headers={"User-Agent": config.USER_AGENT},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.text
    except httpx.HTTPError as e:
        return f'{{"error": "Frankfurter request failed: {e}"}}'
