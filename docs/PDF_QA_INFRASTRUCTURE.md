# תשתית שאילתות מבוססת-מסמכים (PDF Q&A Infrastructure) — Bedrock Knowledge Bases Edition

> **סוג המסמך**: מסמך אדריכלות יישומי (design spec). מתאר תשתית למיצוי, אינדוקס ושאילתה של מסמכי דוחות סביבתיים, **מהווה כעת בAmazon Bedrock Knowledge Bases** — רכיב managed RAG המטפל בקליטה, chunking, embedding, ו-retrieval באופן native.
>
> **רקע**: התשתית נגזרה מאפיון פיילוט אמיתי (אזה"ת חולון–בת ים, 13 מסמכים) שנועד להתרחב לכלל הארגון. הפרמטרים והמאפיינים הספציפיים (שדות מטה-דאטה, היררכיית מיקום, זיהוי נספחים) נמומשו כעת בBedrock Knowledge Base configuration וmetadata filtering.
>
> **טכנולוגיה**: Amazon Bedrock Knowledge Bases + Claude Opus (retrieval + synthesis). אחסון: Amazon S3. Embedding: Bedrock native (Titan או בחירה אחרת). Vector search: Bedrock built-in OpenSearch.
>
> **דרישות AWS**: 
> - Bedrock console access + Claude API enablement
> - S3 bucket (source documents + vector index)
> - IAM role עם הרשאות Bedrock + S3
> - boto3 CLI/SDK Python

## יחס למסמכים אחרים

| מסמך | מה הוא מתאר | תחום |
|------|-------------|------|
| `docs/PDF_EXTRACTION_PROCEDURE.md` | התהליך **הקיים בפועל** בפרויקט זה | ספציפי לפרויקט |
| `docs/GENERIC_PDF_EXTRACTION_AND_RETRIEVAL.md` | מדריך גנרי לאזור חדש (שלבים 0–3 + שליפה בסיסית) | גנרי לאזור |
| **`docs/PDF_QA_INFRASTRUCTURE.md`** (מסמך זה) | **תשתית שאילתות מלאה** — אינדוקס מרוכז + שליפה לפי-דרישה + סינתזה | תשתית גנרית |

מסמך זה מרחיב את שני הקודמים: הוא לוקח את המיצוי (שלבים 0–3) והופך אותו ל**שכבת אינדקס רב-ממדי** שמיועדת לענות על **שאלות שלא ניתן לחזות מראש**, ומוסיף את שכבת השליפה-והסינתזה שמופעלת בעת שאלה.

---

## 1. עיקרון-העל: שני זמנים, שני טריגרים

המערכת מורכבת משני תהליכים שנפרדים בזמן ובטריגר. **ערבוב בין השניים הוא טעות התכנון הנפוצה ביותר.**

```
┌──────────────────────────────────────────────────────────────────┐
│  תהליך א׳ — עיבוד מרוכז (BATCH)                                   │
│  טריגר: מסמכים חדשים עולים למאגר המקור (object store)             │
│  תדירות: פעם אחת לכל מסמך (אידמפוטנטי)                            │
│  פלט: אינדקס עשיר, רב-ממדי, מוכן-לשאילתה                          │
│                                                                    │
│   PDFs  — זיהוי-סוג  — חילוץ  — סינון-נספחים  — נתוח  — מיצוי  — אינדוקס│
└──────────────────────────────────────────────────────────────────┘
                              │
                  (האינדקס נשמר, ממתין)
                              │
┌──────────────────────────────────────────────────────────────────┐
│  תהליך ב׳ — שליפה וסינתזה (ON-DEMAND)                             │
│  טריגר: שאלה מגיעה (טקסט חופשי / בחירה על מפה / סינון אזור)       │
│  תדירות: פעם לכל שאלה                                             │
│  פלט: תשובה מעמיקה, מצוטטת, בעברית                                │
│                                                                    │
│   שאלה  — נתוח-כוונה  — שליפה  — הרכבת-קונטקסט  — סינתזת-LLM  — תשובה │
└──────────────────────────────────────────────────────────────────┘
```

### למה ההפרדה קריטית

- **האינדקס לא יודע מה ישאלו אותו.** לכן הוא חייב ללכוד **כל ממד שאילתה אפשרי** מראש (מיקום, זמן, מזהם, קידוח, אקוויפר, מתקן, גורם-עורך, גורם-נדון, סוג-מסמך). ככל שהאינדקס עשיר בממדים — כך יותר סוגי שאלות ייענו.
- **השאלה מגיעה אחר כך** ופוגשת אינדקס מוכן: (1) תשובה מהירה, (2) שאילתה צולבת בין מסמכים שנקלטו בזמנים שונים, (3) עומק — כי כל המסמכים כבר מעובדים.

### אנלוגיית הספרייה

ספרנית מקטלגת כל ספר שמגיע — לא לפי שאלה ספציפית, אלא לפי כל ממד שמישהו עשוי לחפש לפיו. הקורא מגיע אחר כך עם שאלה, והקטלוג מפנה אותו. **הקטלוג חייב להיות עשיר בממדים כי אינו יודע מראש מה ישאלו.**

---

## 2. תהליך א׳: עיבוד מרוכז ואינדוקס (Bedrock Native)

הקלט: אצוות PDF ב-S3 source bucket. הפלט: **Bedrock Knowledge Base** עם chunks + metadata + embeddings מסונכרנים בOpenSearch.

**Bedrock טיפול אוטומטי** בשלבים 2.1–2.5 (chunking, embedding, metadata filtering). משימת הarchitecture: הגדרת metadata schema + custom chunking rules + סינון נספחים.

### 2.0 קליטה ומניפסט (Bedrock Data Source Configuration)

כל PDF עולה ל-S3 source bucket. **Bedrock ממונע אוטומטית** (sync job) לקליטה, chunking, וembedding.

**S3 קליטה**:
```
s3://[bucket-name]/documents/incoming/
├── monitoring_2023_holon.pdf
├── survey_historical_tahal_2007.pdf
└── ...
```

**Bedrock Data Source** (בקונסול או boto3):
```python
bedrock = boto3.client("bedrock-agent")
response = bedrock.create_knowledge_base(
    name="holon_qa_knowledge_base",
    roleArn="arn:aws:iam::[account]:role/bedrock-kb-role",
    knowledgeBaseConfiguration={
        "type": "VECTOR",
        "vectorKnowledgeBaseConfiguration": {
            "embeddingModelArn": "arn:aws:bedrock:[region]::foundation-model/amazon.titan-embed-text-v1"
        }
    }
)
kb_id = response["knowledgeBase"]["id"]

# הוסף data source
bedrock.create_data_source(
    knowledgeBaseId=kb_id,
    name="holon_s3_documents",
    dataSourceConfiguration={
        "type": "S3",
        "s3Configuration": {
            "bucketArn": "arn:aws:s3:::holon-documents",
            "inclusionPrefixes": ["documents/incoming/"]
        }
    }
)
```

**Bedrock metadata schema** (מהגדרת Data Source):
```json
{
  "document_name": {"type": "string"},
  "report_date": {"type": "date"},
  "report_type": {"type": "string", "enum": ["monitoring", "remediation_followup", "sampling", "annual", "historical_survey", "other"]},
  "preparing_org": {"type": "string"},
  "subject_entity": {"type": "string"},
  "area_canonical": {"type": "string"},
  "city_canonical": {"type": "string"},
  "street_or_site": {"type": "string"},
  "contaminant_groups_canonical": {"type": "string[]"},
  "contaminants_canonical": {"type": "string[]"},
  "aquifer_names": {"type": "string[]"},
  "monitoring_wells": {"type": "string[]"},
  "extraction_confidence": {"type": "float"},
  "source_page": {"type": "int"}
}
```

```
catalog/
├── documents_manifest.jsonl      # שורה אחת לכל מסמך — מצב, hash, מטא-דאטה
└── ingestion_log.jsonl           # לוג הרצות — מתי, מה עובד, מה כשל
```

**עקרונות קליטה**:
- **קליטה אוטומטית**: העלאת PDF למאגר-המקור מפעילה קליטה (זיהוי-סוג  — חילוץ  — סינון  — נתוח  — מיצוי  — אינדוקס) **ללא התערבות ידנית**.
- **הפניית-מקור נשמרת**: לכל מסמך נשמרת הפניה למיקום המקור (נתיב במאגר + שם קובץ) — תנאי לייחוס מקור בתשובות.
- **כשל-והמשך (fail-and-continue)**: קובץ פגום / מוגן-סיסמה / ללא טקסט-בר-חילוץ  — נרשם ביומן עם סיבה, והקליטה **ממשיכה** לשאר הקבצים. אצווה לא נעצרת בגלל מסמך אחד.
- **סנכרון על עדכון/הסרה**: מסמך שעודכן או הוסר ממאגר-המקור  — האינדקס מסונכרן כך שישקף את המצב העדכני (ראה אידמפוטנטיות ו-`superseded_by`).
- **שימור עברית RTL**: כל שרשרת העיבוד שומרת על טקסט עברי תקין (כיווניות RTL, תווים מיוחדים).

**רשומת מסמך ב-`documents_manifest.jsonl`**:

```json
{
  "doc_id": "sha256:a1b2c3...",
  "source_uri": "store://bucket/incoming/monitoring_2023_holon.pdf",
  "filename": "monitoring_2023_holon.pdf",
  "sha256": "a1b2c3...",
  "ingested_at_utc": "2026-06-14T12:00:00Z",
  "status": "indexed",
  "page_count": 23,
  "language": "he",

  "doc_type": "monitoring",
  "stages": {
    "content_type_detected": true,
    "text_extracted": true,
    "appendices_filtered": true,
    "chunked": true,
    "entities_extracted": true,
    "indexed": true
  },
  "stats": {
    "pages_extracted": 14, "pages_skipped": 9,
    "chunk_count": 31, "facts_extracted": 88,
    "ocr_pages": 0, "extraction_confidence_min": 0.97
  },
  "superseded_by": null
}
```

**אידמפוטנטיות (קריטי)**: `doc_id` = SHA-256 של תוכן הקובץ. מסמך שכבר אונדקס (אותו hash) — **מדולג**. גרסה מעודכנת (תוכן שונה)  — hash חדש  — רשומה חדשה, והישנה מסומנת `superseded_by`.

**סוגי מסמכים (`doc_type`)** — אנומרציה סגורה הניתנת להרחבה:
`monitoring` (ניטור) | `remediation_followup` (מעקב שיקום) | `sampling` (דיגום) | `annual` (דוח שנתי) | `historical_survey` | `permit_license` | `enforcement` | `other`

---

### 2.1 זיהוי סוג-תוכן וחילוץ טקסט (Preprocessing לפני Bedrock)

**Bedrock לא מטפל ב-OCR נative.** משימת preprocessing (לפני העלאה ל-S3):

| מצב עמוד | פעולה | יעד |
|----------|-------|-----|
| **דיגיטלי** (טקסט בר-חילוץ) | `pdftotext -layout` ישירות | upload PDF כ-מסמך דיגיטלי |
| **סרוק / איכות נמוכה** | OCR עברית (`Tesseract-heb` locally) + שמירת PDF + טקסט OCR | upload PDF + OCR-text metadata לBedrock |

**Workflow preprocessing**:
```python
import subprocess, json

def preprocess_pdf(pdf_path):
    # 1. בדיקה: דיגיטלי או סרוק?
    text = subprocess.run(["pdftotext", "-", pdf_path], capture_output=True).stdout.decode()
    if len(text.strip()) > 100:
        # דיגיטלי — העלה ישירות
        return {"doc_id": hash_pdf(pdf_path), "type": "digital", "text": text}
    else:
        # סרוק — הפעל OCR
        ocr_text = subprocess.run(["tesseract", pdf_path, "-l", "heb", "-"], capture_output=True).stdout.decode()
        if len(ocr_text.strip()) < 50:
            return {"doc_id": hash_pdf(pdf_path), "type": "needs_ocr", "confidence": 0.0}
        return {"doc_id": hash_pdf(pdf_path), "type": "scanned_with_ocr", "text": ocr_text, "confidence": 0.85}

# metadata שיישמר ב-Bedrock
metadata = {
    "document_name": os.path.basename(pdf_path),
    "extraction_confidence": preprocess_pdf(pdf_path)["confidence"],
    "extraction_method": preprocess_pdf(pdf_path)["type"]
}
```

**Bedrock Preprocessing Configuration** (בקונסול Data Source):
- **Chunking**: Bedrock default (800 tokens, 200-token overlap)
- **Custom metadata extraction**: **Bedrock Parsing (Beta)** — מחלץ טקסט + metadata באופן חכם
- **Metadata filtering**: כל PDF שנטען מקבל את שדות `document_name`, `extraction_confidence`, וכו׳ כמתואר בـ§2.0

---

### 2.2 סינון תוכן וזיהוי נספחים לא-רלוונטיים (Preprocessing Script)

**Bedrock לא מטפל בסינון נספחים נatively.** Preprocessing script Python בStage 0 צריך לסנן דוחות-מעבדה וyומני-שדה **לפני העלאה ל-S3**.

#### Preprocessing logic

```python
import PyPDF2

def filter_appendices(pdf_path):
    """הסר דוחות מעבדה / יומני שדה, החזר PDF מסונן."""
    
    reader = PyPDF2.PdfReader(pdf_path)
    writer = PyPDF2.PdfWriter()
    toc_extracted = False
    appendix_start = None
    
    # שלב 1: חלץ תוכן עניינים אם קיים
    toc_pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text().lower()
        if "תוכן עניינים" in text or "contents" in text:
            toc_pages.append(i)
            # חפש שורות עם "נספח" / "Appendix"
            if "נספח" in text or "appendix" in text:
                for line in text.split("\n"):
                    if "נספח" in line:
                        # חלץ מספר עמוד (~עמ' NN)
                        parts = line.split()
                        if any(p.isdigit() for p in parts):
                            appendix_start = int([p for p in parts if p.isdigit()][-1])
    
    # שלב 2: זהה גבולות נספח
    if appendix_start is None:
        # חיפוש ידני: טבלה צפופה (>30 שורות) + כותרות
        for i, page in enumerate(reader.pages[14:], start=14):  # חפש מעמוד 15
            text = page.extract_text()
            lines = text.split("\n")
            if len(lines) > 30 and any(kw in text.lower() for kw in ["method", "unit", "result", "lab", "תוצאות", "בדיקה"]):
                appendix_start = i
                break
    
    # שלב 3: הוסף עמודים לפני נספח
    if appendix_start is None:
        appendix_start = len(reader.pages)  # אין נספח — כללו את הכל
    
    for i in range(min(appendix_start, len(reader.pages))):
        writer.add_page(reader.pages[i])
    
    # שלב 4: שמור + metadata
    filtered_path = pdf_path.replace(".pdf", "_filtered.pdf")
    with open(filtered_path, "wb") as f:
        writer.write(f)
    
    return {
        "filtered_path": filtered_path,
        "pages_extracted": appendix_start,
        "pages_skipped": len(reader.pages) - appendix_start,
        "appendix_detected": appendix_start < len(reader.pages)
    }
```

#### מבנה טיפוסי של מסמך (מאפיון אמיתי)

| חלק | עמודים אופייניים | למיצוי? |
|-----|------------------|---------|
| עמוד שער + תוכן עניינים | 1–2 | כן (metadata) |
| גוף: רקע, מיקום, ניתוח, טבלאות מעקב מסכמות, סיכום | 3–14 | **כן** |
| **נספחים — דוחות מעבדה** (Aminolab / ALS, טבלאות צפופות) | 15+ | **לא — דלג** |

**Bedrock Upload Pipeline**:
```bash
for pdf in documents/incoming/*.pdf; do
  python filter_appendices.py "$pdf"  # יוצר _filtered.pdf
  aws s3 cp "${pdf%.*}_filtered.pdf" s3://holon-documents/documents/incoming/
done
```

#### אותות זיהוי (משולבים — לעולם לא אות בודד)

1. **תוכן עניינים (אות עדיף)**: אם קיים — מזהים בו את הסעיף "דוחות מעבדה"/"נספח" וקובעים את **טווח העמודים** שלו. אלו העמודים לדילוג.
2. **טבלה צפופה ללא הקשר**: עמוד עם טבלה של **>30 שורות** ושמות-עמודות כמו `Method`, `Unit`, `Result`, `Laboratory sample ID` — סבירות גבוהה לדוח-מעבדה גולמי.
3. **כותרות אופייניות (התאמה גמישה)**: "Analytical Results", "Test Report", "Certificate of Analysis" / "תוצאות מעבדה", "תעודת בדיקה", "דוח בדיקה", "נספח", "יומן שדה" — כולל וריאציות.
4. **עיתוי במסמך**: נספח החל מעמ' 15+ במסמך בן 15–25 עמ' + עמידה באותות 2–3  — סביר דוח-מעבדה.
5. **עמודים סרוקים בסוף מסמך דיגיטלי**: טפסים חוזרים / כתב-יד  — מועמדים ל**יומני שדה**.

#### כללי הכרעה

- **הבחנה קריטית**: טבלאות מסכמות **בגוף** (ערכי מזהמים לאורך זמן) = רלוונטיות למיצוי; טבלאות גולמיות **בנספח** = לדילוג. אל תבלבל ביניהן.
- **מפות / גרפים / איורים**: לחלץ **רק את הכותרת/כיתוב + מספר** (למשל "מפה 1 — מיקום תחנת דלק X"), **לא** את תוכן התמונה. לשמור רשומה (סוג, מספר, עמוד) כמטה-דאטה.
- **ביטחון נמוך  — בדיקה ידנית**: אם גבול-נספח אינו ודאי — **לסמן לבדיקה ידנית, לא לדלג אוטומטית**. עדיף לבזבז מיצוי מאשר לאבד מידע רלוונטי.
- **שקיפות**: לכל מסמך נשמר אילו חלקים מוצו ואילו דולגו (סוג-נספח + טווח-עמודים) — ב-`documents_manifest.jsonl`.

> **הערת אפיון**: בפיילוט שנבדק לא נמצאו יומני-שדה סרוקים (כל התוכן דיגיטלי); הנספח הלא-רלוונטי הדומיננטי היה דוחות-מעבדה. הכלל ליומני-שדה נשמר בכל זאת — אזורים/ארגונים אחרים עשויים לכלול אותם.

---

### 2.3 נתוח (Bedrock Native Chunking)

**Bedrock מטפל באופן אוטומטי** בnunking כשיזונה סינכרון עם S3. הconfiguration הbutool הוא בData Source setup:

```python
bedrock.update_data_source(
    knowledgeBaseId=kb_id,
    dataSourceId=source_id,
    dataSourceConfiguration={
        "type": "S3",
        "s3Configuration": {
            "bucketArn": "arn:aws:s3:::holon-documents",
            "inclusionPrefixes": ["documents/incoming/"],
            "chunkingConfiguration": {
                "chunkingStrategy": "FIXED_SIZE",
                "fixedSizeChunkingConfiguration": {
                    "maxTokens": 800,
                    "overlapPercentage": 25
                }
            }
        }
    }
)
```

| פרמטר | ערך Bedrock | הערה |
|-------|-----------|------|
| גודל chunk | 800 tokens (~ 500–800 מילים) | Bedrock default, מתאים |
| חפיפה | 25% (200 tokens) | Bedrock מומלץ, מונע חיתוך |
| גבול נתוח | Bedrock auto (פסקה/כותרת) | הύnauto-detection, לא ניתן לשינוי בנתחינו |
| טבלה מסכמת | **שומר שלם** אם בגוף (סننו בphase 2.2) | אין risk של חיתוך |

כל chunk נקבל **automatically**:
- `chunk_id` (Bedrock generated hash)
- הטקסט המקורי
- `source_page` (Bedrock מחלץ מPDF metadata)
- `document_name` (מmetadata)

---

### 2.4 מיצוי ישויות ועובדות (Optional: Bedrock Parsing + Parallel Extraction)

**Bedrock אינו מטפל extraction דיאגרמטי** (קידוחים, ממצאי-זיהום, וכו׳) native. שתי אפשרויות:

#### אפשרות א׳: Bedrock Parsing (Beta)
Bedrock Parsing מחלץ טקסט עברי + layout intelligent, אך לא מחלץ structured facts. אם בחרת ברמה גבוהה של QA (יתברר בphase צילום), השתמש בפרסינג:

```python
bedrock_runtime = boto3.client("bedrock-runtime")
response = bedrock_runtime.invoke_model(
    modelId="amazon.nova-lite-v1:0",
    body=json.dumps({
        "documents": [
            {"format": "pdf", "name": "monitoring_2023.pdf", "source": {"bytes": pdf_bytes}}
        ]
    })
)
parsed_output = json.loads(response["body"].read())
```

#### אפשרות ב׳: Parallel Extraction Pipeline (Recommended)
מקביל לBedrock knowledge base, הרץ extraction diagrammatic עם Claude Opus — כמפורט ב-`GENERIC_PDF_EXTRACTION_AND_RETRIEVAL.md §2`:

```python
# שלב ב-parallel למעלה ל-Bedrock:
# <bdi>PDF → Claude</bdi> Opus sub-agent → facts JSON
# facts: קידוחים, ממצאי-זיהום, מתקנים, מגמות, ציטוטים (A–E אמינות)

extracted_facts = claude_extract_entities(pdf_text, persona="hydrogeologist")
# → facts.jsonl (stored separately, not in Bedrock)
```

**עקרון**: Bedrock משמש למיצוי text + vector retrieval. Structured facts (קידוחים, מזהמים) נשמרו ב-**SQLite / DuckDB sidebar** לסינון מדויק בphase שליפה (§3.2).

**כלל אי-המצאה**: שדה שאינו ניתן לחילוץ  — `"unknown"`, **לא ממציאים**.

---

### 2.5 שכבת המטה-דאטה והאינדוקס — לב המערכת

זהו החלק הקריטי. **האינדקס חייב ללכוד כל ממד שאילתה אפשרי מראש.** להלן סכמת המטה-דאטה המלאה — מתועדת, סגורה-ככל-הניתן, וניתנת להרחבה.

#### עקרון הנרמול הקנוני (חל על כל שדה רב-גרסתי)

מונחים נכתבים בגרסאות שונות. לכל שדה כזה נשמרים **שני ערכים**:
- `*_canonical` — הערך הקנוני המנורמל (לסינון אחיד)
- `*_original[]` — כל הגרסאות המקוריות כפי שהופיעו (לחיפוש מילולי)

דוגמאות: `PFAS` / `חומרים פלואורואלקיליים` / `PFOS,PFOA`  — canonical=`PFAS`. `אזה"ת חולון` / `אזור תעשייה חולון`  — canonical=`אזור תעשייה חולון`. `TCE` / `טריכלורואתילן` / `Trichloroethylene`  — canonical=`Trichloroethylene`.

#### א. פרטי המסמך

| שדה | הערה |
|-----|------|
| `document_name` | שם המסמך |
| `report_date` | תאריך הדוח |
| `report_type` | ניטור / מעקב-שיקום / דיגום / שנתי / אחר (= `doc_type`) |
| `author_names[]` | שמות המחברים |
| `preparing_org` | **הגוף שהמחברים מטעמו** — חברת העריכה/הכנה |
| `subject_entity` | **הגורם שהדוח עוסק בו** (למשל "דלק הצבי", "סונול", "פז הסיירים") |

> **הבחנה קריטית**: `preparing_org` (מי כתב את הדוח — יועץ/חברת-ייעוץ) שונה מ-`subject_entity` (על מי/מה הדוח). שני שדות נפרדים. שאלה "אילו דוחות הכין יועץ X?" שונה מ"אילו דוחות עוסקים בתחנת Y?".

#### ב. גיאוהידרולוגיה

| שדה | דוגמה |
|-----|-------|
| `aquifer_names[]` | אקוויפר החוף |
| `sub_aquifers[]` | תת-אקוויפר A/B/C |
| `aquifer_units[]` | יחידות אקוויפריות |
| `monitoring_wells[]` | שמות קידוחי ניטור |
| `production_wells[]` | שמות קידוחי הפקה |

#### ג. זיהום (עם נרמול קנוני)

| שדה | דוגמה | הערה |
|-----|-------|------|
| `contaminant_groups_canonical[]` | מזהמי דלק, ממסים מוכלרים, PFAS | קבוצות מזהמים — מנורמל |
| `contaminants_canonical[]` | Benzene, Toluene, TCE, PCE | מזהם ספציפי — מנורמל |
| `*_original[]` | "בנזן", "BTEX", "פחממנים" | גרסאות מקור (כינויים, ר"ת, איות חלופי) |

#### ד. מיקום + היררכיה (ממד שליפה מרכזי)

מאפיין המיקום הוא **דרך השליפה המרכזית** (בחירה על מפה / שם-אזור). נשמרת **היררכיה**:

```
אזור / אזור-תעשייה  —  עיר/יישוב  —  רחוב / שם-אתר  —  נקודת-ניטור / קידוח
```

| שדה | דוגמה |
|-----|-------|
| `area_canonical` | אזור תעשייה חולון |
| `city_canonical` | חולון |
| `street_or_site[]` | רחוב המלאכה / "תחנת דלק מרכבות האש" |
| `monitoring_points[]` | מזהי בארות/נקודות ניטור |
| `coordinates` | קווי אורך/רוחב או **רשת ישראל ITM**, אם קיימים |
| `*_original[]` | גרסאות מקור (אזה"ת חולון…) |

**כלל היררכיה**: סינון ברמה גבוהה (אזור) **כולל אוטומטית** את כל הרמות שתחתיו (עיר —רחוב —נקודה). מיקום שלא זוהה  — מסומן מפורשות, **לא משויך מיקום שגוי**. קואורדינטות נחשפות כך שניתן להציגן כסמן על מפה.

#### ה. ממדים נגזרים (מהעובדות)

`content_type` (finding/trend/quote/recommendation/hydrogeology) · `evidence_class` (A–E) · `concentration`/`percent_of_standard`/`crossed_standard` · `date`/`year`/`period` · `confidence` (HIGH/MEDIUM/LOW לייחוס-מקור) · `embedding` (וקטור סמנטי).

#### מבנה האחסון — Bedrock Knowledge Base (Managed)

```
Bedrock Knowledge Base (kb_id: "...")
├── Vector Store (OpenSearch)
│   ├── chunks (800 tokens) with embeddings (Titan or Claude)
│   └── metadata filters (area_canonical, report_type, etc.)
│
└── Parallel Sidebar (SQLite / DuckDB — optional)
    └── structured_facts.db
        ├── boreholes table
        ├── contamination_findings table
        ├── facilities_suspected table
        └── trends table
```

**Bedrock Native Storage** (OpenSearch):
- **Chunks**: טקסט + embedding (Titan-embed-text-v1 או custom)
- **Metadata**: `document_name`, `report_date`, `report_type`, `preparing_org`, `subject_entity`, `area_canonical`, `city_canonical`, `contaminant_groups_canonical`, `aquifer_names`, `monitoring_wells`, `extraction_confidence`, `source_page`
- **Retrieval**: Bedrock performs hybrid search (vector similarity + metadata filters)

**Sidebar SQLite** (עבור structured queries):
```sql
CREATE TABLE contamination_findings (
    finding_id TEXT PRIMARY KEY,
    chunk_id TEXT,
    well_name TEXT,
    parameter_canonical TEXT,
    concentration FLOAT,
    percent_of_standard INT,
    report_date DATE,
    area_canonical TEXT,
    evidence_class CHAR(1),
    FOREIGN KEY (chunk_id) REFERENCES bedrock_chunks(id)
);

CREATE INDEX idx_area ON contamination_findings(area_canonical);
CREATE INDEX idx_parameter ON contamination_findings(parameter_canonical);
```

**שלוש שכבות retrieval** (Bedrock + Sidebar):
1. **Vector Search** (Bedrock native): "מה קרה בקידוח X?"  — relevant chunks
2. **Metadata Filter** (Bedrock native): "רק בחולון" + "report_type=monitoring"
3. **Structured Query** (SQLite sidebar, optional): "כל הממצאים עם `percent_of_standard>100` בTCE"  — facts table

**Sync Bedrock ↔ Sidebar**:
```python
# בכל סינכרון Knowledge Base:
def sync_sidebar_on_kb_sync(kb_id):
    # קבל chunks מ-Bedrock
    chunks = bedrock.retrieve(kb_id, query_string="*", maxResults=1000)
    
    # חלץ structured facts עם Claude
    for chunk in chunks:
        facts = claude_extract_facts(chunk["text"])
        for fact in facts:
            insert_into_sqlite(fact, chunk["chunk_id"])
```

---

## 3. תהליך ב׳: שליפה וסינתזה (Bedrock Retrieve + Opus Synthesis)

```
שאלה  — [3.1 נתוח-כוונה]  — [3.2 Bedrock Retrieve + Sidebar Query]  — [3.3 הרכבת-קונטקסט]  — [3.4 Claude Opus]  — תשובה
```

### 3.1 נתוח כוונת השאלה

Claude קצר (משימת-auxiliary) מתרגם שאלה לformat שקל לretrieval:

```python
from anthropic import Anthropic

client = Anthropic()

def parse_query(question):
    """תרגם שאלה חופשית ל-filters + keywords."""
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""Parse this query into filters and keywords for a Bedrock knowledge base retrieval:

Question: {question}

Return JSON with:
- area_canonical (if location mentioned)
- report_type (if type mentioned: monitoring/remediation/etc)
- keywords (list of search terms)
- semantic_query (full question for vector search)
- requires_recent (bool)"""
        }]
    )
    return json.loads(response.content[0].text)
```

### 3.2 שליפה היברידית (Bedrock Native + Sidebar)

```python
def hybrid_retrieve(kb_id, parsed_query):
    """Bedrock vector search + SQLite structured filters."""
    
    bedrock_agent = boto3.client("bedrock-agent-runtime")
    
    # שלב א׳: Bedrock vector + metadata filters
    filters = {}
    if parsed_query.get("area_canonical"):
        filters["area_canonical"] = parsed_query["area_canonical"]
    if parsed_query.get("report_type"):
        filters["report_type"] = parsed_query["report_type"]
    
    response = bedrock_agent.retrieve(
        knowledgeBaseId=kb_id,
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": 20,
                "overrideSearchType": "HYBRID"  # vector + keyword
            }
        },
        searchQuery=parsed_query["semantic_query"],
        filters=filters
    )
    
    retrieved_chunks = response["retrievalResults"]
    
    # שלב ב׳: Sidebar SQLite — if high-specificity query (structured facts)
    if any(kw in parsed_query["keywords"] for kw in ["percent_of_standard", "concentration", "well"]):
        sidebar_results = query_sidebar_db(parsed_query)  # SQL query
        return {"chunks": retrieved_chunks, "facts": sidebar_results}
    
    return {"chunks": retrieved_chunks, "facts": []}

def query_sidebar_db(parsed_query):
    """Query structured facts if available."""
    import sqlite3
    conn = sqlite3.connect("sidebar.db")
    query = "SELECT * FROM contamination_findings WHERE 1=1"
    if parsed_query.get("area_canonical"):
        query += f" AND area_canonical = '{parsed_query['area_canonical']}'"
    if "TCE" in parsed_query["keywords"]:
        query += " AND parameter_canonical IN ('TCE', 'Trichloroethylene')"
    results = conn.execute(query).fetchall()
    conn.close()
    return results
```

**Bedrock Metadata Filters** (תחת retrieval):
```python
filters = {
    "area_canonical": "אזור תעשייה חולון",
    "report_type": "monitoring",
    "extraction_confidence": {"gte": 0.8}  # confidence filtering
}
```

### 3.2ב שליפה לפי מיקום ומפה (Bedrock Native)

```python
def location_based_retrieve(kb_id, area_name):
    """בחר אזור  — החזר כל המסמכים בהיררכיה."""
    
    bedrock_agent = boto3.client("bedrock-agent-runtime")
    
    # normalize area_name (אזה"ת חולון  — אזור תעשייה חולון)
    area_canonical = normalize_location(area_name)
    
    # Bedrock filter עם היררכיה
    response = bedrock_agent.retrieve(
        knowledgeBaseId=kb_id,
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 100}},
        filters={"area_canonical": area_canonical}
    )
    
    return response["retrievalResults"]
```

### 3.3 הרכבת קונטקסט (Bedrock Context Assembly)

Bedrock Retrieve מחזיר chunks עם metadata. Claude מרכיב אותם לLLM-consumable format:

```python
def assemble_context(retrieved_chunks, sidebar_facts, token_budget=2000):
    """הרכם את chunks + facts לקונטקסט תחת תקציב-טוקנים."""
    
    context = "## עובדות מובנות (מmeta-data סינון)\n"
    context += "| מזהם | קידוח | ריכוז | % מתקן | תאריך | מקור | אמינות |\n"
    context += "|------|-------|-------|--------|-------|------|--------|\n"
    
    tokens_used = 0
    for fact in sidebar_facts[:10]:  # top-10 facts
        row = f"| {fact['parameter']} | {fact['well']} | {fact['concentration']} µg/L | {fact['percent_of_standard']}% | {fact['date']} | {fact['source_doc']} | {fact['evidence_class']} |\n"
        if tokens_used + len(row.split()) > token_budget * 0.2:
            break
        context += row
        tokens_used += len(row.split())
    
    context += "\n## קטעי טקסט מקוריים\n"
    for chunk in retrieved_chunks[:10]:  # top-10 chunks
        excerpt = f"### [{chunk['metadata']['document_name']}], עמ' {chunk['metadata'].get('source_page', '?')}\n\"{chunk['content'][:500]}...\"\n\n"
        if tokens_used + len(excerpt.split()) > token_budget:
            break
        context += excerpt
        tokens_used += len(excerpt.split())
    
    return context
```

**Token Budget** (ברירת-מחדל עבור Opus):
- Input: 4K tokens (200K context window, חלק לhistory)
- Output: 2K tokens
- Allocated for context: ~1.5K tokens (~70% chunks, ~20% facts, ~10% reserve)

### 3.4 סינתזה (Claude Opus via Bedrock Agents)

**שתי אפשרויות**:

#### אפשרות א׳: Bedrock Agents (fully managed)
```python
def bedrock_agent_invoke(kb_id, question):
    """Bedrock Agent orchestrates retrieval + synthesis."""
    
    agent_runtime = boto3.client("bedrock-agent-runtime")
    response = agent_runtime.invoke_agent(
        agentId="your-agent-id",  # צריך ליצור agent בקונסול
        agentAliasId="TSTALIASID",
        sessionId="session-1",
        inputText=question
    )
    
    return response["output"]
```

#### אפשרות ב׳: Manual Synthesis (claude-opus-4-8 API)
```python
def manual_synthesis(question, context, model="claude-opus-4-8"):
    """Claude Opus סינתזה עם system prompt."""
    
    client = Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=1500,
        system="""אתה הידרוגיאולוג מומחה בניטור מי-תהום בישראל. 
תשובה בעברית וברורה.
קביעות חייבות להיות מצוטטות מהמסמכים.
אם מידע חסר — אמור "המידע אינו זמין במסמכים שנשלפו".
הצע confidence level (HIGH/MEDIUM/LOW) לייחוס-מקור.
""",
        messages=[{
            "role": "user",
            "content": f"""שאלה: {question}

קונטקסט (מBedrock Knowledge Base):
{context}

כתוב תשובה עמוקה עם ציטוטים מפורשים.
"""
        }]
    )
    
    return response.content[0].text
```

**System Prompt קריטי**:
- ✓ Persona: הידרוגיאולוג מומחה
- ✓ ציטוט חובה: כל קביעה  — document_name + עמוד
- ✓ אי-המצאה: "לא זמין" לא "לא ידוע"
- ✓ Confidence levels: HIGH/MEDIUM/LOW
- ✓ שפה: עברית בלבד

---

## 4. תרשים זרימה מלא (Bedrock Edition)

```
═════════ שלב 0: Preprocessing (Local) ═════════
  PDFs (מחשב מקומי)
     │ 2.1 preprocess_pdfs.py
     │   ├─ דיגיטלי: pdftotext ישירות
     │   └─ סרוק: Tesseract-heb + extraction_confidence
     │ 2.2 filter_appendices.py
     │   ├─ חלץ TOC
     │   └─ סנן דוחות-מעבדה  — _filtered.pdf
     │ 2.0 metadata extraction
     │   └─ document_name, report_date, preparing_org, subject_entity, וכו׳
     ▼
  Filtered PDFs + <bdi>metadata → S3</bdi> bucket

═════════ שלב 1: Bedrock Knowledge Base (Managed) ═════════
  S3 bucket (s3://holon-documents/documents/incoming/)
     │ Bedrock Data Source Sync (automatic or scheduled)
     │   ├─ Chunking: Fixed-Size 800 tokens, 25% overlap
     │   ├─ Embedding: Titan Embed (amazon.titan-embed-text-v1)
     │   └─ Metadata indexing: 7 filters (area_canonical, report_type, וכו׳)
     ▼
  Bedrock Knowledge Base (kb_id: "...")
  └─ OpenSearch Vector Store
     ├─ chunks with embeddings
     └─ metadata filters

═════════ שלב 2: Sidebar SQLite (Optional) ═════════
  (In parallel with Bedrock sync)
  Chunks from <bdi>Bedrock → Claude</bdi> extraction → sidebar.db
  ├─ contamination_findings table
  ├─ boreholes table
  └─ facilities_suspected table

═════════ תהליך ב׳: שליפה + סינתזה (ON-DEMAND) ═════════
  שאלה (עברית חופשית)
     │ 3.1 parse_query()
     │   └─ Claude Opus aux: extract filters + keywords
     │ 3.2 hybrid_retrieve()
     │   ├─ Bedrock vector search + metadata filters
     │   └─ Sidebar SQL query (if high-precision)
     │ 3.3 assemble_context()
     │   └─ facts table + retrieved chunks (token-budgeted)
     │ 3.4 synthesis
     │   └─ Claude Opus: answer with citations
     ▼
  תשובה מעמיקה, מצוטטת, בעברית + confidence levels
```

---

## 5. עקרונות תכנון (Design Invariants)

### Core Principles

1. **אינדוקס רחב מראש** — כל ממד פוטנציאלי בmetadata. הוספת ממד = re-sync בBedrock (מתוקתק).
2. **אטריבוציה מקצה-לקצה** — <bdi>chunk→source_document_name</bdi>+source_page; Bedrock משמר זאת automatic.
3. **Idempotence בpreprocessing** — קובץ מסונן = deterministic filename; S3 upload עם versioning.
4. **הפרדת batch/on-demand** — preprocessing local, Bedrock sync scheduled/event-triggered (לא בזמן-שאלה).
5. **Hybrid retrieval** — Bedrock vector search + metadata filters משולבים.
6. **Canonical + Original** — כל שדה רב-גרסתי (`area_canonical` + `area_original[]`).
7. **Preparing Org ≠ Subject** — `preparing_org` (יועץ) ≠ `subject_entity` (תחנה דלק).
8. **Location Hierarchy** — <bdi>area→city</bdi>→street→point; סינון-אזור כולל תת-רמות.
9. **Graceful Failure** — סרוק ללא OCR זמין  — `status: "needs_ocr"` (לא דלג שקט).
10. **Evidence flowing** — אם יש sidebar facts עם evidence_class A/B  — דירוג גבוה בretrieval.
11. **Non-hallucination** — "לא זמין במידע שנשלף" בלבד (לא creative answers).
12. **Document Filtering** — דוחות-מעבדה + יומני-שדה מסוננים קודם ל-upload.

### Bedrock-Specific Invariants

13. **S3 as Source of Truth** — preprocessed PDFs בS3 הם primary; Bedrock syncs לא כוללות logic
14. **Metadata immutable after indexing** — לא ניתן לשנות metadata של chunk אחרי sync; כדי לתקן  — delete + re-upload PDF
15. **Vector search + filters always both** — Bedrock doesn't support "vector-only" retrieval (filter-less queries are possible but not recommended for this use case)

---

## 6. מדרגיות, הרשאות ונראות (Bedrock)

### מדרגיות (פיילוט חולון  — 18 אזורים)

Bedrock Knowledge Bases נועדו לקנה-מידה:
- **אזור חדש** = Data Source חדש (S3 prefix) + אותה metadata schema
  ```python
  bedrock.create_data_source(
      knowledgeBaseId=kb_id,
      name="zone_raanana_documents",
      dataSourceConfiguration={"s3Configuration": {"bucketArn": "...", "inclusionPrefixes": ["raanana/incoming/"]}}
  )
  ```
- **תוספת מסמכים** = upload ל-<bdi>S3 → Bedrock</bdi> sync **אוטומטי** (webhook-based or scheduled)
- **סכמת metadata** זהה לכל אזור — אנומרציות `area_canonical` רק מתרחבות

### הרשאות Bedrock

**מודל הרשאות**:
- S3 bucket: per-zone folders (`holon/`, `raanana/`, וכו׳)
- IAM: role לכל team/user group עם S3 + Bedrock restrict permissions
- Bedrock Agents: access control built-in (no need for sidebar filtering)

**Metadata-based access** (optional extension):
```python
# אם צריך per-user filtering (משתמש רואה רק documents משהוא מוסמך)
# הוסף access_group למטה-דאטה וסנן בretrieval:
response = bedrock.retrieve(
    knowledgeBaseId=kb_id,
    filters={"access_group": current_user_group}
)
```

### נראות ובקרת איכות (Bedrock Native + Custom)

**Bedrock Console**:
- Knowledge Base sync status (✓ succeeded / ✗ failed)
- Indexed document count
- Vector store size
- Query latency metrics

**Custom Monitoring**:
```python
def monitor_sync(kb_id):
    """Check last sync status + document count."""
    import boto3
    bedrock = boto3.client("bedrock-agent")
    
    # Bedrock doesn't expose detailed sync logs yet
    # Workaround: track S3 upload times + query document count
    
    response = bedrock.retrieve(kb_id, "*", maxResults=1)  # count query
    doc_count = response.get("metadata", {}).get("total_documents", 0)
    print(f"Knowledge Base has {doc_count} documents indexed")
```

**Quality Flags**:
- `extraction_confidence < 0.80` (low OCR quality) → flag document
- Metadata completeness check (חובה: `area_canonical`, `report_type`)
- Spot-check retrieval: "אם חיפשתי על X, האם קיבלתי relevant chunks?"

**Logs**:
- S3 upload logs (CloudWatch)
- Bedrock sync events (CloudWatch)
- Retrieval query logs (custom logging בapi)

---

## 7. Bedrock Configuration Decisions

| # | החלטה | אפשרויות | ברירת-מחדל בBedrock |
|---|-------|----------|-------------------|
| 1 | S3 Source Bucket | קיים / חדש | קיים — `s3://holon-documents/documents/incoming/` |
| 2 | OCR עברית (preprocessing) | Tesseract-heb / Google Vision / ABBYY | Tesseract-heb (local preprocessing) |
| 3 | Bedrock Embedding Model | Titan Embed (Bedrock native) / Custom | `amazon.titan-embed-text-v1` |
| 4 | Vector Store | OpenSearch (Bedrock managed) / External | OpenSearch (Bedrock default) |
| 5 | Chunking Strategy | Fixed-Size (800) / Hierarchical / Full doc | Fixed-Size 800 tokens + 25% overlap |
| 6 | Metadata Filtering | Bedrock native (attribute-based) | כל 7 השדות: area_canonical, report_type, וכו׳ |
| 7 | Synthesis Model | Claude Opus / Sonnet (via Bedrock) | Claude Opus 4.8 (עומק) |
| 8 | Bedrock Agents | Enabled (fully managed) / Manual API | Manual (full control over prompt) |
| 9 | Sidebar DB | SQLite (structured facts) / None | SQLite (recommended for high-precision queries) |

**Bedrock AWS Setup** (required):
```bash
# 1. Enable Bedrock in console + Claude API access
# 2. Create S3 bucket
aws s3 mb s3://holon-documents

# 3. Create IAM role
cat > bedrock-kb-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": "bedrock:*", "Resource": "*"},
    {"Effect": "Allow", "Action": "s3:*", "Resource": "arn:aws:s3:::holon-documents/*"}
  ]
}
EOF
aws iam create-role --role-name bedrock-kb-role --assume-policy-document file://trust-policy.json
aws iam put-role-policy --role-name bedrock-kb-role --policy-name bedrock-s3 --policy-document file://bedrock-kb-policy.json

# 4. Create Knowledge Base (via boto3 — see §2.0)
python create_knowledge_base.py

# 5. Upload preprocessing script to local
# — filter_appendices.py (§2.2)
# — preprocess_pdfs.py (§2.1)
```

**מסלול-התחלה עם Bedrock**:
1. ✓ Preprocessing local: OCR + סינון-נספחים + עלאה ל-S3
2. ✓ Bedrock Knowledge Base: קליטה + chunking + embedding (native)
3. ✓ Sidebar SQLite: structured facts (optional, parallel)
4. ✓ Bedrock Retrieve: vector search + metadata filters
5. ✓ Claude Opus: synthesis with system prompt

**עלות (הערכה)**:
- S3 storage: ~$0.02 / PDF
- Bedrock Knowledge Base: ~$0.10 per 1K tokens indexed
- Bedrock Retrieve: ~$0.10 per query
- Opus API: ~$0.015 per 1K input tokens
- **Total per query**: ~$0.25–0.50

---

## 8. Checklist — Bedrock Deployment

**שלב 0: AWS Setup**:
- [ ] AWS account עם Bedrock access
- [ ] S3 bucket created: `s3://holon-documents`
- [ ] IAM role עם Bedrock + S3 permissions
- [ ] Claude Opus enabled בBedrock console
- [ ] boto3 installed + AWS credentials configured

**שלב 1: Preprocessing (Local)**:
- [ ] `filter_appendices.py` script כתוב + tested (§2.2)
- [ ] `preprocess_pdfs.py` script כתוב (OCR + metadata extraction, §2.1)
- [ ] 13 PDFs מ-חולון עוברים preprocessing בהצלחה
- [ ] כל PDF עם metadata (preparing_org, subject_entity, area_canonical, וכו׳)
- [ ] דוחות-מעבדה מסוננים — רק גוף המסמך עולה ל-S3
- [ ] extraction_confidence neshomar לכל PDF

**שלב 2: Bedrock Knowledge Base**:
- [ ] Knowledge Base created (boto3, §2.0)
- [ ] Data Source configured (S3 bucket)
- [ ] Metadata schema defined (7 שדות: area_canonical, report_type, וכו׳)
- [ ] Chunking configuration set (800 tokens, 25% overlap)
- [ ] First sync job completed בהצלחה
- [ ] OpenSearch vector store populated (check Bedrock console)
- [ ] Test chunk retrieval: `bedrock.retrieve(kb_id, "בנזן", filters={"area_canonical": "חולון"})`

**שלב 3: Sidebar SQLite (Optional)**:
- [ ] `sidebar.db` created עם tables: contamination_findings, boreholes, facilities
- [ ] Sync script בעבודה: קבל chunks מ-<bdi>Bedrock → extract</bdi> facts → insert to SQLite
- [ ] Test query: `SELECT * FROM contamination_findings WHERE area_canonical = 'חולון' AND percent_of_standard > 100`

**שלב 4: Retrieval API**:
- [ ] `parse_query()` function כתובה (Claude aux, §3.1)
- [ ] `hybrid_retrieve()` function כתובה (Bedrock retrieve + SQL, §3.2)
- [ ] `assemble_context()` function כתובה (context assembly, §3.3)
- [ ] Test query: "מה מצב בנזן בחולון?"  — הוחזרו chunks + facts

**שלב 5: Synthesis**:
- [ ] Claude Opus API key configured
- [ ] `manual_synthesis()` function כתובה (§3.4)
- [ ] System prompt tested (עברית, ציטוט חובה, אי-המצאה)
- [ ] End-to-end test: <bdi>question → Bedrock</bdi> retrieve → context → Opus → Hebrew answer

**שלב 6: QA Validation**:
- [ ] Spot-check: 3–5 queries עם expected citations
- [ ] Verify: ציטוטים מכילים document_name + source_page
- [ ] Verify: אם אין תשובה  — "המידע אינו זמין" (לא hallucination)
- [ ] Verify: location filtering עובד (חולון ≠ תל אביב)
- [ ] Performance: latency < 10 seconds per query
```

---

## 9. Bedrock API Reference & Code Templates

### Minimal Python Integration

```python
import boto3
import json
from anthropic import Anthropic

# Initialize
bedrock = boto3.client("bedrock-agent")
bedrock_runtime = boto3.client("bedrock-agent-runtime")
anthropic_client = Anthropic()

# Constants
KB_ID = "your-kb-id"
MODEL_ID = "claude-opus-4-8"

def retrieve_and_synthesize(question):
    """End-to-end: <bdi>query → Bedrock</bdi> → Claude → answer."""
    
    # 1. Parse question
    parsed = parse_query_with_claude(question)
    
    # 2. Retrieve from Bedrock
    filters = {
        "area_canonical": parsed.get("area_canonical", ""),
        "report_type": parsed.get("report_type", "")
    }
    
    response = bedrock_runtime.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 20}},
        searchQuery=parsed["semantic_query"],
        filters={k: v for k, v in filters.items() if v}
    )
    
    chunks = response["retrievalResults"]
    
    # 3. Assemble context
    context = "\n".join([f"[{c['metadata']['document_name']}, עמ' {c['metadata'].get('source_page', '?')}]\n{c['content']}" for c in chunks[:10]])
    
    # 4. Synthesize with Claude
    synthesis_response = anthropic_client.messages.create(
        model=MODEL_ID,
        max_tokens=1500,
        system="אתה הידרוגיאולוג מומחה. תשובה בעברית. ציטוט חובה מהמסמכים.",
        messages=[{"role": "user", "content": f"שאלה: {question}\n\nקונטקסט:\n{context}"}]
    )
    
    return synthesis_response.content[0].text

