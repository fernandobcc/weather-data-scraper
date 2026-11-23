# Decisions

ADR-style log: context → decision → consequence. Each entry is added in the commit of
the task that made it.

## D01: Spec before code (T00)
- **Context:** The brief mixes required, optional and bonus items, plus stakeholder requests (frontend, notebook, tooling).
- **Decision:** Translate the brief into `specs/spec.md` with numbered requirements and data/API contracts before writing code.
- **Consequence:** Every task, feature and test traces back to an `R` id; changes in scope start as spec edits.

## D02: Task harness with checkable completion (T00)
- **Context:** Agents (and people) tend to call work "done" too early, and a tracker can drift from what actually happened.
- **Decision:** One file per task in `tasks/` with a Definition of done and offline Verify commands. `scripts/check_tasks.py` refuses a `done` task with unchecked boxes, failing commands, unfinished dependencies, or no `Tnn:` commit in git history, and keeps `feature_list.json` in sync. One PR per task.
- **Consequence:** The task board, the feature list and the git history can't disagree without CI failing. Re-running every done task's checks on each PR also catches regressions.

## D03: Tooling: uv, pyright, GitHub Actions (T01)
- **Decision:** `uv` manages Python 3.12 and the lockfile. `pyright[nodejs]` runs in standard mode; the `nodejs` extra bundles Node, so no system Node is needed. CI runs pytest, pyright and `check_tasks.py` on every PR, with full git history (`fetch-depth: 0`) so the harness can see `Tnn:` commits.
- **Consequence:** Installs are reproducible, and every merge re-verifies every done task. Runtime dependencies are added by the task that first needs them, so `pyproject.toml` grows along with the history.

## D04: One batched Open-Meteo request (T03)
- **Context:** Open-Meteo accepts comma-separated latitude/longitude lists.
- **Decision:** Fetch all cities in a single call, and normalise the single-location (object) vs multi-location (list) response.
- **Consequence:** N cities = 1 request: faster and gentler on rate limits. If the call fails, the whole run fails, which is acceptable here.

## D05: Ask the API for °C and m/s explicitly (T03)
- **Context:** The brief derives °F and mph "if the API returns Celsius / m/s", but Open-Meteo defaults wind to km/h.
- **Decision:** Send `temperature_unit=celsius` and `wind_speed_unit=ms`; derive °F and mph in pandas (T05).
- **Consequence:** The output matches the brief's example (5 m/s → 11.2 mph).

## D06: Injected `requests.Session` with retries; one upstream error type (T03)
- **Decision:** `make_session()` retries 429/5xx with backoff. Functions take `session` as a parameter. HTTP errors, bad JSON, payload-shape errors and location-count mismatches all raise `weather.errors.UpstreamError`.
- **Consequence:** Tests use `FakeSession`, with no network and no mocking library. Adapters handle one exception type: the API maps it to 502 and the CLI to exit code 1.

## D07: Geocoding as a fallback, degrading per name (T04)
- **Decision:** Names in the default list use the brief's coordinates; any other name goes to the Open-Meteo geocoding API (same provider, no key). A name that can't be resolved, or whose lookup fails, is skipped with a warning. Results are de-duplicated by name and coordinates.
- **Consequence:** Default runs make no geocoding calls; the bonus works for any city; a partial outage doesn't fail the whole request.

## D08: CSV columns are a superset of the brief's example (T05)
- **Decision:** Keep the brief's six columns in order, and add `Latitude`, `Longitude`, `Observed At (UTC)` and `Temperature Rank`. Measurements are rounded to 1 decimal, coordinates to 4. Humidity is a nullable integer. The column order is defined once (`processing.COLUMNS`).
- **Consequence:** The CSV says where, when and in what order, and the brief's example rows reproduce exactly (tested).

## D09: One pipeline, thin adapters (T07)
- **Decision:** `weather.pipeline.run(names, session)` (resolve → fetch → process) is the only composition point. The CLI, the API and the notebook all call it.
- **Consequence:** No logic is duplicated across adapters, and each adapter stays small and easy to test.

## D10: In-memory TTL cache with a lock in the API (T10)
- **Context:** One dashboard load hits several endpoints (data, rankings, a chart) for the same cities.
- **Decision:** Cache pipeline results for 5 min (Open-Meteo "current" data refreshes every 15 min), keyed by the *set* of city names (order and case don't matter), capped at 128 entries. A lock makes concurrent cache misses share one upstream call.
- **Consequence:** One upstream call per page load. The cache is per-process; use Redis if the API scales out.

## D11: Two chart paths, no frontend build step (T11)
- **Decision:** matplotlib PNGs (the bonus, served by `/api/charts/{metric}.png`) **and** a Chart.js dashboard for interactivity (tooltips, °F/mph toggle, metric switch). Plain HTML/JS/CSS, with Chart.js from a CDN.
- **Consequence:** The bonus is met literally and the UI is better; no Node toolchain. The dashboard needs internet access for the CDN (noted as a suggestion).

## D12: Notebook generated by a script, deliverables committed (T12)
- **Decision:** `scripts/build_notebook.py` builds and executes `output/weather_analysis.ipynb` with nbformat/nbconvert; `scripts/check_notebook.py` validates it (no errors, outputs present, three charts). The CSV, the charts and the notebook from a live run are committed in `output/`.
- **Consequence:** The notebook stays reproducible and in sync with the package API. Reviewers see the real outputs without running anything; re-running refreshes them.
