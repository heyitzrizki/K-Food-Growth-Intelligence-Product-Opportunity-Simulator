from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
SYNTHETIC_DIR = BASE_DIR / "data" / "synthetic"
SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


COUNTRIES = [
    "Indonesia",
    "Malaysia",
    "Philippines",
    "Singapore",
    "Thailand",
    "Viet Nam",
    "United States",
    "Australia",
]

COUNTRY_CURRENCY = {
    "Indonesia": "IDR",
    "Malaysia": "MYR",
    "Philippines": "PHP",
    "Singapore": "SGD",
    "Thailand": "THB",
    "Viet Nam": "VND",
    "United States": "USD",
    "Australia": "AUD",
}

FX_TO_USD = {
    "IDR": 1 / 15500,
    "MYR": 1 / 4.7,
    "PHP": 1 / 56,
    "SGD": 1 / 1.35,
    "THB": 1 / 36,
    "VND": 1 / 24500,
    "USD": 1.0,
    "AUD": 1 / 1.52,
}

COUNTRY_PLATFORMS = {
    "Indonesia": ["Shopee ID", "Tokopedia"],
    "Malaysia": ["Shopee MY", "Lazada MY"],
    "Philippines": ["Shopee PH", "Lazada PH"],
    "Singapore": ["FairPrice Online", "Shopee SG"],
    "Thailand": ["Shopee TH", "Lazada TH"],
    "Viet Nam": ["Shopee VN", "Lazada VN"],
    "United States": ["Amazon US", "Walmart"],
    "Australia": ["Amazon AU", "Woolworths"],
}

CATEGORIES = [
    "Korean ramen",
    "Kimchi",
    "Gochujang sauce",
    "Frozen mandu",
    "Ready meal",
    "Seaweed snack",
]

CATEGORY_PRICE_USD_RANGE = {
    "Korean ramen": (1.2, 4.5),
    "Kimchi": (3.5, 12.0),
    "Gochujang sauce": (2.8, 9.5),
    "Frozen mandu": (4.0, 14.0),
    "Ready meal": (3.5, 11.0),
    "Seaweed snack": (1.0, 5.0),
}

CATEGORY_PACK_SIZE_RANGE_G = {
    "Korean ramen": (80, 600),
    "Kimchi": (150, 1000),
    "Gochujang sauce": (200, 1000),
    "Frozen mandu": (300, 1200),
    "Ready meal": (200, 600),
    "Seaweed snack": (10, 100),
}

CATEGORY_FORMATS = {
    "Korean ramen": ["single pack", "multi-pack", "cup noodle"],
    "Kimchi": ["jar", "pouch", "fresh pack"],
    "Gochujang sauce": ["tube", "jar", "squeeze bottle"],
    "Frozen mandu": ["frozen bag", "family pack", "value pack"],
    "Ready meal": ["microwave bowl", "meal kit", "frozen tray"],
    "Seaweed snack": ["snack pack", "multi-pack", "tray pack"],
}

BRAND_TYPES = [
    "Korean Brand",
    "Local Brand",
    "Japanese Brand",
    "Private Label",
    "Premium Import Brand",
]

POSITIONING = ["value", "mainstream", "premium"]


def sample_price_usd(category: str, positioning: str) -> float:
    low, high = CATEGORY_PRICE_USD_RANGE[category]
    price = np.random.uniform(low, high)

    if positioning == "value":
        price *= np.random.uniform(0.75, 0.95)
    elif positioning == "premium":
        price *= np.random.uniform(1.15, 1.55)

    return round(float(price), 2)


def sample_pack_size(category: str) -> int:
    low, high = CATEGORY_PACK_SIZE_RANGE_G[category]
    return int(np.random.randint(low, high + 1))


def sample_rating(positioning: str) -> float:
    if positioning == "premium":
        rating = np.random.normal(4.45, 0.25)
    elif positioning == "mainstream":
        rating = np.random.normal(4.25, 0.35)
    else:
        rating = np.random.normal(4.05, 0.45)

    return round(float(np.clip(rating, 2.8, 5.0)), 1)


def sample_review_count(positioning: str) -> int:
    if positioning == "mainstream":
        return int(np.random.lognormal(mean=4.5, sigma=0.9))
    if positioning == "premium":
        return int(np.random.lognormal(mean=3.8, sigma=0.8))
    return int(np.random.lognormal(mean=4.0, sigma=0.9))


