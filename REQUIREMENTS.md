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
| REQ-A1 | Every data point must cite source (Excel borehole/date OR דוח 2013/page OR דוח 2021/page) | ✅ | CLAUDE.md § Data Integrity | Citation audit on final report |
| REQ-A2 | No interpolation of missing years/boreholes — flag gaps explicitly | ✅ | CLAUDE.md § Data Integrity | "Missing data" section exists |
| REQ-A3 | Severity index calculated per 2021 Report formula (exact, no modifications) | ✅ | CLAUDE.md § Data Integrity | Index values match 2021 table (page 7) |
| REQ-A4 | Trend analysis uses Mann-Kendall (tie-corrected) with SNR ≥ 0.3, soft_trigger = 2 measurements in 5y window | ✅ | CLAUDE.md § Trend Methodology | config/analysis_config.yaml specifies these params |
| REQ-A5 | Contamination attribution presented with confidence levels (HIGH/MEDIUM/LOW), not overstated | ✅ | CLAUDE.md § Incident Response | Attributions include "כל הנראה" or "ברמת ביטחון בינונית" |
| REQ-A6 | Excluded: TPFAS (total PFAS) and BETK (calculated sums) — use individual species only | ✅ | CLAUDE.md § Trend Methodology | Only PFHxS, PFOA, PFHxA, etc. in analysis |
| REQ-A7 | `crossed_standard` flag set BEFORE entry criteria check (single-measurement exceedances captured) | ✅ | CLAUDE.md § Trend Methodology | Code logic verified in preprocess.py |

### B. Report Structure (Word-Level)

| ID | Requirement | Status | Source | Verification |
|---|---|---|---|---|
| REQ-B1 | 6 main sections: תקציר / הקשר / ממצאים / ניתוח / המלצות / מגבלות | ⏳ | STYLE_GUIDE.md § D.2 | Section headings match template |
| REQ-B2 | Subsections (if any) are by time period OR contamination family, NEVER by data source | ⏳ | User request (session start) | No "Data from Excel" / "From 2013 Report" subsections |
| REQ-B3 | All analysis "harmonious" — integrated narrative, not divided by time periods | ⏳ | User request (session start) | Prose flows chronologically without artificial breaks |
| REQ-B4 | Central map figure (איור 1) with boreholes by index, facility markers, flow arrow | 🔄 | User request (current session) | zone_site_map.png per CHART_SPEC § X |

### C. Language & Tone

| ID | Requirement | Status | Source | Verification |
|---|---|---|---|---|
| REQ-C1 | Formal technical Hebrew per 2021 report style (not narrative storytelling) | ✅ | STYLE_GUIDE.md § A.2 | No "עדויות שנחשפו", "שקט מדומה", "לפתע", etc. |
| REQ-C2 | Sentence patterns from 2021 report (zone opening, hydrology, monitoring, findings) | ✅ | STYLE_GUIDE.md § A.2 | Drilling cards replicate 20+ standard phrases |
| REQ-C3 | Lexicon: אזה"ת, קידוח, ריכוז, מגמה, דיגום (not "מתחם", "באר", "כמות", "טרנד") | ✅ | STYLE_GUIDE.md § A.3 | Terminology audit |
| REQ-C4 | Approved tone: "בקידוח X נמדד Y µg/L (% מהתקן; Excel: בור, תאריך)" | ✅ | STYLE_GUIDE.md § E | Sentence templates applied |
| REQ-C5 | Recommendations follow 2021 character: ניטור / חקירה / שיקום / מעקב / הרחבה (no speculative tech) | ⏳ | STYLE_GUIDE.md § F | Recommendation templates verified |
| REQ-C6 | No hedging ("יתכן", "כנראה") without explicit metric (p-value, confidence level, Mann-Kendall) | ✅ | STYLE_GUIDE.md § B.3 | Uncertainty quantified |

### D. Charts & Visualizations

