"""
Saved trips page — lists all trips from Supabase.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

# pre-load env keys into session state
for k in ("OPENAI_API_KEY", "PINECONE_API_KEY", "SERPER_API_KEY", "SUPABASE_DATABASE_URL"):
    if k not in st.session_state:
        st.session_state[k] = os.getenv(k, "")


def _fmt_date(val):
    """Safely convert a value to a short date string."""
    if val is None:
        return ""
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d")
    return str(val)[:10]

st.set_page_config(page_title="My Trips", page_icon="📋", layout="wide")
st.title("📋 My Trips")

if not st.session_state.get("SUPABASE_DATABASE_URL"):
    st.info("Enter your Supabase DB URL in the sidebar to see saved trips.")
    st.stop()

try:
    from database.crud import UserCRUD, TripCRUD

    user = UserCRUD().get_or_create("default@travel.app")
    trips = TripCRUD().get_user_trips(user["id"])

    if not trips:
        st.info("No saved trips yet. Head to the Trip Planner to create one!")
        st.stop()

    # search / filter
    search = st.text_input("Filter by destination", "")
    if search:
        trips = [t for t in trips if search.lower() in t.get("destination", "").lower()]

    st.caption(f"Showing {len(trips)} trip(s)")

    for trip in trips:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            with c1:
                st.markdown(f"### {trip['destination']}")
                st.caption(
                    f"{trip['duration_days']} days · ${trip['budget_usd']} budget"
                )
            with c2:
                est = trip.get("total_estimated_cost")
                if est:
                    st.metric("Est. Cost", f"${est:,.0f}")
            with c3:
                st.caption(_fmt_date(trip.get("created_at")))
            with c4:
                if st.button("View", key=f"view_{trip['id']}"):
                    st.session_state["selected_trip_id"] = trip["id"]
                    st.switch_page("pages/3_Trip_Dashboard.py")
                if st.button("Delete", key=f"del_{trip['id']}"):
                    TripCRUD().delete_trip(trip["id"])
                    st.rerun()

except Exception as e:
    st.error(f"Error loading trips: {e}")
