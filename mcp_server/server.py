"""
Custom MCP travel server entry point.

Run locally as stdio (for `mcp inspector` or local Agno):
    python -m mcp_server.server

Run as HTTP/SSE (for cloud deploy or remote agents):
    python -m mcp_server.server --sse
"""
import argparse

from mcp_server._app import mcp
from mcp_server.config import config


def register_all() -> None:
    """Import every tool / resource / prompt module so their decorators register on `mcp`."""
    # Tools
    from mcp_server.tools import (  # noqa: F401
        weather, geo, places, country, destinations, optimizer, scorer,
    )
    # Resources
    from mcp_server.resources import currency, destinations as dest_res  # noqa: F401
    # Prompts
    from mcp_server.prompts import itinerary, comparison  # noqa: F401


def main() -> None:
    parser = argparse.ArgumentParser(description="Custom Travel MCP Server")
    parser.add_argument("--sse", action="store_true", help="Run with SSE/HTTP transport")
    parser.add_argument("--host", default=config.HOST)
    parser.add_argument("--port", type=int, default=config.PORT)
    args = parser.parse_args()

    register_all()

    if args.sse:
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
