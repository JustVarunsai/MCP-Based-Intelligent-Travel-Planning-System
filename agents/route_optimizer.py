from agno.agent import Agent
from agents.base import create_model, create_google_maps_mcp
from config import config


def create_route_optimizer():
    """
    Plans routes and travel times between locations.
    If a valid Google Maps key is configured, uses the Google Maps MCP for
    live data. Otherwise falls back to LLM knowledge for estimates.
    """
    tools = []
    if config.google_maps_key:
        try:
            tools.append(create_google_maps_mcp())
        except Exception:
            tools = []

    if tools:
        desc = (
            "Route planning specialist with live Google Maps access for distance "
            "calculations, directions, and transportation recommendations."
        )
        instructions = [
            "Calculate distances and travel times between all key locations using Google Maps",
            "Suggest an optimal daily visit order to minimise travel time",
            "Provide transport options for each leg: walking, transit, taxi with costs",
            "Include specific addresses when available",
            "Flag any locations that are far apart and suggest grouping nearby spots",
        ]
    else:
        desc = (
            "Route planning specialist that estimates distances and travel times "
            "based on knowledge of the destination city and common transport options."
        )
        instructions = [
            "Estimate distances and travel times between key locations based on your knowledge",
            "Suggest an optimal daily visit order to minimise travel time",
            "Provide transport options for each leg: walking, transit, taxi with rough cost estimates",
            "Group nearby attractions together by neighbourhood",
            "Be clear that estimates are approximate",
        ]

    return Agent(
        name="Route Optimizer",
        role="Calculates routes, distances, and travel times",
        model=create_model(),
        description=desc,
        instructions=instructions,
        tools=tools,
        markdown=True,
    )