def halal_probability(country: str, category: str) -> float:
    muslim_majority = country in ["Indonesia", "Malaysia"]

    if muslim_majority and category in ["Frozen mandu", "Ready meal", "Korean ramen"]:
        return 0.70
    if muslim_majority:
        return 0.50

    return 0.15


def generate_anonymous_brand(brand_type: str) -> str:
    letter = random.choice(list("ABCDEFGHJKLMNPQRSTUVWXYZ"))
    return f"{brand_type} {letter}"


def generate_product_name(category: str, product_format: str) -> str:
    descriptors = {
        "Korean ramen": ["Spicy Ramen", "Mild Ramen", "Kimchi Ramen", "Cheese Ramen"],
        "Kimchi": ["Cabbage Kimchi", "Fresh Kimchi", "Original Kimchi", "Mild Kimchi"],
        "Gochujang sauce": ["Gochujang Sauce", "Korean Chili Sauce", "Sweet Spicy Sauce"],
        "Frozen mandu": ["Pork Mandu", "Chicken Mandu", "Vegetable Mandu", "Kimchi Mandu"],
        "Ready meal": ["Bibimbap Bowl", "Tteokbokki Meal", "Korean Rice Bowl", "Bulgogi Meal"],
        "Seaweed snack": ["Roasted Seaweed", "Seaweed Snack", "Seaweed Crisps"],
    }

    return f"{random.choice(descriptors[category])} - {product_format}"


def generate_competitor_products(products_per_country_category: int = 8) -> pd.DataFrame:
    rows = []
    product_id = 1

    for country in COUNTRIES:
        currency = COUNTRY_CURRENCY[country]
        fx = FX_TO_USD[currency]

        for category in CATEGORIES:
            for _ in range(products_per_country_category):
                platform = random.choice(COUNTRY_PLATFORMS[country])
                brand_type = random.choices(
                    BRAND_TYPES,
                    weights=[0.42, 0.22, 0.12, 0.14, 0.10],
                    k=1,
                )[0]
                positioning = random.choices(
                    POSITIONING,
                    weights=[0.25, 0.50, 0.25],
                    k=1,
                )[0]

                pack_size_g = sample_pack_size(category)
                product_format = random.choice(CATEGORY_FORMATS[category])
                price_usd = sample_price_usd(category, positioning)
                price_local = round(price_usd / fx, 2)
                price_per_100g = round(price_usd / pack_size_g * 100, 2)
                rating = sample_rating(positioning)
                review_count = max(sample_review_count(positioning), 0)
                halal_claim = np.random.rand() < halal_probability(country, category)

                rows.append(
                    {
                        "product_id": f"P{product_id:04d}",
                        "country": country,
                        "platform": platform,
                        "category": category,
                        "brand_type": brand_type,
                        "anonymous_brand": generate_anonymous_brand(brand_type),
                        "product_name": generate_product_name(category, product_format),
                        "pack_size_g": pack_size_g,
                        "price_local": price_local,
                        "currency": currency,
                        "price_usd": price_usd,
                        "price_per_100g": price_per_100g,
                        "rating": rating,
                        "review_count": review_count,
                        "halal_claim": halal_claim,
                        "product_format": product_format,
                        "positioning": positioning,
                        "data_type": "synthetic_anonymized",
                    }
                )

                product_id += 1

    return pd.DataFrame(rows)


REVIEW_TEMPLATES = {
    "taste_authenticity_positive": [
        "The flavor tastes authentic and reminds me of Korean restaurant food.",
        "I like the rich seasoning and it feels close to real Korean-style food.",
        "The taste is very satisfying and works well for a quick Korean meal at home.",
    ],
    "too_spicy": [
        "The flavor is good, but it is too spicy for my family.",
        "I wish there was a milder version because the spice level is too strong.",
        "The product tastes nice, but the heat level may be difficult for beginners.",
    ],
    "price_sensitivity": [
        "The product is good, but the price feels quite high for the portion size.",
        "I like it, but I would only buy again if there is a discount.",
        "The taste is fine, but it feels expensive compared with local alternatives.",
    ],
    "portion_size": [
        "The portion is smaller than expected.",
        "It tastes good, but one pack is not enough for a full meal.",
        "The serving size could be larger for the price.",
    ],
    "packaging_issue": [
        "The packaging could be improved because it was slightly damaged when delivered.",
        "The product is good, but the packaging does not feel very strong.",
        "The label information could be clearer and easier to read.",
    ],
    "halal_concern": [
        "I would buy this more often if the halal certification was clearly shown.",
        "The product looks good, but I could not find clear halal information.",
        "Clear halal labeling would make me more confident to purchase.",
    ],
    "convenience_positive": [
        "Very convenient for a quick meal after work.",
        "Easy to prepare and good for busy weekdays.",
        "I like that it saves time and still tastes good.",
    ],
    "health_concern": [
        "The taste is nice, but I wish it had less sodium.",
        "I would prefer a healthier version with cleaner ingredients.",
        "Good flavor, but it feels a bit heavy for frequent consumption.",
    ],
}

