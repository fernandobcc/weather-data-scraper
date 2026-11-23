from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_index_serves_dashboard():
    res = client.get("/")
    assert res.status_code == 200
    assert "Current weather" in res.text and "/static/app.js" in res.text


def test_static_assets_are_served():
    assert "function renderChart" in client.get("/static/app.js").text
    assert client.get("/static/styles.css").headers["content-type"].startswith("text/css")


def test_dashboard_escapes_and_reports_errors():
    js = client.get("/static/app.js").text
    assert "const esc" in js and "esc(r[c])" in js
    assert ".catch(() => ({}))" in js
