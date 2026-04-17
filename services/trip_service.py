"""
Core service that runs the travel team and streams events
back to the UI for real-time agent activity visualisation.
"""
import asyncio
from typing import AsyncIterator, Dict, Any
from agents.team import create_travel_team


async def plan_trip_streaming(
    destination: str,
    num_days: int,
    preferences: str,
    budget: int,
) -> AsyncIterator[Dict[str, Any]]:
    """
    Run the multi-agent travel team with streaming enabled.
    Yields structured dicts that the Streamlit frontend can consume.
    """
    team = create_travel_team()

    prompt = (
        f"Create a comprehensive travel itinerary for:\n"
        f"Destination: {destination}\n"
        f"Duration: {num_days} days\n"
        f"Budget: ${budget} USD total\n"
        f"Preferences: {preferences}\n\n"
        f"Delegate to all team members and compile a final structured itinerary. "
        f"Do NOT ask clarifying questions — generate the full plan immediately."
    )

    response = team.arun(input=prompt, stream=True, stream_events=True)

    async for event in response:
        # figure out if this is a member-level or team-level event
        agent_name = getattr(event, "agent_name", None) or getattr(event, "member_name", None)
        event_name = str(getattr(event, "event", ""))

        # member agent events
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

        # team-level content
        else:
            if "Content" in event_name:
                content = getattr(event, "content", "")
                if content:
                    yield {"type": "content", "content": str(content)}
            elif "Completed" in event_name:
                content = getattr(event, "content", "")
                yield {"type": "completed", "content": str(content) if content else ""}


def plan_trip_sync(destination, num_days, preferences, budget):
    """Non-streaming sync wrapper — returns the final markdown string."""
    team = create_travel_team()
    prompt = (
        f"Create a comprehensive travel itinerary for:\n"
        f"Destination: {destination}\n"
        f"Duration: {num_days} days\n"
        f"Budget: ${budget} USD total\n"
        f"Preferences: {preferences}\n\n"
        f"Delegate to all team members and compile a final structured itinerary. "
        f"Do NOT ask clarifying questions — generate the full plan immediately."
    )
    response = asyncio.run(team.arun(input=prompt))
    return response.content
