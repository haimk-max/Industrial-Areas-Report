"""Generate V2 charts for Industrial Areas Report — Raanana zone.

Charts produced:
  1. cvoc_timeseries.png         — TCE (nt_1, nt_2) + PCE (nt_3) time-series 2012-2025
  2. pfas_stacked_turbine.png    — PFAS species at nd_turbine, S/A groups, absolute + % of standard
  3. btex_timeseries_paz.png     — Benzene at nd_paz 2011-2024
  4. cvoc_cross_borehole.png     — Max annual TCE/PCE across boreholes comparison

Usage:
  python scripts/generate_charts_v2.py [--zone raanana] [--output Raanana/charts_v2]
"""

import argparse
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np

# ── Palette (from chart_presets.json) ────────────────────────────────────────
PFAS_S_COLORS = {
    "PFHxS": "#0D47A1",
    "PFBS":  "#1565C0",
    "PFOS":  "#1976D2",
    "PFHpS": "#1E88E5",
    "PFDS":  "#42A5F5",
}
PFAS_A_COLORS = {
    "PFOA":  "#BF360C",
    "PFHxA": "#D84315",
    "PFPeA": "#E64A19",
    "PFBA":  "#F4511E",
    "PFHpA": "#FF5722",
    "PFNA":  "#FF7043",
    "PFDA":  "#FF8A65",
    "PFDoA": "#FFAB91",
    "PFUnA": "#FFCCBC",
}

DWS = {  # drinking water standards (µg/L)
    "TCE": 7.5, "PCE": 10.0, "BENZENE": 5.0,
    "PFHxS": 0.1, "PFOA": 0.1, "PFHxA": 0.1, "PFPeA": 0.1,
    "PFBA": 0.1, "PFHpA": 0.1, "PFBS": 0.1, "PFOS": 0.1,
}

# param_code → display name
PARAM_NAMES = {
    "TCEY": "TCE", "TECE": "PCE", "CDCE": "cis-1,2-DCE",
    "BENZ": "Benzene", "TOLU": "Toluene",
    "PFHxS": "PFHxS", "PFOA": "PFOA", "PFHxA": "PFHxA",
    "PFPeA": "PFPeA", "PFBA": "PFBA", "PFHpA": "PFHpA",
    "PFBS": "PFBS", "PFOS": "PFOS",
}

PFAS_LOD = 0.010  # detection limit for PFAS in this dataset


