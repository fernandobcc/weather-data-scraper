---
id: T01
title: "Project tooling: uv, pytest, pyright and CI"
status: done
requirements: R15
depends_on: T00
---

## Goal
A reproducible Python 3.12 project where every PR runs the gates automatically.

## Scope
- `pyproject.toml`, `uv.lock`, `.python-version`, `.github/workflows/ci.yml`, `tests/test_tasks.py`
- Out of scope: Docker (T13).

## Definition of done
- [x] `uv sync` installs a locked environment
- [x] pyright (standard mode, bundled Node) reports 0 errors
- [x] CI runs pytest, pyright and `check_tasks.py` on PRs and on pushes to main, with full git history
- [x] `tests/test_tasks.py` keeps task files well-formed

## Verify
```bash
uv lock --check --offline
uv run pyright
uv run pytest -q tests/test_tasks.py
grep -q 'fetch-depth: 0' .github/workflows/ci.yml && grep -q 'check_tasks.py' .github/workflows/ci.yml
```

## Manual checks
- The first PR shows a green CI check.

## Evidence
- 2026-11-23 · 4 tests pass, pyright 0 errors, `uv lock --check` clean. CI result shown on the PR.
