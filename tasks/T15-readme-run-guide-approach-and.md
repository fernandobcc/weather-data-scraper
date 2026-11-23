---
id: T15
title: "README: run guide, approach and suggestions"
status: done
requirements: R15
depends_on: T14
---

## Goal
A reader can run the project, read its outputs, and understand how it was built and what comes next.

## Scope
- `README.md`

## Definition of done
- [x] Quick start for uv and Docker
- [x] Guide to the CSV columns and API endpoints
- [x] Approach: spec-driven, task harness, multi-agent roles
- [x] Suggestions, including Scrapy vs requests

## Verify
```bash
for s in '## Quick start' '### Reading the CSV' '## Approach' '## Suggestions'; do grep -q "$s" README.md || exit 1; done
grep -qi scrapy README.md
```

## Evidence
- 2026-11-23 · All README sections present; the links and numbers (99 tests, D01–D16, PR #16) checked against the repo.
