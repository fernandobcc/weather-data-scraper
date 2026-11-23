# Progress

Append-only work log, newest at the bottom. Each entry is written in the task's done commit.
Roles are defined in `AGENTS.md`.

## T00: Spec, backlog and task harness (Planner)
- Read the brief; probed Open-Meteo: the forecast API accepts comma-separated coordinates (one call for N cities) and returns an object for one location, a list for several. The geocoding API needs no key.
- Wrote `specs/spec.md` (R1–R15, data and API contracts), the backlog `tasks/T01–T15`, `feature_list.json` (F01–F12), `AGENTS.md`, and `scripts/check_tasks.py` (D02).
- The brief PDF stays local only (`.gitignore`): the repo is public.

## T01: Project tooling (Implementer)
- `pyproject.toml` (Python 3.12, uv, dev: pytest, pyright[nodejs]), `.github/workflows/ci.yml`, `tests/test_tasks.py` (task files valid; feature list in sync; the checker rejects done tasks with no commit or unchecked boxes). D03.
- Gates: 4 passed, pyright 0 errors.

## T02: Default city list (Implementer)
- `weather/cities.py`: the brief's 10 cities as given, a case-insensitive `known_city()` and `parse_city_names()` for user input. 13 tests pass.

## T03: Fetch current weather (Implementer)
- `weather/client.py`, `http.py`, `errors.py`, `config.py` (dotenv), `.env.example`; `FakeSession` in `tests/conftest.py`. D04–D06.
- Tests: 20 passed (7 new in `test_client.py`). Live check: 10 default cities fetched in one call (New York 20.4 °C, 4.65 m/s at 20:00 UTC).

## T04: Geocoding (Implementer)
- `weather/geocoding.py`: catalog first, then Open-Meteo geocoding; skips unknown or failing names; dedupes. D07.
- Tests: 24 passed (4 new). Live: `Lisbon` resolved (38.7251, -9.1498), `Qwxzzyville` skipped with a warning, `tokyo` matched the default list.

## T05: DataFrame with derived units (Implementer)
- `weather/processing.py`: `COLUMNS`, `celsius_to_fahrenheit`, `ms_to_mph`, `build_dataframe` (rounding, sort, rank, nullable humidity). D08.
- Tests: 32 passed (8 new); the brief's three example rows reproduce exactly.

## T06: Ranking and filtering (Implementer)
- `top_n`, `filter_range` and `rankings` (hottest / coldest / most humid / driest / windiest, JSON-safe values) in `weather/processing.py`.
- Tests: 35 passed (3 new).

## T07: Pipeline and CSV export (Implementer)
- `weather/pipeline.py` (resolve → fetch → process) and `weather/export.py`. D09.
- Tests: 38 passed (3 new); the CSV header equals the data contract, there is no index column, and an end-to-end run makes 3 HTTP calls (2 geocodes + 1 forecast).

## T08: Command-line interface (Implementer)
- `main.py`: `--cities`, `--interactive`, `--sort-by`; prints the table and highlights; writes `output/weather_data.csv`; exits 1 when nothing resolves or on `UpstreamError`. `OUTPUT_DIR` configurable.
- Tests: 42 passed (4 new). Live: `--cities "Lisbon, Tokyo, Nairobi"` printed the table and highlights (hottest Nairobi 17.0 °C) and wrote the CSV.

## T09: matplotlib charts (Implementer, Tester)
- `weather/plots.py`: horizontal bar charts for temperature, humidity and wind (Agg backend, sorted, values labelled); `main.py` saves them unless `--no-charts`.
- Manual check found humidity labelled `94.0`; fixed with a per-metric label format and a regression test.
- Tests: 49 passed (7 new).

## T10: FastAPI endpoints (Implementer, Tester)
- `api/main.py` (thin adapter over the pipeline) and `api/service.py` (TTL cache + lock). D10.
- Tests: 61 passed (12 new, including the cache sharing one upstream call across three requests).
- Live uvicorn: `/health`, `/api/weather`, `/api/rankings`, `/api/charts/temperature.png`, `/api/weather.csv` → 200; unknown city → 404; unknown metric → 404.

## T11: Interactive dashboard (Implementer, Tester)
- `frontend/` (HTML + Chart.js + CSS with light/dark tokens), served at `/` with static assets. D11.
- Tests: 64 passed (3 new).
- Browser (live API): 5 tiles and 10 rows on load; wind + °F/mph switched the title to "Wind speed (mph)"; `Lisbon, Nairobi, Qwxzzyville` showed 2 rows; `Qwxzzyville` alone showed the inline error.

## T12: Notebook and deliverables (Implementer, Tester)
- `scripts/build_notebook.py`, `scripts/check_notebook.py`; `output/` = `weather_data.csv`, three chart PNGs, `weather_analysis.ipynb`, from a live run at 2026-11-23T20:15 UTC (hottest: Mumbai 27.1 °C). D12.
- Notebook check: no errors, every cell has output, 3 chart images.

## T13: Docker (Implementer, Tester)
- `Dockerfile`, `docker-compose.yml` (API + `cli` profile), `.dockerignore`. D13.
- Built locally; container `/health`, `/api/weather?cities=Lisbon`, `/` and `/api/charts/wind.png` → 200. The image contains only `api`, `frontend`, `weather`, `main.py` and the lock files.

## T14: Independent review and hardening (Reviewer, Implementer)

### Reviewer
A separate agent received only `specs/spec.md`, the AGENTS.md conventions and the code (not task notes or this log). It ran the gates and throwaway edge-case scripts and reported 12 findings:

