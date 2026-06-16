# CHART_SPEC.md — יציבות וחוזה גרפים לדוחות אזורי תעשייה

**Purpose**: Stabilise chart file names, define content invariants, and specify colour palettes so changes to functions don't break report references.

**Scope**:
- **Zone-specific charts** (Raanana reference implementation): 9 hand-tuned charts in this inventory — fixed file names, fixed borehole IDs, fixed parameter ordering. Used by `RAANANA_REPORT_V2.md`.
- **Generic data-driven charts** (any other zone): produced by `chart_generic_*` functions in `generate_charts_v2.py`. File names: `cvoc_trends.png`, `btex_trends.png`, `pfas_trends.png`, `exceedances_bar.png`, `severity_panel.png`, `zone_site_map.png`. Top boreholes are auto-selected from data using `scripts/param_families.py` classifier.

The chart inventory below documents the **Raanana reference set** as the canonical example. Adapt naming conventions and ordering when implementing zone-specific hand-tuned charts for other zones (after expert review confirms the generic charts are insufficient).

---

## Chart Inventory (10 charts)

| ID | File Name (STABLE) | Function | Content | Data Source | Invariants |
|---|---|---|---|---|---|
| **0** | **`zone_site_map.png`** | **`chart_zone_site_map()`** *(TO BE IMPLEMENTED)* | **CENTRAL FIGURE: Zone aerial map with boreholes (symbology by max contamination index), facility markers, and groundwater flow direction arrow** | **Excel measurements + `Raanana/data/boreholes.csv` + `Raanana/data/industries.json` + `zone_definitions/zone_polygons.json`** | **Per Section X below — modeled on 2021 report Map B (איור 29 in 2021 report)** |
| 1 | `cvoc_timeseries.png` | `chart_cvoc_timeseries()` | TCE at nt_1, nt_2; PCE at nt_3 (2012–2025) | Excel measurements | Time-series curves only; RTL labels; standard threshold line (TCE 7.5, PCE 10.0 µg/L) |
| ~~2~~ | ~~`pfas_all_boreholes.png`~~ | ~~`chart_pfas_all_boreholes()`~~ | ~~PFAS stacked bar per borehole (S/A groups)~~ | ~~Excel measurements~~ | **❌ DEPRECATED 2026-05-05** — Single measurement point only (nd_turbine July 2025); no time-series data; PFAS signature analysis retained in narrative text only |
| 3 | `btex_timeseries_paz.png` | `chart_btex_timeseries()` | Benzene at nd_paz (2011–2024) | Excel measurements | Time-series curve; RTL labels; standard threshold line (BENZENE 5.0 µg/L) |
| ~~4~~ | ~~`cvoc_cross_borehole.png`~~ | ~~`chart_cvoc_cross_borehole()`~~ | ~~Max annual TCE/PCE across boreholes~~ | ~~Excel measurements~~ | **❌ DEPRECATED 2026-05-05** — redundant with cvoc_pct_standard_panel + cvoc_all_wells; removed from report and inventory |
| 5 | `tce_timeseries_p25.png` | `chart_tce_p25()` | TCE at p_25 production well (2023–2025 exceedance detail) | Excel measurements | Time-series curve; detail view; standard threshold line (7.5 µg/L); RTL labels |
| 6 | `cvoc_all_wells.png` | `chart_cvoc_all_wells()` | CVOC curves for all 4 boreholes: TCE panel + PCE panel | Excel measurements | Pure time-series curves only (never bars); side-by-side panels; RTL labels |
| ~~7~~ | ~~`pfas_pct_stacked.png`~~ | ~~`chart_pfas_pct_stacked()`~~ | ~~100%-stacked PFAS at nd_turbine (source-signature AFFF validation)~~ | ~~Excel measurements~~ | **❌ DEPRECATED 2026-05-05** — Single measurement (July 2025); PFAS S/A signature analysis in narrative text only |
| ~~8~~ | ~~`btex_family_stacked.png`~~ | ~~`chart_btex_family_stacked()`~~ | ~~BTEX full family time-series at nd_paz~~ | ~~Excel measurements~~ | **❌ DEPRECATED 2026-05-05** — Redundant with btex_timeseries_paz (benzene is main BTEX finding); no new information from toluene/xylenes |
| 9 | `cvoc_pct_standard_panel.png` | `chart_cvoc_pct_standard_panel()` | 4-borehole panel: % of drinking water standard (TCE/PCE) over time | Excel measurements | Y-axis as % of standard; 4 subplots (nt_1, nt_2, nt_3, p_25); RTL labels |

