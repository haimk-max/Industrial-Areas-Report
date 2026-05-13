# מדריך תהליך — דוחות אזורי תעשייה (Generalizable Process)

**מטרה**: תעד את הפעולות, ההנחיות, ותבניות ההחלטה שעלו מ-V4 development (Holon) ויוכלו להחול על כל אזור תעשייה.

**מושא**: אזה"ת חולון, צפוי הרחבה ל-18 אזורים.

---

## חלק א: Inputs Preparation (Before Opus)

### A1. Web Search & Facility Discovery

**מטרה**: לאמת מועמדים מקורות ולחפש מפעלים חדשים שלא היו בסקרים היסטוריים (PDF extraction).

**Execution**:
1. **PRTR Israel** (מאגר פליטות ומעברי מזהמים): חיפוש לפי קוד מחוז או שם אזור
   - תאריך: חפש את השנה הנוכחית -1
   - נתונים: קבלו / לא קבלו דיווח; אם קבלו — מה ודיווח
   - תיעוד: "PRTR Israel [Year]: חפש [query], תוצאה: [found/not found]"

2. **תאגיד מי אזורי** (דיווח שפכים שנתי): בדוק דיווח של תאגיד המים לאזור
   - תאריך: השנה או שנה קודמת
   - נתונים: מפעלים דיווחים, תעשיות, סוגי שפכים
   - תיעוד: "תאגיד מי [region] [Year]: בדוק רשימת מפעלים / שפכים תעשייתיים"

3. **Web search**: 3-6 שאילתות מכוונות
   - דוגמאות: "[Zone name] industrial area facilities", "[Specific suspected contaminant] manufacturer [region]", "[בעברית] מפעל ציפוי / כימי [אזור]"
   - מקורות אמינים: registries, company sites, local news, business directories
   - תיעוד: "חיפוש Web (YYYY): [query] → [results]"

4. **Output**: עדכן את `[ZONE]/lean_workspace/02_data_filtered/facility_candidates_holon.md`
   - הוסף שורה לכל תוצאה חדשה
   - בדוק אם מועמדים HIGH פעילים עדיין (סטטוס מסחרי)
   - סמן shuttered facilities כ-inactive

**דוגמה**: Raanana V2, Section 6 (מקורות חיצוניים שנבדקו)
```
- PRTR Israel 2024: נבדק; אף מפעל קריית אתגרים לא דיווח ב-PRTR
- תאגיד מי רעננה — דיווח שפכים 2025: בדוק; כסומים בלבד
- חיפוש Web (2026): 6 שאילתות; פז הנופר אומתה מסחרית; שאר המפעלים אינם באינדקסים ציבוריים
```

---

### A2. Forensics Analysis — Setup

**מטרה**: הכן סיכום forensic מעבר לקובצי המדיה (measurements/trends).

**Execution**:

1. **Decay Chains** — אם יש שרשרת פירוק (PCE→TCE→cis-DCE→VC):
   - קח את הקידוחים מ-`trends_alert.csv` עם כל חברי השרשרת
   - בנה טבלה:
     ```
     | Borehole | Year | PCE | TCE | cis-DCE | VC | Interpretation |
     |---|---|---|---|---|---|---|
     | נת_חולון_14 | 2024 | 105.5 | 94.8 | 12.3 | 0.5 | Active decay chain; VC emerging |
     ```
   - נתון: קטע מ-`hydrogeology_holon.md` על תנאים anoxic ודעיכה ביוכימית

2. **Co-occurrence Patterns** — כל הזוגות [parameter1, parameter2] שעלו ביחד בקידוחים מרובים:
   - דוגמה: Chromium + Nickel (מפעל ציפוי מתכות יחיד)
   - ראיה: `latest_per_borehole_param.csv` — כמה קידוחים יש שניהם
   - פרשנות: co-occurrence עלול לעיד על מקור משותף

3. **Source Signatures** — "ספר זהות" של מזהם:
   - דוגמה: TCE 90%, cis-DCE 7%, VC 3% = DNAPL site (תוך-חוברי חמצן; דעיכה איטית)
   - דוגמה: Benzene 60%, Toluene 25%, Xylene 15% = gasoline (BTEX ratio)
   - ראיה: `latest_per_borehole_param.csv` + `measurements_alert.csv` (אחוזים)

4. **Relative Timing** — מי בא קודם לקידוח:
   - דוגמה: TCE הופיע בנת_חולון_1 ב-2015; בנת_חולון_2 ב-2017 → זרימה דרומה?
   - ראיה: `measurements_alert.csv` (תאריכים) + `hydrogeology_holon.md` (כיוון זרימה)

