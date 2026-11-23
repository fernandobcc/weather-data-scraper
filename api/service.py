import threading
import time

import pandas as pd

from weather import pipeline
from weather.cities import parse_city_names

CACHE_TTL_SECONDS = 300  # Open-Meteo "current" data refreshes every 15 min
CACHE_MAX_ENTRIES = 128
_cache: dict[tuple, tuple[float, pd.DataFrame]] = {}
_locks: dict[tuple, threading.Lock] = {}
_registry = threading.Lock()


def _lock_for(key: tuple) -> threading.Lock:
    with _registry:
        return _locks.setdefault(key, threading.Lock())


def get_weather(raw_cities: str | None) -> pd.DataFrame:
    """Pipeline result cached per city set. Concurrent misses for the same set share one upstream call;
    different sets never wait on each other. Raises ValueError for invalid input."""
    names = parse_city_names(raw_cities)
    key = tuple(sorted({n.casefold() for n in names}))
    with _lock_for(key):
        hit = _cache.get(key)
        if hit and time.monotonic() - hit[0] < CACHE_TTL_SECONDS:
            return hit[1]
        df = pipeline.run(names)
        with _registry:
            if key not in _cache and len(_cache) >= CACHE_MAX_ENTRIES:
                oldest = next(iter(_cache))
                _cache.pop(oldest)
                _locks.pop(oldest, None)
            _cache[key] = (time.monotonic(), df)
        return df


def clear_cache() -> None:
    with _registry:
        _cache.clear()
        _locks.clear()
