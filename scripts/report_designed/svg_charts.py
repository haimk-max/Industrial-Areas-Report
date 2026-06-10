"""Pure-Python SVG chart generators for the designed Holon report.

All charts use the academic monochrome palette from Claude Design v2.
Red (#a82a1c) reserved for: compliance violations, monitoring gaps, INCREASING trends.
"""

from __future__ import annotations
import math
import pandas as pd
from .data_loader import esc


# Palette (matches template.html :root)
INK = "#1a1a1a"
INK_2 = "#3a3a3a"
SOFT = "#6b6b6b"
RED = "#a82a1c"
RED_SOFT = "#d99a93"
GREY_1 = "#f0ede6"
GREY_2 = "#d8d3c8"
GREY_3 = "#a8a29a"
GREY_4 = "#5a564f"
PAPER = "#fdfcf9"
RULE_LIGHT = "#cfcfcf"
RULE_FAINT = "#e6e3dd"


# ───────────────────────── Helpers ─────────────────────────

def log_y(c: float, c_min: float, c_max: float, y_top: float, y_bot: float) -> float:
    """Map concentration to log-scale Y pixel."""
    if c <= 0:
        c = c_min
    log_min = math.log10(max(c_min, 0.01))
    log_max = math.log10(c_max)
    log_c = math.log10(max(c, c_min))
    return y_top + (y_bot - y_top) * (1 - (log_c - log_min) / (log_max - log_min))


def linear_x(year: float, y_min: int, y_max: int, x_left: float, x_right: float) -> float:
    """Map year to X pixel."""
    return x_left + (x_right - x_left) * (year - y_min) / (y_max - y_min)


# ───────────────────────── Figure 1: Severity Ledger ─────────────────────────

def svg_severity_ledger(severity: pd.DataFrame) -> str:
    """Build the F1 ledger: only families with significant findings in Holon.

    Order: CVOC → METALS → FUEL (last, per user request).
    PFAS omitted entirely (max bucket = 0 in Holon, not a focus).
    """
    industry = severity[severity.family == "CVOC"].sort_values("contributing_pct", ascending=False)
    metals = severity[severity.family == "METALS"].sort_values("contributing_pct", ascending=False)
    fuel = severity[severity.family == "FUEL"].sort_values("contributing_pct", ascending=False)

    rows = []

    if not industry.empty:
        top = industry.iloc[0]
        ratio = top.contributing_pct / 100
        body = (f"קידוח מוביל: <b>{esc(top.name_he)}</b> — ריכוז שיא ×{ratio:,.0f} מהתקן "
                f"({esc(top.contributing_param)}). הזיהום מקורו במפעלי תדירגן וציפוי "
                f"היסטוריים; DNAPL בעומק האקוויפר.")
        rows.append(_ledger_row("תרכובות אורגניות מוכלרות",
                                "TCE · PCE · cis-DCE · ליבת הזיהום ההיסטורי",
                                body, ratio))

    if not metals.empty:
        top = metals.iloc[0]
        ratio = top.contributing_pct / 100
        body = (f"קידוח מוביל: <b>{esc(top.name_he)}</b> — {esc(top.contributing_param)} "
                f"×{ratio:,.0f} מהתקן. תוצר היסטורי של תעשיות ציפוי וגלוון.")
        rows.append(_ledger_row("מתכות כבדות",
                                "כרום שש-ערכי · ניקל · קלסטר מזרחי",
                                body, ratio))

    if not fuel.empty:
        top = fuel.iloc[0]
        ratio = top.contributing_pct / 100
        body = (f"קידוח מוביל: <b>{esc(top.name_he)}</b> — {esc(top.contributing_param)} "
                f"×{ratio:,.0f} מהתקן. מקור: UST במתחמי דלק (אגד, מרכבות אש).")
        rows.append(_ledger_row("דלקים",
                                "בנזן · MTBE · BTEX",
                                body, ratio, appendix=True))

    return '<div class="ledger">' + "".join(rows) + "</div>"


def _ledger_row(fam: str, fam_sub: str, body: str, ratio: float, appendix: bool = False) -> str:
    cls = "row appendix" if appendix else "row"
    big_color_style = "" if not appendix else ""
    return (f'<div class="{cls}">'
            f'<div class="fam">{esc(fam)}<small>{esc(fam_sub)}</small></div>'
            f'<div class="body">{body}</div>'
            f'<div class="metric">'
            f'<span class="big">{ratio:,.0f}</span>'
            f'<span class="ratio">×{ratio:,.0f} מהתקן</span>'
            f'</div>'
            f'</div>')


# ───────────────────────── Figure 2: Severity Matrix Table ─────────────────────────

