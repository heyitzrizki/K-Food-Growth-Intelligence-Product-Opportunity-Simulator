from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
from pytrends.request import TrendReq


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = RAW_DATA_DIR / "google_trends_kfood.csv"


COUNTRIES = {
    "Indonesia": "ID",
    "Malaysia": "MY",
    "Philippines": "PH",
    "Singapore": "SG",
    "Thailand": "TH",
    "Viet Nam": "VN",
    "United States": "US",
    "Australia": "AU",
}

KEYWORDS = [
    "korean food",
    "kimchi",
    "gochujang",
    "tteokbokki",
    "korean ramen",
    "bibigo",
]

TIMEFRAME = "2019-01-01 2024-12-31"


def fetch_keyword_trend(
    pytrends: TrendReq,
    country: str,
    geo: str,
    keyword: str,
    retries: int = 3,
    sleep_seconds: int = 5,
) -> pd.DataFrame:
    for attempt in range(1, retries + 1):
        try:
            pytrends.build_payload(
                kw_list=[keyword],
                cat=0,
                timeframe=TIMEFRAME,
                geo=geo,
                gprop="",
            )

            df = pytrends.interest_over_time()

            if df.empty:
                print(f"No data: {country} | {keyword}")
                return pd.DataFrame()

            df = df.reset_index()

            if "isPartial" not in df.columns:
                df["isPartial"] = False

            df = df.rename(
                columns={
                    keyword: "search_interest",
                    "isPartial": "is_partial",
                }
            )

            df["country"] = country
            df["geo"] = geo
            df["keyword"] = keyword

            return df[
                [
                    "date",
                    "country",
                    "geo",
                    "keyword",
                    "search_interest",
                    "is_partial",
                ]
            ]

        except Exception as error:
            print(
                f"Attempt {attempt}/{retries} failed: "
                f"{country} | {keyword} | {error}"
            )
            time.sleep(sleep_seconds * attempt)

    print(f"Failed after retries: {country} | {keyword}")
    return pd.DataFrame()


def fetch_all_trends() -> pd.DataFrame:
    pytrends = TrendReq(
        hl="en-US",
        tz=360,
        timeout=(10, 25)
    )

    all_results = []

    total_jobs = len(COUNTRIES) * len(KEYWORDS)
    job_number = 1

    for country, geo in COUNTRIES.items():
        for keyword in KEYWORDS:
            print(f"[{job_number}/{total_jobs}] Fetching: {country} | {keyword}")

            df = fetch_keyword_trend(
                pytrends=pytrends,
                country=country,
                geo=geo,
                keyword=keyword,
            )

            if not df.empty:
                all_results.append(df)

            job_number += 1
            time.sleep(3)

    if not all_results:
        raise RuntimeError("No Google Trends data were fetched.")

    trends_df = pd.concat(all_results, ignore_index=True)
    trends_df["date"] = pd.to_datetime(trends_df["date"])
    trends_df["search_interest"] = pd.to_numeric(
        trends_df["search_interest"],
        errors="coerce",
    )

    return trends_df


def main() -> None:
    trends_df = fetch_all_trends()
    trends_df.to_csv(OUTPUT_PATH, index=False)

    print("\nGoogle Trends data saved successfully.")
    print(f"Shape: {trends_df.shape}")
    print(f"Path: {OUTPUT_PATH}")
    print("\nPreview:")
    print(trends_df.head())


if __name__ == "__main__":
    main()