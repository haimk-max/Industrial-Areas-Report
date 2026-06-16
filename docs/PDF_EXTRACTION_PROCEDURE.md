# הליך מיצוי מידע מ-PDFs והכנתו לעיבוד

## סקירת ביצוע (Pipeline Overview)

הערכת קידוחים וזיהום בכל אזור מבוססת על שלוש שכבות מידע:

1. **Structured Data Pack** — TSV/CSV מ-Excel, מדידות ממוגדרות (`02_data/`)
2. **External Context** — דוחות היסטוריים (PDFs), ממצאים מיוחסות לקידוחים, מקורות חשודים
3. **Web Intelligence** — חיפוש אתרים, PRTR, דיווחי רשויות

הליך זה מתעסק בשכבה **2 — External Context**: איך מוציאים נתונים מ-PDFs, מארגנים אותם בצורה שמכונה יכולה לעיבד, ומאחדים מרובים.

---

## שלב 1: הכנת PDFs וטקסט גולמי

### מקור נתונים: ספריות PDF

לכל אזור, PDFs מאוחסנים בשתי ספריות אופציוניות:

```
<Zone>/data/external/*.pdf        # PDFs ייעודיות לאזור (דוחות מקומיים, מדידות חדשות)
Base-Report/                      # PDFs משותפות (TAHAL 2008, דוח 2021 של הרשות)
```

**דוגמה חולון**:
- `water-sources-status_tehom_holon-part1.pdf` (9.7 MB, תמצית 2007)
- `water-sources-status_tehom_holon-part2.pdf` (23 MB)
- `water-sources-status_tehom_FinalReport-Holon.pdf` (21 MB)
- `water-sources-status_tehom_Holon-BatYan-Dec2007.pdf` (14 MB)

### ציוד: Extraction Tools

**דרישות מערכת**:
- `pdftotext` (מ-Poppler utils) — חילוץ טקסט עם שמירת RTL עברי (דגל `-layout`)
- `pdfinfo` (מ-Poppler) — קריאת מטה-דאטה (מספר עמודים, תאריך יצירה)
- Python 3.10+

**התקנה** (Linux/macOS):
```bash
# Debian/Ubuntu
apt-get install poppler-utils

# macOS
brew install poppler
```

### ביצוע: `extract_zone_pdfs.py`

**תפקיד**: קריאת כל PDF בספריה, חילוץ טקסט עברי-friendly, שמירת אינדקס.

**שימוש**:
```bash
python scripts/extract_zone_pdfs.py --zone holon
python scripts/extract_zone_pdfs.py --zone <zone> --force          # חילוץ מחדש
python scripts/extract_zone_pdfs.py --zone <zone> --include-shared # כולל Base-Report/
```

**מה שהסקריפט עושה**:

1. **סריקה ספריות**: `<Zone>/data/external/` + `Base-Report/` (אם `--include-shared`)
2. **בדיקת מטא-דאטה**: לכל PDF — מספר עמודים (`pdfinfo`), גודל, תאריך שינוי
3. **בדיקת קשישות**: יש אינדקס קיים (`_pdf_index.json`)? האם ה-PDF כבר עבר עיבוד?
4. **חילוץ טקסט**:
   - הרץ `pdftotext -layout <file>.pdf <file>.txt`
   - דגל `-layout` שומר על רוחב-עמודות (חשוב לטבלאות ו-RTL)
   - תוצאה: `_raw_text/<filename>.txt` (UTF-8, RTL-safe)
5. **עדכון אינדקס**: `_pdf_index.json` — רישום PDF עם:
   - שם קובץ
   - מספר עמודים
   - גודל בתים
   - תאריך חילוץ UTC
   - דגל `extraction_ok` (הצליח או כשל)
   - טיפוסי שגיאה (אם `extraction_ok: false`)

