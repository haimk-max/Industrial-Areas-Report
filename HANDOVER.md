# HANDOVER.md — זיכרון בין-סשן

קובץ זה מתוחזק על-ידי הסקיל `/handover`. הוא מתעדכן **רק** כאשר סשן מייצר משהו שהסשן הבא צריך לדעת — אילוץ, footgun חוזר, החלטה שמגבילה עבודה עתידית.

**אסור לרשום כאן**: פעולות שגרתיות, התקדמות יומית, או מה שנלכד כבר בהודעות commit.

---

## אילוצי סביבה (Environment Constraints)

- המשתמש עובד **אך ורק** דרך Claude Code on the web (GitHub integration) — **אין גישה לטרמינל**.
- `~/.claude/` לא שורד בין סשנים (container חולף). כל דבר שצריך להישמר חייב להיות committed לריפו.
- הסקיל `/handover` מותקן ב-`.claude/skills/handover/SKILL.md` (בריפו, לא גלובלי) — זה מה שגורם לו לשרוד.
- קובץ זה (`HANDOVER.md`) הוא תחליף ל-`~/.claude/CLAUDE.md` שאינו שורד.

---

## החלטות מגבילות (Load-bearing Decisions)

- **§IV = SSOT יחיד לסדר** (REQ #24, 788e8c7): §3 = מוקדים גיאוגרפיים (חומרה יורדת); משפחות משניות בתוך מוקד; "פערי כיסוי" אחרון. FUEL "תמיד אחרון" — בוטל. כל שינוי עתידי לכלל הסדר  — §IV בלבד.
- **focus_order ארטיפקט חובה**: zone_diagnosis.md חייב לכלול `## סדר מוקדים` (טבלה פַּרסְבִיל). Gate 4 מאמת. הדיאגנוזה הנוכחית של חולון כוללת אותו (מאז V6).

## footguns חוזרים

- **פער staleness דיאגנוזה —דוח** (זוהה 2026-06-10, **תוקן 2026-06-14 — REQ #31.5**): `render_zone_prompt.py` חותם כעת `diagnosis_sha256_12` בשלב report, ו-Gate 3 מאמת אותו מול zone_diagnosis.md החי  — snapshot מיושן של `{FOCUS_ORDER_LIST}` = FAIL. עדיין יש משמעת מוסכמה (חובה לרנדר מחדש אחרי Step 4), אך כעת היא **נאכפת** ולא רק מתועדת.
- **פער staleness דוח —דוחות-ניהוליים** (זוהה 2026-06-10): הדוחות הניהוליים (INTERNAL+PUBLIC exec summaries) נוצרים מ-brief YAML שנגזר מהדוח הראשי, אך **אין חוזה טריות** שמקשר ביניהם. ה-brief נושא כעת `source_report_version` + `source_report_sha` (REQ #29); `run_pipeline.sh --stage exec-summary` מזהיר אם ה-sha לא תואם את הדוח הנוכחי. **אם מעדכנים את הדוח הראשי — חובה לחדש את הדוחות הניהוליים** (אחרת מפיצים תוכן ישן תחת גרסה חדשה).
- **`Holon/02_data/` הוא ה-Data Pack הקנוני — לא למחוק** (זוהה 2026-06-10 אחרי שנמחק בטעות ב-REQ#28 ושוחזר): `02_data/` (7 CSVs per DATA_PIPELINE_SPEC) נקרא ע"י **Gate 2** ו-`generate_zone_brief.py`. הוא **שונה** מ-`lean_workspace/` (בסיס-ראיות V4 שה-designed HTML generators קוראים). שניהם פעילים במקביל. אל תתבלבל ביניהם ואל תמחק `02_data/` כ"כפילות".
- **LibreOffice <bdi>HTML→docx</bdi> שבור ב-container** (זוהה 2026-06-10): `libreoffice --headless --convert-to docx` כושל על **כל** קלט (אפילו plain text) עם "source file could not be loaded". לא ניתן לתיקון בסביבה הנוכחית. **חלופות**: Python `markdown-to-docx` + `embed_holon_figures_v5.py` (עובד, ללא CSS); או המשתמש ממיר <bdi>HTML→Word</bdi> ידנית (browser copy-paste → Word — **האפשרות המומלצת** לאיכות גבוהה; גם Word <bdi>File→Open</bdi> HTML, Google Docs import, LibreOffice מקומי).
- **`generate_zone_html_from_brief.py` מחליף רק חלק מהסעיפים** (זוהה 2026-06-14, **תוקן — REQ #31.1**): שוכתב עם `replace_container_inner()` (depth-counting של divs מקוננים) — כל סעיפי ה-brief נצרכים כעת (כולל `stats_public`/`means_summary`/`methodology`/`timeline`). אזור שני כבר לא חסום. design-system/reference נשאר קפוא (לא נגע). 13 טסטים ב-`tests/test_brief_html_generator.py`.
- **דליפת שמות מתקנים ב-PUBLIC** (זוהה ותוקן 2026-06-14, **כעת נאכף — REQ #31.3**): "רימטל" הוחלף ב-"אתר מחזור מתכות משוקם". **Gate 8** (`qa_pipeline.py --gate 8`) סורק כעת את PUBLIC מול `sources[].name_internal` — דליפת שם-מתקן = FAIL; שם-קידוח אמיתי = WARN. מריצים אחרי כל יצירת dוחות ניהוליים.
- **חוזה brief↔report** (**REQ #31.2**): ה-brief חייב לשאת `# source_report_sha256_12:` machine-readable (לא רק בפרוזה). Gate 8 = FAIL אם חסר/לא תואם דוח אחרון. holon.yaml תוקן (היה רק בפרוזה).
- **ספירת קידוחים בדוח חייבת להיגזר מ-`selected_boreholes.json` + `02_data/zone_wells.csv`** (זוהה ותוקן 2026-06-16, REQ #34): דוח חולון V8 הצהיר "46 ניטור כללי + 63 דלק = 111" (46+63=109 — שגיאת חשבון, ושני הנתונים שגויים). אמת-קרקע: `selected_boreholes.json` n=111; `zone_wells.csv` well_type = 40 industrial + 64 fuel + 6 monitoring + 2 private_production (אחד מחוץ לפוליגון). הפילוח הנכון: **47 לא-דלק + 64 דלק = 111**. **כלל**: כל מספר בדוח (קידוחים, מדידות, פילוח) חייב להיגזר מקבצי הנתונים ולא להיכתב ידנית; Gate 2 כבר מאשר "111 — עקבי" אך **אינו** בודק פילוח-משנה בפרוזה. כששינית את הדוח — חדש `source_report_sha256_12` ב-brief (אחרת Gate 8 FAIL) וצור מחדש V8.html + exec summaries.
- **Gate 3 (Prompt Layer) מיושן אחרי שינוי template** (זוהה 2026-06-16): שינוי `scripts/templates/zone_report_prompt_template_v5.md` (כמו ב-REQ #32, 5-fig) משנה את `template_sha`, אבל הפרומפט המרונדר (`Holon/context_pack/05_prompt/zone_report_prompt.md`) שומר חותמת ישנה → Gate 3 FAIL. **תיקון נקי**: `bash scripts/run_pipeline.sh --stage prompts` (או `render_zone_prompt.py --step report`) — אך זה משכתב את הפרומפט מהתבנית, ויאבד תיקוני-RTL ידניים שהוחלו ישירות על הפרומפט המרונדר. ודא שהתבנית עצמה נושאת את תיקוני ה-RTL לפני רינדור-מחדש.
- **`--zone holon` (lowercase) שובר חלק מהשערים** (זוהה 2026-06-16): Gate 8 בונה נתיב `REPO_ROOT/zone/output` — ב-Linux case-sensitive, `holon/output` ≠ `Holon/output` → "דוח לא נמצא" (WARN שקרי). **הרץ qa_pipeline עם `--zone Holon`** (capitalized = שם הספרייה) כדי לאמת באמת.
- **חצים בקובצי HTML עבריים (RTL) מתהפכים** (זוהה 2026-06-15): ` —` בתוך טקסט עברי RTL מוצג הפוך חזותית. תיקון משולש: (1) כינויים טכניים כולם-אנגלי (`<bdi>diagnosis → prompt</bdi>`) — עטוף ב-`<bdi>` לאלץ LTR; (2) `<pre>` — חובה `direction:ltr; unicode-bidi:isolate`; (3) חצי-תוצאה בפסקה עברית — `←` או em-dash (—) במקום `→`. כל HTML עברי עתידי: בדוק `grep -n "→"` ואמת שאין `→` חשוף מחוץ ל-`<bdi>`/`<pre>`.

---

## סטטוס סיום סשן (2026-06-18)

**Production Risk Q&A Agent — Side Project**
- ✅ ענף `claude/production-risk-qa-agent` נוצר ונדחף (שונה שם מ-`claude/create-base-report-directory-5DqAR`)
- ✅ כל 6 commits הם בלעדית Q&A Agent — אין ערבוב עם פרויקט ראשי
- ✅ Layer 0 Discipline הוסף ל-SYSTEM_PROMPT.md (3ef0eb8, 01931d2)
- ⏳ REQ #35 — In Progress: מק חולון 12/14 classification issue פתוחה (forensics_brief "הפקה" מול zone_wells "monitoring")
- ⚠️ ענף `claude/create-base-report-directory-5DqAR` stale ב-remote — מחק דרך GitHub UI

**סטטוס פרויקט ראשי (מ-2026-06-16 — ללא שינוי)**
- ✅ PR #23 (REQ #34 + DOCS_MAP) merged to main
- ⏳ Hydrogeologist review של Holon V8 + Raanana V5 (שלב הבא)

## עבודה בתהליך (In flight)

- **REQ #28 COMPLETE** (ba51451): גנריזציית מחוללי-HTML הושלמה.
- **REQ #29 COMPLETE** (63b3ad2): תשתית דוחות ניהוליים + RAG דחייה + סנכרון.
- **REQ #30 — V8 exec-summaries COMPLETE** (2026-06-14): brief עודכן מ-V5-era ל-V8 (9 ממצאים כולל 3 מוקדי דלק, 16 קידוחים, 7 מקורות); INTERNAL+PUBLIC HTMLs נוצרו (65KB+52KB); דליפת "רימטל" ב-PUBLIC reference תוקנה; generator limitation documented.
- **REQ #32 — Figure Alignment + RTL COMPLETE** (233f2d0, 168218a, 2026-06-16):
  - **Figure captions aligned**: Updated V5 prompt template to mandate 5 figures (not 6); rewrote V8.md captions (איור 2–5) to match rendered output; V8.html regenerated with injected figures.
  - **RTL arrow fixes — scoped to report deliverables**: Created `scripts/fix_rtl_arrows.py` (reusable). Initially applied to 88 files (3bbfd9f) but **narrowed** (168218a) to report deliverables only (Holon V4–V8 + exec summaries, Raanana reports + drilling cards, report-engine outputs) — em-dash degrades clarity in spec files ("ND → NULL" = "maps to"). **Footgun**: tool default still scans whole repo; future runs should target `*/output/*` only.
- **REQ #33 — Branch consolidation COMPLETE** (d69d9e4, 0341772, 2026-06-16):
  - **Toolkit move**: `docs/GENERIC_PDF_EXTRACTION_AND_RETRIEVAL.md` → `toolkit/playbooks/generic_pdf_extraction_and_retrieval.md` (refs updated in PDF_QA_INFRASTRUCTURE.md/.html).
  - **Merged `claude/raanana-v5-pipeline`** into the main working branch (42 files, +9,580 lines): **Raanana is now the 2nd zone through V5 end-to-end** (RAANANA_REPORT_V5.md/.html + full context_pack + 6 CSVs + build_zone_lean_workspace.py). RAANANA_REPORT_V5 awaits hydrogeologist review.
  - **qa_pipeline.py Gate 6** is now **zone-relative** (map circle threshold = wells×0.8, min 3) — critical for small zones (Raanana 7 wells); merged cleanly alongside Gate 8.
  - **Single branch now**: `claude/raanana-v5-pipeline` local+worktree deleted; **remote still stale** (git proxy rejects branch deletion — delete via GitHub UI).
