import logging

import requests

from weather.cities import has_coordinates
from weather.config import GEOCODING_URL, HTTP_TIMEOUT
from weather.errors import UpstreamError

log = logging.getLogger(__name__)


def search(name: str, session: requests.Session, count: int = 5) -> list[dict]:
    """Up to `count` Open-Meteo geocoding matches, best first; UpstreamError if the API fails."""
    try:
        resp = session.get(GEOCODING_URL, params={"name": name, "count": count}, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        return [
            {"name": str(hit["name"]), "admin1": str(hit.get("admin1") or ""), "country": str(hit.get("country") or ""),
             "latitude": float(hit["latitude"]), "longitude": float(hit["longitude"])}
            for hit in (resp.json().get("results") or [])[:count]
        ]
    except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise UpstreamError(f"geocoding failed for {name!r}: {exc}") from exc


def geocode(name: str, session: requests.Session) -> dict | None:
    """Best match as a city record; None if not found."""
    matches = search(name, session, count=1)
    if not matches:
        return None
    best = matches[0]
    return {"City": best["name"], "Latitude": best["latitude"], "Longitude": best["longitude"]}


def resolve_cities(names: list[str], session: requests.Session, catalog: list[dict]) -> list[dict]:
    """Names default to the catalog; catalog coordinates win, anything else is geocoded.
    Unknown names are skipped, duplicates dropped."""
    known = {c["City"].casefold(): c for c in catalog if has_coordinates(c)}
    resolved: dict[tuple, dict] = {}
    for name in names or [c["City"] for c in catalog]:
        city = known.get(name.strip().casefold()) or geocode(name, session)
        if city is None:
            log.warning("Could not resolve city %r, skipping", name)
            continue
        resolved.setdefault((city["City"], city["Latitude"], city["Longitude"]), city)
    return list(resolved.values())
