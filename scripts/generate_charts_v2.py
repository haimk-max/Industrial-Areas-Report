"""Generate V2 charts for Industrial Areas Report.

Raanana zone: 9 zone-specific charts (cvoc_timeseries, pfas, btex, etc.)
Other zones: generic data-driven charts (cvoc_trends, severity_bar, contaminant_panel, site_map)

Usage:
  python scripts/generate_charts_v2.py [--zone raanana] [--output Raanana/charts_v2]
  python scripts/generate_charts_v2.py --zone holon
"""

import argparse
import json as _json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np

from scripts.param_families import classify_family


def _load_selected_ids(zone_dir: Path) -> set | None:
    """Load selected_boreholes.json if it exists (returns set of canonical_ids or None)."""
    sel_file = zone_dir / "data" / "selected_boreholes.json"
    if not sel_file.exists():
        return None
    with open(sel_file, encoding="utf-8") as fh:
        data = _json.load(fh)
    return {b["canonical_id"] for b in data.get("boreholes", [])}


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


def _pct_to_index(pct) -> int:
    """Convert % of drinking water standard to severity index (0–8, per 2021 Report)."""
    if pct is None or (isinstance(pct, float) and np.isnan(pct)):
        return 0
    for level, threshold in [(8, 1000), (7, 500), (6, 200), (5, 100),
                              (4, 75), (3, 50), (2, 25), (1, 10)]:
        if pct >= threshold:
            return level
    return 0


