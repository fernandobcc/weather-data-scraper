---
id: T15
title: README: run guide, approach and suggestions
status: in_progress
requirements: R15
depends_on: T14
---

## Goal
A reader can run the project, read its outputs, and understand how it was built and what comes next.

## Scope
- `README.md`

## Definition of done
- [ ] Quick start for uv and Docker
- [ ] Guide to the CSV columns and API endpoints
- [ ] Approach: spec-driven, task harness, multi-agent roles
- [ ] Suggestions, including Scrapy vs requests

## Verify
```bash
for s in '## Quick start' '### Reading the CSV' '## Approach' '## Suggestions'; do grep -q "$s" README.md || exit 1; done
grep -qi scrapy README.md
```

## Evidence
- _Pending._
