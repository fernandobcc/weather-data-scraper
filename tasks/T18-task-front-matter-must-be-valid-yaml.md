---
id: T18
title: Task front matter must be valid YAML
status: done
requirements: R15
depends_on: T15
---

## Goal
GitHub renders each task's front matter as YAML. Titles containing `:` (T01, T15) broke the rendering ("mapping values are not allowed"), and the hand-rolled parser in `check_tasks.py` didn't notice. Make every task header valid YAML and keep it that way.

## Scope
- `tasks/*.md` headers, `scripts/check_tasks.py` (quoted values), `tests/test_tasks.py`, `tasks/README.md`.
- Out of scope: changing what tasks contain.

## Definition of done
- [x] A test parses every task header (and the template) with a real YAML parser
- [x] T01 and T15 titles are quoted; GitHub renders their headers as a table
- [x] `check_tasks.py` reads quoted values without the quotes
- [x] `tasks/README.md` tells authors to quote values containing `:`

## Verify
```bash
uv run pytest -q tests/test_tasks.py
uv run python scripts/check_tasks.py --list
```

## Manual checks
- Open T01 and T15 on GitHub: no YAML error, header shown as a table.

## Evidence
- 2026-11-23 · The new YAML test failed first (same ScannerError as GitHub), then passed; 100 tests, pyright 0 errors.
- Manual: T01 and T15 opened on GitHub, headers rendered as tables, no YAML error.