**פלט**:
```
<Zone>/data/external/
├── _raw_text/
│   ├── water-sources-status_tehom_holon-part1.txt        (extracted text)
│   ├── water-sources-status_tehom_holon-part2.txt
│   ├── water-sources-status_tehom_FinalReport-Holon.txt
│   └── ... (כל PDF → .txt)
└── _pdf_index.json                                        (manifest)
```

**דוגמה `_pdf_index.json`**:
```json
{
  "zone_id": "holon",
  "extraction_date_utc": "2026-06-01T12:34:56Z",
  "pdf_count": 4,
  "pdfs": [
    {
      "filename": "water-sources-status_tehom_holon-part1.pdf",
      "page_count": 142,
      "char_count_extracted": 125000,
      "extraction_ok": true,
      "extracted_at": "2026-06-01T12:34:56Z"
    },
    { ... }
  ]
}
```

**עמידות (Idempotency)**:
- אם `_raw_text/<name>.txt` כבר קיים ויש רשומה בהצלחה ב-`_pdf_index.json` — דלוג (SKIP)
- אם `--force` → חילוץ מחדש לכל PDF
- אם הקודם כשל (`extraction_ok: false`) → נסיון חוזר

---

## שלב 2: AI Sub-Agent Processing

### תפקיד Agent

לכל PDF שחולץ בשלב 1, סוכן AI **Claude** קורא את `_raw_text/<name>.txt` ומייצא:

```json
_findings_<tag>.json        # findings from this PDF
```

**Persona**: Hydrogeologist (עברית, מטמון טכני גבוה)

**Input to Agent**:
- קובץ טקסט (`_raw_text/<name>.txt`)
- Manifest (`_pdf_index.json`)
- Prompt template (`PDF_INGESTION_PROMPT.md`) — קבוצה של שאלות:

  1. **Boreholes mentioned**: Extract well names + coordinates (if stated) + depth + classification (production/monitoring)
  2. **Contamination findings**: Parameters + concentrations + dates + interpretation (trend, severity)
  3. **Facility suspects**: Company/site names + contaminants + confidence (HIGH/MEDIUM/LOW) + evidence
  4. **Hydrogeology context**: Flow direction, aquifer layer, seasonal patterns
  5. **Trends**: If report describes time-series changes (e.g., "TCE rising since 2008")
  6. **Key quotes**: Significant statements for forensics (literal text + page ref)
  7. **Recommendations**: Actions from report (monitoring frequency, investigation, remediation)

**Output JSON Schema**:
```json
{
  "source_file": "water-sources-status_tehom_holon-part1.pdf",
  "title_he": "דוח מצב מקורות מי-תהום — חולון (2006)",
  "year": 2006,
  "author_org_he": "מכללת תל-אביב",
  "boreholes_mentioned": [
    {
      "name_he": "מק חולון 14",
      "coordinates_itm": [32.00123, 34.78945],
      "depth_m": 45.5,
      "classification": "monitoring"
    }
  ],
  "contamination_findings": [
    {
      "parameter": "TCE",
      "family": "CVOC",
      "concentration_ug_l": 25.3,
      "date": "2006-03-15",
      "well": "מק חולון 14",
      "severity_relative_to_dws": "HIGH (504%)",
      "interpretation_he": "עלייה טדורית"
    }
  ],
  "facilities_suspected": [
    {
      "name_he": "תדיראן קשר",
      "confidence": "HIGH",
      "suspected_contaminants": ["TCE", "1,1-DCA"],
      "evidence_he": "קרבה 200 מ' לקידוח, ייצור שנות 1990-2008"
    }
  ],
  "trends_described_he": [
    "עלייה במודולציה של TCE מ-2006 ל-2015 בקידוח מק חולון 14"
  ],
  "key_quotes_he": [
    {
      "text": "קידוח זה נמצא בדיוק דאונגראדיאנט מתדיראן קשר...",
      "page": 45
    }
  ],
  "recommendations_he": [
    "הגברת תדירות בדיקות TCE בקידוח מק חולון 14 לרבעון"
  ]
}
```

