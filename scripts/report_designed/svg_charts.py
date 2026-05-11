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
    """Build the F1 ledger: 3 family panels (CVOC/INDUSTRY, METALS, FUEL as appendix).

    Returns inner HTML for .ledger container (used in template).
    """
    # Family aggregations
    industry = severity[severity.family == "INDUSTRY"].sort_values("contributing_pct", ascending=False)
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
    """Build the F2 severity matrix: rows=boreholes, cols=families."""
    # Pivot severity to wide form
    pivot = severity.pivot_table(
        index=["borehole", "name_he"],
        columns="family",
        values="max_bucket",
        aggfunc="max",
    ).reset_index()

    pivot.columns.name = None
    for col in ["INDUSTRY", "METALS", "FUEL"]:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot[["INDUSTRY", "METALS", "FUEL"]] = pivot[["INDUSTRY", "METALS", "FUEL"]].fillna(0)

    pivot["max_bucket"] = pivot[["INDUSTRY", "METALS", "FUEL"]].max(axis=1)
    pivot = pivot.sort_values("max_bucket", ascending=False)

    # Compute INCREASING markers from trends
    inc_set = set()
    if not trends.empty:
        inc = trends[trends.classification == "INCREASING"]
        for _, r in inc.iterrows():
            inc_set.add(r.borehole_id)

    # Compute stopped monitoring set from data_avail
    stopped = set()
    if not data_avail.empty:
        agg = (data_avail.groupby("borehole")["last_year"].max().reset_index())
        for _, r in agg.iterrows():
            if r.last_year < 2023:
                stopped.add(r.borehole)

    rows = []
    for _, r in pivot.iterrows():
        bid = r.borehole
        nm = r.name_he
        mark_inc = ' <span class="up">↑</span>' if bid in inc_set else ""
        mark_stop = ' <span style="color:var(--red);font-weight:700">●</span>' if bid in stopped else ""
        rows.append(
            f'<tr>'
            f'<td class="lbl">{esc(nm)}{mark_inc}{mark_stop}</td>'
            f'<td class="val">{_bucket_cell(int(r.INDUSTRY))}</td>'
            f'<td class="val">{_bucket_cell(int(r.METALS))}</td>'
            f'<td class="val">{_bucket_cell(int(r.FUEL))}</td>'
            f'</tr>'
        )

    return (
        '<table class="matrix">'
        '<thead><tr>'
        '<th>קידוח</th><th>CVOC</th><th>מתכות</th><th>דלקים</th>'
        '</tr></thead>'
        '<tbody>' + "".join(rows) + '</tbody>'
        '</table>'
    )


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

def svg_cvoc_panels(measurements: pd.DataFrame, severity: pd.DataFrame) -> str:
    """6 CVOC time-series panels for the top INDUSTRY wells."""
    industry = severity[severity.family == "INDUSTRY"].sort_values("max_bucket", ascending=False)
    top_wells = industry.head(6)["borehole"].tolist()

    panels = []
    for wid in top_wells:
        nm = severity[severity.borehole == wid].iloc[0].name_he
        well_data = measurements[
            (measurements.canonical_id == wid) &
            (measurements.param_code.isin(["TRICHLORO ETHYLENE", "TETRACHLORO ETHYLENE",
                                            "CIS 1,2 DICHLOROETHYLENE"]))
        ].copy()
        if well_data.empty:
            continue
        panels.append(_time_series_panel(well_data, nm, dws=7.5, width=240, height=140))

    if not panels:
        return f'<div style="padding:30px;color:{SOFT};text-align:center">אין נתוני CVOC</div>'

    return _small_multiples_grid(panels, cols=3)


# ───────────────────────── Figure 4: Chromium time series ─────────────────────────

