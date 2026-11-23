---
id: T09
title: matplotlib charts
status: todo
requirements: R11
depends_on: T08
---

## Goal
Bar charts for temperature, humidity and wind, saved by the CLI and available as PNG bytes for the API.

## Scope
- `weather/plots.py`, `main.py` (`--no-charts`)

## Definition of done
- [ ] Three PNG charts, rendered headless
- [ ] The CLI saves them next to the CSV unless `--no-charts`

## Verify
```bash
uv run pytest -q tests/test_plots.py
uv run pytest -q tests/test_cli.py::test_cli_writes_charts
```

## Manual checks
- Look at the PNGs: values labelled, no clipped names.

## Evidence
- _Pending._
