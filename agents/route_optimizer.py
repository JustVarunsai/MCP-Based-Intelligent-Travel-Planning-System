from agno.agent import Agent
from agents.base import create_model, create_google_maps_mcp


def create_route_optimizer():
    """
    Uses Google Maps MCP to calculate distances, travel times,
    and suggest optimal visit orders.
    """
    return Agent(
        name="Route Optimizer",
        role="Calculates routes, distances, and travel times using Google Maps MCP",
        model=create_model(),
        description=(
            "Route planning specialist with Google Maps access for distance "
            "calculations, directions, and transportation recommendations."
        ),
        instructions=[
            "Calculate distances and travel times between all key locations",
            "Suggest an optimal daily visit order to minimise travel time",
            "Provide transport options for each leg: walking, transit, taxi with costs",
            "Include specific addresses when available",
            "Flag any locations that are far apart and suggest grouping nearby spots",
        ],
        tools=[create_google_maps_mcp()],
        markdown=True,
    )
