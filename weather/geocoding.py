import logging

import requests

from weather.cities import DEFAULT_CITIES, known_city
from weather.config import GEOCODING_URL, HTTP_TIMEOUT
from weather.errors import UpstreamError

log = logging.getLogger(__name__)


def geocode(name: str, session: requests.Session) -> dict | None:
    """Best match on the Open-Meteo geocoding API; None if not found, UpstreamError if the API fails."""
    try:
        resp = session.get(GEOCODING_URL, params={"name": name, "count": 1}, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("results") or []
        if not results:
            return None
        hit = results[0]
        return {"City": str(hit["name"]), "Latitude": float(hit["latitude"]), "Longitude": float(hit["longitude"])}
    except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise UpstreamError(f"geocoding failed for {name!r}: {exc}") from exc


def resolve_cities(names: list[str], session: requests.Session) -> list[dict]:
    """Known cities come from the attached dict; anything else is geocoded. Unknown names are skipped, duplicates dropped."""
    if not names:
        return list(DEFAULT_CITIES)
    resolved: dict[tuple, dict] = {}
    for name in names:
        city = known_city(name) or geocode(name, session)
        if city is None:
            log.warning("Could not resolve city %r, skipping", name)
            continue
        resolved.setdefault((city["City"], city["Latitude"], city["Longitude"]), city)
    return list(resolved.values())
