# Playbook: Monitoring Gaps Checklist

> **צ'קליסט זיהוי וסימון פערי ניטור** — פערי ניטור הם **ממצאים אבחוניים, לא היעדרים**. קידוח שהפסיק לדווח אחרי שיא זיהום הוא דגל אדום, לא שורה ריקה.

---

## עיקרון יסוד

> **פער ניטור = ממצא.** השאלה אינה "מה חסר" אלא "מה הפסקנו לראות, ולמה זה מטריד".

קידוח שעמד על severity 6 ואז שתק 47 חודשים מסתיר תמונה — לא חושף שיפור. שתיקה מתואמת (קבוצת קידוחים שפסקה יחד) עשויה לרמז על החלטת ניהול ניטור, לא על דעיכת זיהום.

---

## חלק א — שני מבני נתונים

פערי ניטור נמדדים בשתי רמות granularity:

### רמה 1: Per-Parameter (`monitoring_gaps.csv` — מפורט)

| עמודה | תיאור |
|-------|--------|
| `canonical_well_id` | מזהה קידוח |
| `parameter_canonical` | מזהם (TCE, Cr, PFOS...) |
| `last_measurement_date` | תאריך מדידה אחרונה |
| `is_active` | true/false — האם נמדד ב-5 שנים |
| `reason_if_inactive` | closed / abandoned / no_recent / unknown |
| `n_measurements_total` | סך מדידות היסטוריות |
| `n_measurements_last_5y` | מדידות ב-5 שנים אחרונות |
| `coverage_note` | הערת כיסוי |

### רמה 2: Per-Borehole (aggregated — לדוח)

| עמודה | תיאור |
|-------|--------|
| `borehole_id` | מזהה קידוח |
| `last_measurement_date` | מדידה אחרונה (כל פרמטר) |
| `months_silent` | חודשי שתיקה עד תאריך הדוח |
| `previous_max_bucket` | bucket שיא לפני השתיקה |
| `previous_max_parameter` | איזה פרמטר היה בשיא |
| `last_concentration` | ריכוז אחרון שנמדד |
| `assessment` | HIGH / MEDIUM / LOW (עדיפות) |

> שתי הרמות משלימות: per-parameter מזהה איזה **מזהם** הפסיק; per-borehole מתעדף **קידוחים** לחידוש.

---

## חלק ב — קריטריוני סף

### מתי פער הוא ממצא?

| תנאי | סף | פעולה |
|------|-----|--------|
| **שתיקה ארוכה** | `months_silent` ≥ 12 | רשום ב-monitoring_gaps |
| **שתיקה קריטית** | `months_silent` ≥ 12 **וגם** `previous_max_bucket` ≥ 5 | דגל HIGH |
| **דיגום דליל** | `n_measurements_last_5y` < 5 | סמן coverage חלקי |
| **פער מזהם-מפתח** | TCE/PCE/Cr/Ni/PFOS עם n_5y = 0 | פער כיסוי קריטי |
| **שתיקה אחרי שיא** | מדידה אחרונה = שיא היסטורי + ואז שקט | דגל אדום (הסתרה) |

### תיעדוף assessment

