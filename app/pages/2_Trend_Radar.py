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
trend_features = data["trend_features"].copy()
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

st.subheader("Trend Classification Framework")

st.markdown(
    """
    Not every buzz is a trend. This framework classifies K-Food search signals into
    five business-friendly trend stages: **Fad, Early, Minor, Major, and Mega**.
    """
)

stage_filtered = trend_features[trend_features["country"] == selected_country].copy()

stage_order = ["Fad", "Early", "Minor", "Major", "Mega"]
stage_filtered["trend_stage"] = pd.Categorical(
    stage_filtered["trend_stage"],
    categories=stage_order,
    ordered=True,
)

fig_stage = px.scatter(
    stage_filtered,
    x="recent_12m_interest",
    y="momentum_pct",
    size="peak_interest",
    color="trend_stage",
    hover_name="keyword",
    hover_data={
        "average_interest": ":.2f",
        "recent_12m_interest": ":.2f",
        "momentum_pct": ":.2%",
        "trend_volatility": ":.2f",
        "zero_share": ":.2%",
    },
    title=f"Trend Classification in {selected_country}",
)

fig_stage.update_layout(
    xaxis_title="Recent 12-Month Interest",
    yaxis_title="Recent Momentum",
)

st.plotly_chart(fig_stage, use_container_width=True)

st.dataframe(
    stage_filtered[
        [
            "keyword",
            "trend_stage",
            "average_interest",
            "recent_12m_interest",
            "momentum_pct",
            "trend_volatility",
            "peak_interest",
            "zero_share",
        ]
    ].sort_values(["trend_stage", "recent_12m_interest"], ascending=[True, False]),
    use_container_width=True,
    hide_index=True,
)

st.markdown(
    """
    **Trend stage interpretation**

    - **Fad**: a signal with strong spikes but weak consistency.
    - **Early**: still small, but growing fast enough to monitor closely.
    - **Minor**: low or niche signal with limited business urgency.
    - **Major**: strong and relatively consistent signal worth business attention.
    - **Mega**: very strong signal with high recent interest and positive momentum.
    """
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