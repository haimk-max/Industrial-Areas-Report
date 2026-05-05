# STYLE_GUIDE.md — שפה, טון וקווים מנחים לדוח רעננה

**Purpose**: Define language register, forbid narrative/storytelling phrasing, and establish formatting rules so all edits maintain professional consistency.

---

## Language Register

### Approved Tone (Reference: 2021 Water Authority Report)
- **Formal technical Hebrew** — words like "ממצאים", "ריכוז", "מגמה", "דיגום", "עלייה", "ירידה", "פלום"
- **Neutral, factual** — no drama, no interpretation beyond data
- **Passive/objective** — "נמדד TCE" (TCE was measured) not "היו לנו תוצאות"
- **Attribution explicit** — every measurement cites source (Excel, דוח 2013, דוח 2021)
- **Direct statements** — "ב-2019 נמדד TCE ב-817 µg/L" not "שנמדדו ריכוזים מדהימים"

### Examples of APPROVED Phrasing

✅ "בדיגום 2015 נמדד TCE ב-607.6 µg/L"  
✅ "ירידה בריכוזי TCE בנת רעננה 1: 147.5 µg/L ב-2022"  
✅ "PCE עלה מ-22.9 µg/L (2017) ל-105.5 µg/L (ספטמבר 2024)"  
✅ "פרופיל ה-PFAS תואם חתימת קצף קיבוי AFFF מהדור הישן"  
✅ "מנוע Mann-Kendall מוגבל ברוב קידוחי CVOC ממיעוט מדידות"  
✅ "ממצא זה מעלה חשש ממשי לאיכות מי השתייה"

---

## FORBIDDEN Phrases & Expressions

### Narrative/Storytelling Words (DO NOT USE)
```
✗ "עדויות שנחשפו"        → USE: "ממצאים שהעלו" or "נתונים המציגים"
✗ "שקט מדומה"           → USE: "ריכוזים נמוכים" or "תקופת יציבות"
✗ "לפתע"                 → USE: "בשנת [X]" or "ב-[תאריך]"
✗ "הדממה הייתה זמנית"   → USE: "[פרטי הנתון]"
✗ "נעצרה הדממה"         → USE: "ריכוזים התחילו להעלות"
✗ "הפלום הגיע למים שעשויים לשתות אותם"  → USE: "TCE זוהה בקידוח ייצור פ רעננה 25"
✗ "שום ממצא קודם לא רמז על כך"  → USE: cite source + methodology explicitly
✗ "בדיעבד", "התברר", "טעיתי", "מעניין"  → USE: factual statements
```

### Emotionally-Loaded Words (AVOID)
```
✗ דרמטי (dramatic)  → factual description
✗ מדהים (amazing)   → measurements with units
✗ חושכת (dark/ominous) → specific risk level or % of standard
✗ חירום (emergency)  → "דיווח לרשות" (reporting requirement)
```

### Hedging / Soft Language (CLARIFY)
```
✗ "יתכן" (maybe)        → USE: "Mann-Kendall p=0.055" (explicit uncertainty metric)
✗ "כנראה" (apparently)  → USE: "תואם חתימת [specific signature]"
✗ "אולי הוא מקור" → USE: "סביר להניח כי" + cite forensic evidence
```

---

## Required Attribution Format

### Excel Measurements
**Pattern**: "Excel: [בור], [תאריך]"

✅ "Excel: נת רעננה 1, 2019-07-22"  
✅ "Excel: פ רעננה 25, 2023-09-11"  

**Full sentence example**:  
"ב-2023 נמדד TCE בפ רעננה 25 ב-9.2 µg/L (Excel: פ רעננה 25, 2023-09-11) — חריגה ראשונה מהתקן בקידוח ייצור זה."

### Historical Reports
**Pattern**: "דוח [שנה] / [משרד], עמ' [page]"

✅ "דוח רשות המים 2013, עמ' 13–19"  
✅ "דוח ניטור 2021 (משרד הגנת הסביבה), עמ' 35–36"  

**Full sentence example**:  
"גרדיאנט הזרימה הכללי הוא צפון-מערב–מערב (דוח 2021, עמ' 35)."

