# מדריך המרה לפורמט Word (DOCX)

## סקירה כללית
שני שיטות להמרת דוח V5 לפורמט Word עם RTL וטקסט מיושר:

| שיטה | מקור | יתרונות | חסרונות |
|------|------|---------|---------|
| **<bdi>Markdown→DOCX</bdi>** | `markdown_to_docx.py` | קל, מהיר, ללא dependencies | עיצוב בסיסי בלבד, ללא תמונות |
| **<bdi>HTML→DOCX</bdi>** | `html_to_docx.py` | עיצוב מלא, SVG maps מובנע, סגנונות | דורש LibreOffice, איטי יותר |

## שיטה 1: <bdi>Markdown→DOCX</bdi> (קל, מהיר)

### שימוש
```bash
python scripts/markdown_to_docx.py \
  Holon/rerun_v2_2026-05-28/output/HOLON_REPORT_V5.md \
  Holon/output/HOLON_REPORT_V5_lightweight.docx
```

### פלט
- **גודל**: 65 KB
- **מבנה**: 187 פסקאות, 20 טבלאות
- **עיצוב**: בסיסי (RTL, justified, bold/italic)
- **תמונות**: לא מובנע (references בלבד)
- **זמן**: ~1 שנייה

### מתי להשתמש
✓ ביקורות מהירות בודקות  
✓ הפצה פנימית  
✓ כאשר אין LibreOffice זמין  
✓ כאשר גודל קובץ קריטי  

## שיטה 2: <bdi>HTML→DOCX</bdi> (מלא, styled)

### שימוש
```bash
python scripts/html_to_docx.py \
  Holon/rerun_v2_2026-05-28/output/HOLON_REPORT_V5.html \
  Holon/output/HOLON_REPORT_V5_full.docx
```

### פלט
- **גודל**: 64.6 KB (דחוס!)
- **מבנה**: 187 פסקאות, 20 טבלאות
- **עיצוב**: מלא (colors, fonts, layouts, SVG)
- **תמונות**: SVG map מובנע
- **זמן**: ~5-10 שניות (LibreOffice headless)

### מתי להשתמש
✓ ביקורות חיצוניות של מומחים  
✓ ביקורות משפטיות/רגולטוריות  
✓ הצגות רשמיות  
✓ כאשר עיצוב חיוני  

## תיאור טכני: <bdi>HTML→DOCX</bdi> Pipeline

### שלב 1: המרה LibreOffice
```bash
libreoffice --headless --convert-to docx --outdir [dir] [input.html]
```
- LibreOffice פותח את ה-HTML
- ממיר CSS —עיצוב Word
- שומר SVG כתוכן מובנע
- מחזיר DOCX

### שלב 2: שיפור RTL ושפה
```python
doc = Document(docx_path)
# בכל פסקה:
- pPr.append(OxmlElement('w:bidi'))          # RTL
- alignment = WD_ALIGN_PARAGRAPH.JUSTIFY      # Justified
- language = 'he-IL'                          # Hebrew
```

### שלב 3: הגנת עמודים
```python
# לפני כל טבלה: בדוק אם צריך page break
# התכנסו של break_before אם הטבלה גדולה
```

## השוואה מפורטת

### Markdown Method
```
Input: HOLON_REPORT_V5.md (71 KB)
  ↓
python markdown_to_docx.py
  ├─ Parse markdown (headings, para, tables)
  ├─ Create Document() object
  ├─ Add each block with RTL+justified
  └─ Save DOCX
Output: HOLON_REPORT_V5_lightweight.docx (65 KB)

Features:
✓ RTL text direction
✓ Justified alignment
✓ Hebrew language
✓ Bold, italic, code formatting
✓ Table structure
✓ Lists (bullet points)
✓ Heading hierarchy
✗ No colors or styling
✗ No embedded images
✗ No complex CSS
```

### HTML Method
```
Input: HOLON_REPORT_V5.html (233 KB)
  ↓
python html_to_docx.py
  ├─ LibreOffice --headless conversion
  │  ├─ Parse HTML
  │  ├─ Apply CSS rules
  │  ├─ Convert styles to Word
  │  └─ Embed images/SVG
  ├─ Enhance RTL settings (document-level)
  ├─ Add page break protection
  └─ Save DOCX
Output: HOLON_REPORT_V5_full.docx (64.6 KB)

Features:
✓ RTL text direction (enhanced)
✓ Justified alignment
✓ Hebrew language
✓ All HTML formatting preserved
✓ Colors and styling
✓ SVG maps embedded
✓ Table structure
✓ Lists
✓ Heading hierarchy
✓ Page breaks (avoid table cuts)
✓ Font sizes and weights
✗ Requires LibreOffice installed
```

