import pytest

from weather.cities import DEFAULT_CITIES, known_city, parse_city_names


def test_default_list_has_attached_ten_cities():
    assert len(DEFAULT_CITIES) == 10
    assert DEFAULT_CITIES[0] == {"City": "New York", "Latitude": 40.7128, "Longitude": -74.0060}
    assert DEFAULT_CITIES[-1]["City"] == "Rio de Janeiro"


@pytest.mark.parametrize("name", ["tokyo", "  TOKYO ", "Tokyo"])
def test_known_city_is_case_insensitive(name):
    city = known_city(name)
    assert city is not None and city["City"] == "Tokyo"


def test_unknown_city_is_none():
    assert known_city("Lisbon") is None


@pytest.mark.parametrize("raw, expected", [
    (None, []), ("", []), ("Paris", ["Paris"]), (" Paris , ,Cape Town ", ["Paris", "Cape Town"]),
])
def test_parse_city_names(raw, expected):
    assert parse_city_names(raw) == expected


def test_parse_city_names_limits():
    assert len(parse_city_names(",".join(["Paris"] * 25))) == 25
    with pytest.raises(ValueError):
        parse_city_names(",".join(["Paris"] * 26))
    with pytest.raises(ValueError):
        parse_city_names("x" * 101)
