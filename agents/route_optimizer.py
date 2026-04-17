from agno.agent import Agent
from agents.base import create_model
from agents.tools.openstreetmap import OpenStreetMapTools


def create_route_optimizer():
    """
    Plans routes and travel times using free OpenStreetMap services.
    Uses Nominatim for geocoding and OSRM for routing. No API keys needed.
    """
    return Agent(
        name="Route Optimizer",
        role="Calculates routes, distances, and travel times using OpenStreetMap",
        model=create_model(),
        description=(
            "Route planning specialist with free OpenStreetMap access for distance "
            "calculations, directions, and transportation recommendations."
        ),
        instructions=[
            "Use the route tool to calculate distance and travel time between locations",
            "Use the distance_matrix tool when you need to compare many locations at once for optimal ordering",
            "Use the geocode tool to get coordinates or verify addresses",
            "Suggest an optimal daily visit order to minimise total travel time",
            "Provide transport options (walking, driving, public transit) with estimated costs",
            "Group nearby attractions together by neighbourhood",
            "Include specific addresses from geocoding results",
        ],
        tools=[OpenStreetMapTools()],
        markdown=True,
    )
