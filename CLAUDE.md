# CLAUDE.md - Industrial Areas Report Project Governance

> **Methodology layering**: This file is **prescriptive** (what we do). For per-feature **descriptive** history, see commit messages. For **open patterns awaiting 2nd-case validation, deferred decisions, and tooling roadmap**, see `LESSONS.md`. Promote items from `LESSONS.md` to `REQUIREMENTS.md` only after a 2nd real case validates the pattern.

## Project Overview
**Title**: Structured Reporting System for Groundwater Quality Monitoring in Industrial Areas  
**Scope**: Generalised reporting framework for the 18-zone coastal aquifer industrial monitoring system, Israel  
**Reference Implementation**: Raanana zone (אזה"ת רעננה) — first zone fully validated by expert hydrogeologist (May 2026)  
**Current Application**: Holon zone (אזה"ת חולון) — first end-to-end run of the generalised framework  
**Data Sources**: TAHAL 2008 (historical), 2021 Water Quality Report (baseline), zone-specific Excel measurements  
**Deliverables**: Per-zone reports, drilling cards, trend analysis, forensic attribution, zone site maps  
**Methodology Status**: Framework proven on Raanana, now zone-agnostic — every script accepts `--zone <id>`

---

## 1. Think Before Coding

### State Assumptions Explicitly
- **Data Quality**: All input data sourced from official reports (TAHAL 2008, 2021 Report). Verification: Compare extractions against source document page numbers.
- **Methodology**: Severity index calculation and trend analysis follow 2021 Report methodology exactly. No modifications without expert validation.
- **Scope**: The framework targets generalised reports (any geographic area, any facility) — the 18-zone batch is the first application, not the ceiling. Build abstractions from concrete patterns observed in ≥2 zones; do not pre-design for hypothetical zone variations. Raanana is the reference implementation; Holon is the first generalisation test. Long-term horizons include: arbitrary geographic input → automated data discovery → report; and zone dashboards alongside (or in place of) full reports.
- **Regulatory Context**: Assume Ministry of Environmental Protection standards apply; coordinate with authorities before recommendations.

### Surface Ambiguities & Tradeoffs
Before implementing data processing:
1. **Missing data**: Do not interpolate. Flag gaps explicitly. User decision: extrapolate, accept gap, or seek additional data sources.
2. **Contamination attribution**: Multiple facilities near boreholes; forensic analysis probabilistic. Present confidence levels (HIGH/MEDIUM/LOW); don't overstate certainty.
3. **Trend extrapolation**: Historical trends may not continue. Present as "if trend persists" scenarios only.
4. **Deep aquifer / confined boreholes**: Slow flow may distort trend signals; flag interpretation limitations.
   - `[RAANANA-SPECIFIC]` Boreholes R-004 and R-005 are known confined cases — see `Raanana/README.md` for zone-specific notes.

### Ask Rather Than Assume
- If borehole coordinates fall outside zone polygon ±500m, ask for clarification
- If contamination pattern matches multiple source facilities, present all hypotheses; don't pick silently
- If severity index threshold unclear, request expert clarification before recalculation
- If two source documents disagree on the same fact (e.g., a borehole's classification), flag the discrepancy and request expert validation rather than picking silently

---

## 2. Simplicity First

### Code Scope (consolidate_data.py & Future Scripts)
- **Goal**: Extract, organize, and analyze official monitoring data
- **Don't Add**:
  - Prediction models or extrapolation (user decision, not automated)
  - Automated remediation planning (expert decision)
  - Statistical methods beyond what's documented (current: Mann-Kendall + SNR gating; do not introduce parametric tests, ML, or new estimators without methodology approval)
  - Configurability beyond what existing zones need — config lives in `config/analysis_config.yaml` (engine params) and `config/zone_overrides/{zone}.yaml` (per-zone Excel column overrides). No new config files without 2nd-zone justification.
  
- **Do Keep**:
  - CSV/JSON parsing (foundation for all analysis)
  - Mann-Kendall trend calculation (tie-corrected variance, continuity-corrected Z, SNR ≥ 0.3, soft_trigger=2)
  - Severity index calculation (per 2021 Report formula)
  - Forensic pattern matching (source attribution support, not definitive)

### Data File Scope (CSVs, JSONs)
- **boreholes.csv**: Only columns needed for reporting (canonical_id, name_he, ITM coordinates, depth, layer, source)
- **measurements.csv**: Only columns needed for trend analysis (borehole, date, parameter, concentration, unit, source)
- **facility_attribution.json**: Only properties needed for source attribution (name_he, address_he, suspected_contaminants, confidence, ITM coordinates, evidence)
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
- **Follow established formatting** (tables, headings, structure from `Raanana/output/drilling_card_*_v2.md` and `RAANANA_REPORT_V2.md`)
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
- Goal: Excel ingestion → trend engine → charts. Generalised: every script accepts `--zone <id>`.
- Reference results (Raanana):
  - ✓ 7 real boreholes from Excel (raanana_nt_1 through raanana_p_25)
  - ✓ 2,613 measurements (TPFAS excluded); 179 parameters
  - ✓ Mann-Kendall trend engine (tie-corrected, SNR gating, soft_trigger=2 measurements)
  - ✓ ALERT: NO₃ at p_25; WATCH: CHLF at p_25, ORP at paz_hanofer
  - ✓ 36 parameter/borehole pairs crossed drinking water standard
  - ✓ 9 production charts (V2): zone site map, PFAS stacked, CVOC + trend lines, BTEX, 4 time-series trend charts
  - ✓ V1 charts deprecated and removed from Raanana/charts/ (15 files deleted)
  - ✓ Forensics: 7 decay chains, 14 source signatures, 758 co-occurrence pairs
  - ✓ PFAS at turbine station: PFHxS 1,160%, PFOA 524% (July 2025 — critical new finding)
- Framework readiness (Phase 5):
  - ✓ `parse_excel.py`: zone-specific Excel paths + column overrides via `config/zone_overrides/{zone}.yaml`
  - ✓ `trend_analysis.py`, `forensics_analyzer.py`: zone-derived paths (no Raanana hardcode)
  - ✓ `generate_charts_v2.py`: routes to zone-specific charts (Raanana) or generic data-driven charts (any zone)

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

**Phase 4: System Validation** ✓ COMPLETE (May 2026)
- Goal: Expert hydrogeologist review of Raanana zone report
- Result:
  - ✓ Hydrogeologist approved report as submitted — no corrections required
  - ✓ No confirmatory PFAS sampling planned (hydrogeologist decision)
  - ✓ Boron anomaly (2019-07-22 at nt_2, nt_3) — noted for future investigation; not blocking
  - ✓ Decision: pilot methodology on Holon zone before scaling to all 18 zones

**Phase 5: Zone Application Framework** ✓ FRAMEWORK COMPLETE | ⏳ ZONE-SPECIFIC OUTPUTS PENDING (Holon)
- Goal: Validate the methodology works for **any** of the 18 industrial zones — not just Raanana
- Framework changes (zone-agnostic):
  - ✓ Pipeline scripts (parse_excel, preprocess, trend_analysis, forensics_analyzer, generate_charts_v2,
    select_boreholes, validate_report) — all accept `--zone <id>` and derive paths from zone name
  - ✓ Per-zone Excel column mapping via `config/zone_overrides/{zone}.yaml` (handles format variations)
  - ✓ Generic data-driven charts (`chart_generic_trends`, `chart_generic_exceedances`,
    `chart_generic_severity_panel`) auto-pick top-contaminated boreholes per contaminant family
  - ✓ Zone site map (`chart_zone_site_map`) computes extent + severity from data — no hardcoded IDs
  - ✓ Borehole selection (`select_boreholes.py`) uses zone polygon (Tier 2) + Tier 1/3 lists
- First framework application — Holon (אזה"ת חולון):
  - ✓ Data uploaded: 4 PDFs (`Holon/data/external/`), Excel (`Water Quality Data/...חולון.xlsx`), KMZ polygon
  - ✓ Pipeline executed end-to-end: 112 boreholes parsed → 111 selected (Tier 2 polygon), 4,762 trend pairs
  - ✓ Cross-zone param-family classifier (`scripts/param_families.py`) handles Holon's full English names
    (TRICHLORO ETHYLENE) and Raanana's short codes (TCEY) — CVOC chart now produces 4,915 measurements
  - ✓ Borehole selection persistence (`selected_boreholes.json`): downstream scripts filter automatically
  - ✓ Charts produced: site_map + cvoc_trends + btex_trends + pfas_trends + exceedances_bar + severity_panel
  - ⏳ Facility discovery for Holon (run Agent against Holon zone)
  - ⏳ Holon zone summary report (HOLON_REPORT_V1.md)

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

## 8. Adding a New Zone — Standard Workflow

The framework supports any of the 18 industrial zones in the coastal aquifer monitoring system.
This section is the canonical procedure for activating a new zone.

### Current State (Framework — Reference Implementation: Raanana)
- Pipeline: `parse_excel → preprocess → trend_analysis → forensics_analyzer → generate_charts_v2`
- All scripts: zone-agnostic (`--zone <id>`); paths derived from zone name; column mapping per zone via config
- Reference outputs (Raanana): 7 boreholes, 2,613 measurements, 9 production charts, zone summary, 7 drilling cards
- Holon (first framework application): 112 boreholes, 20,613 measurements, generic charts produced
- 28 automated tests; 3 report validators (chart_refs, tone, attribution)
- Documentation: REQUIREMENTS.md, STYLE_GUIDE.md (Hebrew), CHART_SPEC.md, DATA_DICTIONARY.md
- 18-zone seed data: `zone_definitions/` and `base_layer/`

### Step-by-step: activating zone `<X>`

**1. Data inputs** (uploaded by user):
- `Water Quality Data/<X>_measurements.xlsx` (or any name) — Excel with measurements
- `<X>/data/external/` — zone-specific Water Authority / TAHAL / municipal PDFs
- `zone_definitions/<polygon_file>.kmz` (or already in `zone_polygons.json`) — zone boundary

**2. Configuration**:
- `config/zone_overrides/<X>.yaml` — Excel column mapping if format differs from Raanana defaults
  (provide column indices for borehole_id, name, easting, northing, date, param_name, concentration, etc.)
- `zone_definitions/zone_polygons.json` — populate `<X>` entry with ITM polygon (convert KMZ via pyproj if needed)
- `zone_definitions/tier1_historical_boreholes.json` — historical borehole IDs from 2008/2021 reports
- `zone_definitions/tier3_cross_zone_boreholes.json` — manual additions (upgradient, downgradient)
- `crosswalks/borehole_id_mapping.json` — optional canonical ID mapping (auto-derived if absent)

**3. Pipeline run** (zone-agnostic; recommended order):
```bash
# Step 1: Extract measurements from Excel
python scripts/parse_excel.py        --zone <X>

# Step 2: Borehole selection (Tier 1 historical + Tier 2 polygon + Tier 3 manual)
#         Writes <X>/data/selected_boreholes.json — downstream scripts filter by it
python scripts/select_boreholes.py   --zone <X> --list-tiers

# Step 3: Extract text from background PDFs (mechanical step, IDEMPOTENT)
#         Writes <X>/data/external/_raw_text/*.txt + _pdf_index.json
#         --include-shared: also process root Base-Report/ PDFs (TAHAL 2008, 2021 report)
#         --force: re-extract even if already cached in manifest
#         Default: skips PDFs already in _pdf_index.json with extraction_ok=true
python scripts/extract_zone_pdfs.py  --zone <X> --include-shared

# Step 4: AI agent extraction (parallel sub-agents, one per PDF)
#         Each agent produces <X>/data/external/_findings_<sourcetag>.json
#         Use model="sonnet" (per ~/.claude/CLAUDE.md cost guidance)
#         (run via Agent tool — see prompt template below)

# Step 5: Merge per-PDF findings → unified extracted_findings.json
#         Deduplicates boreholes (by name_he), consolidates findings,
#         preserves source_file attribution for each entry
python scripts/merge_extracted_findings.py --zone <X>

# Step 6: Trend analysis (Mann-Kendall + SNR)
python scripts/trend_analysis.py     --zone <X>

# Step 7: Forensic attribution (decay chains, source signatures, co-occurrence)
python scripts/forensics_analyzer.py --zone <X>

# Step 8: Charts (Raanana → 9 zone-specific; other zones → 6 generic data-driven)
python scripts/generate_charts_v2.py --zone <X>
```

**3a. Idempotency (one-time PDF extraction)**:
`extract_zone_pdfs.py` and the AI extraction step are designed for one-time
processing per PDF file. The manifest `<X>/data/external/_pdf_index.json` tracks
each PDF by filename with `extraction_ok` + `extraction_date_utc`. On re-runs:
- Already-extracted PDFs (`extraction_ok=true`) are SKIPPED
- New PDFs added to `<X>/data/external/` or `Base-Report/` trigger fresh extraction
- `--force` overrides the cache (useful after pdftotext upgrade or schema change)
The same applies to AI agent JSON outputs (`_findings_*.json`): once produced,
they should not be regenerated unless the source PDF changes. The merge step
(`merge_extracted_findings.py`) is cheap and can be re-run freely.

**3b. AI agent prompt template (PDF extraction)**:
The script `extract_zone_pdfs.py` only mechanically converts PDF→text. The
structured extraction is done by AI sub-agents (one per PDF, parallel) with
a hydrogeologist persona, each producing `<X>/data/external/_findings_<tag>.json`.
Schema: `source_file`, `title_he`, `year`, `author_org_he`, `summary_he`,
`boreholes_mentioned[]`, `contamination_findings[]`, `facilities_suspected[]`,
`hydrogeology_he`, `trends_described_he[]`, `recommendations_he[]`,
`key_quotes_he[]`. See `Holon/data/external/_findings_*.json` (4 files, one per
PDF) as worked examples. The merge step combines them into a single
`extracted_findings.json` with `statistics{}` summary and `source_files[]`
attribution. Schema requires Hebrew text preserved verbatim, page references
where possible, confidence levels (HIGH/MEDIUM/LOW) on facility attribution.

**4. Per-zone manual deliverables** (using Raanana as template):
- `<X>/output/<X>_REPORT_V1.md` — zone summary report (Hebrew, per STYLE_GUIDE)
- Drilling cards per Tier 1 borehole (narrative-style, per Raanana template)
- `<X>/data/facility_attribution.json` — populated by AI agent facility discovery
- `<X>/data/external/web_findings.md` — search log for facility discovery

**5. Validation**:
```bash
python scripts/validate_report.py --report <X>/output/<X>_REPORT_V1.md --charts-dir <X>/charts_v2
pytest tests/ -v
```

**6. Expert review** (per zone):
- Submit `<X>_REPORT_V1.md` + drilling cards + charts to expert hydrogeologist
- Address comments (or proceed unchanged if approved as-is, like Raanana)

### Implementation Trigger
- Methodology validated on Raanana ✓ (May 2026, hydrogeologist approval)
- Holon application in progress (validates framework generality)
- After Holon validation → systematic application to remaining 16 zones
- Requires Ministry of Environmental Protection coordination per zone

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

**Framework Success Criteria** (cross-zone — must hold for any zone):
1. ✓ Pipeline scripts accept `--zone <id>` and derive all paths from zone name
2. ✓ Per-zone Excel column mapping configurable (`config/zone_overrides/<zone>.yaml`)
3. ✓ Zone polygon (ITM) intersection drives Tier 2 borehole selection
4. ✓ Generic data-driven charts work without hardcoded borehole IDs
5. ✓ Zone site map computes extent + severity from data
6. ✓ 28 automated tests pass + 3 report validators (chart_refs, tone, attribution)
7. ✓ Documentation describes "Adding a new zone" as standard workflow

**Reference Implementation Criteria — Raanana** (all ✓):
1. ✓ All 7 Raanana boreholes have drilling cards (nt1, nt2, nt3, nd_paz, nd_turbine, p18, p25)
2. ✓ Zone summary report synthesises all data layers (4 contamination foci, trend table, forensics)
3. ✓ Forensic analysis links contaminants to source facilities with confidence levels
4. ✓ PFAS at turbine station flagged for urgent regulatory attention
5. ✓ Real 2011–2026 data integrated (replacing placeholder data)
6. ✓ Zone site map generated (offline ITM schematic); Figure 1 in report; 9 facility candidates identified
7. ✓ Expert hydrogeologist review — approved (May 2026); no PFAS sampling required

**First Framework Application — Holon** (in progress):
1. ✓ Pipeline ran end-to-end (parse → trend → forensics → charts)
2. ✓ 112 boreholes parsed → 111 selected by polygon (Tier 2)
3. ✓ Cross-zone param-family classifier resolved CVOC chart (4,915 measurements detected)
4. ✓ All generic charts produced (site_map, cvoc_trends, btex_trends, pfas_trends, exceedances, severity)
5. ⏳ Holon zone summary report
6. ⏳ Facility discovery (AI agent) for Holon
7. ⏳ Expert hydrogeologist review of Holon report

**Open framework items**:
- ⏳ Basemap integration (REQ-G1) — pending environment resolution
- ⏳ After Holon validation → systematic activation of remaining 16 zones

---

**Project Status**:
- Framework (Phases A–G): ✓ Complete — pipeline zone-agnostic, validated on Raanana, expert-approved
- Phase 5 (Zone Application Framework): ✓ Complete on framework side; Holon as first application — pipeline running, report pending
- Phase 2 (full 18-zone activation): ⏳ Pending Holon report sign-off + Ministry coordination

**Last Updated**: May 6, 2026  
**Completion**: 44/44 core requirements done; 1 deferred (REQ-G1 basemap); 3 deprecated charts  
**Next Review**: After Holon zone summary report complete → systematic activation of remaining 16 zones
