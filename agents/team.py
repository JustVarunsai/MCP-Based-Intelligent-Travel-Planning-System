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
            "You are the lead travel planning coordinator. You manage a team of "
            "5 specialist agents — a destination researcher, accommodation finder, "
            "route optimizer, budget analyst, and itinerary compiler. "
            "Delegate tasks to the right specialists, then compile the final answer."
        ),
        instructions=[
            "1. Send destination + preferences to the Destination Researcher",
            "2. Send accommodation requirements to the Accommodation Agent",
            "3. Once you have key locations, send them to the Route Optimizer",
            "4. Send budget + destination info to the Budget Optimizer for cost analysis",
            "5. Finally, send ALL gathered data to the Itinerary Compiler for the structured plan",
            "Always delegate to the relevant members instead of answering yourself",
            "Synthesise all member outputs into a well-formatted final answer",
        ],
        # streaming config
        stream_member_events=True,
        share_member_interactions=True,
        add_datetime_to_context=True,
        markdown=True,
    )
