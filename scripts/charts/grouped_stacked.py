"""Stacked-grouped bar chart builder (stacked-grouped-chart skill implementation).

Builds stacked bar charts for contaminant families:
  - x-axis: boreholes (stations)
  - y-axis: concentration (absolute or % of total)
  - stacked bars: one segment per compound, colored by group/family

Rules (from stacked-grouped-chart skill):
  1. One row per station — merge if split across multiple rows
  2. Column order = stacking order (group 1 bottom, group 2 middle)
  3. NaN → 0
  4. TPFAS always excluded
  5. Two parallel charts for dual_chart presets (absolute + 100% stacked)
  6. Hebrew labels require arabic_reshaper + bidi for correct RTL display
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np


def _fix_hebrew(text: str) -> str:
    """Apply RTL/reshaping to Hebrew text for matplotlib display."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except ImportError:
        return text


def build_grouped_stacked(
    df_dict: dict[str, dict[str, float]],  # {borehole_name: {compound_code: concentration}}
    preset: dict,
    output_path: Path,
    mode: str = "absolute",   # "absolute" | "percent_100"
    figsize: tuple = (12, 5),
    dpi: int = 150,
) -> Path:
    """
    Build and save a stacked bar chart.

    df_dict: rows = boreholes, columns = compound codes
    preset:  entry from chart_presets.json
    mode:    "absolute" or "percent_100"
    Returns path of saved PNG.
    """
    # ── Determine compound list and colors ────────────────────────────────────
    if "groups" in preset:
        # PFAS-style: two groups stacked in order (S bottom, A top)
        all_codes: list[str] = []
        all_colors: list[str] = []
        for group_name, group_data in preset["groups"].items():
            codes = group_data["codes"]
            colors = group_data["colors"]
            for code, color in zip(codes, colors):
                all_codes.append(code)
                all_colors.append(color)
    else:
        all_codes = preset.get("codes", [])
        all_colors = preset.get("colors", [])
        # Pad/trim colors to match codes
        if len(all_colors) < len(all_codes):
            all_colors = all_colors + ["#999999"] * (len(all_codes) - len(all_colors))
        all_colors = all_colors[:len(all_codes)]

    display_names: dict[str, str] = preset.get("display_names", {})

    # ── Build matrix: rows=boreholes, columns=compounds ──────────────────────
    boreholes = list(df_dict.keys())
    # Filter to compounds that are in the data
    present_codes = [c for c in all_codes if any(df_dict[bh].get(c, 0) > 0 for bh in boreholes)]
    if not present_codes:
        return output_path  # nothing to plot

    present_colors = [all_colors[all_codes.index(c)] for c in present_codes]
    matrix = np.zeros((len(boreholes), len(present_codes)))
    for i, bh in enumerate(boreholes):
        for j, code in enumerate(present_codes):
            matrix[i, j] = df_dict[bh].get(code, 0.0)

    # NaN → 0
    matrix = np.nan_to_num(matrix, nan=0.0)

    # ── 100% normalization ───────────────────────────────────────────────────
    if mode == "percent_100":
        row_sums = matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # avoid divide by zero
        matrix = (matrix / row_sums) * 100

    # ── Plot ──────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(boreholes))
    bottoms = np.zeros(len(boreholes))

    for j, (code, color) in enumerate(zip(present_codes, present_colors)):
        vals = matrix[:, j]
        label = display_names.get(code, code)
        ax.bar(x, vals, bottom=bottoms, color=color, label=label,
               edgecolor="white", linewidth=0.3, width=0.6)
        bottoms += vals

    # Labels and formatting
    title_key = "title_pct_template" if mode == "percent_100" else "title_template"
    title = preset.get(title_key, preset.get("title_template", ""))
    ax.set_title(_fix_hebrew(title), fontsize=11)

    unit = preset.get("unit", "")
    ylabel = "%" if mode == "percent_100" else _fix_hebrew(unit)
    ax.set_ylabel(ylabel)

    # Hebrew borehole names on x-axis
    ax.set_xticks(x)
    ax.set_xticklabels(
        [_fix_hebrew(bh) for bh in boreholes],
        rotation=30, ha="right", fontsize=8
    )

    ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
    ax.tick_params(axis="y", labelsize=8)

    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7,
              frameon=True, framealpha=0.9)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(output_path), dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return output_path
