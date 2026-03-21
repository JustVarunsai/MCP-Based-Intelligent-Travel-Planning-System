from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from agents.base import create_model
from rag.knowledge_base import create_knowledge_base


def create_destination_researcher(knowledge=None):
    """
    Researches destinations using SerpAPI (live web) and the
    Pinecone knowledge base (curated travel data).
    """
    return Agent(
        name="Destination Researcher",
        role="Researches destinations using web search and curated travel knowledge",
        model=create_model(),
        description=(
            "Expert travel researcher with access to web search and a curated "
            "knowledge base of destinations, budget data, and travel tips."
        ),
        instructions=[
            "Search the knowledge base first for destination info before hitting the web",
            "Provide current weather patterns, visa requirements, safety info, and best times to visit",
            "Include cultural norms, local customs, and practical tips",
            "List the top attractions with brief descriptions",
            "Keep your output structured and concise",
        ],
        tools=[SerpApiTools()],
        knowledge=knowledge or create_knowledge_base(),
        search_knowledge=True,
        add_datetime_to_context=True,
        markdown=True,
    )
