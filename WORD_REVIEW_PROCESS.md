# תהליך ביקורת דוח Word (HOLON_REPORT_V5.docx)

## סקירה כללית
תהליך זה מאפשר למומחים שונים לבדוק את דוח אזה"ת חולון V5 בפורמט Word עם יכולת:
- הערות נקודתיות (עריכה ישירה של טקסט ספציפי)
- הערות כלליות (הצעות לשיפור התהליך)

## שלוחות ההתהליך

### שלב 1: הכנת הדוח לביקורת
```bash
python scripts/markdown_to_docx.py \
  Holon/rerun_v2_2026-05-28/output/HOLON_REPORT_V5.md \
  Holon/rerun_v2_2026-05-28/output/HOLON_REPORT_V5.docx
```

**תוצאה**: קובץ Word עם:
- RTL (right-to-left) מהדורה מלאה
- תיישור justified לכל הטקסט
- יכולת Track Changes מופעלת
- שפה: עברית (he-IL)

### שלב 2: שליחה לביקורת
שלח את `HOLON_REPORT_V5.docx` למומחים עם הוראות:
1. **Track Changes**: כל עריכה ישירה של טקסט תעשה עם Track Changes פעיל (`Review > Track Changes`)
2. **Comments**: הערות כלליות יוכנסו דרך `Review > New Comment`
3. **שמור עם שם חדש**: לדוגמה `HOLON_REPORT_V5_expert_name.docx`

### שלב 3: עיבוד ההערות
#### 3a. חילוץ הערות
```bash
python scripts/process_word_comments.py \
  Holon/rerun_v2_2026-05-28/output/HOLON_REPORT_V5_expert_name.docx \
  Holon/rerun_v2_2026-05-28/comments/comments_expert_name.json \
  Holon/rerun_v2_2026-05-28/comments/comments_expert_name.md
```

**פלט**:
- `comments_expert_name.json`: נתונים מובנים (לעיבוד סקריפט)
- `comments_expert_name.md`: דוח קריא (לסקירה ידנית)

הערות מסווגות:
- **נקודתיות**: עריכות ישירות, בקשות לשינוי טקסט ספציפי
- **כלליות**: הצעות לשיפור מבנה, תהליך, או גישה (לא מתייחסות לטקסט ספציפי)

#### 3b. יישום הערות נקודתיות
```bash
python scripts/apply_markdown_comments.py \
  Holon/rerun_v2_2026-05-28/output/HOLON_REPORT_V5.md \
  Holon/rerun_v2_2026-05-28/comments/comments_expert_name.json \
  Holon/rerun_v2_2026-05-28/output/HOLON_REPORT_V5_revised.md
```

**תוצאה**: דוח Markdown עדכן עם הערות משולבות

#### 3c. ניתוח הערות כלליות
```bash
python scripts/apply_markdown_comments.py \
  [--general-only] \
  Holon/rerun_v2_2026-05-28/comments/comments_expert_name.json \
  Holon/rerun_v2_2026-05-28/comments/general_feedback_summary.md
```

**תוצאה**: סיכום הערות כלליות לשיפור תהליך הדוח:
- הצעות לשינוי תבניות prompts
- שיפורים בארגון או מבנה
- שינויים בקטגוריזציה או סדר פרקים

## דוגמת זרימה מלאה

### סיناריו: ביקורת מהידרולוג מומחה
```bash
# 1. הכנה
python scripts/markdown_to_docx.py \
  Holon/rerun_v2_2026-05-28/output/HOLON_REPORT_V5.md \
  Holon/reviews/HOLON_REPORT_V5_for_review.docx

# [שלח למומחה; מומחה מחזיר עם הערות]

# 2. עיבוד הערות מהומחה (מחזיר hydrogeologist_review.docx)
python scripts/process_word_comments.py \
  Holon/reviews/HOLON_REPORT_V5_hydrogeologist.docx \
  Holon/reviews/comments_hydrogeologist.json \
  Holon/reviews/comments_hydrogeologist.md

# 3. סקירת סיכום
cat Holon/reviews/comments_hydrogeologist.md

# 4. יישום הערות נקודתיות
python scripts/apply_markdown_comments.py \
  Holon/rerun_v2_2026-05-28/output/HOLON_REPORT_V5.md \
  Holon/reviews/comments_hydrogeologist.json \
  Holon/output/HOLON_REPORT_V5_revised_v1.md

# 5. הערות כלליות לשיפור תהליך
cat Holon/reviews/comments_hydrogeologist.md | grep "^## הערות כלליות"
# [ידנית: סקור וקבע שיפורים בתהליך]
```

