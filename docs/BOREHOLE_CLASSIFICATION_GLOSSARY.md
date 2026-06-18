# מילון סיווג קידוחים (Borehole Classification Glossary)

**SSOT** לסיווג קידוחים בכל אזורי הניטור. כל שינוי בלוגיקת הסיווג — כאן תחילה.

**מימוש**: `scripts/parse_excel.py` → `_borehole_type()`
**אימות**: `scripts/qa_pipeline.py` → Gate 1.5 + `tests/test_parse_excel.py`

---

## עקרון: בדיקה כפולה (Dual-Check)

לכל קידוח שני סימני זיהוי בלתי תלויים:

1. **`purpose` ("ייעוד הקידוח")** — עמודת ה-Excel. **מקור סמכותי**.
2. **קידומת שם הקידוח** — אות/אותיות פתיחה של השם העברי. **מאשר או fallback**.

### היררכיית ההכרעה
| מצב | תוצאה | `classification_source` |
|------|--------|--------------------------|
| purpose וקידומת מזוהים ותואמים | אותו סוג | `purpose+prefix` |
| purpose וקידומת מזוהים אך **סותרים** | לפי **purpose** (סמכותי) + log WARNING | `purpose (prefix conflict)` |
| רק purpose מזוהה | לפי purpose | `purpose` |
| רק קידומת מזוהה (purpose חסר/לא ידוע) | לפי קידומת | `prefix` |
| שניהם לא מזוהים | `unknown` + log WARNING | `unclassified` |

---

## סוגי קידוחים (well_type)

### קידוחי הפקה (Production)

| well_type | purpose | קידומת | תיאור | סיכון |
|-----------|---------|--------|--------|--------|
| `mekorot_production` | "חברת מקורות" | `מק` | קידוח הפקה של חברת מקורות — **אספקה ציבורית** | **גבוה ביותר** — זיהום פוגע ישירות באספקה עירונית |
| `private_production` | "פרטי" | `פ` | קידוח הפקה פרטי (חקלאי/תעשייתי) | גבוה — פוגע במפעיל פרטי |

### קידוחי ניטור-מחקר (Research/Monitoring)

| well_type | purpose | קידומת | תיאור |
|-----------|---------|--------|--------|
| `research_monitoring` | "יוזום" / "מחקר" | `יו` / `מח` | קידוחי יוזום (השירות ההידרולוגי) וקידוחי מחקר — עוגן ארוך-שנים לרשת מפלסים, לעיתים מדידות איכות מים. **לא חלק מרשת הניטור התעשייתית הבסיסית**; משמשים כגיבוי/עיבוי |

### קידוחי ניטור תעשייתי (Industrial Monitoring)

| well_type | purpose | קידומת | תיאור |
|-----------|---------|--------|--------|
| `industrial_monitoring` | "תעשיה" / "ניטור תעשיה" | `נת` | קידוח ניטור ליד מתקנים תעשייתיים (כימיה, ציפוי מתכות) |
| `fuel_monitoring` | "דלק" / "ניטור דלק" | `נד` | קידוח ניטור ליד מתקני דלק (תחנות, מסופים) — BTEX, MTBE |

### Fallback / לא ידוע

| well_type | מתי | פעולה |
|-----------|-----|--------|
| `monitoring` | קטגוריית fallback ישנה (purpose/קידומת לא זוהו במימוש קודם) | Gate 1.5 → WARNING; דורש בדיקה |
| `unknown` | purpose וקידומת לא מזוהים | Gate 1.5 → WARNING; דורש בדיקת מקור ידנית |

---

## התאמת קידומת (כללי)

הקידומת מזוהה רק כאשר אחריה **רווח** (`"מק חולון 12"`) או **קו-תחתון** (`"מק_חולון_12"`).
זה מונע התאמות-שווא — למשל `"פז סיירים"` **לא** תזוהה כקידוח פרטי (`פ`), כי `"פז"` אין אחריו גבול.

קידומות ארוכות נבדקות לפני קצרות (`מק`/`מח` לפני `פ`).

---

## כללי הכרעת-סתירה (Conflict Resolution)

| תרחיש | תוצאה | פעולה |
|--------|--------|--------|
| purpose="חברת מקורות", שם="נד דלק..." | `mekorot_production` (purpose מנצח) | log WARNING; לבדוק אם ה-Excel או השם שגוי |
| purpose="" (ריק), שם="מק חולון 12" | `mekorot_production` (לפי קידומת) | תקין — fallback מתוכנן |
| purpose="ערך לא במילון", שם="נד פז..." | `fuel_monitoring` (לפי קידומת) | תקין — purpose לא זוהה, קידומת הצילה |
| purpose ושם שניהם לא מזוהים | `unknown` | log WARNING; escalate למשתמש |

---

## דוגמאות לפי אזור

### חולון (Holon — stress-test)
```
מק_חולון_12        חברת מקורות  → mekorot_production
יו_מקוה_ישראל_29/2 יוזום       → research_monitoring
נת_חולון_1         ניטור תעשיה  → industrial_monitoring
נד_אגד_אזור_1      ניטור דלק   → fuel_monitoring
פ_אזור_מקור_חקלאי  פרטי        → private_production
```
התפלגות: 5 mekorot, 1 research, 40 industrial, 64 fuel, 2 private (112 בסך הכל).

### רעננה (Raanana — תקדים סגנוני)
```
raanana_nt_*  ניטור תעשיה  → industrial_monitoring
raanana_nd_*  ניטור דלק   → fuel_monitoring
raanana_p_*   פרטי        → private_production
```
התפלגות: 3 industrial, 2 fuel, 2 private (7 בסך הכל). אין מק/יו.

---

## הוספת ערך חדש

ערך `purpose` או קידומת חדשים (באזורים עתידיים) → הוסף ל-`_PURPOSE_MAP` / `_PREFIX_MAP`
ב-`scripts/parse_excel.py`, הוסף test ב-`tests/test_parse_excel.py`, ועדכן את הטבלאות כאן.
עד אז Gate 1.5 ידגל אותם כ-`unknown` (WARNING) ולא ייפלו בשקט ל-`monitoring`.
