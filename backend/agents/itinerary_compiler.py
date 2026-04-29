from typing import List, Optional
from pydantic import BaseModel
from agno.agent import Agent
from agents.base import create_model


# ── structured output schemas ────────────────────────────────────

class DayActivity(BaseModel):
    time: str
    activity: str
    location: str
    address: Optional[str] = None
    duration_minutes: int = 60
    cost_usd: float = 0
    notes: Optional[str] = None


class DayPlan(BaseModel):
    day_number: int
    date: Optional[str] = None
    theme: str
    activities: List[DayActivity]
    meals: List[DayActivity]
    total_cost_usd: float = 0


class TripItinerary(BaseModel):
    destination: str
    duration_days: int
    total_budget_usd: float
    total_estimated_cost_usd: float
    accommodation_summary: str
    transportation_summary: str
    daily_plans: List[DayPlan]
    packing_list: List[str]
    travel_tips: List[str]


# ── agent factory ────────────────────────────────────────────────

def create_itinerary_compiler():
    """
    Takes outputs from all other agents and compiles them
    into a structured day-by-day travel itinerary.
    """
    return Agent(
        name="Itinerary Compiler",
        role="Compiles all research into a structured, detailed itinerary",
        model=create_model(),
        description=(
            "Master itinerary compiler that synthesises accommodation, route, "
            "budget, and research data into a polished day-by-day travel plan."
        ),
        instructions=[
            "Combine all team member outputs into a coherent day-by-day plan",
            "Ensure timings are realistic — include buffer time between activities",
            "Keep the daily cost total consistent with the overall budget",
            "Generate a packing list based on the destination climate and activities",
            "Add practical travel tips at the end",
            "Output must follow the TripItinerary schema exactly",
        ],
        output_schema=TripItinerary,
        markdown=True,
    )
