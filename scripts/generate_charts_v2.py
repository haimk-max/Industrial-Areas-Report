"""Generate V2 charts for Industrial Areas Report — Raanana zone.

Charts produced:
  1. cvoc_timeseries.png          — TCE (nt_1, nt_2) + PCE (nt_3) time-series 2012-2025
  2. pfas_all_boreholes.png       — PFAS: stacked bar per borehole (S/A groups) + time-series
  3. btex_timeseries_paz.png      — Benzene at nd_paz 2011-2024
  4. cvoc_cross_borehole.png      — Max annual TCE/PCE across boreholes comparison
  5. tce_timeseries_p25.png       — TCE at p25 production well (exceedance detail)
  6. cvoc_all_wells.png           — CVOC curves for all boreholes (TCE + PCE panels)
  7. pfas_pct_stacked.png         — 100%-stacked PFAS for AFFF source-signature (S/A grouping)
  8. btex_family_stacked.png      — BTEX full family time-series at Paz Hanofer
  9. cvoc_pct_standard_panel.png  — 4-borehole panel: % of standard TCE/PCE over time

Usage:
  python scripts/generate_charts_v2.py [--zone raanana] [--output Raanana/charts_v2]
"""

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np


# ── Hebrew RTL helper ─────────────────────────────────────────────────────────
def _fix_hebrew(text: str) -> str:
    """Apply BiDi + reshaping so Hebrew renders RTL in matplotlib."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except ImportError:
        return text

H = _fix_hebrew   # shorthand used throughout


# ── Palette — S group: blue (dark→light), A group: orange/warm (dark→light) ───
# S at bottom of stack, A on top (per pfas-sa-chart skill)
PFAS_S_ORDER  = ["PFHxS", "PFBS", "PFOS", "PFHpS", "PFDS"]
PFAS_A_ORDER  = ["PFOA", "PFHxA", "PFHpA", "PFNA", "PFDA", "PFDoA", "PFBA", "PFPeA", "PFUnA"]
PFAS_S_COLORS = {
    "PFHxS": "#0D47A1",
    "PFBS":  "#1565C0",
    "PFOS":  "#1976D2",
    "PFHpS": "#42A5F5",
    "PFDS":  "#90CAF9",
}
PFAS_A_COLORS = {
    "PFOA":  "#BF360C",
    "PFHxA": "#D84315",
    "PFHpA": "#E64A19",
    "PFNA":  "#F4511E",
    "PFDA":  "#FF7043",
    "PFDoA": "#FF8A65",
    "PFBA":  "#FFAB76",
    "PFPeA": "#FFA726",
    "PFUnA": "#FFF3E0",
}
PFAS_ALL_COLORS = {**PFAS_S_COLORS, **PFAS_A_COLORS}
PFAS_ALL_ORDER  = PFAS_S_ORDER + PFAS_A_ORDER

DWS = {  # drinking water standards (µg/L)
    "TCE": 7.5, "PCE": 10.0, "BENZENE": 5.0,
    "PFHxS": 0.1, "PFOA": 0.1, "PFHxA": 0.1, "PFPeA": 0.1,
    "PFBA": 0.1, "PFHpA": 0.1, "PFBS": 0.1, "PFOS": 0.1,
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
        ("raanana_nt_1", H("נת רעננה 1 (TCE)"), "#D32F2F", "o"),
        ("raanana_nt_2", H("נת רעננה 2 (TCE)"), "#FF8F00", "s"),
    ]:
        sub = df[(df.canonical_id == bh_id) & (df.param_code == "TCEY")].sort_values("date")
        ax.plot(sub["date"], sub["concentration"], marker=marker, color=color,
                linewidth=1.5, markersize=6, label=label)
        ax.fill_between(sub["date"], 0, sub["concentration"], alpha=0.08, color=color)

    ax.axhline(7.5, color="#555", linestyle="--", linewidth=0.9,
               label=H("תקן TCE = 7.5 µg/L"))
    ax.set_title(H("TCE — נת רעננה 1 ו-2 (2012–2025)"), fontsize=11, fontweight="bold")
    ax.set_ylabel(H("ריכוז (µg/L)"), fontsize=10)
    ax.set_xlabel(H("שנה"), fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)

    # Right: PCE + TCE at nt_3 (decay chain)
    ax = axes[1]
    for param, label, color, marker in [
        ("TECE", H("PCE (נת רעננה 3)"), "#1565C0", "o"),
        ("TCEY", H("TCE (נת רעננה 3)"), "#6A1B9A", "^"),
        ("CDCE", H("cis-1,2-DCE (נת רעננה 3)"), "#2E7D32", "D"),
    ]:
        sub = df[(df.canonical_id == "raanana_nt_3") & (df.param_code == param)].sort_values("date")
        if sub.empty or sub["concentration"].max() == 0:
            continue
        ax.plot(sub["date"], sub["concentration"], marker=marker, color=color,
                linewidth=1.5, markersize=6, label=label)
        ax.fill_between(sub["date"], 0, sub["concentration"], alpha=0.08, color=color)

    ax.axhline(10.0, color="#1565C0", linestyle="--", linewidth=0.9, alpha=0.7,
               label=H("תקן PCE = 10 µg/L"))
    ax.axhline(7.5, color="#6A1B9A", linestyle=":", linewidth=0.9, alpha=0.7,
               label=H("תקן TCE = 7.5 µg/L"))
    ax.set_title(H("PCE→TCE פירוק — נת רעננה 3 (2012–2025)"), fontsize=11, fontweight="bold")
    ax.set_ylabel(H("ריכוז (µg/L)"), fontsize=10)
    ax.set_xlabel(H("שנה"), fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)

    fig.suptitle(H("CVOC — שרשרת פירוק כלוריני | קריית אתגרים, רעננה"),
                 fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    fig.savefig(out / "cvoc_timeseries.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: cvoc_timeseries.png")


# ── Chart 2: PFAS — all boreholes, one stacked bar per borehole ──────────────
def chart_pfas_all_boreholes(df: pd.DataFrame, out: Path) -> None:
    """One stacked bar per borehole (S-group at bottom, A-group on top).
    Absolute + 100%-stacked panels. Time-series for boreholes with >1 date.
    """
    BH_LABELS = {
        "raanana_nd_turbine": H("נד תחנת\nטורבינות גז"),
        "raanana_p_25":       H("פ רעננה 25"),
        "raanana_nt_1":       H("נת רעננה 1"),
        "raanana_nt_2":       H("נת רעננה 2"),
        "raanana_nt_3":       H("נת רעננה 3"),
    }

    pfas_df = df[df.param_code.isin(PFAS_ALL_ORDER)].copy()
    if pfas_df.empty:
        return

    # Latest reading per borehole
    def latest_vals(bh_id: str) -> dict:
        sub = pfas_df[pfas_df.canonical_id == bh_id]
        if sub.empty:
            return {}
        ld = sub["date"].max()
        latest = sub[sub.date == ld]
        return {code: float(r["concentration"].values[0])
                for code in PFAS_ALL_ORDER
                for r in [latest[latest.param_code == code]]
                if not r.empty}

    tested_bh = list(pfas_df["canonical_id"].unique())
    bh_data = {bh: latest_vals(bh) for bh in tested_bh}

    # Order: nd_turbine first, rest alphabetically
    preferred = ["raanana_nd_turbine", "raanana_p_25"]
    bh_show = preferred + [b for b in sorted(tested_bh) if b not in preferred]
    bh_show = [b for b in bh_show if b in tested_bh]

    # Boreholes with >1 PFAS sampling date
    multi_bh = [b for b in bh_show
                if pfas_df[pfas_df.canonical_id == b]["date"].nunique() > 1]
    has_ts = bool(multi_bh)

    n_rows = 2 if has_ts else 1
    fig = plt.figure(figsize=(14, 6 * n_rows))
    ax_abs = fig.add_subplot(n_rows, 2, 1)
    ax_pct = fig.add_subplot(n_rows, 2, 2)

    x = np.arange(len(bh_show))
    xlabels = [BH_LABELS.get(b, b) for b in bh_show]

    # ── Absolute stacked bar ─────────────────────────────────────────────────
    bottom_abs = np.zeros(len(bh_show))
    legend_patches = []
    for code in PFAS_ALL_ORDER:
        vals = np.array([bh_data.get(b, {}).get(code, 0.0) for b in bh_show])
        color = PFAS_ALL_COLORS[code]
        ax_abs.bar(x, vals, bottom=bottom_abs, color=color,
                   edgecolor="white", linewidth=0.5)
        if vals.max() > PFAS_LOD:
            legend_patches.append(mpatches.Patch(color=color, label=code))
        bottom_abs += vals

    ax_abs.axhline(0.1, color="#E53935", linestyle="--", linewidth=1.2)
    legend_patches.append(
        plt.Line2D([0], [0], color="#E53935", linestyle="--",
                   linewidth=1.2, label=H("תקן = 0.1 µg/L")))
    ax_abs.set_xticks(x)
    ax_abs.set_xticklabels(xlabels, fontsize=9)
    ax_abs.set_ylabel(H("ריכוז (µg/L)"), fontsize=10)
    ax_abs.set_title(H("PFAS — ריכוז מוחלט לפי קידוח\n(S-group=כחול | A-group=כתום)"),
                     fontsize=10, fontweight="bold")
    ax_abs.legend(handles=legend_patches, fontsize=7.5,
                  bbox_to_anchor=(1.02, 1), loc="upper left")
    ax_abs.grid(axis="y", alpha=0.3)
    ax_abs.set_ylim(bottom=0)

    # ── 100%-stacked bar ─────────────────────────────────────────────────────
    totals = np.array([sum(bh_data.get(b, {}).values()) for b in bh_show])
    bottom_pct = np.zeros(len(bh_show))
    for code in PFAS_ALL_ORDER:
        vals = np.array([bh_data.get(b, {}).get(code, 0.0) for b in bh_show])
        pcts = np.where(totals > 0, vals / totals * 100, 0.0)
        ax_pct.bar(x, pcts, bottom=bottom_pct, color=PFAS_ALL_COLORS[code],
                   edgecolor="white", linewidth=0.5)
        bottom_pct += pcts

    # S/A boundary line
    s_totals = np.array([sum(bh_data.get(b, {}).get(c, 0.0) for c in PFAS_S_ORDER)
                         for b in bh_show])
    s_pcts = np.where(totals > 0, s_totals / totals * 100, 0.0)
    for xi, sp in enumerate(s_pcts):
        if totals[xi] > 0:
            ax_pct.plot([xi - 0.4, xi + 0.4], [sp, sp],
                        color="#FFD600", linewidth=2, linestyle="--", zorder=5)

    ax_pct.set_xticks(x)
    ax_pct.set_xticklabels(xlabels, fontsize=9)
    ax_pct.set_ylabel(H("% מסך PFAS"), fontsize=10)
    ax_pct.set_title(H("PFAS — הרכב יחסי לפי קידוח\n(קו צהוב = גבול S/A)"),
                     fontsize=10, fontweight="bold")
    ax_pct.set_ylim(0, 100)
    ax_pct.grid(axis="y", alpha=0.3)

    # ── Time-series for multi-measurement boreholes ──────────────────────────
    if has_ts:
        ax_ts_s = fig.add_subplot(n_rows, 2, 3)
        ax_ts_a = fig.add_subplot(n_rows, 2, 4)
        ts_colors = ["#1976D2", "#D32F2F", "#2E7D32", "#7B1FA2"]
        for bh, bh_color in zip(multi_bh, ts_colors):
            label = BH_LABELS.get(bh, bh)
            for code, ax_ts, ls in [
                ("PFHxS", ax_ts_s, "-"),  ("PFBS", ax_ts_s, "--"),
                ("PFOA",  ax_ts_a, "-"),  ("PFHxA", ax_ts_a, "--"),
                ("PFPeA", ax_ts_a, ":"),
            ]:
                sub = pfas_df[(pfas_df.canonical_id == bh) &
                              (pfas_df.param_code == code)].sort_values("date")
                if sub.empty:
                    continue
                ax_ts.plot(sub["date"], sub["concentration"], marker="o",
                           color=PFAS_ALL_COLORS[code], linestyle=ls,
                           linewidth=1.5, markersize=6,
                           label=f"{label} — {code}")

        for ax_ts, title in [
            (ax_ts_s, H("S-group (סולפונטים) — ריכוז לאורך זמן")),
            (ax_ts_a, H("A-group (קרבוקסילטים) — ריכוז לאורך זמן")),
        ]:
            ax_ts.axhline(0.1, color="#E53935", linestyle="--", linewidth=1.2,
                          label=H("תקן = 0.1 µg/L"))
            ax_ts.set_ylabel(H("ריכוז (µg/L)"), fontsize=9)
            ax_ts.set_title(title, fontsize=10, fontweight="bold")
            ax_ts.legend(fontsize=8)
            ax_ts.grid(axis="y", alpha=0.3)
            ax_ts.set_ylim(bottom=0)

    fig.suptitle(H("PFAS — ממצאים לפי קידוח | אזה\"ת רעננה"),
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    fig.savefig(out / "pfas_all_boreholes.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: pfas_all_boreholes.png")


# ── Chart 3: Benzene Time-Series at Paz ──────────────────────────────────────
def chart_btex_timeseries(df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))

    paz = df[df.canonical_id == "raanana_nd_paz_hanofer"].copy()

    for param, label, color, marker, lw in [
        ("BENZ", H("בנזן"),   "#D32F2F", "o", 2.0),
        ("TOLU", H("טולואן"), "#F57C00", "s", 1.5),
        ("MTBE", "MTBE",      "#7B1FA2", "^", 1.5),
    ]:
        sub = paz[paz.param_code == param].sort_values("date")
        if sub.empty or sub["concentration"].max() == 0:
            continue
        ax.plot(sub["date"], sub["concentration"], marker=marker, color=color,
                linewidth=lw, markersize=7, label=label, zorder=3)
        ax.fill_between(sub["date"], 0, sub["concentration"], alpha=0.1, color=color)

    ax.axhline(5.0, color="#D32F2F", linestyle="--", linewidth=1.0, alpha=0.8,
               label=H("תקן בנזן = 5 µg/L"))

    peak = paz[(paz.param_code == "BENZ") & (
        paz["concentration"] == paz[paz.param_code == "BENZ"]["concentration"].max())]
    if not peak.empty:
        val = peak["concentration"].values[0]
        ax.annotate(H(f"שיא: {val:.1f} µg/L\n(200% מהתקן)"),
                    xy=(peak["date"].values[0], val),
                    xytext=(0, 15), textcoords="offset points",
                    fontsize=8.5, ha="center", color="#B71C1C",
                    arrowprops=dict(arrowstyle="->", color="#B71C1C", lw=0.8))

    ax.set_title(H("BTEX — נד פז הנופר (2011–2024) | תחנת דלק פז הנופר"),
                 fontsize=12, fontweight="bold")
    ax.set_ylabel(H("ריכוז (µg/L)"), fontsize=10)
    ax.set_xlabel(H("שנה"), fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    fig.savefig(out / "btex_timeseries_paz.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: btex_timeseries_paz.png")


# ── Chart 4: Cross-Borehole CVOC Comparison ──────────────────────────────────
def chart_cvoc_cross_borehole(df: pd.DataFrame, out: Path) -> None:
    boreholes = ["raanana_nt_1", "raanana_nt_2", "raanana_nt_3", "raanana_p_25"]
    labels = [H(l) for l in ["נת רעננה 1", "נת רעננה 2", "נת רעננה 3", "פ רעננה 25"]]

    tce_peaks, pce_peaks = [], []
    for bh in boreholes:
        sub_tce = df[(df.canonical_id == bh) & (df.param_code == "TCEY")]["concentration"]
        sub_pce = df[(df.canonical_id == bh) & (df.param_code == "TECE")]["concentration"]
        tce_peaks.append(sub_tce.max() if not sub_tce.empty else 0)
        pce_peaks.append(sub_pce.max() if not sub_pce.empty else 0)

    x = np.arange(len(labels))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width / 2, tce_peaks, width, label=H("TCE (שיא)"),
                   color="#D32F2F", alpha=0.85, edgecolor="white")
    bars2 = ax.bar(x + width / 2, pce_peaks, width, label=H("PCE (שיא)"),
                   color="#1565C0", alpha=0.85, edgecolor="white")

    ax.axhline(7.5, color="#D32F2F", linestyle="--", linewidth=1.0, alpha=0.7,
               label=H("תקן TCE = 7.5 µg/L"))
    ax.axhline(10.0, color="#1565C0", linestyle="--", linewidth=1.0, alpha=0.7,
               label=H("תקן PCE = 10.0 µg/L"))

    for bar in bars1:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 5, f"{h:.0f}",
                    ha="center", va="bottom", fontsize=8.5, color="#B71C1C", fontweight="bold")
    for bar in bars2:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 5, f"{h:.0f}",
                    ha="center", va="bottom", fontsize=8.5, color="#0D47A1", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel(H("ריכוז שיא (µg/L)"), fontsize=10)
    ax.set_title(H("CVOC — ריכוז שיא לקידוח | קריית אתגרים, רעננה 2012–2025"),
                 fontsize=12, fontweight="bold")
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

    ax.axvspan(sub["date"].min(), pd.Timestamp("2020-01-01"),
               alpha=0.05, color="#9E9E9E", label=H("טרום 2020"))
    ax.axvspan(pd.Timestamp("2020-01-01"), sub["date"].max(),
               alpha=0.06, color="#EF9A9A", label=H("חלון 5 שנים (2020+)"))

    ax.plot(sub["date"], sub["concentration"], marker="o", color="#C62828",
            linewidth=2.0, markersize=7, zorder=3)
    ax.fill_between(sub["date"], 0, sub["concentration"], alpha=0.15, color="#C62828")

    ax.axhline(7.5, color="#E53935", linestyle="--", linewidth=1.2,
               label=H("תקן TCE = 7.5 µg/L"))

    ax.set_title(H("TCE בקידוח ייצור — פ רעננה 25 (2019–2025)\nחריגה מתמשכת מתקן מי שתיה"),
                 fontsize=12, fontweight="bold")
    ax.set_ylabel(H("ריכוז TCE (µg/L)"), fontsize=10)
    ax.set_xlabel(H("תאריך"), fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    fig.savefig(out / "tce_timeseries_p25.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: tce_timeseries_p25.png")


# ── Chart 6: CVOC Multi-Well Time-Series — curves only ────────────────────────
def chart_cvoc_all_wells(df: pd.DataFrame, out: Path) -> None:
    """TCE and PCE time-series for all monitoring boreholes — curves only."""
    wells = [
        ("raanana_nt_1", H("נת רעננה 1"), "#D32F2F", "o"),
        ("raanana_nt_2", H("נת רעננה 2"), "#FF8F00", "s"),
        ("raanana_nt_3", H("נת רעננה 3"), "#6A1B9A", "^"),
        ("raanana_p_25", H("פ רעננה 25"), "#1B5E20", "D"),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=False)

    for ax, param_code, param_label, std_val, std_color in [
        (axes[0], "TCEY", "TCE", 7.5,  "#E53935"),
        (axes[1], "TECE", "PCE", 10.0, "#1565C0"),
    ]:
        for bh_id, label, color, marker in wells:
            sub = df[(df.canonical_id == bh_id) &
                     (df.param_code == param_code)].sort_values("date")
            sub = sub[sub["concentration"] > 0]
            if sub.empty:
                continue
            ax.plot(sub["date"], sub["concentration"], marker=marker, color=color,
                    linewidth=1.8, markersize=7, label=label)
            ax.fill_between(sub["date"], 0, sub["concentration"],
                            alpha=0.07, color=color)

        ax.axhline(std_val, color=std_color, linestyle="--", linewidth=1.0,
                   label=H(f"תקן {param_label} = {std_val} µg/L"))
        ax.set_title(H(f"{param_label} — ריכוז לפי קידוח (2011–2025)"),
                     fontsize=11, fontweight="bold")
        ax.set_ylabel(H("ריכוז (µg/L)"), fontsize=10)
        ax.set_xlabel(H("שנה"), fontsize=10)
        ax.legend(fontsize=8, loc="upper left")
        ax.grid(axis="y", alpha=0.3)
        ax.set_ylim(bottom=0)

    fig.suptitle(H("CVOC — ריכוז כלל קידוחי הניטור | קריית אתגרים, רעננה"),
                 fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    fig.savefig(out / "cvoc_all_wells.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: cvoc_all_wells.png")


# ── Chart 7: 100%-Stacked PFAS (AFFF source signature) ───────────────────────
def chart_pfas_pct_stacked(df: pd.DataFrame, out: Path) -> None:
    turbine = df[df.canonical_id == "raanana_nd_turbine"].copy()
    if turbine.empty:
        return

    all_pfas_codes = list(PFAS_S_COLORS.keys()) + list(PFAS_A_COLORS.keys())
    latest = turbine[turbine.date == turbine.date.max()]

    detected = {}
    for code in all_pfas_codes:
        row = latest[latest.param_code == code]
        val = float(row["concentration"].values[0]) if not row.empty else 0.0
        if val > PFAS_LOD:
            detected[code] = val

    total = sum(detected.values())
    if total == 0:
        return

    species = list(detected.keys())
    fractions = [detected[s] / total * 100 for s in species]
    colors = [PFAS_S_COLORS.get(s, PFAS_A_COLORS.get(s, "#BDBDBD")) for s in species]

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    xtick_label = H("נד תחנת טורבינות\n30.07.2025")

    # Left: 100%-stacked horizontal bar
    ax = axes[0]
    left = 0
    for s, frac, color in zip(species, fractions, colors):
        ax.barh([xtick_label], [frac], left=left, color=color,
                edgecolor="white", linewidth=0.5, label=f"{s}: {frac:.1f}%")
        if frac > 4:
            ax.text(left + frac / 2, 0, f"{s}\n{frac:.0f}%", ha="center", va="center",
                    fontsize=8, color="white" if frac > 10 else "#333", fontweight="bold")
        left += frac

    s_total_pct = sum(detected[s] / total * 100 for s in species if s in PFAS_S_COLORS)
    ax.axvline(s_total_pct, color="#FFD600", linewidth=2, linestyle="--")
    ax.text(s_total_pct / 2, 0.55, f"S-group\n{s_total_pct:.0f}%",
            ha="center", fontsize=9, color="#0D47A1", fontweight="bold")
    ax.text((s_total_pct + 100) / 2, 0.55, f"A-group\n{100 - s_total_pct:.0f}%",
            ha="center", fontsize=9, color="#BF360C", fontweight="bold")

    ax.set_xlim(0, 100)
    ax.set_xlabel(H("% מסך PFAS שנמדד"), fontsize=10)
    ax.set_title(H("חתימת מקור PFAS\n(S-group כחול / A-group כתום)"),
                 fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.25)

    # Right: absolute concentrations per species
    ax = axes[1]
    x_pos = np.arange(len(species))
    bar_colors = [PFAS_S_COLORS.get(s, PFAS_A_COLORS.get(s, "#BDBDBD")) for s in species]
    bars = ax.bar(x_pos, [detected[s] for s in species], color=bar_colors,
                  edgecolor="white", linewidth=0.5)
    ax.axhline(0.1, color="#E53935", linestyle="--", linewidth=1.2,
               label=H("תקן = 0.1 µg/L"))
    ax.set_xticks(x_pos)
    ax.set_xticklabels(species, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel(H("ריכוז (µg/L)"), fontsize=10)
    ax.set_title(H("ריכוז מוחלט לפי מין PFAS\n(vs. תקן 0.1 µg/L)"),
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.25)
    for bar, s in zip(bars, species):
        pct = detected[s] / 0.1 * 100
        if pct > 20:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.03,
                    f"{pct:.0f}%", ha="center", va="bottom", fontsize=8,
                    fontweight="bold", color="#B71C1C")

    fig.suptitle(H("PFAS — חתימת מקור AFFF | נד תחנת טורבינות גז רעננה (30.07.2025)"),
                 fontsize=12, fontweight="bold", y=1.01)
    plt.tight_layout()
    fig.savefig(out / "pfas_pct_stacked.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: pfas_pct_stacked.png")


# ── Chart 8: BTEX Full-Family Stacked at Paz ─────────────────────────────────
def chart_btex_family_stacked(df: pd.DataFrame, out: Path) -> None:
    paz = df[df.canonical_id == "raanana_nd_paz_hanofer"].copy()
    params = [
        ("BENZ", H("בנזן"),   "#D32F2F"),
        ("TOLU", H("טולואן"), "#F57C00"),
        ("MTBE", "MTBE",      "#7B1FA2"),
        ("ETBE", "ETBE",      "#00838F"),
        ("XYLE", H("קסילן"),  "#558B2F"),
    ]

    fig, ax = plt.subplots(figsize=(11, 5))

    plotted = False
    for param_code, label, color in params:
        sub = paz[paz.param_code == param_code].sort_values("date")
        if sub.empty or sub["concentration"].max() == 0:
            continue
        plotted = True
        ax.fill_between(sub["date"], 0, sub["concentration"],
                        alpha=0.45, color=color, label=label)
        ax.plot(sub["date"], sub["concentration"], color=color,
                linewidth=1.2, marker="o", markersize=5)

    if not plotted:
        ax.text(0.5, 0.5, H("אין נתוני BTEX"), transform=ax.transAxes,
                ha="center", va="center", fontsize=14)
    else:
        ax.axhline(5.0, color="#D32F2F", linestyle="--", linewidth=1.0, alpha=0.8,
                   label=H("תקן בנזן = 5 µg/L"))

    ax.set_title(H("BTEX — משפחת פחמימנים | נד פז הנופר (2011–2024)\nתחנת דלק פז הנופר, אזה\"ת רעננה"),
                 fontsize=11, fontweight="bold")
    ax.set_ylabel(H("ריכוז (µg/L)"), fontsize=10)
    ax.set_xlabel(H("שנה"), fontsize=10)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    fig.savefig(out / "btex_family_stacked.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: btex_family_stacked.png")


# ── Chart 9: 4-Borehole % of Standard Panel ───────────────────────────────────
def chart_cvoc_pct_standard_panel(df: pd.DataFrame, out: Path) -> None:
    boreholes = ["raanana_nt_1", "raanana_nt_2", "raanana_nt_3", "raanana_p_25"]
    bh_labels = [H(l) for l in ["נת רעננה 1", "נת רעננה 2", "נת רעננה 3", "פ רעננה 25"]]

    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharey=False)
    axes = axes.flatten()

    for ax, bh_id, label in zip(axes, boreholes, bh_labels):
        for param_code, param_label, dws_val, color, marker, ls in [
            ("TCEY", "TCE",        7.5,  "#D32F2F", "o", "-"),
            ("TECE", "PCE",        10.0, "#1565C0", "s", "--"),
            ("CDCE", "cis-1,2-DCE",50.0, "#2E7D32", "^", ":"),
        ]:
            sub = df[(df.canonical_id == bh_id) & (df.param_code == param_code)].sort_values("date")
            sub = sub[sub["concentration"] > 0]
            if sub.empty:
                continue
            pct = sub["concentration"] / dws_val * 100
            ax.plot(sub["date"], pct, marker=marker, color=color, linewidth=1.5,
                    markersize=5, linestyle=ls,
                    label=H(f"{param_label} (תקן {dws_val} µg/L)"))
            ax.fill_between(sub["date"], 0, pct, alpha=0.07, color=color)

        ax.axhline(100, color="#E53935", linestyle="--", linewidth=1.2, alpha=0.8,
                   label=H("100% (חריגה מתקן)"))
        ax.set_title(label, fontsize=11, fontweight="bold")
        ax.set_ylabel(H("% מהתקן"), fontsize=9)
        ax.set_xlabel(H("שנה"), fontsize=9)
        ax.legend(fontsize=7.5, loc="upper left")
        ax.grid(axis="y", alpha=0.25)
        ax.set_ylim(bottom=0)

    fig.suptitle(H("CVOC — אחוז מתקן מי שתיה לפי קידוח | קריית אתגרים, רעננה 2012–2025"),
                 fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    fig.savefig(out / "cvoc_pct_standard_panel.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: cvoc_pct_standard_panel.png")


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
    chart_pfas_all_boreholes(df, out)
    chart_btex_timeseries(df, out)
    chart_cvoc_cross_borehole(df, out)
    chart_tce_p25(df, out)
    chart_cvoc_all_wells(df, out)
    chart_pfas_pct_stacked(df, out)
    chart_btex_family_stacked(df, out)
    chart_cvoc_pct_standard_panel(df, out)

    print(f"[V2 Charts] Done — 9 charts saved to {out}/")


if __name__ == "__main__":
    main()
