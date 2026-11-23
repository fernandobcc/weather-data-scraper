import pytest

from tests.test_processing import RECORDS
from weather.plots import METRICS, bar_chart, save_all, to_png_bytes
from weather.processing import build_dataframe


@pytest.mark.parametrize("metric", sorted(METRICS))
def test_bar_chart_png(metric):
    png = to_png_bytes(bar_chart(build_dataframe(RECORDS), metric))
    assert png.startswith(b"\x89PNG") and len(png) > 1000


def test_save_all_writes_three_files(tmp_path):
    paths = save_all(build_dataframe(RECORDS), tmp_path)
    assert sorted(p.name for p in paths) == ["humidity_chart.png", "temperature_chart.png", "wind_chart.png"]
    assert all(p.stat().st_size > 1000 for p in paths)


def test_humidity_labels_are_integers():
    fig = bar_chart(build_dataframe(RECORDS), "humidity")
    labels = [t.get_text() for t in fig.axes[0].texts]
    assert labels and all("." not in label for label in labels)
