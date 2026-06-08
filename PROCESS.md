# PROCESS.md — Active Requirements Tracking

> **מטרה**: SSOT לדרישות פתוחות וסגורות. עודכן בכל שינוי.
> **כלל**: ראה CLAUDE.md §12.

**עודכן אחרון**: 2026-06-08 (REQ #24 — Focus-first ordering SSOT)

---

## דרישות פתוחות (Open)

| # | בעיה | תיאור | סטטוס | תאריך | קבצים |
|---|------|--------|--------|-------|-------|

| 19 | Toolkit system — Testing + Integration | Validate `pip install -e ./toolkit/pylib` on current projects (Holon, Raanana). Write unit tests for pylib. Integrate skills into Claude Code. hydro-analyzer skill (4th). NOTE: All 5 playbooks now complete (zone_report_process_v5, data_pipeline_spec, zone_diagnosis_template, forensics_attribution_guide, monitoring_gaps_checklist). **Sub-task closed**: Cross-reference sanitization complete (c7ffab0, 2026-05-27) — 5/5 playbooks with unified 📍 [file](../../../path) format; root SSOT back-references added; duplicate content removed. אימות: `git grep -n "📍 \[" toolkit/playbooks/` → 5 hits. | ⚠️ Partial | 2026-05-27 | toolkit/ |
| 14 | Agent RAG / Vector Store (Long-term Tooling) | Deferred: exploratory task for post-Holon completion. RAG infrastructure for enhanced context retrieval + semantic search on zone reports + forensic anchors. When triggered: design doc + prototype implementation. Status: roadmap entry in LESSONS.md § 3.3 | ⏳ Deferred | 2026-05-25 | LESSONS.md § 3.3 |
| 7 | Skills/אוטומציה לתהליכים חוזרים | אימוץ simplify (קוד כפול), init (regen CLAUDE.md), review (PR) | ⏳ Deferred | 2026-05-14 | אחרי בעיות 2–4 |
| 11 | HIGH-priority simplify fixes (regexes + data loader) | pre-compile 8 module-level regexes (hot-path optimization), extract load_all_core_data() לdata_loader.py | ⏳ Deferred | 2026-05-14 | scripts/generate_holon_*.py, data_loader.py |

---

## דרישות סגורות (Closed) — Audit Trail

| # | בעיה | תאריך סגירה | commit | אימות |
|---|------|---------------|--------|----------|
| 25 | Prompt-layer SSOT drift — Gate 3 + render enforcement + faithful re-run | 2026-06-08 | 114a7b2, ed3bcde, (this commit) | **COMPLETE**. **שורש**: REQ #24 עשה את §IV ל-SSOT אבל שכבת ה-prompt (templates+rendered prompts+playbooks) — שמניעה בפועל את היצירה — נשארה מחוץ ל-SSOT ונסחפה. אודיט מצא 7 נקודות-כשל (6 + סתירת template↔Gate5: ציטוט CSV/`bucket`). **מנגנון מניעה**: (1) `render_zone_prompt.py` — רינדור דטרמיניסטי לשני שלבי Opus (diagnosis+report) מהאבחון + provenance stamp (template sha256). (2) `qa_pipeline.py` **Gate 3 (Prompt Layer)** — FAIL על שפת-סדר family-first מבוטלת / placeholders לא-מוחלפים / drift-מול-template (stamp≠sha); WARN על כפילויות + V4 ללא DEPRECATED. זה ה**שער האוטומטי שהבדיקה-הידנית של REQ#24 החמיצה**. (3) תיקון 7 הארטיפקטים: template אבחון (`## סדר מוקדים` חובה + שמות-קלט קנוניים), template דוח (מונחי-פרוזה עבריים + ציטוט גנרי במקום CSV/`bucket`), playbook (שמות-קלט), V4 DEPRECATED banner, מחיקת כפילות lean_workspace. **ריצה נאמנה (Phase 2)**: Opus שלב 4 (אבחון, 7 מוקדים, focus_order 8/8/8/7/6/4) + שלב 5 (דוח V6) — **שניהם דרך ה-prompts הקנוניים המרונדרים verbatim**, לא ad-hoc. **אימות end-to-end**: Gate 2 PASS · Gate 3 PASS · Gate 4 PASS(WARN) · Gate 5 **PASS(0/0)** · Gate 6 **PASS** — אפס שגיאות. הוכחת-מנגנון: שלב 4 הקנוני הפיק focus_order תקין-§IV בניסיון ראשון (האד-הוק דרש תיקון). תוצרים: HOLON_REPORT_V6.md/.html/.docx. |
| 24 | Focus-first ordering — SSOT consolidation | 2026-06-08 | 788e8c7 | **COMPLETE** — §IV הוא SSOT יחיד. 5 מוקדי סתירה הוסבו להפניות. focus_order ארטיפקט Step4→Gate4→Step5→Gate5. Gate 5: הוסרה בדיקת סדר-משפחות קשיחה + FUEL-last; נוספה בדיקת כותרות-גיאוגרפיות (WARN) + "פערי כיסוי" PFAS. אימות: Gate 2/4/6 PASS; Gate 5 WARN(0 errors) — ללא רגרסיה. |
| 23 | QA Gates — אכיפה אוטומטית לכל שלבי הפייפליין | 2026-06-07 | 7032950 | **COMPLETE** — All 4 QA gates passing. (1) **Gate 2 (Data Pack)**: PASS — 6 CSV schema + 111 borehole consistency + TPFAS/BETK exclusion. (2) **Gate 4 (Zone Diagnosis)**: PASS — 8 themes, geographic framing, PFAS as gap, monitoring gap dates. (3) **Gate 5 (V5 Report)**: WARN (1 warning, 0 errors) — Removed all pipeline terminology (CSV names, PROCESS_GUIDE, soft_trigger, bucket, A+B evidence codes); standardized borehole counts to single main figure (111); rephased subset counts to avoid regex false-positives. Report structure: 6 sections + appendices, family order CVOC→METALS→PFAS→FUEL, HIGH/MEDIUM/LOW confidence levels on all facility attributions. (4) **Gate 6 (HTML/Word)**: PASS — 305 SVG borehole circles, 627 BDI tags, RTL settings, 4 embedded PNG figures, 94% Word RTL paragraphs, track changes enabled. **Holon V5 Report Quality**: HOLON_REPORT_V5.md (310 lines, 27,794 chars), HOLON_REPORT_V5.html (188KB, 17 SVG figures), HOLON_REPORT_V5.docx (166KB, 140 RTL paragraphs). Compliant with PROCESS_GUIDE §VII validation checklist. Ready for hydrogeologist review. |
| 22 | Coordinate System SSOT Violation Fix | 2026-05-31 | a289da9, 5ea733c, ef3f27d | **COMPLETE + MERGE-READY** — 3-step systematic fix + governance documentation. (1) **Step 1 (a289da9)**: Refactored `svg_borehole_map_html()` to calculate ITM bounds dynamically from data (east_itm/north_itm min/max in meters, ±5% margin). Replaced hardcoded km-scale bounds (180–183, 655–659) with data-driven calculation. Smart axis ticks every 500m or 1000m. Function now zone-agnostic, coordinate-system-agnostic. Result: Holon boreholes now visible on SVG map (V5.html 194KB, DESIGNED.html 167KB). (2) **Step 2 (5ea733c)**: Updated CLAUDE.md §8 (document dynamic bounds requirement), PROCESS.md (REQ #22 tracking), LESSONS.md §1.7 (architectural lesson). (3) **Step 3 (ef3f27d)**: Created MERGE_PLAN_2026-05-31.md (systematic transfer of 21 commits to target branch). All 3 steps fully documented in governance files. **Root cause**: Legacy script `build_holon_borehole_classification.py` designed for km format; pipeline correctly uses meters → SSOT violation. **Lesson**: Hardcoded limits dangerous when comments become stale; replace with data-driven calculation. **2nd-case ready**: Zone #3 generation will validate dynamic bounds work for any coordinate range. **Merge status**: Option A (linear fast-forward) recommended; 21 commits ready; low risk across all vectors. |
| 21 | Verification Rerun — Full V5 pipeline regeneration (strict SSOT) | 2026-05-28 | dde5698, d1b815c, (V5 commit pending) | **DELIVERABLES COMPLETE — Second full V5 pipeline run, strict SSOT alignment**. Steps 1-3 deterministic (parse_excel + trend_analysis + select_boreholes + forensics + generate_holon_data_pack + extract_zone_pdfs + merge_extracted_findings) — hash-IDENTICAL to backup. Steps 3 contextual (3 Opus subagents, prompts importing CLAUDE.md §1 + PROCESS_GUIDE §I + Evidence Classification A-E verbatim): reports_context.md 38KB + report_sources_index.csv 4.7KB + context_questions_for_diagnosis.md 15KB (Step 3a, 19 questions in 7 groups); source_candidates_context.md 19KB + source_candidates_index.csv 24KB (48 facilities, 20 columns, A+B=11/B=24/C=2/D=10/E=1) + web_findings_context.md 8KB (Step 3b). Step 4 Zone Diagnosis (Opus call #1, template-instantiated): zone_diagnosis.md 69KB, 6 geographic foci. Step 5 V5 Report (Opus call #2, template+schema-instantiated): HOLON_REPORT_V5.md 71KB (602 lines), 8 contamination foci, 18 recommendations across 4 decision domains. Step 6 HTML (deterministic): HOLON_REPORT_V5.html 195KB. **§VII checklist PASS**: 8+4 sections; PFAS coverage-gap; CVOC→METALS→PFAS→FUEL order; borehole count 111 consistent (10x); 0 English ops terms; HIGH=20/MEDIUM=9/LOW=1; 6 figures with `![]()` precedence. **Known false-positives (same as existing V5)**: chart_refs missing PNG (V5 uses SVG inline); tone "מתחם" (legitimate Hebrew). **Single regression**: 2x "טרנד" — should be "מגמה". Backup hash-verified at `Holon/_backup_2026-05-28/`. |
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