### Data Without Direct Source
**Pattern**: "Excel: [בור], [טווח תאריכים]" or "ממוצע של [N] מדידות"

✅ "טווח TCE בנת רעננה 1: 478–817 µg/L (Excel: נת רעננה 1, 2016–2019)"  
✅ "עלייה של כלורופורם בשלושה קידוחים בו-זמנית (Excel: נת רעננה 2, 3, פ רעננה 25, 2015–2025)"

---

## Section Structure (IMMUTABLE)

### Required Sections
1. **תקציר מנהלים** (Executive Summary)
   - 1–2 ¶ overview + numbered findings (4–5 points)
   - Each finding: 1 sentence, cites value + standard % + source

2. **ההקשר הגיאוגרפי-תעשייתי** (Geographic-Industrial Context)
   - Location, area, geology, flow direction
   - Industrial facilities (name, type, contaminant risk)
   - Suspected plume pathways
   - All cites source + page

3. **ממצאי הניטור — סקירה כרונולוגית** (Monitoring Findings — Chronological Review)
   - Subsections: time periods or events, NOT by source
   - Each subsection: 1–3 paragraphs + relevant chart
   - Chronological order (2003–2011, 2012, 2015–2019, 2019–2024, 2025)

4. **ניתוח המגמות** (Trend Analysis)
   - Subsections by contamination family (CVOC, BTEX, PFAS)
   - Statistical tests named (Mann-Kendall Z, p-value, SNR)
   - Interpretation: what trend + what it means
   - Caveat: sample size, data gaps

5. **המלצות** (Recommendations)
   - Timeline: immediate, short-term, long-term
   - Action + rationale + regulatory requirement (if any)

6. **מגבלות ומקורות** (Limitations and Sources)
   - Data gaps explicitly stated
   - Confidence levels (HIGH/MEDIUM/LOW) for forensic attributions
   - Table of sources (Excel, דוח 2013, דוח 2021, etc.)

### Subsection Rules
- **Don't split by source facility** — split by time or contamination type
- **Never subsection by "before/after" report publication** — that's confusing
- **Do chronological order** for historical narrative (natural flow)

---

## Writing Patterns (Templates)

### Measurement Statement
```
ב-[שנה] נמדד [parameter] ב[בור] ב-[value] µg/L ([% of standard]% מהתקן; Excel: [בור], [תאריך]).
```

**Example**:  
"ב-2019 נמדד TCE בנת רעננה 1 ב-817 µg/L (10,900% מהתקן; Excel: נת רעננה 1, 2019-07-22)."

### Trend Statement
```
[parameter] בנת רעננה [בור] מציג מגמת [עלייה/ירידה] (Mann-Kendall Z=[Z], p=[p], SNR=[SNR]), המאשרת [interpretation].
```

**Example**:  
"cis-1,2-DCE מציג מגמת עלייה בנת רעננה 1 (Mann-Kendall Z=1.92, p=0.055, SNR=1.02), המאשרת פירוק אנאירובי פעיל באקוויפר."

### Data Gap Caveat
```
[analysis] מוגבל [by what] ממיעוט מדידות.
```

**Example**:  
"ניתוח מגמה של TCE בנת רעננה 1 מוגבל בעל מיעוט מדידות בחלון 5 השנים (שתי נקודות בלבד)."

### Forensic Attribution
```
פרופיל [parameter] — [characteristic 1], [characteristic 2] — תואם חתימת [source type] ב[confidence level].
```

**Example**:  
"פרופיל ה-PFAS — דומיננטיות PFHxS על פני PFOS, יחד עם PFOA גבוה — תואם חתימת קצף קיבוי AFFF מהדור הישן (3M FC-203 / Ansul AFFF, שיוצרו לפני 2009)."

---

## Formatting Rules (Markdown)

### Headings
- Level 1 (`#`): Report title only
- Level 2 (`##`): Main sections (תקציר, הקשר, ממצאים, ניתוח, המלצות, מגבלות)
- Level 3 (`###`): Subsections (time periods, contamination families)
- Level 4 (`####`): Not used (if needed, restructure)

### Charts / Figures
**Pattern**: `![Hebrew caption](../charts_v2/filename.png)`

