---
id: T17
title: Manage cities from the frontend with TinyDB
status: todo
requirements: R16
depends_on: T11, T16
---

## Goal
Users list, add and remove the saved cities from a **Cities** page, and the list persists in TinyDB. Default runs (CLI, API, notebook) use the saved list.

## Scope
- `weather/city_store.py`, `weather/pipeline.py`, `weather/geocoding.py`, `api/main.py`, `frontend/cities.*`, nav in `frontend/index.html`, `docker-compose.yml`, `Dockerfile`.
- Out of scope: auth / multi-user lists.

## Definition of done
- [ ] `GET`/`POST /api/cities` and `DELETE /api/cities/{name}` follow the API contract (201/204/404/409/422/502)
- [ ] The store is seeded once from `data/cities.json`; added names are geocoded once and stored with coordinates
- [ ] Names are unique (case-insensitive); the list is capped at 25 cities
- [ ] Default runs use the saved list; every change clears the API cache
- [ ] Tests use a temporary store and never touch `db/`
- [ ] Saved cities survive a container restart (compose volume, writable by the non-root user)

## Verify
```bash
uv run pytest -q tests/test_city_store.py tests/test_cities_api.py
uv run pytest -q tests/test_dashboard.py
grep -q 'city-db:/app/db' docker-compose.yml && grep -q 'mkdir -p /app/db' Dockerfile
```

## Manual checks
- Browser + Docker: add a city by name, reject a duplicate, restart the container, remove the city.

## Evidence
- _Pending._
