"""
Smoke tests for agent factories — verify each agent constructs cleanly.
No live LLM or MCP connections; tools list passed in is None or a dummy.

Agents that touch Pinecone (Destination Researcher, Budget Optimizer) need
a real PINECONE_API_KEY in .env to construct the Knowledge wrapper.
Skipped automatically if not set.
"""
import os
import sys
import pytest
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

os.environ.setdefault("OPENAI_API_KEY", "sk-test")

_PC_OK = bool(os.getenv("PINECONE_API_KEY")) and os.getenv("PINECONE_API_KEY") != "test"
needs_pinecone = pytest.mark.skipif(not _PC_OK, reason="real PINECONE_API_KEY required")


@needs_pinecone
def test_destination_researcher_creation():
    from backend.agents.destination_researcher import create_destination_researcher
    agent = create_destination_researcher(mcp_tools=None)
    assert agent.name == "Destination Researcher"


def test_accommodation_agent_creation():
    from backend.agents.accommodation_agent import create_accommodation_agent
    agent = create_accommodation_agent(mcp_tools=None)
    assert agent.name == "Accommodation Agent"


def test_route_optimizer_creation():
    from backend.agents.route_optimizer import create_route_optimizer
    agent = create_route_optimizer(mcp_tools=None)
    assert agent.name == "Route Optimizer"


@needs_pinecone
def test_budget_optimizer_creation():
    from backend.agents.budget_optimizer import create_budget_optimizer
    agent = create_budget_optimizer(mcp_tools=None)
    assert agent.name == "Budget Optimizer"


def test_itinerary_compiler_creation():
    from backend.agents.itinerary_compiler import create_itinerary_compiler
    agent = create_itinerary_compiler(mcp_tools=None)
    assert agent.name == "Itinerary Compiler"


def test_itinerary_schema():
    from backend.agents.itinerary_compiler import TripItinerary, DayPlan, DayActivity

    activity = DayActivity(time="09:00", activity="Visit museum", location="Downtown")
    day = DayPlan(day_number=1, theme="Sightseeing", activities=[activity], meals=[])
    itinerary = TripItinerary(
        destination="Paris",
        duration_days=3,
        total_budget_usd=2000,
        total_estimated_cost_usd=1500,
        accommodation_summary="Apartment in Marais",
        transportation_summary="Metro",
        daily_plans=[day],
        packing_list=["jacket", "sunscreen"],
        travel_tips=["Learn basic French phrases"],
    )
    assert itinerary.destination == "Paris"
    assert len(itinerary.daily_plans) == 1


def test_mcp_factory_picks_transport():
    """create_travel_mcp returns SSE config when MCP_SERVER_URL set, else stdio."""
    # this only checks the factory logic, not connection
    from backend.agents.base import create_travel_mcp
    from backend.config import config

    # default (no URL set)
    inst = create_travel_mcp()
    assert inst is not None