def svg_severity_matrix(severity: pd.DataFrame, trends: pd.DataFrame,
                         data_avail: pd.DataFrame) -> str:
    """Build the F2 severity matrix grouped by contamination focus (CVOC, METALS, FUEL).

    Under each borehole name: max exceeding compound + concentration for that section's family.
    Holon-specific: PFAS column omitted (all bucket=0 in Holon, not an active focus).
    """
    # Build lookup: (borehole, family) → (param, concentration, unit)
    # Pick the row in `severity` with max contributing_pct for each (borehole, family).
    detail_lookup = {}
    for (bid, fam), grp in severity.groupby(["borehole", "family"]):
        top = grp.sort_values("contributing_pct", ascending=False).iloc[0]
        detail_lookup[(bid, fam)] = {
            "param": top.get("contributing_param", ""),
            "pct": top.get("contributing_pct", 0),
        }

    # Try to enrich with absolute concentrations from param-level severity if available
    try:
        from .data_loader import load_param_level_severity
        param_lvl = load_param_level_severity()
        if not param_lvl.empty:
            for (bid, fam), grp in param_lvl.groupby(["borehole", "family"]):
                top = grp.sort_values("pct_of_standard", ascending=False).iloc[0]
                detail_lookup[(bid, fam)] = {
                    "param": top.get("param_code", ""),
                    "pct": top.get("pct_of_standard", 0),
                    "concentration": top.get("concentration", None),
                    "unit": top.get("unit", "µg/L"),
                }
    except Exception:
        pass

    # Pivot severity to wide form (excluding PFAS — not a Holon focus)
    pivot = severity.pivot_table(
        index=["borehole", "name_he"],
        columns="family",
        values="max_bucket",
        aggfunc="max",
    ).reset_index()

    pivot.columns.name = None
    for col in ["CVOC", "METALS", "FUEL"]:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot[["CVOC", "METALS", "FUEL"]] = pivot[["CVOC", "METALS", "FUEL"]].fillna(0)

    pivot["max_bucket"] = pivot[["CVOC", "METALS", "FUEL"]].max(axis=1)
    # Skip boreholes with no contamination at all
    pivot = pivot[pivot["max_bucket"] > 0].copy()

    # Site consolidation: identify representative boreholes per site
    def get_site(borehole_id: str) -> str:
        if "נת_חולון" in borehole_id:
            return "נת_חולון"
        elif "נד_אגד" in borehole_id:
            return "נד_אגד"
        elif "נת_אלביט" in borehole_id:
            return "נת_חולון"
        else:
            return borehole_id

    pivot["site"] = pivot["borehole"].apply(get_site)

    # Select representatives
    keep_boreholes = set()
    holon_group = pivot[pivot["site"] == "נת_חולון"]
    keep_boreholes.update(holon_group["borehole"].tolist())
    egged_group = pivot[pivot["site"] == "נד_אגד"].sort_values("max_bucket", ascending=False)
    keep_boreholes.update(egged_group.head(2)["borehole"].tolist())
    other_group = pivot[~pivot["site"].isin(["נת_חולון", "נד_אגד"])]
    keep_boreholes.update(other_group["borehole"].tolist())
    pivot = pivot[pivot["borehole"].isin(keep_boreholes)].copy()

    # Compute INCREASING/stopped markers
    inc_set = set()
    if not trends.empty:
        for _, r in trends[trends.classification == "INCREASING"].iterrows():
            inc_set.add(r.borehole_id)
    stopped = set()
    if not data_avail.empty:
        agg = data_avail.groupby("borehole")["last_year"].max().reset_index()
        for _, r in agg.iterrows():
            if r.last_year < 2023:
                stopped.add(r.borehole)

    # Group boreholes by contamination focus.
    # CVOC and METALS sections show all boreholes with that contamination
    # (a borehole with both appears in both sections — matching V4 narrative
    # which discusses the same borehole under multiple foci, e.g., נת חולון 14
    # appears in both CVOC §4.1 and METALS §4.2).
    # FUEL section: boreholes with ONLY FUEL contamination (no CVOC, no METALS).
    cvoc_rows = pivot[pivot["CVOC"] > 0].sort_values("CVOC", ascending=False)
    metals_rows = pivot[pivot["METALS"] > 0].sort_values("METALS", ascending=False)
    fuel_rows = pivot[(pivot["FUEL"] > 0) &
                       (pivot["CVOC"] == 0) &
                       (pivot["METALS"] == 0)].sort_values("FUEL", ascending=False)

    def make_row(r, section_family: str):
        bid = r.borehole
        nm = r.name_he
        mark_inc = ' <span class="up">↑</span>' if bid in inc_set else ""
        mark_stop = ' <span style="color:var(--red);font-weight:700">●</span>' if bid in stopped else ""

        # Build sub-line: max compound + concentration for this section's family
        detail = detail_lookup.get((bid, section_family))
        sub = ""
        if detail:
            param = _short_param_name(detail.get("param", ""))
            conc = detail.get("concentration")
            pct = detail.get("pct", 0)
            unit = _normalize_unit(detail.get("unit", "µg/L"))
            ratio_str = _format_ratio(pct)
            if conc is not None and not pd.isna(conc):
                conc_str = _format_concentration(conc)
                sub = f'<small>{esc(param)} · {conc_str} {esc(unit)} ({ratio_str})</small>'
            elif pct:
                sub = f'<small>{esc(param)} · {ratio_str}</small>'

        return (
            f'<tr>'
            f'<td class="lbl">{esc(nm)}{mark_inc}{mark_stop}{sub}</td>'
            f'<td class="val">{_bucket_cell(int(r.CVOC))}</td>'
            f'<td class="val">{_bucket_cell(int(r.METALS))}</td>'
            f'<td class="val">{_bucket_cell(int(r.FUEL))}</td>'
            f'</tr>'
        )

    def section_header(title: str, n: int) -> str:
        return (f'<tr class="sec"><td colspan="4">'
                f'{esc(title)} <span class="cnt">({n})</span>'
                f'</td></tr>')

    body_parts = []
    if not cvoc_rows.empty:
        body_parts.append(section_header("מוקד CVOC — תרכובות אורגניות מוכלרות", len(cvoc_rows)))
        body_parts.extend(make_row(r, "CVOC") for _, r in cvoc_rows.iterrows())
    if not metals_rows.empty:
        body_parts.append(section_header("מוקד מתכות — כרום וניקל", len(metals_rows)))
        body_parts.extend(make_row(r, "METALS") for _, r in metals_rows.iterrows())
    if not fuel_rows.empty:
        body_parts.append(section_header("מוקד דלקים — בנזן ו-MTBE", len(fuel_rows)))
        body_parts.extend(make_row(r, "FUEL") for _, r in fuel_rows.iterrows())

    return (
        '<table class="matrix">'
        '<thead><tr>'
        '<th>קידוח</th><th>CVOC</th><th>מתכות</th><th>דלקים</th>'
        '</tr></thead>'
        '<tbody>' + "".join(body_parts) + '</tbody>'
        '</table>'
    )


_PARAM_SHORT_NAMES = {
    "TRICHLORO ETHYLENE": "TCE",
    "TETRACHLORO ETHYLENE": "PCE",
    "CIS 1,2 DICHLOROETHYLENE": "cis-1,2-DCE",
    "DICHLOROETHYLENE 1,1": "1,1-DCE",
    "1,4 DIOXANE": "1,4-Dioxane",
    "VINYL CHLORIDE": "VC",
    "CHLOROFORM": "Chloroform",
    "CHROMIUM AS CR": "Cr",
    "NICKEL AS NI": "Ni",
    "ARSENIC AS AS": "As",
    "CADMIUM AS CD": "Cd",
    "LEAD AS PB": "Pb",
    "BENZENE": "Benzene",
    "MTBE": "MTBE",
    " MTBE": "MTBE",
    "TOLUENE": "Toluene",
    "XYLENE": "Xylene",
    "ETHYL BENZENE": "Ethylbenzene",
}


def _short_param_name(p: str) -> str:
    p = (p or "").strip()
    return _PARAM_SHORT_NAMES.get(p, p)


def _normalize_unit(u: str) -> str:
    """Convert CSV unit strings to display form."""
    if not u:
        return "µg/L"
    u = u.strip()
    if u.lower() in ("microgr/l", "ug/l", "ppb"):
        return "µg/L"
    if u.lower() in ("mg/l", "ppm"):
        return "mg/L"
    return u


def _format_concentration(c: float) -> str:
    """Format concentration: no decimals for ≥10, one decimal for <10."""
    if c >= 100:
        return f"{c:,.0f}"
    if c >= 10:
        return f"{c:,.0f}"
    if c >= 1:
        return f"{c:,.1f}"
    return f"{c:,.2f}"


def _format_ratio(pct: float) -> str:
    """Format ratio of standard. pct = percent of DWS.
    - pct ≥ 100 → '×N מהתקן' (multiples of standard)
    - pct < 100 → 'N% מהתקן' (percent below standard)
    """
    if pct is None or pd.isna(pct):
        return ""
    if pct >= 100:
        ratio = pct / 100
        if ratio >= 10:
            return f"×{ratio:,.0f} מהתקן"
        return f"×{ratio:,.1f} מהתקן"
    return f"{pct:,.0f}% מהתקן"


