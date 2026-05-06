from __future__ import annotations

import streamlit as st


st.set_page_config(
    page_title="K-Food Growth Intelligence",
    page_icon="🍜",
    layout="wide",
)

st.title("🍜 K-Food Growth Intelligence & Product Opportunity Simulator")

st.markdown(
    """
    A business planning dashboard that helps identify which K-Food product ideas
    may be attractive in selected global markets.

    The dashboard combines consumer search trends, macro-market readiness,
    simulated marketplace signals, review-based customer pain points, and
    scenario-based business assumptions to support product opportunity decisions.
    """
)

st.info(
    """
    Use the sidebar to follow the story:
    **Executive Overview → Trend Radar → Market Opportunity → Review Intelligence
    → Product Idea Board → Scenario Simulator → Methodology Notes**
    """
)

st.subheader("What business question does this project answer?")

st.markdown(
    """
    **Which K-Food product idea should be prioritized, in which market, and why?**

    The system does not try to predict exact sales. Instead, it creates a structured
    decision-support workflow that turns public and simulated business signals into
    product-market recommendations.
    """
)

st.subheader("Dashboard Story")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        **1. Read the market signal**

        Google Trends is used to understand relative consumer interest in K-Food
        keywords such as kimchi, gochujang, tteokbokki, Korean ramen, and bibigo.
        """
    )

with col2:
    st.markdown(
        """
        **2. Understand the opportunity**

        Country-level indicators, simulated competitor data, and review signals are
        combined into a product opportunity score.
        """
    )

with col3:
    st.markdown(
        """
        **3. Translate insight into action**

        The dashboard recommends product ideas, target segments, channels, and
        scenario-based business outcomes.
        """
    )

st.subheader("Data Transparency")

st.markdown(
    """
    - **Real public data:** World Bank macroeconomic indicators and Google Trends.
    - **Synthetic data:** anonymized competitor benchmark, simulated customer reviews,
      and scenario-based financial assumptions.
    - **Purpose:** portfolio prototype and business analytics demonstration, not real
     company internal analysis.
    """
)