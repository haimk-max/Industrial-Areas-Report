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

- **§IV = SSOT יחיד לסדר** (REQ #24, 788e8c7): §3 = מוקדים גיאוגרפיים (חומרה יורדת); משפחות משניות בתוך מוקד; "פערי כיסוי" אחרון. FUEL "תמיד אחרון" — בוטל. כל שינוי עתידי לכלל הסדר → §IV בלבד.
- **focus_order ארטיפקט חובה**: zone_diagnosis.md חייב לכלול `## סדר מוקדים` (טבלה פַּרסְבִיל). Gate 4 מאמת. הדיאגנוזה הנוכחית של חולון כוללת אותו (מאז V6).

## footguns חוזרים

- **פער staleness דיאגנוזה→דוח** (זוהה 2026-06-10, תיקון נדחה): הפרומפט המרונדר של הדוח חותם **רק** `template_sha256` — לא את ה-sha של zone_diagnosis.md. לכן `{FOCUS_ORDER_LIST}` (snapshot שנצרב ב-render) יכול להיות מיושן מול הדיאגנוזה החיה, ו-Gate 3 לא יתפוס זאת. **המשמעת Step4→render→Step5 נאכפת במוסכמה בלבד.** אם מריצים Step 4 מחדש — חובה לרנדר מחדש את zone_report_prompt.md לפני Step 5, אחרת אופוס צורך סדר-מוקדים סותר (snapshot מנוון מול קובץ מלא). תיקון מוצע (טרם בוצע): לחתום diagnosis-sha + בדיקת Gate 3.
- **פער staleness דוח→דוחות-ניהוליים** (זוהה 2026-06-10): הדוחות הניהוליים (INTERNAL+PUBLIC exec summaries) נוצרים מ-brief YAML שנגזר מהדוח הראשי, אך **אין חוזה טריות** שמקשר ביניהם. ה-brief נושא כעת `source_report_version` + `source_report_sha` (REQ #29); `run_pipeline.sh --stage exec-summary` מזהיר אם ה-sha לא תואם את הדוח הנוכחי. **אם מעדכנים את הדוח הראשי — חובה לחדש את הדוחות הניהוליים** (אחרת מפיצים תוכן ישן תחת גרסה חדשה).
- **`Holon/02_data/` הוא ה-Data Pack הקנוני — לא למחוק** (זוהה 2026-06-10 אחרי שנמחק בטעות ב-REQ#28 ושוחזר): `02_data/` (7 CSVs per DATA_PIPELINE_SPEC) נקרא ע"י **Gate 2** ו-`generate_zone_brief.py`. הוא **שונה** מ-`lean_workspace/` (בסיס-ראיות V4 שה-designed HTML generators קוראים). שניהם פעילים במקביל. אל תתבלבל ביניהם ואל תמחק `02_data/` כ"כפילות".
- **LibreOffice HTML→docx שבור ב-container** (זוהה 2026-06-10): `libreoffice --headless --convert-to docx` כושל על **כל** קלט (אפילו plain text) עם "source file could not be loaded". לא ניתן לתיקון בסביבה הנוכחית. **חלופות**: Python `markdown-to-docx` + `embed_holon_figures_v5.py` (עובד, ללא CSS); או המשתמש ממיר HTML→Word ידנית (browser copy-paste → Word — **האפשרות המומלצת** לאיכות גבוהה; גם Word File→Open HTML, Google Docs import, LibreOffice מקומי).
- **`generate_zone_html_from_brief.py` מחליף רק חלק מהסעיפים** (זוהה 2026-06-14): ה-generator מחליף `context_intro`, `findings`, `framing_warning`, `zone_name`, `doc_id` בלבד. סעיפי `stats_public`, `means_summary`, `methodology`, `timeline` נשארים **hardcoded מה-reference template**. לחולון זה עובד (reference = חולון), אך **חוסם אזור שני**. תיקון: להוסיף replacement logic לסעיפים החסרים.
- **דליפת שמות מתקנים ב-PUBLIC reference** (זוהה ותוקן 2026-06-14): "רימטל" הופיע פעמיים ב-HOLON_PUBLIC.html reference — הפרת מדיניות אנונימיזציה. הוחלף ב-"אתר מחזור מתכות משוקם". **לבדוק כל reference חדש לדליפות לפני commit.**

## עבודה בתהליך (In flight)

- **REQ #28 COMPLETE** (ba51451): גנריזציית מחוללי-HTML הושלמה.
- **REQ #29 COMPLETE** (63b3ad2): תשתית דוחות ניהוליים + RAG דחייה + סנכרון.
- **REQ #30 — V8 exec-summaries COMPLETE** (2026-06-14): brief עודכן מ-V5-era ל-V8 (9 ממצאים כולל 3 מוקדי דלק, 16 קידוחים, 7 מקורות); INTERNAL+PUBLIC HTMLs נוצרו (65KB+52KB); דליפת "רימטל" ב-PUBLIC reference תוקנה; generator limitation documented.
