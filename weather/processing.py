from typing import Any

import pandas as pd

MS_TO_MPH = 2.236936

COLUMNS = [
    "City",
    "Latitude",
    "Longitude",
    "Temperature (C)",
    "Temperature (F)",
    "Humidity (%)",
    "Wind Speed (m/s)",
    "Wind Speed (mph)",
    "Observed At (UTC)",
    "Temperature Rank",
]


def celsius_to_fahrenheit(c: Any) -> Any:
    return c * 9 / 5 + 32


def ms_to_mph(ms: Any) -> Any:
    return ms * MS_TO_MPH


def build_dataframe(records: list[dict]) -> pd.DataFrame:
    """Records -> DataFrame with derived units, sorted hottest first."""
    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame(columns=COLUMNS)
    df["Temperature (F)"] = celsius_to_fahrenheit(df["Temperature (C)"])
    df["Wind Speed (mph)"] = ms_to_mph(df["Wind Speed (m/s)"])
    df = df.round({"Latitude": 4, "Longitude": 4, "Temperature (C)": 1, "Temperature (F)": 1,
                   "Wind Speed (m/s)": 1, "Wind Speed (mph)": 1})
    df["Humidity (%)"] = df["Humidity (%)"].astype("Float64").round().astype("Int64")
    df = df.sort_values("Temperature (C)", ascending=False, ignore_index=True)
    df["Temperature Rank"] = df["Temperature (C)"].rank(ascending=False, method="min").astype("Int64")
    return df.reindex(columns=COLUMNS)


def top_n(df: pd.DataFrame, column: str, n: int = 3, ascending: bool = False) -> pd.DataFrame:
    return df.sort_values(column, ascending=ascending).head(n)


def filter_range(df: pd.DataFrame, column: str, min_value: float | None = None,
                 max_value: float | None = None) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    if min_value is not None:
        mask &= df[column] >= min_value
    if max_value is not None:
        mask &= df[column] <= max_value
    return df.loc[mask]


def rankings(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Headline extremes used by the CLI, API and notebook."""
    if df.empty:
        return {}

    def pick(column: str, largest: bool) -> dict[str, Any]:
        row = df.loc[df[column].idxmax() if largest else df[column].idxmin()]
        value = row[column]
        return {"city": row["City"], "value": getattr(value, "item", lambda: value)(), "metric": column}

    return {
        "hottest": pick("Temperature (C)", True),
        "coldest": pick("Temperature (C)", False),
        "most_humid": pick("Humidity (%)", True),
        "driest": pick("Humidity (%)", False),
        "windiest": pick("Wind Speed (m/s)", True),
    }