def load_measurements(zone_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(zone_dir / "data" / "measurements.csv", parse_dates=["date"])
    return df


# ── Chart 1: CVOC Time-Series ─────────────────────────────────────────────────
def chart_cvoc_timeseries(df: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=False)

    # Left: TCE at nt_1 and nt_2
    ax = axes[0]
    for bh_id, label, color, marker in [
        ("raanana_nt_1", "נת רעננה 1 (TCE)", "#D32F2F", "o"),
        ("raanana_nt_2", "נת רעננה 2 (TCE)", "#FF8F00", "s"),
    ]:
        sub = df[(df.canonical_id == bh_id) & (df.param_code == "TCEY")].sort_values("date")
        ax.plot(sub["date"], sub["concentration"], marker=marker, color=color,
                linewidth=1.5, markersize=6, label=label)
        ax.fill_between(sub["date"], 0, sub["concentration"], alpha=0.08, color=color)

    ax.axhline(7.5, color="#555", linestyle="--", linewidth=0.9, label="תקן TCE = 7.5 µg/L")
    ax.set_title("TCE — נת רעננה 1 ו-2 (2012–2025)", fontsize=11, fontweight="bold")
    ax.set_ylabel("ריכוז (µg/L)", fontsize=10)
    ax.set_xlabel("שנה", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)

    # Right: PCE + TCE at nt_3 (decay chain)
    ax = axes[1]
    for param, label, color, marker in [
        ("TECE", "PCE (נת רעננה 3)", "#1565C0", "o"),
        ("TCEY", "TCE (נת רעננה 3)", "#6A1B9A", "^"),
        ("CDCE", "cis-1,2-DCE (נת רעננה 3)", "#2E7D32", "D"),
    ]:
        sub = df[(df.canonical_id == "raanana_nt_3") & (df.param_code == param)].sort_values("date")
        if sub.empty or sub["concentration"].max() == 0:
            continue
        ax.plot(sub["date"], sub["concentration"], marker=marker, color=color,
                linewidth=1.5, markersize=6, label=label)
        ax.fill_between(sub["date"], 0, sub["concentration"], alpha=0.08, color=color)

    ax.axhline(10.0, color="#1565C0", linestyle="--", linewidth=0.9, alpha=0.7, label="תקן PCE = 10 µg/L")
    ax.axhline(7.5, color="#6A1B9A", linestyle=":", linewidth=0.9, alpha=0.7, label="תקן TCE = 7.5 µg/L")
    ax.set_title("PCE→TCE ריקבון — נת רעננה 3 (2012–2025)", fontsize=11, fontweight="bold")
    ax.set_ylabel("ריכוז (µg/L)", fontsize=10)
    ax.set_xlabel("שנה", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)

    fig.suptitle("CVOC — מסלול ריקבון כלוריני | קריית אתגרים, רעננה", fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    fig.savefig(out / "cvoc_timeseries.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: cvoc_timeseries.png")


# ── Chart 2: PFAS Stacked Bar + % of Standard ────────────────────────────────
def chart_pfas_turbine(df: pd.DataFrame, out: Path) -> None:
    turbine = df[df.canonical_id == "raanana_nd_turbine"].copy()

    # S-group species
    s_codes = {
        "PFHxS": "PFHxS", "PFBS": "PFBS", "PFOS": "PFOS",
        "PFHpS": "PFHpS", "PFDS": "PFDS",
    }
    # A-group species
    a_codes = {
        "PFOA": "PFOA", "PFHxA": "PFHxA", "PFPeA": "PFPeA",
        "PFBA": "PFBA", "PFHpA": "PFHpA", "PFNA": "PFNA",
        "PFDA": "PFDA", "PFDoA": "PFDoA", "PFUnA": "PFUnA",
    }

    latest = turbine[turbine.date == turbine.date.max()]

    def get_conc(code):
        row = latest[latest.param_code == code]
        if row.empty:
            return 0.0
        return float(row["concentration"].values[0])

    s_data = {name: get_conc(code) for code, name in s_codes.items()}
    a_data = {name: get_conc(code) for code, name in a_codes.items()}

    # Filter out at-LOD values for clarity (keep only > LOD)
    s_detected = {k: v for k, v in s_data.items() if v > PFAS_LOD}
    a_detected = {k: v for k, v in a_data.items() if v > PFAS_LOD}

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Absolute concentrations stacked bar
    ax = axes[0]
    species_order = list(s_detected.keys()) + list(a_detected.keys())
    values = [s_detected.get(s, 0) for s in s_detected] + [a_detected.get(s, 0) for s in a_detected]
    colors = [PFAS_S_COLORS.get(s, "#90CAF9") for s in s_detected] + \
             [PFAS_A_COLORS.get(s, "#FFCCBC") for s in a_detected]

    bars = ax.bar(["נד תחנת טורבינות גז\n30.07.2025"],
                  [sum(values)], color="white", edgecolor="none")  # invisible base

    bottom = 0
    bar_patches = []
    for name, val, color in zip(species_order, values, colors):
        b = ax.bar(["נד תחנת טורבינות גז\n30.07.2025"], [val], bottom=bottom,
                   color=color, edgecolor="white", linewidth=0.5)
        bar_patches.append(mpatches.Patch(color=color, label=f"{name}: {val:.3f} µg/L"))
        bottom += val

    ax.axhline(0.1, color="#E53935", linestyle="--", linewidth=1.2, label="תקן = 0.1 µg/L לכל מין")
    ax.set_ylabel("ריכוז (µg/L)", fontsize=10)
    ax.set_title("PFAS — ריכוז מוחלט\n(S-group = כחול, A-group = כתום)", fontsize=10, fontweight="bold")
    ax.legend(handles=bar_patches + [mpatches.Patch(color="#E53935", label="תקן 0.1 µg/L")],
              fontsize=7.5, bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, max(sum(values) * 1.15, 0.3))

    # Right: % of standard (individual bars per species)
    ax = axes[1]
    all_detected = list(s_detected.items()) + list(a_detected.items())
    names_r = [n for n, _ in all_detected]
    pcts = [v / 0.1 * 100 for _, v in all_detected]
    colors_r = [PFAS_S_COLORS.get(n, "#90CAF9") for n in s_detected] + \
               [PFAS_A_COLORS.get(n, "#FFCCBC") for n in a_detected]

    x = range(len(names_r))
    bars_r = ax.bar(x, pcts, color=colors_r, edgecolor="white", linewidth=0.5)
    ax.axhline(100, color="#E53935", linestyle="--", linewidth=1.2, label="100% מהתקן")
    ax.set_xticks(list(x))
    ax.set_xticklabels(names_r, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("% מהתקן (0.1 µg/L)", fontsize=10)
    ax.set_title("PFAS — אחוז מתקן מי שתייה\n(תקן = 0.1 µg/L לכל מין)", fontsize=10, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    for bar_r, pct in zip(bars_r, pcts):
        if pct > 50:
            ax.text(bar_r.get_x() + bar_r.get_width() / 2, bar_r.get_height() + 20,
                    f"{pct:.0f}%", ha="center", va="bottom", fontsize=8, fontweight="bold")

    # S/A group boundary annotation
    if s_detected and a_detected:
        boundary = len(s_detected) - 0.5
        ax.axvline(boundary, color="#9E9E9E", linestyle=":", linewidth=1)
        ax.text(boundary - 0.3, ax.get_ylim()[1] * 0.92, "S-group", ha="right",
                fontsize=8, color="#0D47A1", fontstyle="italic")
        ax.text(boundary + 0.3, ax.get_ylim()[1] * 0.92, "A-group", ha="left",
                fontsize=8, color="#BF360C", fontstyle="italic")

    fig.suptitle("PFAS — תחנת טורבינות גז רעננה (IEC) | דיגום ראשוני 30.07.2025",
                 fontsize=12, fontweight="bold", y=1.01)
    plt.tight_layout()
    fig.savefig(out / "pfas_stacked_turbine.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: pfas_stacked_turbine.png")


# ── Chart 3: Benzene Time-Series at Paz ──────────────────────────────────────
def chart_btex_timeseries(df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))

    paz = df[df.canonical_id == "raanana_nd_paz_hanofer"].copy()

    for param, label, color, marker, lw in [
        ("BENZ",  "בנזן",    "#D32F2F", "o", 2.0),
        ("TOLU",  "טולואן",  "#F57C00", "s", 1.5),
        ("MTBE",  "MTBE",    "#7B1FA2", "^", 1.5),
    ]:
        sub = paz[paz.param_code == param].sort_values("date")
        if sub.empty or sub["concentration"].max() == 0:
            continue
        ax.plot(sub["date"], sub["concentration"], marker=marker, color=color,
                linewidth=lw, markersize=7, label=label, zorder=3)
        ax.fill_between(sub["date"], 0, sub["concentration"], alpha=0.1, color=color)

    ax.axhline(5.0, color="#D32F2F", linestyle="--", linewidth=1.0, alpha=0.8, label="תקן בנזן = 5 µg/L")

    # Annotate peak
    peak = paz[(paz.param_code == "BENZ") & (paz["concentration"] == paz[paz.param_code == "BENZ"]["concentration"].max())]
    if not peak.empty:
        ax.annotate(f"שיא: {peak['concentration'].values[0]:.1f} µg/L\n(200% מהתקן)",
                    xy=(peak["date"].values[0], peak["concentration"].values[0]),
                    xytext=(0, 15), textcoords="offset points",
                    fontsize=8.5, ha="center", color="#B71C1C",
                    arrowprops=dict(arrowstyle="->", color="#B71C1C", lw=0.8))

    ax.set_title("BTEX — נד פז הנופר (2011–2024) | תחנת דלק פז הנופר", fontsize=12, fontweight="bold")
    ax.set_ylabel("ריכוז (µg/L)", fontsize=10)
    ax.set_xlabel("שנה", fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    fig.savefig(out / "btex_timeseries_paz.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: btex_timeseries_paz.png")


# ── Chart 4: Cross-Borehole CVOC Comparison ──────────────────────────────────
def chart_cvoc_cross_borehole(df: pd.DataFrame, out: Path) -> None:
    """Bar chart: peak TCE and PCE per borehole across all time."""
    boreholes = ["raanana_nt_1", "raanana_nt_2", "raanana_nt_3", "raanana_p_25"]
    labels = ["נת רעננה 1", "נת רעננה 2", "נת רעננה 3", "פ רעננה 25"]

    tce_peaks = []
    pce_peaks = []
    for bh in boreholes:
        sub_tce = df[(df.canonical_id == bh) & (df.param_code == "TCEY")]["concentration"]
        sub_pce = df[(df.canonical_id == bh) & (df.param_code == "TECE")]["concentration"]
        tce_peaks.append(sub_tce.max() if not sub_tce.empty else 0)
        pce_peaks.append(sub_pce.max() if not sub_pce.empty else 0)

    x = np.arange(len(labels))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width / 2, tce_peaks, width, label="TCE (שיא)", color="#D32F2F", alpha=0.85, edgecolor="white")
    bars2 = ax.bar(x + width / 2, pce_peaks, width, label="PCE (שיא)", color="#1565C0", alpha=0.85, edgecolor="white")

    ax.axhline(7.5, color="#D32F2F", linestyle="--", linewidth=1.0, alpha=0.7, label="תקן TCE = 7.5 µg/L")
    ax.axhline(10.0, color="#1565C0", linestyle="--", linewidth=1.0, alpha=0.7, label="תקן PCE = 10.0 µg/L")

    for bar in bars1:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 5, f"{h:.0f}", ha="center",
                    va="bottom", fontsize=8.5, color="#B71C1C", fontweight="bold")
    for bar in bars2:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 5, f"{h:.0f}", ha="center",
                    va="bottom", fontsize=8.5, color="#0D47A1", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("ריכוז שיא (µg/L)", fontsize=10)
    ax.set_title("CVOC — ריכוז שיא לקידוח | קריית אתגרים, רעננה 2012–2025", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    fig.savefig(out / "cvoc_cross_borehole.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: cvoc_cross_borehole.png")


# ── Chart 5: TCE at p_25 (production well, exceedance detail) ────────────────
def chart_tce_p25(df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))

    sub = df[(df.canonical_id == "raanana_p_25") & (df.param_code == "TCEY")].sort_values("date")

    # Shade pre-2020 vs 2020+
    ax.axvspan(sub["date"].min(), pd.Timestamp("2020-01-01"), alpha=0.05, color="#9E9E9E", label="טרום 2020")
    ax.axvspan(pd.Timestamp("2020-01-01"), sub["date"].max(), alpha=0.06, color="#EF9A9A", label="חלון 5 שנים (2020+)")

    ax.plot(sub["date"], sub["concentration"], marker="o", color="#C62828",
            linewidth=2.0, markersize=7, zorder=3)
    ax.fill_between(sub["date"], 0, sub["concentration"], alpha=0.15, color="#C62828")

    ax.axhline(7.5, color="#E53935", linestyle="--", linewidth=1.2, label="תקן TCE = 7.5 µg/L")

    ax.set_title("TCE בקידוח ייצור — פ רעננה 25 (2019–2025)\nחריגה מתמשכת מתקן מי שתיה",
                 fontsize=12, fontweight="bold")
    ax.set_ylabel("ריכוז TCE (µg/L)", fontsize=10)
    ax.set_xlabel("תאריך", fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    fig.savefig(out / "tce_timeseries_p25.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: tce_timeseries_p25.png")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate V2 charts for a zone")
    parser.add_argument("--zone", default="raanana")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    zone_dir = Path(args.zone.capitalize())
    if not zone_dir.exists():
        zone_dir = Path(args.zone)
    if not zone_dir.exists():
        sys.exit(f"Zone directory not found: {args.zone}")

    out = Path(args.output) if args.output else zone_dir / "charts_v2"
    out.mkdir(parents=True, exist_ok=True)

    df = load_measurements(zone_dir)
    print(f"[V2 Charts] Loaded {len(df)} measurements from {zone_dir}")

    chart_cvoc_timeseries(df, out)
    chart_pfas_turbine(df, out)
    chart_btex_timeseries(df, out)
    chart_cvoc_cross_borehole(df, out)
    chart_tce_p25(df, out)

    print(f"[V2 Charts] Done — 5 charts saved to {out}/")


if __name__ == "__main__":
    main()
