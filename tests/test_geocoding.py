import pytest
import requests

from tests.conftest import FakeResponse, FakeSession
from weather.cities import load_cities
from weather.errors import UpstreamError
from weather.geocoding import resolve_cities

CATALOG = load_cities()


def test_resolve_defaults_when_no_names(fake_session):
    assert resolve_cities([], fake_session, CATALOG) == CATALOG
    assert fake_session.calls == []


@pytest.mark.parametrize("name", ["tokyo", "  TOKYO ", "Tokyo"])
def test_catalog_lookup_is_case_insensitive(fake_session, name):
    tokyo = {"City": "Tokyo", "Latitude": 35.6895, "Longitude": 139.6917}
    assert resolve_cities([name], fake_session, CATALOG) == [tokyo]
    assert fake_session.calls == []


def test_catalog_entry_without_coordinates_is_geocoded(fake_session):
    catalog = [{"City": "Tokyo", "Latitude": 35.6895, "Longitude": 139.6917}, {"City": "Lisbon"}]
    cities = resolve_cities([], fake_session, catalog)
    assert [c["City"] for c in cities] == ["Tokyo", "Lisbon"] and cities[1]["Latitude"] == 38.72


def test_resolve_known_unknown_and_geocoded(fake_session):
    cities = resolve_cities(["tokyo", "Lisbon", "Atlantis"], fake_session, CATALOG)
    assert cities == [
        {"City": "Tokyo", "Latitude": 35.6895, "Longitude": 139.6917},
        {"City": "Lisbon", "Latitude": 38.72, "Longitude": -9.14},
    ]
    assert [p["name"] for url, p in fake_session.calls if "geocoding" in url] == ["Lisbon", "Atlantis"]


def test_duplicates_are_dropped(fake_session):
    assert [c["City"] for c in resolve_cities(["Paris", "paris", " PARIS "], fake_session, CATALOG)] == ["Paris"]


def test_geocoding_outage_raises_upstream_error():
    """An outage is not "city not found": it must surface as UpstreamError (API 502), not a silent skip."""
    def broken(params):
        raise requests.ConnectionError("down")

    with pytest.raises(UpstreamError):
        resolve_cities(["Tokyo", "Lisbon"], FakeSession({"geocoding": broken}), CATALOG)


@pytest.mark.parametrize("payload", [
    [],
    {"results": [{"name": "X"}]},
    {"results": [{"name": "X", "latitude": "n/a", "longitude": 1}]},
])
def test_malformed_geocoding_payload_raises_upstream_error(payload):
    with pytest.raises(UpstreamError):
        resolve_cities(["Lisbon"], FakeSession({"geocoding": lambda p: FakeResponse(payload)}), CATALOG)


def test_search_returns_all_matches_with_region(fake_session):
    from weather.geocoding import search

    matches = search("Springfield", fake_session)
    assert [(m["name"], m["admin1"], m["country"]) for m in matches] == [
        ("Springfield", "Missouri", "United States"), ("Springfield", "Illinois", "United States"),
    ]
    assert fake_session.calls[0][1]["count"] == 5


def test_geocode_is_the_first_search_match(fake_session):
    assert resolve_cities(["Springfield"], fake_session, CATALOG) == [
        {"City": "Springfield", "Latitude": 37.22, "Longitude": -93.3},
    ]
