# Skill: agent-rag

> **⚠️ DRAFT / NOT IMPLEMENTED (status: deferred — PROCESS.md REQ #14)**
> סקיל זה הוא **שלד עיצובי בלבד**. אין מאחוריו קוד: אין vector store, אין embeddings, אין semantic search.
> ה"מימוש" למטה הוא pseudo-code. בפועל, איסוף ה-context בפייפליין V5 נעשה ע"י Opus sub-agents שכותבים
> `_findings_*.json` + אצירה ידנית דמוית-NotebookLM (ראה PROCESS_GUIDE §I). **אל תתייחס לסקיל כאל כלי עובד.**
> בנייה אמיתית (design doc + prototype) תופעל רק כשתתקבל החלטה מפורשת. ראה LESSONS.md §3.3a.

## מהו?

**agent-rag** = יומן interactive לאיסוף ועיבוד context מרובה לניתוח ממוחשב.

RAG = "Retrieval-Augmented Generation" (בדיקה + תיקוף מחדש)

בהינתן **תיקיית aזור** (zone directory) עם:
- דוחות PDF וmarkdown
- נתונים בCVS
- ממצאים קודמים

הכלי:
1. **סורק אתרים** (web search לתעשיות, מתקנים)
2. **מחלץ מ-PDFs** (הידרוגיאוגרפיה, גבולות, בעלויות)
3. **מרכז context** לפרומפט (NotebookLM-סגנון)
4. **סידור רמות ודאות** (HIGH/MEDIUM/LOW confidence)

---

## Input

```
/<agent-rag> --zone <zone-id> --task <task-type> [--output <dir>]

Arguments:
  --zone <id>            Zone ID (e.g., "holon") — required
  --task <type>          Task type: assemble | extract | augment — required
  --output <dir>         Output directory for context pack
  --force                Force re-scan (ignore cached results)
  --web-search           Enable web search for facilities (default: enabled)
  --pdf-extract          Enable PDF extraction (default: enabled)
```

---

## Task Types

| Task | Input | Output | תיאור |
|------|-------|--------|--------|
| **assemble** | Zone folder | context_pack/ | Gather all sources + web findings into unified context |
| **extract** | PDF + prompt | findings.json | Extract hydrogeology, facilities, contamination from report |
| **augment** | CSV + context | enriched_csv | Add facility names, source confidence to measurements |

---

## Output (assemble task)

```
{zone}/context_pack/
├── 01_scope/
│   └── zone_wells.csv          (selected boreholes)
├── 02_data/
│   └── measurements.csv         (all measurements, normalized)
├── 03_context/
│   ├── reports_context.<bdi>md       ← Key</bdi> excerpts from PDFs
│   ├── facility_attribution.<bdi>md  ← HIGH</bdi>/MEDIUM/LOW confidence
│   ├── web_findings.<bdi>md          ← Current</bdi> facility operations
│   └── hydrogeology.<bdi>md          ← Aquifer</bdi> flow, geology
└── 04_diagnosis/
    └── zone_diagnosis.md        ← 8 key questions for manual review
```

---

## Example

```bash
/<agent-rag> --zone holon --task assemble --output ./context_packs/
```

**Output** (automatically created):
```
context_packs/holon/03_context/
├── reports_context.md
├── facility_attribution.md
├── web_findings.md
└── hydrogeology.md
```

---

## Confidence Levels

כל אחד מ-**high-confidence findings** מתויג:

| Level | טריגר | דוגמה |
|-------|-------|--------|
| **HIGH** | בדוח רשמי + web-verified | "אלביט, תדיראן — TCE, PCE, מפעל אלקטרוניקה" |
| **MEDIUM** | בדוח רשמי או web | "סונול — דלק, אתר עם טריק דלק היסטורי" |
| **LOW** | הסקה מפתרון הימצאות | "כור מתכת — כרום מזוהה, אך לא שם מתקן מאושר" |

---

## זמן ההפעלה

| Task | זמן | תלויות |
|------|------|--------|
| **assemble** | 30–60s | Internet (web search) |
| **extract** | 2–5min | Opus LLM call |
| **augment** | 10–30s | Local CSV processing |

---

## מטבח (Kitchen — מימוש)

(תוך בנייה) הכלי ישתמש ב-Opus LLM agent זאת עם sub-agents:

```python
# Pseudo-code
def assemble_context_pack(zone_id: str, output_dir: str):
    # 1. Scan zone folder
    zone_path = f"./{zone_id}/"
    
    # 2. Extract PDFs
    pdfs = find_pdfs(zone_path)
    for pdf in pdfs:
        findings = agent.extract_pdf(pdf)  # Opus
        save_findings_json(findings)
    
    # 3. Web search
    facilities = get_facilities_list()
    for facility in facilities:
        web_results = web_search(facility)
        save_web_findings(web_results)
    
    # 4. Assemble context
    context = compile_context_pack(
        zone_path,
        findings_json,
        web_results,
    )
    
    # 5. Write to output
    write_context_pack(output_dir, context)
```

---

## שימוש עם V5 Hybrid Pipeline

השלב השני של הPipeline:

```bash
# Step 1: Scope (manual)
# → zone/01_scope/zone_wells.csv

# Step 2: Data pipeline (scripts)
python scripts/parse_excel.py --zone holon
python scripts/trend_analysis.py --zone holon
# → zone/02_data/ (6 CSVs)

# Step 3: Assemble context (agent-rag)
/<agent-rag> --zone holon --task assemble
# → zone/03_context/ + zone/04_diagnosis/

# Step 4–7: Report generation (V5 prompt + Opus)
```

---

**Status**: ⏳ IN PROGRESS (skeleton defined; Opus orchestration TBD)
