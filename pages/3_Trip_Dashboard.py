"""
Dashboard for a single saved trip — itinerary, map, cost charts, packing list.
"""
import os
import json
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

for k in ("OPENAI_API_KEY", "PINECONE_API_KEY", "SERPER_API_KEY", "SUPABASE_DATABASE_URL"):
    if k not in st.session_state:
        st.session_state[k] = os.getenv(k, "")

st.set_page_config(page_title="Trip Dashboard", page_icon="📊", layout="wide")
st.title("📊 Trip Dashboard")

trip_id = st.session_state.get("selected_trip_id")

if not trip_id:
    st.info("Select a trip from the My Trips page first.")
    st.stop()

if not st.session_state.get("SUPABASE_DATABASE_URL"):
    st.info("Supabase not configured.")
    st.stop()

try:
    from database.crud import TripCRUD
    trip = TripCRUD().get_trip(trip_id)
except Exception as e:
    st.error(f"Error loading trip: {e}")
    st.stop()

if not trip:
    st.error("Trip not found.")
    st.stop()

st.subheader(f"{trip['destination']} — {trip['duration_days']} days")
st.caption(f"Budget: ${trip['budget_usd']} · Status: {trip.get('status', 'completed')}")

# tabs
tab_itinerary, tab_map, tab_costs, tab_packing = st.tabs(
    ["Itinerary", "Map", "Cost Breakdown", "Packing List"]
)

itinerary_json = trip.get("itinerary_json") or {}

with tab_itinerary:
    md = trip.get("itinerary_markdown", "")
    if md:
        st.markdown(md)
    else:
        st.info("No itinerary text available.")

with tab_map:
    # try to extract locations from structured data
    locations = []
    for day in itinerary_json.get("daily_plans", []):
        for act in day.get("activities", []) + day.get("meals", []):
            addr = act.get("address") or act.get("location", "")
            if addr:
                locations.append({"name": act.get("activity", ""), "address": addr})

    if locations:
        st.info(f"Found {len(locations)} locations in the itinerary. "
                "Map rendering requires geocoded coordinates — "
                "use the Route Optimizer to get lat/lon data.")
    else:
        st.info("No structured location data. Map requires geocoded coordinates.")

with tab_costs:
    from components.cost_charts import render_daily_spending

    # try to build breakdown from structured data
    daily_plans = itinerary_json.get("daily_plans", [])
    if daily_plans:
        daily_costs = [
            {"day": d["day_number"], "cost": d.get("total_cost_usd", 0)}
            for d in daily_plans
        ]
        render_daily_spending(daily_costs)

        total = itinerary_json.get("total_estimated_cost_usd", 0)
        budget_val = trip.get("budget_usd", 0)
        if total and budget_val:
            diff = budget_val - total
            st.metric("Budget Remaining", f"${diff:,.0f}",
                      delta=f"{'under' if diff >= 0 else 'over'} budget")
    else:
        st.info("No structured cost data available.")

with tab_packing:
    import hashlib
    packing = [p for p in (itinerary_json.get("packing_list") or []) if p]
    if packing:
        st.markdown("Check off items as you pack:")
        for item in packing:
            safe_key = f"pack_{hashlib.md5(str(item).encode()).hexdigest()[:8]}"
            st.checkbox(str(item), key=safe_key)
    else:
        st.info("No packing list in the itinerary data.")
