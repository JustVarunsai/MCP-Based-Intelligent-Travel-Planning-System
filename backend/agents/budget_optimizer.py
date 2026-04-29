from agno.agent import Agent

from backend.agents.base import create_model
from backend.rag.knowledge_base import create_knowledge_base


def create_budget_optimizer(mcp_tools=None, knowledge=None):
    return Agent(
        name="Budget Optimizer",
        role="Optimises trip budget using regional benchmarks and currency conversion",
        model=create_model(),
        description=(
            "Budget analyst with regional cost-of-living benchmarks (RAG) and "
            "live currency conversion (MCP)."
        ),
        instructions=[
            "Search the knowledge base for budget benchmarks for the destination region.",
            "Break down costs into: accommodation, food, transport, activities, misc.",
            "Compare the user's budget against regional averages.",
            "Use convert_currency to show local-currency equivalents where helpful.",
            "Suggest concrete money-saving tips for this destination.",
            "Flag if the budget is unrealistic and recommend adjustments.",
        ],
        tools=[mcp_tools] if mcp_tools else [],
        knowledge=knowledge or create_knowledge_base(),
        search_knowledge=True,
        markdown=True,
    )