### Implementation

**ליד מי?** סוכן AI מוסדי:
- דלדל עם `scripts/pdf_ingestion_agent.py` (placeholder, מחכה לסוכן יעודי)
- או ידני: המשתמש קורא PDF + כותב JSON ידנית

**עדכון (Phase 2)**:
- Skill `pdf-ingest` (לא קיים עדיין) — automatic via Claude PDF API

---

## שלב 3: Merge Extracted Findings

### תפקיד: `merge_extracted_findings.py`

**מטרה**: אחד מרובים `_findings_*.json` לקובץ משותף וחד `extracted_findings.json`.

**שימוש**:
```bash
python scripts/merge_extracted_findings.py --zone holon
```

**לוגיקה**:

1. **סריקה**: קרא כל `_findings_*.json` בתיקייה
2. **דדוקציה**:
   - **Boreholes**: by `name_he` (first occurrence wins, תיעוד source)
   - **Contamination findings**: keep all (multi-source = confidence boost)
   - **Facilities**: deduplicate by `(name_he, confidence)`, keep longest evidence
   - **Trends/recommendations/quotes**: consolidate all + deduplicate exact text
3. **אתריבוציה מקור**: כל entry מקבל `source_file` — tracking איזה PDF הוא בא ממנו
4. **כתיבה**: `extracted_findings.json` — unified structure

**פלט**:
```json
{
  "zone_id": "holon",
  "merge_date_utc": "2026-06-01T13:45:00Z",
  "source_files": [
    "water-sources-status_tehom_holon-part1.pdf",
    "water-sources-status_tehom_holon-part2.pdf",
    ...
  ],
  "boreholes_unique": 28,
  "boreholes": [
    {
      "name_he": "מק חולון 14",
      "coordinates_itm": [32.00123, 34.78945],
      "depth_m": 45.5,
      "classification": "monitoring",
      "source_file": "water-sources-status_tehom_holon-part1.pdf"
    }
  ],
  "contamination_findings": [ ... all, with source ],
  "facilities_suspected": [ ... deduped, with source ],
  "trends": [ ... consolidated ],
  "recommendations": [ ... all ],
  "key_quotes": [ ... all with page ref ]
}
```

**דדוקציה בפרטי**:

- **Boreholes**: אם שני PDFs מזכירים "מק חולון 14":
  - שמור את הראשון (ללא שחזור מחדש)
  - תעד `source_file: "part1.pdf"`
  - בקובץ זרימה נפרד, אם יש סתירה בקואורדינטות — דגל WARN

- **Facilities**: אם PDF A אומר "תדיראן, HIGH confidence" ו-PDF B אומר "תדיראן, MEDIUM confidence":
  - שמור את HIGH (מעודכן יותר)
  - מיזג evidence strings משניהם

---

## שלב 4: Usage in Zone Diagnosis & Report

### Point of Consumption

שני שלבי Opus קוראים מ-`extracted_findings.json`:

1. **Zone Diagnosis (Step 4)** — Opus #1:
   - Input: `extracted_findings.json` + measurement CSV + web findings
   - Output: `zone_diagnosis.md` — 8 שאלות מקצועיות (geographic foci, facility attribution, monitoring gaps)

2. **V5 Report (Step 5)** — Opus #2:
   - Input: `zone_diagnosis.md` + `extracted_findings.json` + measurement trends
   - Output: `HOLON_REPORT_V5.md` — 8 סעיפים (section 2 expansion: hydrogeology + facility context)

### Confidence Levels (Evidence Classification)

כל statement בדוח מסומן עם Evidence Grade **A–E**:

