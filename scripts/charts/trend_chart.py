"""Trend chart: time series for one (borehole, parameter) pair with MK classification.

Shows:
  - Bar chart of measurements over time (colored by year group)
  - Horizontal line at drinking water standard (if available)
  - Trend annotation (ALERT / WATCH / STABLE / DECREASING / NONE)
  - Below-LOD markers (triangles at LOD/2)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np


def _fix_hebrew(text: str) -> str:
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except ImportError:
        return text


CLASSIFICATION_COLORS = {
    "ALERT":      "#C62828",
    "WATCH":      "#FF6F00",
    "STABLE":     "#1565C0",
    "DECREASING": "#2E7D32",
    "NONE":       "#757575",
}


def build_trend_chart(
    dates: list,          # list of datetime.date or str
    concentrations: list[float | None],
    is_below_lod: list[bool],
    borehole_name: str,
    parameter_code: str,
    parameter_name: str,
    classification: str,
    unit: str,
    drinking_water_standard: float | None,
    output_path: Path,
    figsize: tuple = (10, 4),
    dpi: int = 150,
) -> Path:
    from datetime import date as datecls
    from datetime import datetime

    # Convert dates to floats (years with decimal)
    def to_float_year(d) -> float:
        if isinstance(d, str):
            d = datecls.fromisoformat(d[:10])
        if hasattr(d, "timetuple"):
            import time
            tt = d.timetuple()
            return tt.tm_year + (tt.tm_yday - 1) / 365.25
        return float(d)

    float_years = [to_float_year(d) for d in dates]

    # Split detected vs below-LOD
    detected_x, detected_y = [], []
    lod_x, lod_y = [], []
    for fy, conc, blod in zip(float_years, concentrations, is_below_lod):
        if conc is None:
            continue
        if blod:
            lod_x.append(fy)
            lod_y.append(conc)
        else:
            detected_x.append(fy)
            detected_y.append(conc)

    fig, ax = plt.subplots(figsize=figsize)
    cls_color = CLASSIFICATION_COLORS.get(classification, "#757575")

    # Detected values as vertical lines + markers
    if detected_x:
        ax.vlines(detected_x, 0, detected_y, color=cls_color, alpha=0.6, linewidth=4)
        ax.plot(detected_x, detected_y, "o", color=cls_color, markersize=5, label="Detected")

    # Below-LOD as triangles pointing down
    if lod_x:
        ax.plot(lod_x, lod_y, "v", color="#9E9E9E", markersize=5,
                alpha=0.5, label="Below LOD")

    # Drinking water standard
    if drinking_water_standard and drinking_water_standard > 0:
        ax.axhline(y=drinking_water_standard, color="#E53935", linestyle="--",
                   linewidth=1.2, label=f"Standard ({drinking_water_standard} {unit})")

    # Window 2020 marker
    ax.axvline(x=2020, color="#BDBDBD", linestyle=":", linewidth=0.8, alpha=0.7)
    ax.text(2020.1, ax.get_ylim()[1] * 0.95, "5y window", fontsize=6, color="#9E9E9E")

    # Classification annotation
    ann_text = f"  {classification}"
    ax.text(0.02, 0.95, ann_text, transform=ax.transAxes, fontsize=9,
            color=cls_color, fontweight="bold", va="top")

    borehole_display = _fix_hebrew(borehole_name)
    title = f"{borehole_display} — {parameter_code} ({parameter_name})"
    ax.set_title(title, fontsize=10)
    ax.set_ylabel(unit, fontsize=9)
    ax.set_xlabel("Year", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=7, loc="upper right")

    if detected_y or lod_y:
        all_vals = [v for v in detected_y + lod_y if v is not None]
        if all_vals:
            ymax = max(all_vals) * 1.15
            ax.set_ylim(0, ymax)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(output_path), dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return output_path