def _bucket_cell(b: int) -> str:
    if b == 0:
        return '<span class="b s0">0</span>'
    cls = "s0"
    if b <= 2: cls = "s2"
    elif b <= 4: cls = "s4"
    elif b <= 6: cls = "s6"
    else: cls = "s8"
    return f'<span class="b {cls}">{b}</span>'


# ───────────────────────── Figure 3: CVOC small multiples (Top wells time series) ─────────────────────────

_CVOC_PARAMS = ["TRICHLORO ETHYLENE", "1,4 DIOXANE", "TETRACHLORO ETHYLENE"]
_METALS_PARAMS = ["CHROMIUM AS CR", "NICKEL AS NI"]
_FUEL_PARAMS = ["BENZENE", "MTBE", " MTBE", "TOLUENE"]


def svg_cvoc_panels(measurements: pd.DataFrame, severity: pd.DataFrame,
                    boreholes_override: list = None) -> str:
    """CVOC time-series panels (top 3 compounds by exceedance: TCE, 1,4-Dioxane, PCE).

    boreholes_override: explicit list of canonical_ids from V4.md (Opus's selection).
        If None, falls back to top-6 CVOC by max_bucket. See PROCESS_GUIDE §VIII.1.
    """
    alert_boreholes = set(measurements['canonical_id'].unique())
    if boreholes_override:
        # Respect Opus's selection AND its order: the report narrative decides which
        # findings matter. The engine only filters to wells that actually carry CVOC
        # data (so a panel isn't empty) and caps at a grid-friendly maximum. NO
        # severity re-sort — Opus already presents the most important wells first.
        cvoc_wells = set(measurements[measurements.param_code.isin(_CVOC_PARAMS)]['canonical_id'])
        top_wells = [w for w in boreholes_override
                     if w in alert_boreholes and w in cvoc_wells][:8]
    else:
        industry = severity[
            (severity.family == "CVOC") &
            (severity.borehole.isin(alert_boreholes))
        ].sort_values("max_bucket", ascending=False)
        top_wells = industry.head(6)["borehole"].tolist()

    panels = []
    for wid in top_wells:
        nm = severity[severity.borehole == wid].iloc[0].name_he
        well_data = measurements[
            (measurements.canonical_id == wid) &
            (measurements.param_code.isin(_CVOC_PARAMS))
        ].copy()
        if well_data.empty:
            continue
        panels.append(_time_series_panel(well_data, nm, dws=7.5, dws_param="TCE",
                                          width=400, height=276,
                                          param_order=_CVOC_PARAMS))

    if not panels:
        return f'<div style="padding:30px;color:{SOFT};text-align:center">אין נתוני CVOC</div>'

    return _small_multiples_grid(panels, cols=2)


# ───────────────────────── Figure 4: Metals time series (Cr + Ni) ─────────────────────────

def svg_chromium_panels(measurements: pd.DataFrame,
                         boreholes_override: list = None) -> str:
    """Metals time-series panels: Chromium + Nickel (top 2 metals by exceedance).

    boreholes_override: explicit list of canonical_ids from V4.md (Opus's selection).
        If None, falls back to top-4 by max Cr concentration. See PROCESS_GUIDE §VIII.1.

    DWS used: Chromium 50 µg/L (Cr is the dominant exceedance). Nickel DWS = 70 µg/L
    is not shown as a second red line to keep visual clarity; Ni exceedance is
    contextualized via the legend and matrix sub-line.
    """
    metals_data = measurements[
        measurements.param_code.isin(_METALS_PARAMS)
    ].copy()
    if metals_data.empty:
        return f'<div style="padding:30px;color:{SOFT};text-align:center">אין נתוני מתכות</div>'

    if boreholes_override:
        # Respect Opus's selection AND order; filter only to wells that carry metals
        # data. No max-concentration re-sort — the narrative order is authoritative.
        available = set(metals_data['canonical_id'].unique())
        wells = [w for w in boreholes_override if w in available][:6]
    else:
        # Order wells by max Cr concentration (the headline contaminant)
        well_max = (
            metals_data[metals_data.param_code == "CHROMIUM AS CR"]
            .groupby("canonical_id").concentration.max().sort_values(ascending=False)
        )
        wells = well_max.index.tolist()[:4]

    panels = []
    for wid in wells:
        well_data = metals_data[metals_data.canonical_id == wid].copy()
        if well_data.empty:
            continue
        nm = well_data.iloc[0].name_he
        panels.append(_time_series_panel(well_data, nm, dws=50.0, dws_param="Cr",
                                          width=440, height=286,
                                          param_order=_METALS_PARAMS))

    if not panels:
        return f'<div style="padding:30px;color:{SOFT};text-align:center">אין נתוני מתכות</div>'

    return _small_multiples_grid(panels, cols=2)


# ───────────────────────── Figure 5: BTEX panels (Benzene, MTBE, Toluene) ─────────────────────────

def svg_btex_panels(measurements: pd.DataFrame,
                     boreholes_override: list = None) -> str:
    """Fuel time-series: Benzene, MTBE, Toluene (top 3 by exceedance).

    boreholes_override: explicit list of canonical_ids from V4.md (Opus's selection).
        If None, falls back to top-6 by max concentration. See PROCESS_GUIDE §VIII.1.
    """
    fuel_data = measurements[measurements.param_code.isin(_FUEL_PARAMS)].copy()
    if fuel_data.empty:
        return f'<div style="padding:30px;color:{SOFT};text-align:center">אין נתוני דלקים</div>'

    if boreholes_override:
        # Respect Opus's selection AND order; filter only to wells that carry fuel
        # data. No max-concentration re-sort — the narrative order is authoritative.
        available = set(fuel_data['canonical_id'].unique())
        top_wells = [w for w in boreholes_override if w in available][:8]
    else:
        # Select representative FUEL boreholes by max concentration
        well_max = fuel_data.groupby("canonical_id").concentration.max().sort_values(ascending=False)
        top_wells = well_max.head(6).index.tolist()

    # Normalize the leading-space MTBE variant so legend/grouping is clean
    fuel_data["param_code"] = fuel_data["param_code"].str.strip()
    param_order = ["BENZENE", "MTBE", "TOLUENE"]

    panels = []
    for wid in top_wells:
        well_data = fuel_data[fuel_data.canonical_id == wid].copy()
        if well_data.empty:
            continue
        nm = well_data.iloc[0].name_he
        panels.append(_time_series_panel(well_data, nm, dws=5.0, dws_param="Benzene",
                                          width=400, height=276,
                                          param_order=param_order))

    if not panels:
        return f'<div style="padding:30px;color:{SOFT};text-align:center">אין נתוני דלקים</div>'

    return _small_multiples_grid(panels, cols=2)


# ───────────────────────── Internal: time-series panel ─────────────────────────

