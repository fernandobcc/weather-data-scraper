---
id: T03
title: Fetch current weather from Open-Meteo
status: done
requirements: R1, R10
depends_on: T02
---

## Goal
Fetch temperature, humidity and wind for N cities in one `requests` call (°C, m/s), with configuration through dotenv.

## Scope
- `weather/config.py`, `weather/http.py`, `weather/errors.py`, `weather/client.py`, `.env.example`, `tests/conftest.py`

## Definition of done
- [x] One HTTP call for all cities, requesting `celsius` and `ms` explicitly
- [x] Single-location (object) and multi-location (list) responses both handled
- [x] Retries with backoff on 429/5xx
- [x] HTTP errors, malformed payloads and missing locations raise `UpstreamError`
- [x] URLs and timeout overridable through `.env` (documented in `.env.example`)

## Verify
```bash
uv run pytest -q tests/test_client.py
grep -q load_dotenv weather/config.py && grep -q '^HTTP_TIMEOUT=' .env.example
```

## Manual checks
- Fetch the default cities against the live API.

## Evidence
- 2026-11-23 · `tests/test_client.py` 7 cases pass; pyright 0 errors.
- Manual: live fetch of the 10 default cities returned 10 records from one request.
