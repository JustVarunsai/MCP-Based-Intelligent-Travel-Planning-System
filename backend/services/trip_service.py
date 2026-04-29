"""
Core service that runs the travel team with the custom MCP server connected.
Yields structured events the FastAPI backend can stream to the frontend.
"""
import asyncio
from typing import AsyncIterator, Dict, Any

from backend.agents.base import create_travel_mcp
from backend.agents.team import create_travel_team


def _build_prompt(destination: str, num_days: int, preferences: str, budget: int) -> str:
    return (
        f"Create a comprehensive travel itinerary for:\n"
        f"Destination: {destination}\n"
        f"Duration: {num_days} days\n"
        f"Budget: ${budget} USD total\n"
        f"Preferences: {preferences}\n\n"
        f"Delegate to all team members and compile a final structured itinerary. "
        f"Do NOT ask clarifying questions — generate the full plan immediately."
    )


async def plan_trip_streaming(
    destination: str,
    num_days: int,
    preferences: str,
    budget: int,
) -> AsyncIterator[Dict[str, Any]]:
    """Run the team with streaming. Manages MCP client lifecycle."""
    async with create_travel_mcp() as mcp_tools:
        team = create_travel_team(mcp_tools=mcp_tools)
        prompt = _build_prompt(destination, num_days, preferences, budget)

        async for event in team.arun(input=prompt, stream=True, stream_events=True):
            agent_name = getattr(event, "agent_name", None) or getattr(event, "member_name", None)
            event_name = str(getattr(event, "event", ""))

            if agent_name:
                if "ToolCallStarted" in event_name:
                    tool = getattr(event, "tool", None)
                    tool_name = getattr(tool, "tool_name", "tool") if tool else "tool"
                    yield {"type": "agent_tool_start", "agent": agent_name, "tool": tool_name}
                elif "ToolCallCompleted" in event_name:
                    tool = getattr(event, "tool", None)
                    tool_name = getattr(tool, "tool_name", "tool") if tool else "tool"
                    yield {"type": "agent_tool_done", "agent": agent_name, "tool": tool_name}
                elif "RunStarted" in event_name:
                    yield {"type": "agent_started", "agent": agent_name}
                elif "RunCompleted" in event_name:
                    yield {"type": "agent_completed", "agent": agent_name}
                elif "Content" in event_name:
                    content = getattr(event, "content", "")
                    if content:
                        yield {"type": "agent_content", "agent": agent_name, "content": str(content)}
            else:
                if "Content" in event_name:
                    content = getattr(event, "content", "")
                    if content:
                        yield {"type": "content", "content": str(content)}
                elif "Completed" in event_name:
                    content = getattr(event, "content", "")
                    yield {"type": "completed", "content": str(content) if content else ""}


def plan_trip_sync(destination: str, num_days: int, preferences: str, budget: int) -> str:
    """Non-streaming wrapper — returns final markdown."""
    async def _run():
        async with create_travel_mcp() as mcp_tools:
            team = create_travel_team(mcp_tools=mcp_tools)
            prompt = _build_prompt(destination, num_days, preferences, budget)
            response = await team.arun(input=prompt)
            return response.content
    return asyncio.run(_run())
