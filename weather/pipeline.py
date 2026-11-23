import pandas as pd
import requests

from weather import city_store
from weather.client import fetch_current_weather
from weather.geocoding import resolve_cities
from weather.http import make_session
from weather.processing import build_dataframe


def run(city_names: list[str] | None = None, session: requests.Session | None = None,
        catalog: list[dict] | None = None) -> pd.DataFrame:
    """Resolve -> fetch -> process. Shared by the CLI, the API and the notebook; catalog defaults to the saved cities."""
    session = session or make_session()
    catalog = city_store.get_store().all() if catalog is None else catalog
    cities = resolve_cities(city_names or [], session, catalog)
    records = fetch_current_weather(cities, session)
    return build_dataframe(records)
