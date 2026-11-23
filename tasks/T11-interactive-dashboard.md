---
id: T11
title: Interactive dashboard
status: in_progress
requirements: R13
depends_on: T10
---

## Goal
A browser dashboard that plots the data interactively.

## Scope
- `frontend/`, the `/` route in `api/main.py`

## Definition of done
- [ ] Served at `/`
- [ ] City input, metric switch, °F/mph toggle, highlight tiles, Chart.js bars, matplotlib image, table, CSV link
- [ ] User-supplied values are HTML-escaped; API errors are shown inline

## Verify
```bash
uv run pytest -q tests/test_dashboard.py
grep -q 'const esc' frontend/app.js
```

## Manual checks
- Open the dashboard; switch metric and units; load custom cities, including a bad name.

## Evidence
- _Pending._