## פורמט הערות בדוקומנט Word

### הערות נקודתיות (Point-Specific Comments)
**דוגמה**: "צריך לשנות 'זיהום' ל-'מהילוג' בפסקה זו"

```
עריכה: [בחר טקסט] → Review → Track Changes → שנה טקסט
או: [בחר טקסט] → Review → New Comment → כתוב הערה
```

### הערות כלליות (General Comments)
**דוגמה**: "הסדר של הפרקים צריך להיות: מקורות → מוקדי זיהום → מגמות"

```
→ Review → New Comment
כתוב הערה על המבנה הכללי (לא על טקסט ספציפי)
```

## ערכי מטא-דטה

### עבור כל הערה, בדוק:
1. **סוג**: עריכה ישירה (Track Changes) או הערה (Comment)
2. **סיווג אוטומטי**:
   - **נקודתית** אם: התייחסות לטקסט ספציפי, בקשה לשינוי חלק
   - **כללית** אם: התייחסות לתהליך, מבנה, גישה, אסטרטגיה

### בשדות הערה:
```json
{
  "id": "comment-1",
  "author": "שם המומחה",
  "date": "2026-05-31",
  "text": "תוכן ההערה",
  "category": "point_specific|general",
  "scope": "פרק/סעיף",
  "status": "pending|implemented|acknowledged"
}
```

## כללי עבודה

### עבור הערות נקודתיות:
1. ✓ בצע שינויים ישירים בטקסט (Track Changes חייב להיות פעיל)
2. ✓ שנה משפטים, תרכובות, הערות מוצא
3. ✓ אל תזכור טבלאות נתונים מלאות או רפרנסים לחבילות קונטקסט
4. ✗ אל תשנה את המבנה הכללי או סדר הפרקים

### עבור הערות כלליות:
1. ✓ הצע שיפורים בתהליך (פרומפטים, סדר ניתוח)
2. ✓ הצע שיפורים בארגון (חלוקת פרקים, קטגוריזציה)
3. ✓ הצע שיפורים בגישה (מתודולוגיה, עומק ניתוח)
4. ✗ אל תתן רפרנסים מפורטים לטבלאות נתונים
5. ✗ אל תתן הערות על מילים בודדות (זה עבור הערות נקודתיות)

## סטטוס וניהול

### ניהול ביקורות מרובות
אם משתתפים מרובים:
```bash
# עבור כל ביקורת
for expert in hydrogeologist hydrologist economist; do
  python scripts/process_word_comments.py \
    Holon/reviews/HOLON_REPORT_V5_${expert}.docx \
    Holon/reviews/comments_${expert}.json \
    Holon/reviews/comments_${expert}.md
done

# סיכום כולל
cat Holon/reviews/comments_*.md > Holon/reviews/ALL_FEEDBACK.md
```

### עדכון חוזר (Iteration)
```
Revision 1:
  HOLON_REPORT_V5.md → [ביקורת] → HOLON_REPORT_V5_v1.md
  
Revision 2:
  HOLON_REPORT_V5_v1.md → [ביקורת נוספת] → HOLON_REPORT_V5_v2.md
```

## שדרוג קבועים

### עם עדכון דוח (Regeneration)
אם יש לעדכן את הדוח בעקבות הערות כלליות:
```bash
# 1. קבע שיפורים בתהליך (prompts, סדר ניתוח)
# 2. ריצה מחדש של pipeline V5 עם שיפורים
python scripts/generate_holon_v5_html.py --report [path] --output [path]

# 3. המר לחדש Word
python scripts/markdown_to_docx.py [md_path] [docx_path]
```

---

**Last Updated**: 2026-05-31  
**Process Owner**: haimk@water.gov.il
