from agno.agent import Agent

from backend.agents.base import create_model
from backend.rag.knowledge_base import create_knowledge_base


def create_destination_researcher(mcp_tools=None, knowledge=None):
    return Agent(
        name="Destination Researcher",
        role="Researches destinations using the travel MCP server and curated knowledge",
        model=create_model(),
        description=(
            "Expert travel researcher with access to MCP-served weather, country info, "
            "and Wikivoyage destination guides, plus a curated Pinecone knowledge base."
        ),
        instructions=[
            "First, search the curated knowledge base for the destination.",
            "Then call MCP tools: get_weather, country_info, search_destinations.",
            "Provide weather patterns, visa/currency notes, safety info, and best times to visit.",
            "List top attractions with brief descriptions.",
            "Keep your output structured and concise.",
        ],
        tools=[mcp_tools] if mcp_tools else [],
        knowledge=knowledge or create_knowledge_base(),
        search_knowledge=True,
        add_datetime_to_context=True,
        markdown=True,
    )
