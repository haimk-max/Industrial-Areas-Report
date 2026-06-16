# מדריך עקרונות — דוחות אזורי תעשייה (Zone Reports Framework)

**מטרה**: עקרונות מפנה (compass points) לכל דוח אזורי תעשייה, מבוסס על Holon V5 hybrid pipeline. לא טוקסונומיה — שניים-שלוש משפטים לכל עקרון.

**Scope**: Holon + מעבר ל-18 אזורים (אם יתקבל אישור מומחה).

---

## I. Zone Context Pack (קלטים לOpus)

### 01_scope — הגדרת היקף אזור
- `zone_wells.csv` — רשימת קידוחים פעילים וסכום (canonical ID, coordinates, depth, type, status)
- `zone_boundary_or_selection_notes.md` — הערות על גבול אזור או קריטריון בחירה קידוחים

### 02_data — Structured Data Pack (חישובים דטרמיניסטיים)
**6 CSVs המוכנות לOpus (לא לחישוב על-ידיו)**:

#### measurements_scoped.csv
- כל מדידה בקידוחים המתאימים לאזור
- עמודות: canonical_well_id, parameter_canonical, result_value, result_date, unit_standardized, dws_value, source_file, source_row_or_page
- מקור: TAHAL 2008, 2021 Report, אקולוג, ניטור עדכני

#### latest_results.csv
- תוצאה אחרונה לכל קידוח × parameter
- עמודות: canonical_well_id, parameter_canonical, latest_value, latest_date, severity_index

#### severity_by_well_family.csv
- אינדקס חומרה לכל קידוח × משפחה (CVOC, METALS, PFAS, FUEL)
- **חשוב**: based on C_max_5y (לא latest result)
- עמודות: canonical_well_id, family, max_value_window, max_value_date, window_start, window_end, severity_index

#### trends_by_well_parameter.csv
- תוצאות Mann-Kendall (Z, p, SNR, soft_trigger) לכל קידוח × parameter
- עמודות: canonical_well_id, parameter_canonical, mann_kendall_z, mann_kendall_p, snr, soft_trigger_met, trend_classification

#### monitoring_gaps.csv
- פערים בניטור: קידוחים שנסגרו, n<5 מדידות, gaps בזמן
- עמודות: canonical_well_id, parameter_canonical, last_measurement_date, is_active, reason_if_inactive, n_measurements_last_5y

#### figure_ready_series.csv
- time series מוכן לגרפים
- עמודות: canonical_well_id, parameter_canonical, date, value, severity_index, include_in_trend_figure

### 03_context — NotebookLM-like Context (קטעים מלאים, לא תקצירים)

#### Reports Context Pack

שלב זה נועד לעבד דוחות עבר באופן scoped לאזור, לפני Zone Diagnosis.

המטרה אינה ליצור facts.md יבש, ואינה להכניס raw dump מלא של הדוחות, אלא לבנות קונטקסט דמוי NotebookLM: קטעים משמעותיים ורלוונטיים מדוחות קודמים, בצירוף הערות פרשניות קצרות.

**תוצרים**:
- `03_context/reports_context.md`
- `03_context/report_sources_index.csv`
- `03_context/context_questions_for_diagnosis.md`

**תפקיד המקורות**:
- דוח 2021 = baseline פרשני רשמי אחרון.
- דוחות 2008 / תה"ל / אקולוג = הקשר היסטורי, מוקדים, מפעלים, הידרוגיאולוגיה ושיקום.
- נתוני ניטור עדכניים = המקור המרכזי לקביעת מצב נוכחי, חומרה ומגמות.

**הערה**: המידע מדוח 2021 לא יופיע כפרק השוואה נפרד בדוח V5, אלא יוטמע בתוך ניתוח המוקדים, המגמות והשינויים.

#### previous_reports_excerpts.md
- קטעים משמעותיים מדוח 2021, דוח TAHAL 2008, דוחות אקולוג, רלוונטיים לאזור
- **לא תקציר** — טקסט מלא מהמקור (עם ציטוט עמוד)
- מטרה: Opus קורא ומסיק, לא מקבל תקציר יבש

#### hydrogeology_context.md
- כיוון זרימה, שכבות אקוויפר, רקע הידרוגיאולוגי של האזור
- מקור: דוחות TAHAL, מודלים אזוריים

#### Source Candidates Pack

מועמדי מקורות זיהום ייבנו כתוצר של התהליך — **לא** input מובטח. לכל אזור חדש, ה-Pack ייבנה מאפס.

**תוצרים**:
- `03_context/source_candidates_context.md` — מועמדים פרשניים עם סיווג ראיה
- `03_context/web_findings_context.md` — סטטוס פעילות נוכחי בלבד
- `03_context/source_candidates_index.csv` — אינדקס מתועד

**מקורות לבנייה**:
- דוחות עבר (extracted PDF text + raw text במידת הצורך לאימות נקודתי)
- חיפוש Web מתועד (PRTR, B144, Google local — ראה §V)
- נתוני ניטור (severity_by_well_family, trends_by_well_parameter, monitoring_gaps)
- חתימות כימיות (forensics — decay chains, co-occurrence, BTEX ratios)

**הערה לחולון/רעננה**: באזורים אלה קיימים artifacts קודמים (`_findings_*.json`, `extracted_findings.json`, `facility_attribution.json`, `web_findings.md`). שימוש בהם מותר בכפוף לכללים בסעיף §X (Evidence Classification) — אבל **אין להכליל הנחה זו לאזורים חדשים**.

**אזורים חדשים**: אין להניח שקיים `facility_attribution.json` או JSON אחר של מועמדים. ה-Pack ייבנה מאפס מהמקורות לעיל.

#### Evidence Classification System (A–E)

