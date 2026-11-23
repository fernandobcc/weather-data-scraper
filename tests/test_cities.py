import json

import pytest

from weather.cities import has_coordinates, load_cities, parse_city_names


def test_default_list_has_attached_ten_cities():
    cities = load_cities()
    assert len(cities) == 10
    assert cities[0] == {"City": "New York", "Latitude": 40.7128, "Longitude": -74.006}
    assert cities[-1]["City"] == "Rio de Janeiro"


def test_load_cities_from_another_file(tmp_path):
    path = tmp_path / "cities.json"
    path.write_text(json.dumps([{"City": "Lisbon"}]))
    assert load_cities(path) == [{"City": "Lisbon"}]


def test_has_coordinates():
    assert has_coordinates({"City": "A", "Latitude": 0.0, "Longitude": 0.0})
    assert not has_coordinates({"City": "A"})


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
