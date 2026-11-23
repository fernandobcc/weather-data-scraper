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
    assert "const esc" in js and "show(r[c])" in js and "esc(row.City)" in js
    assert ".catch(() => ({}))" in js


def test_cdn_script_has_subresource_integrity():
    html = client.get("/").text
    assert 'integrity="sha384-' in html and 'crossorigin="anonymous"' in html


def test_cities_page_and_navigation():
    page = client.get("/cities").text
    assert "Add a city" in page and "/static/cities.js" in page
    assert 'href="/cities"' in client.get("/").text and 'href="/"' in page


def test_cities_page_builds_rows_without_innerhtml():
    js = client.get("/static/cities.js").text
    assert "textContent" in js and "innerHTML" not in js
