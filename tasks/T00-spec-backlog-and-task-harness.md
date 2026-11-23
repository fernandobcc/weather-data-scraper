---
id: T00
title: Spec, backlog and task harness
status: done
requirements: R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14, R15
depends_on: 
---

## Goal
Turn the brief into a numbered spec, a task backlog with checkable completion, and the agent operating docs, before writing any code.

## Scope
- `specs/spec.md`, `tasks/`, `scripts/check_tasks.py`, `feature_list.json`, `AGENTS.md`, `CLAUDE.md`, `progress.md`, `decision.md`, README stub
- Out of scope: application code.

## Definition of done
- [x] Spec lists R1–R15 with sources, plus data and API contracts
- [x] Every requirement is covered by at least one task
- [x] `check_tasks.py` validates task files, git history and `feature_list.json`
- [x] `AGENTS.md` describes the loop, roles and commit convention

## Verify
```bash
grep -q '| R15 |' specs/spec.md && grep -q '## Data contract' specs/spec.md && grep -q '## API contract' specs/spec.md
python3 scripts/check_tasks.py --list
for r in R1 R2 R3 R4 R5 R6 R7 R8 R9 R10 R11 R12 R13 R14 R15; do grep -lq "requirements:.*\b$r\b" tasks/T0[1-9]*.md tasks/T1*.md || exit 1; done
```

## Manual checks
- Probe Open-Meteo forecast (batched coordinates) and geocoding endpoints before fixing the contracts.

## Evidence
- 2026-11-23 · Planner role. All 3 Verify commands pass; the coverage check was also tested with a fake R99 (correctly reported as uncovered).
- Open-Meteo probe: batched coordinates return a list (an object for one location); the geocoding API works without a key.
