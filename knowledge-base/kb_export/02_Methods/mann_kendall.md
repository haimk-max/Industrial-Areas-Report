---
title: Mann-Kendall trend test
type: method
status: reviewed
evidence: A
source: "Report 2021 p.49; docs/STATISTICAL_OVERVIEW_METHODOLOGY.md"
implements: "toolkit/pylib/signalkit/trend_analysis.py::calculate_mann_kendall"
validated_by: "הידרולוג — אישור דוח רעננה (IAR), מאי 2026"
last_compiled: 2026-06-21
---

# Mann-Kendall — מבחן מגמה

## מתי משתמשים
זיהוי מגמה בסדרת-זמן של ריכוזי מזהם בקידוח בודד (זוג פרמטר×קידוח), כשיש מספיק מדידות (ראה `entry_criteria` בקוד).

## למה Mann-Kendall (ולא רגרסיה לינארית)
לא-פרמטרי: עמיד ל-outliers, לא מניח נורמליות, מתאים לסדרות סביבתיות קצרות ולא-אחידות. **אסור לתאר את המנוע כ"רגרסיה לינארית"** — הוא Mann-Kendall (tie-corrected variance, continuity-corrected Z) עם SNR gating.

## מגבלות (חובה לדווח)
- **קידוחים כלואים (confined)**: זרימה איטית מעוותת אות מגמה — דגל פרשני.
- **SNR נמוך**: מתחת לסף, מגמה = NONE ללא קשר ל-MK (gating).
- מעט מדידות: ראה fallback מלא-רשומה בקוד.

## הפרמטר התפעולי — לא כאן (החלטה 2)
הספים התפעוליים (`soft_trigger`, ספי SNR strong/moderate, חלון 5 שנים) הם **מקור-אמת בקוד בלבד**:
- קונפיג: `config/analysis_config.yaml` → `trend_analysis`
- מימוש: `signalkit.trend_analysis.calculate_mann_kendall`

דף זה **לא משכפל** את הערכים — זה בדיוק הלקח מ-drift: פעם מסמך כתב `soft_trigger=3` בעוד הקוד `=2`. לכן מקשרים, לא משכפלים.

## פלט
`status` (PASS / FAIL_SNR / INSUFFICIENT_DATA), `trend` (INCREASING / DECREASING / STABLE / NONE), MK z, p, SNR, `soft_trigger_detected`.

## קשור
- סקירה סטטיסטית: `docs/STATISTICAL_OVERVIEW_METHODOLOGY.md`
- סקיל ניתוח: `toolkit/skills/trend-detective/`
