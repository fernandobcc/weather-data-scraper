import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from weather import city_store  # noqa: E402
from weather.city_store import CityStore  # noqa: E402
from weather.config import CITIES_FILE  # noqa: E402


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload, self.status_code = payload, status

    def json(self):
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}")


class FakeSession(requests.Session):
    """Routes GETs by URL substring; records calls for assertions."""

    def __init__(self, routes):
        super().__init__()
        self.routes, self.calls = routes, []

    def get(self, url, params=None, timeout=None, **kwargs):  # pyright: ignore[reportIncompatibleMethodOverride]
        self.calls.append((url, params))
        for key, handler in self.routes.items():
            if key in url:
                return handler(params)
        raise AssertionError(f"unexpected url {url}")


def forecast_handler(params):
    """One location per requested latitude; values grow with the index (city i: 10+i °C)."""
    lats = params["latitude"].split(",")
    locations = [
        {"current": {"time": "2026-11-23T19:00", "temperature_2m": 10.0 + i,
                     "relative_humidity_2m": 50 + i, "wind_speed_10m": 2.0 + i}}
        for i in range(len(lats))
    ]
    return FakeResponse(locations if len(locations) > 1 else locations[0])


def geocoding_handler(params):
    """Knows only Lisbon."""
    if params["name"].lower() == "lisbon":
        return FakeResponse({"results": [{"name": "Lisbon", "latitude": 38.72, "longitude": -9.14}]})
    return FakeResponse({})


@pytest.fixture
def fake_session():
    return FakeSession({"forecast": forecast_handler, "geocoding": geocoding_handler})


@pytest.fixture(autouse=True)
def store(tmp_path, monkeypatch):
    """Every test gets a fresh TinyDB seeded with the brief's cities; the real db/ is never touched."""
    test_store = CityStore(tmp_path / "cities.json", CITIES_FILE)
    monkeypatch.setattr(city_store, "get_store", lambda: test_store)
    return test_store
