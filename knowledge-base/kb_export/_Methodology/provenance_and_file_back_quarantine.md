---
title: provenance, דירוג A–E, ושער ה-file-back
type: methodology
status: draft
evidence: D
source: "ZONE_REPORT_PROCESS_GUIDE.md (A–E); docs/KB_METHODOLOGY_REVIEW.md; סשן 2026-06"
last_compiled: 2026-06-21
---

# provenance, דירוג A–E, ושער ה-file-back

## דירוג ראיות (A–E)
יורש מ-`ZONE_REPORT_PROCESS_GUIDE.md`:
A = raw_report_verified · B = ai_extracted_with_page_ref · C = web_verified_current_activity · D = inferred/derived (כולל סינתזת LLM) · E = weak/mention_only.

## שער ה-file-back
כל תוצר שנכתב בחזרה ל-KB נכנס כ-`status: draft, evidence: D` עד **אימות אדם**. רק אדם מקדם ל-`reviewed`/`locked` ומעדכן `evidence`.

## למה — "הלבנת provenance"
בלי השער, הסקה שנולדה כסינתזת-LLM מתויקת בחזרה, ובהמשך **נקראת כאילו הייתה עובדה ממקור**. השער מונע זאת.

## גיבוי חיצוני
- **model collapse** (Shumailov, *Nature* 2024) — אימון רקורסיבי על פלט-LLM קורס; דורש להבחין מה AI-derived.
- **EU AI Act §50** — סימון machine-readable של תוכן סינתטי (אכיף 8/2026). תיוג `evidence:D` הוא גם יישור-לרגולציה.

## ניוד
דיסציפלינת provenance לכל KB עם תרומת-LLM.

## ראה
`capture_hot_verify_cold.md` · `explain_vs_execute_boundary.md`
