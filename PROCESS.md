# PROCESS.md — Active Requirements Tracking

> **מטרה**: SSOT לדרישות פתוחות וסגורות. עודכן בכל שינוי.
> **כלל**: ראה CLAUDE.md §12.

**עודכן אחרון**: 2026-05-28 (REQ #13–19 complete on feature/hybrid-v5-implementation branch; PR #19 created; superseded PR #17)

---

## דרישות פתוחות (Open)

| # | בעיה | תיאור | סטטוס | תאריך פתיחה | קבצים |
|---|------|--------|--------|----------------|--------|
| 20 | PR #19 Merge (REQ #13–19 to main) | מיזוג של feature/hybrid-v5-implementation ל-main — תוכן: REQ #13–19 (Holon V5 pipeline, toolkit, executives, governance) | ⏳ In Review | 2026-05-28 | feature/hybrid-v5-implementation @ c7ffab0 |
| 7 | Skills/אוטומציה לתהליכים חוזרים | אימוץ simplify (קוד כפול), init (regen CLAUDE.md), review (PR) | ⏳ Deferred | 2026-05-14 | אחרי בעיות 2–4 |
| 11 | HIGH-priority simplify fixes (regexes + data loader) | pre-compile 8 module-level regexes (hot-path optimization), extract load_all_core_data() לdata_loader.py | ⏳ Deferred | 2026-05-14 | scripts/generate_holon_*.py, data_loader.py |

---

## דרישות סגורות (Closed) — Audit Trail

| # | בעיה | תאריך סגירה | commit | אימות |
|---|------|---------------|--------|----------|
| 13.1-13.6 | Hybrid V5 Pipeline Implementation (REQ #13 sub-phases 1–6) | 2026-05-26 | 2aed15f, 69b9f41, 02882c3 | ✅ Data pack (7 CSVs), context pack, source candidates, zone diagnosis, V5 report, validation complete; Holon V5.md (310 שורות), HTML (164KB) ready for hydrogeologist review |
| 15 | Executive Summary Engine (INTERNAL + PUBLIC) | 2026-05-26 | 1426659, 0e31665 | ✅ HOLON_EXECUTIVE_SUMMARY_INTERNAL.html (1,698 lines, real names, decision matrix), PUBLIC.html (1,323 lines, generic), YAML design spec (473 lines), RTL/print-ready verified |
| 16 | Report Engine (Generic Architecture) | 2026-05-26 | (multiple) | ✅ 14-file report-engine/ (design system, schemas, per-zone briefs); zone-agnostic; DATA→BRIEF→HTML pipeline operational |
| 17 | Brief YAML Generator Engine | 2026-05-26 | (multiple) | ✅ generate_zone_brief.py (prepare + finalize), zone_brief_prompt_template.md, Holon pilot validated, coords textually injected |
| 18 | Twin HTML Generator Engine | 2026-05-26 | 357751c | ✅ generate_zone_html_from_brief.py, frozen reference templates, field-mappings per CLAUDE.md §5, Holon: 64KB INTERNAL + 52KB PUBLIC |
| 19 | Toolkit Sanitization (Back-references) | 2026-05-27 | c7ffab0 | ✅ 5/5 playbooks with unified reference format (📍 [file](../../../path)); root SSOT enhanced with back-references; duplicate content removed; no broken links |
| 12 | Hybrid V5 Pipeline Refactor — Documentation | 2026-05-17 | 6b8b023, dec12ad, 15d6d0e, 158110d, 8ef25c9, 80c6f7f | PROCESS_GUIDE §I refactor (Zone Context Pack), §II.5 (Zone Diagnosis), §VIII (7-step); DATA_PIPELINE_SPEC.md, REPORT_V5_SCHEMA.md; CLAUDE.md Phase H+ + governance update |
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

---

## סיכום ההחלטה בינואי 28, 2026 — PR #17 vs. feature/hybrid-v5-implementation

### בעיה שהופקה
PR #17 (toolkit-release) נפתח ב-2026-05-27 כציפיה של toolkit להמשך Phase. עם זאת, במקביל, work continued on `feature/hybrid-v5-implementation` לעיצום REQ #13-19.

### ניתוח עומק (48 שעות אחרונות)
- **PR #17**: 20 קבצים (toolkit/), חסר PROCESS.md update + sanitization
- **feature/hybrid-v5-implementation**: 56 commits, **47 קבצים נוספים** (data pack, context, diagnosis, V5 report, executives, engines, sanitization, PROCESS.md governance)

### החלטה מתקבלת
**סגור PR #17 כ-obsolete; יצור PR #19 מ-feature/hybrid-v5-implementation.**

**הנימוק**:
1. feature/hybrid-v5-implementation מכיל את כל הקבצים של PR #17 + עוד הרבה
2. Merging PR #17 לבדו יזיק לסדר (שני merges של אותם 20 קבצים)
3. feature/hybrid-v5-implementation כבר complete + validated + audit-trailed ב-PROCESS.md
4. PR #19 = מסלול יחיד לעיצום; toolkit-release branch יימחק

**סטטוס**:
- ✅ PR #17 סגור עם הערה; comment added
- ✅ PR #19 פתוחה (feature/hybrid-v5-implementation → main)
- 🔄 toolkit-release branch — pending delete (chmod issue; ignore)
- ⏳ REQ #20: Awaiting PR #19 merge

**אכיפה**: CLAUDE.md §12 (Requirements Tracking).
