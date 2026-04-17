"""
Main trip planner page with real-time agent activity streaming.
"""
import os
import asyncio
from queue import Queue, Empty
from threading import Thread
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from components.agent_activity_panel import (
    init_agent_states, render_agent_panel, update_state,
)
from services.export_service import markdown_to_ics

st.set_page_config(page_title="Trip Planner", page_icon="🗺️", layout="wide")

# share the theme CSS
st.markdown("""
<style>
    .stApp { background-color: #FAFAF9; color: #27272A; }
    [data-testid="stSidebar"] { background-color: #F4F4F5; border-right: 1px solid #E4E4E7; }
    [data-testid="stSidebar"] * { color: #27272A; }
    .stButton > button { background-color: #27272A; color: #FAFAF9; border-radius: 6px; border: 1px solid #27272A; }
    .stButton > button:hover { background-color: #3F3F46; color: #FAFAF9; }
    .stButton > button[kind="primary"] { background-color: #18181B; }
    h1, h2, h3, h4, h5 { color: #18181B; }
    .streamlit-expanderHeader { background-color: #FFFFFF; border: 1px solid #E4E4E7; border-radius: 6px; }
    div[data-testid="stMetric"] { background-color: #FFFFFF; border: 1px solid #E4E4E7; padding: 0.75rem; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# pre-load env keys
for k in ("OPENAI_API_KEY", "PINECONE_API_KEY", "SERPER_API_KEY", "SUPABASE_DATABASE_URL"):
    if k not in st.session_state:
        st.session_state[k] = os.getenv(k, "")

for key in ("itinerary_md", "itinerary_json"):
    if key not in st.session_state:
        st.session_state[key] = None

st.title("Trip Planner")
st.caption("5 AI agents collaborate to plan your trip")

# ── tabs for layout ─────────────────────────────────────────────
tab_new, tab_output = st.tabs(["New Trip", "Results"])

# ── helper: background thread running async team ────────────────
def _run_stream(queue, dest, days, prefs, bgt):
    import traceback
    try:
        from services.trip_service import plan_trip_streaming

        async def _inner():
            async for event in plan_trip_streaming(dest, days, prefs, bgt):
                queue.put(event)
            queue.put(None)

        asyncio.run(_inner())
    except Exception as e:
        queue.put({"type": "error", "content": f"{e}\n\n{traceback.format_exc()}"})
        queue.put(None)


# ── NEW TRIP TAB ────────────────────────────────────────────────

# prefill destination from the Destination Explorer page if set
_prefill = st.session_state.pop("prefill_destination", "")

with tab_new:
    with st.expander("Trip Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            destination = st.text_input(
                "Destination",
                value=_prefill,
                placeholder="Paris, Tokyo, Bali...",
            )
            num_days = st.number_input("Days", min_value=1, max_value=30, value=5)
        with col2:
            budget = st.number_input("Budget (USD)", min_value=100, max_value=15000, value=1500, step=100)
            start_date = st.date_input("Start date", min_value=date.today(), value=date.today())
    # persist start_date across reruns so the Results tab can use it
    st.session_state.last_start_date = start_date

    with st.expander("Preferences", expanded=True):
        pref_text = st.text_area(
            "What do you enjoy?",
            placeholder="beaches, local food, cultural sites, nightlife...",
            height=70,
        )
        quick_prefs = st.multiselect(
            "Quick tags",
            ["Adventure", "Relaxation", "Sightseeing", "Cultural", "Beach", "Mountain",
             "Luxury", "Budget-Friendly", "Food & Dining", "Shopping", "Nightlife", "Family-Friendly"],
        )

    parts = []
    if pref_text: parts.append(pref_text)
    if quick_prefs: parts.extend(quick_prefs)
    preferences = ", ".join(parts) if parts else "General sightseeing"

    generate = st.button("Plan My Trip", type="primary", use_container_width=True)

# ── RESULTS TAB ─────────────────────────────────────────────────
with tab_output:
    if generate:
        if not destination:
            st.error("Enter a destination first.")
        elif not st.session_state.get("OPENAI_API_KEY"):
            st.error("Set your API keys in the sidebar.")
        else:
            st.caption(f"Planning {num_days} days in **{destination}** with ${budget} budget")

            q: Queue = Queue()
            thread = Thread(target=_run_stream, args=(q, destination, num_days, preferences, budget))
            thread.start()

            agent_states = init_agent_states()
            panel_placeholder = st.empty()
            render_agent_panel(panel_placeholder, agent_states)

            st.markdown("---")
            st.markdown("#### Final Itinerary")
            output_placeholder = st.empty()
            full_content = ""

            while True:
                try:
                    event = q.get(timeout=300)
                except Empty:
                    st.warning("Timed out waiting for agents.")
                    break

                if event is None:
                    break

                if event.get("type") == "error":
                    with st.expander("Error details", expanded=True):
                        st.error(event.get("content", "Unknown error"))
                    break

                agent_states = update_state(agent_states, event)
                render_agent_panel(panel_placeholder, agent_states)

                if event.get("type") in ("content", "completed"):
                    chunk = event.get("content", "")
                    if chunk:
                        full_content += chunk
                        output_placeholder.markdown(full_content)

            thread.join(timeout=5)

            if full_content:
                st.session_state.itinerary_md = full_content
                # persist trip details so Save Trip works after navigation
                st.session_state.last_destination = destination
                st.session_state.last_num_days = num_days
                st.session_state.last_budget = budget
                st.session_state.last_preferences = preferences
                st.success("Itinerary ready!")

    # persistent view of last generated itinerary
    if st.session_state.itinerary_md:
        st.divider()

        action_col1, action_col2, action_col3 = st.columns(3)
        with action_col1:
            _sd = st.session_state.get("last_start_date", date.today())
            ics = markdown_to_ics(
                st.session_state.itinerary_md,
                datetime.combine(_sd, datetime.min.time()),
            )
            st.download_button(
                "📅 Calendar (.ics)",
                data=ics,
                file_name="travel_itinerary.ics",
                mime="text/calendar",
                use_container_width=True,
            )
        with action_col2:
            if st.session_state.get("SUPABASE_DATABASE_URL"):
                if st.button("💾 Save Trip", use_container_width=True):
                    try:
                        from database.crud import UserCRUD, TripCRUD
                        # prefer the current form values, else fall back to
                        # session state saved when the itinerary was generated
                        save_dest = destination or st.session_state.get("last_destination", "Unknown")
                        save_days = num_days if generate else st.session_state.get("last_num_days", 1)
                        save_budget = budget if generate else st.session_state.get("last_budget", 0)
                        save_prefs = preferences if generate else st.session_state.get("last_preferences", "")
                        user = UserCRUD().get_or_create("default@travel.app")
                        TripCRUD().save_trip(
                            user_id=user["id"],
                            destination=save_dest,
                            duration_days=save_days,
                            budget_usd=save_budget,
                            preferences=save_prefs,
                            itinerary_markdown=st.session_state.itinerary_md,
                        )
                        st.success(f"Trip to {save_dest} saved!")
                    except Exception as e:
                        st.error(f"Could not save: {e}")
        with action_col3:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.itinerary_md = None
                st.session_state.itinerary_json = None
                st.rerun()

        with st.expander("📋 Full Itinerary", expanded=True):
            st.markdown(st.session_state.itinerary_md)
    elif not generate:
        st.info("Generate a trip from the **New Trip** tab to see results here.")
