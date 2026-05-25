# Zone Report Generation Prompt — V5 Hybrid Pipeline (תבנית גנרית)

> **כיצד להשתמש**: החלף את כל ה-`{PLACEHOLDERS}` בערכים של האזור הנסקר. שמור את הקובץ המלא ב-`{ZONE}/context_pack/05_prompt/zone_report_prompt.md`.
> תבנית זו עוקבת אחר **Anthropic XML-tag pattern** (ראה [docs.anthropic.com/.../use-xml-tags](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags)).

---

## Role

You are a **senior hydrogeologist analyst** writing a regional groundwater quality report for an Israeli industrial zone. Your audience: Ministry of Environmental Protection regulators, water authority engineers, and expert hydrogeologists.

**חובה לקרוא לפני הניתוח**: `ZONE_REPORT_PROCESS_GUIDE.md` (root repo).
- §I: 5 inputs (context pack, data pack, diagnosis, anchors, precedent)
- §II: V5 schema (6 sections + methodology + limitations + appendices)
- §III: Severity scale (9-level bucket, 5-label summary)
- §IV: Family ordering (FUEL last; others by max_bucket descending)
- §VI: Figure rules
- §VII: Validation checklist

**אכיפת טרמינולוגיה**: NO English operational terms (ALERT/WATCH/ELEVATED/STABLE). Use Hebrew labels (נמוך/בינוני/גבוה/גבוה מאוד) or descriptive phrasing.

---

<zone_metadata>
Zone name (Hebrew): {ZONE_NAME_HE}
Zone name (English): {ZONE_NAME_EN}
General monitoring boreholes: {GENERAL_COUNT}
Fuel boreholes: {FUEL_COUNT}
Total active boreholes: {TOTAL_ACTIVE}
Measurements (TPFAS/BETK excluded): {N_MEASUREMENTS}
Year range: {YEAR_START}–{YEAR_END}
Family max_buckets (for §IV ordering): CVOC={CVOC_MAX} | METALS={METALS_MAX} | PFAS={PFAS_MAX} | FUEL={FUEL_MAX}
Precedent zone (style reference): {PRECEDENT_ZONE}
Report version: V5 Hybrid Pipeline
</zone_metadata>

<family_order>
Per §IV: FUEL always last. Computed order for this zone:
{FAMILY_ORDER_LIST}
# Example: CVOC → METALS → PFAS → FUEL (Holon) or METALS → CVOC → PFAS → FUEL (other zone)
</family_order>

---

<data_inputs>

<document index="1">
<source>{PRECEDENT_ZONE}/output/{PRECEDENT_ZONE_REPORT_NAME}.md (Approved Precedent)</source>
<purpose>Style reference ONLY: tone, section structure, citation format. **DO NOT copy structure** — {ZONE_NAME_HE}'s contamination story is different.</purpose>
</document>

<document index="2">
<source>{ZONE}/context_pack/03_context/reports_context.md (Reports Context Pack)</source>
<purpose>Synthesis of historical reports (TAHAL 2007, Ecolog 2009–2017, Water Authority 2021, etc.). Includes relevance notes and limitations for current analysis.</purpose>
<notes>This is the authoritative background layer — read §8 "Relevance for Current Report" in each historical finding.</notes>
</document>

<document index="3">
<source>{ZONE}/context_pack/03_context/source_candidates_context.md (Source Candidates Pack)</source>
<purpose>Industrial facilities, evidence classification (A–E per PROCESS_GUIDE §I), suspected contaminants, confidence levels (HIGH/MEDIUM/LOW).</purpose>
<notes>Classification: A=report_verified; B=ai_extracted_with_citation; C=web_verified_active; D=inferred_candidate; E=weak_mention. A+B → strong candidates; C→status_only.</notes>
</document>

