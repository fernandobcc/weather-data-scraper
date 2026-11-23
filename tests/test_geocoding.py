import pytest
import requests

from tests.conftest import FakeResponse, FakeSession
from weather.cities import DEFAULT_CITIES
from weather.errors import UpstreamError
from weather.geocoding import resolve_cities


def test_resolve_defaults_when_no_names(fake_session):
    assert resolve_cities([], fake_session) == DEFAULT_CITIES
    assert fake_session.calls == []


def test_resolve_known_unknown_and_geocoded(fake_session):
    cities = resolve_cities(["tokyo", "Lisbon", "Atlantis"], fake_session)
    assert cities == [
        {"City": "Tokyo", "Latitude": 35.6895, "Longitude": 139.6917},
        {"City": "Lisbon", "Latitude": 38.72, "Longitude": -9.14},
    ]
    assert [p["name"] for url, p in fake_session.calls if "geocoding" in url] == ["Lisbon", "Atlantis"]


def test_duplicates_are_dropped(fake_session):
    assert [c["City"] for c in resolve_cities(["Paris", "paris", " PARIS "], fake_session)] == ["Paris"]


def test_geocoding_outage_raises_upstream_error():
    """An outage is not "city not found": it must surface as UpstreamError (API 502), not a silent skip."""
    def broken(params):
        raise requests.ConnectionError("down")

    with pytest.raises(UpstreamError):
        resolve_cities(["Tokyo", "Lisbon"], FakeSession({"geocoding": broken}))


@pytest.mark.parametrize("payload", [[], {"results": [{"name": "X"}]}, {"results": [{"name": "X", "latitude": "n/a", "longitude": 1}]}])
def test_malformed_geocoding_payload_raises_upstream_error(payload):
    with pytest.raises(UpstreamError):
        resolve_cities(["Lisbon"], FakeSession({"geocoding": lambda p: FakeResponse(payload)}))
