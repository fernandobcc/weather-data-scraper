from tests.test_processing import RECORDS
from weather.processing import build_dataframe, filter_range, rankings, top_n


def test_top_n_and_filter():
    df = build_dataframe(RECORDS)
    assert list(top_n(df, "Humidity (%)", 1, ascending=True)["City"]) == ["Tokyo"]
    assert list(top_n(df, "Wind Speed (m/s)", 2)["City"]) == ["New York", "London"]
    assert set(filter_range(df, "Temperature (C)", min_value=11)["City"]) == {"Tokyo", "London"}
    assert set(filter_range(df, "Temperature (C)", max_value=12)["City"]) == {"London", "New York"}


def test_rankings():
    r = rankings(build_dataframe(RECORDS))
    assert {k: v["city"] for k, v in r.items()} == {
        "hottest": "Tokyo", "coldest": "New York", "most_humid": "New York", "driest": "Tokyo", "windiest": "New York",
    }
    assert isinstance(r["hottest"]["value"], float) and isinstance(r["driest"]["value"], int)


def test_rankings_empty():
    assert rankings(build_dataframe([])) == {}


def test_rankings_skip_all_null_metric_and_report_row():
    records = [dict(r, **{"Humidity (%)": None}) for r in RECORDS]
    df = build_dataframe(records)
    r = rankings(df)
    assert "most_humid" not in r and "driest" not in r
    assert df.iloc[r["hottest"]["row"]]["City"] == r["hottest"]["city"] == "Tokyo"
