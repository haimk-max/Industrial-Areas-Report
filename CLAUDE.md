# CLAUDE.md - Industrial Areas Report Project Governance

## Project Overview
**Title**: Structured Reporting System for Groundwater Quality Monitoring in Industrial Areas  
**Scope**: Raanana industrial zone (אזה"ת רעננה) demonstration, expandable to 18-zone coastal system  
**Data Sources**: TAHAL 2008 (historical), 2021 Water Quality Report (baseline), current monitoring  
**Deliverables**: Drilling cards, zone reports, trend analysis, forensic attribution  
**Timeline**: Phase 1-4 implementation with quarterly review cycles

---

## 1. Think Before Coding

### State Assumptions Explicitly
- **Data Quality**: All input data sourced from official reports (TAHAL 2008, 2021 Report). Verification: Compare extractions against source document page numbers.
- **Methodology**: Severity index calculation and trend analysis follow 2021 Report methodology exactly. No modifications without expert validation.
- **Scope**: Raanana zone is demonstration case; design all scripts/templates to scale to 18 zones with minimal modification.
- **Regulatory Context**: Assume Ministry of Environmental Protection standards apply; coordinate with authorities before recommendations.

### Surface Ambiguities & Tradeoffs
Before implementing data processing:
1. **Missing data (2008-2021 gap)**: Do not interpolate. Flag gaps explicitly. User decision: extrapolate or wait for 2021 report full data.
2. **Contamination attribution**: Multiple facilities near boreholes; forensic analysis probabilistic. Present confidence levels; don't overstate certainty.
3. **Trend extrapolation**: Historical trends (1999-2008) may not continue. Present as "if trend persists" scenarios only.
4. **Deep aquifer sampling**: R-004 and R-005 confounded by confinement; slow flow may distort trend signals. Flag interpretation limitations.

### Ask Rather Than Assume
- If borehole coordinates fall outside zone boundary ±500m, ask for clarification
- If contamination pattern matches multiple source facilities, present all hypotheses; don't pick silently
- If severity index threshold unclear, request expert clarification before recalculation
- If 2021 Report data differs from TAHAL 2008, flag discrepancy for expert validation

---

## 2. Simplicity First

### Code Scope (consolidate_data.py & Future Scripts)
- **Goal**: Extract, organize, and analyze official monitoring data
- **Don't Add**:
  - Prediction models or extrapolation (user decision, not automated)
  - Automated remediation planning (expert decision)
  - Statistical tests beyond linear regression (methodological baseline only)
  - Configurability beyond single YAML config file
  
- **Do Keep**:
  - CSV/JSON parsing (foundation for all analysis)
  - Linear trend calculation (required for reporting)
  - Severity index calculation (per 2021 Report formula)
  - Forensic pattern matching (source attribution support, not definitive)

### Data File Scope (CSVs, JSONs)
- **boreholes.csv**: Only columns needed for reporting (ID, coordinates, depth, layer, classification, source)
- **concentrations.csv**: Only columns needed for trend analysis (year, concentration, severity, source document)
- **industries.json**: Only properties needed for source attribution (location, facility type, expected contaminants)
- No denormalization, no pre-calculated fields beyond severity index

### Report Scope (Markdown Drilling Cards, Zone Report)
- **Drilling Card**: Per-borehole profile with historical data, trends, forensics, and recommendations
- **Zone Report**: Executive summary, contamination overview, risk assessment, monitoring plan
- **No Custom Sections**: Don't add non-standard sections unless user requests
- **No Speculative Analysis**: Findings must trace to source documents; opinions flagged as "requires expert validation"

---

## 3. Surgical Changes

### When Modifying Existing Data Files
- **Match CSV format** exactly (commas, quotes, field order)
- **Preserve comments** and source attribution in header rows
- **Don't rename columns** - coordinate with user if schema needs change
- **Document extraction changes** in source_document field or extraction_notes

### When Updating Analysis Scripts
- **Don't "improve" unrelated functions** - focus on requested analysis
- **Preserve existing error handling** - only add checks for new data types
- **Match existing code style** (variable naming, comments, function structure)
- **Test before committing** - run on sample data to verify output unchanged for old parameters

### When Creating New Reports
- **Follow established formatting** (tables, headings, structure from drilling_card_R-001.md)
- **Cross-reference source documents** with page numbers for every claim
- **Flag limitations explicitly** (data gaps, assumptions, confidence levels)
- **Don't editorialize** - present findings neutrally; recommendations separate from analysis

### Cleanup Rule
- Remove imports/functions only if YOUR current changes made them unused
- Don't remove pre-existing dead code unless explicitly requested
- If noticing unrelated issues (typos, deprecated imports), mention in commit message but don't fix

---

## 4. Goal-Driven Execution

### Verify Success at Each Phase

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

**Phase 4: System Validation** (PENDING expert review)
- Goal: Expert hydrogeologist review; PFAS alert to regulators; boron anomaly investigation
- Plan:
  1. PFAS dip sampling at turbine station (Q3 2026) — top priority
  2. Expert review of forensic attributions (decay chains, source signatures)
  3. Boron anomaly investigation (2019-07-22 readings at nt_2, nt_3)
  4. Regulatory reporting for PFAS exceedances
  5. Phase 2 expansion to additional zones (post-expert validation)

---

## 5. Project-Specific Guidelines

### Data Integrity Rules
1. **Source Attribution Mandatory**: Every data point must cite original source (TAHAL page, 2021 Report page)
2. **No Interpolation**: Missing years/boreholes represented as NULL; never extrapolate historical data
3. **Severity Index Immutable**: Use exact formula from 2021 Report; no modifications without expert approval
4. **Forensics Probabilistic**: Contamination attribution presented with confidence level (HIGH/MEDIUM/LOW)
5. **Cross-Reference Validation**: When integrating TAHAL 2008 and 2021 data, flag discrepancies for expert review

### Reporting Standards
1. **Drilling Card Format**: Header (ID, coordinates, depth, classification) → Contamination findings → Trend analysis → Forensics → Limitations → Recommendations
2. **Trend Interpretation**: State trend classification (ALERT/WATCH/STABLE/DECREASING/NONE), MK z and p values, SNR, soft_trigger; interpret in context of facility operations. Do NOT use "linear regression" — the engine is Mann-Kendall.
3. **Trend Methodology**: Mann-Kendall (tie-corrected variance, continuity-corrected Z) with SNR gating. Soft trigger = 2 consecutive rising values in 5y window (NOT 3). Config in `config/analysis_config.yaml`.
4. **TPFAS Exclusion**: Always exclude TPFAS (total PFAS) and BETK from analysis — they are calculated sums. Individual species (PFHxS, PFOA, etc.) are the canonical representation.
5. **Crossed Standard**: `crossed_standard` flag is set BEFORE entry criteria check so single-measurement exceedances are always captured.
6. **Risk Communication**: Present as % of drinking water standard, classification tier, and trend.
7. **Recommendation Hierarchy**: Immediate (2026), Short-term (2026–2027), Long-term (2027+)
8. **Limitations Statement**: Every report section with assumptions includes "Limitations" callout

### Coordination Requirements
1. **Source Facility Changes**: Before updating risk assessments, query facility operators about production changes
2. **Regulatory Alignment**: Severity thresholds and monitoring frequencies cleared with Ministry of Environmental Protection
3. **Water Supply Impact**: Any recommendations affecting zone classification escalate to regional water authority
4. **Expert Validation**: Forensic attributions and remediation recommendations require hydrologist sign-off before final publication

---

## 6. Quality Assurance Checklist

Before committing code or reports:

### Code Changes
- [ ] No extra features beyond what was requested
- [ ] Existing tests still pass (if applicable)
- [ ] New code tested on sample data (Raanana zone minimum)
- [ ] Error messages helpful (not just "parse error")
- [ ] Comments removed unless WHY is non-obvious
- [ ] No commented-out code left behind

### Data Files
- [ ] CSV parses without errors (test: consolidate_data.py runs)
- [ ] JSON valid (test: json.load() succeeds)
- [ ] All source documents cited with page numbers
- [ ] No confidential facility names (anonymized as I-001, I-002, etc.)
- [ ] Coordinates verified against maps in source documents
- [ ] Units consistent (ppb for all VOCs)

### Reports
- [ ] Every claim traces to source document (page number visible)
- [ ] Trend interpretation includes slope and R²
- [ ] Risk scores calculated per matrix formula
- [ ] Limitations and data gaps explicitly stated
- [ ] Recommendations organized by timeframe
- [ ] Comparison with zone baseline (other 17 zones) included
- [ ] Markdown formatting clean (no orphaned links, proper heading hierarchy)

---

## 7. Incident Response

### If Data Discrepancy Discovered
1. **Stop analysis** - don't hide inconsistency
2. **Flag clearly** - cite both sources and page numbers
3. **Propose resolution** - suggest which source takes precedence
4. **Escalate** - request expert judgment before proceeding

### If Trend Analysis Contradicts Source Interpretation
1. **Recalculate** - verify math (slope, R², data points)
2. **Review methodology** - confirm formula matches 2021 Report
3. **Surface assumption** - what's different from source interpretation
4. **Document explicitly** - in report, note discrepancy and why

### If Forensic Attribution Uncertain
1. **Quantify uncertainty** - present confidence level (HIGH/MEDIUM/LOW)
2. **List alternatives** - show all possible source facilities
3. **Request expert input** - flag for hydrogeologist validation
4. **Never overstate** - avoid "definitely caused by" without evidence

---

## 8. Scaling from Raanana to Full System

### Current State (Raanana — Phases A–G Complete)
- 1 zone, 7 boreholes (real 2011–2026 data), 179 parameters, 2,613 measurements
- Full pipeline: parse_excel → trend_analysis → forensics_analyzer → generate_charts_v2
- 7 drilling cards + zone summary report in Hebrew + zone site map
- 28 automated tests passing (test_preprocess, test_chart_presets, test_borehole_selection); 3 report validators (chart_refs, tone, attribution)
- 9 facility candidates identified with confidence levels (facility_attribution.json)
- Tier 1/2/3 borehole selection in zone_definitions/
- base_layer/ seeded for all 18 zones (Raanana complete; 17 others manual_pending)
- Project documentation: REQUIREMENTS.md (48 requirements, 44 done), STYLE_GUIDE.md (sections A–H), CHART_SPEC.md, DATA_DICTIONARY.md

### Adding a New Zone (Phase 2)
1. `zone_definitions/tier1_historical_boreholes.json` — add zone's historical borehole IDs
2. `zone_definitions/zone_polygons.json` — define zone polygon in ITM coordinates
3. `scripts/parse_excel.py --zone <new_zone>` — extract measurements from Excel
4. `scripts/trend_analysis.py --zone <new_zone>` — run MK trend engine
5. `scripts/forensics_analyzer.py --zone <new_zone>` — forensics analysis
6. `scripts/generate_charts.py --zone <new_zone>` — charts
7. Write zone summary report + drilling cards (Raanana as template)

### Implementation Trigger
- After Phase 4 expert validation on Raanana (Q3 2026)
- Requires Ministry of Environmental Protection approval for zone expansion
- Timeline: Q3 2026 validation → Q4 2026 data integration → Q1 2027 18-zone reporting launch

---

## 9. Contact & Escalation

### For Technical Questions
- Clarification on data source, format, or scope → **User decision** (ask, don't assume)
- Methodology questions (severity index, trend calc) → **Trace to 2021 Report** (if unclear, escalate)
- Script or template bugs → **Debug locally, test fix, commit with explanation**

### For Policy/Regulatory Questions
- Recommendation appropriateness → **Expert validation** (hydrogeologist, Ministry liaison)
- Zone classification changes → **Water authority coordination** (don't recommend without clearance)
- Facility operator engagement → **User coordination** (provide analysis, user handles stakeholder management)

### Escalation Path
1. **Ambiguity**: Surface it. Ask. Don't hide confusion.
2. **Data Discrepancy**: Flag it. Propose resolution. Wait for expert input.
3. **Methodology**: Trace to source. If unclear, escalate. Don't improvise.
4. **Scope Creep**: Resist it. Remind of simplicity rule. Suggest phase 2 for new features.

---

## 10. Version Control & Collaboration

### Commit Message Format
```
[PHASE] Brief summary (imperative)

Detailed explanation (2-3 sentences max) of what changed and why.
Reference relevant source documents (TAHAL Part B page X, 2021 Report page Y).
Mention verification steps taken.

Tracing: TAHAL 2008 Part B pages 53-67, 2021 Report pages 11, 15-16, 49
https://claude.ai/code/session_01VLoT2vE82jwapmUNCB4wRe
```

### Branch Strategy
- **Main**: Stable baseline (commits from validated feature branches)
- **claude/create-base-report-directory-5DqAR**: Active development (daily commits, rapid iteration)
- **Pull Request Review**: Before merging to main, verify Phase completeness and expert validation

### Commit Frequency
- **Data changes**: Commit immediately (extracted new borehole, integrated new parameter)
- **Script changes**: Commit after testing on Raanana data
- **Report changes**: Commit after structure finalized; don't batch minor tweaks
- **Don't commit**: Partial work, experimental branches, or uncommitted changes

---

## 11. Success Metrics

**Phase Completion Criteria**:
1. ✓ Code: Runs without errors on Raanana test data
2. ✓ Data: Verified against source documents (spot-check 10% of rows)
3. ✓ Reports: All claims sourced (page numbers cited)
4. ✓ Verification: Trend calculations match source interpretations or discrepancies flagged
5. ✓ Documentation: CLAUDE.md and DATA_DICTIONARY updated

**Project Success Criteria** (Phase 4 completion):
1. ✓ All 7 Raanana boreholes have drilling cards (nt1, nt2, nt3, nd_paz, nd_turbine, p18, p25)
2. ✓ Zone summary report synthesizes all data layers (4 contamination foci, trend table, forensics)
3. ✓ Forensic analysis links contaminants to source facilities with confidence levels
4. ✓ PFAS at turbine station flagged for urgent regulatory attention
5. ✓ Real 2011–2026 data integrated (replacing placeholder data)
6. ✓ 28 automated tests passing + 3 report validators (chart_refs, tone, attribution)
7. ✓ System designed to scale from 1 zone to 18 zones (--zone flag, zone_definitions/, select_boreholes.py)
8. ✓ CLAUDE.md, DATA_DICTIONARY.md, REQUIREMENTS.md, STYLE_GUIDE.md, CHART_SPEC.md updated
9. ✓ Zone site map generated (offline ITM schematic); Figure 1 in report; 9 facility candidates identified
10. ⏳ Expert hydrogeologist review — pending (Q3 2026)
11. ⏳ PFAS regulatory reporting — pending (Q3 2026)
12. ⏳ Basemap integration (REQ-G1) — pending Phase 4 (environment resolution)

---

**Project Status**: Phases A–G Complete (real data pipeline, trend engine, charts, Hebrew reports, tests, facility discovery, zone map) | Phase 4 (expert validation) Pending Q3 2026  
**Last Updated**: May 5, 2026  
**Completion**: 44/44 core requirements done; 1 deferred (REQ-G1 basemap); 3 deprecated charts  
**Next Review**: Q3 2026 (PFAS confirmatory sampling at turbine station; expert validation; Phase 2 expansion planning)
