# אזור תעשייה חולון — Zone Pilot

**מטרה**: בדיקת מתודולוגיית הדיווח (template רעננה) על אזור שני לפני הכללה ל-18 אזורים.

**סטטוס**: ⏳ ממתין לנתונים — מבנה תיקיות מוכן

---

## מה להעלות לכל תיקייה

### `Base-Report/`
דוחות רשות המים / TAHAL עבור חולון:
- דוחות בקרת איכות מים קודמים (PDF)
- דוח TAHAL 2008 (אם קיים עבור חולון)
- כל מסמך רקע הידרוגיאולוגי

### `data/`
קבצי נתונים מובנים (ייווצרו ע"י pipeline):
- `boreholes.csv` — יווצר אוטומטית מ-`parse_excel.py`
- `concentrations.json` — יווצר אוטומטית מ-`preprocess.py`
- `facility_attribution.json` — יווצר ע"י agent discovery

### `data/external/`
מקורות חיצוניים:
- `prtr_fulldatabase-2024.xlsx` — אותו קובץ PRTR לאומי (להעתיק מ-External Data/)
- דוח שפכי תעשייתיים מתאגיד המים של חולון (PDF, אם קיים)
- כל מסמך רגולטורי מקומי

### `Base-Report/` — קובץ Excel מדידות
קובץ Excel של מדידות איכות מים (פורמט זהה לרעננה):
- שם מומלץ: `היסטורית_איכות_מים_חולון.xlsx`
- עמודות: קידוח, תאריך, פרמטר, ריכוז, יחידה
- טווח שנים: ככל הניתן (עדיף 2011–2025)

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

- [ ] קובץ Excel מדידות — **להעלות**
- [ ] דוחות PDF בסיסיים — **להעלות**
- [ ] הגדרת polygon ITM של אזור חולון — **לאשר/לתקן**
- [ ] רשימת קידוחים (`tier1_historical_boreholes.json`) — **להשלים**
- [ ] מפעלים פוטנציאליים (facility discovery) — **לבצע אחרי נתונים**