_PARAM_STYLES = [
    {"color": "#1a1a1a", "dash": "none",      "marker": "circle"},   # solid black
    {"color": "#5a564f", "dash": "5 2",       "marker": "square"},   # dashed dark-grey
    {"color": "#8a8278", "dash": "1.5 2",     "marker": "triangle"}, # dotted medium-grey
]


def _time_series_panel(well_data: pd.DataFrame, name_he: str, dws: float,
                        dws_param: str = None,
                        width: int = 380, height: int = 256,
                        param_order: list = None) -> str:
    """One SVG time-series panel: log Y, linear X (year), DWS dashed red line.

    Supports multiple parameters with distinct line styles + legend at bottom.

    Args:
        well_data: DataFrame with date, concentration, param_code
        name_he: Hebrew title shown above panel
        dws: Drinking-water-standard line value (red dashed)
        dws_param: Parameter the DWS line refers to (e.g. "TCE"). Shown in the DWS
                   label so a multi-parameter panel makes clear which standard the
                   single red line represents.
        width/height: SVG dimensions
        param_order: List of param_code strings to draw in this order (top to bottom in legend).
                     If None, uses order found in well_data.
    """
    well_data = well_data.copy()
    _dt = pd.to_datetime(well_data["date"])
    well_data["year"] = _dt.dt.year
    # Fractional year (year + day-of-year fraction) is the X coordinate, so two
    # samples in the SAME calendar year separate horizontally instead of stacking
    # into a vertical line that looks like a connector between two parameters.
    well_data["xpos"] = _dt.dt.year + (_dt.dt.dayofyear - 1) / 365.25

    # Determine params present in this well, respecting the requested order
    available = list(well_data.param_code.unique())
    if param_order:
        params = [p for p in param_order if p in available]
    else:
        params = available
    if not params:
        params = available

    # Plot area — generous title (top), axis labels (bottom), legend (very bottom).
    # pad_b holds: year ticks, the "Year" axis title, and the two-row legend.
    pad_l, pad_r, pad_t, pad_b = 46, 14, 38, 70
    x_left = pad_l
    x_right = width - pad_r
    y_top = pad_t
    y_bot = height - pad_b

    y_min_year = 2010
    y_max_year = 2026
    c_min = 0.1
    c_max = max(well_data.concentration.max() * 1.2, dws * 5)

    # direction:ltr on the root neutralizes any RTL HTML container so the numeric
    # Y-axis labels stay anchored to the LEFT of the axis (the Hebrew title carries
    # its own rtl-title class override).
    parts = [f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
             f'direction="ltr" xmlns="http://www.w3.org/2000/svg">']
    parts.append(
        '<style>'
        'text.rtl-title { direction:rtl; unicode-bidi:isolate; font-family:"Frank Ruhl Libre","Times New Roman",serif; }'
        'text.tick { font-family:"IBM Plex Mono",monospace; }'
        'text.legend-label { font-family:"Source Sans 3",sans-serif; direction:ltr; unicode-bidi:bidi-override; }'
        '</style>'
    )

    # Year gridlines + tick labels (INK so the time axis is clearly readable)
    for yr in [2012, 2014, 2016, 2018, 2020, 2022, 2024]:
        x = linear_x(yr, y_min_year, y_max_year, x_left, x_right)
        parts.append(f'<line x1="{x:.1f}" y1="{y_top}" x2="{x:.1f}" y2="{y_bot}" '
                     f'stroke="{RULE_LIGHT}" stroke-width="0.4"/>')
        parts.append(f'<text x="{x:.1f}" y="{y_bot + 13}" '
                     f'font-family="IBM Plex Mono,monospace" font-size="9.5" '
                     f'text-anchor="middle" fill="{INK}">{yr}</text>')
    # X-axis title — makes explicit that the horizontal axis is time (years)
    parts.append(f'<text x="{(x_left + x_right) / 2:.1f}" y="{y_bot + 28}" '
                 f'font-family="Source Sans 3,sans-serif" font-size="9.5" '
                 f'text-anchor="middle" fill="{SOFT}">Year</text>')

    # Log-scale gridlines
    for c in [0.1, 1, 10, 100, 1000, 10000, 100000]:
        if c > c_max: break
        if c < c_min: continue
        y = log_y(c, c_min, c_max, y_top, y_bot)
        parts.append(f'<line x1="{x_left}" y1="{y:.1f}" x2="{x_right}" y2="{y:.1f}" '
                     f'stroke="{RULE_LIGHT}" stroke-width="0.4"/>')
        lbl = f"{c:g}" if c >= 1 else f"{c:.1f}"
        parts.append(f'<text x="{x_left - 6}" y="{y + 3:.1f}" '
                     f'font-family="IBM Plex Mono,monospace" font-size="9" '
                     f'text-anchor="end" fill="{INK}">{lbl}</text>')

    # DWS line (red dashed). The label names the parameter the standard refers to,
    # so a multi-parameter panel makes clear the single red line is e.g. TCE's DWS.
    if dws <= c_max:
        y_dws = log_y(dws, c_min, c_max, y_top, y_bot)
        dws_lbl = f"DWS {dws_param} {dws:g}" if dws_param else f"DWS {dws:g}"
        parts.append(f'<line x1="{x_left}" y1="{y_dws:.1f}" x2="{x_right}" y2="{y_dws:.1f}" '
                     f'stroke="{RED}" stroke-width="1" stroke-dasharray="3 2"/>')
        # DWS label at right
        parts.append(f'<text x="{x_right - 4}" y="{y_dws - 3:.1f}" '
                     f'font-family="IBM Plex Mono,monospace" font-size="8.5" '
                     f'text-anchor="end" fill="{RED}">{esc(dws_lbl)}</text>')

    # Axes
    parts.append(f'<line x1="{x_left}" y1="{y_top}" x2="{x_left}" y2="{y_bot}" '
                 f'stroke="{INK}" stroke-width="1"/>')
    parts.append(f'<line x1="{x_left}" y1="{y_bot}" x2="{x_right}" y2="{y_bot}" '
                 f'stroke="{INK}" stroke-width="1"/>')

    # Y-axis title (µg/L)
    parts.append(f'<text x="{x_left - 32}" y="{(y_top + y_bot) / 2:.1f}" '
                 f'font-family="Source Sans 3,sans-serif" font-size="9.5" '
                 f'text-anchor="middle" fill="{SOFT}" '
                 f'transform="rotate(-90 {x_left - 32} {(y_top + y_bot) / 2:.1f})">µg/L (log)</text>')

    # Data: one series per param, ordered per param_order
    for i, param in enumerate(params):
        style = _PARAM_STYLES[i % len(_PARAM_STYLES)]
        grp = well_data[well_data.param_code == param].sort_values("xpos")
        pts = []
        last_xy = None
        for _, r in grp.iterrows():
            if r.concentration <= 0:
                continue
            x = linear_x(r.xpos, y_min_year, y_max_year, x_left, x_right)
            y = log_y(r.concentration, c_min, c_max, y_top, y_bot)
            pts.append(f"{x:.1f},{y:.1f}")
            last_xy = (x, y)
            parts.append(_marker(x, y, style["marker"], style["color"]))
        if len(pts) >= 2:
            dash_attr = "" if style["dash"] == "none" else f' stroke-dasharray="{style["dash"]}"'
            parts.append(f'<polyline points="{" ".join(pts)}" '
                         f'fill="none" stroke="{style["color"]}" stroke-width="1.3"{dash_attr}/>')
        # Inline end-of-curve label: identify which contaminant each curve is, directly
        # on the curve (independent of the bottom legend, which can be clipped).
        if last_xy is not None:
            lx, ly = last_xy
            near_right = lx > (x_left + x_right) / 2
            tx = lx - 3 if near_right else lx + 3
            anchor = "end" if near_right else "start"
            parts.append(f'<text x="{tx:.1f}" y="{ly - 4:.1f}" '
                         f'font-family="Source Sans 3,sans-serif" font-size="8" font-weight="600" '
                         f'direction="ltr" unicode-bidi="bidi-override" '
                         f'text-anchor="{anchor}" fill="{style["color"]}">'
                         f'{esc(_short_param_name(param))}</text>')

    # Title (well name) — at top, single line, larger; RTL for Hebrew with mixed content
    parts.append(f'<text x="{width / 2:.1f}" y="20" font-family="Source Sans 3,sans-serif" '
                 f'font-size="12" font-weight="700" fill="{INK}" '
                 f'class="rtl-title" '
                 f'text-anchor="middle">{esc(name_he)}</text>')

    # Legend at bottom — two-row layout: line sample on TOP, label BELOW (no overlap).
    # LTR direction forced (parameter names use Latin chars; RTL page would flip them).
    n = max(len(params), 1)
    avail = x_right - x_left
    item_w = avail / n
    line_y = height - 28       # top row: line/marker
    text_y = height - 10       # bottom row: text baseline
    parts.append(f'<g direction="ltr">')
    for i, param in enumerate(params):
        style = _PARAM_STYLES[i % len(_PARAM_STYLES)]
        # Center the item within its slot
        center_x = x_left + (i + 0.5) * item_w
        dash_attr = "" if style["dash"] == "none" else f' stroke-dasharray="{style["dash"]}"'
        # Line sample (24px wide) centered horizontally on TOP row
        line_x1 = center_x - 14
        line_x2 = center_x + 10
        parts.append(f'<line x1="{line_x1:.1f}" y1="{line_y:.1f}" '
                     f'x2="{line_x2:.1f}" y2="{line_y:.1f}" '
                     f'stroke="{style["color"]}" stroke-width="1.4"{dash_attr}/>')
        parts.append(_marker(center_x - 2, line_y, style["marker"], style["color"]))
        # Label CENTERED in slot, on BOTTOM row, LTR forced
        parts.append(f'<text x="{center_x:.1f}" y="{text_y:.1f}" '
                     f'font-family="Source Sans 3,sans-serif" font-size="10.5" '
                     f'direction="ltr" unicode-bidi="bidi-override" '
                     f'text-anchor="middle" fill="{INK}">{esc(_short_param_name(param))}</text>')
    parts.append('</g>')

    parts.append('</svg>')
    return "".join(parts)


