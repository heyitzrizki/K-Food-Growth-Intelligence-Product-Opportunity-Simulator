from __future__ import annotations

import plotly.express as px
import streamlit as st

from app.dashboard_utils import (
    COUNTRY_ISO3,
    load_dashboard_data,
    render_data_note,
    render_score_explanation,
)


st.set_page_config(
    page_title="Market Opportunity",
    page_icon="🌍",
    layout="wide",
)

data = load_dashboard_data()
market_scores = data["market_scores"]
clusters = data["clusters"]

st.title("🌍 Market Opportunity")

st.markdown(
    """
    This page compares countries and product categories based on opportunity signals.
    It helps answer: **where does the market look more attractive, and for which
    K-Food category?**
    """
)

categories = sorted(market_scores["category"].unique().tolist())

selected_categories = st.multiselect(
    "Select categories",
    categories,
    default=categories,
)

filtered = market_scores[market_scores["category"].isin(selected_categories)].copy()

render_score_explanation()

st.subheader("Global Opportunity Map")

country_map = (
    filtered.groupby("country", as_index=False)
    .agg(
        avg_opportunity_score=("product_opportunity_score", "mean"),
        max_opportunity_score=("product_opportunity_score", "max"),
    )
)

country_map["iso_alpha"] = country_map["country"].map(COUNTRY_ISO3)

fig_map = px.choropleth(
    country_map,
    locations="iso_alpha",
    color="avg_opportunity_score",
    hover_name="country",
    hover_data={
        "iso_alpha": False,
        "avg_opportunity_score": ":.2f",
        "max_opportunity_score": ":.2f",
    },
    color_continuous_scale="Blues",
    projection="natural earth",
    title="Average Opportunity Score by Country",
)

fig_map.update_layout(
    margin=dict(l=0, r=0, t=50, b=0),
    coloraxis_colorbar=dict(title="Avg Score"),
)

st.plotly_chart(fig_map, use_container_width=True)

st.subheader("Country-Category Ranking")

st.dataframe(
    filtered[
        [
            "rank",
            "country",
            "category",
            "product_opportunity_score",
            "recommended_action",
            "business_rationale",
        ]
    ].sort_values("product_opportunity_score", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Market Segments")

st.markdown(
    """
    Markets with similar opportunity patterns are grouped together to help compare
    strategic market types, not just individual scores.
    """
)

cluster_filtered = clusters[clusters["category"].isin(selected_categories)].copy()

fig_cluster = px.scatter(
    cluster_filtered,
    x="consumer_interest_score",
    y="macro_potential_score",
    size="product_opportunity_score",
    color="cluster_label",
    hover_name="country",
    hover_data=["category", "recommended_action", "product_opportunity_score"],
    title="Market Segments by Consumer Interest and Macro Readiness",
)

fig_cluster.update_layout(
    xaxis_title="Consumer Interest Score",
    yaxis_title="Macro Readiness Score",
)

st.plotly_chart(fig_cluster, use_container_width=True)

render_data_note()