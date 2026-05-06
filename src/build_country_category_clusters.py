from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

MARKET_SCORES_PATH = PROCESSED_DATA_DIR / "market_opportunity_scores.csv"
OUTPUT_PATH = PROCESSED_DATA_DIR / "country_category_clusters.csv"

N_CLUSTERS = 4
RANDOM_STATE = 42


CLUSTER_FEATURES = [
    "consumer_interest_score",
    "trend_momentum_score",
    "macro_potential_score",
    "market_gap_score",
    "review_opportunity_score_scaled",
    "price_feasibility_score",
    "trend_consistency_score",
]


def load_market_scores() -> pd.DataFrame:
    if not MARKET_SCORES_PATH.exists():
        raise FileNotFoundError(
            f"Missing market opportunity scores: {MARKET_SCORES_PATH}. "
            "Run python src/build_market_opportunity_scores.py first."
        )

    return pd.read_csv(MARKET_SCORES_PATH)


def prepare_clustering_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    available_features = [col for col in CLUSTER_FEATURES if col in df.columns]

    if len(available_features) < 3:
        raise ValueError(
            "Not enough clustering features found. "
            f"Available expected features: {available_features}"
        )

    feature_df = df[available_features].copy()

    for col in available_features:
        feature_df[col] = pd.to_numeric(feature_df[col], errors="coerce")
        feature_df[col] = feature_df[col].fillna(feature_df[col].median())

    scaler = StandardScaler()
    scaled_matrix = scaler.fit_transform(feature_df)

    return feature_df, scaled_matrix


def assign_cluster_labels(cluster_summary: pd.DataFrame) -> dict[int, str]:
    labels = {}

    for _, row in cluster_summary.iterrows():
        cluster_id = int(row["cluster"])

        consumer = row.get("consumer_interest_score", 0)
        momentum = row.get("trend_momentum_score", 0)
        macro = row.get("macro_potential_score", 0)
        review = row.get("review_opportunity_score_scaled", 0)
        gap = row.get("market_gap_score", 0)
        price = row.get("price_feasibility_score", 0)

        if consumer >= 0.60 and momentum >= 0.55:
            labels[cluster_id] = "High-Interest Growth Opportunities"
        elif macro >= 0.60 and price >= 0.50:
            labels[cluster_id] = "Macro-Ready Commercial Markets"
        elif review >= 0.60:
            labels[cluster_id] = "Review-Driven Product Adaptation Markets"
        elif gap >= 0.60:
            labels[cluster_id] = "Open Competitive Space Markets"
        else:
            labels[cluster_id] = "Watchlist / Low-Signal Markets"

    return labels


def build_clusters(df: pd.DataFrame) -> pd.DataFrame:
    output_df = df.copy()

    feature_df, scaled_matrix = prepare_clustering_matrix(output_df)

    n_clusters = min(N_CLUSTERS, len(output_df))

    model = KMeans(
        n_clusters=n_clusters,
        random_state=RANDOM_STATE,
        n_init=20,
    )

    output_df["cluster"] = model.fit_predict(scaled_matrix)

    cluster_summary = (
        output_df.groupby("cluster", as_index=False)[CLUSTER_FEATURES]
        .mean(numeric_only=True)
        .round(3)
    )

    cluster_labels = assign_cluster_labels(cluster_summary)
    output_df["cluster_label"] = output_df["cluster"].map(cluster_labels)

    output_df["cluster_size"] = output_df.groupby("cluster")["cluster"].transform("count")

    selected_columns = [
        "rank",
        "country",
        "category",
        "product_opportunity_score",
        "recommended_action",
        "cluster",
        "cluster_label",
        "cluster_size",
        *[col for col in CLUSTER_FEATURES if col in output_df.columns],
        "business_rationale",
    ]

    selected_columns = [col for col in selected_columns if col in output_df.columns]

    return output_df[selected_columns].sort_values(
        ["cluster", "product_opportunity_score"],
        ascending=[True, False],
    )


def main() -> None:
    market_scores = load_market_scores()
    clustered_df = build_clusters(market_scores)
    clustered_df.to_csv(OUTPUT_PATH, index=False)

    print("Country-category clusters generated successfully.")
    print(f"Output shape: {clustered_df.shape}")
    print(f"Saved to: {OUTPUT_PATH}")

    print("\nCluster summary:")
    summary = (
        clustered_df.groupby(["cluster", "cluster_label"], as_index=False)
        .agg(
            cluster_size=("cluster_size", "first"),
            avg_opportunity_score=("product_opportunity_score", "mean"),
            top_country=("country", "first"),
            top_category=("category", "first"),
        )
    )
    summary["avg_opportunity_score"] = summary["avg_opportunity_score"].round(2)
    print(summary)

    print("\nPreview:")
    print(
        clustered_df[
            [
                "country",
                "category",
                "product_opportunity_score",
                "cluster_label",
                "recommended_action",
            ]
        ].head(12)
    )


if __name__ == "__main__":
    main()