import logging

import requests

from weather.cities import DEFAULT_CITIES, known_city
from weather.config import GEOCODING_URL, HTTP_TIMEOUT

log = logging.getLogger(__name__)


def geocode(name: str, session: requests.Session) -> dict | None:
    """Look up a city name on the Open-Meteo geocoding API (best match only)."""
    resp = session.get(GEOCODING_URL, params={"name": name, "count": 1}, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    results = resp.json().get("results") or []
    if not results:
        return None
    hit = results[0]
    return {"City": hit["name"], "Latitude": hit["latitude"], "Longitude": hit["longitude"]}


def _safe_geocode(name: str, session: requests.Session) -> dict | None:
    try:
        return geocode(name, session)
    except (requests.RequestException, ValueError, KeyError) as exc:
        log.warning("Geocoding failed for %r: %s", name, exc)
        return None


def resolve_cities(names: list[str], session: requests.Session) -> list[dict]:
    """Known cities come from the attached dict; anything else is geocoded. Duplicates are dropped."""
    if not names:
        return list(DEFAULT_CITIES)
    resolved: dict[tuple, dict] = {}
    for name in names:
        city = known_city(name) or _safe_geocode(name, session)
        if city is None:
            log.warning("Could not resolve city %r, skipping", name)
            continue
        resolved.setdefault((city["City"], city["Latitude"], city["Longitude"]), city)
    return list(resolved.values())
