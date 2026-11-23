"""FastAPI app: uvicorn api.main:app --reload"""
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response

from api import service
from weather.config import CSV_NAME
from weather.errors import UpstreamError
from weather.export import to_csv_text
from weather.plots import METRICS, bar_chart, to_png_bytes
from weather.processing import rankings

CitiesQuery = Query(None, description="Comma-separated city names; empty = default 10 cities")

app = FastAPI(title="Weather Scraper API", version="1.0.0")


def load(cities: str | None) -> pd.DataFrame:
    try:
        df = service.get_weather(cities)
    except UpstreamError as exc:
        raise HTTPException(502, f"Weather provider error: {exc}") from exc
    if df.empty:
        raise HTTPException(404, "None of the requested cities could be resolved")
    return df


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/weather")
def weather(cities: str | None = CitiesQuery):
    return Response(load(cities).to_json(orient="records"), media_type="application/json")


@app.get("/api/rankings")
def get_rankings(cities: str | None = CitiesQuery):
    return rankings(load(cities))


@app.get("/api/charts/{metric}.png", responses={200: {"content": {"image/png": {}}}})
def chart(metric: str, cities: str | None = CitiesQuery):
    if metric not in METRICS:
        raise HTTPException(404, f"Unknown metric; choose one of {sorted(METRICS)}")
    png = to_png_bytes(bar_chart(load(cities), metric))
    return Response(png, media_type="image/png")


@app.get("/api/weather.csv")
def download_csv(cities: str | None = CitiesQuery):
    headers = {"Content-Disposition": f'attachment; filename="{CSV_NAME}"'}
    return Response(to_csv_text(load(cities)), media_type="text/csv", headers=headers)
