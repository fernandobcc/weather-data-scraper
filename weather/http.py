import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def make_session(retries: int = 3) -> requests.Session:
    """Session with retry/backoff on transient errors (429, 5xx)."""
    retry = Retry(total=retries, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers["User-Agent"] = "weather-scraper/1.0"
    return session
