---
id: T03
title: Fetch current weather from Open-Meteo
status: todo
requirements: R1, R10
depends_on: T02
---

## Goal
Fetch temperature, humidity and wind for N cities in one `requests` call (°C, m/s), with configuration through dotenv.

## Scope
- `weather/config.py`, `weather/http.py`, `weather/errors.py`, `weather/client.py`, `.env.example`, `tests/conftest.py`

## Definition of done
- [ ] One HTTP call for all cities, requesting `celsius` and `ms` explicitly
- [ ] Single-location (object) and multi-location (list) responses both handled
- [ ] Retries with backoff on 429/5xx
- [ ] HTTP errors, malformed payloads and missing locations raise `UpstreamError`
- [ ] URLs and timeout overridable through `.env` (documented in `.env.example`)

## Verify
```bash
uv run pytest -q tests/test_client.py
grep -q load_dotenv weather/config.py && grep -q '^HTTP_TIMEOUT=' .env.example
```

## Manual checks
- Fetch the default cities against the live API.

## Evidence
- _Pending._