**Rules**:
- Hebrew caption (no English)
- Relative path from report location: `../charts_v2/filename.png`
- Blank line before + after
- Caption describes what data is shown (not "Figure 1" or "Chart A")

**Examples**:
```
![TCE בנת רעננה 1 ו-2, PCE בנת רעננה 3](../charts_v2/cvoc_timeseries.png)

![PFAS — ממצאים לפי קידוח | S-group (כחול) / A-group (כתום)](../charts_v2/pfas_all_boreholes.png)
```

### Tables
**Use sparingly** — mainly for source citations, not for data summary.  
**Format**: Markdown table with Hebrew headers and values.

**Example**:
```
| פריט | ערך |
|---|---|
| נתוני ניטור | Excel: "היסטורית איכות מים לקידוחים — מעודכן לבדיקה.xlsx" (2011–2025) |
| הקשר 2013 | דוח רשות המים 2013 — עמ' 13–19 |
```

### Emphasis
- **Bold** (`**text**`): Important findings, severity levels, yes/no conclusions
- **Italic** (`*text*`): Parameter names, facility names (less common)
- Lists (`-`, `1.`): For multiple findings or steps

---

## Quality Gate Checklist

Before finalizing any section:
- [ ] No forbidden phrases (check against list above)
- [ ] Every numerical value has source attribution (Excel/דוח 2013/דוח 2021)
- [ ] Every claim traces to cited source + page number
- [ ] All chart references use correct file names (from CHART_SPEC.md)
- [ ] All Hebrew text uses formal register (not conversational)
- [ ] No hedging language ("אולי", "כנראה") without explicit uncertainty metric
- [ ] Statistical tests named with Z, p, SNR values
- [ ] Trend interpretation distinguishes data from inference
- [ ] Data gaps and confidence levels stated explicitly
- [ ] Section structure matches IMMUTABLE template

---

## Examples: Good vs. Bad

### Example 1: Measurement
❌ **Bad**: "בשנות ה-2000 מתעד סקר היסטורי של נוכחות מזהמים."  
✅ **Good**: "הסקר ההיסטורי שבוצע בידי רשות המים לפני הקמת מערך הניטור (דוח 2013, טבלה 5, עמ' 19) מתעד נוכחות מזהמים עוד בשנות ה-2000."

### Example 2: Trend
❌ **Bad**: "למרבה ההפתעה, ריכוזי TCE התחילו לרדת."  
✅ **Good**: "מ-2019 ואילך נרשמת ירידה בריכוזי TCE בנת רעננה 1: 147.5 µg/L ב-2022 ו-94.8 µg/L ב-2025. ירידה זו אינה מאושרת סטטיסטית בשל מיעוט מדידות בחלון 5 השנים (שתי נקודות בלבד), אך היא ניכרת ויזואלית."

### Example 3: Forensics
❌ **Bad**: "זה בטוח AFFF, זה בעצם מתחנת הטורבינות."  
✅ **Good**: "פרופיל ה-PFAS — דומיננטיות PFHxS על פני PFOS, יחד עם PFOA גבוה — תואם חתימת קצף קיבוי AFFF מהדור הישן (3M FC-203 / Ansul AFFF, שיוצרו לפני 2009). מקור הזיהום המשוער הוא שימוש היסטורי בקצף AFFF בתחנה."

### Example 4: Caveat
❌ **Bad**: "אנחנו לא בטוחים גם כן."  
✅ **Good**: "שיוך המקורות לרמת מפעל ספציפי נשמר ברמת ביטחון **בינונית** — ללא דיגום פנים-מפעלי לא ניתן להכריע."

---

## Reference Documents

- **2021 Water Authority Report** (משרד הגנת הסביבה) — tone, terminology
- **2013 Water Authority Survey** (דוח 2013) — terminology, section structure
- **CLAUDE.md** (project governance) — data integrity, attribution, source validation

---

## Change Log

| Date | Change | Reason |
|---|---|---|
| 2026-05-05 | Created spec | Standardize tone after multiple rewrites |
| — | — | — |

---

**Status**: LOCKED (guide finalized)  
**Last Review**: 2026-05-05  
**Next Review**: After any significant report rewrite
