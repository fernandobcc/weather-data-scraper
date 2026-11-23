---
id: T14
title: Independent review and hardening
status: todo
requirements: R1, R3, R7, R12, R13
depends_on: T12, T13
---

## Goal
A reviewer agent with no implementation context checks the code against the spec; real findings are fixed with tests.

## Scope
- Code touched by the findings; `progress.md` (findings table)

## Definition of done
- [ ] Review run by a separate agent that received only the spec and the code
- [ ] Every finding logged in `progress.md` as fixed or accepted, with a reason
- [ ] Every fix has a regression test

## Verify
```bash
grep -q '### Reviewer' progress.md
uv run pytest -q 
```

## Evidence
- _Pending._
