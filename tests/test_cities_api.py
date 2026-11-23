import pytest
from fastapi.testclient import TestClient

import api.main
from api import service
from api.main import app
from weather.pipeline import run as real_run


@pytest.fixture
def client(fake_session, monkeypatch):
    service.clear_cache()
    monkeypatch.setattr(service.pipeline, "run", lambda names: real_run(names, fake_session))
    monkeypatch.setattr(api.main, "make_session", lambda: fake_session)
    return TestClient(app)


def test_list_add_delete_flow(client):
    assert len(client.get("/api/cities").json()) == 10
    res = client.post("/api/cities", json={"name": "Lisbon"})
    assert res.status_code == 201 and res.json() == {"City": "Lisbon", "Latitude": 38.72, "Longitude": -9.14}
    assert "Lisbon" in {r["City"] for r in client.get("/api/weather").json()}  # cache cleared, saved list used
    assert client.delete("/api/cities/lisbon").status_code == 204
    assert "Lisbon" not in {r["City"] for r in client.get("/api/weather").json()}


@pytest.mark.parametrize("body, status", [
    ({"name": "Paris"}, 409),
    ({"name": "Atlantis"}, 404),
    ({"name": ""}, 422),
    ({"name": "x" * 101}, 422),
    ({"name": "Porto", "latitude": 41.1}, 422),
    ({"name": "Porto", "latitude": 141.1, "longitude": 1}, 422),
])
def test_add_city_errors(client, body, status):
    assert client.post("/api/cities", json=body).status_code == status


def test_full_list_is_409(client):
    for i in range(15):
        assert client.post("/api/cities", json={"name": f"Town {i}", "latitude": 0, "longitude": i}).status_code == 201
    assert client.post("/api/cities", json={"name": "Extra", "latitude": 1, "longitude": 1}).status_code == 409


def test_geocoder_outage_is_502(client, monkeypatch):
    import requests

    from tests.conftest import FakeSession

    def down(params):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(api.main, "make_session", lambda: FakeSession({"geocoding": down}))
    assert client.post("/api/cities", json={"name": "Lisbon"}).json() == {"detail": "Geocoding provider error"}


def test_delete_unknown_city(client):
    assert client.delete("/api/cities/Atlantis").status_code == 404


def test_geocode_lists_same_name_matches(client):
    res = client.get("/api/geocode", params={"name": " springfield "})
    assert [m["admin1"] for m in res.json()] == ["Missouri", "Illinois"]


@pytest.mark.parametrize("name", ["", "x" * 101])
def test_geocode_rejects_bad_names(client, name):
    assert client.get("/api/geocode", params={"name": name}).status_code == 422


def test_geocode_outage_is_502(client, monkeypatch):
    import requests

    from tests.conftest import FakeSession

    def down(params):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(api.main, "make_session", lambda: FakeSession({"geocoding": down}))
    assert client.get("/api/geocode", params={"name": "Lisbon"}).status_code == 502


def test_picked_match_is_saved_with_its_coordinates(client):
    """The page posts the picked match with explicit coordinates, so no second lookup can pick another place."""
    illinois = client.get("/api/geocode", params={"name": "Springfield"}).json()[1]
    body = {"name": "Springfield (Illinois)", "latitude": illinois["latitude"], "longitude": illinois["longitude"]}
    assert client.post("/api/cities", json=body).json() == {"City": "Springfield (Illinois)", "Latitude": 39.8, "Longitude": -89.64}
    rows = client.get("/api/weather").json()
    assert "Springfield (Illinois)" in {r["City"] for r in rows}
    assert list(rows[0]) == ["City", "Latitude", "Longitude", "Temperature (C)", "Temperature (F)", "Humidity (%)",
                             "Wind Speed (m/s)", "Wind Speed (mph)", "Observed At (UTC)", "Temperature Rank"]