| Assessment | תנאי |
|-----------|------|
| **HIGH** | היה ב-bucket ≥5 לפני השתיקה (זיהום משמעותי "נעלם" מהמכ"ם) |
| **MEDIUM** | היה ב-bucket 3–4, או שתיקה 24–47 חודשים |
| **LOW** | היה ב-bucket ≤2, שתיקה 12–23 חודשים, מזהם משני |

---

## חלק ג — דפוסים לזהות אקטיבית

### 1. שתיקה אחרי שיא (Post-Peak Silence)
ניטור שנעצר **בדיוק** אחרי מדידת שיא או בזמן מגמה עולה.
- **למה מטריד**: התמונה האחרונה היא הגרועה ביותר — ואז עיוורון.
- **בדיקה**: השווה `last_concentration` ל-`previous_max` — אם שווים, השיא הוא הנקודה האחרונה.

### 2. שתיקה מתואמת (Coordinated Silence)
קבוצת קידוחים שפסקה לניטור באותו חלון זמן.
- **למה מטריד**: מרמז על החלטת ניהול (תקציב/מדיניות), לא דעיכה טבעית.
- **בדיקה**: קבץ `last_measurement_date` — חפש אשכולות תאריכים.

### 3. פער כיסוי מזהם מתפתח (Emerging Contaminant Gap)
מזהם (PFAS, 1,4-דיוקסן, תוצרי פירוק) שמעולם לא נדגם, או נדגם בקידוחים הלא-נכונים.
- **למה מטריד**: הקידוחים בסיכון הגבוה לא נבדקו בדיוק לזה.
- **בדיקה**: cross-check coverage PFAS מול קידוחים ב-severity ≥5.

### 4. Vacuum גיאוגרפי (Geographic Vacuum)
קידוחי הפקה שנסגרו ללא ניטור חלופי בסמיכות.
- **למה מטריד**: אזור שלם ללא עיניים.
- **בדיקה**: האם יש קידוח פעיל <500m מהקידוח הסגור?

### 5. אסימטריית כיסוי (Coverage Asymmetry)
מזהמי-מפתח (TCE, Cr) עם coverage גבוה אך מזהמים משניים/מתפתחים עם n<5.
- **למה מטריד**: פאנל הדיגום צר מדי; מחמיץ מזהמים חדשים.

---

## חלק ד — שילוב עם המכנה הפעיל (Active Denominator)

> פערי ניטור משלימים את ספירת "הליבה הפעילה" — לא סותרים.

הפילטר מגדיר את **המכנה הפעיל** (קידוחים שנדגמו ב-5 שנים **וגם** נבדקו למזהמים מעבר לדלק). הקידוחים השקטים הם בדיוק אלו **שנשרו ממנו**.

**הצג שתי ספירות בנפרד**:
- **ליבה פעילה**: קידוחים העונים על שני תנאי הסינון (רעננות + לא-דלק-בלבד)
- **קידוחים היסטוריים ששתקו**: קידוחים שנשרו מהמכנה הפעיל  — טבלת monitoring_gaps

> **אזהרה**: אל תציג שיעור חריגות מבלי לציין selection bias — קידוחי ניטור מוקמו ליד מקורות חשודים.

---

## חלק ה — ניסוח דו-קהלי (פנימי מול ציבורי)

פערי ניטור מנוסחים שונה לפי קהל:

| היבט | ניסוח פנימי | ניסוח ציבורי |
|------|-------------|--------------|
| **מסגור** | אחריות ארגונית | שקיפות |
| **דוגמה** | "9 קידוחים שקטים 40–150 חודשים" | "אזורים שבהם הניטור צריך להתחזק" |
| **פעולה** | "חידוש דיגום CVOC ב-X, Y, Z" | "חידוש דיגום מתוכנן" |
| **טון** | פעולתי, מי-אחראי | מסביר, לא מתנשא |

---

## חלק ו — Checklist זיהוי פערים (להרצה על האזור)

- [ ] `monitoring_gaps.csv` נוצר (per-parameter, רמה 1)
- [ ] aggregated per-borehole חושב (רמה 2) עם `months_silent` + `assessment`
- [ ] כל הקידוחים עם `months_silent` ≥ 12 רשומים
- [ ] קידוחים ב-`previous_max_bucket` ≥ 5  — דגל HIGH
- [ ] דפוס "שתיקה אחרי שיא" נבדק (last = max?)
- [ ] דפוס "שתיקה מתואמת" נבדק (אשכולות תאריכים)
- [ ] PFAS coverage cross-checked מול קידוחים ב-severity ≥5
- [ ] Vacuum גיאוגרפי נבדק (קידוחי הפקה סגורים ללא חלופה <500m)
- [ ] אסימטריית כיסוי נבדקה (מזהמי-מפתח מול משניים)
- [ ] שתי ספירות הוצגו בנפרד (ליבה פעילה מול היסטוריים ששתקו)
- [ ] selection bias caveat נכלל
- [ ] ניסוח דו-קהלי הוכן (אם נדרשים תקצירים פנימי+ציבורי)

---

## חלק ז — דוגמת פלט (טבלת monitoring gaps לדוח)

```markdown
| קידוח | מזהם בשיא | bucket בשיא | מדידה אחרונה | חודשי שתיקה | עדיפות |
|-------|-----------|-------------|--------------|-------------|--------|
| {well_A} | TCE | 6 | 2022-06 | 47 | 🔴 HIGH |
| {well_B} | Cr(VI) | 4 | 2023-11 | 30 | 🟠 MEDIUM |
| {well_C} | Benzene | 2 | 2024-08 | 21 | 🟢 LOW |
```

---

## הפניות

### Root SSOT & Data Integrity
📍 **Governance — Gaps as findings**: [`CLAUDE.md`](../../../CLAUDE.md) §5 Data Integrity Rule #2 (No Interpolation — flag gaps explicitly)  
📍 **Active-core methodology**: [`LESSONS.md`](../../../LESSONS.md) (ה"ח תשובה — active-core well counting pattern)

### Toolkit Playbooks & Data
📋 **Data Pipeline CSV 5 schema**: [`toolkit/playbooks/data_pipeline_spec.md`](../data_pipeline_spec.md) (CSV 5: monitoring_gaps.csv columns)  
📋 **Zone Diagnosis context**: [`toolkit/playbooks/zone_diagnosis_template.md`](../zone_diagnosis_template.md) §4 (Gap questions) + Question Group 4  
📊 **Example (Holon)**: `Holon/02_data/monitoring_gaps.csv`

---

**Version**: 1.0  
**Status**: ✓ TEMPLATE READY  
**Last Updated**: 2026-05-27