def _marker(x: float, y: float, shape: str, color: str) -> str:
    """SVG marker (circle, square, or triangle)."""
    if shape == "square":
        return (f'<rect x="{x - 2:.1f}" y="{y - 2:.1f}" width="4" height="4" '
                f'fill="{color}"/>')
    if shape == "triangle":
        return (f'<polygon points="{x:.1f},{y - 2.4:.1f} '
                f'{x - 2.2:.1f},{y + 1.8:.1f} {x + 2.2:.1f},{y + 1.8:.1f}" '
                f'fill="{color}"/>')
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="{color}"/>'


def _small_multiples_grid(panels: list, cols: int = 3) -> str:
    """Wrap SVG panels in a CSS grid with subtle dividers — matches academic report style."""
    cells = [f'<div>{p}</div>' for p in panels]
    return (
        f'<div style="display:grid;grid-template-columns:repeat({cols},1fr);'
        f'gap:0;background:{PAPER}">'
        + "".join(
            f'<div style="background:{PAPER};padding:14px 10px 10px;'
            f'border-right:1px solid {RULE_FAINT};border-bottom:1px solid {RULE_FAINT}">{c}</div>'
            for c in cells
        )
        + '</div>'
    )


# ───────────────────────── Figure 6: Monitoring gaps timeline ─────────────────────────

def svg_monitoring_gaps(data_avail: pd.DataFrame, severity: pd.DataFrame) -> str:
    """Timeline showing monitoring gaps: only wells with high contamination index that stopped before 2023.

    Filter:
      - Non-FUEL families (CVOC/METALS/PFAS): max_index > 3
      - Production wells (prefix מק_): max_index > 2
    """
    if data_avail.empty:
        return f'<div style="padding:30px;color:{SOFT};text-align:center">אין נתוני זמינות</div>'

    # Build severity summary per borehole (max index and primary family)
    sev_summary = severity.pivot_table(
        index="borehole",
        columns="family",
        values="max_bucket",
        aggfunc="max",
    ).fillna(0)
    sev_summary["max_index"] = sev_summary.max(axis=1)
    sev_summary = sev_summary.reset_index()

    # Determine primary contamination family per borehole
    for idx, row in sev_summary.iterrows():
        families_present = [fam for fam in ["CVOC", "METALS", "PFAS"] if row.get(fam, 0) > 0]
        sev_summary.loc[idx, "primary_family"] = families_present[0] if families_present else "FUEL"

    # Aggregate per borehole: first_year, last_year
    agg = data_avail.groupby(["borehole", "name_he"]).agg(
        first_year=("first_sample_date", lambda x: pd.to_datetime(x).dt.year.min()),
        last_year=("last_sample_date", lambda x: pd.to_datetime(x).dt.year.max()),
    ).reset_index()

    # Join with severity summary
    agg = agg.merge(sev_summary[["borehole", "max_index", "primary_family"]], on="borehole", how="left")

    # Mark production wells (מק_ prefix)
    agg["is_production"] = agg["borehole"].str.startswith("מק_")

    # Filter: stopped before 2023, with high severity per type
    threshold_non_fuel = 3      # אינדקס > 3 בקידוחים בעלי משפחות לא-דלק
    threshold_production = 2    # אינדקס > 2 בקידוחי הפקה
    stopped = agg[
        (agg.last_year < 2023) &
        (
            ((agg.primary_family != "FUEL") & (agg.max_index > threshold_non_fuel)) |
            (agg.is_production & (agg.max_index > threshold_production))
        )
    ].sort_values("last_year")

    if stopped.empty:
        return '<div style="padding:20px;color:#6b6b6b;text-align:center">אין הפסקות ניטור בקידוחים חורגים מובהקים בעלי אינדקס גבוה</div>'

    yr_min, yr_max = 2010, 2026
    rows = []
    rows.append('<div class="gap-grid">')
    rows.append('<div class="hd">קידוח</div>')
    rows.append('<div class="hd">קו זמן 2010–2026</div>')
    rows.append('<div class="hd">דיגום אחרון</div>')

    for _, r in stopped.iterrows():
        nm = r.name_he
        family = r.primary_family
        max_idx = int(r.max_index)
        first_yr = int(r.first_year)
        last_yr = int(r.last_year)
        a_left = (first_yr - yr_min) / (yr_max - yr_min) * 100
        a_width = (last_yr - first_yr) / (yr_max - yr_min) * 100
        m_left = (last_yr - yr_min) / (yr_max - yr_min) * 100
        m_width = 100 - m_left

        # Map family to Hebrew name
        family_he = {
            "CVOC": "תרכובות אורגניות",
            "METALS": "מתכות כבדות",
            "PFAS": "כימיקלים מעמידים",
            "FUEL": "דלקים"
        }.get(family, family)

        rows.append(f'<div class="nm">{esc(nm)}<small>{family_he} · אינדקס {max_idx}</small></div>')
        rows.append(
            f'<div class="gap-bar">'
            f'<div class="a" style="left:{a_left:.1f}%;width:{a_width:.1f}%"></div>'
            f'<div class="m" style="left:{m_left:.1f}%;width:{m_width:.1f}%"></div>'
            f'</div>'
        )
        rows.append(f'<div class="last">{last_yr}</div>')

    rows.append('</div>')
    return "".join(rows)


