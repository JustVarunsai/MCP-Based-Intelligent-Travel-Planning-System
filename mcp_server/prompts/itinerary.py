"""
MCP Prompt: pre-built itinerary generation template.

Demonstrates the third MCP primitive (Prompts) — reusable parameterised
prompt templates a client can invoke.
"""
from mcp_server._app import mcp


@mcp.prompt(name="itinerary-template")
def itinerary_prompt(destination: str, days: int, budget_usd: int, preferences: str = "") -> str:
    """Reusable itinerary-generation prompt the client can fill in."""
    return (
        f"You are planning a trip to {destination} for {days} days with a budget of "
        f"${budget_usd} USD. Traveler preferences: {preferences or 'general sightseeing'}.\n\n"
        f"Use the available MCP tools to ground your answer in real data:\n"
        f"  • get_weather — for the forecast\n"
        f"  • country_info — for currency, language, visa context\n"
        f"  • search_destinations — for Wikivoyage's See/Do/Eat/Sleep guides\n"
        f"  • find_attractions — for nearby points of interest\n"
        f"  • geocode + route — for distances\n"
        f"  • optimize_day_route — to order each day's stops efficiently\n"
        f"  • convert_currency — for local-currency price displays\n"
        f"  • score_itinerary — to self-evaluate before responding\n\n"
        f"Output a structured day-by-day plan. If score_itinerary returns < 60, revise once."
    )
