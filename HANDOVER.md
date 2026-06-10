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
- **LibreOffice HTML→docx שבור ב-container** (זוהה 2026-06-10): `libreoffice --headless --convert-to docx` כושל על **כל** קלט (אפילו plain text) עם "source file could not be loaded". לא ניתן לתיקון בסביבה הנוכחית. **חלופות**: Python `markdown-to-docx` + `embed_holon_figures_v5.py` (עובד, ללא CSS); או המשתמש ממיר HTML→Word ידנית (browser copy-paste → Word — **האפשרות המומלצת** לאיכות גבוהה; גם Word File→Open HTML, Google Docs import, LibreOffice מקומי).

## עבודה בתהליך (In flight)

- **REQ #27 COMPLETE** (88fcb11): V8 report (Opus Steps 4+5), HTML 225KB Gate 6 PASS, Word doc 505KB (4 figures scale=3 ~220 DPI). משתמש ימיר HTML→Word ידנית ויעביר לביקורת מומחה.
- **REQ #28 שלב 2 נותר**: גנריזציית מחוללי-HTML חסומה ב-`report_designed/data_loader.py` (בסיס-ראיות V4 נעוץ-חולון ב-lean_workspace) — refactor גדול, **לא חוסם חולון**. ראה ORCHESTRATION.md לפירוט.
