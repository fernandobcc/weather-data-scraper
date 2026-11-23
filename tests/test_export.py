from weather.export import to_csv, to_csv_text
from weather.pipeline import run

HEADER = ("City,Latitude,Longitude,Temperature (C),Temperature (F),Humidity (%),"
          "Wind Speed (m/s),Wind Speed (mph),Observed At (UTC),Temperature Rank")


def test_pipeline_runs_end_to_end(fake_session):
    df = run(["Tokyo", "Lisbon", "Atlantis"], fake_session)
    assert list(df["City"]) == ["Lisbon", "Tokyo"]
    assert len(fake_session.calls) == 3  # geocode Lisbon, geocode Atlantis, one forecast call


def test_csv_header_matches_contract(fake_session, tmp_path):
    path = to_csv(run([], fake_session), tmp_path / "out" / "weather_data.csv")
    lines = path.read_text().splitlines()
    assert lines[0] == HEADER
    assert len(lines) == 11
    assert lines[1].startswith("Rio de Janeiro,")


def test_csv_text_has_no_index_column(fake_session):
    assert to_csv_text(run(["Paris"], fake_session)).startswith("City,")