def chart_zone_site_map(zone_dir: Path, out: Path, zone_id: str = "raanana") -> None:
    """Schematic ITM zone map — zone-agnostic, fully offline.

    Computes map extent and contamination index from data. Works for any zone.
    """
    import json
    from matplotlib.patches import Polygon as MplPolygon

    # ── Load data ─────────────────────────────────────────────────────────────
    boreholes = pd.read_csv(zone_dir / "data" / "boreholes.csv")

    # Filter to selected boreholes if selection file exists (Phase 5)
    selected_ids = _load_selected_ids(zone_dir)
    if selected_ids is not None:
        boreholes = boreholes[boreholes['canonical_id'].isin(selected_ids)].reset_index(drop=True)

    # Facility attribution is optional (may not exist for new zones)
    attribution_path = zone_dir / "data" / "facility_attribution.json"
    facilities = []
    if attribution_path.exists():
        with open(attribution_path, encoding='utf-8') as f:
            facilities = json.load(f).get('facilities', [])

    # Zone polygon from zone_definitions
    zone_polygons_file = Path("zone_definitions/zone_polygons.json")
    if not zone_polygons_file.exists():
        zone_polygons_file = zone_dir.parent / "zone_definitions" / "zone_polygons.json"
    zone_polygon_coords = None
    zone_name_he = zone_id
    if zone_polygons_file.exists():
        with open(zone_polygons_file, encoding='utf-8') as f:
            zd = json.load(f)
        zone_def = zd.get(zone_id, {})
        zone_polygon_coords = zone_def.get('polygon') or None
        zone_name_he = zone_def.get('zone_name_he', zone_id)

    # ── Compute max severity index per borehole from measurements ─────────────
    INDEX_COLORS = {
        0: "#BDBDBD", 1: "#81C784", 2: "#81C784", 3: "#81C784",
        4: "#FFB74D", 5: "#FB8C00", 6: "#C62828", 7: "#8E0000", 8: "#4A0000"
    }
    INDEX_SIZES = {0: 90, 1: 110, 2: 110, 3: 110, 4: 160, 5: 200, 6: 240, 7: 280, 8: 320}

    max_index: dict[str, int] = {}
    meas_file = zone_dir / "data" / "measurements.csv"
    if meas_file.exists():
        mdf = pd.read_csv(meas_file)
        mdf['pct'] = pd.to_numeric(mdf.get('percent_of_standard', pd.Series()), errors='coerce')
        mdf['idx'] = mdf['pct'].apply(_pct_to_index)
        max_index = mdf.groupby('canonical_id')['idx'].max().to_dict()

    # ── Map extent: derive from borehole coords + polygon ────────────────────
    all_e = boreholes['itm_easting'].dropna().tolist()
    all_n = boreholes['itm_northing'].dropna().tolist()
    if zone_polygon_coords:
        all_e += [c[0] for c in zone_polygon_coords]
        all_n += [c[1] for c in zone_polygon_coords]

    pad = 600
    E_min = int(min(all_e)) - pad if all_e else 0
    E_max = int(max(all_e)) + pad if all_e else 1000
    N_min = int(min(all_n)) - pad if all_n else 0
    N_max = int(max(all_n)) + pad if all_n else 1000
    span = max(E_max - E_min, N_max - N_min)
    grid_step = 250 if span < 3000 else 500

    # ── Axes ──────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 10), dpi=200)
    ax.set_facecolor('#EEF2F5')
    ax.set_xlim(E_min, E_max)
    ax.set_ylim(N_min, N_max)
    ax.set_xticks(range(E_min, E_max + 1, grid_step))
    ax.set_yticks(range(N_min, N_max + 1, grid_step))
    ax.grid(True, color='white', linewidth=0.7, alpha=0.8, zorder=1)
    ax.tick_params(labelsize=7, color='#666', labelcolor='#555')
    ax.set_xlabel(H('כיוון מזרח — ITM (מטרים)'), fontsize=9, color='#444')
    ax.set_ylabel(H('כיוון צפון — ITM (מטרים)'), fontsize=9, color='#444')

    # ── Zone polygon ──────────────────────────────────────────────────────────
    if zone_polygon_coords and len(zone_polygon_coords) >= 3:
        poly_pts = [(e, n) for e, n in zone_polygon_coords]
        ax.add_patch(MplPolygon(poly_pts, closed=True, zorder=2,
                                facecolor='#FFF9C4', edgecolor='#F9A825',
                                linewidth=2.0, linestyle='-', alpha=0.65))
        cx = sum(p[0] for p in poly_pts[:-1]) / max(len(poly_pts) - 1, 1)
        cy = sum(p[1] for p in poly_pts[:-1]) / max(len(poly_pts) - 1, 1)
        ax.text(cx, cy, H(zone_name_he), ha='center', va='center',
                fontsize=9, color='#B8860B', weight='bold', alpha=0.6, zorder=3)

    # ── Boreholes ─────────────────────────────────────────────────────────────
    for _, row in boreholes.iterrows():
        if pd.isna(row.itm_easting) or pd.isna(row.itm_northing):
            continue
        E, N = float(row.itm_easting), float(row.itm_northing)
        idx = max_index.get(row.canonical_id, 0)
        ax.scatter(E, N, c=INDEX_COLORS.get(idx, "#808080"),
                   s=INDEX_SIZES.get(idx, 100), edgecolors='black',
                   linewidths=0.7, zorder=6, alpha=0.9)
        ax.annotate(H(str(row.name_he)), (E, N), textcoords="offset points",
                    xytext=(7, 5), fontsize=7, ha='left', color='#1A1A1A',
                    weight='bold', zorder=7,
                    bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                              alpha=0.7, edgecolor='none'))

    # ── Facilities ────────────────────────────────────────────────────────────
    for facility in facilities:
        coords = facility.get('coordinates_itm', {})
        if not coords or not coords.get('easting'):
            continue
        E, N = float(coords['easting']), float(coords['northing'])
        ftype = facility.get('type', '')
        if 'fuel' in ftype.lower() or 'דלק' in ftype:
            marker, mcolor = 's', '#1565C0'
        elif 'Private' in ftype or 'פרטי' in ftype:
            continue
        else:
            marker, mcolor = '^', '#6A1B9A'
        ax.scatter(E, N, marker=marker, c=mcolor, s=130, edgecolors='black',
                   linewidths=0.6, zorder=5, alpha=0.9)
        label = str(facility.get('name_he', facility.get('facility_id', '')))[:20]
        if label:
            ax.annotate(H(label), (E, N), textcoords="offset points",
                        xytext=(-7, -15), fontsize=7, ha='right', color='#4A148C',
                        zorder=7,
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFFDE7',
                                  alpha=0.85, edgecolor='#F9A825', linewidth=0.5))

    # ── North arrow + scale bar (relative positions) ─────────────────────────
    na_e = E_max - (E_max - E_min) * 0.06
    na_n_lo = N_min + (N_max - N_min) * 0.84
    na_n_hi = N_min + (N_max - N_min) * 0.92
    ax.annotate('', xy=(na_e, na_n_hi), xytext=(na_e, na_n_lo),
                arrowprops=dict(arrowstyle='->', color='black', lw=2.0), zorder=8)
    ax.text(na_e, na_n_hi + (N_max - N_min) * 0.01, H("צ"),
            ha='center', va='bottom', fontsize=13, weight='bold', color='black')

    sb_e0 = E_min + (E_max - E_min) * 0.10
    sb_e1 = sb_e0 + 500
    sb_n = N_min + (N_max - N_min) * 0.04
    tick = (N_max - N_min) * 0.01
    ax.plot([sb_e0, sb_e1], [sb_n, sb_n], 'k-', linewidth=3, solid_capstyle='butt', zorder=8)
    ax.plot([sb_e0, sb_e0], [sb_n - tick, sb_n + tick], 'k-', lw=2, zorder=8)
    ax.plot([sb_e1, sb_e1], [sb_n - tick, sb_n + tick], 'k-', lw=2, zorder=8)
    ax.text((sb_e0 + sb_e1) / 2, sb_n - 2 * tick, H("500 מטר"),
            ha='center', fontsize=8.5, color='black', weight='bold')

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_elements = [
        mpatches.Patch(facecolor='#4A0000', edgecolor='black', label=H('קידוח: אינדקס 8 (קריטי)')),
        mpatches.Patch(facecolor='#8E0000', edgecolor='black', label=H('קידוח: אינדקס 7–6 (גבוה)')),
        mpatches.Patch(facecolor='#FB8C00', edgecolor='black', label=H('קידוח: אינדקס 5–4 (בינוני)')),
        mpatches.Patch(facecolor='#81C784', edgecolor='black', label=H('קידוח: אינדקס 1–3 (נמוך)')),
        mpatches.Patch(facecolor='#BDBDBD', edgecolor='black', label=H('קידוח: אינדקס 0 (אין זיהום)')),
        mpatches.Patch(facecolor='#6A1B9A', edgecolor='black', label=H('▲ מפעל תעשייתי')),
        mpatches.Patch(facecolor='#1565C0', edgecolor='black', label=H('■ תחנת דלק')),
        mpatches.Patch(facecolor='#FFF9C4', edgecolor='#F9A825', label=H('גבול אזה"ת')),
    ]
    leg = ax.legend(handles=legend_elements, loc='lower right', fontsize=8,
                    framealpha=0.95, frameon=True, edgecolor='#999')
    leg.get_frame().set_linewidth(0.8)

    ax.set_title(H(f'מפת אתר — {zone_name_he} | קידוחי ניטור ומקורות זיהום פוטנציאליים'),
                 fontsize=11, weight='bold', pad=8)
    ax.set_aspect('equal', adjustable='box')
    fig.tight_layout()
    fig.savefig(out / "zone_site_map.png", dpi=200, bbox_inches="tight",
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  Saved: zone_site_map.png")


# ── Generic charts (any zone) ─────────────────────────────────────────────────
# Cross-zone parameter-family classification — handles short codes (Raanana: TCEY)
# and full English names (Holon: TRICHLORO ETHYLENE) via regex patterns.


def _filter_family(df: pd.DataFrame, family: str) -> pd.DataFrame:
    """Subset df to rows whose param matches the given family (CVOC/BTEX/PFAS)."""
    if 'family' not in df.columns:
        df = df.copy()
        df['family'] = df.apply(
            lambda r: classify_family(r.get('param_code'), r.get('param_name')), axis=1)
    return df[df['family'] == family]


def _top_boreholes_for_family(df: pd.DataFrame, family: str, n: int = 6) -> list[str]:
    """Return up to n borehole IDs with highest max concentration for a family."""
    subset = _filter_family(df, family)
    if subset.empty:
        return []
    return (subset.groupby('canonical_id')['concentration']
            .max().nlargest(n).index.tolist())


def chart_generic_trends(df: pd.DataFrame, family: str, title_he: str,
                         std_line: float | None, filename: str, out: Path) -> None:
    """Time-series chart for top boreholes in a family. Cross-zone (Raanana, Holon, etc.)."""
    sub_all = _filter_family(df, family)
    if sub_all.empty:
        print(f"  Skipped {filename}: no data for family {family}")
        return

    top_bhs = _top_boreholes_for_family(sub_all, family, n=6)
    if not top_bhs:
        print(f"  Skipped {filename}: no boreholes with detections in family {family}")
        return

    fig, ax = plt.subplots(figsize=(12, 5), dpi=150)
    colors = plt.cm.tab10.colors
    for i, bh_id in enumerate(top_bhs):
        sub = sub_all[sub_all['canonical_id'] == bh_id].copy()
        sub = sub[sub['concentration'].notna() & (sub['concentration'] > 0)]
        if sub.empty:
            continue
        best_param = sub.groupby('param_code')['concentration'].max().idxmax()
        sub2 = sub[sub['param_code'] == best_param].sort_values('date')
        label = H(f"{str(sub2['name_he'].iloc[0])[:15]} ({str(best_param)[:18]})")
        ax.plot(sub2['date'], sub2['concentration'], marker='o', ms=4,
                color=colors[i % len(colors)], label=label, linewidth=1.4)

    if std_line:
        ax.axhline(std_line, color='red', linestyle='--', linewidth=1.2,
                   label=H(f'תקן שתייה ({std_line} מקג"ל)'))

    ax.set_ylabel(H('ריכוז (מקג"ל)'), fontsize=9)
    ax.set_title(H(title_he), fontsize=10, weight='bold')
    ax.legend(fontsize=7, loc='upper left')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / filename, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {filename}")


def chart_generic_exceedances(df: pd.DataFrame, out: Path) -> None:
    """Bar chart: boreholes ranked by number of measurements exceeding drinking water standard."""
    exceed = df[(df['percent_of_standard'].notna()) & (df['percent_of_standard'] >= 100)]
    if exceed.empty:
        print("  Skipped exceedances_bar.png: no exceedances found")
        return

    counts = (exceed.groupby('canonical_id')['param_code']
              .count().sort_values(ascending=True).tail(20))
    names = df[['canonical_id', 'name_he']].drop_duplicates().set_index('canonical_id')

    fig, ax = plt.subplots(figsize=(10, max(4, len(counts) * 0.35)), dpi=150)
    labels = [H(str(names.loc[bid, 'name_he'])[:20] if bid in names.index else bid)
              for bid in counts.index]
    ax.barh(labels, counts.values, color='#C62828', edgecolor='white', height=0.7)
    ax.set_xlabel(H('מספר מדידות מעל תקן שתייה'), fontsize=9)
    ax.set_title(H('קידוחים עם חריגות מתקן מי שתייה — מספר מדידות'), fontsize=10, weight='bold')
    ax.grid(True, axis='x', alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "exceedances_bar.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: exceedances_bar.png")


def chart_generic_severity_panel(df: pd.DataFrame, out: Path) -> None:
    """Heatmap: max severity index per borehole × contaminant family (CVOC/BTEX/PFAS/OTHER)."""
    df2 = df.copy()
    df2['pct'] = pd.to_numeric(df2.get('percent_of_standard', pd.Series()), errors='coerce')
    df2['idx'] = df2['pct'].apply(_pct_to_index)
    df2['family'] = df2.apply(
        lambda r: classify_family(r.get('param_code'), r.get('param_name')), axis=1)
    # Display 'OTHER' in Hebrew for the chart
    df2.loc[df2['family'] == 'OTHER', 'family'] = 'אחר'
    pivot = (df2.groupby(['canonical_id', 'family'])['idx']
             .max().unstack(fill_value=0))

    if pivot.empty:
        return

    # Keep top 20 boreholes by total index
    pivot = pivot.loc[pivot.sum(axis=1).nlargest(20).index]
    names = df[['canonical_id', 'name_he']].drop_duplicates().set_index('canonical_id')
    pivot.index = [H(str(names.loc[bid, 'name_he'])[:18] if bid in names.index else bid)
                   for bid in pivot.index]

    fig, ax = plt.subplots(figsize=(8, max(5, len(pivot) * 0.4)), dpi=150)
    im = ax.imshow(pivot.values, cmap='RdYlGn_r', vmin=0, vmax=8, aspect='auto')
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=9)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=7)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            v = pivot.values[i, j]
            if v > 0:
                ax.text(j, i, str(v), ha='center', va='center', fontsize=8,
                        color='white' if v >= 5 else 'black')
    plt.colorbar(im, ax=ax, label='מדד חומרה (0–8)')
    ax.set_title(H('מדד חומרה מרבי — קידוחים × קבוצת מזהם'), fontsize=10, weight='bold')
    fig.tight_layout()
    fig.savefig(out / "severity_panel.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: severity_panel.png")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate V2 charts for a zone")
    parser.add_argument("--zone", default="raanana")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    zone_id = args.zone.lower()
    zone_dir = Path(args.zone.capitalize())
    if not zone_dir.exists():
        zone_dir = Path(args.zone)
    if not zone_dir.exists():
        sys.exit(f"Zone directory not found: {args.zone}")

    out = Path(args.output) if args.output else zone_dir / "charts_v2"
    out.mkdir(parents=True, exist_ok=True)

    df = load_measurements(zone_dir)
    print(f"[V2 Charts] Zone={zone_id} | {len(df)} measurements from {zone_dir}")

    # Filter to selected boreholes if selection file exists (Phase 5)
    selected_ids = _load_selected_ids(zone_dir)
    if selected_ids is not None:
        n_before = len(df)
        df = df[df['canonical_id'].isin(selected_ids)].reset_index(drop=True)
        print(f"  Filtered to {len(selected_ids)} selected boreholes ({n_before} → {len(df)} rows)")

    # Zone site map — works for any zone
    chart_zone_site_map(zone_dir, out, zone_id=zone_id)

    if zone_id == "raanana":
        # Raanana-specific charts (borehole IDs known)
        chart_cvoc_timeseries(df, out)
        chart_pfas_all_boreholes(df, out)
        chart_btex_timeseries(df, out)
        chart_cvoc_cross_borehole(df, out)
        chart_tce_p25(df, out)
        chart_cvoc_all_wells(df, out)
        chart_pfas_pct_stacked(df, out)
        chart_btex_family_stacked(df, out)
        chart_cvoc_pct_standard_panel(df, out)
        print(f"[V2 Charts] Done — 10 charts saved to {out}/")
    else:
        # Generic data-driven charts for any zone
        chart_generic_trends(df, "CVOC",
                             "מגמות ריכוז CVOC — קידוחים מובילים", 7.5,
                             "cvoc_trends.png", out)
        chart_generic_trends(df, "BTEX",
                             "מגמות ריכוז BTEX — קידוחים מובילים", 5.0,
                             "btex_trends.png", out)
        chart_generic_trends(df, "PFAS",
                             "מגמות ריכוז PFAS — קידוחים מובילים", None,
                             "pfas_trends.png", out)
        chart_generic_exceedances(df, out)
        chart_generic_severity_panel(df, out)
        print(f"[V2 Charts] Done — generic charts saved to {out}/")


if __name__ == "__main__":
    main()
