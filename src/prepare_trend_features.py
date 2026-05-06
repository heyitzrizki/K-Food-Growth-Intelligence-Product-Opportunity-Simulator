from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT_PATH = RAW_DATA_DIR / "google_trends_kfood.csv"
OUTPUT_PATH = PROCESSED_DATA_DIR / "trend_features.csv"


def classify_trend_stage(
    average_interest: float,
    recent_12m_interest: float,
    momentum_pct: float,
    trend_volatility: float,
    peak_interest: float,
    zero_share: float,
) -> str:
    if zero_share >= 0.60:
        return "Minor"

    if peak_interest >= 85 and trend_volatility >= 30 and recent_12m_interest < average_interest:
        return "Fad"

    if average_interest >= 55 and recent_12m_interest >= 60 and momentum_pct >= 0.15:
        return "Mega"

    if average_interest >= 40 and recent_12m_interest >= 45 and momentum_pct >= 0:
        return "Major"

    if average_interest < 35 and momentum_pct >= 0.25 and zero_share < 0.50:
        return "Early"

    if average_interest < 35 and recent_12m_interest < 35:
        return "Minor"

    if momentum_pct <= -0.20 and peak_interest >= 70:
        return "Fad"

    return "Minor"


def prepare_trend_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["search_interest"] = pd.to_numeric(df["search_interest"], errors="coerce")
    df = df.sort_values(["country", "keyword", "date"])

    rows = []

    for (country, geo, keyword), group in df.groupby(["country", "geo", "keyword"]):
        group = group.sort_values("date")

        recent_12m = group.tail(12)
        previous_12m = group.iloc[-24:-12]

        average_interest = group["search_interest"].mean()
        recent_12m_interest = recent_12m["search_interest"].mean()
        previous_12m_interest = previous_12m["search_interest"].mean()

        momentum_change = recent_12m_interest - previous_12m_interest

        if previous_12m_interest == 0:
            momentum_pct = np.nan
        else:
            momentum_pct = momentum_change / previous_12m_interest

        trend_volatility = group["search_interest"].std()
        peak_interest = group["search_interest"].max()
        zero_share = (group["search_interest"] == 0).mean()

        trend_stage = classify_trend_stage(
            average_interest=average_interest,
            recent_12m_interest=recent_12m_interest,
            momentum_pct=0 if pd.isna(momentum_pct) else momentum_pct,
            trend_volatility=trend_volatility,
            peak_interest=peak_interest,
            zero_share=zero_share,
        )

        rows.append(
            {
                "country": country,
                "geo": geo,
                "keyword": keyword,
                "average_interest": round(average_interest, 2),
                "recent_12m_interest": round(recent_12m_interest, 2),
                "previous_12m_interest": round(previous_12m_interest, 2),
                "momentum_change": round(momentum_change, 2),
                "momentum_pct": round(momentum_pct, 4) if not pd.isna(momentum_pct) else np.nan,
                "trend_volatility": round(trend_volatility, 2),
                "peak_interest": peak_interest,
                "zero_share": round(zero_share, 4),
                "trend_stage": trend_stage,
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}. "
            "Place google_trends_kfood.csv in data/raw first."
        )

    raw_df = pd.read_csv(INPUT_PATH)
    trend_features = prepare_trend_features(raw_df)
    trend_features.to_csv(OUTPUT_PATH, index=False)

    print("Trend features generated successfully.")
    print(f"Input shape: {raw_df.shape}")
    print(f"Output shape: {trend_features.shape}")
    print(f"Saved to: {OUTPUT_PATH}")
    print("\nPreview:")
    print(trend_features.head(10))


if __name__ == "__main__":
    main()