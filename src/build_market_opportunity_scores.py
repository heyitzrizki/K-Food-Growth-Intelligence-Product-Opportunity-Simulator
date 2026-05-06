from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

TREND_FEATURES_PATH = PROCESSED_DATA_DIR / "trend_features.csv"
MACRO_FEATURES_PATH = PROCESSED_DATA_DIR / "macro_features.csv"
REVIEW_FEATURES_PATH = PROCESSED_DATA_DIR / "review_opportunity_features.csv"
COMPETITOR_PRODUCTS_PATH = SYNTHETIC_DATA_DIR / "synthetic_competitor_products.csv"

OUTPUT_PATH = PROCESSED_DATA_DIR / "market_opportunity_scores.csv"


KEYWORD_TO_CATEGORY = {
    "korean ramen": "Korean ramen",
    "kimchi": "Kimchi",
    "gochujang": "Gochujang sauce",
    "bibigo": "Frozen mandu",
    "tteokbokki": "Ready meal",
    "korean food": "Ready meal",
}


def minmax_score(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    values = series.astype(float).replace([np.inf, -np.inf], np.nan)

    if values.notna().sum() == 0:
        return pd.Series(np.nan, index=series.index)

    values = values.fillna(values.median())

    if values.nunique() <= 1:
        return pd.Series(0.5, index=series.index)

    scaled = MinMaxScaler().fit_transform(values.to_frame()).ravel()

    if not higher_is_better:
        scaled = 1 - scaled

    return pd.Series(scaled, index=series.index)


def load_trend_features() -> pd.DataFrame:
    if not TREND_FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"Missing trend features file: {TREND_FEATURES_PATH}. "
            "Run python src/prepare_trend_features.py first."
        )

    df = pd.read_csv(TREND_FEATURES_PATH)
    df["category"] = df["keyword"].map(KEYWORD_TO_CATEGORY)
    df = df[df["category"].notna()].copy()

    category_features = (
        df.groupby(["country", "category"], as_index=False)
        .agg(
            average_interest=("average_interest", "mean"),
            recent_12m_interest=("recent_12m_interest", "mean"),
            previous_12m_interest=("previous_12m_interest", "mean"),
            momentum_change=("momentum_change", "mean"),
            momentum_pct=("momentum_pct", "mean"),
            trend_volatility=("trend_volatility", "mean"),
            peak_interest=("peak_interest", "max"),
            zero_share=("zero_share", "mean"),
        )
    )

    category_features["consumer_interest_score"] = minmax_score(
        category_features["average_interest"],
        higher_is_better=True,
    )

    category_features["trend_momentum_score"] = minmax_score(
        category_features["momentum_change"],
        higher_is_better=True,
    )

    category_features["trend_consistency_score"] = minmax_score(
        category_features["zero_share"] + category_features["trend_volatility"] / 100,
        higher_is_better=False,
    )

    return category_features


def load_macro_features() -> pd.DataFrame:
    if not MACRO_FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"Missing macro features file: {MACRO_FEATURES_PATH}. "
            "Run python src/prepare_macro_features.py first."
        )

    df = pd.read_csv(MACRO_FEATURES_PATH)

    if "macro_potential_score" not in df.columns:
        raise ValueError("macro_features.csv must contain macro_potential_score.")

    if "macro_score_year" in df.columns:
        score_year = int(df["macro_score_year"].dropna().max())
        latest_df = df[df["year"] == score_year].copy()
    else:
        latest_year = int(df["year"].max())
        latest_df = df[df["year"] == latest_year].copy()

    expected_columns = [
        "country",
        "population",
        "gdp_per_capita_usd",
        "urban_population_pct",
        "internet_users_pct",
        "household_consumption_usd",
        "inflation_pct",
        "macro_potential_score",
    ]

    available_columns = [col for col in expected_columns if col in latest_df.columns]

    return latest_df[available_columns].copy()


def load_competitor_features() -> pd.DataFrame:
    if not COMPETITOR_PRODUCTS_PATH.exists():
        raise FileNotFoundError(
            f"Missing competitor products file: {COMPETITOR_PRODUCTS_PATH}. "
            "Run python src/generate_synthetic_data.py first."
        )

    df = pd.read_csv(COMPETITOR_PRODUCTS_PATH)

    grouped = (
        df.groupby(["country", "category"], as_index=False)
        .agg(
            competitor_count=("product_id", "count"),
            korean_brand_count=("brand_type", lambda x: (x == "Korean Brand").sum()),
            avg_price_per_100g=("price_per_100g", "mean"),
            median_price_usd=("price_usd", "median"),
            avg_rating=("rating", "mean"),
            total_review_count=("review_count", "sum"),
            halal_claim_share=("halal_claim", "mean"),
        )
    )

    grouped["korean_brand_presence_score"] = minmax_score(
        grouped["korean_brand_count"],
        higher_is_better=True,
    )

    grouped["competitive_intensity_score"] = minmax_score(
        grouped["competitor_count"],
        higher_is_better=True,
    )

    grouped["market_gap_score"] = 1 - grouped["competitive_intensity_score"]

    grouped["price_feasibility_score"] = minmax_score(
        grouped["avg_price_per_100g"],
        higher_is_better=False,
    )

    grouped["review_validation_score"] = minmax_score(
        grouped["total_review_count"],
        higher_is_better=True,
    )

    grouped["rating_score"] = minmax_score(
        grouped["avg_rating"],
        higher_is_better=True,
    )

    return grouped