def svg_borehole_classification_table(classification: pd.DataFrame, classification_intro: str = "") -> str:
    """Generate HTML table of borehole classification statistics (2021-2026).

    Summarizes all 85 boreholes with recent data by classification level.
    If classification_intro provided, includes definitions from V4 report.
    """
    if classification.empty:
        return '<div style="padding:20px;color:#6b6b6b;text-align:center">אין נתוני סיווג זמינים</div>'

    # Summary statistics
    total = len(classification)
    alert_count = len(classification[classification['classification'] == 'ALERT'])
    watch_count = len(classification[classification['classification'] == 'WATCH'])
    elevated_count = len(classification[classification['classification'] == 'ELEVATED'])
    stable_count = len(classification[classification['classification'] == 'STABLE'])
    none_count = len(classification[classification['classification'] == 'NONE'])

    # Family statistics
    cvoc_boreholes = len(classification[classification['families'].str.contains('CVOC', na=False)])
    metals_boreholes = len(classification[classification['families'].str.contains('METALS', na=False)])
    fuel_boreholes = len(classification[classification['families'].str.contains('FUEL', na=False)])

    rows = []
    rows.append('<div class="classification-table">')
    rows.append('<div class="section-title">סיווג קידוחים (בסיס 2021–2026)</div>')

    # Include definitions from V4 if available
    if classification_intro:
        rows.append('<div class="classification-intro" style="font-size:13px;margin-bottom:16px;color:#3a3a3a;line-height:1.6">')
        rows.append(classification_intro)
        rows.append('</div>')

    rows.append('<div class="summary-grid">')
    rows.append('<div class="stat-item">')
    rows.append(f'<div class="stat-label">סה"כ קידוחים</div>')
    rows.append(f'<div class="stat-value">{total}</div>')
    rows.append('</div>')

    rows.append('<div class="stat-item alert">')
    rows.append(f'<div class="stat-label">ALERT</div>')
    rows.append(f'<div class="stat-value">{alert_count}</div>')
    rows.append('</div>')

    rows.append('<div class="stat-item watch">')
    rows.append(f'<div class="stat-label">WATCH</div>')
    rows.append(f'<div class="stat-value">{watch_count}</div>')
    rows.append('</div>')

    rows.append('<div class="stat-item">')
    rows.append(f'<div class="stat-label">ELEVATED</div>')
    rows.append(f'<div class="stat-value">{elevated_count}</div>')
    rows.append('</div>')

    rows.append('<div class="stat-item">')
    rows.append(f'<div class="stat-label">STABLE</div>')
    rows.append(f'<div class="stat-value">{stable_count}</div>')
    rows.append('</div>')

    rows.append('<div class="stat-item">')
    rows.append(f'<div class="stat-label">NONE</div>')
    rows.append(f'<div class="stat-value">{none_count}</div>')
    rows.append('</div>')
    rows.append('</div>')

    rows.append('<div class="family-stats">')
    rows.append(f'<div class="family-item">תרכובות אורגניות (CVOC): {cvoc_boreholes} קידוחים</div>')
    rows.append(f'<div class="family-item">מתכות כבדות (METALS): {metals_boreholes} קידוחים</div>')
    rows.append(f'<div class="family-item">דלקים (FUEL): {fuel_boreholes} קידוחים</div>')
    rows.append('</div>')

    rows.append('</div>')
    return "".join(rows)


