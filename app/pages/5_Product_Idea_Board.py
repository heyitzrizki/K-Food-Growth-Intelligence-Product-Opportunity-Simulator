from __future__ import annotations

import plotly.express as px
import streamlit as st

from dashboard_utils import load_dashboard_data, render_data_note


st.set_page_config(
    page_title="Product Idea Board",
    page_icon="💡",
    layout="wide",
)

data = load_dashboard_data()
product_ideas = data["product_ideas"]

st.title("💡 Product Idea Board")

st.markdown(
    """
    This page turns market signals and customer pain points into product concepts,
    target segments, and channel suggestions.
    """
)

priority_options = sorted(product_ideas["priority_level"].unique().tolist())

selected_priority = st.multiselect(
    "Select priority level",
    priority_options,
    default=priority_options,
)

filtered = product_ideas[product_ideas["priority_level"].isin(selected_priority)].copy()

st.subheader("Top Product Ideas")

top_ideas = filtered.sort_values("product_opportunity_score", ascending=False).head(12)

fig = px.bar(
    top_ideas,
    x="product_opportunity_score",
    y="product_idea",
    color="country",
    orientation="h",
    title="Product Ideas by Opportunity Score",
)

fig.update_layout(
    yaxis=dict(autorange="reversed"),
    xaxis_title="Opportunity Score",
    yaxis_title="Product Idea",
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Product Idea Details")

st.dataframe(
    filtered[
        [
            "rank",
            "country",
            "category",
            "product_idea",
            "target_segment",
            "channel_strategy",
            "priority_level",
            "recommended_action",
            "product_opportunity_score",
            "idea_rationale",
        ]
    ].sort_values("product_opportunity_score", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.markdown(
    """
    **How to read this page:**  
    Product ideas are generated through business rules that translate market signals
    and review-based pain points into product concepts. They should be treated as
    starting points for further validation.
    """
)

render_data_note()