---
id: T06
title: Rank and filter cities
status: done
requirements: R6
depends_on: T05
---

## Goal
Helpers for the extremes and filters the brief asks for (highest temperature, lowest humidity, …).

## Scope
- `weather/processing.py`

## Definition of done
- [x] `rankings()` returns hottest/coldest/most_humid/driest/windiest as JSON-safe values
- [x] `top_n` and `filter_range` work on any numeric column

## Verify
```bash
uv run pytest -q tests/test_ranking.py
```

## Evidence
- 2026-11-23 · `tests/test_ranking.py` 3 cases pass (including the empty frame and JSON-safe value types); pyright 0 errors.