def parse_query_with_claude(question):
    """Extract filters from question."""
    aux_response = anthropic_client.messages.create(
        model="claude-opus-4-8",
        max_tokens=200,
        messages=[{"role": "user", "content": f"Extract JSON with area_canonical, report_type, keywords, semantic_query from: {question}"}]
    )
    try:
        return json.loads(aux_response.content[0].text)
    except:
        return {"semantic_query": question, "area_canonical": "", "report_type": ""}
```

### Bedrock Knowledge Base Creation (One-time Setup)

```python
def setup_knowledge_base():
    """Create KB + Data Source."""
    
    bedrock = boto3.client("bedrock-agent")
    
    # Create KB
    kb_response = bedrock.create_knowledge_base(
        name="holon_qa_kb",
        description="Holon groundwater monitoring Q&A",
        roleArn="arn:aws:iam::YOUR_ACCOUNT:role/bedrock-kb-role",
        knowledgeBaseConfiguration={
            "type": "VECTOR",
            "vectorKnowledgeBaseConfiguration": {
                "embeddingModelArn": "arn:aws:bedrock:YOUR_REGION::foundation-model/amazon.titan-embed-text-v1"
            }
        }
    )
    
    kb_id = kb_response["knowledgeBase"]["id"]
    print(f"Created KB: {kb_id}")
    
    # Create Data Source
    ds_response = bedrock.create_data_source(
        name="holon_s3_source",
        knowledgeBaseId=kb_id,
        dataSourceConfiguration={
            "type": "S3",
            "s3Configuration": {
                "bucketArn": "arn:aws:s3:::holon-documents",
                "inclusionPrefixes": ["documents/incoming/"],
                "chunkingConfiguration": {
                    "chunkingStrategy": "FIXED_SIZE",
                    "fixedSizeChunkingConfiguration": {
                        "maxTokens": 800,
                        "overlapPercentage": 25
                    }
                }
            }
        }
    )
    
    source_id = ds_response["dataSource"]["id"]
    print(f"Created Data Source: {source_id}")
    
    # Start sync
    bedrock.start_ingestion_job(knowledgeBaseId=kb_id, dataSourceId=source_id)
    print("Sync started")
```
