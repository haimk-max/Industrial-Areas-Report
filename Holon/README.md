# Holon — אזור תעשייה חולון

**מטרה**: היישום הראשון של המסגרת הכללית (framework) שפותחה והוכחה ב-Raanana.
חולון = first application of the generalised methodology, not a one-off pilot.

**סטטוס**:
- ✅ נתונים הועלו (Excel + 4 PDFs + KMZ polygon)
- ✅ Pipeline רץ end-to-end (parse → trend → forensics → charts)
- ⏳ דוח סיכום אזור בעברית — לכתיבה
- ⏳ Facility discovery — לביצוע

---

## מבנה תיקיות (זהה ל-Raanana)

```
Holon/
├── data/
│   ├── boreholes.csv               (יווצר ע"י parse_excel)
│   ├── measurements.csv            (יווצר ע"י parse_excel)
│   ├── parameters.csv              (יווצר ע"י parse_excel)
│   ├── trends.csv                  (יווצר ע"י trend_analysis)
│   ├── facility_attribution.json   (יווצר ע"י AI agent — pending)
│   └── external/                   ← דוחות חולון-ספציפיים (4 PDFs)
├── charts_v2/                      (יווצר ע"י generate_charts_v2)
├── forensics/                      (יווצר ע"י forensics_analyzer)
└── output/                         ← דוח סיכום (לכתיבה)
```

---

## מקורות נתונים

### משותפים לכל אזור (בשורש הפרויקט)
- `Base-Report/` — TAHAL 2008, דוח רשות המים 2021
- `External Data/` — PRTR לאומי וכו'

### חולון-ספציפיים
- `Water Quality Data/היסטורית איכות מים לקידוחים - חולון.xlsx` (1.5MB, 20,613 מדידות)
- `Holon/data/external/` — 4 דוחות PDF של רשות המים על חולון
- `zone_definitions/zone_polygons.json` → `holon` — polygon ITM (הומר מ-KMZ)
- `config/zone_overrides/holon.yaml` — מיפוי עמודות Excel (15 עמודות במקום 18 ברעננה)

---

## מה נמצא עד עכשיו (Phase 5 framework run)

| מטריקה | ערך |
|--------|------|
| קידוחים גולמיים מ-Excel | 112 |
| קידוחים נבחרים (Tier 2 לפי polygon) | 111 |
| מדידות (לפני סינון) | 20,613 |
| מדידות (אחרי סינון לקידוחים נבחרים) | 20,506 |
| פרמטרים | 203 |
| שנים | 2010–2025 |
| זוגות (קידוח×פרמטר) למגמה | 4,762 |
| סיווגי מגמה | INCREASING=48, DECREASING=80, STABLE=613, NONE=4,021 |
| זוגות co-occurrence (מקור משותף) | 2,803 |
| מדידות CVOC (TCE/PCE/DCE/וכו') | 4,915 |
| מדידות BTEX | 4,316 |
| מדידות PFAS | 39 |
| גרפים שיוצרו | site_map, **cvoc_trends**, btex_trends, **pfas_trends**, exceedances_bar, severity_panel |

---

## מה חסר (לסיום Phase 5)

1. ~~**Param-code mapping** (`REQ-H3`)~~ ✅ נפתר ע"י `scripts/param_families.py` (regex-based CVOC/BTEX/PFAS classifier)
2. **Facility discovery**: להריץ AI agent על חולון (זיהוי גורמי מקור פוטנציאליים)
3. **דוח סיכום אזור**: `Holon/output/HOLON_REPORT_V1.md` — לכתיבה (Raanana כטמפלייט)
4. **כרטיסי קידוח**: אופציונלי — לאזור גדול עם 111 קידוחים, מומלץ להתמקד ב-top contaminated בלבד
5. **Validate**: `python scripts/validate_report.py --report Holon/output/HOLON_REPORT_V1.md --charts-dir Holon/charts_v2`

---

## הערה מתודולוגית

הפרוצדורה המלאה לאקטיבציה של אזור — **כולל אזורים נוספים מתוך 18 הרשימה** — מתועדת ב-**`CLAUDE.md` § 8 ("Adding a New Zone")**. README זה משמש כתיעוד "מה נעשה בפועל לחולון" ולא כפרוצדורה כללית.