THEME_PROBABILITIES_BY_CATEGORY = {
    "Korean ramen": {
        "taste_authenticity_positive": 0.22,
        "too_spicy": 0.20,
        "price_sensitivity": 0.15,
        "portion_size": 0.10,
        "packaging_issue": 0.08,
        "halal_concern": 0.08,
        "convenience_positive": 0.12,
        "health_concern": 0.05,
    },
    "Kimchi": {
        "taste_authenticity_positive": 0.28,
        "too_spicy": 0.12,
        "price_sensitivity": 0.14,
        "portion_size": 0.10,
        "packaging_issue": 0.10,
        "halal_concern": 0.05,
        "convenience_positive": 0.08,
        "health_concern": 0.13,
    },
    "Gochujang sauce": {
        "taste_authenticity_positive": 0.25,
        "too_spicy": 0.18,
        "price_sensitivity": 0.12,
        "portion_size": 0.06,
        "packaging_issue": 0.10,
        "halal_concern": 0.08,
        "convenience_positive": 0.10,
        "health_concern": 0.11,
    },
    "Frozen mandu": {
        "taste_authenticity_positive": 0.24,
        "too_spicy": 0.08,
        "price_sensitivity": 0.16,
        "portion_size": 0.12,
        "packaging_issue": 0.10,
        "halal_concern": 0.15,
        "convenience_positive": 0.12,
        "health_concern": 0.03,
    },
    "Ready meal": {
        "taste_authenticity_positive": 0.20,
        "too_spicy": 0.10,
        "price_sensitivity": 0.15,
        "portion_size": 0.10,
        "packaging_issue": 0.08,
        "halal_concern": 0.12,
        "convenience_positive": 0.20,
        "health_concern": 0.05,
    },
    "Seaweed snack": {
        "taste_authenticity_positive": 0.24,
        "too_spicy": 0.04,
        "price_sensitivity": 0.18,
        "portion_size": 0.12,
        "packaging_issue": 0.12,
        "halal_concern": 0.06,
        "convenience_positive": 0.14,
        "health_concern": 0.10,
    },
}


def sample_review_theme(category: str, country: str) -> str:
    theme_probs = THEME_PROBABILITIES_BY_CATEGORY[category].copy()

    if country in ["Indonesia", "Malaysia"]:
        theme_probs["halal_concern"] += 0.10
        theme_probs["taste_authenticity_positive"] -= 0.04
        theme_probs["price_sensitivity"] -= 0.03
        theme_probs["convenience_positive"] -= 0.03

    themes = list(theme_probs.keys())
    probs = np.array([theme_probs[t] for t in themes])
    probs = probs / probs.sum()

    return str(np.random.choice(themes, p=probs))


def rating_from_theme(theme: str) -> int:
    positive_themes = {"taste_authenticity_positive", "convenience_positive"}

    if theme in positive_themes:
        return int(np.random.choice([4, 5], p=[0.35, 0.65]))

    return int(np.random.choice([2, 3, 4], p=[0.25, 0.50, 0.25]))


def generate_product_reviews(
    products_df: pd.DataFrame,
    reviews_per_product: tuple[int, int] = (4, 10),
) -> pd.DataFrame:
    rows = []
    review_id = 1

    for _, product in products_df.iterrows():
        n_reviews = int(np.random.randint(reviews_per_product[0], reviews_per_product[1] + 1))

        for _ in range(n_reviews):
            theme = sample_review_theme(product["category"], product["country"])

            rows.append(
                {
                    "review_id": f"R{review_id:05d}",
                    "product_id": product["product_id"],
                    "country": product["country"],
                    "platform": product["platform"],
                    "category": product["category"],
                    "anonymous_brand": product["anonymous_brand"],
                    "product_name": product["product_name"],
                    "rating": rating_from_theme(theme),
                    "review_text": random.choice(REVIEW_TEMPLATES[theme]),
                    "theme_seed": theme,
                    "data_type": "synthetic_review_corpus",
                }
            )

            review_id += 1

    return pd.DataFrame(rows)


