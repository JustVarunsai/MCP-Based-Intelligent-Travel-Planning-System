"""
Reusable trip summary card for the My Trips page.
"""
import streamlit as st


def render_trip_card(trip: dict, on_click_key: str = None):
    """
    Display a compact trip summary card.
    trip keys: id, destination, duration_days, budget_usd, status, created_at
    """
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"### {trip.get('destination', 'Unknown')}")
            st.caption(
                f"{trip.get('duration_days', '?')} days · "
                f"${trip.get('budget_usd', '?')} budget · "
                f"{trip.get('status', 'completed')}"
            )
        with col2:
            est = trip.get("total_estimated_cost", 0)
            if est:
                st.metric("Est. Cost", f"${est:,.0f}")
        with col3:
            created = trip.get("created_at", "")[:10]
            st.caption(f"Created\n{created}")
            if on_click_key:
                st.button("View", key=on_click_key)
