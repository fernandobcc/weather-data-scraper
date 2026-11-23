import threading
import time

import pandas as pd

from weather import pipeline
from weather.cities import parse_city_names

CACHE_TTL_SECONDS = 300  # Open-Meteo "current" data refreshes every 15 min
CACHE_MAX_ENTRIES = 128
_cache: dict[tuple, tuple[float, pd.DataFrame]] = {}
_lock = threading.Lock()


def get_weather(raw_cities: str | None) -> pd.DataFrame:
    """Pipeline result cached per city set; the lock makes concurrent misses share one upstream call."""
    names = parse_city_names(raw_cities)
    key = tuple(sorted({n.casefold() for n in names}))
    with _lock:
        hit = _cache.get(key)
        if hit and time.monotonic() - hit[0] < CACHE_TTL_SECONDS:
            return hit[1]
        df = pipeline.run(names)
        if len(_cache) >= CACHE_MAX_ENTRIES:
            _cache.pop(next(iter(_cache)))
        _cache[key] = (time.monotonic(), df)
        return df


def clear_cache() -> None:
    _cache.clear()
