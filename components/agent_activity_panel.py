"""
Real-time agent activity panel shown during trip planning.
Uses st.status containers that update as events stream in.
"""
import streamlit as st

AGENTS = [
    ("Destination Researcher", "Researching destination info..."),
    ("Accommodation Agent", "Searching Airbnb listings..."),
    ("Route Optimizer", "Calculating routes and distances..."),
    ("Budget Optimizer", "Analysing costs and budget..."),
    ("Itinerary Compiler", "Compiling final itinerary..."),
]


def init_agent_states():
    """Set up a dict to track each agent's status."""
    return {
        name: {"status": "idle", "label": label, "tools": []}
        for name, label in AGENTS
    }


def render_agent_panel(container, states: dict):
    """
    Draw the agent panel inside a given Streamlit container.
    Call this repeatedly as events come in to refresh the display.
    """
    with container:
        st.markdown("#### Agent Activity")
        for name, state in states.items():
            status = state["status"]
            if status == "idle":
                st.markdown(f"⚪ **{name}** — waiting")
            elif status == "working":
                st.markdown(f"🔵 **{name}** — {state['label']}")
                for tool in state["tools"]:
                    st.caption(f"  ↳ using `{tool}`")
            elif status == "done":
                st.markdown(f"🟢 **{name}** — done")


def update_state(states: dict, event: dict) -> dict:
    """Update agent states dict based on a streaming event."""
    etype = event.get("type", "")
    agent = event.get("agent", "")

    if agent not in states:
        return states

    if etype == "agent_started":
        states[agent]["status"] = "working"
        states[agent]["tools"] = []
    elif etype == "agent_tool_start":
        states[agent]["status"] = "working"
        tool = event.get("tool", "tool")
        if tool not in states[agent]["tools"]:
            states[agent]["tools"].append(tool)
    elif etype == "agent_completed":
        states[agent]["status"] = "done"

    return states
