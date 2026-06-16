# Playbook: Structured Data Pack (6-CSV Schema)

> **Self-contained summary** of the Data Pipeline specification for V5 hybrid pipeline.  
> **Full methodology & detailed schema**: See `../../../DATA_PIPELINE_SPEC.md` (root SSOT)

---

## מהו Structured Data Pack?

**Structured Data Pack** = 6 CSVs המכילים את כל המדידות, תוצאות Mann-Kendall, וחישובי חומרה לאזור נתון.

**מיקום**: `{zone}/02_data/`

**קלט**: measurements Excel + בורות מסוגים Tier 1, 2, 3  
**פלט**: 6 CSVs מנורמלים וממוזהמים

---

## ה-6 CSVs בקצרה

| CSV | תכן | שורות | יחידה |
|-----|------|--------|-------|
| **measurements_scoped.csv** | כל מדידה בחלון 5 שנים | 2,000–5,000 | measurement |
| **latest_results.csv** | תוצאה אחרונה לכל (well, param) | 300–800 | well-parameter pair |
| **severity_by_well_family.csv** | אינדקס חומרה לכל (well, משפחה) | 150–400 | well-family pair |
| **trends_by_well_parameter.csv** | תוצאות Mann-Kendall | 200–600 | well-parameter pair |
| **monitoring_gaps.csv** | קידוחים שקטים ≥12 חודשים | 10–50 | borehole |
| **figure_ready_series.csv** | סדרות זמן לגרפים | 2,000–5,000 | measurement |

**Bucket scale**: 0–8 (<bdi>clean → extreme</bdi>), עפ"י `C_max_5y / DWS × 100`.

---

## Generation (שלבים מהירים)

```bash
# 1. Parse measurements from Excel
python scripts/parse_excel.py --zone holon

# 2. Calculate trends + severity + gaps
python scripts/trend_analysis.py --zone holon
python scripts/forensics_analyzer.py --zone holon

# 3. Bundle into 6 CSVs (note: V5 pack tools use the directory name, e.g. Holon)
python scripts/generate_zone_data_pack.py --zone Holon
```

**Output**: כל 6 CSVs ב-`Holon/02_data/`

---

## QA Checklist

- [ ] All 6 CSVs present + valid CSV format
- [ ] No nulls in Required columns
- [ ] Concentrations numeric (no "<LOD" strings)
- [ ] Dates ISO format (YYYY-MM-DD)
- [ ] Bucket values ∈ [0, 8]
- [ ] DWS values > 0
- [ ] Units normalized to ppb (µg/L)

---

**For detailed field-by-field schema, constraints, and examples**, see:  
📍 **`../../../DATA_PIPELINE_SPEC.md`** (Root SSOT — 180 lines, Hebrew + detailed)

**Version**: 1.1  
**Status**: ✓ PLAYBOOK (References root SSOT)  
**Last Updated**: 2026-05-27
