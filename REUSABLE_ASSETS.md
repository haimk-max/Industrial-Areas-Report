# REUSABLE_ASSETS.md — אינדקס נכסים בני-שכפול

> **מטרה**: למפות את כל מה שנבנה בפרויקט וניתן לשימוש חוזר — בפרויקטים אחרים, כתבנית מתודולוגית, או כתהליך מחזורי. מאורגן ב-3 עדשות: **סקילים**, **מתודולוגיית עבודה**, **תהליכים**.
>
> **קהל**: צוות שיפעיל את הפייפליין על 16 האזורים הנותרים; או מי שירצה לאמץ את דפוסי-העבודה בפרויקט data-heavy אחר.
>
> **דירוג ניוד (Portability)**: ⭐⭐⭐ = בלתי-תלוי-דומיין (העתק-הדבק) · ⭐⭐ = גנרי עם התאמה קלה · ⭐ = ספציפי-פרויקט (דורש refactor)

---

## עדשה 1 — סקילים (Skills מוכנים-להרצה)

נכסים ארוזים, בלתי-תלויי-נתוני-הפרויקט, שניתן להעתיק ל-`~/.claude/skills/` או להתקין כספרייה.

| נכס | נתיב | בשלות | ניוד | תיאור |
|------|------|--------|------|--------|
| **signalkit** (pylib) | `toolkit/pylib/signalkit/` | ✅ מלא | ⭐⭐⭐ | ספריית Python: `trend_analysis` (Mann-Kendall), `severity_calculator` (סולם 0–8), `forensics_engine` (decay chains + source signatures), `data_pipeline` (נרמול יחידות→ppb). התקנה: `pip install -e ./toolkit/pylib` |
| **trend-detective** | `toolkit/skills/trend-detective/` | ✅ מוכן | ⭐⭐⭐ | סקיל אינטראקטיבי: Mann-Kendall + SNR gating + soft-trigger על כל סדרת-זמן. עובד offline |
| **severity-calculator** | `toolkit/skills/severity-calculator/` | ✅ מוכן | ⭐⭐ | ניקוד חומרה (% מתקן → bucket 0–8); ספים ניתנים-להחלפה למסגרת-רגולציה אחרת |
| **/handover** | `.claude/skills/handover/SKILL.md` | ✅ פעיל | ⭐⭐⭐ | סיכום סוף-סשן מסונן (Shipped / In-flight / Watch-outs / Open questions) + עדכון `HANDOVER.md`. כבר בשימוש שוטף |
| `agent-rag` | `toolkit/skills/agent-rag/` | ⏳ שלד | — | תוכנן בלבד; ללא vector-store/embeddings (REQ #14, נדחה). **אל תתייחס ככלי עובד** |
| `hydro-analyzer` | (טרם נבנה) | ⏳ מתוכנן | — | פרסור דוחות הידרוגיאולוגיים → נתוני קידוח (REQ #19) |

**הנכסים הבשלים ביותר לייצוא מיידי**: `signalkit`, `trend-detective`, `/handover` — נקיים מ-secrets, מנתיבים-קשיחים ומתלות ישראלית.

---

## עדשה 2 — מתודולוגיית עבודה (דפוסי Governance)

הנכסים החזקים ביותר של הפרויקט: דפוסים שהוכחו על-פני 36+ דרישות סגורות. כל אלה **ברי-שכפול לכל פרויקט data-heavy רב-סשן**.

### 2.1 SSOT-driven enforcement (אכיפה מתוך מקור-אמת-יחיד) ⭐⭐⭐
מונחים אסורים, סדר-סעיפים וכללים מוגדרים **פעם אחת** במסמך-SSOT, ונאכפים כ-**קוד שנכשל** ולא כצ'קליסט ידני.
- דוגמה: מונחים אסורים = regex ב-`scripts/qa_pipeline.py` (Gate 5) נגזרים מ-`docs/STYLE_GUIDE.md §B.5`.
- **הלקח**: SSOT אחד מאכיף, לא מתעד בלבד. מונע סחף בין מסמכים מקבילים.

### 2.2 Provenance / staleness gates (חותמות-טריות) ⭐⭐⭐
חותמות SHA256-12 על artifacts נגזרים; שער QA מזהה drift אוטומטית.
- מימוש: `scripts/render_zone_prompt.py` חותם `template_sha` + `diagnosis_sha`; Gate 3 נכשל אם הם מיושנים.
- **הלקח**: פותר את "המסמך הנגזר התיישן בשקט" — הבעיה הנפוצה ביותר בפייפליינים מרובי-שלבים.

### 2.3 Requirements audit trail (`PROCESS.md`) ⭐⭐⭐
טבלת Open→Closed, כל שורה עם commit hash + שיטת-אימות מפורשת.
- **הלקח**: זיכרון ששורד context-compression; אחריותיות מלאה (אין סגירה שקטה). מושלם לפרויקט מדעי/רגולטורי הדורש ראיות.

### 2.4 Footgun register (`HANDOVER.md`) ⭐⭐⭐
**לא יומן יומי** — רישום אילוצים חוזרים בלבד. מתעדכן רק כשמתגלה דפוס-כשל חדש.
- **הלקח**: מאלץ החלטה אקטיבית להוסיף ערך → לא מצטבר רעש. מפריד "אילוצים נושאי-משקל" מפטפוט-סשן.

### 2.5 Zone-relative thresholds (ספים יחסיים-לנתונים) ⭐⭐⭐
ספים נגזרים מהנתונים (`wells × 0.8`), לא מספרים קשיחים.
- מקור: REQ #22 (הערות-km קשיחות הסתירו קידוחים) + REQ #33 (אזורים קטנים).
- **הלקח**: ערכים קשיחים מסוכנים כשההערות מתיישנות; החלף בחישוב מונע-נתונים.

### 2.6 Data-integrity discipline ⭐⭐⭐
"אל תַמְצִיא; דַגֵּל discrepancy למשתמש במקום לתקן בשקט."
- הוכח: גילוי שגיאת 47→48 בספירת קידוחים; אי-דטרמיניות `datetime.now()` (REQ #36).
- **הלקח**: דפוס תרבותי בר-העברה — תגליות-נתונים עוברות החלטת-משתמש, לא תיקון-שקט.

### 2.7 הפרדה דטרמיניסטי / גנרטיבי ⭐⭐⭐
**הדפוס המרכזי**: קוד מייצר את כל המספרים (severity, trends, gaps) דטרמיניסטית; ה-LLM עושה **רק סינתזה** מעל נתונים מאומתים.
- **הלקח**: זה מה שמאפשר QA gates אמינים. ה-LLM לא ממציא עובדות — הוא מנסח מעל data pack קבוע.

---

## עדשה 3 — תהליכים מחזוריים (Pipelines)

| תהליך | נתיב SSOT | בשלות | ניוד | תיאור |
|--------|-----------|--------|------|--------|
| **V5 Hybrid Pipeline** (7 שלבים) | `ZONE_REPORT_PROCESS_GUIDE.md` §VIII | ✅ 2 אזורים | ⭐⭐ | scope → data pack → context → diagnosis (Opus#1) → report (Opus#2) → HTML → validate. **מחייב ל-16 הנותרים** |
| **6-CSV Structured Data Pack** | `DATA_PIPELINE_SPEC.md` | ✅ גנרי | ⭐⭐ | סכמה דטרמיניסטית; `scripts/generate_zone_data_pack.py --zone <X>` |
| **8 QA Gates** | `scripts/qa_pipeline.py` | ✅ גנרי | ⭐⭐⭐ | אכיפה בכל שלב; FAIL חוסם, WARN מתריע. ראה טבלת השערים למטה |
| **Layered Context Pack** (L0–L3) | `production_risk_qa_agent/` (ענף נפרד) | ✅ הוכח | ⭐⭐ | היררכיה מעובד→גולמי עם הוראות-עומק. דפוס "LLM כרכיב במערכת חיצונית" |
| **5 Playbooks** | `toolkit/playbooks/` | ✅ מלא | ⭐⭐ | מדריכי-צוות ניתנים-להפצה: V5 process, data spec, diagnosis, forensics A–E, monitoring gaps |
| **3-Tier Borehole Selection** | `scripts/select_boreholes.py` | ✅ גנרי | ⭐⭐ | Tier 1 היסטורי + Tier 2 פוליגון + Tier 3 חוצה-אזור |
| **Dual-Check Classification** | `docs/BOREHOLE_CLASSIFICATION_GLOSSARY.md` | ✅ גנרי | ⭐⭐ | purpose סמכותי + קידומת-שם fallback + conflict detection (REQ #35) |

### 8 QA Gates — סקירה
| Gate | תחום | חוסם? | SSOT |
|------|------|-------|------|
| 1.5 | סיווג קידוחים (enum, conflicts) | WARN | `BOREHOLE_CLASSIFICATION_GLOSSARY.md` |
| 2 | Structured Data Pack (6 CSVs) | FAIL | `DATA_PIPELINE_SPEC.md` |
| 3 | Prompt Layer (staleness, placeholders) | FAIL | `ZONE_REPORT_PROCESS_GUIDE.md §IV` |
| 4 | Zone Diagnosis (8 נושאים, PFAS כפער) | FAIL | PROCESS_GUIDE §II.5 |
| 5 | V5 Report (מינוח, מבנה, רמות-ודאות) | FAIL | `STYLE_GUIDE §B.5` + `REPORT_V5_SCHEMA.md` |
| 6 | HTML/Word (RTL, figures, ספים יחסיים) | FAIL | thresholds יחסיים-לאזור |
| 8 | Exec Summaries (anonymization, brief↔report sha) | FAIL | `report-engine/schemas/` |

---

## הנכסים הכי שווי-קידום (המלצה)

1. **Governance starter-kit** ⭐⭐⭐ — צירוף 2.1–2.4 (SSOT-enforcement + provenance-gates + audit-trail + footgun-register) הוא **תבנית governance שלמה** לכל פרויקט data-heavy רב-סשן. ראוי למסמך-תבנית עצמאי.
2. **signalkit + trend-detective** ⭐⭐⭐ — בשלים לייצוא מיידי; בלתי-תלויי-דומיין.
3. **הפרדה דטרמיניסטי/גנרטיבי** (2.7) — העיקרון הארכיטקטוני שמאפשר את כל השאר.

---

## מה ספציפי-לדומיין (לא בר-שכפול-ישיר)

- ספי severity (תקן 2021), decay chains הידרוקרבונים+מתכות, מינוח עברי-RTL, קואורדינטות ITM, מילון פרמטרים. **ניתנים להרחבה** דרך config, אך דורשים התאמת-דומיין.
- סקריפטי `generate_holon_*` — Holon-specific (legacy); `--zone` חלקי. דורשים refactor לשימוש חוזר.

---

**עודכן**: 2026-06-21 · נגזר מסקירת-עומק (3 סוכני Explore) · ראה `DOCS_MAP.md` לטופולוגיית התיעוד המלאה.