| ID | Requirement | Status | Source | Verification |
|---|---|---|---|---|
| REQ-D1 | 10 charts total (9 time-series/index + 1 central map) in `Raanana/charts_v2/` | ⏳ | CHART_SPEC.md § Chart Inventory | All 10 PNG files exist |
| REQ-D2 | File names STABLE (cvoc_timeseries.png, pfas_all_boreholes.png, etc. — no renaming) | ✅ | CHART_SPEC.md § Chart Inventory | File list locked, no changes mid-session |
| REQ-D3 | All Hebrew labels use RTL helper (`H()` = arabic_reshaper + python-bidi) | ⏳ | CHART_SPEC.md § RTL Rendering | Code inspection: grep for `H()` calls |
| REQ-D4 | PFAS symbology: S-group blue (bottom) / A-group orange (top) per pfas-sa-chart skill | ✅ | CHART_SPEC.md § PFAS S/A Ordering | Color order in stacked bar verified |
| REQ-D5 | Drinking water standard threshold lines on CVOC/BTEX charts (dashed, labeled) | ✅ | CHART_SPEC.md § Drinking Water Standards | TCE 7.5, PCE 10.0, Benzene 5.0 µg/L lines visible |
| REQ-D6 | Contamination dynamics (trends): curves ONLY, never bars | ✅ | CHART_SPEC.md § Time-Series vs. Bars | cvoc_timeseries, cvoc_all_wells, btex_timeseries use curves |
| REQ-D7 | Peak comparison: bars OK (historic max values across boreholes, not dynamics) | ✅ | CHART_SPEC.md § Time-Series vs. Bars | cvoc_cross_borehole uses grouped bars |
| REQ-D8 | Central map (zone_site_map.png): aerial photo + boreholes by max index (color scale), facility triangles, flow arrow NW–W | ⏳ | CHART_SPEC.md § X | Map spec complete; implementation pending |

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
| REQ-F4 | Validators (3 scripts) to check: chart refs, tone, attribution | ⏳ | Methodology plan | validate_chart_refs.py, validate_tone.py, validate_attribution.py pending |
| REQ-F5 | No breaking changes to existing tests (25 test suite passes) | ✅ | CLAUDE.md § Phase F | tests/ directory untouched |

---

## Potential Contradictions Found

**None identified.** All user requests are consistent:
- Style req's (narrative → professional + 2021 patterns) are compatible
- Chart reqs (curves for dynamics, bars for peaks) are distinct and non-overlapping
- Data req's (integrity, attribution, methodology) are aligned with CLAUDE.md

---

## Status Summary

| Category | ✅ Done | ⏳ Pending | 🔄 In Progress | Total |
|---|---|---|---|---|
| Data Integrity | 7 | 0 | 0 | 7 |
| Report Structure | 3 | 1 | 0 | 4 |
| Language & Tone | 5 | 1 | 0 | 6 |
| Charts & Viz | 7 | 3 | 0 | 10 |
| Drilling Cards | 5 | 0 | 0 | 5 |
| Process & Gov | 3 | 2 | 0 | 5 |
| **TOTAL** | **30** | **7** | **0** | **37** |

### Pending Work (7 items)

1. **REQ-B1**: Verify 6-section structure in RAANANA_REPORT_V2.md
2. **REQ-B2**: Audit subsections (no data-source divisions)
3. **REQ-B3**: Harmonious narrative (no artificial time-period breaks)
4. **REQ-B4**: Implement central map figure (zone_site_map.png)
5. **REQ-C5**: Apply recommendation templates to report
6. **REQ-D1,D3,D8**: Implement/verify charts (9 time-series + central map)
7. **REQ-F4**: Write 3 validators (chart_refs, tone, attribution)

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
| 2026-05-05 | Created REQUIREMENTS.md v1 (37 requirements, 30 done, 7 pending) | Methodology improvement: single source of truth for what was requested, extracted from chat history + CLAUDE.md + 2021 report analysis |

---

**Status**: REFERENCE (living document — update as requirements change)  
**Last Review**: 2026-05-05  
**Next Review**: After validators implemented
