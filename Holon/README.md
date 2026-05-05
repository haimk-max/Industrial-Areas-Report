# אזור תעשייה חולון — Zone Pilot

**מטרה**: בדיקת מתודולוגיית הדיווח (template רעננה) על אזור שני לפני הכללה ל-18 אזורים.

**סטטוס**: ⏳ ממתין לנתונים — מבנה תיקיות מוכן

---

## מבנה תיקיות (זהה לרעננה)

```
Holon/
├── data/              ← נתונים עיבודיים (ייווצרו ע"י scripts)
│   └── external/      ← מקורות חיצוניים חולון-ספציפיים
├── charts_v2/         ← גרפים (ייווצרו אוטומטית)
├── output/            ← דוח דוח (HOLON_REPORT_V1.md)
└── forensics/         ← ניתוח forensics (ייווצר אוטומטית)
```

---

## מקורות ונתונים

### מקורות בסיסיים **משותפים** לכל האזורים
נמצאים בשורש הפרויקט:
- **`Base-Report/`** ← TAHAL 2008, דוח בקרת איכות מים 2021, וכו'
- **`External Data/`** ← PRTR, דוחות שפכי תעשייתיים, וכו'

### נתונים חולון-ספציפיים

#### `Water Quality Data/` (בשורש הפרויקט)
קובץ Excel מדידות איכות מים של חולון:
- שם מומלץ: `holon_measurements.xlsx` (או `היסטורית_איכות_מים_חולון.xlsx`)
- פורמט: זהה לרעננה
- עמודות: קידוח | תאריך | פרמטר | ריכוז | יחידה
- טווח שנים: ככל הניתן (עדיף 2011–2025)

#### `Holon/data/external/` 
דוחות חולון-ספציפיים:
- דוח בקרת איכות מים — חולון (אם שונה מדוח 2021 לאומי)
- דוח TAHAL 2008 — אזור חולון (אם קיים)
- דוח שפכי תעשייתיים מתאגיד המים המקומי
- כל מסמך הידרוגיאולוגי מקומי אחר

---

## שלבי עבודה (אחרי העלאת נתונים)

```bash
# שלב 1: חילוץ מ-Excel
python scripts/parse_excel.py --zone holon

# שלב 2: ניקוי + נרמול
python scripts/preprocess.py --zone holon

# שלב 3: איחוד עם מקורות היסטוריים
python scripts/consolidate_data.py --zone holon

# שלב 4: ניתוח מגמות Mann-Kendall
python scripts/trend_analysis.py --zone holon

# שלב 5: ניתוח פורנזי
python scripts/forensics_analyzer.py --zone holon

# שלב 6: גרפים
python scripts/generate_charts_v2.py --zone Holon

# שלב 7: אימות דוח
python scripts/validate_report.py --report Holon/output/HOLON_REPORT_V1.md --charts-dir Holon/charts_v2
```

---

## נקודות מעקב

- [ ] קובץ Excel מדידות חולון — **להעלות ל-`Water Quality Data/`**
- [ ] דוחות חולון-ספציפיים (אם קיימים) — **להעלות ל-`Holon/data/external/`**
- [ ] הגדרת polygon ITM של אזור חולון — **לאשר/לתקן ב-`zone_definitions/zone_polygons.json`**
- [ ] רשימת קידוחים (`tier1_historical_boreholes.json`) — **להשלים ב-`zone_definitions/`**
- [ ] מפעלים פוטנציאליים (facility discovery) — **לבצע אחרי נתונים**

