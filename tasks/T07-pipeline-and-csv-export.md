---
id: T07
title: Pipeline and CSV export
status: in_progress
requirements: R7
depends_on: T04, T05
---

## Goal
One pipeline (resolve → fetch → process) shared by every adapter, plus CSV export.

## Scope
- `weather/pipeline.py`, `weather/export.py`

## Definition of done
- [ ] `pipeline.run()` returns the processed DataFrame
- [ ] The CSV header matches the data contract exactly
- [ ] No index column in the CSV

## Verify
```bash
uv run pytest -q tests/test_export.py
```

## Evidence
- _Pending._
