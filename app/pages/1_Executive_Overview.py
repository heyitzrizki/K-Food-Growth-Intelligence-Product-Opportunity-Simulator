from __future__ import annotations

import plotly.express as px
import streamlit as st

from app.dashboard_utils import (
    format_pct,
    format_usd,
    load_dashboard_data,
    render_data_note,
    render_score_explanation,
)


st.set_page_config(
    page_title="Executive Overview",
    page_icon="📊",
    layout="wide",
)

data = load_dashboard_data()
market_scores = data["market_scores"]
product_ideas = data["product_ideas"]
scenario_outputs = data["scenario_outputs"]

st.title("📊 Executive Overview")

st.markdown(
    """
    This page gives a decision-maker view of the strongest K-Food product-market
    opportunities and the recommended next action.
    """
)

top_row = market_scores.sort_values("product_opportunity_score", ascending=False).iloc[0]
top_country = top_row["country"]
top_category = top_row["category"]

top_idea = product_ideas[
    (product_ideas["country"] == top_country)
    & (product_ideas["category"] == top_category)
].iloc[0]

base_scenario = scenario_outputs[
    (scenario_outputs["country"] == top_country)
    & (scenario_outputs["category"] == top_category)
    & (scenario_outputs["scenario"] == "Base")
].iloc[0]

prioritize_count = (market_scores["recommended_action"] == "Prioritize").sum()
pilot_count = (market_scores["recommended_action"] == "Pilot / Test").sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Top Opportunity Score", f"{top_row['product_opportunity_score']:.1f}")
col2.metric("Top Market", top_country)
col3.metric("Top Category", top_category)
col4.metric("Prioritize / Pilot", f"{prioritize_count} / {pilot_count}")

render_score_explanation()

st.subheader("Recommended Product Concept")

st.markdown(f"### {top_idea['product_idea']}")

col_a, col_b = st.columns([1.1, 1])

with col_a:
    st.markdown(f"**Target segment:** {top_idea['target_segment']}")
    st.markdown(f"**Channel strategy:** {top_idea['channel_strategy']}")
    st.markdown(f"**Why this idea:** {top_idea['idea_rationale']}")
    st.markdown(f"**Market rationale:** {top_idea['business_rationale']}")

with col_b:
    st.markdown("**Base scenario snapshot**")
    st.metric("Net Revenue", format_usd(base_scenario["net_revenue_usd"]))
    st.metric("Contribution Margin", format_pct(base_scenario["contribution_margin_pct"]))
    st.metric("Scenario Recommendation", base_scenario["scenario_recommendation"])

st.subheader("Top 5 Opportunities")

top5 = market_scores.sort_values("product_opportunity_score", ascending=False).head(5)

fig = px.bar(
    top5,
    x="product_opportunity_score",
    y="category",
    color="country",
    orientation="h",
    hover_data=["recommended_action"],
    title="Highest-priority country-category opportunities",
)

fig.update_layout(
    yaxis=dict(autorange="reversed"),
    xaxis_title="Opportunity Score",
    yaxis_title="Product Category",
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    top5[
        [
            "rank",
            "country",
            "category",
            "product_opportunity_score",
            "recommended_action",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

render_data_note()