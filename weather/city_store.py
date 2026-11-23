import threading
from functools import lru_cache
from pathlib import Path

import requests
from tinydb import Query, TinyDB

from weather.cities import MAX_CITIES, load_cities
from weather.config import CITIES_DB, CITIES_FILE
from weather.geocoding import geocode


class CityExistsError(Exception):
    pass


class CityLimitError(Exception):
    pass


class CityNotFoundError(Exception):
    pass


class CityStore:
    """Saved city list in TinyDB, seeded from data/cities.json the first time it is created."""

    def __init__(self, path: Path = CITIES_DB, seed: Path = CITIES_FILE):
        path.parent.mkdir(parents=True, exist_ok=True)
        self._table = TinyDB(path, indent=2, ensure_ascii=False).table("cities")
        self._lock = threading.Lock()  # TinyDB is not thread-safe
        if len(self._table) == 0 and seed.exists():
            self._table.insert_multiple(load_cities(seed))

    def all(self) -> list[dict]:
        with self._lock:
            return [dict(doc) for doc in self._table.all()]

    def add(self, name: str, session: requests.Session,
            latitude: float | None = None, longitude: float | None = None) -> dict:
        """Save a city; without coordinates it is geocoded once, here. Raises UpstreamError if the geocoder fails."""
        with self._lock:
            if len(self._table) >= MAX_CITIES:
                raise CityLimitError(f"the list is full ({MAX_CITIES} cities)")
            if self._get(name):
                raise CityExistsError(name.strip())
            if latitude is None or longitude is None:
                city = geocode(name.strip(), session)
                if city is None:
                    raise CityNotFoundError(name.strip())
            else:
                city = {"City": name.strip(), "Latitude": latitude, "Longitude": longitude}
            if self._get(city["City"]):
                raise CityExistsError(city["City"])
            self._table.insert(city)
            return city

    def remove(self, name: str) -> None:
        with self._lock:
            if not self._table.remove(_by_name(name)):
                raise CityNotFoundError(name.strip())

    def _get(self, name: str) -> dict | None:
        doc = self._table.get(_by_name(name))
        return dict(doc) if isinstance(doc, dict) else None


def _by_name(name: str):
    key = name.strip().casefold()
    return Query().City.test(lambda value: str(value).casefold() == key)


@lru_cache(maxsize=1)
def get_store() -> CityStore:
    return CityStore()