**Output**: `[ZONE]/lean_workspace/04_deterministic_anchors/forensics_brief.txt` (טקסט, 200-300 מילים)
```
אזור חולון: 
- TCE→cis-DCE שרשרת פעילה בנת חולון 1 ו-3 (דעיכה ביוכימית)
- Cr+Ni co-occurrence בנת חולון 14 → ציפוי מתכות (HIGH confidence)
- Benzene signature בתחנות דלק: 60% benzene → gasoline (תאימות מקור)
- TCE כניסה לקידוח nt_1 ב-2015, nt_2 ב-2017, p_25 ב-2023 → זרימה SW (match hydrogeology)
```

---

### A3. Contamination Family Order (Context-Dependent)

**עקרון**: בחר סדר **לפי משמעות סביבתית**, לא **לפי מספר בורות או שם אלפבתי**.

**Default order** (אם כל 4 משפחות יש נתונים משמעותיים):
```
1. CVOC — industrial halogenated solvents (TCE, PCE, etc.)
   - עדיפות גבוהה: תופסות גדולות, דעיכה איטית, דעיכה ביוכימית מסוכנת
   
2. PFAS — per/polyfluoroalkyl substances (אם יש >10 דיגומים בסך הקידוחים)
   - עדיפות: persistent, bioaccumulative, new compound class
   - דרישה: אם <10 דיגומים בסך הקידוחים או max_bucket=0 → תאר קצר או דלג

3. METALS — heavy metals (Cr, Ni, Pb, Cd, etc.)
   - עדיפות בינונית: persistent, bioaccumulative, רקע טבעי עלול להתערב

4. FUEL — BTEX, MTBE (Benzene, Toluene, Xylene, MTBE)
   - עדיפות נמוכה: בדרך כלל מקומי (תחנות דלק), קל-דעיכה אנאירובית
```

**Rationale for order**: לא על סמך כמות בורות אלא על סמך **משמעות סביבתית** (risk × persistence × bioaccumulation).

---

## חלק ב: Opus Prompt Inputs

### B1. Five Input Categories (Mandatory)

**יציאה מ-V3 commit (5f21251)**:
> "V3 was generated via a different methodology: a single Opus call given (a) Raanana V2 as a structural precedent, (b) pages 31–32 of the 2021 report as historical context, and (c) a structured brief of trends.csv findings."

**ההנחיה**: תן ל-Opus בדיוק את אלה:

1. **Approved Precedent Report** — קובץ Markdown בשלמותו
   - לדוגמה: `Raanana/output/RAANANA_REPORT_V2.md`
   - תפקיד: "זה היה approved על ידי hydrogeologist; השתמש כ-style/tone/structure precedent"

2. **Historical Authority Documents** — Markdown excerpts מ-PDFs היסטוריים
   - עמודים מס'פריים (לא paraphrases)
   - לדוגמה: דוח תה"ל 2007, עמ' 31-32; דוח רשות המים 2021, עמ' 35, 49
   - תפקיד: קונטקסט היסטורי, סוגי מזהמים כלליים, facilities ראוני-דעד

3. **Structured Statistical Brief** — קובץ טבלה או טקסט מובנה
   - לא raw CSV, אלא סיכום קריא
   - לדוגמה: "ALERT Boreholes (25): CVOC max 8,750% (נת חולון 2, 2022); PFAS max 0% (4 wells); METALS max 1,201% (נד פז סיירים 4); FUEL max 140% (נד פז סיירים 2). INCREASING trends (19): TCE +5%, Benzene flat, Cr +12%. Decay chain active (PCE→TCE) in 2 wells."
   - תפקיד: מתן עובדות crunched כדי שOpus לא יצטרך לפרוס CSV

4. **Forensics Brief** — טקסט מובנה מ-A2 לעיל
   - לדוגמה: "אזור חולון: 3 decay chains פעילות, Cr+Ni co-occurrence → ציפוי מתכות HIGH confidence, BTEX signature → תחנות דלק MEDIUM confidence."
   - תפקיד: להנחות forensics analysis של Opus

5. **Facility Candidates** — `facility_candidates_holon.md`
   - תפקיד: להנחות שיוך מקורות עם רמות ביטחון

### B2. Narrative Structure (From V4 iterations)

**מ-commit a9ff9ac (V4.1 restructure)**:
> "Reordered Section 4: CVOC → METALS → FUEL"

**ההנחיה**: אל תתן ל-Opus חופש מוחלט בסדר. מדריך אותו:
- "Order your findings section by environmental significance, not alphabetical or by borehole count."
- "CVOC typically = primary narrative focus (industrial solvents, slow decay, high risk)"
- "If PFAS has minimal data (<10 wells total, max_bucket=0), describe briefly and move to next family. Don't force it to equal CVOC weight."
- "FUEL usually = secondary to CVOC/METALS (localized, faster decay)"

**ממשקי הנרטיב** (מ-commit d46e4a9):
- **Body text**: "Accessible narrative" — Hebrew prose, readable
- **Statistics**: في appendix table — Z, p, SNR, counts NOT in body prose
- **Citations**: כל מספר עם מקור (trends.csv ref + Z/p, או authority page number)

---

## חלק ג: Constraints & Rules for Opus

