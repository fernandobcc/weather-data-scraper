import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

FORECAST_URL = os.getenv("OPEN_METEO_FORECAST_URL", "https://api.open-meteo.com/v1/forecast")
GEOCODING_URL = os.getenv("OPEN_METEO_GEOCODING_URL", "https://geocoding-api.open-meteo.com/v1/search")
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10"))
OUTPUT_DIR = ROOT / os.getenv("OUTPUT_DIR", "output")
CSV_NAME = "weather_data.csv"
CITIES_FILE = ROOT / os.getenv("CITIES_FILE", "data/cities.json")  # seed for the city store
CITIES_DB = ROOT / os.getenv("CITIES_DB", "db/cities.json")
