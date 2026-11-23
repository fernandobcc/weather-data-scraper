---
id: T08
title: Command-line interface
status: in_progress
requirements: R8, R9
depends_on: T06, T07
---

## Goal
Take cities from arguments or a prompt, print the table and highlights, and save `output/weather_data.csv`.

## Scope
- `main.py`

## Definition of done
- [ ] `--cities`, `--interactive` and `--sort-by` work
- [ ] Prints the table and highlights
- [ ] Exits 1 when nothing resolves or the upstream API fails

## Verify
```bash
uv run pytest -q tests/test_cli.py
```

## Manual checks
- `uv run python main.py` against the live API.

## Evidence
- _Pending._
