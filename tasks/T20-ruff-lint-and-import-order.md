---
id: T20
title: Ruff lint and import order as a CI gate
status: in_progress
requirements: R15
depends_on: T01, T19
---

## Goal
Imports were not consistently sorted and nothing checked style. Add ruff (pycodestyle, pyflakes, isort, bugbear, pyupgrade) to the gates, locally and in CI, so it stays clean.

## Scope
- `pyproject.toml` (`[tool.ruff]`), `.github/workflows/ci.yml`, code touched by the findings, `AGENTS.md`, README gates.
- Out of scope: `ruff format` (a whole-repo reformat); generated files in `output/`.

## Definition of done
- [ ] Ruff configured in `pyproject.toml` (line length 120, rules E/F/W/I/B/UP, `output/` excluded)
- [ ] `ruff check .` reports 0 findings
- [ ] CI runs ruff before the tests
- [ ] AGENTS.md and the README list ruff among the gates

## Verify
```bash
uv run ruff check .
grep -q 'ruff check' .github/workflows/ci.yml
grep -q 'ruff check' AGENTS.md
```

## Evidence
- _Pending._
