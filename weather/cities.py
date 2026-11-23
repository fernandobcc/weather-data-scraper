DEFAULT_CITIES = [
    {"City": "New York", "Latitude": 40.7128, "Longitude": -74.0060},
    {"City": "Tokyo", "Latitude": 35.6895, "Longitude": 139.6917},
    {"City": "London", "Latitude": 51.5074, "Longitude": -0.1278},
    {"City": "Paris", "Latitude": 48.8566, "Longitude": 2.3522},
    {"City": "Berlin", "Latitude": 52.5200, "Longitude": 13.4050},
    {"City": "Sydney", "Latitude": -33.8688, "Longitude": 151.2093},
    {"City": "Mumbai", "Latitude": 19.0760, "Longitude": 72.8777},
    {"City": "Cape Town", "Latitude": -33.9249, "Longitude": 18.4241},
    {"City": "Moscow", "Latitude": 55.7558, "Longitude": 37.6173},
    {"City": "Rio de Janeiro", "Latitude": -22.9068, "Longitude": -43.1729},
]

_BY_NAME = {c["City"].casefold(): c for c in DEFAULT_CITIES}


def known_city(name: str) -> dict | None:
    return _BY_NAME.get(name.strip().casefold())


MAX_CITIES = 25
MAX_NAME_LENGTH = 100


def parse_city_names(raw: str | None) -> list[str]:
    """Split comma-separated input; ValueError past MAX_CITIES names or MAX_NAME_LENGTH characters."""
    names = [n.strip() for n in (raw or "").split(",") if n.strip()]
    if len(names) > MAX_CITIES:
        raise ValueError(f"at most {MAX_CITIES} cities per request")
    if any(len(n) > MAX_NAME_LENGTH for n in names):
        raise ValueError(f"city names are limited to {MAX_NAME_LENGTH} characters")
    return names
