# scripts/report_designed/ — מנוע סגנון וגרפים

תיקייה זו מכילה את **מנוע ה-SVG charts** וה-**designed mini-report** עבור דוחות אזורי תעשייה.

---

## ארכיטקטורה — שני HTML generators

לכל אזור קיימים **שני HTML outputs מקבילים**, שניהם מ-V4.md (Markdown של Opus):

| Generator | פלט | מטרה | תיקייה |
|-----------|-----|-------|---------|
| `generate_{zone}_full_html.py` | `{ZONE}_REPORT_V4.html` | **דוח מלא** — כל 10 הסעיפים של V4.md ב-HTML | `scripts/` |
| `generate_{zone}_designed.py` | `{ZONE}_REPORT_DESIGNED.html` | **דוח מעוצב מקוצר** — תקציר ויזואלי עם top-6 charts + key narrative | `scripts/` |

**שני הדוחות עצמאיים** — לא מיזוג. שניהם נשמרים.

### למה שני דוחות?

- **`_V4.html`** = הפלט הקנוני לארכיון ולמומחה הידרוגיאולוג. כולל את כל הסעיפים (10) + 5 השדה הסטטיסטיים. ~167KB.
- **`_DESIGNED.html`** = פלט ויזואלי לסיכום ולהצגה. ~139KB. סעיפים מקוצרים + חתימות גראפיות מודגשות (severity ledger, family panels, monitoring gaps, recommendations, classification map).

### Pipeline order

```
1. <bdi>Opus → writes</bdi> V4.md (narrative + בחירת קידוחים למוקדים)
2. data_loader.extract_report_boreholes(V4.md, severity) → list of canonical_ids
3. svg_charts.svg_*_panels(measurements, boreholes_override=list) → SVG figures
4. Both generators run in <bdi>parallel → V4</bdi>.html + DESIGNED.html
```

ראה `ZONE_REPORT_PROCESS_GUIDE.md` §VIII.1 לתיאור מלא של ה-pipeline.

---

## קבצי הליבה

| קובץ | אחריות |
|------|---------|
| `svg_charts.py` | פונקציות יצירת SVG: severity_ledger, severity_matrix, *_panels (CVOC/METALS/FUEL), monitoring_gaps, classification_table, borehole_map |
| `data_loader.py` | טעינת CSV מ-`{ZONE}/lean_workspace/`; `extract_report_boreholes()` לקבלת רשימת קידוחים מ-V4.md; `extract_narrative_sections()` לחילוץ סעיפים מ-V4.md |
| `emit_figures.py` | המרת SVG ל-PNG (cairosvg) לשימוש pre-Opus או offline |
| `template.html` | תבנית HTML של designed report (RTL, CSS bidirectional) |

---

## API — `boreholes_override` parameter

הוכנס ב-V4.2 (2026-05-14) — מאפשר ל-Opus לבחור אילו קידוחים יצוירו:

```python
from scripts.report_designed import svg_charts as sc, data_loader as dl

# Opus's selection from V4.md
sev = dl.load_severity_index()
boreholes = dl.extract_report_boreholes(v4_md_path, severity_df=sev)

# Render with override (cap per family: CVOC=6, METALS=4, FUEL=6)
cvoc_svg = sc.svg_cvoc_panels(measurements, sev, boreholes_override=boreholes)
metals_svg = sc.svg_chromium_panels(measurements, boreholes_override=boreholes)
fuel_svg = sc.svg_btex_panels(measurements, boreholes_override=boreholes)
```

**Fallback**: אם `boreholes_override=None`, הפונקציה משתמשת ב-top-N לפי severity (legacy behavior).

**עיקרון**: Opus בוחר **אילו** קידוחים; הקוד מחליט **איך** לאייר (סגנון, צבעים, סדר, גודל).

---

## RTL Requirements (אזורים בעברית)

ראה `ZONE_REPORT_PROCESS_GUIDE.md` §VI ו-§IX:

- כל `<text>` ב-SVG עם תוכן עברי  — `direction="rtl"` + `text-anchor="end"`
- מספרים+יחידות בטקסט מעורב  — `<tspan direction="ltr" unicode-bidi="isolate">` או `<bdi>`
- ב-HTML output → CSS `unicode-bidi: isolate` על containers; `<bdi>` סביב מספרים/יחידות/שמות מזהמים באנגלית

---

## הוספת אזור חדש

1. צור `scripts/generate_{new_zone}_full_html.py` ו-`generate_{new_zone}_designed.py` — העתק מ-Holon, החלף paths
2. צור `{new_zone}/lean_workspace/` עם המבנה הסטנדרטי (ראה PROCESS_GUIDE §I)
3. צור `{new_zone}/output/{NEW_ZONE}_REPORT_V4.md` (Opus output)
4. הרץ את שני ה-generators
5. validate per PROCESS_GUIDE §VII

---

**Last Updated**: 2026-05-14
**SSOT**: `ZONE_REPORT_PROCESS_GUIDE.md`
