import asyncio
import re
from typing import AsyncIterator, Dict, Any

from backend.agents.base import create_travel_mcp
from backend.agents.team import create_travel_team

_DELEGATE_TRACE = re.compile(
    r"delegate_task_to_member\([^)]*\)\s*completed\s*in\s*[\d.]+s\.?\s*",
    re.IGNORECASE,
)


def _clean(text: str) -> str:
    return _DELEGATE_TRACE.sub("", text)


def _short_args(args) -> str:
    if not args:
        return ""
    try:
        if isinstance(args, dict):
            pairs = []
            for k, v in args.items():
                vs = str(v)
                if len(vs) > 30:
                    vs = vs[:30] + "..."
                pairs.append(f"{k}={vs}")
                if len(pairs) >= 3:
                    break
            return ", ".join(pairs)
        return str(args)[:80]
    except Exception:
        return ""


def _build_prompt(destination: str, num_days: int, preferences: str, budget: int) -> str:
    return (
        f"Create a comprehensive travel itinerary for:\n"
        f"Destination: {destination}\n"
        f"Duration: {num_days} days\n"
        f"Budget: ${budget} USD total\n"
        f"Preferences: {preferences}\n\n"
        f"Delegate to all team members and compile a final structured itinerary. "
        f"Do NOT ask clarifying questions - generate the full plan immediately."
    )


async def plan_trip_streaming(
    destination: str,
    num_days: int,
    preferences: str,
    budget: int,
) -> AsyncIterator[Dict[str, Any]]:
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
                    args = getattr(tool, "tool_args", None) if tool else None
                    yield {
                        "type": "agent_tool_start",
                        "agent": agent_name,
                        "tool": tool_name,
                        "args": _short_args(args),
                    }
                elif "ToolCallCompleted" in event_name:
                    tool = getattr(event, "tool", None)
                    tool_name = getattr(tool, "tool_name", "tool") if tool else "tool"
                    yield {"type": "agent_tool_done", "agent": agent_name, "tool": tool_name}
                elif "RunStarted" in event_name:
                    yield {"type": "agent_started", "agent": agent_name}
                elif "RunCompleted" in event_name:
                    yield {"type": "agent_completed", "agent": agent_name}
            else:
                if "Content" in event_name:
                    content = getattr(event, "content", "")
                    if content:
                        cleaned = _clean(str(content))
                        if cleaned:
                            yield {"type": "content", "content": cleaned}
                elif "Completed" in event_name:
                    content = getattr(event, "content", "")
                    cleaned = _clean(str(content)) if content else ""
                    yield {"type": "completed", "content": cleaned}


def plan_trip_sync(destination: str, num_days: int, preferences: str, budget: int) -> str:
    async def _run():
        async with create_travel_mcp() as mcp_tools:
            team = create_travel_team(mcp_tools=mcp_tools)
            prompt = _build_prompt(destination, num_days, preferences, budget)
            response = await team.arun(input=prompt)
            return response.content
    return asyncio.run(_run())
