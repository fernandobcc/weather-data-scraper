---
id: T13
title: Docker image and compose
status: todo
requirements: R15
depends_on: T11
---

## Goal
`docker compose up` serves the API and dashboard; a compose profile runs the CLI.

## Scope
- `Dockerfile`, `docker-compose.yml`, `.dockerignore`

## Definition of done
- [ ] The image installs from `uv.lock` with a uv version that matches the lockfile
- [ ] The image runs uvicorn on :8000 with a healthcheck
- [ ] `cli` profile writes to `./output`

## Verify
```bash
grep -q 'uv sync --frozen --no-dev' Dockerfile && grep -q 'astral-sh/uv:0.9' Dockerfile
grep -q 'healthcheck' docker-compose.yml && grep -q 'profiles: \["cli"\]' docker-compose.yml
grep -q '\*\*/__pycache__' .dockerignore
```

## Manual checks
- `docker build` succeeds; container `/health` and `/api/weather` answer 200.

## Evidence
- _Pending._
