import pytest

import main
from weather.errors import UpstreamError
from weather.pipeline import run as real_run


@pytest.fixture
def cli(fake_session, monkeypatch, tmp_path):
    monkeypatch.setattr(main, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(main.pipeline, "run", lambda names: real_run(names, fake_session))
    return tmp_path


def test_cli_writes_csv(cli, capsys):
    assert main.main(["--cities", "Tokyo,Lisbon", "--sort-by", "humidity"]) == 0
    assert (cli / "weather_data.csv").read_text().splitlines()[0].startswith("City,Latitude")
    out = capsys.readouterr().out
    assert "Highlights" in out and "hottest" in out


def test_cli_interactive(cli, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "Berlin")
    assert main.main(["--interactive"]) == 0
    assert "Berlin" in (cli / "weather_data.csv").read_text()


def test_cli_no_resolvable_cities(cli):
    assert main.main(["--cities", "Atlantis"]) == 1
    assert not (cli / "weather_data.csv").exists()


def test_cli_upstream_error(monkeypatch, tmp_path):
    def boom(names):
        raise UpstreamError("down")

    monkeypatch.setattr(main, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(main.pipeline, "run", boom)
    assert main.main([]) == 1
