from __future__ import annotations

import streamlit as st


st.set_page_config(
    page_title="Methodology Notes",
    page_icon="📘",
    layout="wide",
)

st.title("📘 Methodology Notes")

st.subheader("Project Purpose")

st.markdown(
    """
    This project is a portfolio prototype that demonstrates how public consumer
    signals, macro indicators, synthetic marketplace data, and ML-assisted review
    intelligence can be combined into a business planning decision-support system.
    """
)

st.subheader("Data Sources")

st.markdown(
    """
    **Real public data**

    - World Bank macroeconomic indicators
    - Google Trends relative search interest

    **Synthetic data**

    - Anonymized competitor product benchmark
    - Synthetic customer review corpus
    - Scenario-based business assumptions
    """
)

st.subheader("Data Interpretation")

st.markdown(
    """
    - Google Trends values are normalized relative search interest scores from 0 to 100.
    - Google Trends does not represent absolute search volume, sales volume, or revenue.
    - Synthetic reviews are used to demonstrate the review intelligence workflow.
    - Scenario and P&L outputs are based on synthetic assumptions and do not represent
      CJ CheilJedang financial data.
    """
)

st.subheader("Analytics and Modeling Approach")

st.markdown(
    """
    The system uses:

    - Google Trends feature engineering for consumer interest and trend momentum
    - World Bank indicators for macro-market readiness
    - TF-IDF and NMF topic modeling for review theme detection
    - K-Means clustering for country-category segmentation
    - Weighted scoring for product opportunity prioritization
    - Rule-based product idea mapping
    - Scenario-based revenue and contribution margin simulation
    """
)

st.subheader("Opportunity Score")

st.markdown(
    """
    The opportunity score is a decision-support index. It combines:

    - Consumer interest score
    - Trend momentum score
    - Macro-market readiness score
    - Review-based opportunity signal
    - Competitive space score
    - Price feasibility score
    - Trend consistency score

    It should not be interpreted as a predicted sales number.
    """
)

st.subheader("Limitations")

st.markdown(
    """
    - The project does not use real company sales, distributor, or retailer sell-out data.
    - Marketplace and review datasets are synthetic and designed for demonstration.
    - Product ideas are structured recommendations, not validated launch decisions.
    - Financial scenarios are based on assumptions and require real company data for
      production use.
    """
)

st.subheader("Business Value")

st.markdown(
    """
    Despite these limitations, the project demonstrates a practical analytics workflow
    for connecting consumer trend signals, market readiness, customer pain points,
    competitor conditions, and financial scenarios into structured product opportunity
    recommendations.
    """
)