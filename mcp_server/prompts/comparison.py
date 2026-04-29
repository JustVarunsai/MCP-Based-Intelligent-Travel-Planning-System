from mcp_server._app import mcp


@mcp.prompt(name="destination-comparison")
def comparison_prompt(destination_a: str, destination_b: str, criteria: str = "cost,weather,activities") -> str:
    """Reusable destination-vs-destination comparison prompt."""
    return (
        f"Compare {destination_a} and {destination_b} as travel destinations across "
        f"the following criteria: {criteria}.\n\n"
        f"For each criterion, use the relevant MCP tools:\n"
        f"  • cost - country_info + search_destinations + convert_currency\n"
        f"  • weather - get_weather (use today's date)\n"
        f"  • activities - find_attractions for each city center\n\n"
        f"Output a side-by-side comparison table followed by a 2-3 sentence verdict."
    )
