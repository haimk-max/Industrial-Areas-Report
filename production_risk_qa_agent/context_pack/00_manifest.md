# Manifest — Production Risk Q&A Agent Context Pack

**מטרה**: להגדיר במדויק אילו קבצים נכנסים לריצת הסוכן ואילו לא. קובץ זה מנע הכנסה בטעות של ארטיפקטים מיושנים או בעייתיים.

**גרסה**: 1.0  
**תאריך יצירה**: 2026-06-17  
**אזור**: חולון (אזה״ת חולון)

---

## ✅ קבצים שנכנסים לקלט הסוכן

### `context_pack/data/` — CSV (מספרים)

| קובץ | שורות | עמודות | מקור | תפקיד |
|------|-------|--------|------|--------|
| **zone_wells.csv** | 113 | 7 | Holon/02_data/ | רישום קידוחים: ID, שם עברי, קואורדינטות ITM, סוג (monitoring/industrial_monitoring/fuel_monitoring/**private_production**), מוקד |
| **severity_by_well_family.csv** | 192 | 10 | Holon/02_data/ | **חומרת זיהום לפי משפחה** (C_max_5y בחלון 5 שנה, דברך שריםקת 0–8). טבלת אב לסיכון. |
| **latest_results.csv** | 3,810 | 8 | Holon/02_data/ | תוצאה אחרונה לכל זוג (קידוח, פרמטר): ריכוז, תאריך, יחס לתקן, אינדקס חומרה |
| **trends_by_well_parameter.csv** | 699 | 9 | Holon/02_data/ | Mann-Kendall Z, p, SNR, trend_classification (ALERT/WATCH/STABLE/DECLINING/NONE), מס' מדידות |
| **monitoring_gaps.csv** | 3,663 | 9 | Holon/02_data/ | פערי ניטור: אילו קידוחים הופסק בהם ניטור, מתי, כמה מדידות ב-5 שנות בחלון |
| **source_candidates_index.csv** | 31 | 20 | Holon/context_pack/03_context/ | **מועמדי מקור**: שם, סוג, משפחות מזהמים, רמת ודאות (HIGH/MEDIUM/LOW), רמת ראיה (A–E) |

**סינון מראש**: כל ה-CSVs מסוננים ל-**4 משפחות מזהמים רלוונטיות**:
- CVOC (TCE, PCE, DCE, VC, TCA, וכו')
- FUEL (BTEX, MTBE)
- METALS (Cr, Ni, Cd, As)
- PFAS (PFOS, PFOA, PFHxS, וכו')

פרמטרי איכות מים שאינם מזהמים תעשייתיים (pH, EC, calcium, turbidity, וכו') **אינם** בקבצים.

### `context_pack/context/` — MD (הקשר נרטיבי)

| קובץ | שורות | מקור | תפקיד |
|------|-------|------|--------|
| **zone_diagnosis.md** | 350+ | Holon/context_pack/04_diagnosis/ | **אבחון מקצועי** של האזור: 7 מוקדי זיהום, שרשראות פירוק, טבלת סדר מוקדים לפי חומרה יורדת, שאלות פתוחות, פערי מידע |
| **hydrogeology_holon.md** | 150+ | Holon/lean_workspace/04_deterministic_anchors/ | **פרמטרי זרימה וקיווניות**: כיוון זרימה דרום-מערבי, סוג אקוויפר (חול חוף עם שכבות חרסית), עומק קידוחים, DNAPL outlast, משמעות יד-גיאוגרפית |
| **source_candidates_context.md** | 427 | Holon/context_pack/03_context/ | **תיאור מעמיק של 9–12 מועמדים ראשיים** (A/B grade evidence): שם, סוג פעילות, מיקום, תאימות כימית, קרבה הידרוגיאולוגית, רמת ודאות |
| **forensics_brief.md** | 250+ | Holon/lean_workspace/04_deterministic_anchors/forensics_brief.txt (המרה) | **סיכום פורנזי**: שרשראות פירוק TCE/PCE, חתימות Cr+Ni, MTBE vs BTEX, דפוסי PFAS (or gap), הפסקות ניטור קריטיות, מגבלות |

**עיקרון**: קבצי MD אלו **אינם** טמפלייטים (לא מדריכים לסוכן איך לכתוב). הם **הקשר מקצועי** שהסוכן קורא בעמקות כדי להבין את המצב.

### `context_pack/xgboost/` — XGBOOST Interface & Sample

| קובץ | תפקיד |
|------|--------|
| **XGBOOST_INPUT_SPEC.md** | סכמה צפויה (placeholder) — מה הסוכן צופה מה-XGBOOST בזמן ריצה. גנרי; תקף לכל אזור. **יכול לכלול** `xgboost_new_wells.csv` עבור קידוחי הפקה **חדשים** (לא בתאימות zone_wells.csv), זוהו או ניבוי ע"י ML |
| **xgboost_results.SAMPLE.csv** | דוגמה סינתטית על הקידוחים האמיתיים בחולון (2 קידוחי הפקה + 2 קידוחי מעורבים משמעותיים) כדי להריץ בדיקת-איכות end-to-end |

---

## ❌ קבצים שלא נכנסים

### JSON גולמיים — לא כקלט

- **لא**: `facility_attribution.json` — JSON גולמי מודל
- **לא**: `extracted_findings.json` — merged findings JSON
- **לא**: `_findings_*.json` (5 files) — AI extraction JSONs
- **לא**: `_pdf_index.json` — metadata בלבד

**הנימוק**: JSON לא יספק כקלט פרשני למודל. כל הממצאים כבר המרנו ל-MD נרטיבי בעברית (source_candidates_context.md, zone_diagnosis.md, forensics_brief.md).

### קבצי מתודולוגיה / governance — לא כקלט

- **לא**: `CLAUDE.md` — governance ארוך טווח של הפרויקט; יגרור "חשיבה ישנה"
- **לא**: `ZONE_REPORT_PROCESS_GUIDE.md` — תיאור הפייפליין של V5 hybrid; לא רלוונטי לQ&A קצר
- **לא**: `DATA_PIPELINE_SPEC.md` — מפרט טכני לפייפליין
- **לא**: `REPORT_V5_SCHEMA.md` — סכמה לכתיבת דוח מלא (לא Q&A)

### דוחות קודמים / V-reports — לא כקלט

- **לא**: `HOLON_REPORT_V4.md` דרך `V8.md` — דוחות מלאים מהפרויקט. הסוכן שלנו לא כותב דוח; הוא עונה בקצרה
- **לא**: `Raanana/output/RAANANA_REPORT_V2.md` — תקדים משנה אחרת

---

## מילון נתונים — אינדקסים וקיצורים

### well_type (סוג קידוח)

- `monitoring` — קידוח ניטור כללי (תעשייה או מקום אחר)
- `industrial_monitoring` — קידוח ניטור בתוך אזור תעשייה
- `fuel_monitoring` — קידוח ניטור של תחנות דלק / שטחי דלק
- **`private_production`** — **קידוח הפקה פרטי** → **סיכון אספקה ישיר** ⚠️

### Contamination Families

- **CVOC** (Chlorinated VOCs): TCE, PCE, 1,1-DCE, cis-1,2-DCE, VC, TCA, DCA, Chloroform
- **FUEL** (Petroleum hydrocarbons): BTEX (Benzene, Toluene, Ethylbenzene, Xylenes), MTBE, ETBE, TPH
- **METALS**: Chromium (Cr), Nickel (Ni), Cadmium (Cd), Arsenic (As), Lead (Pb), Zinc (Zn)
- **PFAS** (Per- & polyfluoroalkyl substances): PFOS, PFOA, PFHxS, PFBS, GenX

### severity_index (0–8 scale)

Formula: `bucket(C_max_5y / DWS × 100)` where C_max_5y = maximum concentration in 5-year window (2021–2026), DWS = drinking water standard.

- **0–1**: נקי (Clean, <25% of standard)
- **2–3**: נמוך (Low, 25–50%)
- **4–5**: בינוני (Moderate, 50–100%)
- **6–7**: גבוה (High, 100–1,000%)
- **8**: גבוה מאוד (Very High / Extreme, >10,000%)

### trend_classification

- **ALERT**: Strong upward trend, soft_trigger=true + p<0.10 (SNR≥1.0) OR p<0.05 (SNR≥0.3)
- **WATCH**: Partial signal (soft_trigger OR MK at lower threshold)
- **STABLE**: No significant trend
- **DECLINING**: Significant downward trend (p<0.05)
- **NONE**: Insufficient data (n<5) or SNR gate failed

### Evidence Grade (A–E)

- **A**: raw_report_verified (direct quote, page ref) — STRONG
- **B**: ai_extracted_with_page_ref (AI-derived, page cited) — STRONG
- **C**: web_verified_current_activity (web status, NOT contamination proof) — CONTEXT ONLY
- **D**: inferred_candidate (plausible, not attested) — BACKGROUND / HYPOTHESIS
- **E**: weak/mention_only (single mention, no corroboration) — APPENDIX LEVEL

---

## עיקרון חלוקה

**שאלה לקבלת החלטה**: לפני שימוש בקובץ, שאל:

1. האם הקובץ הוא **נתונים משמעותיים** (CSV numeric / MD narrative)? → כן → הכנס
2. האם הקובץ הוא **טמפלייט / הנחיה איך לכתוב**? → כן → **אל תכנס**
3. האם הקובץ הוא **JSON גולמי**? → כן → **אל תכנס** (already converted to MD)
4. האם הקובץ הוא **קובץ מתודולוגיה / governance של הפרויקט**? → כן → **אל תכנס**
5. האם הקובץ הוא **דוח V-number קודם** (V1–V3, V4–V8)? → כן → **אל תכנס** (use only for audit trail)

---

## סיכום

**קלט**: ~1.2 MB של CSV (5.9 MB עם trends) + ~1.2 MB של MD (total ~7 MB)  
**קידוחים**: 113 סך הכל (111 פעילים), כולל **2 private_production** (סיכון אספקה)  
**מדידות**: 15,174 שורות (TPFAS/BETK בחרוג)  
**משפחות**: 4 (CVOC, FUEL, METALS, PFAS)  
**מוקדים**: 7 גיאוגרפיים מזוהים  
**מועמדים**: 31 מקור פוטנציאליים (A–E)

---

*קובץ זה הוא תחזוקה. עדכן אותו אם הוסיפים/מסירים קבצים מ-context_pack/.*
