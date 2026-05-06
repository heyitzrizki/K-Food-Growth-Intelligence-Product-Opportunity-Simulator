from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_utils import load_dashboard_data, render_data_note


st.set_page_config(
    page_title="Trend Radar",
    page_icon="📈",
    layout="wide",
)

data = load_dashboard_data()
trend_raw = data["trend_raw"].copy()
trend_raw["date"] = pd.to_datetime(trend_raw["date"])

st.title("📈 Trend Radar")

st.markdown(
    """
    This page shows how consumer search interest for selected K-Food keywords changed
    over time across target markets.

    Google Trends is used as a **relative interest signal**, not as actual sales,
    market size, or absolute search volume.
    """
)

countries = sorted(trend_raw["country"].unique().tolist())
keywords = sorted(trend_raw["keyword"].unique().tolist())

col1, col2 = st.columns(2)

selected_country = col1.selectbox("Select country", countries)
selected_keywords = col2.multiselect(
    "Select keywords",
    keywords,
    default=["korean food", "kimchi", "korean ramen"],
)

chart_df = trend_raw[
    (trend_raw["country"] == selected_country)
    & (trend_raw["keyword"].isin(selected_keywords))
]

fig = px.line(
    chart_df,
    x="date",
    y="search_interest",
    color="keyword",
    title=f"Relative K-Food Search Interest in {selected_country}",
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Google Trends Index",
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Keyword Interest Comparison")

heatmap_df = (
    trend_raw.groupby(["country", "keyword"], as_index=False)["search_interest"]
    .mean()
    .rename(columns={"search_interest": "average_interest"})
)

fig_heatmap = px.density_heatmap(
    heatmap_df,
    x="keyword",
    y="country",
    z="average_interest",
    color_continuous_scale="Blues",
    title="Average Relative Interest by Country and Keyword",
)

fig_heatmap.update_layout(
    xaxis_title="Keyword",
    yaxis_title="Country",
)

st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown(
    """
    **How to read this page:**  
    A higher value means the keyword had stronger relative search interest within
    the selected Google Trends query. It should be interpreted as directional
    consumer curiosity, not confirmed purchase demand.
    """
)

render_data_note()