def svg_borehole_map_html(classification: pd.DataFrame,
                          zone_polygon: list | None = None) -> str:
    """Generate SVG map showing borehole locations colored by severity bucket.

    Uses ITM coordinates (בקואורדינטות ITM) in meters.
    Calculates bounds dynamically from data to support any zone.
    Optionally draws the zone polygon boundary (ITM meters list of [east, north]).
    Labels shown for high-severity wells (≥6).
    """
    if classification.empty:
        return '<div style="padding:20px;color:#6b6b6b;text-align:center">אין נתוני קידוחים זמינים</div>'

    # Calculate ITM bounds dynamically from actual data (in meters)
    valid_coords = classification[
        (pd.notna(classification['east_itm'])) &
        (pd.notna(classification['north_itm']))
    ]

    if valid_coords.empty:
        return '<div style="padding:20px;color:#6b6b6b;text-align:center">אין נתוני קידוחים עם קואורדינטות</div>'

    # Get data bounds, extended to include polygon vertices if provided
    all_east = list(valid_coords['east_itm'])
    all_north = list(valid_coords['north_itm'])
    if zone_polygon:
        all_east += [pt[0] for pt in zone_polygon]
        all_north += [pt[1] for pt in zone_polygon]

    data_east_min, data_east_max = min(all_east), max(all_east)
    data_north_min, data_north_max = min(all_north), max(all_north)

    # Add 7% margin around data
    east_margin = (data_east_max - data_east_min) * 0.07
    north_margin = (data_north_max - data_north_min) * 0.07

    east_min = data_east_min - east_margin
    east_max = data_east_max + east_margin
    north_min = data_north_min - north_margin
    north_max = data_north_max + north_margin

    # SVG dimensions
    svg_width, svg_height = 800, 600
    padding = 60
    plot_width = svg_width - 2 * padding
    plot_height = svg_height - 2 * padding

    def to_svg(east_m, north_m):
        """Convert ITM meters to SVG pixel coordinates."""
        x = padding + (east_m - east_min) / (east_max - east_min) * plot_width
        y = svg_height - padding - (north_m - north_min) / (north_max - north_min) * plot_height
        return x, y

    # Color mapping for severity buckets
    color_map = {
        0: GREY_1, 1: GREY_2, 2: GREY_2,
        3: GREY_3, 4: GREY_3,
        5: INK_2, 6: INK,
        7: RED_SOFT, 8: RED,
    }

    lines = []
    lines.append(f'<svg viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">')

    # Background: light map color (like a standard topographic base)
    lines.append(f'<rect width="{svg_width}" height="{svg_height}" fill="{PAPER}"/>')

    # Plot area: slightly off-white base (open area / unbuilt land tone)
    lines.append(f'<rect x="{padding}" y="{padding}" width="{plot_width}" height="{plot_height}" '
                f'fill="#eee9e0" stroke="none"/>')

    # KM grid lines (every 500m)
    east_start = int((east_min / 500 + 1)) * 500
    north_start = int((north_min / 500 + 1)) * 500
    for eg in range(east_start, int(east_max) + 500, 500):
        gx, _ = to_svg(eg, north_min)
        lines.append(f'<line x1="{gx:.1f}" y1="{padding}" x2="{gx:.1f}" y2="{svg_height-padding}" '
                    f'stroke="#d0ccc4" stroke-width="0.6" stroke-dasharray="3,4"/>')
    for ng in range(north_start, int(north_max) + 500, 500):
        _, gy = to_svg(east_min, ng)
        lines.append(f'<line x1="{padding}" y1="{gy:.1f}" x2="{svg_width-padding}" y2="{gy:.1f}" '
                    f'stroke="#d0ccc4" stroke-width="0.6" stroke-dasharray="3,4"/>')

    # Zone polygon (industrial area boundary from zone_polygons.json)
    if zone_polygon and len(zone_polygon) >= 3:
        pts = [to_svg(pt[0], pt[1]) for pt in zone_polygon]
        poly_pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        lines.append(f'<polygon points="{poly_pts}" '
                    f'fill="#dde8d8" fill-opacity="0.55" '
                    f'stroke="#6a9a64" stroke-width="1.8" stroke-dasharray="6,3" stroke-linejoin="round"/>')
        # Label the polygon
        cx = sum(p[0] for p in pts) / len(pts)
        cy = min(p[1] for p in pts) - 8
        lines.append(f'<text x="{cx:.0f}" y="{cy:.0f}" text-anchor="middle" '
                    f'font-size="9" fill="#4a7a44" font-style="italic" direction="rtl" unicode-bidi="isolate">'
                    f'גבולות אזה"ת</text>')

    # Outer border of plot area
    lines.append(f'<rect x="{padding}" y="{padding}" width="{plot_width}" height="{plot_height}" '
                f'fill="none" stroke="{RULE_LIGHT}" stroke-width="1.2"/>')

    # CSS styles
    lines.append('<style>')
    lines.append('.label { font-size: 8px; fill: #1a1a1a; pointer-events: none; }')
    lines.append('.label-bg { fill: white; fill-opacity: 0.92; stroke: #d8d3c8; stroke-width: 0.4; }')
    lines.append('.borehole:hover { r: 7; }')
    lines.append('</style>')

    # ITM coordinate ticks (smart intervals based on data range)
    # For east-west (meters): show every 500m or 1000m depending on range
    east_range = east_max - east_min
    east_interval = 1000 if east_range > 5000 else 500
    east_start = int((east_min / east_interval) + 0.5) * east_interval

    for east in range(east_start, int(east_max) + east_interval, east_interval):
        x = padding + (east - east_min) / (east_max - east_min) * plot_width
        lines.append(f'<line x1="{x}" y1="{svg_height-padding}" x2="{x}" y2="{svg_height-padding+5}" stroke="{INK}" stroke-width="1"/>')
        lines.append(f'<text x="{x}" y="{svg_height-padding+18}" text-anchor="middle" font-size="9" fill="{SOFT}">{east/1000:.1f}</text>')

    # For north-south (meters): similar logic
    north_range = north_max - north_min
    north_interval = 1000 if north_range > 5000 else 500
    north_start = int((north_min / north_interval) + 0.5) * north_interval

    for north in range(north_start, int(north_max) + north_interval, north_interval):
        y = svg_height - padding - (north - north_min) / (north_max - north_min) * plot_height
        lines.append(f'<line x1="{padding}" y1="{y}" x2="{padding-5}" y2="{y}" stroke="{INK}" stroke-width="1"/>')
        lines.append(f'<text x="{padding-8}" y="{y+3}" text-anchor="end" font-size="9" fill="{SOFT}">{north/1000:.1f}</text>')

    # Plot border (axes)
    lines.append(f'<line x1="{padding}" y1="{svg_height-padding}" x2="{svg_width-padding}" y2="{svg_height-padding}" stroke="{INK}" stroke-width="1.5"/>')
    lines.append(f'<line x1="{padding}" y1="{padding}" x2="{padding}" y2="{svg_height-padding}" stroke="{INK}" stroke-width="1.5"/>')

    # Sort by severity (low first) so high-severity dots render on top
    sorted_classification = classification.sort_values('severity_bucket', ascending=True)

    # First pass: draw all dots
    points = []
    for _, row in sorted_classification.iterrows():
        if pd.notna(row['east_itm']) and pd.notna(row['north_itm']):
            x, y = to_svg(row['east_itm'], row['north_itm'])

            bucket = int(row['severity_bucket'])
            color = color_map.get(bucket, GREY_3)
            radius = 5 if bucket >= 5 else 3.5

            name = row.get('borehole_name', '') or ''
            points.append({'x': x, 'y': y, 'color': color, 'radius': radius,
                          'bucket': bucket, 'name': str(name)})

            lines.append(f'<circle class="borehole" cx="{x:.1f}" cy="{y:.1f}" r="{radius}" '
                        f'fill="{color}" stroke="{INK}" stroke-width="0.7"/>')
            lines.append(f'<title>{esc(str(name))} (אינדקס {bucket})</title>')

    # Second pass: labels ONLY for high-severity (≥6) to avoid clutter
    # Use simple anti-overlap: track placed label rectangles
    placed_labels = []
    high_severity_points = sorted([p for p in points if p['bucket'] >= 6],
                                   key=lambda p: -p['bucket'])

    char_w = 6.0   # Hebrew glyph width at 8px font (wider than Latin)
    pad_x = 4.0    # horizontal padding inside the white box
    text_height = 12

    label_draw = []  # defer drawing so all labels sit above all dots/boxes
    for p in high_severity_points:
        name = p['name']
        if not name:
            continue

        text_width = len(name) * char_w
        box_w = text_width + 2 * pad_x
        half_w = box_w / 2

        # Candidate CENTER positions for the label box relative to the dot.
        # Using a center anchor makes geometry direction-independent (RTL-safe).
        for off_x, off_y in [(half_w + 6, -10), (-half_w - 6, -10),
                             (half_w + 6, 12), (-half_w - 6, 12),
                             (half_w + 10, 1), (-half_w - 10, 1),
                             (half_w + 6, -24), (-half_w - 6, -24)]:
            cx = p['x'] + off_x
            cy = p['y'] + off_y

            box = (cx - half_w, cy - text_height + 2, cx + half_w, cy + 3)

            # Reject if outside plot area
            if (box[0] < padding or box[2] > svg_width - padding or
                    box[1] < padding or box[3] > svg_height - padding):
                continue

            # Reject if overlapping an already-placed label
            if any(not (box[2] < q[0] or box[0] > q[2] or
                        box[3] < q[1] or box[1] > q[3]) for q in placed_labels):
                continue

            placed_labels.append(box)
            label_draw.append((p['x'], p['y'], cx, cy, box, name))
            break

    # Leader lines first (under boxes)
    for bx, by, cx, cy, box, name in label_draw:
        # connect dot to the nearest horizontal edge of its label box
        edge_x = box[0] if cx > bx else box[2]
        lines.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{edge_x:.1f}" y2="{cy-3:.1f}" '
                    f'stroke="#999" stroke-width="0.5" opacity="0.7"/>')
    # Boxes + text on top (center-anchored: RTL-safe)
    for bx, by, cx, cy, box, name in label_draw:
        lines.append(f'<rect class="label-bg" x="{box[0]:.1f}" y="{box[1]:.1f}" '
                    f'width="{box[2]-box[0]:.1f}" height="{box[3]-box[1]:.1f}" rx="1.5"/>')
        lines.append(f'<text class="label" x="{cx:.1f}" y="{cy:.1f}" '
                    f'text-anchor="middle" direction="rtl" unicode-bidi="isolate">{esc(name)}</text>')

    # Axis labels
    lines.append(f'<text x="{svg_width/2}" y="{svg_height-15}" text-anchor="middle" direction="rtl" unicode-bidi="isolate" font-size="11" fill="{INK}">מזרח (ITM, ק"מ)</text>')
    lines.append(f'<text x="20" y="{svg_height/2}" text-anchor="middle" direction="rtl" unicode-bidi="isolate" font-size="11" fill="{INK}" transform="rotate(-90 20 {svg_height/2})">צפון (ITM, ק"מ)</text>')

    # Title
    lines.append(f'<text x="{svg_width/2}" y="30" text-anchor="middle" direction="rtl" unicode-bidi="isolate" font-size="14" font-weight="bold" fill="{INK}">מיקומי קידוחים — אזה"ת חולון</text>')
    lines.append(f'<text x="{svg_width/2}" y="46" text-anchor="middle" direction="rtl" unicode-bidi="isolate" font-size="10" fill="{SOFT}">צבע לפי אינדקס חומרה (0–8) · תוויות לקידוחים באינדקס ≥6</text>')

    # Legend (bottom-right, compact)
    legend_x = svg_width - padding - 130
    legend_y = svg_height - padding - 110
    lines.append(f'<rect x="{legend_x}" y="{legend_y}" width="120" height="100" fill="white" stroke="{RULE_LIGHT}" stroke-width="0.8" opacity="0.95"/>')
    lines.append(f'<text x="{legend_x+115}" y="{legend_y+14}" text-anchor="end" direction="rtl" unicode-bidi="isolate" font-size="10" font-weight="bold" fill="{INK}">אינדקס חומרה</text>')

    legend_items = [
        (RED, 8, "8 — חמור מאוד"),
        (RED_SOFT, 7, "7 — חמור"),
        (INK, 6, "6 — גבוה"),
        (INK_2, 5, "5 — בינוני-גבוה"),
        (GREY_3, 3, "3–4 — בינוני"),
        (GREY_2, 1, "0–2 — נמוך"),
    ]

    for i, (color, bucket, label) in enumerate(legend_items):
        ly = legend_y + 26 + i * 12
        radius = 4 if bucket >= 5 else 2.5
        lines.append(f'<circle cx="{legend_x+108}" cy="{ly}" r="{radius}" fill="{color}" stroke="{INK}" stroke-width="0.5"/>')
        lines.append(f'<text x="{legend_x+100}" y="{ly+3}" text-anchor="end" direction="rtl" unicode-bidi="isolate" font-size="9" fill="{INK}">{label}</text>')

    lines.append('</svg>')

    return "".join(lines)


