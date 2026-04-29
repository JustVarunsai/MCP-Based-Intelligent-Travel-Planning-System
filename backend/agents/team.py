"""
Assembles the 5-member travel planning team under an Orchestrator
using Agno's Team framework in coordinate mode.
"""
from agno.team.team import Team
from agno.team.mode import TeamMode
from agents.base import create_model
from agents.destination_researcher import create_destination_researcher
from agents.accommodation_agent import create_accommodation_agent
from agents.route_optimizer import create_route_optimizer
from agents.budget_optimizer import create_budget_optimizer
from agents.itinerary_compiler import create_itinerary_compiler
from rag.knowledge_base import create_knowledge_base


def create_travel_team():
    """
    Build the multi-agent travel planning team.

    The orchestrator (team leader) delegates sub-tasks to 5 specialist
    agents and then synthesises a final comprehensive response.
    """
    # share one knowledge instance so we don't duplicate Pinecone connections
    knowledge = create_knowledge_base()

    return Team(
        name="AI Travel Planner Team",
        mode=TeamMode.coordinate,
        model=create_model(),
        members=[
            create_destination_researcher(knowledge=knowledge),
            create_accommodation_agent(),
            create_route_optimizer(),
            create_budget_optimizer(knowledge=knowledge),
            create_itinerary_compiler(),
        ],
        description=(
            "You are the lead travel planning coordinator. You MUST delegate to all 5 "
            "specialist agents — destination researcher, accommodation agent, "
            "route optimizer, budget optimizer, and itinerary compiler — "
            "for every trip plan request."
        ),
        instructions=[
            "MANDATORY WORKFLOW — follow these steps for every request:",
            "1. Call Destination Researcher for destination info (weather, attractions, culture)",
            "2. Call Accommodation Agent to find stays within budget",
            "3. Call Route Optimizer to calculate distances and optimal visit order",
            "4. Call Budget Optimizer to analyse costs against regional benchmarks",
            "5. Call Itinerary Compiler last to produce the final structured day-by-day plan",
            "ALL 5 agents MUST be called — do NOT skip any of them",
            "Do not answer the user yourself — always delegate to the specialists",
            "Return the Itinerary Compiler's final output as the response",
        ],
        # streaming config
        stream_member_events=True,
        share_member_interactions=True,
        add_datetime_to_context=True,
        markdown=True,
    )
