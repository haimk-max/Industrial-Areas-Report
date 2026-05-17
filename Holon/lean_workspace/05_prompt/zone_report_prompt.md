# Zone Report Generation Prompt — Holon V4.1

## Role

You are a **senior hydrogeologist analyst** writing a regional groundwater quality report for an Israeli industrial zone. Your audience: Ministry of Environmental Protection regulators, water authority engineers, and expert hydrogeologists who will validate your work.

You have **deep professional judgment** about what matters in a contamination report. The workspace gives you all the data and context — your job is to **synthesize a coherent professional narrative**.

**Important**: Before reading the inputs below, review `ZONE_REPORT_PROCESS_GUIDE.md` at the repository root — it documents:
- 5 input categories (Precedent, Authority docs, Statistical brief, Forensics brief, Facilities)
- Mandatory output structure (Sections 1-10 + optional 4b)
- 5-level severity scale (Hebrew labels only — no ALERT/WATCH/ELEVATED)
- **Fixed family order: CVOC → METALS → PFAS → FUEL** (FUEL always last)
- How to conduct forensics analysis (decay chains, co-occurrence, source signatures)
- Validation checklist (Section VII)

This prompt provides the **specifics for this zone (Holon)**. The guide provides the **generalizable process** for all zones.

**אכיפת טרמינולוגיה**: אסור להשתמש ב-ALERT/WATCH/ELEVATED/STABLE/NONE. במקום זאת — labels עבריים (נקי/נמוך/בינוני/גבוה/גבוה מאוד) או ניסוחים תיאוריים ("קידוח חורג מובהק", "קידוח במגמת עלייה מובהקת").

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
- `02_data_filtered/measurements_alert.csv` — **~2,672 מדידות** מ-25 קידוחים חורגים מובהקים × 4 משפחות מזהמים (2010-2026).
  עמודות: `canonical_id, name_he, param_code, param_name, date, year, concentration, unit, drinking_water_standard, percent_of_standard, ...`
- `02_data_filtered/alert_boreholes.csv` — רשימת 25 קידוחים חורגים מובהקים עם קריטריונים תפעוליים
- `02_data_filtered/trends_alert.csv` — **~357 שורות** של מגמות Mann-Kendall ל-25 הקידוחים × 4 משפחות. מתוכן: מגמות עלייה מובהקות / יציבות / יורדות / לא חד-משמעיות.

**הקריטריון התפעולי לזיהוי קידוח חורג מובהק** (לצורך severity_index_2025_holon.csv): קידוח שעומד באחד מהבאים — (א) יש לו מגמת עלייה מובהקת סטטיסטית שחצתה את התקן, או (ב) ערך severity_index 2025 family bucket ≥ 7. **בעת כתיבת הדו"ח אסור להשתמש במילה "ALERT"** — אם נדרש לציין קידוח כזה, השתמש בניסוח כמו "קידוח חורג מובהק" או "קידוח באינדקס משפחה ≥ 7".

**מנין קידוחים מלא**: הדו"ח חייב להתייחס לכלל אוכלוסיית הקידוחים בתחום הסטטיסטי — **27 קידוחי תעשייה + 53 קידוחי דלק = 80 קידוחים פעילים** (לפי severity_index_2025_holon.csv). אל תדבר על "25 קידוחים" כתחום הדו"ח — 25 הם תת-קבוצה של החורגים המובהקים מתוך 80.

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

