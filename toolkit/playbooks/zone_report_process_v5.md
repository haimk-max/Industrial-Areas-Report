# Playbook: V5 Hybrid Pipeline for Zone Reports

> **תהליך מחייב** לדוח אזור (zone report) באמצעות הpipeline ההיברידי (משולב).

## מבנה כללי

```
7 שלבים (7 steps):

1️⃣  Define Scope       → zone/01_scope/zone_wells.csv
2️⃣  Data Pipeline      → zone/02_data/ (6 CSVs, deterministic)
3️⃣  Assemble Context   → zone/03_context/ (NotebookLM-style)
4️⃣  Zone Diagnosis     → zone/04_diagnosis/zone_diagnosis.md
5️⃣  V5 Report          → zone/output/ZONE_REPORT_V5.md (Opus call)
6️⃣  Render Figures     → Inline SVG, HTML designed
7️⃣  Validate           → Checklist (7 criteria)
```

---

## שלב 1️⃣: Define Scope

**Input**: Zone definition (ITM polygon, historical borehole list)  
**Output**: `zone/01_scope/zone_wells.csv`

### Borehole Selection (3-Tier)

**Tier 1 — Historical Boreholes**
- From TAHAL 2008 / 2021 Report
- Always included (known baselines)
- Example: holon_nt_1, holon_nt_2, holon_nt_3, ... (5–10 boreholes)

**Tier 2 — Polygon Boreholes**
- Fall within zone ITM polygon (±500m tolerance)
- Measured in past 5 years
- At least one non-fuel contaminant measurement
- Example: additional 40–80 boreholes

**Tier 3 — Cross-Zone Monitoring**
- Boreholes just outside polygon but showing relevant signal
- Use sparingly (2–5 boreholes)

### CSV Template

```csv
borehole_canonical_id,name_he,itm_east,itm_north,depth_m,layer,selection_tier
holon_nt_1,נת חולון 1,171234,556789,45,unconfined,1
holon_nt_2,נת חולון 2,171456,556890,50,confined,1
holon_nt_3,נת חולון 3,171678,557012,48,unconfined,1
holon_p_25,מק חולון 25,172100,557500,55,unconfined,2
...
```

---

## שלב 2️⃣: Data Pipeline

**Input**: Excel measurements + scoped boreholes  
**Output**: 6 CSVs in `zone/02_data/`

### 6 CSVs (Structured Data Pack)

**1. measurements_scoped.csv**
- All measurements for scoped boreholes
- Columns: borehole_id, date, parameter, concentration, unit, source

**2. latest_results.csv**
- Most recent measurement per (borehole, parameter) pair
- Columns: borehole_id, parameter, latest_date, concentration, c_max_5y, dws

**3. severity_by_well_family.csv**
- Severity bucket per (borehole, contamination_family) pair
- Columns: borehole_id, family (CVOC/METALS/PFAS/FUEL), max_bucket, crossed_standard_count

**4. trends_by_well_parameter.csv**
- Mann-Kendall trend results
- Columns: borehole_id, parameter, trend (ALERT/WATCH/STABLE), z_score, p_value, snr, slope

**5. monitoring_gaps.csv**
- Boreholes with long silence periods
- Columns: borehole_id, last_measurement_date, months_silent, previous_max_bucket, last_concentration

**6. figure_ready_series.csv**
- Time series for chart rendering (one row per measurement)
- Columns: borehole_id, parameter, date, concentration, c_max_5y_at_date, bucket_at_date

### Scripts to Run

```bash
# Parse Excel → raw measurements
python scripts/parse_excel.py --zone holon --output 02_data/

# Preprocess + normalize units
python scripts/preprocess_measurements.py --zone holon

# Trend analysis (Mann-Kendall)
python scripts/trend_analysis.py --zone holon

# Severity calculation + forensics
python scripts/forensics_analyzer.py --zone holon

# Generate aggregates (6 CSVs)
python scripts/generate_data_pack.py --zone holon
```

---

## שלב 3️⃣: Assemble Context

**Input**: Zone folder (PDFs, Excel, prior reports)  
**Output**: `zone/03_context/` (5 folders)

### Context Assembly (NotebookLM-style)

Use skill: `/<agent-rag> --zone <zone_id> --task assemble`

Or manual assembly:

**3.1 reports_context.md**
- Key excerpts from PDFs (with page numbers)
- Hydrogeology summary
- Historical contamination events
- Facility operations notes

**3.2 facility_attribution.md**
- List of suspected source facilities
- Evidence per facility (HIGH/MEDIUM/LOW confidence)
- Location, operation type, contaminants, timeline

**3.3 web_findings.md**
- Current facility status (active, closed, remediated?)
- News/public records of spills
- Regulatory history
- Source: Google search, news databases, govt records

**3.4 hydrogeology.md**
- Aquifer depth, flow direction, velocity
- Seasonal variations
- Aquitard/confining layers
- Relevant data from TAHAL 2008

**3.5 context_questions_for_diagnosis.md**
- 8 guiding questions for the next step (Zone Diagnosis)
- Example:
  1. What is the primary contamination source?
  2. Is the contamination plume stable or expanding?
  3. Are there multiple independent sources?

---

## שלב 4️⃣: Zone Diagnosis

**Input**: Context assembly (from Step 3)  
**Output**: `zone/04_diagnosis/zone_diagnosis.md`

### 8 Professional Questions (Manual / AI-Assisted)

Hydrologist/expert fills in answers:

1. **Primary Contamination Source**  
   Which facility/event caused the main detected contaminants?

2. **Plume Behavior**  
   Expanding, stable, or shrinking?

3. **Multiple Sources?**  
   How many independent contamination foci?

