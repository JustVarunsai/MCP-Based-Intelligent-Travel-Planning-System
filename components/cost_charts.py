"""
Wrappers for rendering Plotly cost charts in Streamlit.
"""
import streamlit as st
from services.cost_analysis_service import cost_breakdown_pie, daily_spending_bar


def render_cost_breakdown(breakdown: dict):
    """Show the pie chart if there's data."""
    if not breakdown:
        st.info("No cost breakdown data available.")
        return
    fig = cost_breakdown_pie(breakdown)
    st.plotly_chart(fig, use_container_width=True)


def render_daily_spending(daily_costs: list):
    """Show the bar chart if there's data."""
    if not daily_costs:
        st.info("No daily cost data available.")
        return
    fig = daily_spending_bar(daily_costs)
    st.plotly_chart(fig, use_container_width=True)
