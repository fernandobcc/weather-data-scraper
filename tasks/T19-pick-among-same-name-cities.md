---
id: T19
title: Pick among same-name cities on the Cities page
status: todo
requirements: R17
depends_on: T17, T18
---

## Goal
A name like "Springfield" exists in several places, and the app silently took the top geocoding match. Let the user search, see each match's state and country, and pick one, without changing the CSV columns (stakeholder decision).

## Scope
- `weather/geocoding.py` (`search`), `GET /api/geocode`, `frontend/cities.*`.
- Out of scope: new CSV columns; country hints in the dashboard's one-off input.

## Definition of done
- [ ] `search()` returns up to 5 matches with name, admin1, country and coordinates; `geocode()` is its first match
- [ ] `GET /api/geocode` follows the API contract (200 / 422 / 502)
- [ ] The Cities page lists the matches; picking one fills name and coordinates, then Add saves those exact coordinates
- [ ] Same-name matches get a suggested name with their region, e.g. `Springfield (Illinois)`; the user can edit it
- [ ] Match labels are rendered with `textContent` (no HTML injection)
- [ ] CSV header unchanged

## Verify
```bash
uv run pytest -q tests/test_geocoding.py tests/test_cities_api.py tests/test_dashboard.py tests/test_export.py
uv run pyright
```

## Manual checks
- Browser, live API: search "Springfield", pick Illinois, add it, and check the dashboard shows Springfield (Illinois) weather.

## Evidence
- _Pending._
