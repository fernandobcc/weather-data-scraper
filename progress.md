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
