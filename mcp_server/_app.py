"""
Shared FastMCP instance.

All tool / resource / prompt modules import `mcp` from here and attach via decorators.
This avoids circular imports between `server.py` and the tool modules.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="travel-mcp",
    instructions=(
        "Travel planning tool server. Provides geocoding, routing, weather, "
        "places, country info, currency conversion, destination knowledge, "
        "and itinerary scoring. All backed by free public APIs."
    ),
)
