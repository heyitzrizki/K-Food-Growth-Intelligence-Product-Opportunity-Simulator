from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUTS_DIR = BASE_DIR / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
REPORTS_DIR = OUTPUTS_DIR / "reports"

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

COUNTRY_CODES = {
    "Indonesia": "ID",
    "Malaysia": "MY",
    "Philippines": "PH",
    "Singapore": "SG",
    "Thailand": "TH",
    "Viet Nam": "VN",
    "United States": "US",
    "Australia": "AU",
}

CATEGORIES = [
    "Korean ramen",
    "Kimchi",
    "Gochujang sauce",
    "Frozen mandu",
    "Ready meal",
    "Seaweed snack",
]

GOOGLE_TRENDS_KEYWORDS = [
    "korean food",
    "kimchi",
    "gochujang",
    "tteokbokki",
    "korean ramen",
    "bibigo",
]