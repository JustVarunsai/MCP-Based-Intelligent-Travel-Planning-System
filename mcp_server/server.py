"""
Custom MCP travel server.

Run locally (stdio for testing with `mcp inspector`):
    python -m mcp_server.server

Run as HTTP/SSE for cloud deploy or remote access:
    python -m mcp_server.server --sse
"""
import argparse
import sys
from mcp.server.fastmcp import FastMCP

from mcp_server.config import config

# create the FastMCP server instance — tools/resources/prompts attach via decorators
mcp = FastMCP(
    name="travel-mcp",
    instructions=(
        "Travel planning tool server. Provides geocoding, routing, weather, "
        "places, country info, currency conversion, destination knowledge, "
        "and itinerary scoring. All backed by free public APIs."
    ),
)


def register_all() -> None:
    """Wire up tools, resources, and prompts. Imports trigger @mcp.tool() decorators."""
    # placeholder — phase 2 will add weather; phase 4 fills the rest
    from mcp_server.tools import weather  # noqa: F401


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sse", action="store_true", help="Run with SSE/HTTP transport")
    parser.add_argument("--host", default=config.HOST)
    parser.add_argument("--port", type=int, default=config.PORT)
    args = parser.parse_args()

    register_all()

    if args.sse:
        # FastMCP runs SSE on /sse; configurable host/port
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
