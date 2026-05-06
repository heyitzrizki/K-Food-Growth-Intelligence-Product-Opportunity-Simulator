from __future__ import annotations

import random
import time
from pathlib import Path

import pandas as pd
from pytrends.request import TrendReq


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = RAW_DATA_DIR / "google_trends_kfood.csv"
FAILED_PATH = RAW_DATA_DIR / "failed_google_trends_queries.csv"

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


def wait(min_seconds: int = 12, max_seconds: int = 25) -> None:
    delay = random.randint(min_seconds, max_seconds)
    print(f"Waiting {delay} seconds...")
    time.sleep(delay)


def create_pytrends_client() -> TrendReq:
    return TrendReq(
        hl="en-US",
        tz=360,
        timeout=(10, 25),
    )


def fetch_keyword_trend(
    country: str,
    geo: str,
    keyword: str,
    retries: int = 4,
) -> tuple[pd.DataFrame, dict | None]:
    for attempt in range(1, retries + 1):
        try:
            pytrends = create_pytrends_client()

            pytrends.build_payload(
                kw_list=[keyword],
                cat=0,
                timeframe=TIMEFRAME,
                geo=geo,
                gprop="",
            )

            df = pytrends.interest_over_time()

            if df.empty:
                print(f"No data returned: {country} | {keyword}")
                return pd.DataFrame(), {
                    "country": country,
                    "geo": geo,
                    "keyword": keyword,
                    "reason": "empty_result",
                }

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

            return (
                df[
                    [
                        "date",
                        "country",
                        "geo",
                        "keyword",
                        "search_interest",
                        "is_partial",
                    ]
                ],
                None,
            )

        except Exception as error:
            error_message = str(error)
            print(
                f"Attempt {attempt}/{retries} failed: "
                f"{country} | {keyword} | {error_message}"
            )

            if "429" in error_message:
                backoff = 60 * attempt
            else:
                backoff = 15 * attempt

            print(f"Retrying after {backoff} seconds...")
            time.sleep(backoff)

    return pd.DataFrame(), {
        "country": country,
        "geo": geo,
        "keyword": keyword,
        "reason": "failed_after_retries",
    }


def fetch_all_trends() -> tuple[pd.DataFrame, pd.DataFrame]:
    all_results = []
    failed_queries = []

    jobs = [
        (country, geo, keyword)
        for country, geo in COUNTRIES.items()
        for keyword in KEYWORDS
    ]

    total_jobs = len(jobs)

    for job_number, (country, geo, keyword) in enumerate(jobs, start=1):
        print(f"\n[{job_number}/{total_jobs}] Fetching: {country} | {keyword}")

        df, failed_query = fetch_keyword_trend(
            country=country,
            geo=geo,
            keyword=keyword,
        )

        if not df.empty:
            all_results.append(df)

        if failed_query is not None:
            failed_queries.append(failed_query)

        wait(12, 25)

    if all_results:
        trends_df = pd.concat(all_results, ignore_index=True)
        trends_df["date"] = pd.to_datetime(trends_df["date"])
        trends_df["search_interest"] = pd.to_numeric(
            trends_df["search_interest"],
            errors="coerce",
        )
    else:
        trends_df = pd.DataFrame(
            columns=[
                "date",
                "country",
                "geo",
                "keyword",
                "search_interest",
                "is_partial",
            ]
        )

    failed_df = pd.DataFrame(failed_queries)

    return trends_df, failed_df


def main() -> None:
    trends_df, failed_df = fetch_all_trends()

    trends_df.to_csv(OUTPUT_PATH, index=False)
    failed_df.to_csv(FAILED_PATH, index=False)

    print("\nGoogle Trends data collection completed.")
    print(f"Successful data shape: {trends_df.shape}")
    print(f"Saved to: {OUTPUT_PATH}")

    if not failed_df.empty:
        print(f"\nFailed queries: {failed_df.shape[0]}")
        print(f"Failed query log saved to: {FAILED_PATH}")
        print(failed_df)
    else:
        print("\nNo failed queries.")


if __name__ == "__main__":
    main()