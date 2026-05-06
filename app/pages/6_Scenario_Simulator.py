from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.dashboard_utils import format_pct, format_usd, load_dashboard_data, render_data_note


st.set_page_config(
    page_title="Scenario Simulator",
    page_icon="💰",
    layout="wide",
)

data = load_dashboard_data()
scenario_outputs = data["scenario_outputs"]

st.title("💰 Scenario & P&L Simulator")

st.markdown(
    """
    This page estimates how a selected product idea could perform under conservative,
    base, and aggressive business scenarios.

    The purpose is to show business planning logic, not to forecast actual company results.
    """
)

col1, col2, col3 = st.columns(3)

country = col1.selectbox(
    "Select country",
    sorted(scenario_outputs["country"].unique().tolist()),
)

category_options = sorted(
    scenario_outputs[scenario_outputs["country"] == country]["category"].unique().tolist()
)

category = col2.selectbox("Select category", category_options)

scenario_options = ["Conservative", "Base", "Aggressive"]
available_scenarios = scenario_outputs[
    (scenario_outputs["country"] == country)
    & (scenario_outputs["category"] == category)
]["scenario"].unique().tolist()

scenario_options = [s for s in scenario_options if s in available_scenarios]

scenario = col3.selectbox("Select scenario", scenario_options)

selected = scenario_outputs[
    (scenario_outputs["country"] == country)
    & (scenario_outputs["category"] == category)
    & (scenario_outputs["scenario"] == scenario)
].iloc[0]

st.subheader("Scenario Snapshot")

col_a, col_b, col_c, col_d = st.columns(4)

col_a.metric("Net Revenue", format_usd(selected["net_revenue_usd"]))
col_b.metric("Contribution Profit", format_usd(selected["contribution_profit_usd"]))
col_c.metric("Contribution Margin", format_pct(selected["contribution_margin_pct"]))
col_d.metric("Break-even Units", f"{selected['break_even_units']:,.0f}")

st.markdown(f"**Product idea:** {selected['product_idea']}")
st.markdown(f"**Scenario recommendation:** {selected['scenario_recommendation']}")

scenario_compare = scenario_outputs[
    (scenario_outputs["country"] == country)
    & (scenario_outputs["category"] == category)
].copy()

st.subheader("Scenario Comparison")

fig_revenue = px.bar(
    scenario_compare,
    x="scenario",
    y="net_revenue_usd",
    color="scenario",
    title="Net Revenue by Scenario",
)

fig_revenue.update_layout(
    xaxis_title="Scenario",
    yaxis_title="Net Revenue",
)

st.plotly_chart(fig_revenue, use_container_width=True)

st.subheader("Cost Structure")

cost_cols = [
    "cogs_pct",
    "logistics_pct",
    "marketing_pct",
    "trade_promo_pct",
    "distributor_margin_pct",
]

cost_labels = {
    "cogs_pct": "COGS",
    "logistics_pct": "Logistics",
    "marketing_pct": "Marketing",
    "trade_promo_pct": "Trade Promotion",
    "distributor_margin_pct": "Distributor Margin",
}

cost_data = pd.DataFrame(
    {
        "Cost Component": [cost_labels[col] for col in cost_cols],
        "Share": [selected[col] for col in cost_cols],
    }
)

fig_cost = px.bar(
    cost_data,
    x="Cost Component",
    y="Share",
    title="Cost Assumption Breakdown",
)

fig_cost.update_layout(
    yaxis_tickformat=".0%",
    xaxis_title="",
    yaxis_title="Share of Revenue",
)

st.plotly_chart(fig_cost, use_container_width=True)

render_data_note()