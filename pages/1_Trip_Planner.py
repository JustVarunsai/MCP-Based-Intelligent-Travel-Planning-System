"""
Main trip planner page with real-time agent activity streaming.
"""
import asyncio
from queue import Queue, Empty
from threading import Thread
from datetime import date, datetime

import streamlit as st
from components.agent_activity_panel import init_agent_states, render_agent_panel, update_state
from services.export_service import markdown_to_ics

st.set_page_config(page_title="Trip Planner", page_icon="🗺️", layout="wide")

# ── session defaults ─────────────────────────────────────────────
for key in ("itinerary_md", "itinerary_json"):
    if key not in st.session_state:
        st.session_state[key] = None

st.title("🗺️ Trip Planner")

# ── trip config form ─────────────────────────────────────────────
col_form, col_panel = st.columns([2, 3])

with col_form:
    st.subheader("Trip Details")
    destination = st.text_input("Destination", placeholder="e.g. Paris, Tokyo, Bali")

    c1, c2 = st.columns(2)
    with c1:
        num_days = st.number_input("Days", min_value=1, max_value=30, value=7)
    with c2:
        budget = st.number_input("Budget (USD)", min_value=100, max_value=15000, value=2000, step=100)

    start_date = st.date_input("Start date", min_value=date.today(), value=date.today())

    st.subheader("Preferences")
    pref_text = st.text_area(
        "Describe what you enjoy",
        placeholder="beaches, local food, cultural sites, nightlife...",
        height=80,
    )
    quick_prefs = st.multiselect(
        "Quick tags",
        ["Adventure", "Relaxation", "Sightseeing", "Cultural",
         "Beach", "Mountain", "Luxury", "Budget-Friendly",
         "Food & Dining", "Shopping", "Nightlife", "Family-Friendly"],
    )
    parts = []
    if pref_text:
        parts.append(pref_text)
    if quick_prefs:
        parts.extend(quick_prefs)
    preferences = ", ".join(parts) if parts else "General sightseeing"

    generate = st.button("Plan My Trip", type="primary", use_container_width=True)

# ── helpers for running the async team in a thread ───────────────

def _run_stream(queue, dest, days, prefs, bgt):
    """Worker thread that pushes events onto a queue."""
    from services.trip_service import plan_trip_streaming

    async def _inner():
        async for event in plan_trip_streaming(dest, days, prefs, bgt):
            queue.put(event)
        queue.put(None)  # sentinel

    asyncio.run(_inner())

# ── generate itinerary ───────────────────────────────────────────

with col_panel:
    if generate:
        if not destination:
            st.error("Enter a destination first.")
        elif not st.session_state.get("OPENAI_API_KEY"):
            st.error("Set your API keys in the sidebar.")
        else:
            q: Queue = Queue()
            thread = Thread(target=_run_stream, args=(q, destination, num_days, preferences, budget))
            thread.start()

            agent_states = init_agent_states()
            panel_container = st.container()
            render_agent_panel(panel_container, agent_states)

            output_placeholder = st.empty()
            full_content = ""

            with st.spinner("Agents are working..."):
                while True:
                    try:
                        event = q.get(timeout=120)
                    except Empty:
                        st.warning("Timed out waiting for agents.")
                        break

                    if event is None:
                        break

                    # update agent panel
                    agent_states = update_state(agent_states, event)
                    render_agent_panel(panel_container, agent_states)

                    # accumulate content
                    if event.get("type") in ("content", "completed"):
                        chunk = event.get("content", "")
                        if chunk:
                            full_content += chunk
                            output_placeholder.markdown(full_content)

            thread.join(timeout=5)

            if full_content:
                st.session_state.itinerary_md = full_content
                st.success("Itinerary ready!")

# ── display saved itinerary + actions ────────────────────────────

if st.session_state.itinerary_md:
    st.divider()
    st.subheader("Your Itinerary")
    st.markdown(st.session_state.itinerary_md)

    bcol1, bcol2 = st.columns(2)
    with bcol1:
        ics = markdown_to_ics(
            st.session_state.itinerary_md,
            datetime.combine(start_date, datetime.min.time()),
        )
        st.download_button(
            "Download Calendar (.ics)",
            data=ics,
            file_name="travel_itinerary.ics",
            mime="text/calendar",
        )
    with bcol2:
        if st.session_state.get("SUPABASE_URL"):
            if st.button("Save Trip"):
                try:
                    from database.crud import UserCRUD, TripCRUD
                    user = UserCRUD().get_or_create("default@travel.app")
                    TripCRUD().save_trip(
                        user_id=user["id"],
                        destination=destination,
                        duration_days=num_days,
                        budget_usd=budget,
                        preferences=preferences,
                        itinerary_markdown=st.session_state.itinerary_md,
                    )
                    st.success("Trip saved!")
                except Exception as e:
                    st.error(f"Could not save: {e}")