**כלל גנרי לכל האזורים** — מוטמע ב-`source_candidates_index.csv` תחת עמודה `evidence_class`:

| Class | משמעות | בסיס ראיה |
|-------|---------|-----------|
| **A** | `raw_report_verified` | ציטוט ישיר מטקסט גולמי של דוח (raw text excerpt) |
| **B** | `ai_extracted_with_page_ref` | AI-derived מ-`_findings_*.json` או extracted PDF text, עם page_ref מפורש; לא אומת ב-raw text |
| **C** | `web_verified_current_activity` | סטטוס פעילות עדכני מ-web. **אינו מוכיח קישור לזיהום** |
| **D** | `inferred_candidate` | קרבה גיאוגרפית / שם קידוח / הקשר; ללא ראיית מסמך ישירה |
| **E** | `weak / mention_only` | אזכור בודד במסמך אחד; ללא קישור לקידוח/מזהם |

**מדיניות שימוש ב-Zone Diagnosis ובדוח V5**:
- **A + B**  — מועמדים חזקים; ייכנסו לגוף ה-Zone Diagnosis ולסעיף 5 בדוח V5
- **C**  — משלים מצב נוכחי; אסור להציג כראיית זיהום בעצמו
- **D / E**  — רקע או נספח. ייכנסו לסעיף 5 רק אם נתוני הניטור (severity, trends, חתימות כימיות) מחזקים אותם עצמאית

#### approved_precedent_excerpt.md
- קטע מדוח רעננה V2 (סגנון, טון, מבנה) או חולון V4–V8 validated
- **לא תוכני** — רק דוגמה לאיך לכתוב

#### 01_scope / 02_data / 03_context
ראה המבנה הכולל בתחילת §I.

### (Legacy) קלט 1: Precedent Report (Approved)
- **מה**: דוח אזור אחר שהאושר על ידי hydrogeologist
- **למה**: Style reference (tone, section structure, citation format)
- **דוגמה**: Raanana V2 עבור Holon
- **שימוש חדש**: `03_context/approved_precedent_excerpt.md`

