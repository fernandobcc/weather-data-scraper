import io
from pathlib import Path

import pandas as pd
from matplotlib.figure import Figure

BAR_COLOR = "#2a78d6"
INK = "#52514e"

METRICS = {  # metric -> (column, title, bar-label format)
    "temperature": ("Temperature (C)", "Current temperature (°C)", "%.1f"),
    "humidity": ("Humidity (%)", "Relative humidity (%)", "%.0f"),
    "wind": ("Wind Speed (m/s)", "Wind speed (m/s)", "%.1f"),
}


def bar_chart(df: pd.DataFrame, metric: str) -> Figure:
    """Horizontal bar chart, largest value on top, values labelled at bar ends."""
    column, title, fmt = METRICS[metric]
    data = df.sort_values(column)
    fig = Figure(figsize=(8, 0.45 * len(data) + 1.2))  # no pyplot: thread-safe in the API
    ax = fig.subplots()
    bars = ax.barh(data["City"], data[column], color=BAR_COLOR, height=0.6)
    ax.bar_label(bars, fmt=fmt, padding=4, color=INK, fontsize=9)
    ax.set_title(title, loc="left", fontsize=12, color="#0b0b0b")
    ax.axvline(0, color=INK, linewidth=0.8)
    ax.tick_params(colors=INK, labelsize=9, length=0)
    ax.grid(axis="x", color="#e6e5e0", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    return fig


def to_png_bytes(fig: Figure) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    return buf.getvalue()


def save_all(df: pd.DataFrame, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for metric in METRICS:
        path = out_dir / f"{metric}_chart.png"
        path.write_bytes(to_png_bytes(bar_chart(df, metric)))
        paths.append(path)
    return paths