---

## Section X: Central Map Figure — `zone_site_map.png` (PRIMARY FIGURE)

### Purpose
Replicate the 2021 Water Authority report's **per-zone Map B** (e.g., איור 29 for Raanana, page 36) — the canonical spatial overview of any industrial zone.

### Required Visual Elements

#### 1. Background
- **Aerial photograph** of the zone area (extracted from satellite imagery / OSM tiles / similar)
- **ITM coordinates** displayed on axes (Israel Transverse Mercator)
- **Scale bar** (typically 250–500 m increments)

#### 2. Zone Polygon
- **Red boundary line** (~2pt thick) following the official zone polygon
- Source: `zone_definitions/zone_polygons.json` for Raanana
- Label "אזור תעשייה רעננה" centered inside polygon (red text)

#### 3. Boreholes — Symbology by Max Contamination Index
Each borehole appears as a **colored circle** with **borehole label** (Hebrew name).

**Color scale** (per 2021 report, Index column on page 7):
| Max Index | Color | RGB / Hex | Meaning |
|---|---|---|---|
| 0 | Light gray | `#BDBDBD` | No contamination detected |
| 1–3 | Light green | `#81C784` | Low |
| 4 | Light orange | `#FFB74D` | Medium |
| 5 | Orange | `#FB8C00` | Medium-high |
| 6 | Bordo (dark red) | `#C62828` | High |
| 7 | Dark bordo | `#8E0000` | Very high |
| 8 | Black-bordo | `#4A0000` | Extreme |

