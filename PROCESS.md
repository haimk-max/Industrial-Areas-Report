# PROCESS.md — Active Requirements Tracking

> **מטרה**: SSOT לדרישות פתוחות וסגורות. עודכן בכל שינוי.
> **כלל**: ראה CLAUDE.md §12.

**עודכן אחרון**: 2026-05-28 (REQ #20 closed — PR #19 merged to main via a19a917; Phase H+ Implementation complete)

---

## דרישות פתוחות (Open)

| # | בעיה | תיאור | סטטוס | תאריך פתיחה | קבצים |
|---|------|--------|--------|----------------|--------|
| 19 | Toolkit system — Testing + Integration | Validate `pip install -e ./toolkit/pylib` on current projects (Holon, Raanana). Write unit tests for pylib. Integrate skills into Claude Code. hydro-analyzer skill (4th). NOTE: All 5 playbooks now complete (zone_report_process_v5, data_pipeline_spec, zone_diagnosis_template, forensics_attribution_guide, monitoring_gaps_checklist). **Sub-task closed**: Cross-reference sanitization complete (c7ffab0, 2026-05-27) — 5/5 playbooks with unified 📍 [file](../../../path) format; root SSOT back-references added; duplicate content removed. אימות: `git grep -n "📍 \[" toolkit/playbooks/` → 5 hits. | ⚠️ Partial | 2026-05-27 | toolkit/ |
| 14 | Agent RAG / Vector Store (Long-term Tooling) | Deferred: exploratory task for post-Holon completion. RAG infrastructure for enhanced context retrieval + semantic search on zone reports + forensic anchors. When triggered: design doc + prototype implementation. Status: roadmap entry in LESSONS.md § 3.3 | ⏳ Deferred | 2026-05-25 | LESSONS.md § 3.3 |
| 7 | Skills/אוטומציה לתהליכים חוזרים | אימוץ simplify (קוד כפול), init (regen CLAUDE.md), review (PR) | ⏳ Deferred | 2026-05-14 | אחרי בעיות 2–4 |
| 11 | HIGH-priority simplify fixes (regexes + data loader) | pre-compile 8 module-level regexes (hot-path optimization), extract load_all_core_data() לdata_loader.py | ⏳ Deferred | 2026-05-14 | scripts/generate_holon_*.py, data_loader.py |

---

## דרישות סגורות (Closed) — Audit Trail

| # | בעיה | תאריך סגירה | commit | אימות |
|---|------|---------------|--------|----------|
| 20 | PR #19 Merge + branch cleanup | 2026-05-28 | a19a917 | ✅ PR #19 merged to main (52 commits, 76 files, +61,116 / -47 lines). Phase H+ Implementation complete: REQ #13–18 all closed; REQ #19 sanitization sub-task in main. ⚠️ Branch cleanup pending: `git push origin --delete toolkit-release` failed with HTTP 403 in current env — user to delete via GitHub UI. PR #17 (toolkit-release) closed as obsolete. |
| 18 | ENGINE: Brief → Twin HTML generator | 2026-05-26 | 357751c | **COMPLETE**: `scripts/generate_zone_html_from_brief.py` reads brief YAML + clones frozen reference templates + data-replaces per field-mappings (CLAUDE.md §5) → two self-contained HTML files. Holon verified: 64KB INTERNAL (real names, decision matrix) + 52KB PUBLIC (generic only, no decisions). All sections injected: KPI grid, family ledger, 7 findings w/ dual framing, decisions table, metadata. Design system preserved (CSS vars, fonts, RTL, Leaflet). **Final proof**: entire pipeline V5.md → brief.yaml → HTML operational. Zone-agnostic. |
| 17 | ENGINE: Full Report → Brief YAML generator | 2026-05-26 | (multiple) | **COMPLETE**: `scripts/generate_zone_brief.py` (two-stage: prepare + finalize) + zone_brief_prompt_template.md (Opus input). Holon verified: prepare assembles 112-well ITM→WGS84 lookup + prompt; Opus produces 7 findings w/ dual framing + 11 boreholes + 4 sources + 4 decision-cats; finalize validates schema + injects coords textually (preserves format/comments) + flags leaks. **Critical fix**: מק חולון 14 coords corrected to [32.01068, 34.7899] (vs. Claude Design error). Edge case: רימטל facility not in wells → warning + [0,0]. |
| 16 | ENGINE: Exec-Summary Engine (report-engine/) | 2026-05-26 | (multiple) | **ORGANIZED**: 14-file generic engine under `report-engine/` (not zone-specific). (1) CLAUDE.md (operating manual, field-mappings, quality-bar). (2) design-system/ FROZEN: tokens.css, architecture.md, typography.md, color.md, voice.md, reference/ (gold-standard HTML). (3) schemas/zone-brief.schema.json (validation). (4) briefs/holon.yaml (per-zone data). Data-only distinction: per-zone data in briefs/<zone>.yaml; design + schema constant across 18 zones. Generators (brief + HTML) complete pipeline. |
| 15 | Executive Summary HTML Deliverables (Internal + Public) | 2026-05-26 | 1426659 (HTML), 0e31665 (YAML spec) | **DELIVERABLES COMPLETE**: (1) **HOLON_EXECUTIVE_SUMMARY_INTERNAL.html** (1,698 lines) — Real facility names + confidence (HIGH/MEDIUM/LOW), full technical depth (µg/L, % standard, z-values), **4-category decision matrix** (4 decision domains × actions × what's needed), 7 color-coded findings (🔴 critical / 🟠 high / 🟢 positive), KPI cards, framing warning. (2) **HOLON_EXECUTIVE_SUMMARY_PUBLIC.html** (1,323 lines) — Generic source attribution only (0 real facility names), simplified technical depth, **NO decision matrix**, 7 findings in public framing, timeline narrative, heat map, transparency callouts. (3) **Design Spec (YAML)** — HOLON_EXEC_SUMMARY_DESIGN_SPEC.yaml (473 lines) — Self-contained, tool-friendly spec covering audiences, design tokens (colors/fonts/RTL), KPIs, 7 findings (dual framing), decision matrix structure, source attribution mapping, page layout specs, validation checklist. **Verification**: Internal 17 real names ✓, Public 0 real names ✓, Internal matrix ✓, Public no matrix ✓, RTL HTML/CSS/SVG only ✓, Print-ready A4 ✓. Ready for distribution. |
| 13 | Hybrid V5 Pipeline Implementation + REQ #13.6 Holon V5 Report (FINAL) | 2026-05-26 | 69b9f41, 02882c3 | **13.1–13.5** ✓ + **13.6 FINAL** ✅ **METHODOLOGY CORRECTIONS & VALIDATION COMPLETE**: (1) **Option B Family Filtering**: generate_holon_data_pack.py excludes "OTHER" family from all 7 CSVs → measurements_scoped 20,613→15,173 rows, trends cleaned, severity_by_well_family 191 rows (CVOC/METALS/PFAS/FUEL only). (2) **Graph Bug Fix**: svg_charts.py INDUSTRY→CVOC (15 occurrences) — critical refactor completed, regenerated V5.html with corrected graphs. (3) **Hebrew-Only Enforcement (CLAUDE.md §1)**: zone_report_prompt.md strengthened with explicit rules (ALERT→חרום, WATCH→אזהרה, etc.); Opus validated 0 English ops terms. (4) **Data Corrections**: Borehole count 112→111 (identified duplicate wells נד אגד אזור 7/איזור 7 with identical ITM coords); CVOC bucket-8 corrected 30→18; PFAS properly flagged "אי-בחינה". (5) **Final V5.md**: 310 שורות, 6 sections + methodology + limitations + 4 appendices; 27 boreholes in narrative; ✓ all figures with image markdown; ✓ severity_index matches CSV. (6) **V5.html**: 164KB, 12 sections, corrected graphs (CVOC references fixed). **Validation per §VII**: Structural PASS, data integrity PASS, methodology PASS, content PASS, technical/RTL PASS. Ready for hydrogeologist sign-off. |
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

## סיכום ההחלטה ב-28 במאי 2026 — PR #17 vs. feature/hybrid-v5-implementation

### בעיה שהופקה
PR #17 (toolkit-release) נפתח ב-2026-05-27 כענף נפרד להוצאת ה-toolkit לצוות, ללא churn של עבודת Holon V5. במקביל, ההמשך פותח על `feature/hybrid-v5-implementation` להשלמת REQ #13–19.

### ניתוח עומק (48 שעות אחרונות)
- **PR #17**: 20 קבצים (toolkit/), חסר PROCESS.md update + sanitization
- **feature/hybrid-v5-implementation**: 56+ commits, **47 קבצים נוספים** (data pack, context, diagnosis, V5 report, executives, engines, sanitization, PROCESS.md governance)

### החלטה
**סגור PR #17 כ-obsolete; יצור PR #19 מ-feature/hybrid-v5-implementation.**

**הנימוק**:
1. feature/hybrid-v5-implementation מכיל את כל הקבצים של PR #17 + עוד הרבה
2. Merging PR #17 לבדו ייצור סדר עבודה כפול (שני merges של אותם 20 קבצים)
3. feature/hybrid-v5-implementation כבר complete + validated + audit-trailed ב-PROCESS.md
4. PR #19 = מסלול מיזוג יחיד להשלמה; toolkit-release branch יימחק כחלק מ-REQ #20

**סטטוס**:
- ✅ PR #17 סגור עם הערה הפניה (comment added)
- ✅ PR #19 פתוחה (feature/hybrid-v5-implementation → main)
- ⚠️ toolkit-release branch — `git push origin --delete toolkit-release` נכשל עם HTTP 403 ב-environment הנוכחי; מחיקה תתבצע ע"י המשתמש דרך GitHub UI לאחר מיזוג PR #19
- 🔄 REQ #20: ממתין למיזוג PR #19 + מחיקת toolkit-release

---

**אכיפה**: CLAUDE.md §12 (Requirements Tracking).
