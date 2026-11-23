---
id: T10
title: FastAPI endpoints
status: in_progress
requirements: R12
depends_on: T06, T09
---

## Goal
Serve data, rankings, charts and the CSV download over HTTP, as specified in the API contract.

## Scope
- `api/main.py`, `api/service.py`
- Out of scope: the dashboard page (T11).

## Definition of done
- [ ] Every API-contract endpoint except `/` responds as specified
- [ ] 404 when no city resolves, 502 on upstream failure, 404 for an unknown metric
- [ ] Results cached for 5 min per city set; concurrent misses share one upstream call

## Verify
```bash
uv run pytest -q tests/test_api.py
```

## Manual checks
- `uv run uvicorn api.main:app`, then curl each endpoint.

## Evidence
- _Pending._
