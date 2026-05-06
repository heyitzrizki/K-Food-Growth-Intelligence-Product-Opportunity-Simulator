from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

MARKET_SCORES_PATH = PROCESSED_DATA_DIR / "market_opportunity_scores.csv"
OUTPUT_PATH = PROCESSED_DATA_DIR / "product_idea_recommendations.csv"


MUSLIM_MAJOR_MARKETS = {"Indonesia", "Malaysia"}

CATEGORY_BASE_IDEAS = {
    "Korean ramen": {
        "default": "Localized Korean ramen multi-pack",
        "halal": "Halal-certified Korean ramen multi-pack",
        "mild": "Mild-spicy Korean ramen for beginner K-Food consumers",
        "value": "Affordable Korean ramen value bundle",
        "health": "Lower-sodium Korean ramen line",
    },
    "Kimchi": {
        "default": "Fresh kimchi starter pack",
        "halal": "Halal-certified kimchi with clear ingredient labeling",
        "mild": "Mild kimchi for mainstream consumers",
        "value": "Family-size kimchi value pack",
        "health": "Low-sodium kimchi line",
    },
    "Gochujang sauce": {
        "default": "Korean sauce starter kit",
        "halal": "Halal-certified gochujang sauce",
        "mild": "Mild-spicy gochujang sauce for localized taste preference",
        "value": "Affordable gochujang cooking sauce bundle",
        "health": "Clean-label gochujang sauce with reduced sodium",
    },
    "Frozen mandu": {
        "default": "Frozen Korean mandu family pack",
        "halal": "Halal-certified frozen mandu for Muslim-majority markets",
        "mild": "Mild-flavor frozen mandu for mainstream consumers",
        "value": "Affordable frozen mandu value pack",
        "health": "Vegetable-forward frozen mandu line",
    },
    "Ready meal": {
        "default": "Microwaveable Korean ready meal",
        "halal": "Halal-certified microwaveable Korean ready meal",
        "mild": "Mild-spicy Korean ready meal for localized taste preference",
        "value": "Affordable Korean ready meal lunch pack",
        "health": "Balanced Korean ready meal with cleaner ingredients",
    },
    "Seaweed snack": {
        "default": "Korean seaweed snack multi-pack",
        "halal": "Halal-friendly Korean seaweed snack",
        "mild": "Lightly seasoned Korean seaweed snack",
        "value": "Affordable Korean seaweed snack bundle",
        "health": "Low-sodium Korean seaweed snack",
    },
}


def load_market_scores() -> pd.DataFrame:
    if not MARKET_SCORES_PATH.exists():
        raise FileNotFoundError(
            f"Missing market opportunity scores: {MARKET_SCORES_PATH}. "
            "Run python src/build_market_opportunity_scores.py first."
        )

    return pd.read_csv(MARKET_SCORES_PATH)


def choose_product_idea(row: pd.Series) -> tuple[str, str]:
    country = row["country"]
    category = row["category"]
    base_ideas = CATEGORY_BASE_IDEAS.get(category, {})

    halal_concern = row.get("halal_concern_share", 0)
    spiciness_issue = row.get("spiciness_issue_share", 0)
    price_issue = row.get("price_issue_share", 0)
    health_concern = row.get("health_concern_share", 0)

    if country in MUSLIM_MAJOR_MARKETS and halal_concern >= 0.10:
        return base_ideas.get("halal", base_ideas.get("default")), (
            "High halal-related concern in review signals and strong relevance "
            "for Muslim-majority markets."
        )

    if spiciness_issue >= 0.15:
        return base_ideas.get("mild", base_ideas.get("default")), (
            "Review signals indicate spiciness localization as an important product adaptation need."
        )

    if price_issue >= 0.15:
        return base_ideas.get("value", base_ideas.get("default")), (
            "Review signals indicate price sensitivity and value-for-money concerns."
        )

    if health_concern >= 0.10:
        return base_ideas.get("health", base_ideas.get("default")), (
            "Review signals indicate consumer concern around health, sodium, or ingredient quality."
        )

    return base_ideas.get("default", f"{category} product concept"), (
        "Product idea is based on category-level opportunity signals and overall market attractiveness."
    )


def infer_target_segment(row: pd.Series) -> str:
    country = row["country"]
    category = row["category"]

    if country in MUSLIM_MAJOR_MARKETS and row.get("halal_concern_share", 0) >= 0.10:
        return "Muslim Gen Z and young family consumers seeking trusted halal K-Food options"

    if category in {"Ready meal", "Korean ramen"}:
        return "Urban young professionals and students seeking convenient K-Food meals"

    if category in {"Kimchi", "Gochujang sauce"}:
        return "Home cooks and K-Food enthusiasts seeking authentic Korean flavors"

    if category == "Frozen mandu":
        return "Young families and convenience-focused consumers"

    return "Mainstream K-Food snack and convenience consumers"


def infer_channel_strategy(row: pd.Series) -> str:
    category = row["category"]

    if category in {"Korean ramen", "Seaweed snack"}:
        return "E-commerce, convenience stores, and modern retail"

    if category in {"Frozen mandu", "Ready meal"}:
        return "Modern grocery, frozen section, e-commerce grocery, and food delivery partnerships"

    if category in {"Kimchi", "Gochujang sauce"}:
        return "Modern grocery, specialty Asian stores, and e-commerce"

    return "E-commerce and modern retail"


def classify_priority(score: float) -> str:
    if score >= 75:
        return "High"
    if score >= 60:
        return "Medium-High"
    if score >= 45:
        return "Medium"
    return "Low"


def build_product_idea_recommendations(market_scores: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for _, row in market_scores.iterrows():
        product_idea, idea_rationale = choose_product_idea(row)

        rows.append(
            {
                "rank": row["rank"],
                "country": row["country"],
                "category": row["category"],
                "product_idea": product_idea,
                "target_segment": infer_target_segment(row),
                "channel_strategy": infer_channel_strategy(row),
                "product_opportunity_score": row["product_opportunity_score"],
                "priority_level": classify_priority(row["product_opportunity_score"]),
                "recommended_action": row["recommended_action"],
                "idea_rationale": idea_rationale,
                "business_rationale": row["business_rationale"],
                "consumer_interest_score": row.get("consumer_interest_score"),
                "trend_momentum_score": row.get("trend_momentum_score"),
                "macro_potential_score": row.get("macro_potential_score"),
                "review_opportunity_score": row.get("review_opportunity_score"),
                "halal_concern_share": row.get("halal_concern_share"),
                "spiciness_issue_share": row.get("spiciness_issue_share"),
                "price_issue_share": row.get("price_issue_share"),
                "health_concern_share": row.get("health_concern_share"),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    market_scores = load_market_scores()
    product_ideas = build_product_idea_recommendations(market_scores)
    product_ideas.to_csv(OUTPUT_PATH, index=False)

    display_columns = [
        "rank",
        "country",
        "category",
        "product_idea",
        "priority_level",
        "product_opportunity_score",
        "recommended_action",
    ]

    print("Product idea recommendations generated successfully.")
    print(f"Output shape: {product_ideas.shape}")
    print(f"Saved to: {OUTPUT_PATH}")
    print("\nTop 10 product ideas:")
    print(product_ideas[display_columns].head(10))


if __name__ == "__main__":
    main()