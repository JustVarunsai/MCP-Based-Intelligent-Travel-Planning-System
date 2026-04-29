from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="travel-mcp",
    instructions=(
        "Travel planning tool server. Provides geocoding, routing, weather, "
        "places, country info, currency conversion, destination knowledge, "
        "and itinerary scoring."
    ),
)
