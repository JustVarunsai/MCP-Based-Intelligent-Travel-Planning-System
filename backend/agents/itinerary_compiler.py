from agno.agent import Agent

from backend.agents.base import create_model


def create_itinerary_compiler(mcp_tools=None):
    return Agent(
        name="Itinerary Compiler",
        role="Synthesises team outputs into a polished day-by-day plan",
        model=create_model(),
        description=(
            "Master itinerary compiler. Combines accommodation, route, budget, "
            "and research data into a polished day-by-day markdown plan."
        ),
        instructions=[
            "Combine all team member outputs into a coherent day-by-day plan.",
            "Use clear markdown headings: Day 1, Day 2, etc. Each day has Morning, Afternoon, Evening sections.",
            "Include realistic timings with buffer time between activities.",
            "Keep the daily cost total consistent with the overall budget.",
            "Add a Packing List section and a Travel Tips section at the end.",
            "Be concise - do NOT repeat instructions or include meta-commentary.",
            "Output the plan only, no preamble.",
        ],
        tools=[mcp_tools] if mcp_tools else [],
        markdown=True,
    )
