---
id: T10
title: FastAPI endpoints
status: done
requirements: R12
depends_on: T06, T09
---

## Goal
Serve data, rankings, charts and the CSV download over HTTP, as specified in the API contract.

## Scope
- `api/main.py`, `api/service.py`
- Out of scope: the dashboard page (T11).

## Definition of done
- [x] Every API-contract endpoint except `/` responds as specified
- [x] 404 when no city resolves, 502 on upstream failure, 404 for an unknown metric
- [x] Results cached for 5 min per city set; concurrent misses share one upstream call

## Verify
```bash
uv run pytest -q tests/test_api.py
```

## Manual checks
- `uv run uvicorn api.main:app`, then curl each endpoint.

## Evidence
- 2026-11-23 · `tests/test_api.py` 12 cases pass; pyright 0 errors.
- Manual: live uvicorn smoke test, all endpoints as in the API contract (200/404).
