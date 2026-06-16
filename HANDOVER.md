# HANDOVER.md — זיכרון בין-סשן

קובץ זה מתוחזק על-ידי הסקיל `/handover`. הוא מתעדכן **רק** כאשר סשן מייצר משהו שהסשן הבא צריך לדעת — אילוץ, footgun חוזר, החלטה שמגבילה עבודה עתידית.

**אסור לרשום כאן**: פעולות שגרתיות, התקדמות יומית, או מה שנלכד כבר בהודעות commit.

---

## אילוצי סביבה (Environment Constraints)

- המשתמש עובד **אך ורק** דרך Claude Code on the web (GitHub integration) — **אין גישה לטרמינל**.
- `~/.claude/` לא שורד בין סשנים (container חולף). כל דבר שצריך להישמר חייב להיות committed לריפו.
- הסקיל `/handover` מותקן ב-`.claude/skills/handover/SKILL.md` (בריפו, לא גלובלי) — זה מה שגורם לו לשרוד.

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
- **חצים בקובצי HTML עבריים (RTL) מתהפכים** (זוהה 2026-06-15): ` —` בתוך טקסט עברי RTL מוצג הפוך חזותית. תיקון משולש: (1) כינויים טכניים כולם-אנגלי (`<bdi>diagnosis → prompt</bdi>`) — עטוף ב-`<bdi>` לאלץ LTR; (2) `<pre>` — חובה `direction:ltr; unicode-bidi:isolate`; (3) חצי-תוצאה בפסקה עברית — `←` או em-dash (—) במקום `→`. כל HTML עברי עתידי: בדוק `grep -n "→"` ואמת שאין `→` חשוף מחוץ ל-`<bdi>`/`<pre>`.

## עבודה בתהליך (In flight)

- **REQ #28 COMPLETE** (ba51451): גנריזציית מחוללי-HTML הושלמה.
- **REQ #29 COMPLETE** (63b3ad2): תשתית דוחות ניהוליים + RAG דחייה + סנכרון.
- **REQ #30 — V8 exec-summaries COMPLETE** (2026-06-14): brief עודכן מ-V5-era ל-V8 (9 ממצאים כולל 3 מוקדי דלק, 16 קידוחים, 7 מקורות); INTERNAL+PUBLIC HTMLs נוצרו (65KB+52KB); דליפת "רימטל" ב-PUBLIC reference תוקנה; generator limitation documented.
