from agno.agent import Agent
from agents.base import create_model, create_airbnb_mcp


def create_accommodation_agent():
    """
    Finds real Airbnb listings using the Airbnb MCP server.
    Returns pricing, amenities, and location info.
    Falls back to LLM knowledge if MCP fails.
    """
    tools = []
    try:
        tools.append(create_airbnb_mcp())
    except Exception:
        tools = []

    return Agent(
        name="Accommodation Agent",
        role="Finds and recommends accommodations",
        model=create_model(),
        description=(
            "Accommodation specialist with access to live Airbnb listings "
            "when available, plus knowledge of typical pricing ranges for most cities."
        ),
        instructions=[
            "Search Airbnb for options matching the destination, dates, and budget",
            "If Airbnb MCP is unavailable, suggest typical accommodation types with realistic price ranges",
            "Return at least 3 options across different price points",
            "Include property name/type, nightly rate, total cost, key amenities",
            "Note the neighbourhood and proximity to the city centre",
            "If a listing looks particularly good value, highlight that",
        ],
        tools=tools,
        markdown=True,
    )
