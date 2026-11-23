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
