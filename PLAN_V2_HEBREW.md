# תוכנית מימוש: V2 דוחות רעננה
## גרסה 2 — הערכה הידרוגיאולוגית מקצועית עם attribution של תעשיות

**תאריך**: מאי 3, 2026  
**סטטוס**: תוכנית עבודה מלאה — מוכן לביצוע  
**משך משוער**: 4–5 ימי עבודה

---

## 1. סקירת שינויים מ-V1 ל-V2

### מטרה אסטרטגית
התרת דוח סטטיסטי (מעקב מגמות Mann-Kendall + סיווגים ALERT/WATCH/STABLE) לתוך **הערכה הידרוגיאולוגית מקצועית** המתמקדת בזיהומים תעשייתיים בלבד, קשורה לתעשיות ספציפיות, וכתובה בסגנון רגולטורי (מערכת 2021).

### שינויים עיקריים

| מישור | V1 (סטטיסטי) | V2 (הידרוגיאולוגי) |
|------|-------------|------------------|
| **הוצאה** | NO₃, Cl⁻, THM, מתכות | רק CVOC, PFAS, BTEX |
| **מטבח תעשיות** | חסר | מלא — שמות אמיתיים, קואורדינטות, פעילויות |
| **טיימליין** | תלוש (1999-2008, 2008-2021, 2021-2026) | ממשיך (1999–2026 סיפור אחיד) |
| **מתודולוגית מגמות** | soft_trigger + MK → ALERT/WATCH/STABLE | soft_trigger מוסר; MK Z/p + תיאור טקסטי |
| **גרפים** | scatter points, per-borehole stacked | continuous curves, family-level stacked |
| **attribution** | חסר | בעיתוקים גבוהים/בינוניים/נמוכים |
| **קבצים** | RAANANA_ZONE_SUMMARY_REPORT.md | RAANANA_REPORT_V2.md (חדש; v1 נשמר) |

---

## 2. שלבים מימוש

### PHASE V.0: הכנה — חילוץ תעשיות אמיתיות מ-TAHAL 2008 Part B

**יעד**: החלפת placeholder facilities ב-netting אמיתיות מעמודות 53–67 של TAHAL 2008 Part B

