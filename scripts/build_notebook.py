"""Generate and execute <OUTPUT_DIR>/weather_analysis.ipynb (uv run python scripts/build_notebook.py)."""
import sys
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from weather.config import OUTPUT_DIR  # noqa: E402

NOTEBOOK = OUTPUT_DIR / "weather_analysis.ipynb"

CELLS = [
    new_markdown_cell("# Weather analysis\nLive data from Open-Meteo, processed with the `weather` package."),
    new_code_cell(
        "import sys, pathlib\n"
        "sys.path.insert(0, str(pathlib.Path.cwd()))  # executed from the project root\n"
        "from weather import pipeline\n"
        "from weather.processing import top_n, filter_range, rankings\n"
        "from weather.plots import bar_chart\n"
        "%matplotlib inline"
    ),
    new_markdown_cell("## 1. Fetch + process (default 10 cities)"),
    new_code_cell("df = pipeline.run()\ndf"),
    new_markdown_cell("## 2. Rankings and filters"),
    new_code_cell("rankings(df)"),
    new_code_cell('top_n(df, "Humidity (%)", n=3, ascending=True)[["City", "Humidity (%)"]]'),
    new_code_cell('filter_range(df, "Temperature (C)", min_value=15)[["City", "Temperature (C)", "Temperature (F)"]]'),
    new_markdown_cell("## 3. Charts"),
    new_code_cell('bar_chart(df, "temperature")'),
    new_code_cell('bar_chart(df, "humidity")'),
    new_code_cell('bar_chart(df, "wind")'),
    new_markdown_cell("## 4. Bonus: geocoded cities"),
    new_code_cell(
        'pipeline.run(["Lisbon", "Buenos Aires", "Nairobi"])[["City", "Latitude", "Longitude", "Temperature (C)"]]'
    ),
]


def main() -> None:
    nb = new_notebook(cells=CELLS)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    ExecutePreprocessor(timeout=120, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(ROOT)}})
    NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
    NOTEBOOK.write_text(nbformat.writes(nb))
    print(f"Saved {NOTEBOOK}")


if __name__ == "__main__":
    main()
