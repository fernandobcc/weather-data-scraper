from pathlib import Path

import pandas as pd


def to_csv(df: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def to_csv_text(df: pd.DataFrame) -> str:
    return df.to_csv(index=False)
