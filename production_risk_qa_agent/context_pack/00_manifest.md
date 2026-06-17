# מניפסט חבילת הקונטקסט — סוכן Q&A סיכון לקידוחי הפקה

**תאריך**: 2026-06-17 (עדכון v2: Layered Context)  
**אזור**: חולון (Holon)  
**משימה**: Q&A מבוסס-XGBOOST + ניתוח פורנזי לסיכון קידוחי הפקה  
**ארכיטקטורה**: **Layered 4-tier (עומק משכיל)**

---

## ארכיטקטורה Layered — סקירה מהירה

קונטקסט מחולק ל-**4 שכבות** — סוכן בוחר איזו לנצל בכל שאלה:

| שכבה | שם | שימוש | קבצים |
|------|-----|--------|--------|
| **L0** | Core/Synthesized | 90% שאלות | V8 Report, zone_diagnosis, forensics_brief, CSVs, LAYER_0_README |
| **L1** | Supporting Context | 8% שאלות | reports_context, web_findings, LAYER_1_README |
| **L2** | PDF Extractions | 1–2% שאלות | pdf_extractions/*.json, manifest |
| **L3** | Raw TXT | <1% | external, _raw_text/ |

**דוגמה L0**: "מה הסיכון לקידוח X?" → zone_diagnosis + V8  
**דוגמה L1**: "איך אנחנו יודעים שתדיראן היא מקור?" → reports_context + evidence grades  
**דוגמה L2**: "מתי בדיוק הגלו TCE בנת חולון 11?" → extracted_findings.json (כל דוחות עד 2021)

---

## מה כלול בחבילה (What's In) — לפי שכבה

### **Layer 0: Core/Synthesized** (`context/`, `data/`, `xgboost/`)

#### 1. **CSV — נתונים כמותיים** (`data/`)

| קובץ | מקור | תוכן | משתמשים |
|------|------|------|---------|
| `zone_wells.csv` | Holon/02_data | 111 קידוחים פעילים, canonical IDs, קואורדינטות ITM, well_type (private_production, monitoring, fuel_monitoring) | סינון קידוחי הפקה |
| `severity_by_well_family.csv` | Holon/02_data | severity [0-8] לכל קידוח ומשפחת מזהם (CVOC, METALS, FUEL, PFAS) | הערכת סיכון דטרמיניסטי |
| `latest_results.csv` | Holon/02_data | ריכוזים עדכניים (C_latest) וממוצעים (C_avg) לכל קידוח-parameter | קיום / התוכן מזהמים |
| `trends_by_well_parameter.csv` | Holon/02_data | Mann-Kendall Z, p-value, slope, SNR, classification (ALERT/WATCH/STABLE/DECLINING/NONE) | זיהוי מגמות |
| `monitoring_gaps.csv` | Holon/02_data | תאריכי ניטור אחרון, פער זמני (months), סטטוס (active/stopped) | זיהוי פערי ניטור |
| `source_candidates_index.csv` | Holon/context_pack/03_context | מתקנים/תחנות משוערות, קואורדינטות, confidence (HIGH/MEDIUM/LOW), סוג | שיוך מקורות |

#### 2. **MD — Context (L0)** (`context/`)

| קובץ | משימה | עומק |
|------|-------|------|
| `HOLON_REPORT_V8.md` | דוח סיכום מלא עם תוצאות לכל קידוח וסעיף ניתוח (45 KB) | **סינתזה מלאה** ← חדש |
| `zone_diagnosis.md` | סיכום מקורות זיהום, מוקדים קריטיים, קידוחי הפקה בסכנה | סקר שלם |
| `forensics_brief.md` | decay chains, co-occurrence, source signatures, PFAS gaps (156 שורות — גרסה מלאה) | עומק פורנזי |
| `hydrogeology_holon.md` | זרימה טבעית (SW), קצב זרימה, עומק אקוויפר, שכבות חרסית | כללים הידרולוגיים |
| `source_candidates_context.md` | תיאור מתקנים: קיימים, סגורים, סוגים (ציפוי, דלק, כימיקלים, מזון) | ראיות A-E |
| `LAYER_0_README.md` | הנחיות — למתי להשתמש בL0, איך לנווט | מיקום שכבה |

#### 3. **XGBOOST Interface** (`xgboost/`)

| קובץ | תפקיד | פורמט |
|------|--------|--------|
| `XGBOOST_INPUT_SPEC.md` | סכמת הקלט הגנרית (placeholder) שעליה תזרום "המערכת ההיא" פלט XGBOOST | CSV schema |
| `xgboost_results.SAMPLE.csv` | דוגמה סינתטית על קידוחי ההפקה האמיתיים של חולון | CSV (well predictions + SHAP) |

---

### **Layer 1: Supporting Context** (`context/`)

| קובץ | משימה | עומק |
|------|-------|------|
| `reports_context.md` | הקשר דוחות עבר (TAHAL 2008, 2021 Water Authority) — כיצד הגיעו לממצאים (28 KB) | היסטוריה מובנה ← חדש |
| `web_findings_context.md` | מצב נוכחי מקורות — פעילות/סגירה 2026 (7.4 KB) | סטטוס נוכחי ← חדש |
| `LAYER_1_README.md` | הנחיות — מתי להשתמש בL1, דוגמאות | מיקום שכבה |

---

### **Layer 2: PDF Extractions** (`pdf_extractions/`)

| קובץ | מקור PDF | גודל | תוכן |
|------|----------|------|------|
| `extracted_findings.json` | כל 5 דוחות מאוחדים | 157 KB | **אינדקס מלא** — חפש כאן ראשון |
| `_findings_batyam2007.json` | TAHAL 2007 | 36 KB | ממצאים היסטוריים 2007 |
| `_findings_finalreport.json` | דוח סכום | 24 KB | סיכום עם ממצאים |
| `_findings_part1.json` | חלק 1 ניתוח | 34 KB | ניתוח חלק 1 |
| `_findings_part2.json` | חלק 2 ניתוח | 24 KB | ניתוח חלק 2 |
| `_findings_report2021.json` | Water Authority 2021 | 24 KB | דוח 2021 |
| `00_pdf_extractions_manifest.md` | אינדקס | — | סכמה JSON + דוגמה + הנחיות |

---

### **Layer 3: Raw TXT** (External, ללא import)

| קובץ | מקור | גודל | הערה |
|------|------|------|------|
| `_raw_text/*.txt` | Holon/data/external/ | 41–333 KB | גולמי, לא מובנה — backup בלבד |
| `_raw_text/README.md` | חדש | — | "שימוש רק במקרה חירום" |

---

## מה לא כלול (What's NOT In)

❌ **JSON גולמי**: facility_attribution.json, _findings_*.json — אלה artifacts משלב הניתוח, לא קלט סוכן  
❌ **דוחות V1–V5**: HOLON_REPORT_*.md, INTERNAL/PUBLIC HTML — אלה פלט, לא קלט  
❌ **קבצי מתודולוגיה**: severity_calculator.py, scripts/*, config/ — קוד, לא קלט  
❌ **טמפלייטים-כקלט**: zone_diagnosis_prompt_template.md, zone_report_prompt_template_v5.md — המודל לא ישתמש בהם ישירות  
❌ **figure files**: SVGs, PNGs — וויזואליזציה, לא קלט  

---

## קונבנציות ומילון

### well_type (בקובץ zone_wells.csv)
- `private_production` = קידוח הפקה (ממוקד בחקר סיכון → עדיפות דיווח)
- `monitoring` = קידוח ניטור תעשייתי (בקרה)
- `fuel_monitoring` = קידוח ניטור דלק (תחנות דלק)
- `industrial_monitoring` = קידוח ניטור תעשייתי (מתקנים כימיים)

### Severity Scale (0–8)
| bucket | range | interpretation |
|--------|-------|-----------------|
| 0 | 0–1% DWS | clean |
| 1 | 1–10% DWS | low |
| 2 | 10–50% DWS | moderate-low |
| 3 | 50–100% DWS | moderate |
| 4 | 100–500% DWS | moderate-high |
| 5 | 500–1000% DWS | high |
| 6 | 1000–5000% DWS | very high |
| 7 | 5000–50000% DWS | critical |
| 8 | >50000% DWS | extreme |

### Trend Classes (Mann-Kendall)
- **ALERT**: p < 0.05, Z > 0, SNR ≥ 0.3 (עלייה מובהקת)
- **WATCH**: 0.05 ≤ p < 0.1, Z > 0 (עלייה חלשה)
- **STABLE**: p ≥ 0.1, |Z| < 1 (ללא מגמה)
- **DECLINING**: p < 0.05, Z < 0 (ירידה מובהקת)
- **NONE**: אין מדידות / חסרות תצפיות

### Evidence Classification (A–E)
- **A**: חומר מקור מאומת (דוח רשמי, מדידה בשדה)
- **B**: AI-extracted with page reference (מוקסט דוח מסמך)
- **C**: web-verified, current activity (חיפוש אתר, תמונות עדכניות)
- **D**: inferred candidate (היקש מגיאוגרפיה + סוג תעשייה)
- **E**: weak/mention_only (אזכור חולף, בדיוק לא ברור)

---

## טעימות נתונים

### zone_wells.csv (head)
```
canonical_well_id,name_he,itm_easting,itm_northing,well_type,zone_scope_source,monitoring_site
מק_חולון_12,מק חולון 12,182088,657195,monitoring,Holon_main_industrial,
פ_אזור_מקור_חקלאי,פ אזור מקור חקלאי,182567,659210,private_production,Holon_main_industrial,
```

### severity_by_well_family.csv (head)
```
canonical_well_id,cvoc_severity,metals_severity,fuel_severity,pfas_severity
מק_חולון_12,8,3,0,0
מק_חולון_5,7,0,0,0
```

### trends_by_well_parameter.csv (head)
```
canonical_well_id,parameter,mann_kendall_z,p_value,snr,classification,slope_per_year
נת_חולון_2,TCE,0.5,0.6,0.1,STABLE,50
נת_חולון_2,PCE,2.13,0.034,0.35,ALERT,200
```

---

## טיפול במקרי קצה

### PFAS
כיסוי PFAS **מינימלי** (4 קידוחים מ-80). תוצאות: 0.0 µg/L בכולם.
- **דיווח**: "כיסוי מינימלי — אין דגימה על 98% הקידוחים. סטטוס PFAS באזור חולון **לא ידוע**."
- **לא לומר**: "אין PFAS בחולון" ← זו טעות; זה פער ניטור, לא היעדר.

### ניטור הופסק
2 קידוחים קריטיים (נת חולון 2, נד המרכבה ק2) בהם ניטור הופסק בשיא:
- **דיווח**: "ניטור הופסק [שנה] בעת [שיא]; פער קריטי."
- **המלצה**: חיזור דגימה

### קידוח חדש (ML prediction)
קידוח לא רשום ב-zone_wells.csv:
- **דיווח**: "זה ניבוי ML מבוסס מרחק + זרימה, לא מאומת במערכת. אך אם קיימים נתונים בקידוח עצמו (למשל TCE, Cr), זה עדות."
- **סטאטוס**: "משוער, דורש אימות שדה"

---

## להתחבר למערכת החיצונית

**"המערכת ההיא"** (external XGBOOST system) תזרום פלט בפורמט:
- `xgboost_well_predictions.csv`: canonical_well_id, predicted_risk_class, risk_probability
- `xgboost_feature_importance.csv`: canonical_well_id, feature_name, shap_contribution

ה-SYSTEM_PROMPT קורא שני קבצים אלה ומשלב עם החבילה הדטרמיניסטית.

---

## סטטוס מדידות

**עדכון**: 2026-06-17  
- **אחרון ממדידה**: 2024 (מק חולון 14 PFAS), 2023-2024 (רוב CVOC)
- **מתודולוגיה**: תמונת חתך (snapshot), לא forecast

---

## צעדים הבאים (לפי PROCESS.md)

1. ✅ חבילה מסודרת
2. ⏳ SYSTEM_PROMPT.md כתוב (Type A + Type B)
3. ⏳ test_questions.md עם 8+ שאלות
4. ⏳ בדיקת איכות (סוכן Claude Code מול החבילה)
5. ⏳ commit + push

