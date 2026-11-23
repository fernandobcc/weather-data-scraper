import json
from pathlib import Path

from weather.config import CITIES_FILE


def load_cities(path: Path = CITIES_FILE) -> list[dict]:
    """Default city list. Each entry needs "City"; Latitude/Longitude are optional (geocoded when missing)."""
    return json.loads(path.read_text(encoding="utf-8"))


def has_coordinates(city: dict) -> bool:
    return city.get("Latitude") is not None and city.get("Longitude") is not None


MAX_CITIES = 25
MAX_NAME_LENGTH = 100


def parse_city_names(raw: str | None) -> list[str]:
    """Split comma-separated input; ValueError past MAX_CITIES names or MAX_NAME_LENGTH characters."""
    names = [n.strip() for n in (raw or "").split(",") if n.strip()]
    if len(names) > MAX_CITIES:
        raise ValueError(f"at most {MAX_CITIES} cities per request")
    if any(len(n) > MAX_NAME_LENGTH for n in names):
        raise ValueError(f"city names are limited to {MAX_NAME_LENGTH} characters")
    return names
