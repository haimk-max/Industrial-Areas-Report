# ORCHESTRATION.md — מפת הפייפליין מקצה-לקצה (V5 Hybrid)

> **מטרה**: נקודת-מבט אחת על כל שלבי הפייפליין — מה דטרמיניסטי, מה Opus, מה גנרי, מה עדיין נעוץ-בחולון, ואיזה שער QA חוסם כל שלב. נועד למנוע את "הקושי לסדר את הפייפליין בסוף".
>
> **דרַייבר**: `scripts/run_pipeline.sh <ZONE> <stage>` מריץ את השלבים הדטרמיניסטיים ועוצר בכל גבול Opus.
> **SSOT לתהליך**: `ZONE_REPORT_PROCESS_GUIDE.md` §VIII. כאן — שכבת ההרצה (איזה סקריפט, איזו מוסכמה).

---

## רצף 7 השלבים

| שלב | מה | סוג | סקריפט / כלי | שער QA |
|-----|-----|------|---------------|---------|
| 1 | הגדרת scope | חצי-ידני | `select_boreholes.py --zone <lc>` | — |
| 2 | Data Pack (6–7 CSVs) | **דטרמיניסטי** | `parse_excel` → `trend_analysis` → `forensics_analyzer` → **`generate_zone_data_pack.py --zone <Dir>`** | **Gate 2** |
| 3 | Context Pack | **ידני** (NotebookLM-like) | הרכבת `03_context/` (reports/sources/web) | — |
| 4a | רינדור prompt אבחון | **דטרמיניסטי** | `render_zone_prompt.py --step diagnosis` | Gate 3 |
| 4b | אבחון אזורי | **OPUS #1** | הרצת הprompt → `04_diagnosis/zone_diagnosis.md` | **Gate 4** |
| 5a | רינדור prompt דוח | **דטרמיניסטי** | `render_zone_prompt.py --step report` | **Gate 3** |
| 5b | דוח V5 | **OPUS #2** | הרצת הprompt → `output/{ZONE}_REPORT_Vn.md` | **Gate 5** |
| 6 | איורים + HTML | **דטרמיניסטי** | `generate_holon_v5_html.py` *(עדיין Holon-coupled — REQ #28)* | **Gate 6** |
| 7 | אימות | **דטרמיניסטי** | `qa_pipeline.py --gate all` | את כולם |

**גבולות Opus** (אי-אפשר לאטמט): 4b, 5b. הדרַייבר עוצר שם עם הוראת-המשך.

**חוזה בין-שלבי קריטי (4→5)**: `zone_diagnosis.md` מכיל בלוק `## סדר מוקדים`. שלב 5a גוזר ממנו את `{FOCUS_ORDER_LIST}` בזמן רינדור. **כל הרצה חוזרת של שלב 4 מחייבת רינדור-מחדש של שלב 5a** לפני Opus #2 — אחרת ה-snapshot מיושן (footgun ה-staleness, REQ #27 / HANDOVER).

---

## מוסכמת `--zone` (פיצול קיים-מראש)

| קבוצת כלים | טפסת `--zone` | דוגמה | נגזרת |
|-------------|----------------|--------|--------|
| סקריפטי-ליבה (parse_excel, trend_analysis, forensics, select_boreholes) | **אות קטנה** (מוגדל פנימית) | `--zone holon` | `Holon/data/` |
| כלי-V5 (generate_zone_data_pack, render_zone_prompt, qa_pipeline) | **שם-ספרייה** | `--zone Holon` | `Holon/02_data/`, `Holon/context_pack/` |

> איחוד המוסכמות לטפסה אחת = תת-משימת REQ #28 (נוגע ב-`cli_common.py` וכל סקריפטי-הליבה — לא בוצע עדיין).

---

## מצב גנריות הסקריפטים (חוב 18-האזורים)

| סקריפט | מצב | הערה |
|--------|------|------|
| `generate_zone_data_pack.py` | ✅ **גנרי** | `--zone`; אומת byte-identical על חולון |
| `parse_excel`, `trend_analysis`, `forensics_analyzer`, `select_boreholes`, `generate_charts_v2` | ✅ גנרי | `--zone` (אות קטנה) |
| `render_zone_prompt.py`, `qa_pipeline.py` | ✅ גנרי | `--zone` (שם-ספרייה) |
| `embed_holon_figures_v5.py` | ✅ גנרי תפקודית | מקבל paths כ-args; השם בלבד נעוץ-חולון |
| `generate_holon_v5_html.py`, `generate_holon_designed.py` | ⏳ **Holon-coupled** | קוראים מ-`report_designed/data_loader.py` (בסיס-ראיות V4 ב-`lean_workspace/`, שמות נעוצי-חולון). גנריזציה = REQ #28. **לא חוסם** ריצת חולון. |
| `generate_holon_full_html.py` | ⛔ **DEPRECATED** | V4-era |
| `build_holon_borehole_classification.py` | ⛔ **DEPRECATED** | V4-era legacy |

---

## הרצה מהירה (חולון)

```bash
ZONE_NAME_HE='אזה״ת חולון'  scripts/run_pipeline.sh Holon data
# … הרכב 03_context ידנית …
ZONE_NAME_HE='אזה״ת חולון'  scripts/run_pipeline.sh Holon render-diagnosis
# … OPUS #1 → zone_diagnosis.md … ; qa_pipeline --gate 4
ZONE_NAME_HE='אזה״ת חולון'  scripts/run_pipeline.sh Holon render-report
# … OPUS #2 → {ZONE}_REPORT_Vn.md … ; qa_pipeline --gate 5
scripts/run_pipeline.sh Holon html       # (חולון: generate_holon_v5_html.py)
scripts/run_pipeline.sh Holon validate   # Gate all
```

**עודכן**: 2026-06-10 (REQ #28 — שלב ראשון: data_pack גנרי + דרַייבר + מפה).