| Grade | דעיכה | הגדרה | דוגמה |
|-------|------|--------|---------|
| **A** | ירוק | `raw_report_verified` | בדיקה ידנית של מדידה בדוח מקור עם page ref |
| **B** | כחול | `ai_extracted_with_page_ref` | Opus חילץ מטקסט PDF + ציטט עמוד |
| **C** | צהוב | `web_verified_current_activity` | אתר אומת עדכני (PRTR, דיווח עסק) |
| **D** | כתום | `inferred_candidate` | AI השער סביר על קשר בין facilities |
| **E** | אדום | `weak_or_mention_only` | אזכור חלוש בהערה שולית |

**כללים**:
- A+B → strong evidence; use in main narrative
- C → status update; background only (no contamination proof)
- D/E → appendix / context, unless corroborated by measurements

---

## שלב 5: Quality Assurance

### Validation Checklist

כל `extracted_findings.json` חייב לעבור:

1. **Schema validation**: בדוק כנגד `schemas/extracted_findings.schema.json`
2. **Borehole coordinate check**: אם `coordinates_itm` נתונות — בדוק TTM bounds סביר (מתאים אזור)
3. **Deduplication integrity**: כל בור קידוחים מופיע רק פעם אחת; כל facility (עם ביטחוןแรחד) פעם אחת
4. **Source attribution**: כל entry בעל `source_file` (traceability)
5. **Date reasonableness**: דאו שדברו נתונים בטווח הצפוי (1990-2026 בחולון)

### Known Limitations

- **OCR Text Quality**: טקסט מחולץ מ-PDF סרוק (scanned) עשוי להשחת Hebrew — בדוק ידנית עמוד חשוב
- **Coordinate System**: PDFs עתיקות יכולות להשתמש ב-WGS84 בלבד → transformation דרוש ל-ITM
- **Table Complexity**: טבלאות מורכבות עם merge-cells → ניתוח ידני (pdftotext לא טוב בטבלאות מורכבות)

---

## Workflow End-to-End

```
PDFs in <Zone>/data/external/
    ↓ [extract_zone_pdfs.py]
_raw_text/*.txt + _pdf_index.json
    ↓ [AI Sub-Agent or Manual JSON]
_findings_*.json (per PDF)
    ↓ [merge_extracted_findings.py]
extracted_findings.json (unified)
    ↓ [Zone Diagnosis & V5 Report]
zone_diagnosis.md + HOLON_REPORT_V5.md
```

---

## Maintenance

### For New Zones

בעת הוספת אזור חדש (זון #3–18):

1. **Setup**:
   ```bash
   mkdir -p <Zone>/data/external/_raw_text
   ```

2. **Upload PDFs**: העתק ל-`<Zone>/data/external/`

3. **Extract text**:
   ```bash
   python scripts/extract_zone_pdfs.py --zone <zone_id> --include-shared
   ```

4. **AI processing**: ספק `_findings_*.json` (ידנית או via skill)

5. **Merge**:
   ```bash
   python scripts/merge_extracted_findings.py --zone <zone_id>
   ```

6. **Validate**: בדוק `extracted_findings.json` כנגד checklist

### Maintenance Commands

```bash
# Re-extract text for a single PDF
python scripts/extract_zone_pdfs.py --zone holon --force

# List what was extracted (manifest)
cat Holon/data/external/_pdf_index.json | jq '.pdfs[] | {filename, extraction_ok, page_count}'

# Check merged findings
cat Holon/data/external/extracted_findings.json | jq '.boreholes | length'

# Search a specific finding
grep -i "TCE" Holon/data/external/_findings_*.json
```

---

**Last Updated**: 2026-06-14  
**Related Files**:
- `scripts/extract_zone_pdfs.py` — Text extraction engine
- `scripts/merge_extracted_findings.py` — Consolidation engine
- `ZONE_REPORT_PROCESS_GUIDE.md` — Full pipeline (§I.2 PDF ingestion)
- `docs/STATISTICAL_OVERVIEW_METHODOLOGY.md` — Confidence grading (Evidence A–E)
