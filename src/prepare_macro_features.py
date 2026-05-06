from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT_PATH = RAW_DATA_DIR / "worldbank_macro_indicators_2014_2024.xlsx"
OUTPUT_PATH = PROCESSED_DATA_DIR / "macro_features.csv"

COUNTRIES = [
    "Australia",
    "Indonesia",
    "Malaysia",
    "Philippines",
    "Singapore",
    "Thailand",
    "United States",
    "Viet Nam",
]

YEARS = [str(year) for year in range(2014, 2025)]


def find_header_row(path: Path, sheet_name: str = "Data") -> int:
    preview = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=20)

    for idx, row in preview.iterrows():
        values = row.astype(str).str.strip().tolist()
        if "Country Name" in values and "Series Name" in values:
            return idx

    raise ValueError(
        "Could not find the header row containing 'Country Name' and 'Series Name'."
    )


def clean_column_name(column: object) -> str:
    text = str(column).strip()

    if "[" in text:
        text = text.split("[")[0].strip()

    return text


def load_worldbank_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"World Bank file not found: {path}. "
            "Place the file in data/raw/ and rename it to "
            "worldbank_macro_indicators_2014_2024.xlsx."
        )

    header_row = find_header_row(path)
    df = pd.read_excel(path, sheet_name="Data", header=header_row)
    df.columns = [clean_column_name(col) for col in df.columns]

    df = df.dropna(how="all").copy()

    required_columns = ["Country Name", "Country Code", "Series Name", "Series Code"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Missing expected columns after header detection: {missing_columns}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    df = df[df["Country Name"].isin(COUNTRIES)].copy()

    year_columns = [col for col in df.columns if col in YEARS]
    if not year_columns:
        raise ValueError(
            f"No expected year columns found. Available columns: {df.columns.tolist()}"
        )

    return df


def map_series_name(series_name: str) -> str | None:
    text = str(series_name).lower()

    if "population, total" in text:
        return "population"

    if "gdp per capita" in text and "current" in text:
        return "gdp_per_capita_usd"

    if "urban population" in text and "% of total population" in text:
        return "urban_population_pct"

    if "individuals using the internet" in text:
        return "internet_users_pct"

    if "final consumption expenditure" in text and "current" in text:
        return "household_consumption_usd"

    if "inflation" in text and "consumer prices" in text:
        return "inflation_pct"

    return None


def reshape_macro_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["indicator"] = df["Series Name"].apply(map_series_name)
    df = df[df["indicator"].notna()].copy()

    if df.empty:
        unique_series = sorted(df["Series Name"].dropna().unique().tolist())
        raise ValueError(
            "No mapped indicators found. Check the Series Name values.\n"
            f"Available series: {unique_series}"
        )

    available_years = [col for col in YEARS if col in df.columns]

    long_df = df.melt(
        id_vars=["Country Name", "Country Code", "Series Name", "Series Code", "indicator"],
        value_vars=available_years,
        var_name="year",
        value_name="value",
    )

    long_df["value"] = (
        long_df["value"]
        .replace("..", np.nan)
        .replace("", np.nan)
    )
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
    long_df["year"] = long_df["year"].astype(int)

    wide_df = (
        long_df.pivot_table(
            index=["Country Name", "Country Code", "year"],
            columns="indicator",
            values="value",
            aggfunc="first",
        )
        .reset_index()
        .rename(
            columns={
                "Country Name": "country",
                "Country Code": "country_code",
            }
        )
    )

    wide_df.columns.name = None

    return wide_df


def forward_fill_by_country(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["country", "year"]).copy()

    feature_columns = [
        "population",
        "gdp_per_capita_usd",
        "urban_population_pct",
        "internet_users_pct",
        "household_consumption_usd",
        "inflation_pct",
    ]

    for col in feature_columns:
        if col in df.columns:
            df[col] = df.groupby("country")[col].ffill()

    return df


def get_latest_complete_year(df: pd.DataFrame) -> int:
    core_columns = [
        "population",
        "gdp_per_capita_usd",
        "urban_population_pct",
        "internet_users_pct",
        "household_consumption_usd",
        "inflation_pct",
    ]

    available_core_columns = [col for col in core_columns if col in df.columns]

    completeness = (
        df.groupby("year")[available_core_columns]
        .apply(lambda x: x.notna().mean().mean())
        .reset_index(name="completeness")
        .sort_values("year", ascending=False)
    )

    complete_years = completeness[completeness["completeness"] >= 0.85]

    if complete_years.empty:
        return int(completeness.iloc[0]["year"])

    return int(complete_years.iloc[0]["year"])


def add_macro_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    score_year = get_latest_complete_year(df)
    latest_df = df[df["year"] == score_year].copy()

    positive_features = [
        "population",
        "gdp_per_capita_usd",
        "urban_population_pct",
        "internet_users_pct",
        "household_consumption_usd",
    ]

    available_positive_features = [
        col for col in positive_features if col in latest_df.columns
    ]

    for col in available_positive_features:
        latest_df[col] = latest_df[col].fillna(latest_df[col].median())

    scaler = MinMaxScaler()
    score_columns = []

    if available_positive_features:
        scaled_values = scaler.fit_transform(latest_df[available_positive_features])

        for idx, col in enumerate(available_positive_features):
            score_col = f"{col}_score"
            latest_df[score_col] = scaled_values[:, idx]
            score_columns.append(score_col)

    if "inflation_pct" in latest_df.columns:
        inflation = latest_df[["inflation_pct"]].copy()
        inflation["inflation_pct"] = inflation["inflation_pct"].fillna(
            inflation["inflation_pct"].median()
        )

        latest_df["inflation_risk_score"] = 1 - MinMaxScaler().fit_transform(inflation)
        score_columns.append("inflation_risk_score")

    latest_df["macro_potential_score"] = latest_df[score_columns].mean(axis=1)

    score_df = latest_df[
        [
            "country",
            *score_columns,
            "macro_potential_score",
        ]
    ].copy()

    score_df["macro_score_year"] = score_year

    return df.merge(score_df, on="country", how="left")


def main() -> None:
    raw_df = load_worldbank_data(INPUT_PATH)
    macro_df = reshape_macro_data(raw_df)
    macro_df = forward_fill_by_country(macro_df)
    macro_features = add_macro_scores(macro_df)

    macro_features.to_csv(OUTPUT_PATH, index=False)

    print("Macro features generated successfully.")
    print(f"Raw input shape: {raw_df.shape}")
    print(f"Output shape: {macro_features.shape}")
    print(f"Saved to: {OUTPUT_PATH}")
    print("\nColumns:")
    print(macro_features.columns.tolist())
    print("\nPreview:")
    print(macro_features.head())


if __name__ == "__main__":
    main()