"""
Wrapper around Folium map for easy use in Streamlit pages.
"""
import streamlit as st
from streamlit_folium import st_folium
from services.map_service import create_trip_map


def render_trip_map(locations: list, height: int = 500):
    """
    Render an interactive map in the current Streamlit container.
    locations: list of dicts with name, lat, lon, type, notes
    """
    if not locations:
        st.info("No location data available for mapping.")
        return

    m = create_trip_map(locations)
    st_folium(m, height=height, use_container_width=True)