**Marker**:
- Circle radius proportional to severity (small for index 0–3, larger for 6–8)
- Border: black `#000000`, 0.5pt
- Label: Hebrew borehole name positioned with offset (so it doesn't overlap marker)
- Index value as numeric label inside or beside marker (per 2021 style)

**For Raanana (7 boreholes)**:
| Borehole | Max Index | Color | Source |
|---|---|---|---|
| נת רעננה 1 | 7 | `#8E0000` | Excel: max TCE 817 µg/L |
| נת רעננה 2 | 4 | `#FFB74D` | Excel: max TCE 24 µg/L |
| נת רעננה 3 | 7 | `#8E0000` | Excel: max PCE 105.5 µg/L |
| נד פז הנופר | 4 | `#FFB74D` | Excel: max benzene 10 µg/L |
| נד תחנת טורבינות גז | 8 | `#4A0000` | Excel: PFHxS 1.16 µg/L (1,160% of standard) |
| פ רעננה 18 | 0 | `#BDBDBD` | No recent data |
| פ רעננה 25 | 5 | `#FB8C00` | Excel: max TCE 14.1 µg/L |

#### 4. Facility Markers (Pollution Source Candidates)
Industrial facilities and gas stations marked per 2021 report symbology:

| Type | Marker | Color | Source File |
|---|---|---|---|
| Industrial facility | Triangle (▲) | Purple `#7B1FA2` | `Raanana/data/industries.json` |
| Gas station | Square (■) | Blue `#1565C0` | `Raanana/data/industries.json` |

**For Raanana (5 sources)**:
- אידכים (כימיקלים) — triangle, purple, label "אידכים"
- אדג' מדיקל דוויסס — triangle, purple, label "אדג' מדיקל"
- אביב ריצ'רדסון — triangle, purple, label "אביב ריצ'רדסון"
- תחנת טורבינות גז (חברת החשמל) — triangle, purple, label "תחנת טורבינות גז"
- תחנת דלק פז הנופר — square, blue, label "פז הנופר"

#### 5. Groundwater Flow Direction Arrow
- **Large directional arrow** (length ~150 m at scale, prominent)
- Direction: **NW–W** for Raanana (per 2021 report, page 35)
- Color: dark blue `#0D47A1`
- Label adjacent: "כיוון זרימת מי התהום" (groundwater flow direction)
- Position: prominent area of the map (e.g., top-right corner)

#### 6. Legend (Hebrew)
Bottom-right corner with all symbology:
```
■ אזור תעשייה
● קידוח ניטור (לפי רמת זיהום: ירוק —אדום)
▲ מפעל תעשייתי
■ תחנת דלק
↗ כיוון זרימת מי התהום
```

### Implementation Approach

**Option A (preferred)**: Matplotlib + Cartopy / Folium-static
- Aerial photo via OSM tiles or user-provided basemap
- Scatter for boreholes (size + color by index)
- Triangles/squares for facilities
- `plt.annotate` with `arrowprops` for flow direction
- Save to `Raanana/charts_v2/zone_site_map.png` at 300 DPI

**Option B**: Static composite from QGIS / Google Earth screenshot
- User provides aerial photo PNG
- Overlay boreholes/facilities/arrow programmatically
- Save to same path

**Option C** (interim): SVG composite manually
- Reasonable for one-time creation
- Document in code comments

### Position in Report
- **Section 2 (ההקשר הגיאוגרפי-תעשייתי)** — at the top, immediately after section heading, before any text
- Caption: `איור 1: מפת אזור תעשייה רעננה — קידוחים, מפעלי מקור פוטנציאליים וכיוון זרימת מי התהום`

### Reference Implementation
2021 Report figure to emulate:
- File: `Base-Report/בקרת איכות מים במערך ניטור אזורי תעשייה באקויפר החוף 2021.pdf`
- Page 36, איור 29
- Caption: "אינדקס איכות מים מירבי לחומרים אורגניים נדיפים (אדום) ודלקים (שחור) בקידוחי ניטור והפקה באזור רעננה"

---

## Color Palettes (IMMUTABLE)

### PFAS S-Group (Sulfonate-based, BOTTOM of stack)
```python
PFAS_S_COLORS = {
    "PFHxS": "#0D47A1",   # Dark blue
    "PFBS":  "#1565C0",   # Blue
    "PFOS":  "#1976D2",   # Medium blue
    "PFHpS": "#42A5F5",   # Light blue
    "PFDS":  "#90CAF9",   # Very light blue
}
```

### PFAS A-Group (Carboxylate-based, TOP of stack)
```python
PFAS_A_COLORS = {
    "PFOA":  "#BF360C",   # Dark orange
    "PFHxA": "#D84315",   # Orange-red
    "PFHpA": "#E64A19",   # Orange
    "PFNA":  "#F4511E",   # Orange-red
    "PFDA":  "#FF7043",   # Coral
    "PFDoA": "#FF8A65",   # Light coral
    "PFBA":  "#FFAB76",   # Peach
    "PFPeA": "#FFA726",   # Light orange
    "PFUnA": "#FFF3E0",   # Very light orange
}
```

### CVOC & BTEX (Reference)
- TCE: `#D32F2F` (dark red)
- PCE: `#FF8F00` (dark orange)
- Benzene: varies by function (check script)

---

## Chart Requirements (Contracts)

### RTL Rendering (ALL CHARTS)
- **Invariant**: Every Hebrew label must use `H()` helper (calls `_fix_hebrew()`)
- **Verification**: Code inspection — grep for `ax.set_title(H(...))`, `ax.set_ylabel(H(...))`
- **Failure Mode**: Text renders LTR (backwards) if missing

### PFAS S/A Ordering (Charts 2, 7)
- **Invariant**: S-group columns appear BEFORE A-group in data stack (<bdi>bottom → top</bdi>)
- **Code**: `PFAS_ALL_ORDER = PFAS_S_ORDER + PFAS_A_ORDER`
- **Verification**: Visual inspection — blue at bottom, orange at top
- **Failure Mode**: Wrong stack order = confusing forensics

### Drinking Water Standards (Charts 1, 3, 5)
- **Invariant**: Horizontal dashed line at drinking water standard threshold
- **Values**:
  - TCE: 7.5 µg/L
  - PCE: 10.0 µg/L
  - Benzene: 5.0 µg/L
- **Verification**: Check chart visually for dashed line presence
- **Failure Mode**: Missing line = chart loses reference point

### Time-Series vs. Bars (Dynamics vs. Peaks)
- **Rule**: Contamination *dynamics* (trends, changes) → curves only (Charts 1, 3, 5, 6)
- **Rule**: Peak *comparison* (max values across boreholes) → bar chart (Chart 4)
- **Rule**: PFAS composition (proportions at one borehole) → bar or stacked (Charts 2, 7, 8)
- **Verification**: Report section names ("דינמיקת הזיהום") should cite curves, not bars

### File Output Paths (STABLE)
- **Invariant**: All functions save to `out / filename` where `out = zone_dir / "charts_v2"`
- **Code Pattern**: `fig.savefig(out / "cvoc_timeseries.png", dpi=150, bbox_inches="tight")`
- **Verification**: Bash `ls Raanana/charts_v2/ | grep -c .png` should return 9 (all 9 exist)

---

## Data Inputs (EXCEL)

**File**: `Raanana/data/measurements.csv`

**Key columns** (assumed):
- `canonical_id` — borehole ID (e.g., "raanana_nt_1")
- `date` — sampling date (ISO 8601)
- `param_code` — parameter code (e.g., "TCEY", "PFOA")
- `concentration` — concentration value (µg/L)

**Coverage** (per report):
- CVOC: nt_1, nt_2, nt_3, p_25 (2012–2025)
- PFAS: nd_turbine (2025-07-30), p_25 (2025-07-30)
- BTEX: nd_paz (2011–2024)

---

## Validation Checklist

Before committing chart changes:
- [ ] All 10 chart entries (incl. zone_site_map.png) accounted for
- [ ] All currently-implemented chart functions in `generate_charts_v2.py` run without error
- [ ] All implemented PNG files exist in `Raanana/charts_v2/`
- [ ] File names match this spec (stable, no renaming)
- [ ] Hebrew labels render RTL (visual check or screenshot)
- [ ] S/A colors appear in correct order (blue bottom, orange top, for PFAS)
- [ ] Standard threshold lines visible on CVOC/BTEX charts
- [ ] Time-series curves (not bars) on dynamics charts
- [ ] Bar charts on peak comparison charts
- [ ] All referenced charts in report exist
- [ ] **Central map figure** (`zone_site_map.png`) implemented per Section X — boreholes colored by max index, facility triangles, gas station squares, NW–W flow arrow, RTL Hebrew labels

---

## Reference Implementation

**Location**: `/home/user/Industrial-Areas-Report/scripts/generate_charts_v2.py`

**Main function**: `main()`
- Calls all chart functions in order
- Saves to `out / charts_v2/`
- Prints "Done — N charts saved"

**Run command**:
```bash
python scripts/generate_charts_v2.py --zone raanana --output Raanana/charts_v2
```

**Pending implementation**: `chart_zone_site_map()` — Section X above

---

## Change Log

| Date | Change | Reason |
|---|---|---|
| 2026-05-04 | Created spec | Stabilize after renaming issues |
| 2026-05-05 | Added Chart 0 (`zone_site_map.png`) — central map figure with boreholes by index, facility markers, flow arrow. Modeled on 2021 report Map B (איור 29, p.36). Added Section X with full visual specification | Per user request: central report figure must be a zone map with index-based borehole symbology, facility sources, and flow direction |

---

**Status**: LOCKED (spec finalized v2)  
**Last Review**: 2026-05-05  
**Next Review**: After implementation of `zone_site_map.png` or any chart function changes
