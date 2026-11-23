---
id: T08
title: Command-line interface
status: done
requirements: R8, R9
depends_on: T06, T07
---

## Goal
Take cities from arguments or a prompt, print the table and highlights, and save `output/weather_data.csv`.

## Scope
- `main.py`

## Definition of done
- [x] `--cities`, `--interactive` and `--sort-by` work
- [x] Prints the table and highlights
- [x] Exits 1 when nothing resolves or the upstream API fails

## Verify
```bash
uv run pytest -q tests/test_cli.py
```

## Manual checks
- `uv run python main.py` against the live API.

## Evidence
- 2026-11-23 · `tests/test_cli.py` 4 cases pass; pyright 0 errors.
- Manual: live run with three cities printed the table and highlights and saved the CSV.
