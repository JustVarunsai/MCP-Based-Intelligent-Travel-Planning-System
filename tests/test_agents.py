"""
Basic tests for agent creation — verifies agents can be instantiated
without errors and have correct names/roles.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# mock API keys so constructors don't fail
os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ.setdefault("PINECONE_API_KEY", "test")
os.environ.setdefault("SERPER_API_KEY", "test")


def test_destination_researcher_creation():
    from agents.destination_researcher import create_destination_researcher
    agent = create_destination_researcher()
    assert agent.name == "Destination Researcher"


def test_accommodation_agent_creation():
    from agents.accommodation_agent import create_accommodation_agent
    agent = create_accommodation_agent()
    assert agent.name == "Accommodation Agent"


def test_route_optimizer_creation():
    from agents.route_optimizer import create_route_optimizer
    agent = create_route_optimizer()
    assert agent.name == "Route Optimizer"


def test_budget_optimizer_creation():
    from agents.budget_optimizer import create_budget_optimizer
    agent = create_budget_optimizer()
    assert agent.name == "Budget Optimizer"


def test_itinerary_compiler_creation():
    from agents.itinerary_compiler import create_itinerary_compiler
    agent = create_itinerary_compiler()
    assert agent.name == "Itinerary Compiler"


def test_itinerary_schema():
    from agents.itinerary_compiler import TripItinerary, DayPlan, DayActivity

    activity = DayActivity(time="09:00", activity="Visit museum", location="Downtown")
    day = DayPlan(day_number=1, theme="Sightseeing", activities=[activity], meals=[])
    itinerary = TripItinerary(
        destination="Paris",
        duration_days=3,
        total_budget_usd=2000,
        total_estimated_cost_usd=1500,
        accommodation_summary="Airbnb in Marais",
        transportation_summary="Metro",
        daily_plans=[day],
        packing_list=["jacket", "sunscreen"],
        travel_tips=["Learn basic French phrases"],
    )
    assert itinerary.destination == "Paris"
    assert len(itinerary.daily_plans) == 1
