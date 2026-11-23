"""FastAPI app: uvicorn api.main:app --reload"""
import logging
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator

from api import service
from weather import city_store
from weather.cities import MAX_CITIES, MAX_NAME_LENGTH
from weather.city_store import CityExistsError, CityLimitError, CityNotFoundError
from weather.config import CSV_NAME, ROOT
from weather.errors import UpstreamError
from weather.export import to_csv_text
from weather.http import make_session
from weather.plots import METRICS, bar_chart, to_png_bytes
from weather.processing import rankings

FRONTEND = ROOT / "frontend"
CitiesQuery = Query(None, description=f"Comma-separated city names (max {MAX_CITIES}); empty = saved city list")
log = logging.getLogger(__name__)

app = FastAPI(title="Weather Scraper API", version="1.0.0")
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


def load(cities: str | None) -> pd.DataFrame:
    """Cached pipeline result, mapped to HTTP errors: 422 bad input, 502 provider failure, 404 nothing resolved."""
    try:
        df = service.get_weather(cities)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except UpstreamError as exc:
        log.warning("Upstream failure: %s", exc)
        raise HTTPException(502, "Weather provider error") from exc
    if df.empty:
        raise HTTPException(404, "None of the requested cities could be resolved")
    return df


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")


@app.get("/cities", include_in_schema=False)
def cities_page() -> FileResponse:
    return FileResponse(FRONTEND / "cities.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/weather")
def weather(cities: str | None = CitiesQuery) -> Response:
    return Response(load(cities).to_json(orient="records"), media_type="application/json")


@app.get("/api/rankings")
def get_rankings(cities: str | None = CitiesQuery) -> dict[str, dict[str, Any]]:
    return rankings(load(cities))


@app.get("/api/charts/{metric}.png", responses={200: {"content": {"image/png": {}}}})
def chart(metric: str, cities: str | None = CitiesQuery) -> Response:
    if metric not in METRICS:
        raise HTTPException(404, f"Unknown metric; choose one of {sorted(METRICS)}")
    return Response(to_png_bytes(bar_chart(load(cities), metric)), media_type="image/png")


@app.get("/api/weather.csv")
def download_csv(cities: str | None = CitiesQuery) -> Response:
    headers = {"Content-Disposition": f'attachment; filename="{CSV_NAME}"'}
    return Response(to_csv_text(load(cities)), media_type="text/csv", headers=headers)


class CityIn(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_NAME_LENGTH)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)

    @model_validator(mode="after")
    def both_or_neither(self) -> "CityIn":
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("give both latitude and longitude, or neither")
        return self


@app.get("/api/cities")
def list_cities() -> list[dict]:
    return city_store.get_store().all()


@app.post("/api/cities", status_code=201)
def add_city(body: CityIn) -> dict:
    try:
        city = city_store.get_store().add(body.name, make_session(), body.latitude, body.longitude)
    except (CityExistsError, CityLimitError) as exc:
        detail = f"{exc} is already in the list" if isinstance(exc, CityExistsError) else str(exc)
        raise HTTPException(409, detail) from exc
    except CityNotFoundError as exc:
        raise HTTPException(404, f"Could not find a city called {exc}") from exc
    except UpstreamError as exc:
        log.warning("Upstream failure: %s", exc)
        raise HTTPException(502, "Geocoding provider error") from exc
    service.clear_cache()
    return city


@app.delete("/api/cities/{name}", status_code=204)
def delete_city(name: str) -> Response:
    try:
        city_store.get_store().remove(name)
    except CityNotFoundError as exc:
        raise HTTPException(404, f"{exc} is not in the list") from exc
    service.clear_cache()
    return Response(status_code=204)
