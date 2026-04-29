import argparse

from mcp_server._app import mcp
from mcp_server.config import config


def register_all() -> None:
    from mcp_server.tools import (
        weather, geo, places, country, destinations, optimizer, scorer,
    )
    from mcp_server.resources import currency, destinations as dest_res
    from mcp_server.prompts import itinerary, comparison


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sse", action="store_true")
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
