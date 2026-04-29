from agno.team.team import Team
from agno.team.mode import TeamMode

from backend.agents.base import create_model
from backend.agents.destination_researcher import create_destination_researcher
from backend.agents.accommodation_agent import create_accommodation_agent
from backend.agents.route_optimizer import create_route_optimizer
from backend.agents.budget_optimizer import create_budget_optimizer
from backend.agents.itinerary_compiler import create_itinerary_compiler
from backend.rag.knowledge_base import create_knowledge_base


def create_travel_team(mcp_tools=None):
    knowledge = create_knowledge_base()

    return Team(
        name="AI Travel Planner Team",
        mode=TeamMode.coordinate,
        model=create_model(),
        members=[
            create_destination_researcher(mcp_tools=mcp_tools, knowledge=knowledge),
            create_accommodation_agent(mcp_tools=mcp_tools),
            create_route_optimizer(mcp_tools=mcp_tools),
            create_budget_optimizer(mcp_tools=mcp_tools, knowledge=knowledge),
            create_itinerary_compiler(mcp_tools=mcp_tools),
        ],
        description=(
            "You are the lead travel planning coordinator. You MUST delegate to all 5 "
            "specialist agents - destination researcher, accommodation, route optimizer, "
            "budget optimizer, and itinerary compiler - for every trip plan request."
        ),
        instructions=[
            "MANDATORY WORKFLOW - follow these steps for every request:",
            "1. Destination Researcher → destination info (weather, attractions, culture)",
            "2. Accommodation Agent → stays within budget",
            "3. Route Optimizer → distances and optimal visit order",
            "4. Budget Optimizer → cost analysis vs regional benchmarks",
            "5. Itinerary Compiler → final structured day-by-day plan (self-scored)",
            "ALL 5 agents MUST be called - do NOT skip any.",
            "Do not answer the user yourself - always delegate.",
            "Return the Itinerary Compiler's final output as the response.",
        ],
        stream_member_events=True,
        share_member_interactions=True,
        add_datetime_to_context=True,
        markdown=True,
    )
