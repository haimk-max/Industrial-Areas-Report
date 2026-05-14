# PROCESS.md — Active Requirements Tracking

> **מטרה**: SSOT לדרישות פתוחות וסגורות. עודכן בכל שינוי.
> **כלל**: ראה CLAUDE.md §12.

**עודכן אחרון**: 2026-05-14 (שלב 4 + 10: simplify + md_utils refactor)

---

## דרישות פתוחות (Open)

| # | בעיה | תיאור | סטטוס | תאריך פתיחה | קבצים |
|---|------|--------|--------|----------------|--------|
| 7 | Skills/אוטומציה לתהליכים חוזרים | אימוץ simplify (קוד כפול), init (regen CLAUDE.md), review (PR) | ⏳ Deferred | 2026-05-14 | אחרי בעיות 2–4 |
| 11 | HIGH-priority simplify fixes (regexes + data loader) | pre-compile 8 module-level regexes (hot-path optimization), extract load_all_core_data() לdata_loader.py | ⏳ Deferred | 2026-05-14 | scripts/generate_holon_*.py, data_loader.py |

---

## דרישות סגורות (Closed) — Audit Trail

| # | בעיה | תאריך סגירה | commit | אימות |
|---|------|---------------|--------|----------|
| 1 | SSOT terminology מפוזר | 2026-05-14 | 2b6e775 | PROCESS_GUIDE §III טבלה קנונית; METHODOLOGY.md redirect header |
| 5a | CLAUDE.md אינדקס אזורים | 2026-05-14 | 2b6e775 | CLAUDE.md שורה 12-22 — Zone Status Index |
| 6 | ערבוב Raanana/Holon | 2026-05-14 | 2b6e775 | CLAUDE.md Zone Status Index מפריד בין השניים |
| 8 | חיפוש מקורות זיהום (תיעוד) | 2026-05-14 | 2b6e775 | PROCESS_GUIDE §I.5 — 6 web channels + queries |
| 9 | PDF ingestion (תיעוד) | 2026-05-14 | 2b6e775 | PROCESS_GUIDE §I.2 — External Data/{zone}/ structure |
| H1 | Session-start-hook | 2026-05-14 | 7aa031d, d8e3d15 | `.claude/hooks/session-start.sh` + settings.json; CLAUDE_CODE_REMOTE guard |
| H2 | HOLON_REPORT_V4.html regenerated | 2026-05-14 | fea643c | `generate_holon_full_html.py` rerun; 180KB; figure injection safety net |
| H3 | Requirements tracking infrastructure | 2026-05-14 | 5744f8f | `PROCESS.md` SSOT + CLAUDE.md §12 rule + session-start.sh auto-display |
| 2 | סדר פייפליין הפוך (boreholes_override) | 2026-05-14 | pre-existing | `svg_charts.py:343,388,441` — 3 panel functions accept `boreholes_override`; `data_loader.py:126` — `extract_report_boreholes()` defined |
| 3 | HTML generators README | 2026-05-14 | pre-existing | `scripts/report_designed/README.md` — תיעוד מלא בעברית של 2 generators, pipeline order, API, RTL |
| 4 | תבנית פרומפט generic | 2026-05-14 | pre-existing | `scripts/templates/zone_report_prompt_template.md` — 31 placeholders, 49 XML tags, Anthropic structure |
| 5b | CLAUDE.md Phase H docs מלאים | 2026-05-14 | pre-existing | CLAUDE.md §4 שורות 109-121 — scripts, outputs, lean_workspace, severity, generators, safety net, SSOT, family ordering, web search |
| Fig | Figure numbering bug + empty figures 2, 6 | 2026-05-14 | b9f28b6, a822495 | הסרת `<span class='ttl'>איור N</span>` duplicate; הוספת `.ledger` CSS ל-full HTML; הסרת fig_02_severity_matrix phantom |
| R3 | "MD בעברית, קוד באנגלית" | 2026-05-14 | a822495 | CLAUDE.md §1 Language Rules — 5 כללים מפורשים |
| R2 | V4.md §3 מתודולוגיה ארוכה | 2026-05-14 | pending | Opus agent קיצץ מ-59 שורות (§3.1-§3.7) ל-7 שורות (פסקה אחת); הפניה ל-PROCESS_GUIDE §III |
| R1 | V4.md §4.1-§4.4 פירוט per-borehole | 2026-05-14 | pending | Opus agent: §4.1 9→0 bullets, §4.2 9→0, §4.3 4→0, §4.4 13→3 (רק חתימות פורנזיות); כל forensics + facility attributions נשמרו כפסקאות זרימה |
| R4 | איור 2 (severity_matrix) — החזר | 2026-05-14 | 0fe1cfa + 1fcb2f4 | הוספת image markdown ב-V4.md §3, הוספת `fig_02_severity_matrix` ל-figure_svgs dict ב-generate_holon_full_html.py, regenerate HTML (174KB); 7 figures עכשיו |
| Z1 | /scout — מחוק (לא רלוונטי) | 2026-05-14 | 0fe1cfa | משתמש ביקש למחוק בקשה זו; אין מטרה ברורה, דרישה סגורה |
| 10 | (שלב 10) Simplify: קוד reuse + refactor | 2026-05-14 | 1628510 + 91cf5ad | בוצע שלב 4 (boreholes_override כבר pre-existing) + שלב 10 (simplify skill). סיכום: extracted md_utils.py (120 שורות), הסר dead fig_counter, fixed import direction (generators לא יובאים זה מזה). ~75 שורות duplicate code חוסלו |

---

## הסבר ושימוש

### עבור Claude (קוד / agent)
1. **בתחילת כל סשן**: `cat PROCESS.md` (אוטומטי דרך session-start hook).
2. **לפני start על משימה**: ודא שיש שורה ב-Open table; אם לא — הוסף.
3. **בסיום משימה**: העבר שורה מ-Open ל-Closed עם commit hash + אימות.
4. **commit message**: ציין `[PROCESS.md] closed #2` או `[PROCESS.md] added #10`.

### עבור המשתמש (review)
- **רואה בדיוק מה פתוח**: טבלת Open.
- **רואה היסטוריה**: טבלת Closed עם commits.
- **יכול לבדוק**: כל פתרון יש לו commit + שיטת אימות.

---

## פורמט שורות

```markdown
| {מספר} | {שם קצר} | {תיאור משימה} | {סטטוס} | {תאריך} | {קבצים} |
```

**סטטוסים**:
- ❌ Open — לא התחיל
- 🔄 In Progress — בעבודה
- ⚠️ Partial — חלקי (יש sub-tasks)
- ⏳ Deferred — מתוכנן ל-Phase מאוחר יותר
- ✅ Closed — הושלם (בטבלת Closed)

---

**אכיפה**: CLAUDE.md §12 (Requirements Tracking).
