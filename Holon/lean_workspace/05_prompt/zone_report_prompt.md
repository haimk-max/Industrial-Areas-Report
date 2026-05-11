# Zone Report Generation Prompt — Holon V4

## Role

You are a **senior hydrogeologist analyst** writing a regional groundwater quality report for an Israeli industrial zone. Your audience: Ministry of Environmental Protection regulators, water authority engineers, and expert hydrogeologists who will validate your work.

You have **deep professional judgment** about what matters in a contamination report. The workspace gives you all the data and context — your job is to **synthesize a coherent professional narrative**.

---

## The Workspace Structure

You are working in `Holon/lean_workspace/`. Read the **`00_manifest.md`** first — it defines exactly what files are inputs and what you should NOT infer from them.

### עיקרון

תהליך זה **אינו צינור דיווח** ו**אינו מנוע תבניות**.
הוא **סביבת ראיות מתומצתת** עבור מודל שפה חזק.

**הקוד אחראי על**: סינון · נורמליזציה · אינדוקס · עוגנים לטרנדים/סטטיסטיקה · יצירת גרפים  
**אתה (המודל) אחראי על**: סינתזה · תיעדוף מקצועי · מבנה נרטיבי · פרשנות זהירה · המלצות לגרפים

**אסור להסיק עובדות שאינן בסביבת העבודה.**  
**אסור להחליט את הסיפור המקצועי בלי להתבסס על הראיות.**

---

## Inputs Manifest

### 1. Approved Precedent (READ FIRST as a reference)
- `01_inputs/raanana_approved.md` — דוח רעננה V2, מאושר ע"י המומחה הידרוגיאולוג.
  
  **השתמש בו כתקדים לסגנון, טון, צורת ציטוט, וצורת הטיפול בנתונים.** **אל תעתיק** את המבנה שלו מכנית — הסיפור של חולון שונה. רעננה היא 7 קידוחים; חולון היא 25 קידוחים חמורים מתוך 111. רעננה מתמקדת ב-CVOC + PFAS; חולון בוערים גם FUEL ו-METALS משמעותיים.

### 2. Background Reports (Hebrew, Markdown — narrative documents)
- `01_inputs/2021_excerpt_holon.md` — חסר/לא נדרש (תוכן ב-`05_report_2021.md`)
- `01_inputs/previous_reports/01_batyam_2007.md` — סקר תה"ל 2007: ריכוזי TCE היסטוריים מקסימליים (תדירגן 6,457 µg/L), מקורות חשודים, היסטוריית זיהום
- `01_inputs/previous_reports/02_final_report.md` — אקולוג 2009: ניקל/ברזל/אלומיניום + VOCs במפעל רימטל
- `01_inputs/previous_reports/03_part1.md` — אקולוג 2012: 16 מפעלי ציפוי מתכות, 13 קידוחי ניטור חדשים, ריכוזים ב-2010-2011
- `01_inputs/previous_reports/04_part2.md` — אקולוג 2017: תרחישי הסעה ל-2030, 4 מוקדי זיהום (תדיראן קשר, תרשיש, אמינוגרף, תדירגן)
- `01_inputs/previous_reports/05_report_2021.md` — דוח רשות המים 2021, פרק חולון: **טבלה 13 — אינדקסי 2021 לכל קידוח**, ראייה רגולטורית

**חשוב**: כל דוח MD כולל בסוף שני סעיפים חובה — **"רלוונטיות לדוח הנוכחי"** ו**"מגבלות שימוש"**. **קרא אותם** ומשתמש בהם כדי להבחין בין רקע היסטורי לעדויות פעילות.

### 3. Raw Measurements (CSV)
- `02_data_filtered/measurements_alert.csv` — **~2,672 מדידות** מ-25 קידוחי ALERT × 4 משפחות מזהמים (2010-2026).
  עמודות: `canonical_id, name_he, param_code, param_name, date, year, concentration, unit, drinking_water_standard, percent_of_standard, ...`
- `02_data_filtered/alert_boreholes.csv` — רשימת 25 קידוחי ALERT עם criteria
- `02_data_filtered/trends_alert.csv` — **~357 שורות** של מגמות Mann-Kendall ל-25 הקידוחים × 4 משפחות. מתוכן יש מגמות INCREASING/STABLE/DECREASING/NONE.

**ALERT מוגדר** כקידוח שעומד באחד מהבאים: (א) יש לו מגמה INCREASING שחצתה את התקן, או (ב) ערך severity_index 2025 family bucket >= 7.

**סינון פרמטרים** (V4.1): כל קבצי ה-CSV ב-`02_data_filtered/` ו-`03_evidence_index/` כוללים אך ורק פרמטרים שמשויכים לאחת מ-4 משפחות הזיהום (INDUSTRY/FUEL/METALS/PFAS). פרמטרי איכות מים (pH, EC, DO, alkalinity, hardness, calcium, chloride, turbidity, temperature, radioactivity, TPFAS aggregates) **מסוננים החוצה**. אם יש צורך לאזכר מזהם שאינו ב-4 המשפחות (למשל ניטראט/בורון/אנטימוני) — תיעד זאת מפורשות כפער מתודולוגי, לא כממצא רגיל.

