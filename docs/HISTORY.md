# Project History — Industrial Areas Report

> מסמך זה מכיל את **תיעוד שלבי הביצוע ההיסטוריים** של הפרויקט (Phases 1–4, A–G).
> ל-CLAUDE.md בעליון יש את התעדה של ה-Phase הפעיל (כעת: Phase H — Holon V4.2) ושלב 4 (Validation Pending).
>
> מסמך זה הוא לעיון בלבד — לא לעריכה אחורה. כל phase חדש מתועד תחילה ב-CLAUDE.md ועובר לכאן אחרי שהוא הופך לעבר.

---

## Verify Success at Each Phase (Historical)

**Phase 1: Data Organization** ✓ COMPLETE
- Goal: Define schemas and populate Raanana borehole/concentration data
- Verify:
  - ✓ 5 boreholes from TAHAL 2008 Part B pages 53-67 extracted
  - ✓ 1999-2008 concentrations for 3+ parameters (TCE, 1,2-DCA, chloroform)
  - ✓ Data schemas validated (CSV parses correctly, JSON well-formed)
  - ✓ Source attribution documented for every data point

**Phase 2: Data Consolidation** ✓ COMPLETE
- Goal: Merge TAHAL 2008 historical with 2021 report baseline
- Verify:
  - ✓ 2021 severity index integrated (zone score 3 / "medium")
  - ✓ Forensics schema populated with contamination families
  - ✓ Flow direction assessment complete
  - ✓ Industries mapped with spatial relationships
  - ✓ Consolidation script executes without errors

**Phase 3: Drilling Card & Report Generation** ✓ COMPLETE (R-001, R-004)
- Goal: Generate R-001 and R-004 drilling cards; zone summary report
- Verify:
  - ✓ Drilling cards include: trends, severity assessment, forensics, recommendations
  - ✓ Trend analysis matches source document interpretations (TCE up, 1,2-DCA down)
  - ✓ Zone summary synthesizes all data layers
  - ✓ All findings traced to source documents (page numbers cited)
  - ✓ Risk scores calculated per methodology

**Phase A–C: Real Data Pipeline** ✓ COMPLETE (May 2026)
- Goal: Replace placeholder data with real 2011–2026 Excel measurements; statistical trend engine; charts
- Verify:
  - ✓ 7 real boreholes from Excel (raanana_nt_1 through raanana_p_25)
  - ✓ 2,613 measurements (TPFAS excluded); 179 parameters
  - ✓ Mann-Kendall trend engine (tie-corrected, SNR gating, soft_trigger=2 measurements)
  - ✓ ALERT: NO₃ at p_25; WATCH: CHLF at p_25, ORP at paz_hanofer
  - ✓ 36 parameter/borehole pairs crossed drinking water standard
  - ✓ 9 production charts (V2): zone site map, PFAS stacked, CVOC + trend lines, BTEX, 4 time-series trend charts
  - ✓ V1 charts deprecated and removed from Raanana/charts/ (15 files deleted)
  - ✓ Forensics: 7 decay chains, 14 source signatures, 758 co-occurrence pairs
  - ✓ PFAS at turbine station: PFHxS 1,160%, PFOA 524% (July 2025 — critical new finding)

**Phase D: Hebrew Reports & Zone Map** ✓ COMPLETE (May 2026)
- Goal: Professional Hebrew zone summary + 7 drilling cards + central site map from real data
- Verify:
  - ✓ Zone summary report with 4 critical contamination findings (TCE, PCE, PFAS, Benzene)
  - ✓ 7 individual drilling cards (nt1, nt2, nt3, nd_paz, nd_turbine, p18, p25)
  - ✓ All findings sourced to Excel (borehole/date) or TAHAL/2021 (page number)
  - ✓ Limitations and data gaps explicitly stated
  - ✓ Zone site map (zone_site_map.png): offline ITM schematic with boreholes (color by index), facilities (triangles/squares), flow arrow (NW), scale bar, ITM grid; Figure 1 added to Section 2
  - ✓ Facility discovery: 9 candidates identified (F-001 through F-009) via AI agent sector-based search; facility_attribution.json populated with HIGH/MEDIUM/LOW confidence levels
  - ✓ Section 6 ("מקורות חיצוניים שנבדקו") documents PRTR, Mey Raanana, web search methodology