def generate_business_assumptions() -> pd.DataFrame:
    rows = []

    scenario_multipliers = {
        "Conservative": {"units": 0.75, "marketing": 0.85},
        "Base": {"units": 1.00, "marketing": 1.00},
        "Aggressive": {"units": 1.35, "marketing": 1.20},
    }

    category_base_units = {
        "Korean ramen": 120_000,
        "Kimchi": 45_000,
        "Gochujang sauce": 60_000,
        "Frozen mandu": 55_000,
        "Ready meal": 70_000,
        "Seaweed snack": 90_000,
    }

    category_base_price = {
        "Korean ramen": 2.5,
        "Kimchi": 7.0,
        "Gochujang sauce": 5.5,
        "Frozen mandu": 8.5,
        "Ready meal": 6.5,
        "Seaweed snack": 2.8,
    }

    for country in COUNTRIES:
        for category in CATEGORIES:
            for scenario, multipliers in scenario_multipliers.items():
                estimated_units = int(
                    category_base_units[category]
                    * multipliers["units"]
                    * np.random.uniform(0.8, 1.2)
                )
                estimated_price_usd = round(
                    category_base_price[category] * np.random.uniform(0.9, 1.15),
                    2,
                )

                cogs_pct = round(float(np.random.uniform(0.38, 0.52)), 3)
                logistics_pct = round(float(np.random.uniform(0.06, 0.12)), 3)
                marketing_pct = round(
                    float(np.random.uniform(0.08, 0.16) * multipliers["marketing"]),
                    3,
                )
                trade_promo_pct = round(float(np.random.uniform(0.05, 0.12)), 3)
                distributor_margin_pct = round(float(np.random.uniform(0.08, 0.16)), 3)

                gross_revenue = estimated_units * estimated_price_usd
                net_revenue = gross_revenue * (1 - trade_promo_pct)
                cogs = net_revenue * cogs_pct
                logistics = net_revenue * logistics_pct
                marketing = net_revenue * marketing_pct
                distributor_margin = net_revenue * distributor_margin_pct

                contribution_profit = net_revenue - cogs - logistics - marketing - distributor_margin
                contribution_margin_pct = contribution_profit / net_revenue if net_revenue else 0

                rows.append(
                    {
                        "country": country,
                        "category": category,
                        "scenario": scenario,
                        "estimated_units": estimated_units,
                        "estimated_price_usd": estimated_price_usd,
                        "cogs_pct": cogs_pct,
                        "logistics_pct": logistics_pct,
                        "marketing_pct": marketing_pct,
                        "trade_promo_pct": trade_promo_pct,
                        "distributor_margin_pct": distributor_margin_pct,
                        "gross_revenue_usd": round(gross_revenue, 2),
                        "net_revenue_usd": round(net_revenue, 2),
                        "contribution_profit_usd": round(contribution_profit, 2),
                        "contribution_margin_pct": round(contribution_margin_pct, 3),
                        "data_type": "synthetic_business_assumption",
                    }
                )

    return pd.DataFrame(rows)


def main() -> None:
    products_df = generate_competitor_products(products_per_country_category=8)
    reviews_df = generate_product_reviews(products_df, reviews_per_product=(4, 10))
    assumptions_df = generate_business_assumptions()

    products_path = SYNTHETIC_DIR / "synthetic_competitor_products.csv"
    reviews_path = SYNTHETIC_DIR / "synthetic_product_reviews.csv"
    assumptions_path = SYNTHETIC_DIR / "synthetic_business_assumptions.csv"

    products_df.to_csv(products_path, index=False)
    reviews_df.to_csv(reviews_path, index=False)
    assumptions_df.to_csv(assumptions_path, index=False)

    print("Synthetic data generated successfully.")
    print(f"Competitor products: {products_df.shape} -> {products_path}")
    print(f"Product reviews:      {reviews_df.shape} -> {reviews_path}")
    print(f"Business assumptions: {assumptions_df.shape} -> {assumptions_path}")


if __name__ == "__main__":
    main()