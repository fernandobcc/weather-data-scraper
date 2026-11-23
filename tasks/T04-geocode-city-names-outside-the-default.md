---
id: T04
title: Geocode city names outside the default list
status: in_progress
requirements: R3, R8
depends_on: T03
---

## Goal
Any city name works: names that aren't in the default list get coordinates from the Open-Meteo geocoding API.

## Scope
- `weather/geocoding.py`

## Definition of done
- [ ] Default-list coordinates win; other names are geocoded
- [ ] Unresolvable names are skipped with a warning
- [ ] A geocoding outage skips only that name
- [ ] Duplicates (same name and coordinates) are dropped

## Verify
```bash
uv run pytest -q tests/test_geocoding.py
```

## Manual checks
- Resolve `Lisbon` and a nonsense name against the live API.

## Evidence
- _Pending._
