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
