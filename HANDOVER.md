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

## עבודה בתהליך (In flight)

- **REQ #27 Part C** (ממתין להרצת Opus): התבניות+פרומפטים מוכנים (Part A+B נדחפו). נותר: Opus Step 4 → zone_diagnosis.md חדש (עם ניתוח קידוחי הפקה) → render Step 5 → Opus Step 5 → HOLON_REPORT_V8.md → HTML+QA. ראה footgun ה-staleness לעיל לגבי סדר הרינדור.
- **חוב אורקסטרציה — REQ #28 שלב 1 הושלם** (f85dc35): `generate_zone_data_pack.py` גנרי (byte-identical על חולון), `run_pipeline.sh` דרַייבר, `ORCHESTRATION.md` מפה, Gate 5/6 גנרי-לגרסה (`_latest_report` glob → קולט V7/V8), 2 סקריפטי V4 deprecated. **שלב 2 נותר**: גנריזציית מחוללי-HTML חסומה ב-`report_designed/data_loader.py` (בסיס-ראיות V4 נעוץ-חולון ב-lean_workspace) — refactor גדול, **לא חוסם חולון**; איחוד מוסכמת `--zone`; ריצת אזור-2 e2e. ראה ORCHESTRATION.md.