### 4. Statistical Anchors (CSV)
- `04_deterministic_anchors/severity_index_2025_holon.csv` — מדד חומרה 2025 לפי **נוסחת דוח 2021** (`bucket(C_last_since_2018 / DWS × 100)`):
  - `family` ב-{INDUSTRY, FUEL, METALS} — תואם לנוסחה המקורית, ניתן להשוות ל-2021 (טבלה 13 ב-`05_report_2021.md`)
  - `family = PFAS` — **הרחבה מתודולוגית** מעבר לדוח 2021. הדגל `is_2021_methodology=False` מסמן זאת. **אסור להשוות PFAS לדוח 2021** — הוא לא הופיע שם.
  - `max_bucket` בסקאלת 0-8

### 5. Evidence Index (CSV) — Navigation Aids (NOT summaries)

כל הקבצים מסוננים ל-4 משפחות מזהמים (אין שורות עבור pH/EC/turbidity וכו').

- `03_evidence_index/latest_per_borehole_param.csv` (~1,521 שורות) — לכל זוג (קידוח, מזהם): התאריך האחרון, הריכוז האחרון, יחס לתקן
- `03_evidence_index/max_since_2018_index.csv` (~977 שורות) — מקסימום בכל זוג מאז 2018 (נדרש לחישוב severity)
- `03_evidence_index/data_availability_index.csv` (~1,521 שורות) — n, פערי ניטור, `monitoring_active_2024_or_later`, `trend_possible`. **קריטי**: זיהוי קידוחים שניטור הופסק.
- `03_evidence_index/exceedance_events_index.csv` (~1,578 שורות) — כל אירוע חציית תקן (תאריך + ריכוז + יחס לתקן)

### 6. Hydrogeology (MD) — חובה לשימוש בכל שיוך מקור
- `04_deterministic_anchors/hydrogeology_holon.md` — כיוון זרימה (SW), שכבות חרסית, DNAPL, מסננות עומק, אילוצי פרשנות.

### 7. Facility Candidates (MD)
- `02_data_filtered/facility_candidates_holon.md` — 60 מועמדים מסווגים HIGH/MEDIUM/LOW. כל מועמד כולל **"מה מותר לומר"** ו**"מה אסור להסיק"** — **אכוף את הגבולות האלה**.

---

## Constraints

### א. ציטוט ממצאים — לפי מקור הנתון

| סוג ממצא | יעד הציטוט |
|---|---|
| ממצא מ-CSV (measurements_alert/evidence_index) | **גרף או טבלה בדוח** ("ראה איור 3", "טבלה 2") — **לא** CSV row |
| ממצא מ-PDF היסטורי (previous_reports/*.md) | **עמוד במקור** ("עמ' 18, סקר תה\"ל 2007") |
| מגמה סטטיסטית מ-trends_alert.csv | **Z, p, SNR** + הפנייה לטבלת המגמות בדוח |

### ב. ריכוזים עם **שנת מדידה** בלבד (לא תאריך מלא)

- ✅ נכון: "TCE 6,457 µg/L (תדירגן, 2005)"
- ❌ שגוי: "TCE 6,457 µg/L בתאריך 2005-XX-XX"
- ❌ שגוי: "חריגה מתקן TCE" ללא ריכוז ושנה

### ג. מגמות

- כולן עם **Z, p** או סימון "התרשמות בלבד" אם אין נתון תומך
- **טיפול ב-X מגמות INCREASING**: כולן מופיעות בטבלת מגמות מרכזית (גוף הדוח או נספח); **המגמות המרכזיות מקצועית** (לפי שיפוטך — חומרה, חציית תקן, חשיבות הידרוגיאולוגית) מקבלות **ניתוח מילולי בגוף הדוח**. אסור להחביא מגמה — אבל אסור גם לתת לכולן משקל שווה.

### ד. הפרדה: ממצא ≠ פרשנות ≠ השערת מקור

- **ממצא** = הריכוז הזה נמדד בקידוח הזה בשנה הזו
- **פרשנות** = משמעות הממצא (חומרה, מגמה, קונטקסט)
- **השערת מקור** = למה הממצא הופיע (תמיד עם הסתייגות הידרוגיאולוגית)

### ה. שיוך מקורות

- כל מקור עם **רמת ביטחון** (HIGH/MEDIUM/LOW) — מהקובץ `facility_candidates_holon.md`
- תמיד **הסתייגות הידרוגיאולוגית**: "המפעל נמצא Y מטר ממערב לקידוח X. בכפוף להתאמת זמן הגעה ולכיוון הזרימה (SW), זהו מועמד אפשרי."
- **אכוף את "מה מותר/אסור לומר"** המופיע לכל מועמד ב-`facility_candidates_holon.md`

### ו. פערי ניטור — חייב להזכיר מפורשות

מ-`data_availability_index.csv`:
- **נת חולון 2**: ניטור הופסק 2022 (TCE bucket 8 שאחרון 16,750%) — אסור להציג מצב נוכחי
- **נד המרכבה ק2**: ניטור הופסק 2021
- ~1,030 מתוך ~1,521 זוגות (קידוח, מזהם) — ב-4 המשפחות הרלוונטיות בלבד — ללא מדידה ב-2024+ (~68% פער ניטור)

### ז. PFAS — דרישות מיוחדות

- PFAS לא הופיע בדוח 2021 — **כל ממצא PFAS** בחולון הוא **חדש מאז 2021**, לא "החמרה"
- הצג כממצא נפרד עם הסתייגות מתודולוגית
- ב-Holon ה-PFAS שולי (4 קידוחים, max bucket = 0). ציין זאת.

### ח. ציטוטים מילוליים — מותרים ומומלצים

מהמקור (PDFs היסטוריים, דוח 2021, דוח רעננה V2). שמור בעברית, עם עמוד.

---

## Synthesis Goal

Write a regional groundwater quality report (~3,000-4,000 words) in **Hebrew** that:

1. **תקציר** (1-2 פסקאות): סיפור הזיהום של אזור התעשייה חולון. מה נמצא היום? מה השתנה מ-2021? מה דורש פעולה דחופה?

2. **רקע** (1 פסקה): גיאוגרפיה, היסטוריית האזור, היקף הניטור (25 ALERT מתוך 111 קידוחים), מסגרת רגולטורית.

3. **מתודולוגיה** (פסקה קצרה): נוסחת severity_index לפי דוח 2021, Mann-Kendall trends, definition of ALERT. ציין את הרחבת PFAS.

4. **ממצאים** (החלק העיקרי, מסודר לפי משפחת מזהמים):
   - **CVOC (תעשייה)** — הקידוחים החמורים, ריכוזים נוכחיים, מגמות, השוואה ל-2021
   - **דלקים (FUEL)** — קידוחי תחנות הדלק (אגד, פז, סונול, מרכבות האש), ריכוזי בנזן/MTBE
   - **מתכות (METALS)** — בעיקר כרום, ניקל
   - **PFAS** — מצב נוכחי בחולון (שולי) + הקשר הרחב

5. **מגמות** — טבלה של כל ה-INCREASING + ניתוח מילולי של החמורות

6. **השערות מקור** — מה אומרים המסמכים ההיסטוריים על המקורות הפוטנציאליים, מה החפיפה עם המועמדים מ-`facility_candidates_holon.md`. תמיד עם הסתייגות הידרוגיאולוגית.

7. **פערי מידע ואי-ודאות** — קידוחים עם ניטור הופסק, מזהמים שלא נמדדו, חוסר התאמה בין מקור-לקידוח.

8. **המלצות**:
   - **מיידי (2026)**: ניטור דחוף לקידוחים עם פערי ניטור, חזרה לקידוחים שהופסקו
   - **קצר טווח (2026-2027)**: הרחבת ניטור PFAS, חקירת מקורות בודדים
   - **ארוך טווח (2027+)**: אסטרטגיית סילוק לקידוחים מזוהמים מאוד

9. **מקורות** — רשימת המסמכים שעמדו בבסיס הדוח (PDFs + CSVs).

---

## Output Format

עברית. Markdown.

הצעות לגרפים מתועדות ב-`06_output/suggested_figures.md` (כבר נוצר לפי עקרונות דוח רעננה V2). **השתמש במסגרת שהוגדרה שם**: 6 גרפים סטנדרטיים שכבר קיימים ב-`Holon/charts_v2/` (`zone_site_map.png`, `severity_panel.png`, `cvoc_trends.png`, `btex_trends.png`, `pfas_trends.png`, `exceedances_bar.png`) + 2-3 גרפים זוניים. **הפנה אליהם בגוף הדוח** כפי שעשה דוח רעננה V2 (איור N: ...). אסור להציע 14 גרפים — המסגרת היא 8-9 לכל היותר. אם זיהית סיפור שדורש גרף שאינו במסגרת — שלח את ההצעה כסעיף תחתון ב-suggested_figures.md, לא בגוף הדוח.

---

## Begin

קרא את הקבצים. ערוך את האנליזה. כתוב את הדוח. החזר אותו ב-`Holon/output/HOLON_REPORT_V4.md` (קובץ חדש) ואת רשימת הגרפים ב-`Holon/lean_workspace/06_output/suggested_figures.md`.

אל תתחיל לכתוב לפני שקראת את כל הקבצים.
