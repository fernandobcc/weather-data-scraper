# AGENTS.md

Operating guide for AI coding agents (Claude Code, Codex, Cursor…) and humans
working in this repo. Read this first, then follow the loop.

## Source of truth (read in this order)

1. `specs/spec.md`: requirements (R1…), data contract, API contract.
2. `tasks/`: units of work, each with a Definition of done and Verify commands ([how it works](tasks/README.md)).
3. `feature_list.json`: features ↔ requirements ↔ tasks, with status.
4. `progress.md`: what was done, by which role, and what's next.
5. `decision.md`: architecture decisions. Don't reverse one silently; add a new entry.

## The loop

1. `python scripts/check_tasks.py --list`, then pick a `todo` task whose dependencies are `done`.
2. Branch `tNN-short-name`; set the task to `in_progress`.
3. Write or extend the tests named in the task's Verify block, then implement.
4. Work commit(s): `Tnn: <what changed>`.
5. Gates, all green:
   ```bash
   uv run pytest -q
   uv run pyright
   uv run python scripts/check_tasks.py Tnn
   ```
6. Done commit `Tnn: mark done`: tick the boxes, fill in Evidence, flip the feature, log `progress.md`.
7. One PR per task; merge only when CI is green.

Never mark a task `done` by hand-waving: the checker rejects a done task with
unchecked boxes, failing Verify commands, or no `Tnn:` commits.

## Agent roles

| Role | Responsibility | Writes to |
|------|----------------|-----------|
| Planner | Brief → `specs/spec.md`, `tasks/`, `feature_list.json` | specs, tasks, feature list |
| Implementer | One task at a time, against its Definition of done | code, tests, task file |
| Tester | Gates plus the task's manual checks (live API, browser, Docker) | task Evidence, progress |
| Reviewer | Independent review of the code against the spec, without the implementer's reasoning | findings in progress, new tasks |

Roles can be separate subagents or sequential passes by one agent. The reviewer
gets the spec and the code, **not** the implementer's conclusions.

## Code conventions

- Small single-purpose modules; `api/` and `main.py` are thin adapters over `weather/pipeline.py`.
- HTTP sessions are injected (`session` parameter); tests use `tests/conftest.py::FakeSession` and never touch the network.
- The output column order is defined once, in `weather/processing.py::COLUMNS`.
- Data belongs in data files, not in Python modules.
- Short comments; clear names; one-line docstrings. Type hints everywhere; pyright stays at 0 errors.

## Commands

```bash
uv sync                                       # install
uv run python main.py                         # CLI -> output/
uv run uvicorn api.main:app --reload          # API + dashboard on :8000
uv run python scripts/check_tasks.py --list   # task board
docker compose up --build                     # API in Docker
```
