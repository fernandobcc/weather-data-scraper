import requests

from weather.config import FORECAST_URL, HTTP_TIMEOUT
from weather.errors import UpstreamError

CURRENT_FIELDS = "temperature_2m,relative_humidity_2m,wind_speed_10m"


def fetch_current_weather(cities: list[dict], session: requests.Session) -> list[dict]:
    """Fetch current weather for all cities in a single Open-Meteo call."""
    if not cities:
        return []
    params = {
        "latitude": ",".join(str(c["Latitude"]) for c in cities),
        "longitude": ",".join(str(c["Longitude"]) for c in cities),
        "current": CURRENT_FIELDS,
        "temperature_unit": "celsius",
        "wind_speed_unit": "ms",
        "timezone": "UTC",
    }
    try:
        resp = session.get(FORECAST_URL, params=params, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        payload = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise UpstreamError(f"forecast request failed: {exc}") from exc

    # A single location returns an object, several return a list.
    locations = payload if isinstance(payload, list) else [payload]
    if len(locations) != len(cities):
        raise UpstreamError(f"expected {len(cities)} locations, got {len(locations)}")
    try:
        return [_to_record(city, loc["current"]) for city, loc in zip(cities, locations, strict=True)]
    except (KeyError, TypeError) as exc:
        raise UpstreamError(f"unexpected forecast payload: {exc!r}") from exc


def _to_record(city: dict, current: dict) -> dict:
    return {
        "City": city["City"],
        "Latitude": city["Latitude"],
        "Longitude": city["Longitude"],
        "Temperature (C)": _number(current["temperature_2m"]),
        "Humidity (%)": _number(current["relative_humidity_2m"]),
        "Wind Speed (m/s)": _number(current["wind_speed_10m"]),
        "Observed At (UTC)": str(current["time"]),
    }


def _number(value: object) -> float | None:
    """Open-Meteo sends numbers or null; anything else is a malformed payload."""
    if value is None or (isinstance(value, (int, float)) and not isinstance(value, bool)):
        return value
    raise TypeError(f"expected a number or null, got {value!r}")
