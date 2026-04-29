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

**Phase 4: System Validation** (IN PROGRESS)
- Goal: Generate R-002, R-003, R-005 drilling cards; validate against expert review
- Plan:
  1. Complete R-002, R-003, R-005 drilling cards → Verify coverage of all boreholes
  2. Generate per-parameter summary tables → Verify trend calculations match zone report
  3. Create CLAUDE.md project governance → Verify alignment with best practices
  4. Schedule expert review → Coordinate with hydrogeologist and regulatory contact
  5. Integrate 2021 measurements → Validate trend continuation/reversal

---

## 5. Project-Specific Guidelines

### Data Integrity Rules
1. **Source Attribution Mandatory**: Every data point must cite original source (TAHAL page, 2021 Report page)
2. **No Interpolation**: Missing years/boreholes represented as NULL; never extrapolate historical data
3. **Severity Index Immutable**: Use exact formula from 2021 Report; no modifications without expert approval
4. **Forensics Probabilistic**: Contamination attribution presented with confidence level (HIGH/MEDIUM/LOW)
5. **Cross-Reference Validation**: When integrating TAHAL 2008 and 2021 data, flag discrepancies for expert review

### Reporting Standards
1. **Drilling Card Format**: Header (ID, coordinates, depth, classification) → Geology → Contamination trends → Forensics → Recommendations
2. **Trend Interpretation**: State trend mathematically (slope, R²), then interpret in context of facility operations
3. **Risk Communication**: Use matrix format with weighted factors; final score ranges 1-10
4. **Recommendation Hierarchy**: Immediate (2024-2026), Medium-term (2026-2030), Long-term (2030+)
5. **Limitations Statement**: Every report section that relies on assumptions includes "Limitations" callout

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

### Current State (Raanana Only)
- 1 zone, 5 boreholes, 3 parameters, 1999-2008 historical data
- Manually created CSVs and reports
- Ad-hoc consolidation script

### Scalability Plan (18 Zones)
- **Data**: Extend boreholes.csv and concentrations.csv with zone column
- **Scripts**: Modify consolidate_data.py to accept `--zone` parameter
- **Templates**: Reuse drilling_card_R-001.md format for all boreholes
- **Automation**: Create zone_summary_generator.py to batch-produce zone reports
- **No new schemas**: Current design supports full 18-zone expansion

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
1. ✓ All 5 Raanana boreholes have drilling cards
2. ✓ Zone summary report synthesizes all data layers
3. ✓ Forensic analysis links contaminants to source facilities with confidence levels
4. ✓ Risk matrix calculated and validated
5. ✓ 2021 baseline integrated and compared with historical
6. ✓ Expert hydrogologist review completed
7. ✓ System designed to scale from 1 zone (Raanana) to 18 zones without redesign
8. ✓ CLAUDE.md and project governance documented

---

**Project Status**: Phase 3 Complete (R-001, R-004 drilling cards + zone summary) | Phase 4 In Progress  
**Last Updated**: April 29, 2026  
**Next Review**: May 15, 2026 (Phase 4 milestone: R-002, R-003, R-005 cards complete)
