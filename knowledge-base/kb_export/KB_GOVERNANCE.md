# KB_GOVERNANCE — חוקי הממשל של בסיס הידע

> **סטטוס**: אזור **staging** בתוך IAR; ינוד ל-repo ייעודי `water-knowledge-base` (אז ייקרא `CLAUDE.md`).
> **בסיס**: דפוס ה-LLM-Wiki של Karpathy + ממשל רגולטורי. רקע: `docs/KB_METHODOLOGY_REVIEW.md`.

## עקרון-על
ה-LLM כותב ומתחזק את ה-wiki; האדם אחראי **מקורות, שאלות, ואישור**. כל דף נושא frontmatter שמאפשר אכיפה אוטומטית (lint) ושער-אדם.

## החלטה 1 — בעלות (חותמת בגרות)
`status:` קובע כמה ה-LLM חופשי:
| status | מי שולט |
|--------|---------|
| `draft` | LLM כותב/משכתב חופשי |
| `reviewed` | LLM מציע, אדם אישר (חובה `validated_by`) |
| `locked` | שינוי דורש אישור מפורש + חתימת מומחה (נוסחאות, ספים, תוצרים רגולטוריים) |
| `deprecated` | נשמר להיסטוריה, לא מקור פעיל |

## החלטה 2 — גבול KB↔toolkit
**אם זה רץ → toolkit; אם קוראים אותו לשיפוט → KB.**
- קוד, פרמטרים תפעוליים, נוסחאות → `toolkit/` / `signalkit`.
- פרשנות, מתי/למה, מגבלות → דף KB.
- דף KB **מקשר** (`implements:`) לקוד — **לעולם לא משכפל ערך תפעולי**. מקור-אמת יחיד למספר = הקוד.

## החלטה 3 — provenance (A–E + שער file-back)
כל דף נושא `evidence:` (יורש מ-`ZONE_REPORT_PROCESS_GUIDE.md`):
| רמה | משמעות |
|-----|---------|
| A | raw_report_verified |
| B | ai_extracted_with_page_ref |
| C | web_verified_current_activity |
| D | inferred / derived (כולל סינתזת LLM) |
| E | weak / mention_only |

**שער file-back**: כל תוצר שנכתב בחזרה ל-KB נכנס כ-`status: draft, evidence: D` עד אימות אדם. מונע "הלבנת provenance".

## חוזה ה-frontmatter (מינימלי)
```yaml
---
title: <שם>
type: domain | method | project | lesson | methodology
status: draft | reviewed | locked | deprecated
evidence: A | B | C | D | E
source: "<מקור>"
implements: "<path::function>"   # רק לדפי method הממופים לקוד
validated_by: "<מי, תאריך>"      # חובה ל-reviewed/locked
last_compiled: YYYY-MM-DD
---
```

## כללי lint (machine-checkable)
1. כל דף → `title/type/status/evidence/source/last_compiled` קיימים.
2. `status: reviewed|locked` → חייב `validated_by`.
3. `implements:` → חייב להצביע על קובץ/פונקציה **קיימים** ב-`toolkit/`.
4. דף `method` עם מספר תפעולי בפרוזה וללא `implements:` → אזהרה (חשד לשכפול ערך — החלטה 2).
5. תוכן file-back נשאר `evidence: D` + `status: draft` עד שאדם שינה ידנית.

## ערוצי מקור → raw/
`raw/` = מקורות immutable. ערוצים: דוחות רשמיים, IAR, צ'אטים מ-ChatGPT/Claude, מצגות, מדיניות.
**לא מתחייבים (commit) dump גולמי לא-מסונן** — מסננים מקצועי-רלוונטי-בלבד קודם. תוכן שיחתי נכנס `evidence: D` עד אימות.

## תהליך הוספת ידע: distill → format → review
1. **distill** — ה-LLM מזקק את ה-5% הבר-קיימא (לא מעתיק).
2. **format** — דף Markdown + frontmatter, `status: draft`.
3. **review** — אדם מאשר → `reviewed`/`locked`, מוסיף `validated_by`.

## Lint תקופתי (בעקבות Karpathy)
מעת לעת בקש health-check: סתירות בין דפים, טענות מיושנות, דפים יתומים, והפרות ה-lint לעיל.