| # | Finding | Resolution |
|---|---------|------------|
| 1 | `rankings()` crashes when a metric is all null → `/api/rankings` 500 | Fixed: all-null metrics are omitted |
| 2 | Geocoder outage silently skipped → 404 (spec: 502), and a degraded result was cached | Fixed: `UpstreamError` → 502, not cached (D14) |
| 3 | Non-dict geocoding JSON or non-numeric forecast values → 500 | Fixed: validated, `UpstreamError` → 502 |
| 4 | Unbounded `cities` (2000 names = 2000 geocoding calls) | Fixed: max 25 names × 100 chars → 422 / CLI exit 2 |
| 5 | Global lock held during network I/O serialises the whole API | Fixed: one lock per city set |
| 6 | pyplot global state in threaded API handlers | Fixed: `Figure()` without pyplot |
| 7 | CDN script without SRI | Fixed: sha384 `integrity` + `crossorigin` |
| 8 | Tiles looked up rows by name only; null shown as "null" | Fixed: `rankings` returns `row`; nulls shown as "–" |
| 9 | 502 detail leaked the upstream URL | Fixed: generic detail, logged server-side |
| 10 | Container runs as root | Fixed: `USER app` (uid 1000) |
| 11 | City data in Python; missing type hints and docstrings | Type hints added. City data → new task **T16**. Docstring rule clarified in AGENTS.md (one line where the name isn't enough) |
| 12 | Missing regression tests for the above | Fixed: 13 new tests |
| — | Notebook ignored `OUTPUT_DIR`; httpx2 deprecation warning | Notebook fixed. Warning accepted (it comes from FastAPI's test client) |

### Implementer
- 77 tests pass, pyright 0 errors. The harness caught one slip of mine: attaching T16 to F01 left F01 marked `done`; reopened as `in_progress`.
- Regenerated `output/` with the new code (live run 20:15 UTC). The notebook still has 3 chart images without pyplot.
- Docker: rebuilt; runs as `app`; endpoints 200; 26 names → 422. Browser: SRI-pinned Chart.js loads; tiles and bars correct (Mumbai 27.1 °C).

## T16: Default city list as a data file (Implementer)
- `data/cities.json` (the brief's 10 cities, unchanged), `load_cities()`, `CITIES_FILE`; `resolve_cities` takes the catalog; the Dockerfile copies `data/`. Closes review finding #11. D15.
- Tests: 79 passed. Live: a catalog with Tokyo (coordinates) plus Lisbon and Nairobi (name only) resolved all three. The image loads 10 cities.

## T17: Manage cities from the frontend (Planner, Implementer, Tester)
- Planner commit first: R16, API-contract rows, feature F13 and this task (the scope change goes through the spec).
- `weather/city_store.py` (TinyDB), `GET/POST /api/cities`, `DELETE /api/cities/{name}`, Cities page + nav, compose volume. `resolve_cities` now takes the catalog explicitly; the pipeline passes the saved list. D16.
- Tests: 99 passed (20 new: store, API contract codes 201/204/404/409/422/502, page). Pyright 0 errors.
- Docker compose + browser: Lisbon added by name (201) and persisted across `restart`; `paris` and `TOKYO` → 409; half-filled coordinates rejected in the form; Nairobi geocoded and added; Lisbon removed (204). Volume writable as `app`.

## T15: README (Implementer)
- Done last on purpose (it depends only on T14), so it describes the finished project: quick start (uv and Docker), outputs, CSV and API guide, managing cities, layout, the approach (spec-driven, task harness, multi-agent roles, independent review) and suggestions (Scrapy vs requests, async, history, Redis/SQLite, Playwright).
- Final state: 18 tasks done (T00–T17), 13 features done, 99 tests, pyright 0 errors, 16 decisions. Every task merged through its own PR with CI green.

## T18: Valid YAML front matter (Implementer, Tester)
- Reported by the stakeholder: GitHub showed "Error in user YAML: mapping values are not allowed" on T15. Cause: unquoted `:` in the T01 and T15 titles. The checker's hand-rolled parser accepted it, so the harness had a blind spot.
- Test first: `test_front_matter_is_valid_yaml` parses every task header with PyYAML; it failed with GitHub's exact error before the fix. Titles quoted, the checker strips quotes, and the rule is in `tasks/README.md`.
- 100 tests pass, pyright 0 errors. GitHub (branch preview): T01 and T15 headers render as tables with no error.

## T19: Pick among same-name cities (Planner, Implementer, Tester)
- Stakeholder question: what happens with a city name that exists in several places? Checked live: "Springfield" silently became Springfield, Missouri; "Springfield, IL" in the dashboard input split into "Springfield" + "IL" → Il, Kenya. The stakeholder chose picking over new columns.
- Planner commit first: R17, the `/api/geocode` contract row, a note that the column set is fixed, F13 extended, task T19. D17.
- `geocoding.search()` (`geocode()` = its first match), `GET /api/geocode`, Find button + match list on the Cities page (rendered with `textContent`).
- Tests: 108 passed (8 new, including a picked match saved with its exact coordinates and the CSV header unchanged). Pyright 0 errors.
- Browser (live geocoder, throwaway DB so the user's local list wasn't touched): "Springfield" → 5 matches (MO, IL, MA, OH, TN). Picked Illinois, then Missouri; both saved as `Springfield (Illinois)` / `Springfield (Missouri)` with their own weather (4.6 °C / 6.1 °C); columns unchanged.
