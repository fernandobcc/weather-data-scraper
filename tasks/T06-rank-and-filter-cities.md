---
id: T06
title: Rank and filter cities
status: in_progress
requirements: R6
depends_on: T05
---

## Goal
Helpers for the extremes and filters the brief asks for (highest temperature, lowest humidity, …).

## Scope
- `weather/processing.py`

## Definition of done
- [ ] `rankings()` returns hottest/coldest/most_humid/driest/windiest as JSON-safe values
- [ ] `top_n` and `filter_range` work on any numeric column

## Verify
```bash
uv run pytest -q tests/test_ranking.py
```

## Evidence
- _Pending._