### C1. Forensics Constraints

**יש לפרוס ל-Opus בתוך `zone_report_prompt.md`**:

```
### ד. Forensics Analysis — Decay Chains, Co-occurrence, Source Signatures

- **Decay Chains**: If you observe PCE→TCE→cis-DCE progression in the same well over time:
  * Document the chain explicitly (not just "TCE is decreasing")
  * Cite biotic conditions from `hydrogeology_holon.md` (anoxic/aerobic/mixed)
  * Note: cis-DCE formation = active denitrification or sulfate reduction

- **Co-occurrence Patterns**: If Cr + Ni appear in multiple wells together:
  * Suggests shared source (metal plating facility)
  * Cite: [borehole names] + dates + concentrations

- **Source Signatures**: If Benzene:Toluene:Xylene ratio is ~60:25:15:
  * Consistent with gasoline (BTEX signature)
  * Cite: measurement ratios + facility type match

- **Confidence Levels**: Every source attribution must carry HIGH/MEDIUM/LOW:
  * HIGH = geographic + hydrogeology + signature match
  * MEDIUM = 2 of 3 factors
  * LOW = single line of evidence
  * Always note: "Requires additional sampling/interviews for confirmation."
```

### C2. Citation Rules (From zone_report_prompt.md, Section א)

**המתודולוגיה קיימת; פשוט הוסיף עבור Forensics**:
- **Forensic findings** צריכים לצטט כ:
  - "בנת חולון 1 ו-2: TCE→cis-DCE chain (Mann-Kendall Z=1.92, p=0.055 לעלייה ב-cis-DCE), בכפוף להתאמה הידרוגיאולוגית (anoxic conditions per hydrogeology_holon.md)"
  - **לא**: "TCE is degrading" (unspecific)

---

## חלק ד: Validation Checklist (Post-Generation)

### D1. Process Checks

- [ ] **Web search**: PRTR + facility discovery executed and documented
- [ ] **Forensics**: decay chains, co-occurrence, source signatures identified
- [ ] **Family order**: CVOC first (if meaningful), PFAS second (if >10 wells), METALS, FUEL
- [ ] **Precedent used**: Raanana V2 referenced for style
- [ ] **Authority documents**: Excerpts from 2021/2017/2012/2009/2007 reports included
- [ ] **Facility candidates**: updated with web search results + confidence levels
- [ ] **Constraints applied**: citations, forensics, confidence, decay chains all present

### D2. Output Checks (Per zone_report_prompt.md Section א-ח)

- [ ] All claims traced to source (CSV row, trends ref, or page number)
- [ ] All trends with Z, p, SNR (or "insufficient data")
- [ ] All source attributions with HIGH/MEDIUM/LOW + hydrogeological caveat
- [ ] No dropped findings (even if "marginal") — always documented
- [ ] Monitoring gaps (closed wells, low frequency) explicitly noted
- [ ] PFAS status clear: "new since 2021" if applicable; "minimal data" if <10 wells

---

## חלק ה: Scaling to Additional Zones

### E1. Adaptation Pattern (Per Zone)

For zone [N]:
1. Extract PDF reports (TAHAL 2007, engineering firms 2009-2017, water authority 2021)
2. Run `parse_excel.py --zone [N]` to generate measurements_alert.csv
3. Run `trend_analysis.py --zone [N]` to generate trends_alert.csv
4. Run forensics discovery (decay chains, co-occurrence)
5. Run web search (PRTR, facility discovery)
6. Update `facility_candidates_[N].md`
7. Build `forensics_brief_[N].txt`
8. Update `zone_report_prompt.md` with family order for [N]
9. Construct 5 Input Categories (precedent, authority excerpts, statistical brief, forensics brief, facility candidates)
10. Call Opus with prompt + inputs
11. Validate output against checklist D1-D2

### E2. "Approved Precedent" for Zone N+1

Once zone [N] passes expert validation, it becomes the approved precedent for zone [N+1]. Store as:
```
[N+1]/lean_workspace/01_inputs/[N]_approved_precedent.md
```

---

## חלק ו: Summary

**Process Instructions (Zone-Agnostic)**:

| Phase | Input/Output | Responsibility |
|---|---|---|
| A1 | Web search + facility discovery | Human + agent (search tools) |
| A2 | Forensics analysis (decay chains, co-occurrence) | Agent (analysis + brief) |
| A3 | Family order decision | Human (context) or Agent (rule-based) |
| B1-B5 | 5 Input Categories prepared | Agent (compilation) |
| B2, C1-C2 | Constraints documented in zone_report_prompt.md | Human (once, then reused) |
| Opus call | Report generation | Opus (via prompt + inputs) |
| D1-D2 | Validation | Human (checklist) |

---

**Version**: Based on Holon V4 iterations (commits 5f21251, 4163b51, a9ff9ac, d46e4a9, etc.)  
**Status**: Generalizable to all 18 industrial zones (pending expert validation on Holon V4 itself)