**Phase E: Zone Selection** ✓ COMPLETE (May 2026)
- Goal: 3-tier borehole selection mechanism for scalability
- Verify:
  - ✓ zone_definitions/tier1_historical_boreholes.json (18 zones)
  - ✓ zone_definitions/zone_polygons.json (18 zones, Raanana polygon defined)
  - ✓ zone_definitions/tier3_cross_zone_boreholes.json (18 zones)
  - ✓ scripts/select_boreholes.py — Raanana selects all 7 boreholes (5 Tier1 + 2 Tier2)

**Phase F: Tests** ✓ COMPLETE (May 2026)
- Goal: Automated regression tests for trend engine and chart presets
- Verify:
  - ✓ 28 tests passing: test_preprocess.py (8), test_chart_presets.py (11), test_borehole_selection.py (9)
  - ✓ Golden dataset: 144 measurements, 10 expected trend classifications
  - ✓ Key invariants guarded: ALERT/WATCH classifications, soft_trigger=2, SNR gating, crossed_standard before entry criteria
  - ✓ validate_report.py (3 validators): chart_refs, tone, attribution — all PASS on current report

**Phase G: Facility Discovery & Map Implementation** ✓ COMPLETE (May 5, 2026)
- Goal: Systematic contamination source identification via AI-assisted facility search; offline zone site map
- Verify:
  - ✓ AI agent facility discovery: sector-based search (CVOC sources + PFAS sources) with 2 search iterations
  - ✓ 9 facility candidates identified (F-001 through F-009): Aidchem (CVOC HIGH), Chemitron (CVOC MEDIUM), בית דקל (CVOC HIGH), CMSR (CVOC MEDIUM), Nemal (CVOC LOW), Epoxy (CVOC MEDIUM), Aerospheres (PFAS MEDIUM-HIGH), + 2 new candidates validated
  - ✓ facility_attribution.json populated: name_he, coordinates_itm, confidence, suspected_contaminants, operating_years, evidence_type
  - ✓ web_findings.md created: search log documenting PRTR queries, B144 business registry, Mey Raanana 2025 report
  - ✓ Zone site map (zone_site_map.png): 1200×960px, offline ITM schematic (no tile dependency)
    - Boreholes: 7 points colored by max contamination index (0–8 scale)
    - Facilities: 8 markers (triangles for industrial, squares for fuel)
    - Geographic: 250m ITM grid lines, scale bar (500m), north arrow, flow direction arrow (NW), ITM axis labels
  - ✓ Figure 1 caption added to Section 2 of RAANANA_REPORT_V2.md
  - ✓ REQUIREMENTS.md updated: REQ-A8 (facility discovery), REQ-B4/D8 (map), REQ-D3 (RTL), REQ-F4 (validators)
  - ✓ STYLE_GUIDE.md updated: Section H (facility discovery methodology)
  - ✓ Project structure cleanup: README.md recreated, External Data/README.md created, V1 charts removed, documentation consolidated

**Phase G.1: Basemap Integration** ⏳ DEFERRED (Phase 4 / Q3 2026)
- **Goal**: Overlay OSM or cadastral basemap on zone_site_map.png (REQ-G1)
- **Blocker**: All tile providers (OSM, CartoDB, Stamen, ESRI, contextily) return 403 Forbidden in current environment
- **Options documented**:
  1. **Cached raster tiles**: Locally hosted MBTiles or GeoTIFF of Raanana area (requires manual download)
  2. **Israeli WMS**: govmap.gov.il / Survey of Israel WMS endpoint (requires authentication, DNS verification)
  3. **Vector rendering**: Overpass API street network + geopandas render (no tile dependency, slower initial fetch)
- **Decision**: Current offline ITM schematic is production-ready; basemap deferred pending expert environment access (Phase 4)

---

**הערה**: Phase H (Holon V4.2) ו-Phase 4 (System Validation pending) **נשארים ב-CLAUDE.md** מאחר שהם פעילים/ממתינים.

**עוגן**: `CLAUDE.md` (פעיל) | `ZONE_REPORT_PROCESS_GUIDE.md` (SSOT)