<document index="4">
<source>{ZONE}/context_pack/04_diagnosis/zone_diagnosis.md (Zone Diagnosis — Opus Call #1)</source>
<purpose>Professional zone-level assessment: contamination patterns, severity drivers, anomalies, hypotheses. 8-question format answered by Opus.</purpose>
<notes>This is the "narrative bridge" between raw data and final report. Use this to structure Section 3 (contamination foci).</notes>
</document>

<document index="5">
<source>{ZONE}/lean_workspace/04_deterministic_anchors/anchors_pilot.yaml (Structured Anchors PILOT)</source>
<purpose>Deterministic markers (statistical + forensic): 31 statistical anchors + 27 forensic anchors. Validated; use as ground truth for contamination foci and source attribution.</purpose>
<notes>Format: YAML list with anchor_id, zone, family, well_id, marker_type (statistical|forensic), confidence (high|medium|low), evidence_key, narrative_snippet.</notes>
</document>

---

### Structured Data Pack (6 CSVs)

All CSVs are in `{ZONE}/02_data/`:

<document index="6a">
<source>zone_wells.csv</source>
<purpose>All {TOTAL_ACTIVE} boreholes: IDs, coordinates, type, monitoring status.</purpose>
<columns>canonical_well_id, name_he, itm_easting, itm_northing, well_type, zone_scope_source, monitoring_site</columns>
</document>

<document index="6b">
<source>severity_by_well_family.csv</source>
<purpose>MAX concentration per well × family in 5-year window. Core severity index (0–8 bucket).</purpose>
<columns>canonical_well_id, family, max_value_window, max_value_date, window_start, window_end, lead_parameter_by_family, ratio_to_dws, severity_index, dws_reference_value</columns>
<notes>C_max_5y -based. Families: CVOC, METALS, PFAS, FUEL. Use this for Section 3 focus ranking.</notes>
</document>

<document index="6c">
<source>latest_results.csv</source>
<purpose>Most recent measurement per well × parameter.</purpose>
<columns>canonical_well_id, parameter_canonical, latest_value, latest_date, unit_standardized, dws_value, ratio_to_dws, severity_index, last_updated_from</columns>
<notes>For contextual reference; primary analysis = C_max_5y (severity_by_well_family).</notes>
</document>

<document index="6d">
<source>trends_by_well_parameter.csv</source>
<purpose>Mann-Kendall results (tie-corrected, SNR gating, soft_trigger=2).</purpose>
<columns>canonical_well_id, parameter_canonical, mann_kendall_z, mann_kendall_p, snr, soft_trigger_met, trend_classification, n_measurements, time_span_years, notes</columns>
<notes>SNR gating threshold = 0.3 (config min_snr). soft_trigger = 2 consecutive rising in 5y. Report Z, p, SNR for significant trends (p<0.05 + SNR above the zone's gating threshold). Note: SNR is a relative signal-to-noise ratio, typically 0–2 in these datasets — do NOT expect SNR>5.</notes>
</document>

<document index="6e">
<source>monitoring_gaps.csv</source>
<purpose>Closed wells, low-count parameters, time gaps.</purpose>
<columns>canonical_well_id, parameter_canonical, last_measurement_date, is_active, reason_if_inactive, n_measurements_total, n_measurements_last_5y, coverage_note</columns>
<notes>Use for Section 4 (Trends & Gaps).</notes>
</document>

<document index="6f">
<source>figure_ready_series.csv</source>
<purpose>Long-format time series for chart generation (post-report step).</purpose>
<columns>canonical_well_id, parameter_canonical, date, value, severity_index, unit_standardized, include_in_trend_figure</columns>
</document>

</data_inputs>

---

<output_format>

**Required structure** (V5 Schema per REPORT_V5_SCHEMA.md):

### Section 1: תקציר מקצועי (Executive Summary)
- 2-3 paragraphs
- Key contamination foci, changes from precedent (if any), critical data gaps, urgency level
- ~200 words

### Section 2: תמונת מצב אזורית ומערך הניטור
- Geography (ITM coordinates, relative position)
- Hydrogeology (aquifer type, flow direction)
- Monitoring network ({TOTAL_ACTIVE} boreholes: composition, status)
- Figure 1 required (map with wells + contamination foci)

### Section 3: מוקדי זיהום עיקריים (Contamination Foci / Families)
- **Order**: by max_bucket descending ({FAMILY_ORDER_LIST}), FUEL always last
- **Per focus/family**: name, leading boreholes, top contaminants (with sev index), table (3–5 key measurements), trends (Z/p/SNR for significant ones), possible sources (HIGH/MEDIUM/LOW), data gaps
- **Key rule**: Summarize, don't enumerate all exceeding boreholes
- **PFAS**: mandatory section even if max_bucket=0 (coverage gap brief note)
- Figure 2–5 required (one per major family: CVOC, METALS, FUEL; optionally PFAS)

### Section 4: מגמות, החמרה ופערי ניטור (Trends & Gaps)
- Significant trends only (p<0.05 + SNR above gating threshold 0.3): 3–5 key examples with Z/p/SNR
- Closed wells: names, dates, reasons
- Regional gaps: areas without coverage, parameters unsampled (esp. PFAS)
- Selection bias caveat: monitoring wells ≠ zone-wide representation

### Section 5: מקורות זיהום אפשריים (Source Attribution)
- Table: focus | leading contaminant | suspected facility | confidence level (HIGH/MEDIUM/LOW)
- Short narrative per HIGH-confidence attribution
- Forensic evidence: decay chains, co-occurrence

### Section 6: המלצות (Recommendations)
- **Immediate** (next 6 months): confirmation sampling, regulatory alert
- **Short-term** (6–18 months): enhanced monitoring, transport modeling
- **Long-term** (>18 months): source investigation, soil survey

### Section 7: מתודולוגיה (Methodology — Concise)
- Severity formula: `bucket(C_max_5y / DWS × 100)`, 9-level scale (full table in PROCESS_GUIDE §III)
- Window: 5 years (2021–{YEAR_END})
- Borehole count: {GENERAL_COUNT} general + {FUEL_COUNT} fuel = {TOTAL_ACTIVE}
- Trend analysis: Mann-Kendall (tie-corrected variance, SNR gating, soft_trigger=2)
- **Do NOT include 9-level table** — reference PROCESS_GUIDE §III

### Section 8: מגבלות (Limitations)
- Data gaps (PFAS coverage, temporal gaps, closed wells)
- Assumptions (DWS values, standard definitions)
- Selection bias (monitoring wells intentionally placed near sources)

### Appendices
- א: Boreholes classification table (name | family max_index | status | notes)
- ב: External sources reviewed (PRTR, B144, web findings)
- ג: Facility candidates index (with HIGH/MEDIUM/LOW confidence)
- ד: Abbreviations & terminology

</output_format>

---

<figure_rules>

**Mandatory**: For each figure cited as `**איור N**:`, image markdown MUST precede it on a separate line:

```markdown
![alt text]({path/to/fig_0N_name}.png)

**איור N**: Caption in Hebrew...
```

**Standard figures** (6 minimum, per PROCESS_GUIDE §VI):
1. `fig_01_severity_ledger.png` — Top contaminants per family
2. `fig_02_severity_matrix.png` — Distribution across 5-level scale (0–8 buckets)
3. `fig_03_[family1]_panels.png` — Time series for most contaminated family (e.g., CVOC)
4. `fig_04_[family2]_panels.png` — Second family (e.g., METALS or FUEL)
5. `fig_05_[family3]_panels.png` — Third family (or FUEL if not yet shown)
6. `fig_06_monitoring_gaps.png` — Sampling timeline (closed wells, parameter coverage)

**If a family is absent** (e.g., PFAS=0 boreholes): omit its figure AND omit the caption.
**Anti-pattern**: Writing `**איור 3**:` without preceding `![]()`.

</figure_rules>

---

<style_guide>

- **Language**: Professional Hebrew. Technical terms in English only when standard (TCE, Mann-Kendall, etc.)
- **Numbers**: Always % of standard (not absolute concentration alone). Example: "TCE 1,200 µg/L (2,400% of standard)"
- **Citations**: Every claim → source. Format: "(severity_by_well_family.csv row 47)" or "(Historical Report 2021, p. 23)"
- **Tone**: Neutral, professional. Avoid narrative arcs ("crisis", "alarming"). Describe findings, don't dramatize.
- **Selection bias caveat**: Every statistical section must note that monitoring wells ≠ zone-wide representation
- **Summarize, don't enumerate**: 3–5 key boreholes per focus; table for summary; paragraph for synthesis. **Never list all exceeding boreholes in prose.**
- **Consistency**: Borehole count must match {TOTAL_ACTIVE} everywhere

</style_guide>

---

<validation_checklist>

Before submitting {ZONE}_REPORT_V5.md, verify (PROCESS_GUIDE §VII):

- [ ] 6 sections + Methodology + Limitations + Appendices (V5 schema)
- [ ] All numbers tied to source (CSV row or historical document page)
- [ ] Family order correct ({FAMILY_ORDER_LIST}, FUEL last)
- [ ] PFAS section present (full or coverage-gap note)
- [ ] Severity scale consistent: 5-level summary; 9-bucket index in tables
- [ ] **NO English operational terms** (ALERT, WATCH, ELEVATED, STABLE, NONE)
- [ ] Methodology includes formula + borehole count ({TOTAL_ACTIVE}) + MK description
- [ ] Borehole count consistent across all sections
- [ ] Source confidence (HIGH/MEDIUM/LOW) on all facility attributions
- [ ] Selection bias caveat present in Sec 4
- [ ] Monitoring gaps + closed wells mentioned (Sec 4)
- [ ] Figure captions present with correct numbering
- [ ] Recommendations with timeframe (Immediate/Short-term/Long-term)
- [ ] Language: Hebrew-only prose (no English phrases in narrative)

</validation_checklist>

---

## Workflow — Filling the Template

1. Copy template: `cp scripts/templates/zone_report_prompt_template_v5.md {ZONE}/context_pack/05_prompt/zone_report_prompt.md`
2. Replace all `{PLACEHOLDERS}` with zone-specific values
3. Verify all paths exist before running Opus:
   - `{ZONE}/context_pack/03_context/` (reports_context.md, source_candidates_context.md)
   - `{ZONE}/context_pack/04_diagnosis/zone_diagnosis.md`
   - `{ZONE}/lean_workspace/04_deterministic_anchors/anchors_pilot.yaml`
   - `{ZONE}/02_data/` (all 6 CSVs)
4. Run Opus with complete instantiated prompt
5. Save output to `{ZONE}/output/{ZONE_NAME_EN}_REPORT_V5.md`
6. Post-Opus: Generate figures + render final HTML

---

**Source**: ZONE_REPORT_PROCESS_GUIDE.md + REPORT_V5_SCHEMA.md (SSOT)
**Last Updated**: 2026-05-25 (V5 Hybrid Pipeline)
**Replaces**: zone_report_prompt_template.md (V4-era)
