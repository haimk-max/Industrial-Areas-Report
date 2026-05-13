# מדריך עקרונות — דוחות אזורי תעשייה (Zone Reports Framework)

**מטרה**: עקרונות מפנה (compass points) לכל דוח אזורי תעשייה, מבוסס על Holon V4 iterations. לא טוקסונומיה — טו־דלת־טו־שלוש משפטים לכל עקרון.

**Scope**: Holon + מעבר ל-18 אזורים (אם יתקבל אישור מומחה).

---

## I. קלטים ל-Opus (לפני הריצה)

### קלט 1: Precedent Report (Approved)
- **מה**: דוח אזור אחר שהאושר על ידי hydrogeologist
- **למה**: Style reference (tone, section structure, citation format)
- **דוגמה**: Raanana V2 עבור Holon

### קלט 2: Authority Documents (Direct Excerpts)
- **מה**: עמודים ממשפחה מפורסמת (תה"ל 2007, הנדסה 2009-2017, רשות המים 2021) — לא paraphrases
- **למה**: Historical context, contamination types, facility names
- **דוגמה**: דוח רשות 2021 עמ' 35-49 (גיאוגרפיה, severity)

### קלט 3: Statistical Brief (Structured Text)
- **מה**: סיכום קריא של trends + severity distribution — **לא raw CSV**
- **למה**: Opus יכול להתמקד בממצאים, לא ב-parsing
- **דוגמה**: "ALERT Boreholes (25/80): CVOC max 8,750% (בורה X, 2024); Trends INCREASING (19): TCE +5%, Cr +12%, Benzene flat"

### קלט 4: Forensics Brief (Optional, As-Needed)
- **מה**: Decay chains, co-occurrence patterns, source signatures — ברמת overview בלבד
- **למה**: Only if meaningful patterns exist (not per-finding, not mandatory)
- **דוגמה**: "PCE→TCE→cis-DCE chain active (3 wells, p<0.01); Cr+Ni co-occurrence suggests plating facility (5 wells)"

### קלט 5: Facility Candidates (Updated from Web Search)
- **מה**: `facility_candidates_[ZONE].md` — גם HIGH מ-PDFs אומתו עדכנים; + תוצאות web search (PRTR, דיווח שפכים)
- **למה**: Sourcing guidance עם confidence levels (HIGH/MEDIUM/LOW)
- **דוגמה**: "אלגונל (HIGH, confirmed address, ציפוי מתכת) | PFHxS מגורם דיגום Holon Q3 2025 עתידי"

---

## II. Opus Output Structure (Mandatory Framework)

### Section 1: Executive Summary (Findings, Not Narrative Arc)
- ממצאים עיקריים: בורה, מזהם, ריכוז (% of standard), תאריך
- שנויו מ-baseline (אם רלוונטי)
- ללא "סיפור שנה מסוימת"

### Section 2: Geographic Context (+ Map Figure)
- Hydrogeology, flow direction, facilities identified
- **Methodology** של facility discovery (which reports, PRTR result, web search queries)

### Section 3-5: Contamination Analysis
- **Order by environmental significance, not data volume**:
  1. CVOC (halogenated solvents — high persistence, slow decay)
  2. METALS (if meaningful data)
  3. FUEL (if meaningful data; note as localized/expected)
  4. PFAS (only if >10 samples zone-wide AND max_bucket ≥1; else omit)
- **Per family**: current findings + trends (Z, p, SNR) + decay chains (if active) + source hypotheses

### Section 6: Trends & Temporal Patterns
- Statistical findings from trends_alert.csv (Mann-Kendall results)
- **Deep-dive Forensics** only where justified (e.g., rapid rise + biotic decay chain)
- Cite: "Mann-Kendall Z=X, p=Y, SNR=Z; declining/stable/rising over [timeframe]"

### Section 7: Limitations & Data Gaps
- Monitoring interruptions (closed wells)
- Low sample counts (n < 5 measurements per parameter)
- Selection bias caveat (monitoring wells ≠ zone-wide distribution)

### Section 8: Recommendations
- **Structure**: Immediate (30-90d) | Ongoing (2026-2027) | Investigation (2027+)
- Specific: borehole name + parameter + sampling frequency

### Section 9: Sources & Confidence Levels
- Table: [Finding] | [Value] | [Source Document] | [Date/Page] | [HIGH/MEDIUM/LOW confidence]

---

## III. Severity Scale (Unified, No Variants)

**Only one scale: 5-level severity index per contamination level (C% / DWS)**

| Index | Label | Definition |
|---|---|---|
| 0 | נקי (Clean) | <10% of drinking water standard |
| 1-3 | נמוך (Low) | 10–100% |
| 4-5 | בינוני (Medium) | 100–1,000% |
| 6-7 | גבוה (High) | 1,000–10,000% |
| 8 | גבוה מאוד (Very High) | >10,000% |

**Terminology enforcement**: Use Hebrew labels only. No 'bucket', no 'ALERT/WATCH/ELEVATED', no 'עקבה'.

---

## IV. Family Ordering (Environmental Priority, Not Data Volume)

**Default order when multiple contamination families present:**

1. **CVOC** — industrial chlorinated solvents (TCE, PCE, 1,4-Dioxane, Chloroform, etc.)
   - Persist years–decades, slow decay, high bioaccumulation risk
   - **Always narrative core** (if data exists)

2. **METALS** — heavy metals (Cr, Ni, Pb, Cd, As, etc.)
   - Persistent, bioaccumulative, redox-sensitive
   - **Second priority** (if data exists and index ≥3)

3. **FUEL** — BTEX, MTBE, Benzene
   - Localized (point-source), faster decay, expected near gas stations
   - **Supplementary** — brief mention, not headline
   - Frame as "fuel-dedicated boreholes" to flag selection bias

4. **PFAS** — per/polyfluoroalkyl substances
   - New compound class (post-2021), emerging concern
   - **Only if** >10 samples zone-wide AND max_bucket ≥1
   - Else: omit entirely (don't force into narrative)

**Rule: Drop families where max_bucket = 0** (no meaningful exceedance). Note omission in methodology.

---

## V. Web Search & Source Attribution (Pre-Opus)

### Step 1: PRTR Registry Check
- Search: National Pollution Release & Transfer Register (PRTR) for zone name
- Document: "PRTR [YEAR]: [query] → [found/not found]; if found: [facility name, reported pollutants]"
- If not found: "Facilities below reporting threshold or don't use PRTR reporting"

### Step 2: Water Authority Report (Sewage Dossier)
- Search: Local water utility sewage dossier for industrial zone
- Document: "תאגיד מי [region] [YEAR]: [facilities reported / no industrial report]"

### Step 3: Web Search (3-6 targeted queries)
- Example searches: "[Zone name] industrial facilities", "[suspected contaminant] manufacturer [region]", "[בעברית] ציפוי מתכת [אזור]"
- Document: "חיפוש Web [YEAR]: [X queries] → [results summary]"
- Verify facility status (active/inactive/relocated)

### Output
- Update `facility_candidates_[ZONE].md` with web search results
- Mark HIGH candidates as "אומתו פעילות" or "הופסקו [year]"
- Add any new MEDIUM candidates discovered

---

## VI. Designed Figures (6 Standard Figures Per Zone)

**Process**: `emit_figures.py` (SVG → PNG via weasyprint + pdftoppm) before Opus call.

**Figures** (from `scripts/report_designed/svg_charts.py`):
1. `fig_01_severity_ledger.png` — Top contaminants per family
2. `fig_02_severity_matrix.png` — Distribution across 5-level scale
3. `fig_03_cvoc_panels.png` — CVOC time series (if data exists)
4. `fig_04_metals_panels.png` — METALS time series (if data exists; rename per zone)
5. `fig_05_fuel_panels.png` — FUEL/BTEX time series (if data exists; rename per zone)
6. `fig_06_monitoring_gaps.png` — Sampling timeline + interruptions

**Role**: Input to Opus (for citation in report) + HTML embedding.

---

## VII. Validation Checklist (Post-Opus, Pre-HTML)

- [ ] No narrative arc ("crisis in 20XX")
- [ ] All numbers tied to source (CSV row, page number, Z/p/SNR)
- [ ] Family order = environmental significance (CVOC → METALS → FUEL → PFAS)
- [ ] PFAS: either meaningful data + section, or omitted entirely (no half-measures)
- [ ] Severity scale = 5-level only (נקי/נמוך/בינוני/גבוה/גבוה מאוד)
- [ ] Source confidence: HIGH/MEDIUM/LOW on all facility attributions
- [ ] Selection bias caveat present (monitoring wells ≠ zone-wide)
- [ ] Monitoring gaps + closed wells mentioned
- [ ] Figures 1-6 referenced (or subsets if family omitted)
- [ ] Recommendations: timeframe structure (Immediate/Ongoing/Investigation)

---

## VIII. Scaling Pattern (For Zone N+1, N+2, …)

1. Extract PDFs + run web search (A: Web Search & Source Attribution)
2. Generate figures from zone-specific data (VI: Designed Figures)
3. Write statistical brief (I: Quilt 3)
4. Build forensics brief if patterns exist (I: Quilt 4, as-needed)
5. Update facility_candidates (I: Quilt 5)
6. Call Opus with 5 quilts + zone_report_prompt.md variant
7. Validate (VII: Checklist)
8. Render HTML (generate_holon_designed.py)

**Precedent for Zone N+1**: Once Zone N passes expert validation, store as `[N+1]/lean_workspace/01_inputs/[N]_approved_precedent.md`.

---

**Status**: Holon V4 (complete, pending expert review) | Scalable to all 18 zones  
**Last Updated**: [date]  
**Governance**: Holon CLAUDE.md + project REQUIREMENTS.md
