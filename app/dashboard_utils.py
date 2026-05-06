from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

MARKET_SCORES_PATH = PROCESSED_DATA_DIR / "market_opportunity_scores.csv"
PRODUCT_IDEAS_PATH = PROCESSED_DATA_DIR / "product_idea_recommendations.csv"
SCENARIO_OUTPUTS_PATH = PROCESSED_DATA_DIR / "scenario_outputs.csv"
CLUSTERS_PATH = PROCESSED_DATA_DIR / "country_category_clusters.csv"
TREND_RAW_PATH = RAW_DATA_DIR / "google_trends_kfood.csv"
REVIEW_TOPICS_PATH = PROCESSED_DATA_DIR / "review_topics.csv"
REVIEW_FEATURES_PATH = PROCESSED_DATA_DIR / "review_opportunity_features.csv"

COUNTRY_ISO3 = {
    "Indonesia": "IDN",
    "Malaysia": "MYS",
    "Philippines": "PHL",
    "Singapore": "SGP",
    "Thailand": "THA",
    "Viet Nam": "VNM",
    "United States": "USA",
    "Australia": "AUS",
}


@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        st.error(f"Missing file: {path}")
        st.stop()

    return pd.read_csv(path)


@st.cache_data
def load_dashboard_data() -> dict[str, pd.DataFrame]:
    return {
        "market_scores": load_csv(MARKET_SCORES_PATH),
        "product_ideas": load_csv(PRODUCT_IDEAS_PATH),
        "scenario_outputs": load_csv(SCENARIO_OUTPUTS_PATH),
        "clusters": load_csv(CLUSTERS_PATH),
        "trend_raw": load_csv(TREND_RAW_PATH),
        "review_topics": load_csv(REVIEW_TOPICS_PATH),
        "review_features": load_csv(REVIEW_FEATURES_PATH),
    }


def render_data_note() -> None:
    st.caption(
        "Data note: World Bank and Google Trends are real public data sources. "
        "Competitor benchmark, customer review corpus, and financial assumptions are "
        "synthetic and used for prototype simulation only."
    )


def render_score_explanation() -> None:
    st.caption(
        "Opportunity score is a 0–100 decision-support index combining consumer interest, "
        "trend momentum, macro readiness, review signals, competitive space, and price feasibility. "
        "It is not a sales forecast."
    )


def format_usd(value: float) -> str:
    return f"${value:,.0f}"


def format_pct(value: float) -> str:
    return f"{value:.1%}"