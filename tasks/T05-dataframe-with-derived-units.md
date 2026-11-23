---
id: T05
title: DataFrame with derived units
status: done
requirements: R4, R5
depends_on: T03
---

## Goal
Turn raw records into a pandas DataFrame with °F and mph, matching the brief's example rows.

## Scope
- `weather/processing.py`

## Definition of done
- [x] 10 °C → 50 °F and 5 m/s → 11.2 mph
- [x] Rounding and column order follow the data contract
- [x] Rows sorted hottest first with `Temperature Rank`
- [x] Null humidity doesn't crash (nullable Int64)

## Verify
```bash
uv run pytest -q tests/test_processing.py
```

## Evidence
- 2026-11-23 · `tests/test_processing.py` 8 cases pass, including the brief's example rows (New York 50 °F / 11.2 mph, Tokyo 59 / 6.7, London 53.6 / 8.9); pyright 0 errors.
