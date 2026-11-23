---
id: T05
title: DataFrame with derived units
status: in_progress
requirements: R4, R5
depends_on: T03
---

## Goal
Turn raw records into a pandas DataFrame with °F and mph, matching the brief's example rows.

## Scope
- `weather/processing.py`

## Definition of done
- [ ] 10 °C → 50 °F and 5 m/s → 11.2 mph
- [ ] Rounding and column order follow the data contract
- [ ] Rows sorted hottest first with `Temperature Rank`
- [ ] Null humidity doesn't crash (nullable Int64)

## Verify
```bash
uv run pytest -q tests/test_processing.py
```

## Evidence
- _Pending._