**תהליך**:
1. קרא TAHAL 2008 Part B PDF (עמ' 53–67) ידנית
   - זיהוי רשימת תעשיות סמוכות לרעננה
   - קידום שם, סוג (כימיקלים, פרמצבטיקה, דלק, אחר), קואורדינטות, פעילויות, מזהמים צפויים
   - תעדוף: מזהומים החופפים לממצאים (TCE, PCE, BTEX, PFAS)
2. עדכון `base_layer/tahal_2008/raanana.json`:
   - הסר placeholder facilities (I-001, I-002, I-003)
   - הוסף תעשיות אמיתיות עם שמות אמיתיים או anonymization קבוע (לא arbitrary)
   - הוסף קואורדינטות ITM נכונות (בדוק ערכים קיימים בדוח)
   - הוסף מזהומים צפויים ממשיים

**פלט**: 
- `base_layer/tahal_2008/raanana.json` — מעודכן עם תעשיות אמיתיות
- `Raanana/data/tahal_facilities_extraction_notes.txt` — רשם קריאת PDF (עמודות משומשות, הערות)

**אומדן זמן**: 2–3 שעות (קריאה ידנית של PDF, validation)

---

### PHASE V.1: חיפוש תעשיות חיצוני — Web Search

**יעד**: תיעוד מהיכן מקורות CVOC, PFAS, BTEX ידוע או חשוד ברעננה

**תהליך**:
1. Web search על כל תעשיה אמיתית שחולצה מ-TAHAL:
   - שם תעשיה + "רעננה" + מזהם (למשל: "Chemical Facility X Raanana TCE")
   - חפש: סטטוס פעולה, תאונות/פליטות מדווחות, סגירה/רישוי, חדשות 2015–2026
   - צילום: תוקף פעולה, מידע פליטות

2. Web search ספציפיים לזיהומים שהוזהו:
   - "Raanana AFFF" — חפש דוחות על שימוש בקצף כיבוי (related turbine station)
   - "Raanana TCE" — חפש דוחות עבודה מישרד הגנת הסביבה
   - "Raanana benzene fuel" — חפש מידע על תחנות דלק בסביבה

3. עדכון `Raanana/data/facility_attribution.json`:
   ```json
   {
     "facilities": [
       {
         "id": "I-001",
         "name": "Chemical Facility X",
         "tahal_2008_page": 53,
         "type": "Organic chemicals synthesis",
         "coordinates": {"easting": 191400, "northing": 707100},
         "expected_contaminants": ["TCE", "PCE", "Benzene"],
         "web_findings": {
           "status_operating": "Yes (as of 2024)",
           "incidents_reported": "No major incidents 2015-2026",
           "news_summary": "Production increased 2020-2021; no environmental violations"
         },
         "attribution_to_boreholes": [
           {
             "borehole": "raanana_nt_1",
             "distance_m": 500,
             "gradient": "upgradient",
             "contaminant_match": "TCE + PCE profile matches expected",
             "confidence": "HIGH"
           }
         ]
       }
     ],
     "external_data_sources": {
       "queries": ["Raanana AFFF", "Raanana TCE", "Chemical Facility X", ...],
       "search_date": "2026-05-04",
       "summary": "Web search found no major new contamination sources; existing facilities in TAHAL 2008 remain operational"
     }
   }
   ```

**פלט**:
- `Raanana/data/facility_attribution.json` — מלא עם findings
- `Raanana/logs/web_search_log.md` — רשם שאילתות ותוצאות

**אומדן זמן**: 3–4 שעות (5–10 שאילתות ידניות × 20–30 דקות כל אחת)

---

### PHASE V.2: סידור נתונים TAHAL 1999–2008 עם Excel 2011–2026

**יעד**: איחוד היסטוריה 1999–2026 לטיימליין אחיד

**תהליך**:

1. **זיהוי קידוחים מתואמים** (TAHAL R-001 ↔ Excel raanana_nt_1):
   - בדוק קואורדינטות — TAHAL coordinates בברור שגויים (191392 vs 188515 easting)
   - חיוך לולתכל: האם R-001 בעמ' 53 של TAHAL מתאים לנת רעננה 1?
   - אם לא, תעדוף: השתמש רק ב-Excel measurements 2011–2026 לתיים אחד; TAHAL כ"הקשר היסטורי" בלבד (לא merged data)

2. **יצירת merged timeline**:
   - אם TAHAL/Excel קידוחים תואמים:
     ```
     1999-2008: TAHAL measurements (R-001)
     2008-2011: GAP (אין נתונים)
     2011-2026: Excel measurements (raanana_nt_1)
     ```
   - אם לא תואמים:
     ```
     1999-2008: TAHAL R-001 (historical context only; may be different borehole)
     2011-2026: Excel raanana_nt_1 (current monitoring; authoritative)
     → Note: TAHAL and Excel may represent different boreholes; not merged for trend analysis
     ```

3. **בדיקת תחביר נתונים**:
   - יחידות זהות? (TAHAL ppb vs Excel µg/L?)
   - טווחי פרמטרים זהים? (TCE, 1,2-DCA, Chloroform in both?)
   - רמת confidence בzihuim: TAHAL = context; Excel = authoritative

**פלט**:
- `Raanana/data/borehole_timeline_mapping.json` — זיהוי תחביר TAHAL/Excel
- `Raanana/logs/data_alignment_notes.md` — הערות על פערים/חוסרים

**אומדן זמן**: 1–2 שעות

**הערה חשובה**: אם TAHAL coordinates אינם תואמים Excel, נשמור על שני מערכי נתונים נפרדים עם בהירות מלאה בדוח. אין "יציאה" של פערים תחת השטיח.

---

### PHASE V.3: כתיבת דוח אזור V2

**יעד**: `Raanana/output/RAANANA_REPORT_V2.md` — דוח איזור חדש, סגנון 2021 Report

**מבנה V2 (8 סעיפים)**:

#### 1. תקציר מנהלים (Executive Summary)
- 3–4 ממצאים עיקריים עם מקורות תעשיה מזוהים/חשודים
- PFAS alert קריטי (turbine station, July 2025)
- דירוג חומרה בהשוואה ל-18 אזורים
- המלצה עדיפות (ניטור מיידי, דגימות confirmation)
- דוגמה פסקה:
  > "אזה"ת רעננה מנוטרת במערכת הניטור הלאומית של משרד הגנת הסביבה כחלק מ-18 אזורי תעשייה במישט התעשייה החוף. ממצאים 2011–2026 מגלים **4 מוקדי זיהום פעילים**: TCE בנת רעננה 1 (עד 817 µg/L, פי 109 מתקן), PCE בנת רעננה 3 (עד 105 µg/L), PFAS חדש בתחנת טורבינות (July 2025: PFHxS 1,160%, PFOA 524%), בנזן יציב בנד פז הנופר (10 ppb כנציב 2011–2024). **דרישת־עדיפות**: ניטור הד"כל בתחנת טורבינות Q2–Q3 2026 כדי להבחין בין זיהום חד־פעמי לממקור רציף."

#### 2. הקשר גיאוגרפי וגיאולוגי (Geographic & Geological Context)
- מיקום אזה"ת רעננה בצפון־מזרח המרינציפל
- קואורדינטות ITM אזורי (bounds של פוליגון אזור)
- כיוון זרימת מי תהום כללי (מ-2021 Report maps)
- סוג אקויפר (A2 חול קורקר, חוף, רגישות גבוהה per TAHAL 2008)
- שימוש קרקע: תעשיות כימיות, פרמצבטיקה, שירותים; תחנת דלק; תחנת כוח

#### 3. מפה תעשייתית וגיאוגרפיית סיכון (Industrial Facilities & Risk Landscape)
- טבלה: 4–6 תעשיות אמיתיות מ-TAHAL 2008 + web search findings
  ```
  | שם תעשיה | סוג | מיקום (E,N) | מזהמים צפויים | סטטוס 2008 | סטטוס 2024–2026 |
  |---------|-----|------------|--------------|----------|----------------|
  | Chemical Facility X | ייצור כימיקלים | 191400,707100 | TCE, PCE, Benzene | operating | Operating (web search) |
  | Pharmaceutical Y | תרופות | 191600,706800 | Solvents, VOCs | operating | Operating |
  | Fuel Station Z | דלק | 189174,677924 | BTEX, MTBE | operating | Operating |
  | Gas Turbine Site | כוח | 189345,678575 | AFFF (firefighting) | operating | Operating |
  ```
- מרחקים בחטיבה בקידוחים; כיווני gradient (upgradient/downgradient)

#### 4. סיפור זיהום אחיד 1999–2026 (Integrated Contamination Narrative)
- **CVOC — TCE בנת רעננה 1** (מוקד חם ראשי):
  - **1999–2008 (TAHAL)**: ריכוז 5–31 ppb; מדידות דלילות
  - **2011–2019 (Excel)**: עלייה חדה ל-817 µg/L (July 2019)
  - **2020–2026 (Excel recent)**: ירידה הדרגתית ל-95 µg/L (July 2025); עדיין פי 12 מהתקן
  - **Interpretation**: שרשרת ריקבון PCE→TCE זוהה (PCE 28.79 µg/L); מקור ראשוני במפעל תעשייתי upgradient (Facility X, מ-TAHAL 2008 + web search); פירוק "slow-moving" בתנאים אנאירוביים
  - **יחוס תעשיה**: Chemical Facility X (HIGH confidence) — coordinates match, expected contaminants match profile, operating since 1999

- **CVOC — PCE בנת רעננה 3** (מוקד חם שני):
  - **Timeline similar**: 1999–2008 sparse, 2011–2024 rising to 105 µg/L
  - **Interpretation**: plume נפרד או zone ריקבון שונה
  - **יחוס תעשיה**: Possibly Facility X (medium confidence) או Facility B (pharmaceutical, MEDIUM confidence)

- **PFAS — ממצא קריטי חדש בתחנת טורבינות** (מוקד חם חדש):
  - **July 2025 first detection**: PFHxS 1.160 µg/L (1,160% standard), PFOA 0.524 µg/L (524% standard)
  - **Pre-2025 absence does NOT imply non-existence**: PFAS testing only added to Excel 2025
  - **Source hypothesis**: AFFF foam (aqueous film-forming foam) from firefighting operations
  - **Facility attribution**: Gas Turbine Site (HIGH confidence for AFFF source); turbine station known for firefighting infrastructure; AFFF use typical at critical infrastructure
  - **Web search findings**: No major AFFF incident reported; routine firefighting drills likely source
  - **Status**: Urgent confirmatory sampling Q2–Q3 2026 to distinguish one-off from ongoing source

- **BTEX — בנזן בנד פז הנופר** (ממצא כרוני יציב):
  - **Timeline**: Consistent 10 ppb throughout 2011–2024 (200% standard)
  - **Source**: Fuel station (facility name known, operations standard)
  - **Interpretation**: chronic low-level leak; stable trend suggests no active remediation but not worsening
  - **Attribution**: Fuel Station Z (HIGH confidence) — name matches monitoring well designation, BTEX expected from gasoline

#### 5. ניתוח מגמות פשוט וסטטיסטי (Simplified Trend Analysis)
- **מטבח**: לא ALERT/WATCH/STABLE; במקום זה: תיאור טקסטי + Mann-Kendall Z, p-value (5y window) + SNR (אם computable)
- **דוגמה - TCE ב-nt_1**:
  > "בחלון 5 השנים האחרונות (2020–2026), TCE בנת רעננה 1 מראה מגמת ירידה (147 µg/L ב-2023 → 94.8 µg/L ב-2025). עם זאת, הירידה אינה סטטיסטית מובהקת בשל מספר מדידות נמוך בחלון (n5=2 < minimum required for MK). ריכוז עדיין **1,264% מתקן** (7.5 µg/L). Mann-Kendall (full record, 9 points): z=0.21, p=0.83 — אין מגמה סטטיסטית ברורה על פני 13 השנים."

- **דוגמה - PCE ב-nt_3**:
  > "בחלון 5 השנים (2020–2024), PCE בנת רעננה 3 מראה מגמת עלייה (63 µg/L ב-2022 → 105 µg/L ב-2024). Mann-Kendall (full record, מקום מדידות): z=2.55, p=0.011 — **עלייה סטטיסטית מובהקת** ברשומה הכוללת. הממצא דורש ניטור מוגבר."

- **דוגמה - Benzene ב-paz_hanofer**:
  > "בנזן בנד פז הנופר יציב במוצע 10 ppb (range 8–12 ppb) לאורך 2011–2024. אין סימן עלייה או ירידה סטטיסטית (Mann-Kendall p>0.05). מגמה יציבה תואמת להנחה של דלף כרוני קטן, לא תיקון פעיל."

- טבלה סיכום (ללא סיווג ALERT/WATCH):
  ```
  | בור | פרמטר | n | n5 | MK z (5y) | p (5y) | מגמה 5y | דעות |
  |-----|--------|---|----|-----------|----|---------|--------|
  | nt_1 | TCE | 9 | 2 | — | — | ירידה חלשה (n5 < min) | דורש ניטור ongoing |
  | nt_3 | PCE | 5 | 4 | 2.55 | 0.011 | **עלייה מובהקת** | ניטור רבעוני מוקדם |
  | paz | Benzene | 13 | 13 | 0.31 | 0.76 | יציב | שנתי מספיק |
  | turbine | PFAS | 1 | 1 | — | — | חדש; בדיקה דחופה | confirmation Q2–Q3 2026 |
  ```

#### 6. המלצות ניטור (Monitoring Recommendations)
- **By priority**:
  1. **URGENT (Q2–Q3 2026)**: Confirmatory PFAS dip sampling בתחנת טורבינות (לפחות 3 samples בחודשים שונים); מדוד PFOS, PFPeS, PFBA לשיוך סוג AFFF
  2. **HIGH (ממשיך רבעוני)**: TCE ב-nt_1; PCE ב-nt_3 (trend escalation)
  3. **MEDIUM (ממשיך שנתי)**: Benzene בpaz_hanofer (יציב, שנתי מספיק)
  4. **חדשים לשקול**: 6:2 Fluorotelomer Sulfonate (6:2 FTS) בturbine עבור AFFF discrimination

#### 7. מגבלות וצרכי review מומחה (Data Gaps & Expert Review Needs)
- TAHAL 1999–2008 דלילה (3–5 points per parameter, 10 years) → uncertainty גבוה
- PFAS testing only started 2025; pre-2025 absence ≠ non-existence
- Boron anomalies (2019-07-22, nt_2/nt_3: 61–83 mg/L) require lab retest
- Multiple facilities near boreholes → attribution probabilistic, NOT definitive
- **Requires expert hydrogeologist review** before regulatory submission
- Coordinate with Ministry of Environmental Protection before issuing recommendations

#### 8. מטא-נתונים ומקורות (Metadata & Sources)
- compilation date
- Excel snapshot date
- TAHAL 2008 extract: pages 53–67
- 2021 Report: pages X–Y
- web search: 2026-05-04
- Analyst: Claude Code
- Review status: Draft — pending expert validation

**סגנון וטון**:
- Hebrew formal, regulatory-facing (Ministry audience)
- Professional terminology (no jargon unexplained)
- Source attribution on every claim (page numbers visible)
- Tables for data, narrative for interpretation
- Limitations explicitly flagged (no "fudging")

**פלט**:
- `Raanana/output/RAANANA_REPORT_V2.md` — דוח אזור V2 מלא

**אומדן זמן**: 6–8 שעות (כתיבה, עריכה, validation נתונים)

---

### PHASE V.4: כתיבת כרטיסי קידוח V2

**יעד**: 7 כרטיסים חדשים (אחד לכל בור) — `Raanana/output/drilling_card_*_v2.md`

**מבנה כרטיס V2**:

#### 1. Header & Metadata
```
# כרטיס קידוח: [Name HE]
**Canonical ID**: [raanana_nt_1]  
**סוג**: [ניטור תעשיה]  
**קואורדינטות ITM**: E [188,515] / N [677,986]  
**עומק אקויפר**: [30 m]  
**תקופת ניטור**: [2012–2025]  
**מספר מדידות**: [557]  
**מפעיל**: [Ministry of Environmental Protection]  
```

#### 2. זיהום מרכזי ומצב נוכחי
- תיאור רשות: "נת רעננה 1 מנוטרת כחלק ממערך הניטור של אזה"ת רעננה..."
- מזהם דומיננטי: TCE (with details)
- ריכוז נוכחי: 94.8 µg/L (July 2025) = 1,264% standard
- טבלה: שנה | ריכוז | % מהתקן | מספר דגימות

#### 3. Timeline היסטורי מדוד (Historical Data Timeline)
```
| תקופה | מקור | ריכוז טיפוסי | ריכוז שיא | מגמה | הערות |
|--------|------|-----------|---------|------|--------|
| 1999–2008 | TAHAL | 5–27 ppb | 31 ppb | עלייה | sparse (4 measurements) |
| 2011–2019 | Excel | 10–200 | 817 | עלייה חדה | escalation began ~2017 |
| 2020–2026 | Excel | 95–147 | 147 | ירידה | recent moderation from peak |
```

#### 4. זיהומים משניים
טבלה: פרמטר | שיא | תאריך | % מהתקן | הערות

#### 5. ניתוח Forensics (לא בסיכום אלא פה)
- **Decay chain**: PCE → TCE → cis-DCE → Vinyl Chloride
  - TCE 817 µg/L + PCE 28.79 µg/L → suggests "mother compound" PCE with in-situ dechlorination
  - cis-DCE detected historically (2015) → supports reductive path
- **Source Attribution**: Chemical Manufacturing Facility X (HIGH confidence)
  - Distance: 500m upgradient
  - Expected contaminants: TCE, PCE (match)
  - Operations: 1999–present (consistent with TCE history)
  - Alternative: Facility B (pharmaceutical, MEDIUM confidence) — less likely given TCE dominance
- **Confidence Level**: HIGH (decay chain + gradient + facility match)

#### 6. סטטוס נוכחי וקונטקסט סיכון
- Latest measurement: July 29, 2025 | TCE 94.8 µg/L | PCE absent
- Status among 7 boreholes: **Highest TCE** (all others < 25 µg/L)
- Severity index (2021 Report context): Borehole class 7/8 (very high)
- Zoning context: Industrial facility upgradient

#### 7. ניתוח מגמות (no classification, just numbers + interpretation)
| Contaminant | n | n5 | MK z (5y) | MK p (5y) | SNR | Interpretation |
|---|---|---|---|---|---|---|
| TCE | 9 | 2 | — | — | — | Insufficient n5 for 5y MK; full record p=0.83 (not significant) |

#### 8. מגבלות וחוסרים
- Low measurement frequency (0–2 per year in most years)
- Gap 2008–2011 (no Excel data until 2011)
- Boron anomaly 2019-07-22 (17.3 mg/L) requires retest

#### 9. המלצות
| Priority | Action | Timeline | Details |
|----------|--------|----------|---------|
| Continued | Quarterly TCE + PCE monitoring | Ongoing | Track declining trend |
| Investigation | Facility X interview/inspection | 2026 Q3 | Verify operations, emissions control |
| Optional | Add cis-DCE, VC | 2026 Q3 | Better decay chain characterization |

**פלט**: 7 files
- `drilling_card_nt1_v2.md`
- `drilling_card_nt2_v2.md`
- ...
- `drilling_card_p25_v2.md`

**אומדן זמן**: 2–3 שעות (7 כרטיסים × 15–20 דקות כל אחד)

---

### PHASE V.5: שינויים קודיים — הסרת soft_trigger

**יעד**: הסרה מלאה של soft_trigger logic מהקוד; Methodological shift from classification to plain-language description

**שינויים ספציפיים**:

#### V.5.1 `config/analysis_config.yaml`
```yaml
# BEFORE:
soft_trigger:
  window_size: 2

# AFTER: (remove entire soft_trigger section)
# soft_trigger: disabled in v2
```

#### V.5.2 `scripts/preprocess.py`
- **Remove lines ~173** (soft_trigger_window extraction)
- **Remove lines ~219–223** (soft_trigger computation)
- **Remove line ~55** (soft_trigger field in TrendResult)
- **Remove classification logic** (lines ~263–272) that references soft_trigger
- **Keep**: Mann-Kendall Z, p-value, SNR computation (unchanged)
- **New field**: `trend_description` (string) instead of `classification` (enum)
  ```python
  if result.mk_p_5y < 0.05 and result.mk_z_5y > 0:
      result.trend_description = f"Rising trend (p={result.mk_p_5y:.3f}); MK Z={result.mk_z_5y:.2f}"
  elif result.mk_p_5y < 0.05 and result.mk_z_5y < 0:
      result.trend_description = f"Declining trend (p={result.mk_p_5y:.3f}); MK Z={result.mk_z_5y:.2f}"
  else:
      result.trend_description = f"No significant trend (p={result.mk_p_5y:.3f}); MK Z={result.mk_z_5y:.2f}"
  ```

#### V.5.3 `scripts/trend_analysis.py`
- Update output CSV to use `trend_description` instead of `classification`
- Drilling cards and zone summary use `trend_description` instead of ALERT/WATCH labels

#### V.5.4 `tests/test_preprocess.py`
- Update golden dataset: replace `classification` column with `trend_description` values
- Update assertions: no longer test for ALERT/WATCH; instead test MK z/p values
- New test: `test_soft_trigger_disabled()` — verify soft_trigger field does NOT exist in result
- Example change:
  ```python
  # BEFORE:
  assert result.classification == "ALERT"
  
  # AFTER:
  assert "Rising trend" in result.trend_description
  assert result.mk_p_5y < 0.05
  ```

**פלט**: Modified files
- `config/analysis_config.yaml`
- `scripts/preprocess.py`
- `scripts/trend_analysis.py`
- `tests/test_preprocess.py`
- `tests/golden/expected_trends.csv` (updated for new structure)

**אומדן זמן**: 2–3 שעות (קוד changes + test updates + validation)

---

### PHASE V.6: גרפים V2 — Restructured Charts

**יעד**: תיקייה חדשה של גרפים `Raanana/charts_v2/` עם family-level stacked bars + continuous time-series curves

**סוגי גרפים V2**:

#### Type 1: Family-Level Stacked Bar Charts (One per family)
- **CVOC_all_boreholes_absolute_v2.png**
  - X-axis: Years (1999, 2005, 2010, 2015, 2020, 2025) — annual or multi-year bins
  - Y-axis: Concentration (ppb or µg/L)
  - Bars: One per year; segments per borehole (nt_1, nt_2, nt_3, paz, turbine, p18, p25)
  - Purpose: Cross-borehole comparison — which boreholes have high TCE/PCE? How distributed?
  - Color scheme: nt_1=red, nt_2=orange, nt_3=yellow, paz=green, turbine=blue, p18=purple, p25=brown

- **PFAS_S_A_groups_absolute_v2.png**
  - Similar structure but S-group (blue) and A-group (orange) as separate grouped bars per year
  - Purpose: Distinguish PFAS composition change over time

- **BTEX_all_boreholes_absolute_v2.png**
  - BTEX family (Benzene, Toluene, Ethylbenzene, Xylene) as stacked sub-bars per borehole

#### Type 2: Continuous Time-Series Curves (Per-borehole, per-family)
- **CVOC_timeseries_nt1_v2.png** (TCE + PCE + cis-DCE on same plot)
  - X-axis: Time (1999–2026)
  - Y-axis: Concentration (ppb)
  - Lines: TCE = solid red, PCE = dashed blue, cis-DCE = dotted green
  - Annotation: TAHAL data points (circles, 1999–2008), Excel data (crosses, 2011–2026), gap (dashed connector 2008–2011)
  - Purpose: See decay chain progression over 27 years

- **PFAS_timeseries_turbine_v2.png** (S-group + A-group on same plot, 2025 only)
  - Single point (July 2025) since PFAS only measured once; annotate "first detection — dip sampling recommended Q2–Q3 2026"

- **BTEX_timeseries_paz_v2.png** (Benzene only, 2011–2024)
  - Continuous line; horizontal "trendline" overlay showing stability
  - Annotation: "Stable 10 ppb; no evidence of remediation"

#### Implementation Details
- Modify `scripts/generate_charts.py`:
  1. Query Excel measurements (2011–2026) + base_layer TAHAL (1999–2008, if available and matched)
  2. For each family:
     - Aggregate by year (annual bins or multi-year, depending on measurement density)
     - Create family-level stacked bar chart using matplotlib
     - Save as PNG in `Raanana/charts_v2/`
  3. For selected parameters (TCE, PFOA, Benzene):
     - Create continuous time-series curve (matplotlib `plot()`)
     - Annotate data sources (TAHAL circles, Excel crosses)
     - Save as PNG in `Raanana/charts_v2/`

- **File naming convention**: 
  - `[family]_all_boreholes_[mode]_v2.png` (e.g., `cvoc_all_boreholes_absolute_v2.png`)
  - `[family]_timeseries_[borehole]_v2.png` (e.g., `tcey_timeseries_nt1_v2.png`)

**פלט**: 
- Directory `Raanana/charts_v2/` with 8–12 PNG files
- Legend in each chart (Hebrew labels, borehole colors, line styles)

**אומדן זמן**: 3–4 שעות (graphing + legend + validation)

---

### PHASE V.7: בדיקות ו-Validation

**יעד**: Ensure V2 structures valid, charts render, content accurate

**Checklist**:

#### Data Integrity
- [ ] `base_layer/tahal_2008/raanana.json` — real facilities with non-placeholder names
- [ ] `facility_attribution.json` — populated with HIGH/MEDIUM/LOW confidence levels
- [ ] Excel measurements 2011–2026 load correctly (no NaN/parsing errors)
- [ ] TAHAL 1999–2008 data (if used) has matching borehole IDs or explicit mismatch noted

#### Documents
- [ ] `RAANANA_REPORT_V2.md` — 8 sections, each with substantive content
- [ ] All claims sourced (TAHAL page, 2021 Report page, Excel date visible)
- [ ] No ALERT/WATCH/STABLE labels (only trend descriptions)
- [ ] All 7 drilling cards (`drilling_card_*_v2.md`) exist and follow template
- [ ] Tone matches 2021 Report professional standard (עברית formal)

#### Code Changes
- [ ] soft_trigger removed from config, preprocess.py, trend_analysis.py
- [ ] Tests updated; all tests passing (`pytest tests/ -v`)
- [ ] `trend_description` field populated (not `classification`)
- [ ] golden dataset updated with MK z/p values instead of classification labels

#### Charts
- [ ] Family stacked bars render without error (CVOC, PFAS, BTEX)
- [ ] Time-series curves render correctly (TCE nt_1, PFOA turbine, Benzene paz)
- [ ] Legends correct (borehole colors, line styles, Hebrew labels)
- [ ] Data points annotated (TAHAL circles, Excel crosses)
- [ ] PNG files in `Raanana/charts_v2/` directory

#### External Data
- [ ] Web search completed (log in `web_search_log.md`)
- [ ] At least 5 facility searches performed
- [ ] PFAS hypothesis documented (AFFF source at turbine)

**אומדן זמן**: 2 שעות (testing, spot-checks, fixes)

---

## 3. סדר ביצוע (Execution Order)

```
PHASE V.0: Extract TAHAL real facilities from PDF
  ↓ (2–3 hours)
PHASE V.1: Web search on facilities
  ↓ (3–4 hours)
PHASE V.2: Data alignment TAHAL/Excel
  ↓ (1–2 hours)
PHASE V.3: Write zone summary V2
  ↓ (6–8 hours)
PHASE V.4: Write 7 drilling cards V2
  ↓ (2–3 hours)
PHASE V.5: Code changes — remove soft_trigger
  ↓ (2–3 hours)
PHASE V.6: Generate V2 charts
  ↓ (3–4 hours)
PHASE V.7: Testing & validation
  ↓ (2 hours)
FINAL: Commit & push
  (1 hour)
```

**סה"כ זמן משוער**: 22–30 שעות = 3–4 ימי עבודה מלאים

---

## 4. קריטריונים הצלחה (V2 Success Criteria)

- [ ] `base_layer/tahal_2008/raanana.json` — real facilities (non-placeholder)
- [ ] `facility_attribution.json` — populated with confidence levels
- [ ] `RAANANA_REPORT_V2.md` — 8-section, professional, sourced, no soft_trigger labels
- [ ] 7 × `drilling_card_*_v2.md` — follow new template
- [ ] Charts V2 (family stacked + time-series curves) — render, legend correct
- [ ] Code: soft_trigger removed; `trend_description` field used
- [ ] Tests passing; golden dataset updated
- [ ] All claims in V2 documents sourced (page numbers, dates visible)
- [ ] Hebrew tone matches 2021 Report standard
- [ ] V1 documents & charts preserved for comparison

---

## 5. Deliverables סיכום

| קובץ/תיקייה | סטטוס | משימה |
|-----------|--------|-------|
| `base_layer/tahal_2008/raanana.json` | עדכון | Real facilities |
| `Raanana/data/facility_attribution.json` | חדש | Attribution HIGH/MEDIUM/LOW |
| `Raanana/data/tahal_facilities_extraction_notes.txt` | חדש | PDF extraction log |
| `Raanana/logs/web_search_log.md` | חדש | Search queries & results |
| `Raanana/output/RAANANA_REPORT_V2.md` | חדש | Zone summary V2 |
| `Raanana/output/drilling_card_*_v2.md` (×7) | חדש | Drilling cards V2 |
| `Raanana/charts_v2/` (×8–12 PNGs) | חדש | Charts V2 |
| `config/analysis_config.yaml` | עדכון | Remove soft_trigger |
| `scripts/preprocess.py` | עדכון | Remove soft_trigger |
| `scripts/trend_analysis.py` | עדכון | Use trend_description |
| `tests/test_preprocess.py` | עדכון | Update golden data |

---

## 6. Notes & Edge Cases

1. **TAHAL/Excel coordinate mismatch**: אם קואורדינטות TAHAL לא תואמות Excel, נשמור משני מערכי נתונים נפרדים עם הערה ברורה בדוח.

2. **PFAS single measurement**: Single July 2025 PFAS measurement insufficient for trend analysis; recommend urgent Q2–Q3 2026 confirmatory sampling.

3. **Boron anomaly**: 2019-07-22 B values (61–83 mg/L) are extreme outliers; likely lab error; mark for retest, do NOT include in analysis.

4. **Web search effort**: Active but targeted — 5–10 searches for facility names, AFFF use, incidents; NOT exhaustive web crawl.

5. **Soft_trigger removal rationale**: Soft trigger (2 consecutive rising values) is useful for early-warning statistical dashboards but not standard in professional hydrogeological reports. V2 shift to expert interpretation + plain-language trend description is more appropriate for regulatory submission.

---

**מוכן לביצוע. סדר לפעולה ממתין לאישור.**

