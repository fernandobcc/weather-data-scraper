import pytest

from tests.conftest import FakeResponse, FakeSession
from weather.cities import DEFAULT_CITIES
from weather.client import fetch_current_weather
from weather.errors import UpstreamError


def test_fetches_all_cities_in_one_call(fake_session):
    records = fetch_current_weather(DEFAULT_CITIES, fake_session)
    assert len(records) == 10
    assert len(fake_session.calls) == 1
    params = fake_session.calls[0][1]
    assert params["wind_speed_unit"] == "ms" and params["temperature_unit"] == "celsius"
    assert records[0] == {"City": "New York", "Latitude": 40.7128, "Longitude": -74.006, "Temperature (C)": 10.0,
                          "Humidity (%)": 50, "Wind Speed (m/s)": 2.0, "Observed At (UTC)": "2026-11-23T19:00"}


def test_single_city_response_is_normalised(fake_session):
    assert [r["City"] for r in fetch_current_weather(DEFAULT_CITIES[:1], fake_session)] == ["New York"]


def test_empty_city_list_skips_http(fake_session):
    assert fetch_current_weather([], fake_session) == []
    assert fake_session.calls == []


@pytest.mark.parametrize("payload", [[{"current": {}}], {"error": True, "reason": "bad"}])
def test_malformed_payload_raises_upstream_error(payload):
    session = FakeSession({"forecast": lambda p: FakeResponse(payload)})
    with pytest.raises(UpstreamError):
        fetch_current_weather(DEFAULT_CITIES[:1], session)


def test_location_count_mismatch_raises():
    one = {"current": {"time": "t", "temperature_2m": 1, "relative_humidity_2m": 1, "wind_speed_10m": 1}}
    session = FakeSession({"forecast": lambda p: FakeResponse([one])})
    with pytest.raises(UpstreamError):
        fetch_current_weather(DEFAULT_CITIES[:3], session)


def test_http_error_raises_upstream_error():
    session = FakeSession({"forecast": lambda p: FakeResponse({}, status=500)})
    with pytest.raises(UpstreamError):
        fetch_current_weather(DEFAULT_CITIES, session)
