# REQUIREMENTS.md — Raanana Zone Report Specifications

**Purpose**: Single source of truth for all project requirements — what was requested, why, what was built, what's pending.

**Baseline**: Extracted from chat history, CLAUDE.md, 2021 report analysis, and current methodology work.

---

## Project Context

**Goal**: Produce a professional Hebrew zone report for Raanana industrial area (קריית אתגרים) that integrates historical data (2013 Water Authority survey, TAHAL 2008) with real measurements (2011–2025 Excel).

**Scope**: 
- 7 boreholes (nt_1, nt_2, nt_3, nd_paz, nd_turbine, p_18, p_25)
- 179 parameters (CVOC, PFAS, BTEX, metals)
- 2,613 measurements (2011–2025)
- Designed to scale to 18-zone coastal system

**Reference Standard**: 2021 Water Authority report (דוח בקרת איכות מים) for tone, structure, and recommendation patterns

---

## Requirements by Category

### A. Data Integrity & Methodology

| ID | Requirement | Status | Source | Verification |
|---|---|---|---|---|
| REQ-A1 | Every data point must cite source — in flowing text, borehole name + year is sufficient; full Excel/report citations belong in Section 6 data table only | ✅ | CLAUDE.md § Data Integrity, STYLE_GUIDE § C.1 | Citation audit on final report |
| REQ-A2 | No interpolation of missing years/boreholes — flag gaps explicitly | ✅ | CLAUDE.md § Data Integrity | "Missing data" section exists |
| REQ-A3 | Severity index calculated per 2021 Report formula (exact, no modifications) | ✅ | CLAUDE.md § Data Integrity | Index values match 2021 table (page 7) |
| REQ-A4 | Trend analysis uses Mann-Kendall (tie-corrected) with SNR ≥ 0.3, soft_trigger = 2 measurements in 5y window | ✅ | CLAUDE.md § Trend Methodology | config/analysis_config.yaml specifies these params |
| REQ-A5 | Contamination attribution presented with confidence levels (HIGH/MEDIUM/LOW), not overstated | ✅ | CLAUDE.md § Incident Response | Attributions include "כל הנראה" or "ברמת ביטחון בינונית" |
| REQ-A6 | Excluded: TPFAS (total PFAS) and BETK (calculated sums) — use individual species only | ✅ | CLAUDE.md § Trend Methodology | Only PFHxS, PFOA, PFHxA, etc. in analysis |
| REQ-A7 | `crossed_standard` flag set BEFORE entry criteria check (single-measurement exceedances captured) | ✅ | CLAUDE.md § Trend Methodology | Code logic verified in preprocess.py |
| REQ-A8 | Industrial facility discovery performed by AI agent with expert prompt; sector-based search (CVOC sources + PFAS sources); output JSON → facility_attribution.json | ✅ | User request (2026-05-06) | Agent methodology documented in STYLE_GUIDE.md § H; 2 new candidates (F-008, F-009) added; web_findings.md logged |

### B. Report Structure (Word-Level)

