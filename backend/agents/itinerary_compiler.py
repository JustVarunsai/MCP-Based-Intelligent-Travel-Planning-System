"""
Itinerary Compiler — synthesises team outputs into a structured day-by-day plan
matching the TripItinerary Pydantic schema. Self-evaluates with score_itinerary.
"""
from typing import List, Optional
from pydantic import BaseModel
from agno.agent import Agent
from backend.agents.base import create_model


# ── structured output schema ───────────────────────────────────

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


def create_itinerary_compiler(mcp_tools=None):
    return Agent(
        name="Itinerary Compiler",
        role="Synthesises team outputs into a structured day-by-day plan",
        model=create_model(),
        description=(
            "Master itinerary compiler. Combines accommodation, route, budget, "
            "and research data into a polished plan and self-evaluates with "
            "score_itinerary before finalising."
        ),
        instructions=[
            "Combine all team member outputs into a coherent day-by-day plan.",
            "Ensure timings are realistic — include buffer time between activities.",
            "Keep the daily cost total consistent with the overall budget.",
            "Generate a packing list based on destination climate and activities.",
            "Add practical travel tips at the end.",
            "Call score_itinerary on the MCP server to self-evaluate. Revise once if score < 60.",
            "Output must follow the TripItinerary schema exactly.",
        ],
        tools=[mcp_tools] if mcp_tools else [],
        output_schema=TripItinerary,
        markdown=True,
    )
