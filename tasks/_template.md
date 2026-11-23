---
id: Tnn
title: Short imperative title
status: todo
requirements: R?
depends_on:
---

## Goal
One or two sentences: the outcome, and which spec requirement it serves.

## Scope
- Files expected to change.
- Out of scope: what this task deliberately does not do.

## Definition of done
- [ ] Observable outcome 1
- [ ] Observable outcome 2
- [ ] All gates green (`pytest`, `pyright`, `check_tasks.py`)

## Verify
```bash
uv run pytest -q tests/test_x.py::test_y
```

## Manual checks
- Network / browser / Docker checks that can't run offline.

## Evidence
- Filled in by the done commit: what was run and observed.
