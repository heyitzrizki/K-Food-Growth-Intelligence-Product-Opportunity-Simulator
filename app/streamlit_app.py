import streamlit as st

st.set_page_config(
    page_title="K-Food Growth Intelligence",
    page_icon="🍜",
    layout="wide",
)

st.title("🍜 K-Food Growth Intelligence & Product Opportunity Simulator")

st.markdown(
    """
    This dashboard is an ML-assisted business analytics prototype for identifying
    K-Food product opportunities across selected global markets.
    
    The system combines real public macro and Google Trends data with synthetic
    anonymized marketplace and review datasets.
    """
)

st.info("Project setup is ready. Data pipeline and analytics modules will be added next.")