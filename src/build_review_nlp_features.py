from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

REVIEWS_PATH = SYNTHETIC_DATA_DIR / "synthetic_product_reviews.csv"
REVIEW_TOPICS_PATH = PROCESSED_DATA_DIR / "review_topics.csv"
REVIEW_FEATURES_PATH = PROCESSED_DATA_DIR / "review_opportunity_features.csv"

N_TOPICS = 8
N_TOP_WORDS = 8


TOPIC_LABEL_RULES = {
    "halal": "Halal trust and certification",
    "certification": "Halal trust and certification",
    "spicy": "Spiciness and taste localization",
    "milder": "Spiciness and taste localization",
    "price": "Price sensitivity",
    "discount": "Price sensitivity",
    "expensive": "Price sensitivity",
    "portion": "Portion size and value perception",
    "serving": "Portion size and value perception",
    "packaging": "Packaging and labeling",
    "label": "Packaging and labeling",
    "convenient": "Convenience and quick meal",
    "quick": "Convenience and quick meal",
    "easy": "Convenience and quick meal",
    "authentic": "Taste authenticity",
    "korean": "Taste authenticity",
    "sodium": "Health and nutrition concern",
    "healthy": "Health and nutrition concern",
    "ingredients": "Health and nutrition concern",
}


NEGATIVE_THEME_SEEDS = {
    "too_spicy",
    "price_sensitivity",
    "portion_size",
    "packaging_issue",
    "halal_concern",
    "health_concern",
}

POSITIVE_THEME_SEEDS = {
    "taste_authenticity_positive",
    "convenience_positive",
}


def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def assign_sentiment_from_rating(rating: int) -> str:
    if rating >= 4:
        return "positive"
    if rating == 3:
        return "neutral"
    return "negative"


def label_topic(topic_words: list[str]) -> str:
    joined_words = " ".join(topic_words)

    for keyword, label in TOPIC_LABEL_RULES.items():
        if keyword in joined_words:
            return label

    return "General product experience"


def build_topic_model(reviews_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = reviews_df.copy()
    df["clean_review_text"] = df["review_text"].apply(clean_text)
    df["sentiment_label"] = df["rating"].apply(assign_sentiment_from_rating)

    vectorizer = TfidfVectorizer(
        max_features=500,
        min_df=2,
        max_df=0.95,
        stop_words="english",
        ngram_range=(1, 2),
    )

    tfidf_matrix = vectorizer.fit_transform(df["clean_review_text"])

    n_topics = min(N_TOPICS, tfidf_matrix.shape[0] - 1)

    model = NMF(
        n_components=n_topics,
        random_state=42,
        init="nndsvda",
        max_iter=500,
    )

    topic_matrix = model.fit_transform(tfidf_matrix)
    topic_assignments = topic_matrix.argmax(axis=1)

    feature_names = np.array(vectorizer.get_feature_names_out())

    topic_rows = []

    for topic_id, topic_weights in enumerate(model.components_):
        top_word_indices = topic_weights.argsort()[::-1][:N_TOP_WORDS]
        top_words = feature_names[top_word_indices].tolist()
        topic_label = label_topic(top_words)

        topic_rows.append(
            {
                "topic_id": topic_id,
                "topic_label": topic_label,
                "top_words": ", ".join(top_words),
            }
        )

    topic_df = pd.DataFrame(topic_rows)

    df["topic_id"] = topic_assignments
    df = df.merge(topic_df, on="topic_id", how="left")

    return df, topic_df


def build_review_opportunity_features(review_level_df: pd.DataFrame) -> pd.DataFrame:
    df = review_level_df.copy()

    df["is_negative_theme"] = df["theme_seed"].isin(NEGATIVE_THEME_SEEDS)
    df["is_positive_theme"] = df["theme_seed"].isin(POSITIVE_THEME_SEEDS)
    df["is_halal_concern"] = df["theme_seed"].eq("halal_concern")
    df["is_spiciness_issue"] = df["theme_seed"].eq("too_spicy")
    df["is_price_issue"] = df["theme_seed"].eq("price_sensitivity")
    df["is_convenience_driver"] = df["theme_seed"].eq("convenience_positive")
    df["is_authenticity_driver"] = df["theme_seed"].eq("taste_authenticity_positive")
    df["is_health_concern"] = df["theme_seed"].eq("health_concern")

    grouped = (
        df.groupby(["country", "category"], as_index=False)
        .agg(
            review_count=("review_id", "count"),
            avg_review_rating=("rating", "mean"),
            negative_theme_share=("is_negative_theme", "mean"),
            positive_theme_share=("is_positive_theme", "mean"),
            halal_concern_share=("is_halal_concern", "mean"),
            spiciness_issue_share=("is_spiciness_issue", "mean"),
            price_issue_share=("is_price_issue", "mean"),
            convenience_driver_share=("is_convenience_driver", "mean"),
            authenticity_driver_share=("is_authenticity_driver", "mean"),
            health_concern_share=("is_health_concern", "mean"),
        )
    )

    grouped["review_opportunity_score"] = (
        grouped["negative_theme_share"] * 0.30
        + grouped["halal_concern_share"] * 0.20
        + grouped["spiciness_issue_share"] * 0.15
        + grouped["price_issue_share"] * 0.15
        + grouped["convenience_driver_share"] * 0.10
        + grouped["authenticity_driver_share"] * 0.10
    )

    grouped["review_opportunity_score"] = (
        grouped["review_opportunity_score"] * 100
    ).round(2)

    grouped["avg_review_rating"] = grouped["avg_review_rating"].round(2)

    share_columns = [
        "negative_theme_share",
        "positive_theme_share",
        "halal_concern_share",
        "spiciness_issue_share",
        "price_issue_share",
        "convenience_driver_share",
        "authenticity_driver_share",
        "health_concern_share",
    ]

    for col in share_columns:
        grouped[col] = grouped[col].round(4)

    return grouped


def main() -> None:
    if not REVIEWS_PATH.exists():
        raise FileNotFoundError(
            f"Missing review file: {REVIEWS_PATH}. "
            "Run python src/generate_synthetic_data.py first."
        )

    reviews_df = pd.read_csv(REVIEWS_PATH)

    review_level_df, topic_df = build_topic_model(reviews_df)
    review_features_df = build_review_opportunity_features(review_level_df)

    review_topics_output = review_level_df[
        [
            "review_id",
            "product_id",
            "country",
            "category",
            "anonymous_brand",
            "rating",
            "review_text",
            "theme_seed",
            "sentiment_label",
            "topic_id",
            "topic_label",
            "top_words",
        ]
    ].copy()

    review_topics_output.to_csv(REVIEW_TOPICS_PATH, index=False)
    review_features_df.to_csv(REVIEW_FEATURES_PATH, index=False)

    print("Review NLP features generated successfully.")
    print(f"Input reviews shape: {reviews_df.shape}")
    print(f"Review topic output shape: {review_topics_output.shape}")
    print(f"Review feature output shape: {review_features_df.shape}")
    print(f"Saved review topics to: {REVIEW_TOPICS_PATH}")
    print(f"Saved review features to: {REVIEW_FEATURES_PATH}")

    print("\nDiscovered topics:")
    print(topic_df)

    print("\nReview opportunity features preview:")
    print(review_features_df.head(10))


if __name__ == "__main__":
    main()