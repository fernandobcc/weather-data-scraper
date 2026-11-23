import pandas as pd
import pytest

from weather.processing import COLUMNS, build_dataframe, celsius_to_fahrenheit, ms_to_mph

RECORDS = [
    {"City": "New York", "Latitude": 40.7128, "Longitude": -74.006, "Temperature (C)": 10.0, "Humidity (%)": 80,
     "Wind Speed (m/s)": 5.0, "Observed At (UTC)": "t"},
    {"City": "Tokyo", "Latitude": 35.6895, "Longitude": 139.6917, "Temperature (C)": 15.0, "Humidity (%)": 60,
     "Wind Speed (m/s)": 3.0, "Observed At (UTC)": "t"},
    {"City": "London", "Latitude": 51.5074, "Longitude": -0.1278, "Temperature (C)": 12.0, "Humidity (%)": 70,
     "Wind Speed (m/s)": 4.0, "Observed At (UTC)": "t"},
]


@pytest.mark.parametrize("c, f", [(0.0, 32), (100.0, 212), (-40.0, -40), (10.0, 50)])
def test_celsius_to_fahrenheit(c, f):
    assert celsius_to_fahrenheit(c) == pytest.approx(f)


def test_ms_to_mph():
    assert ms_to_mph(5.0) == pytest.approx(11.18, abs=0.01)


def test_build_dataframe_matches_pdf_example():
    """Same three rows as the brief's example table."""
    df = build_dataframe(RECORDS)
    assert list(df.columns) == COLUMNS
    assert list(df["City"]) == ["Tokyo", "London", "New York"]
    assert list(df["Temperature Rank"]) == [1, 2, 3]
    rows = df.set_index("City")
    assert rows.loc["New York", "Temperature (F)"] == 50.0 and rows.loc["New York", "Wind Speed (mph)"] == 11.2
    assert rows.loc["Tokyo", "Temperature (F)"] == 59.0 and rows.loc["Tokyo", "Wind Speed (mph)"] == 6.7
    assert rows.loc["London", "Temperature (F)"] == 53.6 and rows.loc["London", "Wind Speed (mph)"] == 8.9


def test_build_dataframe_empty():
    assert list(build_dataframe([]).columns) == COLUMNS


def test_rounding_and_null_humidity():
    record = dict(RECORDS[0], **{"Temperature (C)": 10.04, "Wind Speed (m/s)": 2.95, "Humidity (%)": None,
                                 "Latitude": 1.123456})
    row = build_dataframe([record]).iloc[0]
    assert row["Temperature (C)"] == 10.0
    assert row["Wind Speed (m/s)"] == 3.0
    assert row["Wind Speed (mph)"] == 6.6
    assert row["Latitude"] == 1.1235
    assert row["Humidity (%)"] is pd.NA
