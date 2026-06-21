# בסיס ידע למים (Water KB) — אזור staging

אזור **staging** של בסיס הידע לתחום המים, מתארח כרגע בתוך ריפו IAR. ינוד ל-repo ייעודי `water-knowledge-base` כשיבשיל (הכול Markdown — ההגירה היא העתקת תיקייה).

## מבנה
- `KB_GOVERNANCE.md` — **חוקי הממשל (קרא קודם)**.
- `raw/` — מקורות גלם *immutable* (source of truth).
- `01_Domains/` — ידע מושגי (מזהמים, הידרוגיאולוגיה, סמנים).
- `02_Methods/` — שיטות (מקשרות ל-`toolkit/`).
- `03_Projects/` — דפוסי-פרויקט בני-שימוש-חוזר.
- `_Lessons/` — לקחים חוצי-פרויקט.

## בסיס מתודולוגי
דפוס ה-LLM-Wiki של Karpathy (`raw → wiki → file-back`, Markdown, ללא RAG) **+ שכבת ממשל רגולטורית**.
רקע מלא: `docs/KB_METHODOLOGY_REVIEW.md` · עיצוב: `docs/WATER_KB_ARCHITECTURE.md`.

## הוספת ידע
סקיל **`/kb-transfer`** — מזקק מקור (דוח / מסמך IAR / צ'אט) לדפי `draft`. אדם מאשר → `reviewed`/`locked`.
