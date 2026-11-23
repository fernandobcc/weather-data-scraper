---
id: T09
title: matplotlib charts
status: done
requirements: R11
depends_on: T08
---

## Goal
Bar charts for temperature, humidity and wind, saved by the CLI and available as PNG bytes for the API.

## Scope
- `weather/plots.py`, `main.py` (`--no-charts`)

## Definition of done
- [x] Three PNG charts, rendered headless
- [x] The CLI saves them next to the CSV unless `--no-charts`

## Verify
```bash
uv run pytest -q tests/test_plots.py
uv run pytest -q tests/test_cli.py::test_cli_writes_charts
```

## Manual checks
- Look at the PNGs: values labelled, no clipped names.

## Evidence
- 2026-11-23 · `tests/test_plots.py` (5) and the two chart cases in `tests/test_cli.py` pass; pyright 0 errors.
- Manual: looked at the live-run PNGs. Humidity labels showed `94.0`, fixed to integers (`test_humidity_labels_are_integers`); no clipped names.
