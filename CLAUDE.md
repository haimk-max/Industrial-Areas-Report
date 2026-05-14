# CLAUDE.md - Industrial Areas Report Project Governance

## Project Overview
**Title**: Structured Reporting System for Groundwater Quality Monitoring in Industrial Areas  
**Scope**: 18-zone coastal system. Active development on Holon; Raanana frozen as approved precedent.  
**Data Sources**: TAHAL 2007/2008, אקולוג 2009–2017, 2021 Water Quality Report, current monitoring  
**Deliverables**: Drilling cards, zone reports, trend analysis, forensic attribution  
**Timeline**: Phase 1-4 implementation with quarterly review cycles

---

## אינדקס מצב אזורים (Zone Status Index)

| אזור | מצב | מיקום סקריפטים | מיקום פלטים | קישור |
|------|-----|----------------|--------------|-------|
| **רעננה** | V2 מאושר, **קפוא** (legacy precedent) | `Raanana/scripts/` | `Raanana/output/` | — |
| **חולון** | V4.2 ממתין לאישור הידרולוג; פייפליין פעיל | `scripts/` + `scripts/report_designed/` | `Holon/output/` | `Holon/lean_workspace/05_prompt/zone_report_prompt.md` |
| 16 אזורים נוספים | ⏳ Phase 2 (Q3 2026+) | (לבנייה אחר אישור Holon) | (לבנייה) | תבנית: `scripts/templates/zone_report_prompt_template.md` |

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

## 4. Phases — Active & Pending

> תיעוד phases היסטוריים: ראה `docs/HISTORY.md` (Phases 1–4, A–G, G.1).

**Phase H: Holon V4 + Pipeline Refactor** ✓ COMPLETE (May 2026)
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

**Phase 4: System Validation** ⏳ PENDING (Q3 2026)
- Goal: Expert hydrogeologist review; PFAS alert to regulators; boron anomaly investigation
- Plan:
  1. PFAS dip sampling at turbine station — top priority
  2. Expert review of forensic attributions (decay chains, source signatures)
  3. Boron anomaly investigation (2019-07-22 readings at Raanana nt_2, nt_3)
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

## 8. Scaling to Additional Zones

**עוגנים** (SSOT לתהליך):
- `ZONE_REPORT_PROCESS_GUIDE.md` — terminology + pipeline ordering
- `scripts/templates/zone_report_prompt_template.md` — generic prompt (30 placeholders)
- `scripts/report_designed/README.md` — chart engine docs

**Workflow לאזור חדש** (ראה PROCESS_GUIDE §VIII):
1. PDF ingestion → `External Data/{zone}/raw_pdfs/` (PROCESS_GUIDE §I.2)
2. Facility discovery → `facility_candidates_{zone}.md` (PROCESS_GUIDE §I.5, §V — 6 web channels)
3. Data prep → `{zone}/lean_workspace/{02_data_filtered,03_evidence_index,04_deterministic_anchors}/`
4. Fill prompt template → `{zone}/lean_workspace/05_prompt/zone_report_prompt.md`
5. Opus call → `{zone}/output/{ZONE}_REPORT_V4.md`
6. Render → `scripts/generate_{zone}_full_html.py` + `generate_{zone}_designed.py`
7. Validate per PROCESS_GUIDE §VII

**Implementation Trigger**: Phase 4 expert validation on Holon (Q3 2026) + Ministry approval.

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

**Phase 4 (System Validation) — pending criteria**:
- ⏳ Expert hydrogeologist review (Raanana + Holon V4.2)
- ⏳ PFAS regulatory reporting (Raanana turbine station)
- ⏳ Boron anomaly investigation (Raanana nt_2, nt_3)
- ⏳ Basemap integration (REQ-G1)
- ⏳ Phase 2 (16 remaining zones) — gated on Ministry approval

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

**Project Status**: Phase H Complete (Holon V4.2 pipeline + reusable architecture) | Phase 4 Pending Q3 2026  
**Last Updated**: May 14, 2026 (Phase H+: pipeline ordering, SSOT consolidation, figure safety net, CLAUDE.md slim-down)  
**Historical phases**: see `docs/HISTORY.md`