# ───────────────────────── Figure 7: Recommendations table ─────────────────────────

def html_recommendations_table() -> str:
    """Hardcoded recommendations from V4 §8."""
    return (
        '<table class="rec">'
        '<thead><tr>'
        '<th>תיעדוף</th><th>פעולה</th><th>אזור / קידוח</th><th>אופק</th>'
        '</tr></thead>'
        '<tbody>'
        '<tr class="cat"><td colspan="4">קטגוריה א — דחיפות מיידית <span class="n">תוך 6 חודשים</span></td></tr>'
        '<tr><td class="tier urg">דחוף</td>'
        '<td class="action"><b>חידוש ניטור</b> בקידוחים שהופסקו</td>'
        '<td>נת חולון 2, נד המרכבה ק2</td><td class="cost">Q3 2026</td></tr>'
        '<tr><td class="tier urg">דחוף</td>'
        '<td class="action"><b>דיגום אישוש</b> מוקד הכרום</td>'
        '<td>נת חולון 26 (Cr 4,036 µg/L)</td><td class="cost">Q3 2026</td></tr>'
        '<tr><td class="tier urg">דחוף</td>'
        '<td class="action"><b>ניטור חצי-שנתי</b> בקידוח הפקה (CVOC)</td>'
        '<td>מק חולון 14 (88.5% מהתקן)</td><td class="cost">Q3 2026</td></tr>'
        '<tr class="cat"><td colspan="4">קטגוריה ב — בירור הנדסי <span class="n">תוך 12 חודשים</span></td></tr>'
        '<tr><td class="tier">חשוב</td>'
        '<td class="action">בדיקת יעילות EBR® במתחם אגד (לאחר 180 יום)</td>'
        '<td>19 קידוחי מתחם אגד</td><td class="cost">פברואר 2026</td></tr>'
        '<tr><td class="tier">חשוב</td>'
        '<td class="action">בירור מקור DNAPL בעומק (סונול המלאכה)</td>'
        '<td>מ-1, ק-1 — TCE 2,722 µg/L</td><td class="cost">2026</td></tr>'
        '<tr class="cat"><td colspan="4">קטגוריה ג — שיקום ארוך-טווח <span class="n">2027+</span></td></tr>'
        '<tr><td class="tier">תכנון</td>'
        '<td class="action">שיקום ממוקד למוקד הכרום המזרחי</td>'
        '<td>נת חולון 14, 26</td><td class="cost">2027</td></tr>'
        '<tr><td class="tier">תכנון</td>'
        '<td class="action">מודל הסעה מעודכן לאזור התעשייה</td>'
        '<td>כל האזור</td><td class="cost">2027</td></tr>'
        '</tbody></table>'
    )
