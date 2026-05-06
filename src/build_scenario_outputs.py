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

PRODUCT_IDEAS_PATH = PROCESSED_DATA_DIR / "product_idea_recommendations.csv"
BUSINESS_ASSUMPTIONS_PATH = SYNTHETIC_DATA_DIR / "synthetic_business_assumptions.csv"
OUTPUT_PATH = PROCESSED_DATA_DIR / "scenario_outputs.csv"


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


def load_product_ideas() -> pd.DataFrame:
    if not PRODUCT_IDEAS_PATH.exists():
        raise FileNotFoundError(
            f"Missing product idea file: {PRODUCT_IDEAS_PATH}. "
            "Run python src/build_product_ideas.py first."
        )

    return pd.read_csv(PRODUCT_IDEAS_PATH)


def load_business_assumptions() -> pd.DataFrame:
    if not BUSINESS_ASSUMPTIONS_PATH.exists():
        raise FileNotFoundError(
            f"Missing business assumptions file: {BUSINESS_ASSUMPTIONS_PATH}. "
            "Run python src/generate_synthetic_data.py first."
        )

    return pd.read_csv(BUSINESS_ASSUMPTIONS_PATH)


def calculate_break_even_units(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    variable_cost_pct = (
        df["cogs_pct"]
        + df["logistics_pct"]
        + df["marketing_pct"]
        + df["distributor_margin_pct"]
    )

    contribution_per_unit = df["estimated_price_usd"] * (1 - df["trade_promo_pct"]) * (
        1 - variable_cost_pct
    )

    fixed_launch_cost = df["net_revenue_usd"] * 0.08

    df["contribution_per_unit_usd"] = contribution_per_unit.round(2)

    df["break_even_units"] = np.where(
        contribution_per_unit > 0,
        np.ceil(fixed_launch_cost / contribution_per_unit),
        np.nan,
    )

    df["break_even_units"] = df["break_even_units"].round(0)

    return df


def classify_profitability(row: pd.Series) -> str:
    margin = row["contribution_margin_pct"]

    if margin >= 0.25:
        return "High profitability"
    if margin >= 0.15:
        return "Moderate profitability"
    if margin >= 0.05:
        return "Low profitability"
    return "Unattractive profitability"


def classify_scenario_recommendation(row: pd.Series) -> str:
    opportunity_score = row["product_opportunity_score"]
    margin = row["contribution_margin_pct"]

    if opportunity_score >= 75 and margin >= 0.15:
        return "Scale opportunity"
    if opportunity_score >= 60 and margin >= 0.10:
        return "Pilot launch"
    if opportunity_score >= 45 and margin >= 0.05:
        return "Monitor and refine assumptions"
    return "Do not prioritize"


def build_scenario_outputs(
    product_ideas: pd.DataFrame,
    assumptions: pd.DataFrame,
) -> pd.DataFrame:
    merged = product_ideas.merge(
        assumptions,
        on=["country", "category"],
        how="left",
    )

    merged = calculate_break_even_units(merged)

    merged["profitability_label"] = merged.apply(
        classify_profitability,
        axis=1,
    )

    merged["scenario_recommendation"] = merged.apply(
        classify_scenario_recommendation,
        axis=1,
    )

    merged["scenario_profitability_score"] = minmax_score(
        merged["contribution_margin_pct"],
        higher_is_better=True,
    )

    merged["scenario_revenue_score"] = minmax_score(
        merged["net_revenue_usd"],
        higher_is_better=True,
    )

    merged["scenario_business_score"] = (
        merged["scenario_profitability_score"] * 0.60
        + merged["scenario_revenue_score"] * 0.40
    )

    merged["scenario_business_score"] = (
        merged["scenario_business_score"] * 100
    ).round(2)

    selected_columns = [
        "rank",
        "country",
        "category",
        "product_idea",
        "target_segment",
        "channel_strategy",
        "priority_level",
        "recommended_action",
        "scenario",
        "product_opportunity_score",
        "estimated_units",
        "estimated_price_usd",
        "gross_revenue_usd",
        "net_revenue_usd",
        "cogs_pct",
        "logistics_pct",
        "marketing_pct",
        "trade_promo_pct",
        "distributor_margin_pct",
        "contribution_profit_usd",
        "contribution_margin_pct",
        "contribution_per_unit_usd",
        "break_even_units",
        "scenario_profitability_score",
        "scenario_revenue_score",
        "scenario_business_score",
        "profitability_label",
        "scenario_recommendation",
        "idea_rationale",
        "business_rationale",
    ]

    selected_columns = [col for col in selected_columns if col in merged.columns]

    return merged[selected_columns].sort_values(
        ["rank", "scenario"],
        ascending=[True, True],
    )


def main() -> None:
    product_ideas = load_product_ideas()
    assumptions = load_business_assumptions()

    scenario_outputs = build_scenario_outputs(product_ideas, assumptions)
    scenario_outputs.to_csv(OUTPUT_PATH, index=False)

    print("Scenario outputs generated successfully.")
    print(f"Output shape: {scenario_outputs.shape}")
    print(f"Saved to: {OUTPUT_PATH}")

    print("\nTop scenario outputs:")
    print(
        scenario_outputs[
            [
                "rank",
                "country",
                "category",
                "scenario",
                "product_opportunity_score",
                "net_revenue_usd",
                "contribution_margin_pct",
                "scenario_recommendation",
            ]
        ].head(12)
    )


if __name__ == "__main__":
    main()