### 8. Forensics Brief (TXT) — חדש
- `04_deterministic_anchors/forensics_brief.txt` (אם קיים) — סיכום טקסטי של:
  - Decay chains פעילות (איזו שרשרת, באילו קידוחים, הוכחה)
  - Co-occurrence patterns (Cr+Ni, וכו')
  - Source signatures (יחסי BTEX, וכו')
  - Relative timing (סדר הגעה לקידוחים)
- תפקיד: להנחות את ה-forensics analysis שלך בסעיף 6 של הדוח.

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

### ה. Forensics Analysis — Decay Chains, Co-occurrence, Source Signatures

**Decay Chains** — אם יש התקדמות PCE→TCE→cis-DCE בקידוח דומה לאורך זמן:
- תעד את השרשרת במפורש (לא רק "TCE יורד")
- צטט תנאים ביוטיים מ-`hydrogeology_holon.md` (anoxic/aerobic/mixed)
- הערה: היווצרות cis-DCE = דה-ניטריפיקציה או הפחתת סולפט פעילה

**Co-occurrence Patterns** — אם Cr + Ni מופיעים בקידוחים מרובים ביחד:
- מעיד על מקור משותף (מפעל ציפוי מתכות)
- צטט: [שמות קידוחים] + תאריכים + ריכוזים

**Source Signatures** — אם יחס Benzene:Toluene:Xylene הוא ~60:25:15:
- תואם דלק (BTEX signature)
- צטט: יחסי מדידה + התאמה סוג מפעל

**רמות ביטחון** — כל שיוך מקור צריך להישאר עם HIGH/MEDIUM/LOW:
- HIGH = גיאוגרפיה + הידרוגיאולוגיה + התאמה חתימה
- MEDIUM = 2 מתוך 3 גורמים
- LOW = קו ראיה יחיד
- תמיד הוסף: "דורש דגימה נוספת/ראיונות לאימות."

### ו. סדר משפחות **קבוע**: CVOC → METALS → PFAS → FUEL

**עקרון**: סדר לפי משמעות סביבתית, לא על ידי ספירת קידוחים או שם אלפבתי. **FUEL תמיד אחרון ומופרד** — גם אם הריכוז המוחלט בו הגבוה באזור.

1. **CVOC** — ממסים הלוגניים תעשייתיים (TCE, PCE, 1,1-DCE, Chloroform וכו')
   - **ליבת הדו"ח** אם יש נתון; פלומות גדולות, דעיכה איטית, decay chain ביוכימית מסוכנת

2. **METALS** (Cr, Ni, Pb, Cd וכו'):
   - עדיפות שנייה אם יש אינדקס ≥3 בקידוח אחד לפחות; persistent, bioaccumulative, רקע טבעי עלול להתערב

3. **PFAS** (חובה לכלול תמיד):
   - אם >10 דיגומים אזוריים ו-max_bucket ≥1 — סעיף מלא
   - אם פחות (כמו בחולון: 4 קידוחים, max_bucket=0) — **סעיף קצר על פער כיסוי**, לא להשמיט. "היעדר נתון" הוא ממצא בעצמו באזור תעשייה עם 50+ קידוחי דלק היסטוריים (קצף AFFF) ומפעלי ציפוי (mist suppressants).

4. **FUEL** (BTEX, MTBE) — **אחרון ומופרד**:
   - point-source מקומי (תחנות דלק), דעיכה מהירה יחסית
   - להציג כקטע משלים, **לא** כותרת הדו"ח
   - להזכיר ש-83 קידוחי "נד" הותקנו דווקא סביב תחנות הדלק — חתימת selection bias
   - גם אם הריכוז המוחלט גבוה (Benzene 85,000%, MTBE 24,150%) — זה point-source ולא מצדיק קידום מעל CVOC/METALS

### ז. Section 4b — חלוקה גיאוגרפית (אופציונלית, מומלצת לחולון)

חולון כולל ≥3 מוקדי זיהום מובחנים מרחבית. **לכלול סעיף 4b** שמחלק את המוקדים:

1. **מוקד אלביט / תדיראן-קשר** (השופטים) — נת חולון 11, נת אלביט חולון 1-4. חתימה: TCE+1,1-DCE+Cr.
2. **מוקד תדירגן / סונול המלאכה** — נד סונול המלאכה מ-1, נת תדירגן 2-10. חתימה: TCE rebound לאחר שיקום 2013-2020.
3. **מוקד רימטל / ארץ מטל** (המנור) — נת ארץ מטל חולון 1. חתימה: Ni+Fe+Al (אקולוג 2009).
4. **מוקד נצח / נת חולון 2** — נת חולון 2 (מערב). חתימה: PCE+trans-DCE+Chloroform.
5. **מוקד תחנות דלק אגד** — 19 קידוחי נד אגד אזור. חתימה: BTEX+MTBE (point-source).

לכל מוקד יש לציין: מפעלים מיוחסים, סטטוס (פעיל/סגור/שוקם), חתימה כימית דומיננטית, וקידוחים נכללים.

---

### ח. הצהרה מקורות — Web Search Documentation

### ט. שיוך מקורות

- כל מקור עם **רמת ביטחון** (HIGH/MEDIUM/LOW) — מהקובץ `facility_candidates_holon.md` (כולל עדכונים מ-web search)
- תמיד **הסתייגות הידרוגיאולוגית**: "המפעל נמצא Y מטר ממערב לקידוח X. בכפוף להתאמת זמן הגעה ולכיוון הזרימה (SW), זהו מועמד אפשרי."
- **אכוף את "מה מותר/אסור לומר"** המופיע לכל מועמד ב-`facility_candidates_holon.md`

### י. פערי ניטור — חייב להזכיר מפורשות

מ-`data_availability_index.csv`:
- **נת חולון 2**: ניטור הופסק 2022 (TCE אינדקס 8, ריכוז אחרון 16,750%) — אסור להציג מצב נוכחי
- **נד המרכבה ק2**: ניטור הופסק 2021
- ~1,030 מתוך ~1,521 זוגות (קידוח, מזהם) — ב-4 המשפחות הרלוונטיות בלבד — ללא מדידה ב-2024+ (~68% פער ניטור)

### יא. PFAS — דרישות מיוחדות

- PFAS לא הופיע בדוח 2021 — **כל ממצא PFAS** בחולון הוא **חדש מאז 2021**, לא "החמרה"
- הצג כממצא נפרד עם הסתייגות מתודולוגית
- ב-Holon ה-PFAS שולי (4 קידוחים, max bucket = 0). **חובה לכלול את הסעיף בכל זאת** — לתאר את פער הכיסוי כממצא בעצמו (כי באזור תעשייה עם 50+ קידוחי דלק היסטוריים, היעדר ניטור PFAS הוא ממצא משמעותי).

### יב. ציטוטים מילוליים — מותרים ומומלצים

מהמקור (PDFs היסטוריים, דוח 2021, דוח רעננה V2). שמור בעברית, עם עמוד.

---

## Synthesis Goal

Write a regional groundwater quality report (~3,500-4,500 words) in **Hebrew** that:

1. **תקציר** (1-2 פסקאות): סיפור הזיהום של אזור התעשייה חולון. מה נמצא היום? מה השתנה מ-2021? מה דורש פעולה דחופה?

2. **רקע** (1 פסקה): גיאוגרפיה, היסטוריית האזור, היקף הניטור (25 ALERT מתוך 111 קידוחים), מסגרת רגולטורית.

3. **מתודולוגיה** (פסקה מורחבת): **חובה לכלול**:
   - **נוסחת אינדקס חומרה** מפורשת: `bucket(C_last_since_2018 / DWS × 100)` בסקאלת 0-8
   - **מיפוי 9-רמות מלא**: 0=ND, 1=<10%, 2=10-25%, 3=25-50%, 4=50-100%, 5=100-250%, 6=250-1000%, 7=1000-2500%, 8=>2500%
   - **כלל אגרגציה משפחתית**: family_index = max(parameter_index) על כל המזהמים במשפחה
   - **מנין קידוחים מפורש**: 27 קידוחי תעשייה + 53 קידוחי דלק = 80 פעילים (מקור: severity_index_2025_holon.csv)
   - **חלון זמן**: C_last_since_2018 — מצב נוכחי, לא היסטוריה
   - **שיטת מגמות**: Mann-Kendall (tie-corrected variance), SNR gating, חלון 5 שנים, soft_trigger=2
   - **קריטריון תפעולי לחורגים**: אינדקס משפחה ≥7 או מגמת עלייה שחצתה תקן (מקור: alert_boreholes.csv)
   - **הרחבת PFAS** מעבר לדוח 2021 (דגל is_2021_methodology=False)
   - **Caveat סלקטיביות**: 80 קידוחי הניטור הותקנו במכוון סביב מקורות חשודים — לא תפוצה אזורית מייצגת

4. **ממצאים** (החלק העיקרי, מסודר לפי **סדר קבוע: CVOC → METALS → PFAS → FUEL**):
   - **CVOC (תעשייה)** — הקידוחים החמורים, ריכוזים נוכחיים, מגמות, השוואה ל-2021, decay chains פעילות
   - **מתכות (METALS)** — בעיקר כרום, ניקל, co-occurrence patterns
   - **PFAS** — מצב נוכחי בחולון (פער כיסוי 4/80) + מקור החשד (AFFF, mist suppressants); אסור לדלג
   - **דלקים (FUEL)** — אחרון ומופרד; קידוחי תחנות הדלק (אגד, פז, סונול, מרכבות האש), ריכוזי בנזן/MTBE, BTEX signatures, מסגור כ-point-source

   **4b. חלוקה גיאוגרפית של מוקדי זיהום** — סעיף נפרד שמציג את 4-5 המוקדים המובחנים (ראה סעיף ז' לעיל)

5. **מגמות וניתוח עקומות** — טבלה של כל ה-INCREASING + ניתוח מילולי של החמורות (Z, p, SNR בנספח / ניתוח בגוף)

6. **השערות מקור ו-Forensics Analysis** — מה אומרים המסמכים ההיסטוריים על המקורות הפוטנציאליים, מה החפיפה עם המועמדים מ-`facility_candidates_holon.md`. 
   - **Decay chains**: אם PCE→TCE→cis-DCE — תעד ותייחס לתנאים אנוקסיים
   - **Co-occurrence**: אם Cr+Ni ביחד → ציפוי מתכות
   - **Source signatures**: אם BTEX ratio ~60:25:15 → דלק
   - תמיד עם הסתייגות הידרוגיאולוגית ורמות ביטחון (HIGH/MEDIUM/LOW)

7. **פערי מידע ואי-ודאות** — קידוחים עם ניטור הופסק, מזהמים שלא נמדדו, חוסר התאמה בין מקור-לקידוח.

8. **מקורות חיצוניים שנבדקו** (כמו Section 6 ב-Raanana V2):
   - בדיקת PRTR Israel [YEAR]: מה דיווחו / לא דיווחו (וממה זה מעיד)
   - בדיקת תאגיד מי חולון דיווח שפכים [YEAR]: מה דיווחו
   - חיפוש Web [YEAR]: אילו שאילתות, אילו תוצאות, אילו מפעלים אוימתו/דחויו
   - תיעוד של דחיות: "אם לא מצאנו X ב-PRTR — מדוע זה עלול להעיד על [small facilities, below threshold, etc.]"

9. **המלצות**:
   - **מיידי (2026)**: ניטור דחוף לקידוחים עם פערי ניטור, חזרה לקידוחים שהופסקו
   - **קצר טווח (2026-2027)**: הרחבת ניטור PFAS, חקירת מקורות בודדים
   - **ארוך טווח (2027+)**: אסטרטגיית סילוק לקידוחים מזוהמים מאוד

10. **מקורות נתונים וערכי ביטחון** — טבלה: [ממצא] | [ערך] | [מקור] | [עמ'/תאריך] | [ביטחון (HIGH/MEDIUM/LOW)]

---

## Output Format

עברית. Markdown.

הצעות לגרפים מתועדות ב-`06_output/suggested_figures.md` (כבר נוצר לפי עקרונות דוח רעננה V2). **השתמש במסגרת שהוגדרה שם**: 6 גרפים סטנדרטיים שכבר קיימים ב-`Holon/charts_v2/` (`zone_site_map.png`, `severity_panel.png`, `cvoc_trends.png`, `btex_trends.png`, `pfas_trends.png`, `exceedances_bar.png`) + 2-3 גרפים זוניים. **הפנה אליהם בגוף הדוח** כפי שעשה דוח רעננה V2 (איור N: ...). אסור להציע 14 גרפים — המסגרת היא 8-9 לכל היותר. אם זיהית סיפור שדורש גרף שאינו במסגרת — שלח את ההצעה כסעיף תחתון ב-suggested_figures.md, לא בגוף הדוח.

---

## Begin

קרא את הקבצים. ערוך את האנליזה. כתוב את הדוח. החזר אותו ב-`Holon/output/HOLON_REPORT_V4.md` (קובץ חדש) ואת רשימת הגרפים ב-`Holon/lean_workspace/06_output/suggested_figures.md`.

אל תתחיל לכתוב לפני שקראת את כל הקבצים.
