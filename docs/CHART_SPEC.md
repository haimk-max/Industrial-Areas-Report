# CHART_SPEC.md — יציבות וחוזה גרפים לדוח רעננה

**Purpose**: Stabilize chart file names, define content invariants, and specify color palettes so changes to functions don't break report references.

---

## Chart Inventory (9 charts)

| ID | File Name (STABLE) | Function | Content | Data Source | Invariants |
|---|---|---|---|---|---|
| 1 | `cvoc_timeseries.png` | `chart_cvoc_timeseries()` | TCE at nt_1, nt_2; PCE at nt_3 (2012–2025) | Excel measurements | Time-series curves only; RTL labels; standard threshold line (TCE 7.5, PCE 10.0 µg/L) |
| 2 | `pfas_all_boreholes.png` | `chart_pfas_all_boreholes()` | PFAS stacked bar per borehole (S/A groups) + time-series subplots if >1 measurement | Excel measurements | S-group bottom (blue), A-group top (orange); bar per borehole, latest reading; time-series if 2+ dates exist |
| 3 | `btex_timeseries_paz.png` | `chart_btex_timeseries()` | Benzene at nd_paz (2011–2024) | Excel measurements | Time-series curve; RTL labels; standard threshold line (BENZENE 5.0 µg/L) |
| 4 | `cvoc_cross_borehole.png` | `chart_cvoc_cross_borehole()` | Max annual TCE/PCE across boreholes (nt_1, nt_2, nt_3, p_25) | Excel measurements | Bar chart (historic peaks, not dynamics); grouped by borehole; RTL labels |
| 5 | `tce_timeseries_p25.png` | `chart_tce_p25()` | TCE at p_25 production well (2023–2025 exceedance detail) | Excel measurements | Time-series curve; detail view; standard threshold line (7.5 µg/L); RTL labels |
| 6 | `cvoc_all_wells.png` | `chart_cvoc_all_wells()` | CVOC curves for all 4 boreholes: TCE panel + PCE panel | Excel measurements | Pure time-series curves only (never bars); side-by-side panels; RTL labels |
| 7 | `pfas_pct_stacked.png` | `chart_pfas_pct_stacked()` | 100%-stacked PFAS at nd_turbine (source-signature AFFF validation) | Excel measurements | S-group bottom (blue), A-group top (orange); 100% normalized; RTL labels |
| 8 | `btex_family_stacked.png` | `chart_btex_family_stacked()` | BTEX full family (benzene, toluene, ethylbenzene, xylenes) time-series at nd_paz | Excel measurements | Stacked time-series; separate colors per compound; RTL labels |
| 9 | `cvoc_pct_standard_panel.png` | `chart_cvoc_pct_standard_panel()` | 4-borehole panel: % of drinking water standard (TCE/PCE) over time | Excel measurements | Y-axis as % of standard; 4 subplots (nt_1, nt_2, nt_3, p_25); RTL labels |

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
- **Invariant**: S-group columns appear BEFORE A-group in data stack (bottom → top)
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
- [ ] All 9 functions in `generate_charts_v2.py` run without error
- [ ] All 9 PNG files exist in `Raanana/charts_v2/`
- [ ] File names match this spec (stable, no renaming)
- [ ] Hebrew labels render RTL (visual check or screenshot)
- [ ] S/A colors appear in correct order (blue bottom, orange top, for PFAS)
- [ ] Standard threshold lines visible on CVOC/BTEX charts
- [ ] Time-series curves (not bars) on dynamics charts
- [ ] Bar charts on peak comparison charts
- [ ] All referenced charts in report exist

---

## Reference Implementation

**Location**: `/home/user/Industrial-Areas-Report/scripts/generate_charts_v2.py`

**Main function**: `main()` (lines ~??–??)
- Calls all 9 chart functions in order
- Saves to `out / charts_v2/`
- Prints "Done — 9 charts saved"

**Run command**:
```bash
python scripts/generate_charts_v2.py --zone raanana --output Raanana/charts_v2
```

---

## Change Log

| Date | Change | Reason |
|---|---|---|
| 2026-05-04 | Created spec | Stabilize after renaming issues |
| — | — | — |

---

**Status**: LOCKED (spec finalized)  
**Last Review**: 2026-05-05  
**Next Review**: After any chart function changes
