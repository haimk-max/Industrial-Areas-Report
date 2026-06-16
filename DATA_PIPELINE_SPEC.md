# Data Pipeline Specification — Structured Data Pack

**מטרה**: Schema של 6 ה-CSVs ב-`02_data/` בעת Hybrid V5 Pipeline.

**תפקיד**: קובץ זה מגדיר את החוזה בין data pipeline (deterministic scripts) לבין Opus + report generation.

---

## 1. measurements_scoped.csv

**מטרה**: כל מדידה בקידוחים של האזור.

**עמודות** (mandatory):

| עמודה | סוג | הסבר | דוגמה |
|------|------|-------|---------|
| `canonical_well_id` | string | מזהה קידוח ייחודי (ITM-based או שם סטנדרטי) | `nt_holon_01`, `nee_raanana_02` |
| `original_well_name` | string | שם בדוח מקורי (TAHAL, אקולוג, וכו') | `נת-חולון-1`, `בעל"א 4-A` |
| `well_type` | enum | סוג קידוח: monitoring, supply, observation | `monitoring` |
| `zone_scope_source` | string | איפה נמצא הקידוח (איזה אזור / דוח) | `Holon_main_industrial`, `Raanana_perimeter` |
| `parameter_canonical` | string | שם כימי סטנדרטי (TCE, PFOA, Cr, etc.) | `TCE`, `PFHxS`, `Chromium` |
| `parameter_original` | string | שם בדוח מקורי | `Trichloroethylene`, `Cr(VI)` |
| `unit_original` | string | יחידות בדוח מקורי | `µg/L`, `ppb`, `mg/L` |
| `unit_standardized` | string | יחידות סטנדרטיות (כל קודים: µg/L) | `µg/L` |
| `dws_value` | float | Drinking Water Standard (מי שתייה תקן) | `5.0`, `70.0`, `100.0` |
| `result_value` | float | ערך המדידה (numeric; "ND" → NULL) | `5000.0`, `15.5`, `<1.0` |
| `result_date` | date | תאריך המדידה (YYYY-MM-DD) | `2024-06-15` |
| `result_qualifier` | enum | איכות התוצאה: =, <, >, ≤, ≥, ND | `=`, `<`, `ND` |
| `source_file` | string | שם הדוח / הקובץ | `TAHAL_2008_PartB`, `2021_Report_page_52`, `current_monitoring_2024` |
| `source_row_or_page` | string | מיקום בדוח: page, table row, date | `page 52`, `table 3 row 12`, `June 2024 field report` |

**דוגמה**:

```csv
canonical_well_id,original_well_name,well_type,zone_scope_source,parameter_canonical,parameter_original,unit_original,unit_standardized,dws_value,result_value,result_date,result_qualifier,source_file,source_row_or_page
nt_holon_01,נת חולון 1,monitoring,Holon_main_industrial,TCE,Trichloroethylene,µg/L,µg/L,5.0,250.0,2024-06-15,=,current_monitoring_2024,June 2024 field report
nt_holon_01,נת חולון 1,monitoring,Holon_main_industrial,PFOA,Perfluorooctanoic acid,µg/L,µg/L,0.07,0.15,2024-06-15,=,current_monitoring_2024,June 2024 field report
nt_holon_02,נת חולון 2,monitoring,Holon_perimeter,Chromium,Cr(VI),µg/L,µg/L,50.0,,2023-01-01,,TAHAL_2008_PartB,page 52
```

---

## 2. latest_results.csv

**מטרה**: תוצאה אחרונה לכל קידוח × parameter (quick lookup).

**עמודות** (mandatory):

| עמודה | סוג | הסבר |
|------|------|-------|
| `canonical_well_id` | string | מזהה קידוח |
| `parameter_canonical` | string | שם כימי סטנדרטי |
| `latest_value` | float | ערך אחרון |
| `latest_date` | date | תאריך המדידה האחרונה |
| `unit_standardized` | string | יחידות (µg/L) |
| `dws_value` | float | תקן מי שתייה |
| `ratio_to_dws` | float | latest_value / dws_value × 100 (%) |
| `severity_index` | int | אינדקס 0–8 (לפי bucket formula) |
| `last_updated_from` | string | מקור (source_file) |

---

## 3. severity_by_well_family.csv

**מטרה**: אינדקס חומרה לכל קידוח × משפחה כימית.

**חשוב**: based on **C_max_5y** (לא latest result). חלון ברירת מחדל = 5 שנים אחרונות מעכשיו.

**עמודות** (mandatory):

| עמודה | סוג | הסבר |
|------|------|-------|
| `canonical_well_id` | string | מזהה קידוח |
| `family` | enum | CVOC, METALS, PFAS, FUEL |
| `max_value_window` | float | ערך מקסימלי בחלון 5 שנים |
| `max_value_date` | date | תאריך ערך המקסימום |
| `window_start` | date | תחילת חלון (YYYY-MM-DD) |
| `window_end` | date | סיום חלון (YYYY-MM-DD) |
| `lead_parameter_by_family` | string | הparameter שגרם למקסימום (TCE, Cr, וכו') |
| `ratio_to_dws` | float | max_value_window / dws_value × 100 (%) |
| `severity_index` | int | אינדקס 0–8 |
| `dws_reference_value` | float | תקן שנבחר לחישוב |

**דוגמה**:

```csv
canonical_well_id,family,max_value_window,max_value_date,window_start,window_end,lead_parameter_by_family,ratio_to_dws,severity_index,dws_reference_value
nt_holon_01,CVOC,8750.0,2019-12-15,2019-12-01,2024-06-15,TCE,175000.0,8,5.0
nt_holon_02,METALS,150.0,2023-06-10,2019-06-10,2024-06-15,Chromium,300.0,6,50.0
nee_raanana_05,PFAS,0.5,2024-06-15,2019-06-15,2024-06-15,PFHxS,714.3,6,0.07
```

---

## 4. trends_by_well_parameter.csv

**מטרה**: תוצאות Mann-Kendall לכל קידוח × parameter.

**עמודות** (mandatory):

| עמודה | סוג | הסבר |
|------|------|-------|
| `canonical_well_id` | string | מזהה קידוח |
| `parameter_canonical` | string | שם כימי |
| `mann_kendall_z` | float | Z-statistic (tie-corrected, continuity-corrected) |
| `mann_kendall_p` | float | p-value |
| `snr` | float | Signal-to-Noise Ratio (variance-based) |
| `soft_trigger_met` | boolean | true אם 2+ consecutive rising values בחלון 5 שנים |
| `trend_classification` | enum | RISING, STABLE, DECLINING, INSUFFICIENT_DATA |
| `n_measurements` | int | מספר מדידות בחלון |
| `time_span_years` | float | משך החלון בשנים |
| `notes` | string | הערות (לדוג' "only 3 measurements", "gap 2020-2021") |

**תנאים לMK**:
- Window: 5 שנים אחרונות (ברירת מחדל)
- tie-corrected variance
- continuity-corrected Z
- SNR threshold (gate): SNR > 5 כדי להחשיב כמובהק (recommendation, לא חובה בCSV)
- soft_trigger: 2 consecutive rising values (לא 3)

---

## 5. monitoring_gaps.csv

**מטרה**: תיעוד של פערי ניטור — קידוחים שסגרו, parameters עם n<5, time gaps.

**עמודות** (mandatory):

| עמודה | סוג | הסבר |
|------|------|-------|
| `canonical_well_id` | string | מזהה קידוח |
| `parameter_canonical` | string | שם כימי (או "overall" אם הקידוח כולו סגור) |
| `last_measurement_date` | date | תאריך מדידה אחרונה |
| `is_active` | boolean | true אם ניטור פעיל |
| `reason_if_inactive` | enum | closed, no_budget, contaminated, relocated, unknown |
| `n_measurements_total` | int | מס' מדידות בכל ההיסטוריה |
| `n_measurements_last_5y` | int | מס' מדידות בחלון 5 שנים |
| `coverage_note` | string | הערה (לדוג' "gap 2020-2022", "only field measurements") |

**דוגמה**:

```csv
canonical_well_id,parameter_canonical,last_measurement_date,is_active,reason_if_inactive,n_measurements_total,n_measurements_last_5y,coverage_note
nt_holon_02,overall,2022-03-15,false,closed,"Monitoring well sealed",15,0,gap 2022-2024
nt_holon_05,PFAS,2024-06-15,true,,8,3,only 3 PFAS measurements
```

---

## 6. figure_ready_series.csv

**מטרה**: time series מוכן לגרפים (long format, לא wide format).

**עמודות** (mandatory):

| עמודה | סוג | הסבר |
|------|------|-------|
| `canonical_well_id` | string | מזהה קידוח |
| `parameter_canonical` | string | שם כימי |
| `date` | date | תאריך מדידה |
| `value` | float | ערך |
| `severity_index` | int | אינדקס 0–8 (חישוב בזמן real time אם צריך, או pre-calc) |
| `unit_standardized` | string | יחידות |
| `include_in_trend_figure` | boolean | true אם להציג בגרף מגמה (לפי boreholes_override אחרי Opus) |

**הערה**: `include_in_trend_figure` עשוי להשתנות אחרי Opus call (כשBoreholes נבחרים). CSV הראשונית = true לכל הקידוחים הפעילים.

---

## Notes on Schema Alignment

1. **Source traceability**: כל CSV מכיל `source_file` ו-`source_row_or_page` (או שקול) כדי לאפשר VerificAtion.
2. **C_max_5y ≠ latest_result**: אלה שתי מדידות שונות. `severity_by_well_family` משתמש ב-C_max_5y; `latest_results` משתמש בתוצאה האחרונה. שניהן חשובות.
3. **Window definition**: ברירת מחדל = 5 שנים אחרונות מתאריך ה-export. תועד בצורה ברורה (window_start, window_end).
4. **PFAS special case**: אם parameter_canonical = "PFHxS", "PFOA", וכו' (לא "TPFAS" או "BETK"), זה valid. מחרוצות מסוגות סכומות ("TPFAS") מוסרות.

---

## See Also

🔧 **Self-contained toolkit playbook**: `toolkit/playbooks/data_pipeline_spec.md` (lightweight summary for team distribution; references this SSOT for full details)

---

**Last Updated**: 2026-05-17  
**Phase**: H+ (Hybrid V5 Pipeline — Documentation)  
**Last Sanitized**: 2026-05-27 (Back-references added)
