"""
Generates Plotly charts for trip cost analysis.
"""
import plotly.express as px
import plotly.graph_objects as go


def cost_breakdown_pie(breakdown: dict):
    """
    Pie chart showing cost distribution across categories.
    breakdown: {"Accommodation": 500, "Food": 200, ...}
    """
    labels = list(breakdown.keys())
    values = list(breakdown.values())

    fig = px.pie(
        names=labels,
        values=values,
        title="Budget Breakdown",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.4,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#F8FAFC",
        margin=dict(t=40, b=20, l=20, r=20),
    )
    return fig


def daily_spending_bar(daily_costs: list):
    """
    Bar chart showing estimated spending per day.
    daily_costs: [{"day": 1, "cost": 150}, ...]
    """
    days = [f"Day {d['day']}" for d in daily_costs]
    costs = [d["cost"] for d in daily_costs]

    fig = go.Figure(
        go.Bar(
            x=days,
            y=costs,
            marker_color="#2563EB",
            text=[f"${c:.0f}" for c in costs],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Daily Estimated Spending",
        xaxis_title="",
        yaxis_title="Cost (USD)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#F8FAFC",
        margin=dict(t=40, b=20, l=40, r=20),
    )
    return fig


def comparison_radar(trips: list):
    """
    Radar chart comparing multiple trips across dimensions.
    trips: [{"name": "Paris Trip", "cost": 2000, "days": 7,
             "activities": 15, "attractions": 10, "budget_fit": 85}, ...]
    """
    categories = ["Cost Efficiency", "Duration", "Activities", "Attractions", "Budget Fit"]

    fig = go.Figure()
    for trip in trips:
        fig.add_trace(go.Scatterpolar(
            r=[
                trip.get("budget_fit", 50),
                trip.get("days", 0) * 10,
                trip.get("activities", 0) * 5,
                trip.get("attractions", 0) * 8,
                trip.get("budget_fit", 50),
            ],
            theta=categories,
            fill="toself",
            name=trip["name"],
        ))
    fig.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#F8FAFC",
        margin=dict(t=30, b=30, l=60, r=60),
    )
    return fig
