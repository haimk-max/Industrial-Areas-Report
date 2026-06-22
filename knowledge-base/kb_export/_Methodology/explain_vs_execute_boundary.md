---
title: גבול הסבר↔ביצוע (KB↔toolkit)
type: methodology
status: draft
evidence: D
source: "סשן 2026-06; docs/KB_METHODOLOGY_REVIEW.md; REUSABLE_ASSETS §2.7"
last_compiled: 2026-06-21
---

# גבול הסבר↔ביצוע (KB↔toolkit)

## הכלל
**אם זה רץ → שכבה ביצועית** (toolkit/code/config). **אם קוראים אותו לשיפוט → KB** (פרשנות, מתי/למה, מגבלות).

## מקשרים, לא משכפלים
דף KB **מקשר** לפרמטר תפעולי (`implements:`) — לעולם לא משכפל את הערך. **מקור-אמת יחיד למספר = הקוד.**

## דוגמת ה-drift
מסמך כתב פעם `soft_trigger=3` בעוד הקוד `=2`. אילו המסמך היה מקשר במקום לשכפל — הסתירה לא הייתה נולדת. זה הנימוק הקונקרטי לכלל.

## גיבוי
- **Diátaxis** — הפרדה מחייבת בין *Reference* (עובדות/תפעולי) ל-*Explanation* (מושגים/שיפוט).
- = **REUSABLE_ASSETS §2.7** (deterministic/generative separation): קוד מייצר את כל המספרים; ה-LLM מסנתז מעל נתונים מאומתים.

## ניוד
כל פרויקט עם קוד + תיעוד מקביל.

## ראה
`provenance_and_file_back_quarantine.md`