4. **Uncertainty & Confidence**  
   What's still unknown?

5. **Seasonal / Operational Links**  
   Does contamination correlate with facility operations?

6. **Monitoring Adequacy**  
   Which zones need more boreholes?

7. **Remediation Potential**  
   Is source remediation feasible?

8. **Regulatory Status**  
   Any pending violations or cleanup orders?

### Output Template

```markdown
# Zone Diagnosis: Holon (May 2026)

## 1. Primary Contamination Source
**Answer**: TCE plume originates from Albit (tediran) electroplating facility.
**Confidence**: HIGH (TAHAL report + web search corroborate)

## 2. Plume Behavior
**Answer**: Stable for 3 years; no new boreholes with exceedances outside historical polygon.
**Confidence**: MEDIUM (only 15% of zone monitored)

...
```

---

## שלב 5️⃣: V5 Report (Opus)

**Input**: Data Pack (Step 2) + Context + Diagnosis (Steps 3–4)  
**Output**: `zone/output/ZONE_REPORT_V5.md`

### V5 Report Schema (6 Sections + Appendices)

**I. Executive Summary**
- 2–3 paragraphs
- Key findings: contamination foci, severity, trend
- Regulatory status

**II. Hydrogeologic Setting**
- Aquifer geometry, flow, geology
- Seasonal variations
- Relevance to contamination transport

**III. Contamination Findings**
- Per family (CVOC, METALS, PFAS, FUEL)
- Severity distribution (how many boreholes in each bucket?)
- Spatial patterns (maps, clustering)

**IV. Contamination Foci & Attribution**
- 3–5 main sources (HIGH confidence)
- Evidence per source
- Confidence levels (HIGH/MEDIUM/LOW)

**V. Trends & Monitoring Gaps**
- Boreholes with significant trends (ALERT / WATCH)
- Long silence periods (monitoring gaps)
- Recommendations for enhanced monitoring

**VI. Recommendations**
- Immediate (2026)
- Short-term (2026–2027)
- Long-term (2027+)
- Per-facility if applicable

**Appendices**:
- A. Borehole Summary Table (severity, family, trend)
- B. Facility Attribution Confidence Matrix
- C. Data Limitations & Assumptions
- D. References & Source Documents

### Opus Prompt

Use: `scripts/templates/zone_report_prompt_template_v5.md`

Includes XML tags:
```xml
<context_pack_path>/home/user/Industrial-Areas-Report/holon/03_context/</context_pack_path>
<data_pack_path>/home/user/Industrial-Areas-Report/holon/02_data/</data_pack_path>
<zone_diagnosis_path>./04_diagnosis/zone_diagnosis.md</zone_diagnosis_path>
```

---

## שלב 6️⃣: Render Figures & HTML

**Input**: V5 Report + Data Pack  
**Output**: HTML + inline SVG charts

### Scripts

```bash
# Generate diagnostic figures (pre-report)
python scripts/generate_charts_v2.py --zone holon --style diagnostic

# Generate V5 HTML (Opus report → structured HTML)
python scripts/generate_holon_v5_html.py

# Designed variant (summary visual)
python scripts/generate_holon_v5_html_designed.py
```

### Output Files

```
zone/output/
├── ZONE_REPORT_V5.md                 (Markdown report)
├── ZONE_REPORT_V5.html               (Full HTML, ~180KB)
├── ZONE_REPORT_V5_DESIGNED.html      (Visual summary, ~120KB)
└── figures/
    ├── holon_severity_map.svg
    ├── holon_family_distribution.svg
    ├── holon_trend_timeline.svg
    └── ...
```

---

## שלב 7️⃣: Validate

**Input**: V5 Report + HTML  
**Output**: Validation checklist (✓ PASS / ✗ FAIL)

### 7-Point Validation

| # | Criterion | Check |
|---|-----------|-------|
| 1 | **Context Pack** | All 5 files present (reports_context.md, web_findings.md, etc.) |
| 2 | **Data Pack** | All 6 CSVs generated; no missing values in critical columns |
| 3 | **Zone Diagnosis** | 8 questions answered by expert |
| 4 | **PFAS Logic** | PFAS boreholes correctly identified; gaps noted |
| 5 | **Monitoring Gaps** | All boreholes silent > 12 months listed |
| 6 | **C_max_5y Separation** | Latest results don't contradict trends |
| 7 | **HTML Renders** | Charts display; no broken links |

### Validation Script

```bash
python scripts/validate_report.py --zone holon --report-path zone/output/ZONE_REPORT_V5.md
```

---

## Timeline

| Phase | Duration | Task |
|-------|----------|------|
| **Scope + Data** | 2–3 days | Select boreholes, run data scripts |
| **Context Assembly** | 3–5 days | Manual + AI (PDFs, web search) |
| **Zone Diagnosis** | 2–3 days | Expert fills in 8 questions |
| **V5 Report** | 1 day | Opus call + validation |
| **Rendering** | 1 day | HTML + charts |
| **Total** | **1–2 weeks** | From definition to final HTML |

---

## Checklist for Implementation

- [ ] Step 1: Define scope (ITM polygon, historical boreholes)
- [ ] Step 2: Run data pipeline (6 CSVs)
- [ ] Step 3: Assemble context (5 folders, NotebookLM-style)
- [ ] Step 4: Zone Diagnosis (8 questions answered)
- [ ] Step 5: V5 Report (Opus call)
- [ ] Step 6: Render figures + HTML
- [ ] Step 7: Validate (7-point checklist)
- [ ] Commit to git

---

**Last Updated**: 2026-05-27  
**Status**: ✓ TEMPLATE DEFINED (Implementation in progress)
