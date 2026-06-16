# ORCHESTRATION.md — מפת הפייפליין מקצה-לקצה (V5 Hybrid)

> **מטרה**: נקודת-מבט אחת על כל שלבי הפייפליין — מה דטרמיניסטי, מה Opus, מה גנרי, מה עדיין נעוץ-בחולון, ואיזה שער QA חוסם כל שלב. נועד למנוע את "הקושי לסדר את הפייפליין בסוף".
>
> **דרַייבר**: `scripts/run_pipeline.sh <ZONE> <stage>` מריץ את השלבים הדטרמיניסטיים ועוצר בכל גבול Opus.
> **SSOT לתהליך**: `ZONE_REPORT_PROCESS_GUIDE.md` §VIII. כאן — שכבת ההרצה (איזה סקריפט, איזו מוסכמה).

---

## רצף השלבים

| שלב | מה | סוג | סקריפט / כלי | שער QA |
|-----|-----|------|---------------|---------|
| 1 | הגדרת scope | חצי-ידני | `select_boreholes.py --zone <lc>` | — |
| 2 | Data Pack (6–7 CSVs) | **דטרמיניסטי** | `parse_excel`  — `trend_analysis`  — `forensics_analyzer`  — **`generate_zone_data_pack.py --zone <Dir>`** | **Gate 2** |
| 3 | Context Pack | **ידני** (NotebookLM-like) | הרכבת `03_context/` (reports/sources/web) | — |
| 4a | רינדור prompt אבחון | **דטרמיניסטי** | `render_zone_prompt.py --step diagnosis` | Gate 3 |
| 4b | אבחון אזורי | **OPUS #1** | הרצת הprompt  — `04_diagnosis/zone_diagnosis.md` | **Gate 4** |
| 5a | רינדור prompt דוח | **דטרמיניסטי** | `render_zone_prompt.py --step report` | **Gate 3** |
| 5b | דוח Vn | **OPUS #2** | הרצת הprompt  — `output/{ZONE}_REPORT_Vn.md` | **Gate 5** |
| 6 | איורים + HTML | **דטרמיניסטי** | `generate_holon_v5_html.py --zone <lc>` *(✅ גנרי מ-REQ #28)* | **Gate 6** |
| 7 | אימות | **דטרמיניסטי** | `qa_pipeline.py --gate all` | את כולם |
| 8a | רינדור prompt brief | **דטרמיניסטי** | `generate_zone_brief.py prepare` *(גוזר מהדוח האחרון + provenance)* | — |
| 8b | brief ניהולי | **OPUS #3** | הרצת הprompt  — `raw_brief.yaml` | validate (ב-finalize) |
| 8c | דוחות ניהוליים | **דטרמיניסטי** | `generate_zone_brief.py finalize`  — `generate_zone_html_from_brief.py` | חוזה staleness + Gate 31.2/31.3 |

**גבולות Opus** (אי-אפשר לאטמט): 4b, 5b, 8b. הדרַייבר עוצר שם עם הוראת-המשך.

**שלב 8 (דוחות ניהוליים) — הערה**: רץ **אחרי אישור הדוח** (לא חלק מהלולאה הראשית). מייצר INTERNAL+PUBLIC exec summaries. נדחה לחולון עד אישור הידרולוג (REQ #29). **חוזה staleness**: ה-brief נושא `source_report_sha256_12`; `run_pipeline.sh ... exec-summary` מזהיר אם הדוח השתנה מאז.

> ⚠️ **מגבלת generator נוכחית (REQ #31.1 — חוסם אזור שני)**: `generate_zone_html_from_brief.py` מחליף כיום רק 5 סעיפים מה-brief (`context_intro`, `findings`, `framing_warning`, `zone_name`, `doc_id`). סעיפי `stats_public`, `means_summary`, `methodology`, `timeline` נשארים **hardcoded מה-reference template** (חולון). לחולון זה תקין (reference=חולון), אך **אזור שני יקבל נתוני-חולון שגויים** עד שתתווסף replacement logic לכל הסעיפים. **חוזה האנונימיזציה** (PUBLIC ללא שמות-מתקנים) ייאכף ע"י Gate 31.3; **חוזה הטריות** (brief↔report sha) ע"י Gate 31.2.

**חוזה בין-שלבי קריטי (4 —5)**: `zone_diagnosis.md` מכיל בלוק `## סדר מוקדים`. שלב 5a גוזר ממנו את `{FOCUS_ORDER_LIST}` בזמן רינדור. **כל הרצה חוזרת של שלב 4 מחייבת רינדור-מחדש של שלב 5a** לפני Opus #2 — אחרת ה-snapshot מיושן (footgun ה-staleness, REQ #27 / HANDOVER). **כיום נאכף במוסכמה בלבד**: הפרומפט חותם רק `template_sha256`, לא את ה-sha של zone_diagnosis.md, כך ש-Gate 3 לא תופס snapshot מיושן. **REQ #31.5** מוסיף חתימת `diagnosis_sha` + אכיפת Gate 3.

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
| `generate_holon_v5_html.py`, `generate_holon_designed.py` | ✅ **גנרי (REQ #28)** | `--zone <lc>` + auto-detect גרסה; `data_loader.py` מקבל `zone`. השם בלבד נעוץ-חולון. |
| `generate_zone_brief.py`, `generate_zone_html_from_brief.py` | ✅ גנרי | `--zone`; gozr מהדוח האחרון; tech-debt: עוגנים נעוצי-חולון ב-html-from-brief (REQ #29) |
| סקריפטי legacy (`scripts/legacy/*`) | ⛔ **ARCHIVED** | V4-era; ראה `scripts/legacy/README.md` |

---

## הרצה מהירה (חולון)

```bash
ZONE_NAME_HE='אזה״ת חולון'  scripts/run_pipeline.sh Holon data
# … הרכב 03_context ידנית …
ZONE_NAME_HE='אזה״ת חולון'  scripts/run_pipeline.sh Holon render-diagnosis
# … OPUS #1 → zone_diagnosis.md … ; qa_pipeline --gate 4
ZONE_NAME_HE='אזה״ת חולון'  scripts/run_pipeline.sh Holon render-report
# … OPUS #2 → {ZONE}_REPORT_Vn.md … ; qa_pipeline --gate 5
scripts/run_pipeline.sh Holon html       # generate_holon_v5_html.py --zone holon (auto-detect Vn)
scripts/run_pipeline.sh Holon validate   # Gate all
# … אחרי אישור הדוח בלבד: …
scripts/run_pipeline.sh Holon exec-summary  # Step 8: brief <bdi>prompt → OPUS</bdi> #3 → finalize → exec HTML
```

**עודכן**: 2026-06-14 (REQ #30 — V8 exec-summaries; REQ #31 — מגבלת generator בשלב 8c + footgun diagnosis_sha תועדו). קודם: 2026-06-10 (REQ #28 גנריזציה מלאה; REQ #29 שלב 8 + חוזה staleness).
