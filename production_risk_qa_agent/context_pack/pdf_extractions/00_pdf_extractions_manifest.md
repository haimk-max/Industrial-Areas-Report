# PDF Extractions Manifest — Layer 2 Context (עומק מחקר)

**קבצים**: חילוצי AI מדוחות PDF היסטוריים, מובנים כ-JSON.

---

## מה זה Layer 2?

קבצים **מובנים (JSON)** חילוצים מ-PDFs — כל דוח מיצואו לעדויות, ממצאים, זיהומים, משפחות.

**מתי להשתמש**:
- ✅ "אימות עדות היסטורית"
- ✅ "מתי בדיוק הוגלה זה לראשונה?"
- ✅ "מה הדוח מ-2007 אומר?"
- ✅ ריסוף פרטי של דוח מסוים

**מתי לא**:
- ❌ שאלה מהירה "מה הסיכון?" → Shכבה 0
- ❌ צריך סטטוס נוכחי → Shכבה 1

---

## קבצים בShכבה זו

| קובץ | מקור PDF | שנה | גודל | תוכן |
|------|----------|------|------|------|
| `_findings_batyam2007.json` | TAHAL Report (Bat-Yam/Holon) | 2007 | 36KB | ממצאים היסטוריים מ-2007 |
| `_findings_finalreport.json` | סיכום/Final Report | ~2021 | 24KB | דוח סכום עם ממצאים מסוג |
| `_findings_part1.json` | חלק 1 דוח | ~2020 | 34KB | חלק ראשון של ניתוח מלא |
| `_findings_part2.json` | חלק 2 דוח | ~2020 | 24KB | חלק שני של ניתוח מלא |
| `_findings_report2021.json` | Water Authority Report 2021 | 2021 | 24KB | דוח רשות המים 2021 |
| `extracted_findings.json` | **כל 5 דוחות מאוחדים** | 2007–2021 | 157KB | אינדקס מלא — חפש כאן ראשון |

---

## Schema של קובץ JSON

```json
{
  "source_file": "water-sources-status_tehom_FinalReport-Holon.pdf",
  "title_he": "דוח סיכום...",
  "year": 2021,
  "author_org_he": "רשות המים",
  "summary_he": "סיכום ממצאים...",
  
  "boreholes_mentioned": [
    {
      "canonical_id": "מק_חולון_12",
      "name_he": "מק חולון 12",
      "latest_concentration": { "TCE": "8,750 µg/L", "year": 2020 },
      "trend_description": "עלייה / יציב / ירידה"
    }
  ],
  
  "contamination_findings": [
    {
      "contaminant": "TCE",
      "locations": ["מק חולון 12", "נת חולון 11"],
      "concentration_range": "100–30,000 µg/L",
      "severity_assessment": "critical"
    }
  ],
  
  "facilities_suspected": [
    {
      "name_he": "תדיראן",
      "type": "ציפוי מתכות",
      "evidence_grade": "A",
      "confidence": "HIGH",
      "reasoning": "decay chain TCE + Cr signature"
    }
  ],
  
  "hydrogeology_he": "זרימה דרום-מערבית בקצב 1–3 מ'/שנה...",
  "trends_described_he": ["TCE עולה בנת חולון 2", "1,1-DCE צומח", "..."],
  "recommendations_he": ["דגימה רבעונית", "קידוח מאימות", "..."],
  "key_quotes_he": ["\"זיהום קריטי בקידוח X\"", "..."]
}
```

---

## דוגמה: חיפוש בShכבה 2

**שאלה**: "מתי בדיוק הוגלתה הבעיה של TCE בנת חולון 11?"

**כיצד למצוא**:
1. פתח `extracted_findings.json` (מאוחד)
2. חפש "نت חולון 11" + "TCE"
3. קרא את כל ההרשומות (2007 → 2021) → ראה מתי הופיע ראשון

**תשובה בDL**: "לפי דוח [שנה], TCE בקידוח זה היה [ערך]"

---

## חוזק + מגבלה של Shכבה 2

✅ **חוזק**:
- מובנה (JSON) — קל לחיפוש
- מלא — כל עדויות מדוחות
- א-בחינה — evidence grades מובחנים

⚠️ **מגבלה**:
- גדול (157KB) — יש הרבה נתונים, תצטרך להיות ספציפי בחיפוש
- אם צריך טקסט **גולמי** בדיוק כפי שהופיע בדוח → Layer 3 (Raw TXT, rare)

---

## שימוש עם System Prompt

בתוך ה-System Prompt, בתשובה:

```
אם שימשת בShכבה 2 (pdf_extractions):
- הוסף הערה: "מקור מעומק 2 (extracted_findings.json / _findings_XXXX.json)"
- ציין את השנה/דוח
- ציין את הevidence grade (A/B/C/D/E)
```

---

**Last Updated**: 2026-06-17