### (Legacy) קלט 2: Authority Documents (Direct Excerpts)
- **מה**: עמודים ממשפחה מפורסמת (תה"ל 2007, הנדסה 2009-2017, רשות המים 2021) — לא paraphrases
- **למה**: Historical context, contamination types, facility names
- **דוגמה**: דוח רשות 2021 עמ' 35-49 (גיאוגרפיה, severity)
- **שימוש חדש**: `03_context/previous_reports_excerpts.md`

#### מבנה PDFs לאזור חדש (סקיילינג ל-16 אזורים נוספים)

**מיקום סטנדרטי**: `External Data/{zone}/`
```
External Data/{zone}/
├── raw_pdfs/                         # PDFs מקור (לא שינויים)
│   ├── tahal_2007_{zone}.pdf         # סקר אתרי קרקע מזוהמת (אם רלוונטי)
│   ├── ecolog_2009-2017_{zone}.pdf   # מודל הסעה / מפעלי ציפוי (אם רלוונטי)
│   ├── water_authority_2021_{zone}.pdf  # חובה אם האזור נמנה ב-18
│   └── facility_reports/             # מסמכי מפעלים (אופציונלי)
│       └── {facility_id}.pdf
└── extracted/                        # תוצרי חילוץ ידני / אוטומטי
    ├── boreholes_table.csv           # מטבלת קידוחים שב-PDF
    ├── concentrations_table.csv      # ריכוזים היסטוריים
    └── extraction_notes.md           # עמודי מקור, הערות, חוסרים
```

**חילוץ ידני (כיום)**: קריאת PDF + העתקה ידנית של טבלאות לקבצי CSV. תיעוד בעמוד מקור (לדוג' "TAHAL 2008 Part B עמ' 53-67").

**חילוץ אוטומטי (Phase 2)**: Skill `pdf-ingest` יעשה את החילוץ עם Claude PDF Beta / pdfplumber. עד אז — ידני.

**חשוב — אישור היסטורי**: כל extraction חייב להישמר עם source citation (`source_document: TAHAL_2008_Part_B`, `source_page: 53-67`) לטובת validation.

### 04_diagnosis — Zone Diagnosis (קלט לפני כתיבת V5 Report)
**קובץ אחד בלבד**: `zone_diagnosis.md`

Opus קורא את כל Context Pack (01–03) ומייצר אבחנה מקצועית קצרה (1-2 עמודים):

```
1. מהם מוקדי הזיהום המרכזיים בנתונים?
2. אילו קידוחים מובילים כל מוקד?
3. אילו מזהמים מגדירים כל מוקד?
4. מה השתנה ביחס לדוח 2021?
5. אילו מגמות חשובות באמת? (MK p<0.05, SNR>5, soft_trigger=true?)
6. אילו פערי ניטור קריטיים?
7. אילו מקורות אפשריים ראויים לדיון?
8. מה צריך להיכנס לגוף הדוח (§3) ומה לנספח?
```

### 05_prompt — Prompt ל-Opus
**קובץ אחד בלבד**: `zone_report_prompt.md`

Prompt filled instance שמנחה את Opus לכתוב V5 Report (ראה §II.5 לפרטים על Zone Diagnosis, ראה REPORT_V5_SCHEMA.md לסכמה הגנרית).

---

### (Legacy) קלט 3: Statistical Brief (Structured Text)
- **מה**: סיכום קריא של trends + severity distribution — **לא raw CSV**
- **למה**: Opus יכול להתמקד בממצאים, לא ב-parsing
- **דוגמה**: "קידוחים חורגים מובהקים (25/80): CVOC max 8,750% (בורה X, 2024); מגמות עלייה מובהקות (19): TCE +5%, Cr +12%, Benzene יציב"
- **דרישה — מנין קידוחים**: ה-brief חייב לציין מפורש את **סך כל הקידוחים בתחום** (לפי תוצאת severity_index — למשל "27 קידוחי תעשייה + 53 קידוחי דלק = 80 פעילים"). הדו"ח חייב להתייחס לכלל הקידוחים הללו ולא לתת-קבוצה.
- **שימוש חדש**: Opus יחשב זאת בעצמו מתוך Structured Data Pack + Zone Diagnosis (לא קלט מראש)

### (Legacy) קלט 4: Forensics Brief (Optional, As-Needed)
- **מה**: Decay chains, co-occurrence patterns, source signatures — ברמת overview בלבד
- **למה**: Only if meaningful patterns exist (not per-finding, not mandatory)
- **דוגמה**: "<bdi>PCE→TCE</bdi>→cis-DCE chain active (3 wells, p<0.01); Cr+Ni co-occurrence suggests plating facility (5 wells)"
- **שימוש חדש**: Opus יחשב זאת מתוך Context Pack + Diagnosis

### (Legacy) קלט 5: Facility Candidates (Updated from Web Search)
- **מה**: `facility_candidates_[ZONE].md` — גם HIGH מ-PDFs אומתו עדכנים; + תוצאות web search (PRTR, דיווח שפכים)
- **למה**: Sourcing guidance עם confidence levels (HIGH/MEDIUM/LOW)
- **דוגמה**: "אלגונל (HIGH, confirmed address, ציפוי מתכת) | PFHxS מגורם דיגום Holon Q3 2025 עתידי"
- **שימוש חדש**: `03_context/source_candidates_context.md`

#### מקורות Web סטנדרטיים לחיפוש (Facility Discovery)

**6 ערוצי חיפוש לפעולה לכל אזור חדש**:

| # | מקור | URL / שאילתה | מה לחפש |
|---|------|--------------|----------|
| 1 | **PRTR Israel** | ecology.sviva.gov.il | מפעלים מחויבי דיווח (>1,000 ק"ג/שנה) באזור הנסקר |
| 2 | **B144** | b144.co.il | רישום עסקים לפי רחוב/קואורדינטות |
| 3 | **WebSearch כללי** | "מפעל ציפוי {אזור}", "תקרית זיהום {רחוב}" | חדשות, תקריות, מפעלים היסטוריים |
| 4 | **גוגל מפות** | maps.google.com (manual) | מפעלים תעשייתיים בקואורדינטות + סוג עסק |
| 5 | **פורומים מקומיים** | פייסבוק קבוצות, אתרי שכונה | תלונות תושבים על ריחות / פליטות |
| 6 | **דוחות גורמים** | רשות המים, אקולוג, תה"ל | מפעלים שזוהו במחקרים קודמים |

**שאילתות סטנדרטיות לכל אזור**:
```
"מפעל ציפוי {שם_אזור}"
"תקרית זיהום {שם_רחוב}"
"{שם_אזור} זיהום מי תהום"
"{שם_אזור} industrial waste"
"PRTR {שם_אזור}"
"chrome plating {city_name} Israel"
```

**Output structure** (`facility_candidates_{zone}.md`):
```markdown
| מפעל | קואורדינטות ITM | מזהמים חשודים | רמת ביטחון | מקור (URL/PDF) | פעיל? |
|------|------------------|----------------|------------|----------------|--------|
```

**רמות ביטחון**:
- **HIGH**: address confirmed + מזהם מתאים מקידוח קרוב (<500m) + שנות פעילות חופפות לעדות בקידוח
- **MEDIUM**: 2 מתוך 3 הקריטריונים
- **LOW**: 1 קריטריון, או רק רישום ללא ראיות שטח

**אוטומציה — Phase 2**: skill `facility-discovery` יבצע את 6 הערוצים אוטומטית עם confidence scoring מבוסס Emipy pattern (distance × pollutant_match × operating_year_overlap).

---

## II. V5 Report Schema (Mandatory Framework)

### §II.5: Zone Diagnosis (Pre-V5 Report Step)

**מטרה**: אבחנה מקצועית של Opus על Context Pack, לפני כתיבת הדוח הסופי.

**קלטים**: 01_scope/ + 02_data/ + 03_context/ (מלא, לא תקציר).

**פלטים**: `04_diagnosis/zone_diagnosis.md` (1-2 עמודים בעברית).

**פלט חובה — בלוק "## סדר מוקדים"** (focus_order):
בסוף ה-zone_diagnosis.md, Opus **חייב** לכלול בלוק בפורמט הקבוע הבא (פַּרסְבִיל ל-Gate 4):

```
## סדר מוקדים

| # | שם המוקד | מיקום / רחוב | משפחה מובילה | max_bucket | משפחות נוספות | קישור מנגנוני |
|---|----------|--------------|--------------|------------|----------------|----------------|
| 1 | [שם]     | [מיקום]      | [CVOC/METALS/FUEL/PFAS] | [0-8] | [רשימה] | [תיאור / —] |
| 2 | ...      | ...          | ...          | ...        | ...            | ...            |
| N | פערי כיסוי | — | PFAS (ואחרים) | — | — | — |
```

הבלוק ממוין לפי **max_bucket יורד**. שורת "פערי כיסוי" תמיד אחרונה.
Gate 4 מאמת: בלוק קיים + ממוין + מספר מוקדים סביר (≥1).

**שאלות ש-Opus עונה**:
1. מהם מוקדי הזיהום המרכזיים בנתונים? (גיאוגרפיה + מזהמים)
2. אילו קידוחים מובילים כל מוקד?
3. אילו מזהמים מגדירים כל מוקד?
4. מה השתנה ביחס לדוח 2021?
5. אילו מגמות חשובות באמת? (MK p<0.05, SNR>5, soft_trigger=true?)
6. אילו פערי ניטור קריטיים?
7. אילו מקורות אפשריים ראויים לדיון?
8. מה צריך להיכנס לגוף הדוח (§3) ומה לנספח?

**הערה**: זו לא תקציר הנתונים — זו **אבחנה מקצועית** המכוונת את הכתיבה הסופית.

---

### V5 Report — 6 פרקים גנריים

```
1. תקציר מקצועי
2. תמונת מצב אזורית ומערך הניטור
3. מוקדי זיהום עיקריים
4. מגמות, החמרה ופערי ניטור
5. מקורות זיהום אפשריים ורמות ביטחון
6. המלצות
נספחים
```

#### פרק 1: תקציר מקצועי
- ממצאים עיקריים: מוקדים, מזהמים, ריכוזים (% of standard), תאריכים
- שנויים מ-דוח 2021 (אם רלוונטי)
- פערי מידע קריטיים
- תגובה מיידית נדרשת?

#### פרק 2: תמונת מצב אזורית ומערך הניטור
- גיאוגרפיה, הידרוגיאולוגיה, כיוון זרימה
- מערך קידוחים: מספר, סוגים, מיקום, סטטוס (פעיל/סגור)
- מפת קידוחים + מוקדים (איור 1)

#### פרק 3: מוקדי זיהום עיקריים

**סדר**: לפי מוקד גיאוגרפי — ראה §IV.

**תבנית לכל מוקד זיהום** (נשמרת זהה בכל אזור):
```
- שם המוקד (רחוב / מפעל / אזור)
- קידוחים מרכזיים (מנהל + מיקום)
- מזהמים מובילים (שמות כימיים + ריכוזים)
- ריכוזים ותאריכים (טבלה קצרה)
- מגמות (MK Z, p, SNR; soft_trigger?)
- קשר לדוחות קודמים (מה השתנה מ-2021?)
- מקורות אפשריים (שם מפעל + סוג עסק)
- רמת ביטחון (HIGH/MEDIUM/LOW)
- פערי מידע (מה חסר?)
- פעולה נדרשת (בדיקה? סגירה? ניטור משופר?)
```

**חשוב**: PFAS ללא נתונים מאמתים  — נכנס לסעיף "פערי כיסוי" אחרון (ראה §IV).

#### פרק 4: מגמות, החמרה ופערי ניטור
- מגמות בולטות (MK results, only p<0.05 + SNR>5 + soft_trigger)
- קידוחים שהופסק ניטורם (closed wells)
- פערי ניטור אזוריים (אזורים ללא קידוחים, parameters שלא נשקלו)
- Selection bias caveat: קידוחים הותקנו במכוון בסמיכות למקורות חשודים, לא נציגים של תפוצה אזורית

#### פרק 5: מקורות זיהום אפשריים ורמות ביטחון
- טבלה קצרה: [מוקד] | [מזהם עיקרי] | [מפעל משוער] | [סוג עסק] | [רמת ביטחון: HIGH/MEDIUM/LOW]
- **רמות ביטחון**: HIGH = address confirmed + מזהם מתאים + שנות פעילות חופפות; MEDIUM = 2/3; LOW = 1/3

#### פרק 6: המלצות
- **Immediate** (30-90 ימים): דיגום אישור, בדיקות quick-look
- **Short-term** (2026-2027): בדיקות עומק, דיגום פרובים, ניטור משופר
- **Long-term** (2027+): עדכון מודל אזורי, תיקון מקורות, ניטור רציף

#### מתודולוגיה (סעיף קצר)
- formula אינדקס: `bucket(C_max_5y / DWS × 100)`
- Mann-Kendall: tie-corrected, SNR=5 gate, soft_trigger=2, חלון 5 שנים
- מנין קידוחים מפורש בדוח
- selection bias caveat
- הפניה ל-PROCESS_GUIDE §III לפרטים מלאים

#### מגבלות (סעיף נפרד)
- פערי ניטור (closed wells, n<5, gaps בזמן)
- selection bias מפורש
- הנחות על מקורות (confidence levels)

#### נספחים
- **נספח א**: טבלאות מלאות (כל קידוחים, מגמות, ALERT, אינדקסים)
- **נספח ב**: פורנזיקה כימית (decay chains, co-occurrence, source signatures)
- **נספח ג**: מועמדי מקורות מלאים (PRTR, web search, facility history)
- **נספח ד**: Context Pack excerpts (source citations)

---

## III. Severity Scale (Unified, No Variants)

**נוסחת חישוב קנונית**: `bucket = severity_index(C_max_5y / DWS × 100)`
- `C_max_5y` = ריכוז מקסימלי בחלון 5 שנים אחרונות (מ-2021 ואילך לדו"חות 2026)
- `DWS` = drinking water standard (תקן מי שתייה ישראלי)

**טבלת אינדקס קנונית (9-רמות, 0–8)** — לפי הקוד ב-`severity_index_2025_*.csv`:

| אינדקס | % מהתקן | תווית (5-רמות) |
|--------|---------|------------------|
| 0 | ND (לא זוהה) | נקי |
| 1 | <10% | נקי |
| 2 | 10–25% | נמוך |
| 3 | 25–50% | נמוך |
| 4 | 50–100% | בינוני |
| 5 | 100–250% | בינוני |
| 6 | 250–1,000% | גבוה |
| 7 | 1,000–2,500% | גבוה |
| 8 | >2,500% | גבוה מאוד |

**הצגה בדו"ח**: השתמש ב-5 תוויות בלבד (נקי / נמוך / בינוני / גבוה / גבוה מאוד).
**שמירה ב-CSV**: 9-רמות מספריות (0–8).

**Terminology enforcement (אכיפה)**: יש להשתמש ב-labels עבריים בלבד. אסור: 'bucket', 'ALERT/WATCH/ELEVATED/STABLE/NONE', 'עקבה'. במקום ALERT — "קידוח חורג מובהק" או "אינדקס גבוה (≥7)" או "קידוח במגמת עלייה מובהקת" (לפי הקשר). אם דרושה הגדרה אופרטיבית, יש לתעד את המקור (CSV/מסמך) שמייצר אותה.

---

## IV. Focus Ordering — מוקד גיאוגרפי ראשי, משפחות משניות (Zone-Adaptive)

> **SSOT**: כלל הסדר מוגדר **פעם אחת** כאן. כל סעיף אחר בפייפליין שמזכיר סדר — מפנה ל-§IV זה.

### כלל ראשי — סדר מוקדים גיאוגרפיים

**§3 בדוח = רצף מוקדים גיאוגרפיים**, ממוין לפי **חומרת-המוקד יורדת** (max_bucket של הקידוח הכי חמור במוקד).

סדר-המוקדים הוא **ארטיפקט-שיפוט** שמיוצר ב-Step 4 (Zone Diagnosis) — הוא אינו דטרמיניסטי מ-CSV בלבד, כי אשכול גיאוגרפי ומיון מוקדים דורשים שיפוט מקצועי (Opus). הארטיפקט מוצהר כבלוק "## סדר מוקדים" ב-zone_diagnosis.md ונאכף ב-Gate 5 (ראה §VIII).

מספר המוקדים הוא **data-driven** — לא מספר קבוע. אזור עם מקור בודד יכול לקבל מוקד אחד; אזור מורכב — שמונה מוקדים. מה שחייב להיות עקבי: מספר `### 3.N` בפרק 3 **חייב להיות שווה** למספר המוקדים שמוצהר בפרק 1.

### כלל משני — סדר משפחות בתוך מוקד

בתוך כל מוקד, המשפחות מסודרות לפי max_bucket יורד **בנתוני אותו מוקד בלבד**:

```python
def families_within_focus(focus_max_buckets: Dict[str, int]) -> List[str]:
    """סדר משפחות בתוך מוקד אחד — חומרה יורדת. PFAS נכלל אם יש לו נתונים במוקד."""
    return sorted(
        [f for f in focus_max_buckets if focus_max_buckets[f] > 0],
        key=lambda f: focus_max_buckets[f],
        reverse=True
    )
```

**דוגמא — מוקד A (CVOC דומיננטי)**:
- max_bucket במוקד: CVOC=8, FUEL=6, METALS=3
- סדר תצוגה בתוך המוקד: **<bdi>CVOC → FUEL</bdi> → METALS**

**דוגמא — מוקד B (METALS דומיננטי)**:
- max_bucket במוקד: METALS=8, CVOC=2
- סדר תצוגה: **<bdi>METALS → CVOC</bdi>**

### חריג — כלל קישור מנגנוני (תוך-מוקד בלבד)

כאשר קיים קשר פיזיקו-כימי בין שתי משפחות **באותו מוקד** — המשפחה הקשורה מוצגת מיד אחרי המשפחה הדומיננטית, לפני משפחה חמורה-יותר שאינה קשורה. יש לנמק את הקישור במפורש בטקסט.

**שלוש הדוגמאות הקנוניות**:
1. **VC כתוצר-פירוק TCE** (<bdi>CVOC→CVOC</bdi>): VC מוצג מיד אחרי TCE/PCE, גם אם BTEX חמור יותר.
2. **1,4-dioxane כמייצב TCA** (<bdi>CVOC→CVOC</bdi>): dioxane מוצג מיד אחרי TCA.
3. **LNAPL כתורם-אלקטרונים לפירוק רדוקטיבי של CVOC** (<bdi>FUEL→CVOC</bdi>): אם LNAPL מניע פירוק CVOC, FUEL מוצג מיד אחרי CVOC כהקשר מסביר.

**הגבלה**: הקישור תקף **תוך-מוקד בלבד**. קשר חוצה-מוקדים (לדוג' LNAPL בצפון שעשוי להשפיע על CVOC בדרום) מטופל כ"חציית סיגנל" עם השערות מתחרות — לא כקישור מנגנוני.

### סעיף "פערי כיסוי" — סיום גנרי

כאשר משפחה (בעיקר PFAS) **אין לה מוקד גיאוגרפי עם נתונים מאמתים** — היא נכנסת לסעיף **"פערי כיסוי"** אחרון (לא סעיף PFAS-ייעודי). הסעיף גנרי ויכול לכלול גם:
- פערים מרחביים (אזורים ללא קידוחים)
- פערים פרמטריים (פרמטרים שלא נדגמו)
- PFAS הוא המופע המרכזי, בשל חשש עולה גלובלית (קצף כיבוי AFFF, mist suppressants) — "היעדר נתון" הוא ממצא בעצמו

**PFAS עם נתונים** (>10 דגימות אזוריות ו-max_bucket ≥1): סעיף מלא כמוקד רגיל, ממוין לפי חומרה.

### הערת FUEL — selection bias

FUEL אינו "תמיד אחרון" עוד — מוקד דלק חמור יכול להוביל (3.1) אם max_bucket שלו הוא הגבוה ביותר. אולם, **חובה למסגר** קידוחי-דלק כ"קידוחי דלק ייעודיים" כדי לסמן selection bias: קידוחים אלה הותקנו ב-point-source ידוע ואינם נציגים של תפוצה אזורית.

### תיאור משפחות

1. **CVOC** — ממסים מוכלרים תעשייתיים (TCE, PCE, 1,4-Dioxane, Chloroform, etc.)
   - מתמידים שנים–עשורים, דעיכה איטית, סיכון ביו-מצטבר גבוה

2. **METALS** — מתכות כבדות (Cr, Ni, Pb, Cd, As, etc.)
   - מתמידות, ביו-מצטברות, רגישות-רדוקס

3. **PFAS** — חומרים פר/פולי-פלואורואלקיליים
   - מחלקת תרכובות חדשה (פוסט-2021), חשש עולה גלובלית
   - ראה כלל "פערי כיסוי" לעיל

4. **FUEL** — BTEX, MTBE, Benzene
   - מקומי (point-source), דעיכה מהירה יחסית, צפוי סביב תחנות דלק
   - ראה הערת selection bias לעיל

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
- Document: "חיפוש Web [YEAR]: [X queries]  — [results summary]"
- Verify facility status (active/inactive/relocated)

### Output
- Update `facility_candidates_[ZONE].md` with web search results
- Mark HIGH candidates as "אומתו פעילות" or "הופסקו [year]"
- Add any new MEDIUM candidates discovered

---

## VI. Figures (Diagnostic + Final)

### §VI.0: Pre-Opus Diagnostic Figures (Optional, for Zone Diagnosis guidance)

**Process**: `emit_diagnostic_figures.py` (לפני Opus call).

**Figures**:
1. `severity_overview_[ZONE].png` — הפצה של severity indices אזור-רחב (box plot per family)
2. `trend_candidates_[ZONE].png` — קידוחים עם MK Z significant (p<0.05, SNR>5)
3. `monitoring_gaps_timeline_[ZONE].png` — ציר זמן של ניטור: פעיל/סגור/gaps
4. `top_exceedances_[ZONE].png` — 10-15 ממצאים עליונים (ריכוז % of DWS)

**מטרה**: עזרה לOpus בעת כתיבת Zone Diagnosis (ראה §II.5). אינו חובה בDiagnosis עצמו.

### §VI.1: Final Figures (Post-Opus, per Boreholes Selection)

**Process**: `emit_figures.py` (<bdi>SVG → PNG</bdi> via cairosvg) after Opus call + boreholes_override.

**Figures** (from `scripts/report_designed/svg_charts.py`):
1. `fig_01_severity_ledger.png` — Top contaminants per family
2. `fig_02_severity_matrix.png` — Distribution across 5-level scale
3. `fig_03_cvoc_panels.png` — CVOC time series (if data exists; only boreholes_override)
4. `fig_04_metals_panels.png` — METALS time series (if data exists; rename per zone)
5. `fig_05_fuel_panels.png` — FUEL/BTEX time series (if data exists; rename per zone)
6. `fig_06_monitoring_gaps.png` — Sampling timeline + interruptions

**Role**: Input to Opus (for citation in report) + HTML embedding.
**חשוב**: Opus בוחר אילו קידוחים להציג; סקריפט בוחר איך.

**RTL Requirements** (for zones in Hebrew-speaking regions):
- כל `<text>` ב-SVG עם תוכן עברי חייב לכלול `direction="rtl"` ו-`text-anchor="end"`
- כותרות ראשיות (chart title): position מימין, יישור לימין
- תוויות צירים (axis labels): RTL, יישור לימין
- אגדה (legend): RTL ordering, יישור לימין
- מספרים + יחידות שמופיעים בתוך טקסט עברי (לדוגמה "27,860 µg/L") — יש לעטוף ב-`<tspan direction="ltr" unicode-bidi="isolate">`

---

## VII. Validation Checklist (Post-Opus, Pre-HTML)

### Structural Checks
- [ ] No narrative arc ("crisis in 20XX")
- [ ] All numbers tied to source (CSV row, page number, Z/p/SNR, source file)
- [ ] **Focus order: §3 לפי מוקד גיאוגרפי (חומרה יורדת); משפחות-בתוך לפי §IV; PFAS בסעיף "פערי כיסוי" אחרון** (ראה §IV)
- [ ] PFAS section present (סעיף מלא אם max_bucket≥1 ו->10 דגימות; "פערי כיסוי" אחרון אחרת)
- [ ] Severity scale = 5-level only (נקי/נמוך/בינוני/גבוה/גבוה מאוד)
- [ ] **אין טרמינולוגיה אנגלית** (ALERT/WATCH/ELEVATED/STABLE/NONE) — רק labels עבריים או ניסוחים תיאוריים מתועדים

### Data Integrity Checks
- [ ] **Zone Context Pack assembled**: 01_scope/, 02_data/ (6 CSVs), 03_context/ (4-5 files), 04_diagnosis/, 05_prompt/ קיימים
- [ ] **Structured Data Pack valid**: 6 CSVs (measurements_scoped, latest_results, severity_by_well_family, trends_by_well_parameter, monitoring_gaps, figure_ready_series) parseable + columns match DATA_PIPELINE_SPEC.md
- [ ] **Zone Diagnosis present**: 04_diagnosis/zone_diagnosis.md exists + answers 8 questions
- [ ] **C_max_5y ≠ latest result** — window_start/window_end/max_value_date differentiated in severity_by_well_family.csv

### Methodology Checks
- [ ] **Methodology כוללת**: נוסחת אינדקס מפורשת, מיפוי 9-רמות, כלל אגרגציה, מנין קידוחים מפורש, חלון זמן
- [ ] **מנין קידוחים עקבי** בין כל הסעיפים (לדוג' 27+53=80 ולא 87 בסעיף 1 ו-80 בסעיף 3)
- [ ] **PFAS logic block**: גם כש-max_bucket=0, יש סעיף על coverage gap + סיבה לחשד (AFFF, mist suppressants, etc.)
- [ ] **Monitoring gaps explicit** (פרק 4): closed wells מרויים, n<5 מדידות מרויות, time gaps מזוהים
- [ ] Source confidence: HIGH/MEDIUM/LOW on all facility attributions
- [ ] Selection bias caveat present (monitoring wells ≠ zone-wide distribution)

### Content & Presentation Checks
- [ ] **תמציתיות נרטיב**: סעיף 3 (משפחות) **לא מונה כל קידוח חורג** — מסכם התפלגות + מציין בולטים בלבד (top 3–5 לכל משפחה)
- [ ] **מתודולוגיה סעיף תמציתית**: 5–10 שורות בלבד; הפניה ל-PROCESS_GUIDE §III לפרטים מלאים
- [ ] **כל איור עם image markdown לפניו**: לכל `**איור N**:` בטקסט, יש שורת `![](.../fig_0N_*.png)` לפניו (HTML generator יכלול safety net, אבל לתעד מקור הוא תפקיד המודל)
- [ ] Figures 1-6 referenced (or subsets if family omitted)
- [ ] Recommendations: timeframe structure (Immediate/Ongoing/Investigation)

### Technical Checks
- [ ] **HTML post-processing**: numbers+units+pollutant names wrapped in `<bdi>`; CSS `unicode-bidi: isolate` applied to text containers
- [ ] **SVG figures**: titles/labels RTL when zone is Hebrew-speaking

---

## VIII. Scaling Pattern — 7-Step Hybrid Pipeline + Step 8 (Exec Summaries, post-approval) — For Zone N+1, N+2, …

> **אכיפת QA**: לכל שלב שמייצר פלט — יש שער QA אוטומטי. הפקודה הרלוונטית מצוינת לכל שלב.
> כלי: `python scripts/qa_pipeline.py --gate <N> --zone <ZONE>`
> פלט: PASS / WARN (ממשיכים) / FAIL (חסימה — אסור להמשיך לשלב הבא).

1. **Define zone scope** → 01_scope/ (zone_wells.csv, zone_boundary_or_selection_notes.md)

2. **Run deterministic data pipeline** → 02_data/ (6 CSVs: measurements_scoped, latest_results, severity_by_well_family, trends_by_well_parameter, monitoring_gaps, figure_ready_series)
   ```bash
   python scripts/qa_pipeline.py --gate 2 --zone {ZONE}
   ```
   **חסימה על FAIL**: עמודות חסרות, CSVs חסרים, מנין קידוחים לא עקבי ב-CSVs ראשיים, TPFAS/BETK בניתוח.

3. **Assemble scoped NotebookLM-like context** → 03_context/ (previous_reports_excerpts, hydrogeology_context, source_candidates_context, web_findings_context, approved_precedent_excerpt)

4. **Generate zone diagnosis** → Opus call #1 (קלט: 01–03) → 04_diagnosis/zone_diagnosis.md (עונה על 8 שאלות)
   ```bash
   python scripts/qa_pipeline.py --gate 4 --zone {ZONE}
   ```
   **חסימה על FAIL**: zone_diagnosis.md חסר, נושאים קריטיים לא מכוסים.
   **אזהרה על WARN**: מבנה גיאוגרפי חלש, PFAS לא מוסגר כפער, תאריכי סגירה חסרים.
   **כלל גישור שלב 4→5 (חוזה בין-שלבי)**: בלוק "## סדר מוקדים" מ-zone_diagnosis.md (ראה §II.5) **חייב** לעצב את כותרות פרק 3 בדוח — כל `### 3.N` = שם מוקד גיאוגרפי מהבלוק, בסדרו. PFAS שמוסגר כ"פערי כיסוי" באבחון **חייב** להישמר כ"פערי כיסוי" בדוח — לא לעלות לרמת מוקד שווה.

5. **Generate V5 expert report** → Opus call #2 (קלט: 01–04 + zone_report_prompt.md) → output/{ZONE}_REPORT_V5.md (לפי §II V5 schema)
   ```bash
   python scripts/qa_pipeline.py --gate 5 --zone {ZONE}
   ```
   **חסימה על FAIL**: טרמינולוגיית pipeline בגוף הדוח, סעיפים חסרים, חוסר עקביות במנין קידוחים, כותרות פרק 3 אינן מוקדים גיאוגרפיים, PFAS חסר לחלוטין, רמות ביטחון חסרות בפרק 5.
   **אזהרה על WARN**: קביעות נחרצות יתר (דורשות ריכוך), PFAS ללא ניסוח "פער כיסוי", מתודולוגיה ארוכה מ-15 שורות.

   **איסור טרמינולוגיית pipeline בגוף הדוח** (חדש — §VIII.5):
   - אסור: שמות קבצים (`severity_by_well_family.csv`), שלבים (`Step 5`, `Opus Call #2`), שמות pipeline (`V5 Hybrid Pipeline`, `PROCESS_GUIDE`), קודי סיווג (`A+B`, `C-class`, `D-class`), מונחים סטטיסטיים פנימיים (`soft_trigger`, `SNR gating`, `bucket`)
   - מותר: מונחים מקצועיים סטנדרטיים בתחום (TCE, Mann-Kendall, CVOC, PFAS, ISCO, DNAPL)
   - הכלל: אם הקורא הוא הידרוגיאולוג מרשות המים — האם יבין את המונח ללא הכשרה בפייפליין הפנימי? לא → החלף.

6. **Generate final figures + HTML** → `emit_figures.py` (boreholes_override path) → `generate_{zone}_full_html.py` + `generate_{zone}_designed.py`
   ```bash
   python scripts/qa_pipeline.py --gate 6 --zone {ZONE}
   ```
   **חסימה על FAIL**: SVG מפה עם פחות מ-50 עיגולים, RTL חסר ב-HTML, Word ללא איורים מוטבעים, RTL פסקאות מתחת ל-85%.

7. **Validate** → §VII: Checklist ידני + הרצת כל השערים:
   ```bash
   python scripts/qa_pipeline.py --gate all --zone {ZONE}
   ```
   פלט אוטומטי: `{ZONE}/output/QA_REPORT_{date}.md` — יש לצרף ל-commit.

8. **(לאחר אישור הידרולוג בלבד) Generate executive summaries** → דוחות ניהוליים INTERNAL + PUBLIC.
   **לא חלק מהלולאה הראשית** — רץ רק אחרי שהדוח המלא (שלב 5) אושר. ה-**brief YAML** (`report-engine/briefs/{zone}.yaml`) הוא ה-artifact הסטנדרטי של שלב זה: הוא נגזר מהדוח המלא ונושא `source_report_version` + `source_report_sha` (חוזה טריות).
   ```bash
   # 8a (דטרמיניסטי): גזירת brief-prompt מהדוח האחרון + provenance
   python scripts/generate_zone_brief.py prepare --zone {zone}
   # 8b (OPUS #3): הרצת הprompt → raw_brief.yaml (9 ממצאים, dual framing, מקורות)
   # 8c (דטרמיניסטי): finalize + רינדור HTML צמודים
   python scripts/generate_zone_brief.py finalize --zone {zone}
   python scripts/generate_zone_html_from_brief.py --zone {zone}
   ```
   **חסימה על FAIL**:
   - **Gate brief↔report sha** (REQ #31.2): `source_report_sha` ב-brief חייב לתאום את ה-sha של הדוח הנוכחי — אחרת מופצים דוחות ניהוליים מיושנים תחת גרסה חדשה.
   - **Gate אנונימיזציה** (REQ #31.3): PUBLIC חייב להיות נקי משמות-מתקנים אמיתיים (סריקה מול רשימת שמות) — דליפה = FAIL.
   > ⚠️ **מגבלה ידועה (REQ #31.1)**: `generate_zone_html_from_brief.py` ממלא כיום את כל סעיפי ה-brief (כולל `stats_public`, `means_summary`, `methodology`, `timeline`) — אזור חדש מקבל את נתוניו שלו ולא של חולון. (לפני התיקון: רק 5 סעיפים הוחלפו; השאר נשארו hardcoded מ-reference חולון.)

**Precedent for Zone N+1**: Once Zone N passes expert validation, store as `[N+1]/lean_workspace/01_inputs/[N]_approved_precedent.md`.

### VIII.1 Pipeline Ordering — תקין (V5+)

**עיקרון מרכזי**: **Opus בוחר אילו קידוחים** לאייר; **הסקריפט מחליט איך** לאייר (גודל, צבעים, סדר, סוג גרף) על בסיס סגנון מוסכם.

**סדר תקין**:
1. **Opus call** → כותב את V4.md הטרי (10 סעיפים, narrative פרשני, **בחירת קידוחים** למוקדים).
2. **חילוץ קידוחים** → `extract_report_boreholes(v4_md_path)` מחלץ את רשימת הקידוחים שהוזכרו ב-V4.md.
3. **יצירת גרפים** → `svg_charts.py` מקבל `boreholes_override=List[str]` ומאייר רק את הקידוחים שנבחרו. הסגנון (RTL, צבעים, גודל, סוג גרף) מוגדר ב-svg_charts.py לפי הסגנון של הדו"ח המעוצב + תיקונים עד כה.
4. **Render HTML** → `generate_holon_full_html.py` (full report) + `generate_holon_designed.py` (mini-report).

**עריכת ידנית מתי בסדר**: רק תיקוני post-Opus של ולידציה (סעיף VII) — תיקוני טרמינולוגיה, סדר משפחות, פערים. **לא** הרחבות מבניות (אלה מחייבות Opus call טרי).

**API**:
```python
# scripts/report_designed/data_loader.py
def extract_report_boreholes(v4_md_path: str) -> List[str]:
    """Parse V4.md, extract all borehole IDs mentioned in §4–6."""
    ...

# scripts/report_designed/svg_charts.py
def svg_cvoc_panels(data, boreholes_override: Optional[List[str]] = None) -> str:
    if boreholes_override:
        # use Opus's selection
    else:
        # fallback: top-6 by severity (legacy)
```

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

## Toolkit Resources (Self-Contained Playbooks)

🔧 **Zone Report V5 Process**: `toolkit/playbooks/zone_report_process_v5.md` (lightweight 7-step pipeline summary for team distribution)

🔧 **Zone Diagnosis Template**: `toolkit/playbooks/zone_diagnosis_template.md` (8 professional diagnostic questions + reading order)

🔧 **Forensics Attribution Guide**: `toolkit/playbooks/forensics_attribution_guide.md` (A–E evidence classification + 3-criterion confidence, with attribution workflow)

🔧 **Monitoring Gaps Checklist**: `toolkit/playbooks/monitoring_gaps_checklist.md` (gap detection patterns + dual-audience framing)

🔧 **Data Pipeline Spec**: `toolkit/playbooks/data_pipeline_spec.md` (6-CSV schema summary; references this guide's detailed version)

---

**Status**: V5 Hybrid Pipeline | SSOT לטרמינולוגיה ולסדר פייפליין | Scalable to all 18 zones  
**Last Updated**: 2026-05-14 (Refactor: §III סולם 9-רמות קנוני, §IV סדר משפחות אדפטיבי, §VIII.1 pipeline ordering נפתר, §I.2 PDF ingestion, §I.5 Web sources)  
**Last Sanitized**: 2026-05-27 (Toolkit back-references added)  
**Governance**: CLAUDE.md (אינדקס אזורים + Phase H) + project REQUIREMENTS.md