def svg_chromium_panels(measurements: pd.DataFrame) -> str:
    """Chromium time-series panels."""
    cr_data = measurements[measurements.param_code == "CHROMIUM AS CR"].copy()
    if cr_data.empty:
        return f'<div style="padding:30px;color:{SOFT};text-align:center">אין נתוני כרום</div>'

    wells = cr_data.canonical_id.unique()
    panels = []
    for wid in wells[:4]:
        nm = cr_data[cr_data.canonical_id == wid].iloc[0].name_he
        well_data = cr_data[cr_data.canonical_id == wid].copy()
        if len(well_data) < 1:
            continue
        panels.append(_time_series_panel(well_data, nm, dws=50.0, width=340, height=180))

    if not panels:
        return f'<div style="padding:30px;color:{SOFT};text-align:center">אין נתוני כרום</div>'

    return _small_multiples_grid(panels, cols=2)


# ───────────────────────── Figure 5: BTEX panels ─────────────────────────

def svg_btex_panels(measurements: pd.DataFrame) -> str:
    """BTEX (Benzene, MTBE) time-series for top Egged/fuel wells."""
    fuel_data = measurements[measurements.param_code.isin(["BENZENE", " MTBE", "MTBE"])].copy()
    if fuel_data.empty:
        return f'<div style="padding:30px;color:{SOFT};text-align:center">אין נתוני BTEX</div>'

    # Top 6 wells by max concentration
    well_max = fuel_data.groupby("canonical_id").concentration.max().sort_values(ascending=False)
    top_wells = well_max.head(6).index.tolist()

    panels = []
    for wid in top_wells:
        nm = fuel_data[fuel_data.canonical_id == wid].iloc[0].name_he
        well_data = fuel_data[fuel_data.canonical_id == wid].copy()
        panels.append(_time_series_panel(well_data, nm, dws=5.0, width=240, height=140))

    return _small_multiples_grid(panels, cols=3)


# ───────────────────────── Internal: time-series panel ─────────────────────────

