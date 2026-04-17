"""
Real-time agent activity panel shown during trip planning.
Uses a single st.empty() placeholder that gets rewritten on every update
so the panel replaces itself instead of stacking.
"""
import streamlit as st

AGENTS = [
    ("Destination Researcher", "🔎"),
    ("Accommodation Agent", "🏨"),
    ("Route Optimizer", "🗺️"),
    ("Budget Optimizer", "💰"),
    ("Itinerary Compiler", "📋"),
]


def init_agent_states():
    return {
        name: {"status": "idle", "icon": icon, "tools": [], "content": ""}
        for name, icon in AGENTS
    }


def render_agent_panel(placeholder, states: dict):
    """
    Render the panel into a single st.empty() placeholder.
    Calling this again replaces the previous render — no stacking.
    """
    with placeholder.container():
        done = sum(1 for s in states.values() if s["status"] == "done")
        working = sum(1 for s in states.values() if s["status"] == "working")
        total = len(states)

        st.markdown(f"**Agent progress: {done}/{total} complete** · {working} working")
        st.progress(done / total if total else 0)

        for name, state in states.items():
            status = state["status"]
            icon = state["icon"]
            if status == "idle":
                label = f"{icon} {name} — waiting"
                expanded = False
            elif status == "working":
                label = f"{icon} {name} — working..."
                expanded = True
            else:
                label = f"{icon} {name} — ✓ done"
                expanded = False

            with st.expander(label, expanded=expanded):
                if state["tools"]:
                    st.caption("Tools used:")
                    for tool in state["tools"]:
                        st.code(tool, language=None)
                if state["content"]:
                    st.markdown(state["content"][:1500])
                if not state["tools"] and not state["content"]:
                    st.caption("_No activity yet._")


def update_state(states: dict, event: dict) -> dict:
    etype = event.get("type", "")
    agent = event.get("agent", "")

    if agent and agent in states:
        if etype == "agent_started":
            states[agent]["status"] = "working"
        elif etype == "agent_tool_start":
            states[agent]["status"] = "working"
            tool = event.get("tool", "tool")
            if tool not in states[agent]["tools"]:
                states[agent]["tools"].append(tool)
        elif etype == "agent_completed":
            states[agent]["status"] = "done"
        elif etype == "agent_content":
            chunk = event.get("content", "")
            if chunk:
                states[agent]["content"] += chunk

    return states