def load_review_features() -> pd.DataFrame:
    if not REVIEW_FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"Missing review opportunity file: {REVIEW_FEATURES_PATH}. "
            "Run python src/build_review_nlp_features.py first."
        )

    df = pd.read_csv(REVIEW_FEATURES_PATH)

    if "review_opportunity_score" not in df.columns:
        raise ValueError(
            "review_opportunity_features.csv must contain review_opportunity_score."
        )

    df["review_opportunity_score_scaled"] = minmax_score(
        df["review_opportunity_score"],
        higher_is_better=True,
    )

    return df


def classify_recommended_action(score: float) -> str:
    if score >= 75:
        return "Prioritize"
    if score >= 60:
        return "Pilot / Test"
    if score >= 45:
        return "Monitor"
    return "Deprioritize"


def create_business_rationale(row: pd.Series) -> str:
    strengths = []

    if row["consumer_interest_score"] >= 0.65:
        strengths.append("strong consumer search interest")
    if row["trend_momentum_score"] >= 0.65:
        strengths.append("positive recent trend momentum")
    if row["macro_potential_score"] >= 0.65:
        strengths.append("attractive macro-market readiness")
    if row["market_gap_score"] >= 0.65:
        strengths.append("relatively open competitive space")
    if row["review_opportunity_score_scaled"] >= 0.65:
        strengths.append("meaningful review-based opportunity signals")
    if row["price_feasibility_score"] >= 0.65:
        strengths.append("favorable price feasibility")

    if not strengths:
        return (
            "Opportunity is limited or requires further validation across consumer, "
            "macro, review, and competitive signals."
        )

    return "Opportunity supported by " + ", ".join(strengths) + "."


def build_market_opportunity_scores() -> pd.DataFrame:
    trend_df = load_trend_features()
    macro_df = load_macro_features()
    competitor_df = load_competitor_features()
    review_df = load_review_features()

    opportunity_df = (
        trend_df.merge(macro_df, on="country", how="left")
        .merge(competitor_df, on=["country", "category"], how="left")
        .merge(review_df, on=["country", "category"], how="left")
    )

    score_components = {
        "consumer_interest_score": 0.23,
        "trend_momentum_score": 0.17,
        "macro_potential_score": 0.15,
        "market_gap_score": 0.12,
        "review_opportunity_score_scaled": 0.18,
        "price_feasibility_score": 0.10,
        "trend_consistency_score": 0.05,
    }

    for col in score_components:
        if col not in opportunity_df.columns:
            opportunity_df[col] = np.nan

        opportunity_df[col] = opportunity_df[col].fillna(opportunity_df[col].median())

    opportunity_df["product_opportunity_score"] = 0.0

    for col, weight in score_components.items():
        opportunity_df["product_opportunity_score"] += opportunity_df[col] * weight

    opportunity_df["product_opportunity_score"] = (
        opportunity_df["product_opportunity_score"] * 100
    ).round(2)

    opportunity_df["recommended_action"] = opportunity_df[
        "product_opportunity_score"
    ].apply(classify_recommended_action)

    opportunity_df["business_rationale"] = opportunity_df.apply(
        create_business_rationale,
        axis=1,
    )

    opportunity_df = opportunity_df.sort_values(
        "product_opportunity_score",
        ascending=False,
    ).reset_index(drop=True)

    opportunity_df["rank"] = np.arange(1, len(opportunity_df) + 1)

    return opportunity_df


def main() -> None:
    opportunity_df = build_market_opportunity_scores()
    opportunity_df.to_csv(OUTPUT_PATH, index=False)

    display_columns = [
        "rank",
        "country",
        "category",
        "product_opportunity_score",
        "recommended_action",
        "consumer_interest_score",
        "trend_momentum_score",
        "macro_potential_score",
        "review_opportunity_score_scaled",
        "market_gap_score",
        "business_rationale",
    ]

    display_columns = [col for col in display_columns if col in opportunity_df.columns]

    print("Market opportunity scores generated successfully.")
    print(f"Output shape: {opportunity_df.shape}")
    print(f"Saved to: {OUTPUT_PATH}")
    print("\nTop 10 opportunities:")
    print(opportunity_df[display_columns].head(10))


if __name__ == "__main__":
    main()