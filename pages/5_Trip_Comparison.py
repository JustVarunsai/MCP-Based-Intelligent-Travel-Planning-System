"""
Side-by-side comparison of two saved trips.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

for k in ("OPENAI_API_KEY", "PINECONE_API_KEY", "SERPER_API_KEY", "SUPABASE_DATABASE_URL"):
    if k not in st.session_state:
        st.session_state[k] = os.getenv(k, "")

st.set_page_config(page_title="Trip Comparison", page_icon="⚖️", layout="wide")
st.title("⚖️ Compare Trips")

if not st.session_state.get("SUPABASE_DATABASE_URL"):
    st.info("Enter your Supabase DB URL in the sidebar to compare saved trips.")
    st.stop()

try:
    from database.crud import UserCRUD, TripCRUD
    from services.cost_analysis_service import comparison_radar

    user = UserCRUD().get_or_create("default@travel.app")
    trips = TripCRUD().get_user_trips(user["id"])
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

if len(trips) < 2:
    st.info("You need at least 2 saved trips to compare. Create more trips first.")
    st.stop()

def _fmt_date(val):
    if val is None:
        return ""
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d")
    return str(val)[:10]

trip_labels = {f"{t['destination']} ({_fmt_date(t.get('created_at'))})": t for t in trips}
labels = list(trip_labels.keys())

col1, col2 = st.columns(2)
with col1:
    pick_a = st.selectbox("Trip A", labels, index=0)
with col2:
    pick_b = st.selectbox("Trip B", labels, index=min(1, len(labels) - 1))

if pick_a == pick_b:
    st.warning("Pick two different trips to compare.")
    st.stop()

trip_a = trip_labels[pick_a]
trip_b = trip_labels[pick_b]

# comparison table
st.subheader("Overview")
data = {
    "": ["Destination", "Duration", "Budget", "Est. Cost", "Status"],
    "Trip A": [
        trip_a["destination"],
        f"{trip_a['duration_days']} days",
        f"${trip_a['budget_usd']}",
        f"${trip_a.get('total_estimated_cost', 'N/A')}",
        trip_a.get("status", "completed"),
    ],
    "Trip B": [
        trip_b["destination"],
        f"{trip_b['duration_days']} days",
        f"${trip_b['budget_usd']}",
        f"${trip_b.get('total_estimated_cost', 'N/A')}",
        trip_b.get("status", "completed"),
    ],
}
st.table(data)

# radar chart comparison
st.subheader("Visual Comparison")

itinerary_a = trip_a.get("itinerary_json") or {}
itinerary_b = trip_b.get("itinerary_json") or {}

def _trip_stats(trip, itinerary):
    days = trip.get("duration_days", 1)
    plans = itinerary.get("daily_plans", [])
    activities = sum(len(d.get("activities", [])) for d in plans)
    est = itinerary.get("total_estimated_cost_usd", trip.get("budget_usd", 0))
    budget = trip.get("budget_usd", 1)
    fit = max(0, min(100, int((1 - abs(est - budget) / budget) * 100))) if budget else 50
    return {
        "name": trip["destination"],
        "days": days,
        "activities": activities,
        "attractions": len(plans),
        "budget_fit": fit,
    }

stats = [_trip_stats(trip_a, itinerary_a), _trip_stats(trip_b, itinerary_b)]
fig = comparison_radar(stats)
st.plotly_chart(fig, use_container_width=True)
