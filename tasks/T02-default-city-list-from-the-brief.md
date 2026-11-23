---
id: T02
title: Default city list from the brief
status: todo
requirements: R2
depends_on: T01
---

## Goal
The 10 cities attached to the brief are the default input, with their given coordinates.

## Scope
- `weather/cities.py`

## Definition of done
- [ ] 10 cities with the brief's exact coordinates
- [ ] Case-insensitive lookup by name
- [ ] Comma-separated user input parsed into clean names

## Verify
```bash
uv run pytest -q tests/test_cities.py
```

## Evidence
- _Pending._