def _time_series_panel(well_data: pd.DataFrame, name_he: str, dws: float,
                        width: int = 240, height: int = 140) -> str:
    """One SVG time-series panel: log Y, linear X (year), DWS dashed red line."""
    well_data = well_data.copy()
    well_data["year"] = pd.to_datetime(well_data["date"]).dt.year

    # Plot area
    pad_l, pad_r, pad_t, pad_b = 32, 8, 18, 22
    x_left = pad_l
    x_right = width - pad_r
    y_top = pad_t
    y_bot = height - pad_b

    y_min_year = 2010
    y_max_year = 2026
    c_min = 0.1
    c_max = max(well_data.concentration.max() * 1.2, dws * 5)

    # Draw grid + axes + DWS line
    parts = [f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">']

    # Year gridlines
    for yr in [2012, 2016, 2020, 2024]:
        x = linear_x(yr, y_min_year, y_max_year, x_left, x_right)
        parts.append(f'<line x1="{x:.1f}" y1="{y_top}" x2="{x:.1f}" y2="{y_bot}" '
                     f'stroke="{RULE_LIGHT}" stroke-width="0.4"/>')
        parts.append(f'<text x="{x:.1f}" y="{height - 4}" '
                     f'font-family="IBM Plex Mono,monospace" font-size="8.5" '
                     f'text-anchor="middle" fill="{SOFT}">{yr}</text>')

    # Log-scale gridlines (1, 10, 100, 1000)
    for c in [1, 10, 100, 1000, 10000]:
        if c > c_max: break
        y = log_y(c, c_min, c_max, y_top, y_bot)
        parts.append(f'<line x1="{x_left}" y1="{y:.1f}" x2="{x_right}" y2="{y:.1f}" '
                     f'stroke="{RULE_LIGHT}" stroke-width="0.4"/>')
        parts.append(f'<text x="{x_left - 4}" y="{y + 3:.1f}" '
                     f'font-family="IBM Plex Mono,monospace" font-size="8" '
                     f'text-anchor="end" fill="{SOFT}">{c}</text>')

    # DWS line (red dashed)
    if dws <= c_max:
        y_dws = log_y(dws, c_min, c_max, y_top, y_bot)
        parts.append(f'<line x1="{x_left}" y1="{y_dws:.1f}" x2="{x_right}" y2="{y_dws:.1f}" '
                     f'stroke="{RED}" stroke-width="1" stroke-dasharray="3 2"/>')

    # Axes
    parts.append(f'<line x1="{x_left}" y1="{y_top}" x2="{x_left}" y2="{y_bot}" '
                 f'stroke="{INK}" stroke-width="1"/>')
    parts.append(f'<line x1="{x_left}" y1="{y_bot}" x2="{x_right}" y2="{y_bot}" '
                 f'stroke="{INK}" stroke-width="1"/>')

    # Data: connect by parameter
    for param, grp in well_data.groupby("param_code"):
        grp = grp.sort_values("year")
        pts = []
        for _, r in grp.iterrows():
            if r.concentration <= 0:
                continue
            x = linear_x(r.year, y_min_year, y_max_year, x_left, x_right)
            y = log_y(r.concentration, c_min, c_max, y_top, y_bot)
            pts.append(f"{x:.1f},{y:.1f}")
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="{INK}"/>')
        if len(pts) >= 2:
            parts.append(f'<polyline points="{" ".join(pts)}" '
                         f'fill="none" stroke="{INK}" stroke-width="1.2"/>')

    # Title (well name)
    parts.append(f'<text x="{x_left}" y="14" font-family="Source Sans 3,sans-serif" '
                 f'font-size="10.5" font-weight="600" fill="{INK}">{esc(name_he)}</text>')

    parts.append('</svg>')
    return "".join(parts)


def _small_multiples_grid(panels: list, cols: int = 3) -> str:
    """Wrap SVG panels in a CSS grid."""
    cells = [f'<div>{p}</div>' for p in panels]
    return (
        f'<div style="display:grid;grid-template-columns:repeat({cols},1fr);'
        f'gap:1px;background:{RULE_LIGHT};border:1px solid {INK}">'
        + "".join(f'<div style="background:{PAPER};padding:6px">{c}</div>' for c in cells)
        + '</div>'
    )


# ───────────────────────── Figure 6: Monitoring gaps timeline ─────────────────────────

def svg_monitoring_gaps(data_avail: pd.DataFrame, severity: pd.DataFrame) -> str:
    """Timeline showing monitoring gaps for ALERT wells with stopped monitoring."""
    if data_avail.empty:
        return f'<div style="padding:30px;color:{SOFT};text-align:center">אין נתוני זמינות</div>'

    # Aggregate per borehole: first_year, last_year
    agg = data_avail.groupby(["borehole", "name_he"]).agg(
        first_year=("first_sample_date", lambda x: pd.to_datetime(x).dt.year.min()),
        last_year=("last_sample_date", lambda x: pd.to_datetime(x).dt.year.max()),
    ).reset_index()

    # Filter: only wells in severity that stopped before 2023
    alert_set = set(severity.borehole.unique())
    stopped = agg[(agg.borehole.isin(alert_set)) & (agg.last_year < 2023)].sort_values("last_year")

    if stopped.empty:
        return '<div style="padding:20px;color:#6b6b6b;text-align:center">אין הפסקות ניטור בקידוחי ALERT</div>'

    yr_min, yr_max = 2010, 2026
    rows = []
    rows.append('<div class="gap-grid">')
    rows.append('<div class="hd">קידוח</div>')
    rows.append('<div class="hd">קו זמן 2010–2026</div>')
    rows.append('<div class="hd">דיגום אחרון</div>')

    for _, r in stopped.iterrows():
        bid = r.borehole
        nm = r.name_he
        first_yr = int(r.first_year)
        last_yr = int(r.last_year)
        a_left = (first_yr - yr_min) / (yr_max - yr_min) * 100
        a_width = (last_yr - first_yr) / (yr_max - yr_min) * 100
        m_left = (last_yr - yr_min) / (yr_max - yr_min) * 100
        m_width = 100 - m_left

        rows.append(f'<div class="nm">{esc(nm)}<small>{esc(bid)}</small></div>')
        rows.append(
            f'<div class="gap-bar">'
            f'<div class="a" style="left:{a_left:.1f}%;width:{a_width:.1f}%"></div>'
            f'<div class="m" style="left:{m_left:.1f}%;width:{m_width:.1f}%"></div>'
            f'</div>'
        )
        rows.append(f'<div class="last">{last_yr}</div>')

    rows.append('</div>')
    return "".join(rows)


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
