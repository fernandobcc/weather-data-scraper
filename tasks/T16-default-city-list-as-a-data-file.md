---
id: T16
title: Default city list as a data file
status: done
requirements: R2
depends_on: T14
---

## Goal
The default cities live in a data file instead of a Python module, so changing them never means editing code (reviewer finding #11 in T14; AGENTS.md "data belongs in data files").

## Scope
- `data/cities.json`, `weather/cities.py`, `weather/geocoding.py`, config, Dockerfile.
- Out of scope: editing the list from the UI.

## Definition of done
- [x] The 10 attached cities live in `data/cities.json` with unchanged coordinates
- [x] Entries may omit coordinates; those are geocoded
- [x] No city list remains in Python code
- [x] The Docker image includes `data/`

## Verify
```bash
uv run pytest -q tests/test_cities.py tests/test_geocoding.py
test -f data/cities.json && ! grep -rq 'New York' weather/ api/
grep -q 'COPY --chown=app data' Dockerfile
```

## Evidence
- 2026-11-23 · 79 tests pass, pyright 0 errors; all earlier tasks still verify.
- Manual: custom catalog with name-only entries resolved live; the Docker image contains data/ (10 cities).
