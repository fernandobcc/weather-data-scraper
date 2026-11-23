---
id: T02
title: Default city list from the brief
status: done
requirements: R2
depends_on: T01
---

## Goal
The 10 cities attached to the brief are the default input, with their given coordinates.

## Scope
- `weather/cities.py`

## Definition of done
- [x] 10 cities with the brief's exact coordinates
- [x] Case-insensitive lookup by name
- [x] Comma-separated user input parsed into clean names

## Verify
```bash
uv run pytest -q tests/test_cities.py
```

## Evidence
- 2026-11-23 · `tests/test_cities.py`: 9 cases pass; pyright 0 errors.
