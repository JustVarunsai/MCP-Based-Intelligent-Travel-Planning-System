from agno.agent import Agent
from agents.base import create_model, create_airbnb_mcp


def create_accommodation_agent():
    """
    Finds real Airbnb listings using the Airbnb MCP server.
    Returns pricing, amenities, and location info.
    """
    return Agent(
        name="Accommodation Agent",
        role="Finds and recommends accommodations using Airbnb MCP",
        model=create_model(),
        description=(
            "Accommodation specialist with direct access to live Airbnb "
            "listings including real pricing and availability."
        ),
        instructions=[
            "Search Airbnb for options matching the destination, dates, and budget",
            "Return at least 3 options across different price points",
            "Include property name, nightly rate, total cost, key amenities, and guest rating",
            "Note the neighbourhood and proximity to the city centre",
            "If a listing looks particularly good value, highlight that",
        ],
        tools=[create_airbnb_mcp()],
        markdown=True,
    )
