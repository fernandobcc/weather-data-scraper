---
id: T01
title: Project tooling: uv, pytest, pyright and CI
status: in_progress
requirements: R15
depends_on: T00
---

## Goal
A reproducible Python 3.12 project where every PR runs the gates automatically.

## Scope
- `pyproject.toml`, `uv.lock`, `.python-version`, `.github/workflows/ci.yml`, `tests/test_tasks.py`
- Out of scope: Docker (T13).

## Definition of done
- [ ] `uv sync` installs a locked environment
- [ ] pyright (standard mode, bundled Node) reports 0 errors
- [ ] CI runs pytest, pyright and `check_tasks.py` on PRs and on pushes to main, with full git history
- [ ] `tests/test_tasks.py` keeps task files well-formed

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
- _Pending._