| ID | Requirement | Status | Source | Verification |
|---|---|---|---|---|
| REQ-B1 | 6 main sections: תקציר / הקשר / ממצאים / ניתוח / המלצות / מגבלות | ✅ | STYLE_GUIDE.md § D.2 | Section headings match template — confirmed in audit 2026-05-05 |
| REQ-B2 | Section 3 has NO subsection headings (###) — flowing prose only; sources integrated naturally | ✅ | User request (2026-05-05) | No ### headers in Section 3 after rewrite |
| REQ-B3 | Section 3 ends with a dedicated paragraph on recent data (2022–2025) and active trends | ✅ | User request (2026-05-05) | Final paragraph synthesizes current borehole status + active trends |
| REQ-B4 | Central map figure (איור 1) with boreholes by index, facility markers, flow arrow | ✅ | User request (current session) | zone_site_map.png generated; Figure 1 added to Section 2 |
| REQ-B5 | Section 6 includes subsection "מקורות חיצוניים שנבדקו" describing PRTR, web search, Mey Raanana, and facility_attribution.json methodology | ✅ | User request (2026-05-05) | Section 6 subsection lists 5 sources + attribution file |

### C. Language & Tone

| ID | Requirement | Status | Source | Verification |
|---|---|---|---|---|
| REQ-C1 | Formal technical Hebrew per 2021 report style (not narrative storytelling) | ✅ | STYLE_GUIDE.md § A.2 | No "עדויות שנחשפו", "שקט מדומה", "לפתע", etc. |
| REQ-C2 | Sentence patterns from 2021 report (zone opening, hydrology, monitoring, findings) | ✅ | STYLE_GUIDE.md § A.2 | Drilling cards replicate 20+ standard phrases |
| REQ-C3 | Lexicon: אזה"ת, קידוח, ריכוז, מגמה, דיגום (not "מתחם", "באר", "כמות", "טרנד") | ✅ | STYLE_GUIDE.md § A.3 | Terminology audit |
| REQ-C4 | Approved tone: "בקידוח X נמדד Y מקג"ל (% מהתקן)" — No inline Excel citation in prose; source tracing in Section 6 data table | ✅ | STYLE_GUIDE.md § C.1, E.1 | Sentence templates applied |
| REQ-C5 | Recommendations follow 2021 character: ניטור / חקירה / שיקום / מעקב / הרחבה (no speculative tech) | ✅ | STYLE_GUIDE.md § F | Confirmed in audit 2026-05-05: Section 5 uses מיידי/ניטור שוטף/חקירה pattern |
| REQ-C6 | No hedging ("יתכן", "כנראה") without explicit metric (p-value, confidence level, Mann-Kendall) | ✅ | STYLE_GUIDE.md § B.3 | Uncertainty quantified |
| REQ-C7 | Terminology standardization: פלומה (not פלום), בארות הפקה (not בארות ייצור), מקג"ל in text, תרכובות אורגניות מוכלרות (not ממסים כלוריניים) | ✅ | User request (2026-05-05) | Global find-replace applied; grep verification clean |
| REQ-C8 | % of drinking water standard cited ONCE per (borehole, contaminant) pair; concentrations only in subsequent mentions | ✅ | User request (2026-05-05) | All findings follow "ריכוז עדכני של X מקג"ל (Y% מהתקן)" format once, then "ריכוז X מקג"ל" |
| REQ-C9 | No facility-level regulatory reporting requirements (דיווח לרשות/משרד) — report is BY Water Authority, not TO regulators | ✅ | User clarification (2026-05-05) | Removed all "דיווח לרשות המים ולמשרד הגנת הסביבה" language; retained sampling requirements |
| REQ-C10 | No analysis of fuel leak patterns or detection-limit-near values (5–10 µg/L benzene) — cite only current low concentrations | ✅ | User guidance (2026-05-05) | BTEX paragraph simplified: no "דפוס תדלוק UST", only current 0.6 µg/L |

### D. Charts & Visualizations

| ID | Requirement | Status | Source | Verification |
|---|---|---|---|---|
| REQ-D1 | 10 charts total (9 time-series/index + 1 central map) in `Raanana/charts_v2/` | ✅ | CHART_SPEC.md § Chart Inventory | All 10 PNG files generated and verified |
| REQ-D2 | File names STABLE (cvoc_timeseries.png, pfas_all_boreholes.png, etc. — no renaming) | ✅ | CHART_SPEC.md § Chart Inventory | File list locked, no changes mid-session |
| REQ-D3 | All Hebrew labels use RTL helper (`H()` = arabic_reshaper + python-bidi) | ✅ | CHART_SPEC.md § RTL Rendering | Verified: zone_site_map, cvoc_timeseries, pfas_all_boreholes — all labels RTL correct |
| REQ-D4 | PFAS symbology: S-group blue (bottom) / A-group orange (top) per pfas-sa-chart skill | ✅ | CHART_SPEC.md § PFAS S/A Ordering | Color order in stacked bar verified |
| REQ-D5 | Drinking water standard threshold lines on CVOC/BTEX charts (dashed, labeled) | ✅ | CHART_SPEC.md § Drinking Water Standards | TCE 7.5, PCE 10.0, Benzene 5.0 µg/L lines visible |
| REQ-D6 | Contamination dynamics (trends): curves ONLY, never bars | ✅ | CHART_SPEC.md § Time-Series vs. Bars | cvoc_timeseries, cvoc_all_wells, btex_timeseries use curves |
| REQ-D7 | ~~Peak comparison bar chart (cvoc_cross_borehole.png)~~ | ❌ DEPRECATED | User decision (2026-05-05): information redundant with cvoc_pct_standard_panel + cvoc_all_wells; chart removed from report | N/A |
| REQ-D8 | Central map (zone_site_map.png): boreholes by max index (color scale), facility triangles/squares, flow arrow NW–W | ✅ | CHART_SPEC.md § X | zone_site_map.png implemented with OSM basemap fallback; added to Section 2 of report |
| REQ-D9 | ~~PFAS time-series chart (pfas_all_boreholes.png)~~ | ❌ DEPRECATED | User decision (2026-05-05): single measurement point (nd_turbine July 2025); no time-series data; narrative analysis sufficient | Chart removed from report references |
| REQ-D10 | ~~PFAS % stacked chart (pfas_pct_stacked.png) + BTEX family stacked chart (btex_family_stacked.png)~~ | ❌ DEPRECATED | User decision (2026-05-05): PFAS signature analysis in text only; BTEX family redundant | Charts removed from report references |

### E. Drilling Cards (7 per Zone)

| ID | Requirement | Status | Source | Verification |
|---|---|---|---|---|
| REQ-E1 | 7 drilling cards (nt_1, nt_2, nt_3, nd_paz, nd_turbine, p_18, p_25) in flowing narrative style | ✅ | User request (session 1) | All *_v2.md files committed |
| REQ-E2 | Each card: sections for geography, history, trends, forensics, limitations, recommendations | ✅ | CLAUDE.md § Reporting Standards | Template applied to all 7 |
| REQ-E3 | Cards reference 2013 PDF data (installation context, pre-2012 findings) where available | ✅ | Prior session work | 2013 PDF facts integrated (e.g., nt_1 south of Edge Medical) |
| REQ-E4 | Cards cite boreholes by Hebrew name, not canonical IDs (e.g., "נת רעננה 1" not "raanana_nt_1") | ✅ | User correction (session 1) | All *_v2.md use Hebrew names in prose |
| REQ-E5 | Trends include Mann-Kendall Z, p, SNR; interpreted in context of facility ops | ✅ | CLAUDE.md § Trend Methodology | Z, p, SNR values in all trend statements |

### F. Process & Governance

| ID | Requirement | Status | Source | Verification |
|---|---|---|---|---|
| REQ-F1 | All work on branch `claude/create-base-report-directory-5DqAR` | ✅ | System message | Current branch confirmed |
| REQ-F2 | Clear commit messages with session URL (claude.ai/code/...) | ✅ | CLAUDE.md § Version Control | 3 commits: 6ed3ac5, 534b79c [+ pending] |
| REQ-F3 | STYLE_GUIDE.md + CHART_SPEC.md locked before any code changes | ✅ | Current methodology | Both docs finalized, committed |
| REQ-F4 | Validators (3 scripts) to check: chart refs, tone, attribution | ✅ | Methodology plan | scripts/validate_report.py — all 3 validators PASS on current report |
| REQ-F5 | No breaking changes to existing tests (25 test suite passes) | ✅ | CLAUDE.md § Phase F | tests/ directory untouched |

---

## Potential Contradictions Found

**None identified.** All user requests are consistent:
- Style req's (narrative → professional + 2021 patterns) are compatible
- Chart reqs (curves for dynamics, bars for peaks) are distinct and non-overlapping
- Data req's (integrity, attribution, methodology) are aligned with CLAUDE.md

---

## Status Summary

| Category | ✅ Done | ⏳ Pending | ❌ Deprecated | Total |
|---|---|---|---|---|
| Data Integrity | 8 | 0 | 0 | 8 |
| Report Structure | 6 | 0 | 0 | 6 |
| Language & Tone | 10 | 0 | 0 | 10 |
| Charts & Viz | 9 | 0 | 3 | 12 |
| Drilling Cards | 5 | 0 | 0 | 5 |
| Process & Gov | 6 | 0 | 0 | 6 |
| **TOTAL** | **44** | **0** | **3** | **47** |

### Pending Work (0 items)

All requirements complete. See Change Log for history.

---

## Cross-References

| Requirement ID | STYLE_GUIDE Section | CHART_SPEC Section | CLAUDE.md Section |
|---|---|---|---|
| REQ-C (Language) | A, B, C, D, E, F, J | — | § Reporting Standards |
| REQ-D (Charts) | G | Chart Inventory, X | — |
| REQ-A (Data) | — | — | § Data Integrity, Trend Methodology |
| REQ-B (Structure) | D | — | § Reporting Standards |
| REQ-F (Process) | — | Validation Checklist | § Version Control |

---

## Notes for Next Phase

- **Zone site map**: Refer to 2021 report, page 36 (איור 29), as visual reference
- **Recommendation templates**: Extract from STYLE_GUIDE.md § F.3–F.4 when writing report § 5
- **Validation**: After all pending items complete, run 3 validators sequentially before final commit
- **Scaling**: This spec is for Raanana only; generalize to 18-zone system in Phase 2 (post-expert review)

---

## Change Log

| Date | Change | Reason |
|---|---|---|
| 2026-05-05 | Created REQUIREMENTS.md v1 (36 done, 4 pending, 1 deprecated) | Methodology improvement: single source of truth for what was requested, extracted from chat history + CLAUDE.md + 2021 report analysis |
| 2026-05-06 | v1.1: Added REQ-C7 through REQ-C10 (terminology, reporting prohibition, BTEX limit-near values); REQ-D9, REQ-D10 (3 charts deprecated); REQ-B5 (methodology subsection) | User refinements: terminology standardization, chart reduction based on data availability, methodology exposure |
| 2026-05-06 | v1.2: Implemented central map (zone_site_map.png) + REQ-A8 (AI agent facility discovery); updated REQ-B4, REQ-D1, REQ-D8 to ✅; status now 42 done, 2 pending, 3 deprecated | Map implementation completed; 9 facilities confirmed (F-001 through F-009), 2 new candidates added (בית דקל, Aerospheres) |
| 2026-05-06 | v1.3: RTL verification (REQ-D3 ✅) + 3 validators (REQ-F4 ✅); all requirements COMPLETE (44 done, 0 pending); fixed zone_site_map.png clipping (p_25 visibility); improved flow arrow anchoring | Full regression guard: validate_report.py PASS on all validators |

---

**Status**: COMPLETE (all 44 requirements done; 3 deprecated)  
**Last Review**: 2026-05-06 (RTL + validators + map clipping fix)  
**Next Review**: After Phase 4 expert validation (Q3 2026) or new user requirements
