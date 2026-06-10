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

## עבודה בתהליך (In flight)

- **REQ #28 COMPLETE** (ba51451): שני השלבים סגורים. גנריזציית מחוללי-HTML הושלמה — `data_loader.py` + 2 המחוללים מקבלים `--zone`; legacy archived; QA gates הוקשחו. הפייפליין זון-גנרי מקצה-לקצה.
- **REQ #29 — שלמות לקראת אריזה** (בתהליך): תשתית דוחות-ניהוליים (de-hardcode V5→latest, חיווט לפייפליין, חוזה טריות) + RAG דחייה רשמית + סנכרון קבצי-מעקב. **תוכן V8 של הדוחות הניהוליים נדחה עד אישור הידרולוג.**
