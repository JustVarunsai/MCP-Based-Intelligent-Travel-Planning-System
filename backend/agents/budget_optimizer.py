from agno.agent import Agent
from agents.base import create_model
from rag.knowledge_base import create_knowledge_base


def create_budget_optimizer(knowledge=None):
    """
    Analyses trip costs against regional benchmarks from the
    knowledge base and suggests ways to stay on budget.
    """
    return Agent(
        name="Budget Optimizer",
        role="Optimizes trip budget using cost benchmarks from the knowledge base",
        model=create_model(),
        description=(
            "Budget analyst with access to regional cost-of-living benchmarks "
            "and pricing data for accommodation, food, and transport."
        ),
        instructions=[
            "Search the knowledge base for budget benchmarks for the destination region",
            "Break down costs into categories: accommodation, food, transport, activities, misc",
            "Compare the user's budget against regional averages",
            "Suggest specific money-saving tips for this destination",
            "Flag if the budget is unrealistic and recommend adjustments",
            "Always show costs in USD with local currency equivalents when useful",
        ],
        knowledge=knowledge or create_knowledge_base(),
        search_knowledge=True,
        markdown=True,
    )
