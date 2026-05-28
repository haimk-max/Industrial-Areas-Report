# CLAUDE.md - Industrial Areas Report Project Governance

> **Methodology layering**: This file is **prescriptive** (what we do). For per-feature **descriptive** history, see commit messages. For **open patterns awaiting 2nd-case validation, deferred decisions, and tooling roadmap**, see `LESSONS.md`. Promote items from `LESSONS.md` to `REQUIREMENTS.md` only after a 2nd real case validates the pattern.

## Project Overview
**Title**: Structured Reporting System for Groundwater Quality Monitoring in Industrial Areas  
**Scope**: Generalised reporting framework for the 18-zone coastal aquifer industrial monitoring system, Israel  
**Reference Implementation (style precedent)**: Raanana zone (אזה"ת רעננה) — V2 validated by expert hydrogeologist (May 2026)  
**Methodological stress-test**: Holon zone (אזה"ת חולון) — V4.2 first end-to-end run; **not a binding template** for the remaining 16 zones  
**Binding methodology for new zones**: V5 hybrid pipeline (Structured Data Pack + NotebookLM-like context + Zone Diagnosis + V5 schema) — see `ZONE_REPORT_PROCESS_GUIDE.md`  
**Data Sources**: TAHAL 2008 (historical), 2021 Water Quality Report (baseline), zone-specific Excel measurements  
**Deliverables**: Per-zone reports (V5 schema), drilling cards, trend analysis, forensic attribution, zone site maps  
**Methodology Status**: Framework proven on Raanana (style) + Holon (stress-test). V5 hybrid pipeline = the binding methodology going forward.

---

## אינדקס מצב אזורים (Zone Status Index)

| אזור | מצב | תפקיד | מיקום |
|------|-----|--------|--------|
| **רעננה** | V2 מאושר | **תקדים סגנוני מאושר** (סגנון כתיבה, סדר משפחות, RTL, צבע גרפים) | `Raanana/` |
| **חולון** | V4.2 ממתין לאישור הידרולוג | **stress-test מתודולוגי** (pipeline לאזור מורכב, PFAS gaps, monitoring gaps) — לא תבנית ל-16 אזורים | `Holon/` |
| 16 אזורים נוספים | ⏳ Phase 2 (Q3 2026+) | יבנו ב-**V5 hybrid pipeline** (METHODOLOGY המחייבת לאזורים חדשים) | (לבנייה אחר אישור) |

**SSOT לטרמינולוגיה וסדר פייפליין**: `ZONE_REPORT_PROCESS_GUIDE.md` (V4.2)
**Methodology סטטיסטית**: `docs/STATISTICAL_OVERVIEW_METHODOLOGY.md`
**Scripts README**: `scripts/report_designed/README.md`

---

## 1. Think Before Coding

### Language Rules (CRITICAL — User Preference)
- **Markdown files (CLAUDE.md, PROCESS.md, PROCESS_GUIDE.md, V4.md, etc.)**: **תמיד בעברית**. כותרות, טקסט, טבלאות — בעברית. מונחים טכניים באנגלית מותרים בתוך טקסט עברי (e.g., "Mann-Kendall trend").
- **Code (Python, JS, shell)**: **תמיד באנגלית**. שמות משתנים, פונקציות, comments, docstrings.
- **תכניות עבודה** (plan mode, todos): **תמיד בעברית**.
- **Commit messages**: אנגלית (convention של Git).
- **כותרות סעיפים בדוחות** (V4.md, V4.html): **עברית בלבד**.

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

## 4. Phases — Active & Pending

> תיעוד phases היסטוריים: ראה `docs/HISTORY.md` (Phases 1–4, A–G, G.1).

**Phase H: Holon V4 + Pipeline Refactor** ✓ COMPLETE (May 2026)  
**Phase H+: Methodological Refactor — Hybrid Pipeline** ✅ COMPLETE (May 2026)
- Goal: Production pipeline for Holon zone (80 active boreholes, 2,672 measurements) + reusable architecture for 16 remaining zones
- Status:
  - ✓ Holon V4.2 report: 10 sections in Hebrew, 5 contamination foci (CVOC, METALS, PFAS, FUEL), 25 significantly-exceeding boreholes
  - ✓ Lean workspace: `Holon/lean_workspace/{01_inputs,02_data_filtered,03_evidence_index,04_deterministic_anchors,05_prompt}/`
  - ✓ Severity index: `bucket(C_max_5y / DWS × 100)`, 9-level scale 0–8 (PFAS included as extension beyond 2021)
  - ✓ Two HTML generators: `_V4.html` (canonical, ~180KB) + `_DESIGNED.html` (visual summary, ~139KB); both rely on `boreholes_override` from V4.md (CVOC=6, METALS=4, FUEL=6 panel caps; sorted by family severity desc)
  - ✓ Safety net: HTML generator auto-injects `![]()` image markdown when Opus omits it (figure caption present but image markdown missing)
  - ✓ SSOT: `ZONE_REPORT_PROCESS_GUIDE.md` for terminology + pipeline; `STATISTICAL_OVERVIEW_METHODOLOGY.md` redirects to §III
  - ✓ Generic Zone Prompt Template: `scripts/templates/zone_report_prompt_template.md` (Anthropic XML-tag structure, 30 placeholders, `<figure_rules>` enforcing image-before-caption)
  - ✓ Family ordering: FUEL always last; CVOC/METALS/PFAS by zone max_bucket descending (§IV)
  - ✓ Web search & PDF ingestion documented in PROCESS_GUIDE §I.2 + §I.5 (External Data/{zone}/ structure, 6 channels)

- **Phase H+ Implementation** ✅ COMPLETE (2026-05-28, PR #19 merged via a19a917):
  - ✅ PROCESS_GUIDE refactored: §I → Zone Context Pack (5 folders: scope/data/context/diagnosis/prompt)
  - ✅ §II → V5 Schema (6 sections, generic for all zones)
  - ✅ §II.5 → Zone Diagnosis (8 questions, pre-report step)
  - ✅ §VI → diagnostic + final figures (pre-Opus + post-Opus)
  - ✅ §VII → validation checklist (6 new checks: Context Pack, Data Pack, Diagnosis, PFAS, gaps, C_max_5y separation)
  - ✅ §VIII → 7-step hybrid pipeline
  - ✅ DATA_PIPELINE_SPEC.md created (6 CSVs schema)
  - ✅ REPORT_V5_SCHEMA.md created (V5 skeleton + templates)
  - ✅ CLAUDE.md §8 Scaling updated (hybrid pipeline workflow)
  - ✅ Holon V5 report generation (REQ #13.6): Opus → figures → HTML designed (164KB+177KB)
  - ✅ Documentation sync: PROCESS.md (requirements tracking) + LESSONS.md (tech-debt roadmap)
  - ✅ Data pipeline scripts (REQ #13.1): generate_holon_data_pack.py → 7 CSVs (15,173 rows)
  - ✅ Reports Context Pack (REQ #13.2) + Source Candidates (REQ #13.3) + Zone Diagnosis (REQ #13.4) + Templates (REQ #13.5)
  - ✅ Executive summaries (REQ #15): INTERNAL.html (64KB, 1,698 lines) + PUBLIC.html (52KB, 1,323 lines)
  - ✅ Report Engine (REQ #16): 14-file generic report-engine/ for all 18 zones
  - ✅ Brief YAML + Twin HTML generators (REQ #17, #18)
  - ✅ Toolkit system (REQ #19): Tier A skills + Tier B pylib (signalkit) + Tier C playbooks (5/5), sanitized cross-references

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
  - ✓ 36 parameter/borehole pairs crossed drinking water standard
  - ✓ 9 production charts (V2)
  - ✓ Forensics: 7 decay chains, 14 source signatures, 758 co-occurrence pairs
  - ✓ PFAS at turbine station: PFHxS 1,160%, PFOA 524% (July 2025 — critical new finding)

**Phase D: Hebrew Reports & Zone Map** ✓ COMPLETE (May 2026)
- ✓ Zone summary report with 4 critical contamination findings
- ✓ 7 individual drilling cards
- ✓ Zone site map (offline ITM schematic; Figure 1 in Section 2)
- ✓ Facility discovery: 9 candidates (F-001..F-009) with HIGH/MEDIUM/LOW confidence

**Phase E–F: Zone Selection + Tests** ✓ COMPLETE (May 2026)
- ✓ 3-tier borehole selection (Tier 1 historical + Tier 2 polygon + Tier 3 cross-zone)
- ✓ 28 automated tests + 3 report validators (chart_refs, tone, attribution)

**Phase G: Facility Discovery & Map Implementation** ✓ COMPLETE (May 5, 2026)
- ✓ AI agent facility discovery (sector-based search)
- ✓ facility_attribution.json populated; web_findings.md created
- ✓ Zone site map: offline ITM schematic (1200×960px, no tile dependency)
- ✓ REQUIREMENTS.md updated (REQ-A8, REQ-B4/D8, REQ-D3, REQ-F4)

**Phase G.1: Basemap Integration** ⏳ DEFERRED (REQ-G1 — tile providers blocked in current env)

**Phase 4: System Validation (Raanana)** ✓ COMPLETE (May 2026)
- ✓ Hydrogeologist approved Raanana report as submitted — no corrections required
- ✓ Decision: pilot methodology on Holon zone before scaling to all 18 zones

**Phase 5: Zone Application Framework** ✓ FRAMEWORK COMPLETE
- Goal: Validate the methodology works for **any** of the 18 industrial zones
- Framework changes (zone-agnostic):
  - ✓ Pipeline scripts (parse_excel, preprocess, trend_analysis, forensics_analyzer, generate_charts_v2,
    select_boreholes, validate_report) — all accept `--zone <id>`
  - ✓ Per-zone Excel column mapping via `config/zone_overrides/{zone}.yaml`
  - ✓ Generic data-driven charts (auto-pick top-contaminated boreholes per family)
  - ✓ Borehole selection persistence via `selected_boreholes.json`
- First framework application — Holon V4.2 (stress-test):
  - ✓ 112 boreholes parsed → 111 selected (Tier 2 polygon), 4,762 trend pairs
  - ✓ Cross-zone param-family classifier (`scripts/param_families.py`)
  - ✓ Charts produced; HOLON_REPORT_V4.md drafted (awaiting hydrogeologist approval)
  - **Note**: Holon V4.2 served as a stress-test of the prompt-driven pipeline. Future zones will use V5 hybrid pipeline (see Phase H+ below) — Holon is **not** the binding template.

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

## 8. Adding a New Zone — V5 Hybrid Pipeline (Binding Methodology)

The framework supports any of the 18 industrial zones in the coastal aquifer monitoring system.
**Going forward, every new zone uses the V5 hybrid pipeline** (defined in `ZONE_REPORT_PROCESS_GUIDE.md` and the spec files `DATA_PIPELINE_SPEC.md` + `REPORT_V5_SCHEMA.md`).

### SSOT for the process
- `ZONE_REPORT_PROCESS_GUIDE.md` — terminology + 7-step pipeline ordering
- `DATA_PIPELINE_SPEC.md` — schema for the 6 deterministic CSVs (Structured Data Pack)
- `REPORT_V5_SCHEMA.md` — V5 report skeleton (6 sections + focus template)
- `scripts/templates/zone_report_prompt_template_v5.md` — **generic V5 prompt** (6 sections + appendices, context_pack/02_data paths, anchors inputs; REQ #13 closed). The V4-era `zone_report_prompt_template.md` is retained for reference only.
- `scripts/generate_holon_v5_html.py` — V5 HTML generator (renders all sections + injects inline SVG figures at `**איור N**` anchors; reuses `svg_charts.py` engine)
- `scripts/report_designed/README.md` — chart engine docs

### Workflow for a new zone (V5 hybrid — 7 steps)
1. **Define scope** → `{zone}/01_scope/` (zone_wells.csv, selection_notes.md)
2. **Run deterministic data pipeline** → `{zone}/02_data/` (6 CSVs: measurements_scoped, latest_results, severity_by_well_family, trends_by_well_parameter, monitoring_gaps, figure_ready_series — see `DATA_PIPELINE_SPEC.md`)
3. **Assemble scoped NotebookLM-like context** → `{zone}/context_pack/03_context/`:
   - **Reports Context Pack** (required before Zone Diagnosis — do not skip directly from Data Pack to report): `reports_context.md`, `report_sources_index.csv`, `context_questions_for_diagnosis.md`
   - **Source Candidates Pack**: `source_candidates_context.md`, `web_findings_context.md`, `source_candidates_index.csv` — built **from scratch** for new zones. Do NOT assume any pre-existing facility JSON exists. For Holon/Raanana (legacy zones), pre-existing artifacts (`_findings_*.json`, `web_findings.md`) may be used as AI-derived index; `facility_attribution.json` is a derived artifact (multi-step transformation) and is NOT a primary evidence source.
   - **Evidence Classification (A–E)** is a generic rule for all zones — see PROCESS_GUIDE §I "Evidence Classification System":
     - A = raw_report_verified | B = ai_extracted_with_page_ref | C = web_verified_current_activity | D = inferred_candidate | E = weak/mention_only
     - In Zone Diagnosis & V5: A+B → strong candidates; C → status only (no contamination proof); D/E → background/appendix unless monitoring data corroborates
   - Additional: previous_reports_excerpts, hydrogeology_context, approved_precedent_excerpt
4. **Generate zone diagnosis** (Opus call #1) → `{zone}/04_diagnosis/zone_diagnosis.md` (8 professional questions)
5. **Generate V5 expert report** (Opus call #2) → `{zone}/output/{ZONE}_REPORT_V5.md` (6 sections + appendices, per `REPORT_V5_SCHEMA.md`)
6. **Render final figures + HTML** → `scripts/generate_{zone}_full_html.py` + `generate_{zone}_designed.py` (boreholes_override path)
7. **Validate** per PROCESS_GUIDE §VII checklist (including Context Pack, Structured Data Pack, Zone Diagnosis, PFAS logic, monitoring gaps, C_max_5y separation)

### Existing zone-agnostic scripts (used inside Step 2 of V5 pipeline)
The Phase 5 framework provides the deterministic data layer. These scripts feed into Step 2 of the V5 pipeline:

```bash
python scripts/parse_excel.py        --zone <X>   # Step 2a: extract Excel measurements
python scripts/select_boreholes.py   --zone <X> --list-tiers   # Tier 1/2/3 selection → selected_boreholes.json
python scripts/extract_zone_pdfs.py  --zone <X> --include-shared   # idempotent PDF→text
# (AI sub-agents per PDF → <X>/data/external/_findings_<tag>.json)
python scripts/merge_extracted_findings.py --zone <X>   # consolidate per-PDF findings
python scripts/trend_analysis.py     --zone <X>   # Mann-Kendall + SNR
python scripts/forensics_analyzer.py --zone <X>   # decay chains, source signatures
python scripts/generate_charts_v2.py --zone <X>   # generic data-driven charts
```

**Idempotency**: PDF extraction tracks each file in `_pdf_index.json` with `extraction_ok` + `extraction_date_utc`. Re-runs SKIP already-extracted files unless `--force` is passed.

**Per-zone configuration**:
- `config/zone_overrides/<X>.yaml` — Excel column mapping if format differs
- `zone_definitions/zone_polygons.json` — ITM polygon for Tier 2 selection
- `zone_definitions/tier1_historical_boreholes.json` — historical IDs from 2008/2021 reports
- `crosswalks/borehole_id_mapping.json` — optional canonical ID mapping

### AI sub-agent prompt schema (PDF extraction, Step 2 helper)
Each PDF sub-agent (hydrogeologist persona, model="sonnet") produces `_findings_<tag>.json` with: `source_file`, `title_he`, `year`, `author_org_he`, `summary_he`, `boreholes_mentioned[]`, `contamination_findings[]`, `facilities_suspected[]`, `hydrogeology_he`, `trends_described_he[]`, `recommendations_he[]`, `key_quotes_he[]`. See `Holon/data/external/_findings_*.json` for worked examples. Confidence levels (HIGH/MEDIUM/LOW) required on facility attribution.

### Implementation Trigger
- ✓ Methodology validated on Raanana (May 2026, hydrogeologist approval) — **style precedent**
- ✓ V4.2 stress-tested on Holon — **methodological precedent, not a binding template**
- ✓ V5 hybrid pipeline documented (Phase H+, REQ #12 closed)
- ✓ V5 hybrid pipeline implementation (Phase H+ Implementation, REQ #13 closed 2026-05-28 — PR #19 a19a917)
- ⏳ Hydrogeologist review of Holon V5 → systematic application to remaining 16 zones
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

**Per-phase completion** (generic):
1. Code runs without errors on zone test data
2. Data verified against source documents (spot-check ≥10% of rows)
3. Reports: all claims sourced (page numbers cited)
4. Trend calculations match source interpretations or discrepancies flagged
5. Documentation updated (CLAUDE.md, PROCESS_GUIDE, prompt template)

**Framework Success Criteria** (cross-zone — must hold for any zone):
1. ✓ Pipeline scripts accept `--zone <id>` and derive all paths from zone name
2. ✓ Per-zone Excel column mapping configurable (`config/zone_overrides/<zone>.yaml`)
3. ✓ Zone polygon (ITM) intersection drives Tier 2 borehole selection
4. ✓ Generic data-driven charts work without hardcoded borehole IDs
5. ✓ Zone site map computes extent + severity from data
6. ✓ 28 automated tests pass + 3 report validators (chart_refs, tone, attribution)
7. ✓ Documentation describes V5 hybrid pipeline as standard workflow (`ZONE_REPORT_PROCESS_GUIDE.md`)

**Reference Implementation — Raanana V2 (style precedent, all ✓)**:
1. ✓ 7 drilling cards; zone summary report synthesises all data layers
2. ✓ Forensic analysis with HIGH/MEDIUM/LOW confidence levels
3. ✓ PFAS at turbine station flagged for regulatory attention
4. ✓ Zone site map (offline ITM schematic); 9 facility candidates
5. ✓ Expert hydrogeologist review — approved (May 2026)

**Methodological Stress-Test — Holon V4.2** (awaiting hydrogeologist approval):
1. ✓ Pipeline ran end-to-end (parse → trend → forensics → charts)
2. ✓ 112 boreholes parsed → 111 selected; 4,915 CVOC measurements
3. ✓ HOLON_REPORT_V4.md drafted; charts produced
4. ⏳ Hydrogeologist approval
5. **Note**: V4.2 used prompt-driven workflow. New zones use V5 hybrid pipeline (Phase H+).

**Phase H+ — V5 Hybrid Pipeline** ✅ COMPLETE (Documentation + Implementation):
- ✓ Documentation refactor (REQ #12, closed 2026-05-17)
- ✓ Implementation (REQ #13, closed 2026-05-28 via PR #19 / a19a917): data pipeline scripts (7 CSVs), context assembly, zone diagnosis prompt, V5 report prompt, Structured Anchors pilot (#13.5, PASS), Holon V5 generation (164KB+177KB MD/HTML)
- ✓ Executive summaries (REQ #15): INTERNAL + PUBLIC HTML
- ✓ Report engine (REQ #16): 14-file generic architecture
- ✓ Brief + Twin HTML generators (REQ #17, #18)
- ✓ Toolkit system (REQ #19, sanitization sub-task complete): 3 tiers (skills + pylib + 5 playbooks)
- ⏳ Hydrogeologist review of Holon V5 (next step)

**Open framework items**:
- ⏳ Basemap integration (REQ-G1) — pending environment resolution
- ⏳ Holon V5 generation (after REQ #13)
- ⏳ After Holon V5 validation → systematic activation of remaining 16 zones

---

## 12. Requirements Tracking (Sustainable)

**Rule**: `PROCESS.md` (top-level) is the **SSOT for active requirements**. It tracks Open requirements (to do) and Closed requirements (audit trail).

### Workflow

1. **בתחילת כל סשן**: קרא `PROCESS.md` (אוטומטי דרך session-start hook). אם יש Open items — התחל מהן.
2. **דרישה חדשה** (מהמשתמש או מבדיקה): הוסף שורה ל-טבלת Open ב-`PROCESS.md` **לפני שמתחילים לעבוד**.
3. **בסיום משימה**:
   - העבר שורה מ-Open ל-Closed
   - הוסף commit hash + שיטת אימות
   - commit message: `[PROCESS.md] closed #N` או `[PROCESS.md] added #N`
4. **לפני commit כללי**: ודא ש-`PROCESS.md` משקף את המצב.

### למה זה קריטי

תכניות בצ'אט נעלמות אחרי context compression. **PROCESS.md הוא הזיכרון הקבוע** — כל שינוי בדרישות חייב לעבור דרכו.

### מבנה הקובץ

```markdown
## דרישות פתוחות (Open)
| # | בעיה | תיאור | סטטוס | תאריך | קבצים |

## דרישות סגורות (Closed) — Audit Trail
| # | בעיה | תאריך סגירה | commit | אימות |
```

ראה `PROCESS.md` להמשך.

---

**Project Status**:
- Framework (Phases A–G): ✓ Complete — pipeline zone-agnostic, validated on Raanana, expert-approved
- Phase 5 (Zone Application Framework): ✓ Complete on framework side; Holon V4.2 as stress-test (awaiting hydrogeologist)
- Phase H+ (V5 Hybrid Pipeline): ✅ COMPLETE — Documentation (REQ #12) + Implementation (REQ #13, PR #19 merged 2026-05-28 / a19a917)
- Phase 2 (full 18-zone activation): ⏳ Pending Holon V5 hydrogeologist sign-off + Ministry coordination

**Last Updated**: 2026-05-28 (Phase H+ Implementation COMPLETE via PR #19 / a19a917 — Holon V5 + Toolkit + Engines + Governance all merged to main)  
**Historical phases**: see `docs/HISTORY.md`
