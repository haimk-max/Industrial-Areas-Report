# תהליך ביקורת דוח Word (Expert Review Cycle)

> **גרסה נוכחית**: הדוח הקנוני הוא **V8** (`Holon/output/HOLON_REPORT_V8.{md,html,docx}`).
> כל הנתיבים למטה משתמשים ב-`Holon/output/` — תיקיית הפלט הקנונית. **אין** להשתמש בנתיבי
> `rerun_v2_*` או `lean_workspace/output/` (נמחקו/הוחלפו). החלף `V8` בגרסה העדכנית בעת הביקורת.

## סקירה כללית
תהליך זה מאפשר למומחים לבדוק את דוח אזה"ת חולון בפורמט Word עם יכולת:
- הערות נקודתיות (Track Changes — עריכה ישירה של טקסט ספציפי)
- הערות כלליות (Comments — הצעות לשיפור התהליך/המבנה)

---

## ⚠️ הערה קריטית — המרת <bdi>HTML→Word</bdi> בסביבה זו

`libreoffice --headless --convert-to docx` **שבור ב-container** (כושל על כל קלט, "source file could not be loaded"). לכן:

| מסלול | כלי | איכות | מתי |
|-------|-----|--------|-----|
| **המרה ידנית** (מומלץ) | דפדפן  — העתק HTML  — הדבק ל-Word | גבוהה (CSS+RTL נשמרים) | להפצה למומחים |
| Python (אוטומטי) | `markdown_to_docx.py` + `embed_holon_figures_v5.py` | בסיסי (ללא CSS) | טיוטות פנימיות |

**להפצה למומחה — העדף את המסלול הידני** (browser <bdi>copy-paste → Word</bdi>, או Word File→Open על ה-HTML).

---

## שלבי התהליך

### שלב 1: הכנת הדוח לביקורת

**מסלול Python (טיוטה פנימית):**
```bash
python scripts/markdown_to_docx.py \
  Holon/output/HOLON_REPORT_V8.md \
  Holon/reviews/HOLON_REPORT_V8_for_review.docx
python scripts/embed_holon_figures_v5.py \
  Holon/reviews/HOLON_REPORT_V8_for_review.docx \
  Holon/output/HOLON_REPORT_V8.html
```

**מסלול ידני (מומלץ להפצה):** פתח את `Holon/output/HOLON_REPORT_V8.html` בדפדפן  — בחר הכול  — העתק  — הדבק ל-Word  — שמור כ-`.docx`.

**תוצאה**: קובץ Word עם RTL מלא, יישור justified, Track Changes זמין, שפה he-IL.

### שלב 2: שליחה לביקורת
שלח את ה-`.docx` למומחים עם הוראות:
1. **Track Changes**: כל עריכת טקסט עם Track Changes פעיל (`Review > Track Changes`)
2. **Comments**: הערות כלליות דרך `Review > New Comment`
3. **שמור עם שם חדש**: לדוגמה `HOLON_REPORT_V8_<expert_name>.docx`

### שלב 3: עיבוד ההערות

#### 3a. חילוץ הערות
```bash
python scripts/process_word_comments.py \
  Holon/reviews/HOLON_REPORT_V8_<expert_name>.docx \
  Holon/reviews/comments_<expert_name>.json \
  Holon/reviews/comments_<expert_name>.md
```
**פלט**: `comments_<expert>.json` (מובנה) + `comments_<expert>.md` (קריא). הערות מסווגות אוטומטית ל**נקודתיות** (עריכות טקסט ספציפי) ו**כלליות** (מבנה/תהליך/גישה).

#### 3b. יישום הערות נקודתיות
```bash
python scripts/apply_markdown_comments.py \
  Holon/output/HOLON_REPORT_V8.md \
  Holon/reviews/comments_<expert_name>.json \
  Holon/output/HOLON_REPORT_V8_revised.md
```

#### 3c. ניתוח הערות כלליות
```bash
python scripts/apply_markdown_comments.py --general-only \
  Holon/reviews/comments_<expert_name>.json \
  Holon/reviews/general_feedback_summary.md
```
**תוצאה**: סיכום הערות כלליות (שינויי prompts, ארגון פרקים, מתודולוגיה) — קלט ל-Step 4 (Opus) בריצה הבאה.

---

## דוגמת זרימה מלאה — ביקורת הידרולוג

```bash
# 1. הכנה (מסלול ידני מומלץ; כאן Python לדוגמה)
python scripts/markdown_to_docx.py \
  Holon/output/HOLON_REPORT_V8.md \
  Holon/reviews/HOLON_REPORT_V8_for_review.docx

# [שלח למומחה; מחזיר HOLON_REPORT_V8_hydrogeologist.docx]

# 2. חילוץ הערות
python scripts/process_word_comments.py \
  Holon/reviews/HOLON_REPORT_V8_hydrogeologist.docx \
  Holon/reviews/comments_hydrogeologist.json \
  Holon/reviews/comments_hydrogeologist.md

# 3. סקירה
cat Holon/reviews/comments_hydrogeologist.md

# 4. יישום הערות נקודתיות
python scripts/apply_markdown_comments.py \
  Holon/output/HOLON_REPORT_V8.md \
  Holon/reviews/comments_hydrogeologist.json \
  Holon/output/HOLON_REPORT_V9_revised.md
```

---

## סיווג הערות (Word)

| סוג | דוגמה | פעולה ב-Word |
|-----|-------|---------------|
| **נקודתית** | "שנה 'זיהום' ל-'מהילה' בפסקה זו" | בחר טקסט  — Track Changes  — ערוך |
| **כללית** | "סדר הפרקים: מקורות  — מוקדים  — מגמות" | New Comment על המבנה הכללי |

**פורמט שדות הערה (JSON)**:
```json
{
  "id": "comment-1",
  "author": "שם המומחה",
  "date": "2026-06-10",
  "text": "תוכן ההערה",
  "category": "point_specific|general",
  "scope": "פרק/סעיף",
  "status": "pending|implemented|acknowledged"
}
```

## כללי עבודה

**הערות נקודתיות**: ✓ עריכות טקסט ישירות (Track Changes פעיל); ✓ שינוי משפטים/תרכובות/הערות מקור; ✗ אל תשנה מבנה/סדר פרקים; ✗ אל תיגע בטבלאות נתונים מלאות.

**הערות כלליות**: ✓ שיפורי תהליך (prompts, סדר ניתוח); ✓ ארגון (חלוקת פרקים); ✓ מתודולוגיה; ✗ אל תיתן הערות על מילים בודדות (זה נקודתי).

## ביקורות מרובות
```bash
for expert in hydrogeologist hydrologist economist; do
  python scripts/process_word_comments.py \
    Holon/reviews/HOLON_REPORT_V8_${expert}.docx \
    Holon/reviews/comments_${expert}.json \
    Holon/reviews/comments_${expert}.md
done
cat Holon/reviews/comments_*.md > Holon/reviews/ALL_FEEDBACK.md
```

## עדכון חוזר (Iteration)
הערות כלליות מהותיות  — ריצת Opus מחדש (Step 4+5) דרך `scripts/run_pipeline.sh`, לא תיקון ידני של ה-HTML. הערות נקודתיות בלבד  — `apply_markdown_comments.py`  — גרסה הבאה (V9).

---

**Last Updated**: 2026-06-10 (REQ #29 — נתיבים מעודכנים ל-V8/Holon/output, LibreOffice-broken מתועד)
**Process Owner**: haimk@water.gov.il
