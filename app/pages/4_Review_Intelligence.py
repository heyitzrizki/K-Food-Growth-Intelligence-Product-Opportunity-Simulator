from __future__ import annotations

import plotly.express as px
import streamlit as st

from app.dashboard_utils import load_dashboard_data, render_data_note


st.set_page_config(
    page_title="Review Intelligence",
    page_icon="🧠",
    layout="wide",
)

data = load_dashboard_data()
review_topics = data["review_topics"]
review_features = data["review_features"]

st.title("🧠 Review Intelligence")

st.markdown(
    """
    This page summarizes simulated customer feedback to identify product pain points
    and adaptation opportunities such as price, spiciness, halal labeling, packaging,
    convenience, and health concerns.
    """
)

countries = sorted(review_topics["country"].unique().tolist())
categories = sorted(review_topics["category"].unique().tolist())

col1, col2 = st.columns(2)

selected_country = col1.selectbox("Select country", countries)
selected_category = col2.selectbox("Select category", categories)

filtered_reviews = review_topics[
    (review_topics["country"] == selected_country)
    & (review_topics["category"] == selected_category)
].copy()

features_filtered = review_features[
    (review_features["country"] == selected_country)
    & (review_features["category"] == selected_category)
]

st.subheader("Customer Feedback Snapshot")

if not features_filtered.empty:
    row = features_filtered.iloc[0]

    col_a, col_b, col_c, col_d = st.columns(4)

    col_a.metric("Review Opportunity Score", f"{row['review_opportunity_score']:.1f}")
    col_b.metric("Halal Concern", f"{row['halal_concern_share']:.1%}")
    col_c.metric("Spiciness Issue", f"{row['spiciness_issue_share']:.1%}")
    col_d.metric("Price Issue", f"{row['price_issue_share']:.1%}")

st.subheader("Feedback Sentiment")

fig_sentiment = px.histogram(
    filtered_reviews,
    x="sentiment_label",
    color="sentiment_label",
    title=f"Feedback Sentiment: {selected_country} - {selected_category}",
)

fig_sentiment.update_layout(
    xaxis_title="Sentiment",
    yaxis_title="Number of Reviews",
)

st.plotly_chart(fig_sentiment, use_container_width=True)

st.subheader("Main Feedback Themes")

topic_summary = (
    filtered_reviews.groupby(["topic_label", "top_words"], as_index=False)
    .agg(
        review_count=("review_id", "count"),
        avg_rating=("rating", "mean"),
    )
    .sort_values("review_count", ascending=False)
)

topic_summary["avg_rating"] = topic_summary["avg_rating"].round(2)

st.dataframe(
    topic_summary,
    use_container_width=True,
    hide_index=True,
)

st.subheader("Example Review Texts")

st.dataframe(
    filtered_reviews[
        [
            "anonymous_brand",
            "rating",
            "review_text",
            "sentiment_label",
            "topic_label",
        ]
    ].head(15),
    use_container_width=True,
    hide_index=True,
)

st.markdown(
    """
    **How to read this page:**  
    The system groups review text into business themes. The purpose is to identify
    product adaptation opportunities, not to claim real customer sentiment.
    """
)

render_data_note()