---
id: T04
title: Geocode city names outside the default list
status: done
requirements: R3, R8
depends_on: T03
---

## Goal
Any city name works: names that aren't in the default list get coordinates from the Open-Meteo geocoding API.

## Scope
- `weather/geocoding.py`

## Definition of done
- [x] Default-list coordinates win; other names are geocoded
- [x] Unresolvable names are skipped with a warning
- [x] A geocoding outage skips only that name
- [x] Duplicates (same name and coordinates) are dropped

## Verify
```bash
uv run pytest -q tests/test_geocoding.py
```

## Manual checks
- Resolve `Lisbon` and a nonsense name against the live API.

## Evidence
- 2026-11-23 · `tests/test_geocoding.py` 4 cases pass; pyright 0 errors.
- Manual: live resolve of Lisbon / Qwxzzyville / tokyo gave Lisbon geocoded, the nonsense name skipped, Tokyo from the list.
