from agno.agent import Agent

from backend.agents.base import create_model


def create_accommodation_agent(mcp_tools=None):
    return Agent(
        name="Accommodation Agent",
        role="Recommends accommodation options for the destination and budget",
        model=create_model(),
        description=(
            "Accommodation specialist. Uses MCP search_destinations for Wikivoyage "
            "'Sleep' content and budget benchmarks for realistic pricing across tiers."
        ),
        instructions=[
            "Call search_destinations(query, sections=['Sleep']) on the MCP server "
            "to retrieve neighbourhood and stay recommendations.",
            "Cross-reference price points with regional budget benchmarks.",
            "Return at least 3 options across budget / mid-range / luxury tiers.",
            "Each option: type (hostel / apartment / hotel), neighbourhood, "
            "estimated nightly rate (USD), key amenities, why it's a good fit.",
        ],
        tools=[mcp_tools] if mcp_tools else [],
        markdown=True,
    )
