# Spec: Weather Data Scraping Exercise

Source: the exercise brief PDF (`specs/exercise.pdf`, kept local and out of git).
This spec is the single source of truth. Every task in `tasks/` and every feature
in `feature_list.json` points back to a requirement ID below.

## Functional requirements

| ID | Requirement | Source |
|----|-------------|--------|
| R1 | Fetch current temperature, wind speed and humidity from Open-Meteo using `requests` | Brief §1 |
| R2 | Support at least 10 cities, defaulting to the attached city dict | Brief §1 |
| R3 | (Bonus) Resolve lat/long from a city name via an external geocoding API | Brief §1 bonus |
| R4 | Build a pandas DataFrame from the collected data | Brief §2 |
| R5 | Derive Temperature (F) from Celsius and Wind Speed (mph) from m/s | Brief §2 |
| R6 | Filter / rank cities (hottest, coldest, lowest humidity, windiest) | Brief §2 |
| R7 | Export to `weather_data.csv` | Brief §3 |
| R8 | Accept user input for cities (CLI argument or interactive prompt), falling back to the default list | Program structure a |
| R9 | Display processed data in the terminal | Program structure c |
| R10 | Use `python-dotenv` for configuration | Requirements (optional) |
| R11 | (Bonus) Charts with matplotlib | Bonus |
| R12 | (Bonus plus) FastAPI endpoints serving charts and the CSV download | Bonus plus |
| R13 | Frontend that plots the data interactively | Stakeholder request |
| R14 | Jupyter notebook with the analysis, plus generated deliverables, in `output/` | Stakeholder request |
| R15 | README with run instructions, approach and suggestions; uv, pyright and Docker tooling | Submission + stakeholder request |
| R16 | Manage the saved city list (list / add / remove) from the frontend, persisted in TinyDB | Stakeholder request (after T16) |
| R17 | When a city name exists in several places, let the user pick the right one on the Cities page; the CSV columns stay unchanged | Stakeholder request (after T18) |

## Data contract

CSV columns, in order:

`City, Latitude, Longitude, Temperature (C), Temperature (F), Humidity (%), Wind Speed (m/s), Wind Speed (mph), Observed At (UTC), Temperature Rank`

- Rows are sorted by `Temperature (C)` descending; `Temperature Rank` 1 = hottest.
- Measurements are rounded to 1 decimal and coordinates to 4; humidity is an integer (nullable).
- `F = C * 9/5 + 32`, `mph = m/s * 2.236936` (mph is computed from the unrounded m/s).
- Duplicate cities (same name and coordinates) are dropped.
- The column set is fixed (stakeholder decision in R17): disambiguation lives in the saved `City` name, e.g. `Springfield (Illinois)`, not in extra columns.

## API contract (FastAPI)

| Method | Path | Returns |
|--------|------|---------|
| GET | `/` | Dashboard (HTML) |
| GET | `/health` | `{"status": "ok"}` |
| GET | `/api/weather?cities=A,B` | JSON rows following the data contract |
| GET | `/api/rankings?cities=A,B` | Hottest, coldest, most humid, driest, windiest city |
| GET | `/api/charts/{metric}.png?cities=A,B` | matplotlib PNG; metric ∈ temperature, humidity, wind; unknown metric → `404` |
| GET | `/api/weather.csv?cities=A,B` | CSV download (`weather_data.csv`) |
| GET | `/cities` | City management page (HTML) |
| GET | `/api/geocode?name=X` | Up to 5 matches `{name, admin1, country, latitude, longitude}`; `422` empty or too long; `502` geocoder down |
| GET | `/api/cities` | Saved cities |
| POST | `/api/cities` | Body `{name, latitude?, longitude?}` (both coordinates or neither) → `201` city; `409` duplicate or list full (25); `404` name not found; `422` invalid; `502` geocoder down |
| DELETE | `/api/cities/{name}` | `204`; `404` if not saved (case-insensitive) |

`cities` is optional; when omitted, the saved city list is used (seeded from the brief's 10 cities). Unknown city names are
skipped; if none resolve, the API answers `404`. Upstream failures (HTTP errors,
malformed payloads, missing locations) answer `502`.

## Non-functional

- Small single-purpose modules (fetch / geocode / process / plot / export / serve); the CLI, the API and the notebook share one pipeline.
- Tests never hit the network (HTTP is injected).
- One HTTP call fetches all cities (Open-Meteo accepts comma-separated coordinates).
- Gates: `ruff` (lint + import order), `pytest`, `pyright` (0 errors) and `scripts/check_tasks.py`, run in CI on every PR.
