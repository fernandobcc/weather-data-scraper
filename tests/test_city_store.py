import pytest
import requests

from tests.conftest import FakeSession
from weather.cities import MAX_CITIES
from weather.city_store import CityExistsError, CityLimitError, CityNotFoundError, CityStore
from weather.errors import UpstreamError


def test_seeded_once_from_data_file(store, tmp_path):
    assert len(store.all()) == 10
    store.remove("Tokyo")
    reopened = CityStore(tmp_path / "cities.json", tmp_path / "missing-seed.json")
    assert len(reopened.all()) == 9


def test_add_with_coordinates_skips_geocoding(store, fake_session):
    city = store.add(" Porto ", fake_session, 41.15, -8.61)
    assert city == {"City": "Porto", "Latitude": 41.15, "Longitude": -8.61}
    assert fake_session.calls == []


def test_add_geocodes_once_and_persists(store, fake_session, tmp_path):
    store.add("lisbon", fake_session)
    reopened = CityStore(tmp_path / "cities.json")
    assert {"City": "Lisbon", "Latitude": 38.72, "Longitude": -9.14} in reopened.all()


def test_duplicate_is_rejected_case_insensitively(store, fake_session):
    with pytest.raises(CityExistsError):
        store.add("  paris ", fake_session)


def test_unknown_city(store, fake_session):
    with pytest.raises(CityNotFoundError):
        store.add("Atlantis", fake_session)


def test_geocoder_outage(store):
    def broken(params):
        raise requests.ConnectionError("down")

    with pytest.raises(UpstreamError):
        store.add("Lisbon", FakeSession({"geocoding": broken}))


def test_list_is_capped(store, fake_session):
    for i in range(MAX_CITIES - 10):
        store.add(f"Town {i}", fake_session, 0.0, float(i))
    with pytest.raises(CityLimitError):
        store.add("One too many", fake_session, 1.0, 1.0)


def test_remove(store):
    store.remove("new york")
    assert "New York" not in [c["City"] for c in store.all()]
    with pytest.raises(CityNotFoundError):
        store.remove("New York")
