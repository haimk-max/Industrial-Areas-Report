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
- **דוגמה**: "קידוחים חורגים מובהקים (25/80): CVOC max 8,750% (בורה X, 2024); מגמות עלייה מובהקות (19): TCE +5%, Cr +12%, Benzene יציב"
- **דרישה — מנין קידוחים**: ה-brief חייב לציין מפורש את **סך כל הקידוחים בתחום** (לפי תוצאת severity_index — למשל "27 קידוחי תעשייה + 53 קידוחי דלק = 80 פעילים"). הדו"ח חייב להתייחס לכלל הקידוחים הללו ולא לתת-קבוצה.

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

### Section 3: Methodology (Mandatory Content)
- **חישוב אינדקס חומרה**: נוסחה מפורשת — `bucket(C_last_since_YEAR / DWS × 100)` עם מיפוי 9 רמות:
  - 0 = ND (לא זוהה)
  - 1 = <10% מהתקן
  - 2 = 10–25%
  - 3 = 25–50%
  - 4 = 50–100%
  - 5 = 100–250%
  - 6 = 250–1,000%
  - 7 = 1,000–2,500%
  - 8 = >2,500%
- **כלל אגרגציה משפחתית**: family_index = max(parameter_index) על כל המזהמים במשפחה
- **מנין קידוחים מפורש**: סך הקידוחים בתחום הדו"ח חייב להופיע בסעיף זה (לדוג' "27 קידוחי תעשייה + 53 קידוחי דלק = 80 פעילים"); הדו"ח חייב להתייחס לכל הקידוחים, ללא סתירות בין סעיפים
- **חלון זמן**: יש לציין את ערך הסף `C_last_since_YEAR` (בד"כ 2018) ואת ההיגיון (מצב נוכחי, לא היסטוריה)
- **שיטת מגמות**: Mann-Kendall עם SNR gating, חלון 5 שנים, soft_trigger=2
- **Caveat סלקטיביות**: קידוחי ניטור ≠ תפוצה אזורית (הקידוחים הותקנו במכוון בסמיכות למקורות חשודים)
- **הימנעות מטרמינולוגיה אנגלית**: לא "ALERT/WATCH/ELEVATED/STABLE/NONE". במקום זאת — labels עבריים (נקי/נמוך/בינוני/גבוה/גבוה מאוד) או ניסוחים תיאוריים ("קידוח חורג מובהק", "קידוח במגמת עלייה מובהקת"). אם נדרשת הגדרה תפעולית (קריטריון אופרטיבי), יש לתעד את המקור שלה (לדוג' "קריטריון = אינדקס משפחה ≥ 7 או מגמת עלייה שחצתה תקן, על פי severity_index_2025_[ZONE].csv").

### Section 4: Contamination Analysis by Family
- **סדר קבוע**: 1. CVOC → 2. METALS → 3. PFAS → 4. FUEL
  - **CVOC** ראשון (ממסים מוכלרים תעשייתיים — ליבת הסיפור)
  - **METALS** שני (מתכות כבדות — עדיפות משנית אם יש נתון משמעותי)
  - **PFAS** שלישי (אם יש נתון משמעותי; אחרת — סעיף קצר על פער כיסוי. **אין להשמיט את הניתוח גם אם max_bucket=0** — מדובר בקבוצת חשיבות גלובלית עולה ו"היעדר ממצא" עצמו הוא ממצא)
  - **FUEL אחרון ומופרד** — מסגור ברור כ-point-source / קידוחי דלק ייעודיים / משלים; **לא הכותרת של הדו"ח**
- **לכל משפחה**: ממצאים נוכחיים + מגמות (Z, p, SNR) + שרשרות דעיכה (אם פעילות) + השערות מקור

### Section 4b: Geographic Foci (אופציונלי)
- **קריטריון הפעלה**: באזור יש ≥3 מוקדי זיהום מובחנים במרחק >500מ' זה מזה, עם חתימות מזהם דומיננטיות שונות
- **לכל מוקד**: שם (לפי רחוב/מפעל), קידוחים, חתימה דומיננטית, מפעלים מיוחסים, סטטוס (פעיל/סגור/שוקם)
- **מתי לדלג**: באזורים קטנים, חד-מוקדיים, או באזורים בהם הגיאוגרפיה כבר שזורה בסעיף 4

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

**Terminology enforcement (אכיפה)**: יש להשתמש ב-labels עבריים בלבד. אסור: 'bucket', 'ALERT/WATCH/ELEVATED/STABLE/NONE', 'עקבה'. במקום ALERT — "קידוח חורג מובהק" או "אינדקס גבוה (≥7)" או "קידוח במגמת עלייה מובהקת" (לפי הקשר). אם דרושה הגדרה אופרטיבית, יש לתעד את המקור (CSV/מסמך) שמייצר אותה.

---

## IV. Family Ordering (Fixed Order)

**סדר קבוע, ללא תלות בנפח נתונים:**

1. **CVOC** — ממסים מוכלרים תעשייתיים (TCE, PCE, 1,4-Dioxane, Chloroform, etc.)
   - מתמידים שנים–עשורים, דעיכה איטית, סיכון ביו-מצטבר גבוה
   - **ליבת הסיפור** תמיד (אם יש נתון)

2. **METALS** — מתכות כבדות (Cr, Ni, Pb, Cd, As, etc.)
   - מתמידות, ביו-מצטברות, רגישות-רדוקס
   - **עדיפות שנייה** (אם יש נתון משמעותי, אינדקס ≥3 בקידוח אחד לפחות)

3. **PFAS** — חומרים פר/פולי-פלואורואלקיליים
   - מחלקת תרכובות חדשה (פוסט-2021), חשש עולה גלובלית
   - **לכלול תמיד**: גם כאשר אין חריגות, יש לכלול סעיף קצר על פער כיסוי (coverage gap). "היעדר נתון" הוא ממצא בעצמו כשהקבוצה מציינת סיכון תעשייתי-היסטורי (קצף כיבוי AFFF, mist suppressants בציפוי).
   - אם יש >10 דגימות אזוריות ו-max_bucket ≥1 — סעיף מלא; אם פחות — תת-סעיף שמתאר את הפער ומקור החשד

4. **FUEL** — BTEX, MTBE, Benzene
   - מקומי (point-source), דעיכה מהירה יחסית, צפוי סביב תחנות דלק
   - **אחרון ומופרד** — קטע משלים, **לא כותרת הדו"ח**
   - יש למסגר כ"קידוחי דלק ייעודיים" כדי לסמן selection bias
   - שיא דלק לא ידחק מקדם CVOC/METALS גם אם הריכוז המוחלט גבוה יותר — זה point-source בעוד CVOC הוא איום אזורי

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

**Process**: `emit_figures.py` (SVG → PNG via cairosvg) before Opus call.

**Figures** (from `scripts/report_designed/svg_charts.py`):
1. `fig_01_severity_ledger.png` — Top contaminants per family
2. `fig_02_severity_matrix.png` — Distribution across 5-level scale
3. `fig_03_cvoc_panels.png` — CVOC time series (if data exists)
4. `fig_04_metals_panels.png` — METALS time series (if data exists; rename per zone)
5. `fig_05_fuel_panels.png` — FUEL/BTEX time series (if data exists; rename per zone)
6. `fig_06_monitoring_gaps.png` — Sampling timeline + interruptions

**Role**: Input to Opus (for citation in report) + HTML embedding.

**RTL Requirements** (for zones in Hebrew-speaking regions):
- כל `<text>` ב-SVG עם תוכן עברי חייב לכלול `direction="rtl"` ו-`text-anchor="end"`
- כותרות ראשיות (chart title): position מימין, יישור לימין
- תוויות צירים (axis labels): RTL, יישור לימין
- אגדה (legend): RTL ordering, יישור לימין
- מספרים + יחידות שמופיעים בתוך טקסט עברי (לדוגמה "27,860 µg/L") — יש לעטוף ב-`<tspan direction="ltr" unicode-bidi="isolate">`

---

## VII. Validation Checklist (Post-Opus, Pre-HTML)

- [ ] No narrative arc ("crisis in 20XX")
- [ ] All numbers tied to source (CSV row, page number, Z/p/SNR)
- [ ] **Family order fixed: CVOC → METALS → PFAS → FUEL** (FUEL אחרון תמיד)
- [ ] PFAS section present (full if max_bucket≥1; coverage-gap analysis if not)
- [ ] Severity scale = 5-level only (נקי/נמוך/בינוני/גבוה/גבוה מאוד)
- [ ] **אין טרמינולוגיה אנגלית** (ALERT/WATCH/ELEVATED/STABLE/NONE) — רק labels עבריים או ניסוחים תיאוריים מתועדים
- [ ] **Methodology כוללת**: נוסחת אינדקס מפורשת, מיפוי 9-רמות, כלל אגרגציה, מנין קידוחים מפורש, חלון זמן
- [ ] **מנין קידוחים עקבי** בין כל הסעיפים (לדוג' 27+53=80 ולא 87 בסעיף 1 ו-80 בסעיף 3)
- [ ] Source confidence: HIGH/MEDIUM/LOW on all facility attributions
- [ ] Selection bias caveat present (monitoring wells ≠ zone-wide)
- [ ] Monitoring gaps + closed wells mentioned
- [ ] Figures 1-6 referenced (or subsets if family omitted)
- [ ] **Geographic Foci (Section 4b)**: present if ≥3 distinct clusters; else justified omission
- [ ] Recommendations: timeframe structure (Immediate/Ongoing/Investigation)
- [ ] **HTML post-processing**: numbers+units+pollutant names wrapped in `<bdi>`; CSS `unicode-bidi: isolate` applied to text containers
- [ ] **SVG figures**: titles/labels RTL when zone is Hebrew-speaking

---

## VIII. Scaling Pattern (For Zone N+1, N+2, …)

1. Extract PDFs + run web search (V: Web Search & Source Attribution)
2. Generate figures from zone-specific data (VI: Designed Figures, RTL enforced)
3. Write statistical brief (I: קלט 3, with explicit borehole inventory)
4. Build forensics brief if patterns exist (I: קלט 4, as-needed)
5. Update facility_candidates (I: קלט 5)
6. Call Opus with 5 קלטים + zone_report_prompt.md variant
7. Validate (VII: Checklist)
8. Render HTML (generate_holon_designed.py) with bidi post-processing

**Precedent for Zone N+1**: Once Zone N passes expert validation, store as `[N+1]/lean_workspace/01_inputs/[N]_approved_precedent.md`.

---

## IX. HTML Output Requirements (Bidirectional Text)

**מטרה**: לחל בעיות רנדור של טקסט מעורב עברית/אנגלית/ספרות (לדוגמה "TCE 27,860 µg/L נמדד בנת חולון 11 בשנת 2012") שהאלגוריתם הביידי-דירקציוני המובנה לא תמיד פותר נכון.

### IX.1 פוסט-עיבוד HTML — `<bdi>` wrapping
ב-`generate_holon_designed.py` או templating layer, יש לעטוף את הסוגים הבאים ב-`<bdi>`:

- **מספרים + יחידות**: `\d[\d,\.]*\s*(?:µg/L|mg/L|ng/L|%|µS/cm|מ"ק|דונם|מ')`
- **סטטיסטיקות**: `Z=X.XX`, `p=X.XXX`, `SNR=X.XX`, `n=X`
- **שמות מזהמים באנגלית**: TCE, PCE, MTBE, BTEX, CVOC, PFAS, PFHxS, PFOA, DCE, VC, DNAPL, AFFF, PVDC, DWS, NMVOC, ITM, PRTR
- **תרכובות מורכבות**: 1,1-DCE, cis-1,2-DCE, trans-1,2-DCE, 1,2-DCA, 1,4-dioxane, CCl₄
- **סמלי מתכות**: Cr, Ni, Pb, As, Fe, Al, Cd
- **שנים בודדות בתוך טקסט**: 2012, 2026 (כאשר לא צמודים לעברית)

### IX.2 CSS Standards
ב-template HTML head:
```css
bdi { unicode-bidi: isolate; }
body, p, li, td, th, h1, h2, h3, h4 { unicode-bidi: isolate; }
[dir="auto"] { unicode-bidi: isolate; }
```

### IX.3 פתרון מבני
- אסור להשתמש ב-`<span dir="ltr">` כברירת מחדל — `<bdi>` בטוח יותר (לא דורש לדעת מראש את הכיוון)
- אסור להוסיף ידנית `&lrm;` או `&rlm;` בתוך טקסט — שימוש ב-CSS+`<bdi>` בלבד
- בטבלאות: `<th>` ו-`<td>` עם תוכן מעורב — `dir="auto"` + `unicode-bidi: isolate`

### IX.4 Validation
לאחר רנדור HTML:
- בדיקה ויזואלית של 5 פסקאות אקראיות (מספר/אנגלית/עברית באותו משפט)
- חיפוש regex לאחר העטיפה: `[֐-׿][^<]*\d` ללא `<bdi>` — חשד לבעיה
- וידוא ש-`<bdi>` ניתן ספירה ≥ מספר המספרים בטקסט המקורי

---

**Status**: Holon V4.1 framework (7-point refinement) | Scalable to all 18 zones  
**Last Updated**: 2026-05-14  
**Governance**: Holon CLAUDE.md + project REQUIREMENTS.md
