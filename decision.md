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
