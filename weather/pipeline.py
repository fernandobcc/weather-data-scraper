import pandas as pd
import requests

from weather.client import fetch_current_weather
from weather.geocoding import resolve_cities
from weather.http import make_session
from weather.processing import build_dataframe


def run(city_names: list[str] | None = None, session: requests.Session | None = None) -> pd.DataFrame:
    """Resolve -> fetch -> process. Shared by the CLI, the API and the notebook."""
    session = session or make_session()
    cities = resolve_cities(city_names or [], session)
    records = fetch_current_weather(cities, session)
    return build_dataframe(records)
