import pytest
from fastapi.testclient import TestClient

from api import service
from api.main import app
from weather.errors import UpstreamError
from weather.pipeline import run as real_run


@pytest.fixture
def client(fake_session, monkeypatch):
    service.clear_cache()
    monkeypatch.setattr(service.pipeline, "run", lambda names: real_run(names, fake_session))
    return TestClient(app)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_weather_default_cities(client):
    rows = client.get("/api/weather").json()
    assert len(rows) == 10
    assert rows[0]["City"] == "Rio de Janeiro" and rows[0]["Temperature Rank"] == 1


def test_weather_custom_cities(client):
    rows = client.get("/api/weather", params={"cities": "Paris, Lisbon"}).json()
    assert {r["City"] for r in rows} == {"Paris", "Lisbon"}


def test_unknown_cities_404(client):
    assert client.get("/api/weather", params={"cities": "Atlantis"}).status_code == 404


def test_rankings(client):
    assert set(client.get("/api/rankings").json()) == {"hottest", "coldest", "most_humid", "driest", "windiest"}


@pytest.mark.parametrize("metric", ["temperature", "humidity", "wind"])
def test_chart_png(client, metric):
    res = client.get(f"/api/charts/{metric}.png")
    assert res.headers["content-type"] == "image/png"
    assert res.content.startswith(b"\x89PNG")


def test_chart_unknown_metric(client):
    assert client.get("/api/charts/pressure.png").status_code == 404


def test_csv_download(client):
    res = client.get("/api/weather.csv")
    assert 'filename="weather_data.csv"' in res.headers["content-disposition"]
    assert res.text.splitlines()[0].startswith("City,Latitude,Longitude,Temperature (C)")


def test_upstream_failure_502(monkeypatch):
    service.clear_cache()

    def boom(names):
        raise UpstreamError("down")

    monkeypatch.setattr(service.pipeline, "run", boom)
    assert TestClient(app).get("/api/weather").status_code == 502


def test_cache_is_shared_per_city_set(fake_session, monkeypatch):
    service.clear_cache()
    calls = []
    monkeypatch.setattr(service.pipeline, "run", lambda names: calls.append(names) or real_run(names, fake_session))
    client = TestClient(app)
    client.get("/api/weather", params={"cities": "Paris,Tokyo"})
    client.get("/api/rankings", params={"cities": "tokyo, paris"})
    client.get("/api/charts/wind.png", params={"cities": "Tokyo,Paris"})
    assert len(calls) == 1


def test_upstream_error_detail_is_generic(monkeypatch):
    service.clear_cache()

    def boom(names):
        raise UpstreamError("https://internal.example/v1?secret=1 failed")

    monkeypatch.setattr(service.pipeline, "run", boom)
    assert TestClient(app).get("/api/weather").json() == {"detail": "Weather provider error"}


def test_geocoder_outage_is_502_and_not_cached(fake_session, monkeypatch):
    import requests

    from tests.conftest import FakeSession, forecast_handler

    service.clear_cache()

    def down(params):
        raise requests.ConnectionError("down")

    sessions = [FakeSession({"forecast": forecast_handler, "geocoding": down}), fake_session]
    monkeypatch.setattr(service.pipeline, "run", lambda names: real_run(names, sessions[0]))
    client = TestClient(app)
    assert client.get("/api/weather", params={"cities": "Lisbon"}).status_code == 502
    sessions.pop(0)
    assert client.get("/api/weather", params={"cities": "Lisbon"}).json()[0]["City"] == "Lisbon"


@pytest.mark.parametrize("cities", [",".join(["Paris"] * 26), "x" * 101])
def test_oversized_input_is_422(client, cities):
    assert client.get("/api/weather", params={"cities": cities}).status_code == 422


def test_slow_city_set_does_not_block_others(fake_session, monkeypatch):
    import threading

    service.clear_cache()
    release = threading.Event()

    def run(names):
        if names == ["Tokyo"]:
            release.wait(5)
        return real_run(names, fake_session)

    monkeypatch.setattr(service.pipeline, "run", run)
    slow = threading.Thread(target=service.get_weather, args=("Tokyo",))
    slow.start()
    try:
        assert list(service.get_weather("Paris")["City"]) == ["Paris"]  # returns while Tokyo is still in flight
        assert slow.is_alive()
    finally:
        release.set()
        slow.join()
