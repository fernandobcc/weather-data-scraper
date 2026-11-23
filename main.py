"""CLI: python main.py [--cities "Paris,Lisbon"] [--interactive] [--sort-by humidity]"""
import argparse
import logging
import sys

import pandas as pd

from weather import pipeline
from weather.cities import parse_city_names
from weather.config import CSV_NAME, OUTPUT_DIR
from weather.errors import UpstreamError
from weather.export import to_csv
from weather.plots import save_all
from weather.processing import rankings

SORT_COLUMNS = {
    "temperature": ("Temperature (C)", False),
    "humidity": ("Humidity (%)", True),
    "wind": ("Wind Speed (m/s)", False),
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch, process and export current weather.")
    p.add_argument("--cities", help="Comma-separated city names (default: the 10 attached cities)")
    p.add_argument("--interactive", action="store_true", help="Prompt for city names")
    p.add_argument("--sort-by", choices=SORT_COLUMNS, default="temperature", help="Display order")
    p.add_argument("--no-charts", action="store_true", help="Skip PNG chart generation")
    return p.parse_args(argv)


def ask_cities() -> str:
    return input("Cities (comma-separated, empty for default list): ")


def show(df: pd.DataFrame, sort_by: str) -> None:
    column, ascending = SORT_COLUMNS[sort_by]
    with pd.option_context("display.width", 160, "display.max_columns", None):
        print(df.sort_values(column, ascending=ascending).to_string(index=False))
    print("\nHighlights:")
    for label, item in rankings(df).items():
        print(f"  {label:<11} {item['city']:<16} {item['value']} {item['metric']}")


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    raw = ask_cities() if args.interactive else args.cities
    try:
        df = pipeline.run(parse_city_names(raw))
    except UpstreamError as exc:
        logging.error("Weather API request failed: %s", exc)
        return 1
    if df.empty:
        logging.error("No cities could be resolved.")
        return 1

    show(df, args.sort_by)
    csv_path = to_csv(df, OUTPUT_DIR / CSV_NAME)
    print(f"\nSaved {csv_path}")
    if not args.no_charts:
        for path in save_all(df, OUTPUT_DIR):
            print(f"Saved {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
