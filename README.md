# Weather Data Scraper

Fetches current weather (temperature, humidity, wind) for a list of cities from
[Open-Meteo](https://open-meteo.com/), processes it with pandas, exports
`weather_data.csv`, draws charts, and serves everything through a FastAPI API
with an interactive dashboard and a page to manage the saved cities.

[![CI](https://github.com/fernandobcc/weather-data-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/fernandobcc/weather-data-scraper/actions/workflows/ci.yml)

## Quick start

Requires [uv](https://docs.astral.sh/uv/) (or Docker).

```bash
uv sync                                          # Python 3.12 venv + locked dependencies

uv run python main.py                            # saved cities -> output/ (CSV + charts)
uv run python main.py --cities "Lisbon, Tokyo, Nairobi" --sort-by humidity
uv run python main.py --interactive              # prompts for city names

uv run uvicorn api.main:app --reload             # dashboard  http://localhost:8000
                                                 # cities     http://localhost:8000/cities
                                                 # API docs   http://localhost:8000/docs
```

With Docker:

```bash
docker compose up --build                        # API + dashboard on :8000
docker compose run --rm cli                      # CLI run, writes ./output
```

Quality gates (the same ones CI runs on every PR):

```bash
uv run pytest -q                                 # 99 tests, offline
uv run pyright                                   # 0 errors
uv run python scripts/check_tasks.py             # re-verifies every done task
```

## Outputs

| Output | What it is |
|--------|-----------|
| [`output/weather_data.csv`](output/weather_data.csv) | The required deliverable |
| `output/{temperature,humidity,wind}_chart.png` | matplotlib bar charts (bonus) |
| [`output/weather_analysis.ipynb`](output/weather_analysis.ipynb) | Executed notebook: table, rankings, filters, charts, geocoding demo |
| `http://localhost:8000` | Dashboard: city input, metric switch, °F/mph toggle, highlights, charts, table, CSV download |

The committed outputs come from a live run. Regenerate them with
`uv run python main.py && uv run python scripts/build_notebook.py`.

### Reading the CSV

| Column | Meaning |
|--------|---------|
| `City`, `Latitude`, `Longitude` | Location (from the saved list, or geocoded) |
| `Temperature (C)` / `Temperature (F)` | 2 m air temperature; F = C × 9/5 + 32 |
| `Humidity (%)` | Relative humidity at 2 m |
| `Wind Speed (m/s)` / `Wind Speed (mph)` | 10 m wind speed; mph = m/s × 2.236936 |
| `Observed At (UTC)` | Open-Meteo observation time (15-minute resolution) |
| `Temperature Rank` | 1 = hottest; rows are sorted by it |

The CLI also prints the **highlights**: hottest, coldest, most humid, driest and windiest city.

### Managing cities

The saved list starts as the 10 cities from the brief ([`data/cities.json`](data/cities.json))
and lives in a small [TinyDB](https://tinydb.readthedocs.io/) file, `db/cities.json`.
Use the **Cities** page or the API to add a city by name (its coordinates are looked
up once) or with explicit coordinates, and to remove one. Up to 25 cities.
A one-off `--cities` run or the dashboard input doesn't change the saved list.
To reset, delete `db/cities.json`.

### API

| Endpoint | Returns |
|----------|---------|
| `GET /api/weather?cities=A,B` | JSON rows (same columns as the CSV) |
| `GET /api/rankings?cities=A,B` | Hottest / coldest / most humid / driest / windiest |
| `GET /api/charts/{temperature\|humidity\|wind}.png` | matplotlib PNG |
| `GET /api/weather.csv?cities=A,B` | CSV download |
| `GET /api/cities` · `POST /api/cities` · `DELETE /api/cities/{name}` | Saved city list |
| `GET /health` | Liveness |

`cities` is optional and defaults to the saved list. Unknown names are skipped (`404` if
none resolve). Bad input → `422`. Weather or geocoding provider failure → `502`.
The full contract is in [`specs/spec.md`](specs/spec.md).

## Project layout

```
├── specs/spec.md       requirements R1–R16, data and API contracts (source of truth)
├── tasks/              one file per task: Definition of done + Verify commands
├── feature_list.json   features ↔ requirements ↔ tasks
├── progress.md         work log, one entry per task (incl. the review findings)
├── decision.md         architecture decisions D01–D16
├── AGENTS.md           how agents and humans work here (CLAUDE.md imports it)
├── weather/            core package, one concern per module
│   ├── cities.py         load data/cities.json, parse and limit input
│   ├── city_store.py     TinyDB saved city list
│   ├── http.py           requests.Session with retries
│   ├── client.py         Open-Meteo forecast, one batched call
│   ├── geocoding.py      name → coordinates (bonus)
│   ├── processing.py     pandas: units, rounding, ranking, filters
│   ├── plots.py          matplotlib charts (thread-safe Figure API)
│   ├── export.py         CSV
│   └── pipeline.py       resolve → fetch → process
├── api/                FastAPI adapter (+ per-city-set cache)
├── frontend/           dashboard + Cities page (HTML, Chart.js)
├── main.py             CLI adapter
├── scripts/            task checker, notebook builder and checker
├── data/  db/          seed city list · runtime TinyDB (gitignored)
├── tests/              offline tests (FakeSession, temporary city store)
└── output/             generated deliverables
```

## Approach

### Spec-driven development

Before any code, the brief was turned into [`specs/spec.md`](specs/spec.md): numbered
requirements, an exact data contract (columns, rounding, conversions) and an API
contract. Scope changes go through the spec first. When the stakeholder asked to
manage cities from the UI, R16 and its API rows were added in a planner commit
before any implementation ([PR #16](https://github.com/fernandobcc/weather-data-scraper/pull/16)).

### A task harness with checkable completion

The work was split into [`tasks/`](tasks/). Each task has a **Definition of done** and
**Verify** commands that are deterministic and run offline. [`scripts/check_tasks.py`](scripts/check_tasks.py)
treats a task as done only if:

- every Definition-of-done box is ticked and every Verify command passes;
- its dependencies are done;
- git history contains commits whose subject starts with `Tnn:`;
- the matching feature in `feature_list.json` has the same status.

CI runs the checker on every PR and re-verifies *all* done tasks, so a later change
that breaks an earlier task fails the build. Each task was built on its own branch
(work commit(s) → `Tnn: mark done`) and merged through its own PR with CI green.
`progress.md` and `decision.md` were updated in the same commits, so the tracker and
the history tell the same story.

The harness also caught mistakes as they happened. In T14, adding a follow-up task
to a finished feature left that feature marked `done`, and the checker failed the
build until it was reopened.

### Multi-agent roles

[`AGENTS.md`](AGENTS.md) defines four roles:

- **Planner:** brief → spec, tasks, feature list.
- **Implementer:** one task at a time.
- **Tester:** the gates, plus each task's manual checks against the live API, the browser and Docker.
- **Reviewer:** reviews the code against the spec.

The review in T14 was done by a **separate agent that received only the spec and the
code**, not the implementer's notes, so its reading wasn't anchored on them. It found
12 issues, including a 500 on all-null metrics, outages being reported as "not found",
unbounded input and a global lock held during I/O. Each one was fixed with a
regression test or explicitly accepted. The findings table is in [`progress.md`](progress.md).

### Design choices (details in [`decision.md`](decision.md))

- **One HTTP call for all cities.** Open-Meteo accepts coordinate lists (D04).
- **Units requested explicitly** (°C, m/s), then converted in pandas, so the brief's example rows reproduce exactly (D05, D08).
- **Injected sessions and one `UpstreamError` type,** so tests use no network and adapters map errors to 502 or exit 1 (D06, D14).
- **One pipeline, thin adapters:** the CLI, the API and the notebook share `pipeline.run()` (D09).
- **Data, not code:** the default city list is a JSON seed, and the saved list lives in TinyDB (D15, D16).

## Suggestions / next steps

- **Scrapy instead of requests** if this grows into real crawling (many sources, HTML pages, pagination). Scrapy brings concurrency, throttling, retries, item pipelines and feed exports (CSV/JSON). For one JSON API, `requests` (or async `httpx`) stays simpler, which is why it's used here.
- **Async fetching** (`httpx.AsyncClient`) for providers that can't batch locations.
- **Persist history** (SQLite/DuckDB) to chart trends over time instead of snapshots, and **schedule runs** (cron / GitHub Actions) to refresh the CSV.
- **Shared cache** (Redis) and SQLite instead of TinyDB once the API runs more than one worker.
- **Pydantic response models** for typed contracts and richer OpenAPI docs.
- **Self-host Chart.js** so the dashboard works offline (it's already pinned with SRI).
- **Browser tests** (Playwright) to turn the manual dashboard checks into Verify commands.
