"""
Route Optimizer — uses the travel MCP server's geocode / route /
optimize_day_route tools (backed by free OpenStreetMap services).
"""
from agno.agent import Agent
from backend.agents.base import create_model


def create_route_optimizer(mcp_tools=None):
    return Agent(
        name="Route Optimizer",
        role="Calculates routes and optimal visit orders via MCP geo tools",
        model=create_model(),
        description=(
            "Route planning specialist using the travel MCP server's geocoding, "
            "routing, and TSP-based daily ordering tools."
        ),
        instructions=[
            "Call geocode to resolve any place names to coordinates first.",
            "Use route(from, to, mode) for pairwise distances and durations.",
            "Use optimize_day_route(stops) when ordering 3+ stops to minimise travel time.",
            "Suggest transport mode (walking, driving, transit) per leg with rough costs.",
            "Group nearby attractions by neighbourhood to limit cross-city travel.",
        ],
        tools=[mcp_tools] if mcp_tools else [],
        markdown=True,
    )