## דוגמאות שימוש

### לביקורת מומחים
```bash
# שלח HTML version עם SVG map
python scripts/html_to_docx.py \
  Holon/rerun_v2_2026-05-28/output/HOLON_REPORT_V5.html \
  Holon/reviews/HOLON_REPORT_V5_for_expert_review.docx

# שלח למומחה:
# הערות  — Track Changes
# שיפורים  — Comments
```

### לביקורת פנימית מהירה
```bash
# קל וקצר
python scripts/markdown_to_docx.py \
  Holon/rerun_v2_2026-05-28/output/HOLON_REPORT_V5.md \
  /tmp/quick_review.docx

# סקירה מהירה
# שינויים חשובים בלבד
```

### ביקורת מרובה (עובדים עם שני versions)
```bash
# Version 1: Lightweight (internal review)
python scripts/markdown_to_docx.py \
  HOLON_REPORT_V5.md \
  HOLON_INTERNAL.docx

# Version 2: Full (expert review)
python scripts/html_to_docx.py \
  HOLON_REPORT_V5.html \
  HOLON_EXPERT.docx

# שלח שניהם, בהתאם לסוג הביקורת
```

## עדכון לאחר ביקורת

### עם markdown comment integration
```bash
# 1. עבד את Word עם הערות
# 2. חלץ הערות
python scripts/process_word_comments.py \
  HOLON_REPORT_V5_reviewed.docx \
  comments.json \
  comments.md

# 3. יישום בחזרה למרקדאון
python scripts/apply_markdown_comments.py \
  HOLON_REPORT_V5.md \
  comments.json \
  HOLON_REPORT_V5_revised.md

# 4. המר לWord שוב
python scripts/html_to_docx.py \
  HOLON_REPORT_V5_revised.html \
  HOLON_REPORT_V5_v2.docx
```

## דרישות מערכת

### עבור markdown_to_docx.py
```
Python 3.7+
python-docx >= 1.2.0
lxml >= 3.1.0
```

### עבור html_to_docx.py
```
Python 3.7+
python-docx >= 1.2.0
LibreOffice >= 7.0 (headless mode)
```

### בדוק availability
```bash
python3 -c "from docx import Document; print('✓ python-docx')"
which libreoffice && echo "✓ LibreOffice"
```

## Troubleshooting

### LibreOffice timeout
```bash
# אם ההמרה תלויה:
# 1. וודא שאין LibreOffice instances רצים
pkill -9 soffice

# 2. כדי להגדיל timeout:
# עדכן timeout בקוד: subprocess.run(..., timeout=120)
```

### RTL not working in Word
```bash
# בוודא שהשפה של יצירת נתוני (language) הוא Hebrew
# Word > Review > Language > Set to Hebrew (Israel)
```

### SVG not appearing
```bash
# <bdi>HTML→DOCX</bdi>: SVG יהיה embedded כ-raster
# אם דרוש SVG ממוטי: שמור HTML במקום
```

### Page breaks cutting tables
```bash
# html_to_docx.py בדרך כלל מטפל בזה
# אם בעיה: edit html_to_docx.py שיטת add_page_break_before_tables
```

## ביצועים

| פעולה | זמן | הערות |
|------|------|--------|
| <bdi>Markdown→DOCX</bdi> | ~1 שנייה | Python בלבד |
| <bdi>HTML→DOCX</bdi> | ~5-10 שניות | LibreOffice startup |
| Batch (10 files) | ~2 דקות | LibreOffice reuse |

## תוכנית עתידית

- [ ] Native SVG preservation (currently: raster in DOCX)
- [ ] Batch conversion script
- [ ] Style templates (corporate branding)
- [ ] Automated quality checks (page breaks, fonts, etc.)

---

**Last Updated**: 2026-05-31  
**Tested on**: LibreOffice 24.2.7.2, python-docx 1.2.0
