# Playbook: Forensics & Source Attribution Guide

> **מדריך שיוך מקורות זיהום** — איך לקשר זיהום שנמדד בקידוח למתקן/אתר מקור, עם רמות ביטחון מבוססות-ראיה. שיוך פורנזי הוא **הסתברותי** — לעולם אל תטען וודאות שלא נתמכת.

---

## עיקרון יסוד

שיוך מקור זיהום **תמיד מוצג עם רמת ביטחון** (HIGH / MEDIUM / LOW). הימנע מ"בהחלט נגרם על-ידי X" ללא ראיה. הצג השערות מתחרות; אל תבחר בשתיקה.

> **כלל זהב**: כשדפוס זיהום תואם מספר מתקני-מקור — הצג את כל ההשערות. שיוך פורנזי תומך, לא חד-משמעי.

---

## חלק א — שתי שכבות סיווג

יש **שתי מערכות סיווג נפרדות** שעובדות יחד:

### 1. Evidence Classification (A–E) — חוזק הראיה למקור

| Class | משמעות | בסיס ראיה | משקל |
|-------|---------|-----------|------|
| **A** | `raw_report_verified` | ציטוט ישיר מטקסט גולמי של דוח (עם עמוד) | **חזק** |
| **B** | `ai_extracted_with_page_ref` | AI-derived מ-`_findings_*.json` / PDF, עם page_ref מפורש | **חזק** |
| **C** | `web_verified_current_activity` | סטטוס פעילות עדכני מ-web | **סטטוס בלבד — לא הוכחת זיהום** |
| **D** | `inferred_candidate` | קרבה גיאוגרפית / שם קידוח / הקשר; ללא ראיית מסמך | **רקע / השערה** |
| **E** | `weak / mention_only` | אזכור בודד; ללא קישור לקידוח/מזהם | **נספח בלבד** |

**מדיניות שימוש**:
- **A + B**  — מועמדים חזקים; ייכנסו לגוף הדוח (סעיף שיוך מקורות)
- **C**  — משלים מצב נוכחי; **אסור** להציג כראיית זיהום בעצמו
- **D / E**  — רקע/נספח. נכנסים לגוף הדוח **רק אם** נתוני הניטור (severity, trends, חתימות כימיות) מחזקים אותם עצמאית

### 2. Attribution Confidence (HIGH/MEDIUM/LOW) — חוזק הקישור קידוח↔מקור

מבוסס על **3 קריטריונים**:

| קריטריון | תיאור |
|----------|--------|
| **כתובת מאומתת** | מיקום המתקן מאושר בתוך/סמוך לפוליגון האזור |
| **מזהם מתאים מקידוח קרוב** | מזהם שנמדד בקידוח <500m תואם לחתימת המתקן |
| **חפיפת שנות פעילות** | תקופת פעילות המתקן חופפת לעדות בקידוח |

| Confidence | תנאי |
|-----------|------|
| **HIGH** | כל 3 הקריטריונים (address + מזהם מתאים <500m + שנות פעילות חופפות) |
| **MEDIUM** | 2 מתוך 3 הקריטריונים |
| **LOW** | קריטריון 1, או רק רישום ללא ראיות שטח |

> **הבחנה חשובה**: Evidence Class (A–E) = *כמה אמין מקור המידע על המתקן*. Attribution Confidence (HIGH/MEDIUM/LOW) = *כמה חזק הקישור בין המתקן לזיהום שנמדד*. מתקן יכול להיות Class A (מתועד בדוח) אך LOW confidence (רחוק מכל קידוח בחריגה).

---

## חלק ב — חתימות כימיות (Source Signatures)

`signalkit.forensics_engine` מספק חתימות מובנות. השתמש בהן לזהות **סוג מתקן** מדפוס המזהמים.

### משפחות מתכות (METAL_FAMILIES)

| חתימה | Primary | Secondary | מקור מרומז |
|-------|---------|-----------|------------|
| `chromium_complex` | Cr(VI) | Cr(III), Cr_total | ציפוי, גימור מתכות, עיבוד עורות |
| `nickel_cluster` | Ni | Co | מיחזור מתכות, ציפוי, סוללות |
| `lead_zinc_pair` | Pb | Zn | כרייה היסטורית, התכה, סוללות |
| `mercury_indicator` | Hg | MeHg | כלור-אלקלי היסטורי, מד-חום |

### משפחות PFAS

| חתימה | Markers | מקור | ציר זמן |
|-------|---------|------|---------|
| `legacy_AFFF` | PFOS, PFOA | קצף כיבוי אש (שדות תעופה, צבא) | 1970s–2000s |
| `emerging_PFAS` | PFHxS, PFBS, GenX, ADONA | AFFF חלופי, שימוש תעשייתי | 2000s+ |
| `telomer_series` | 8-2 FTS, 10-2 FTS | ייצור פלואורופולימרים, טקסטיל | מתמשך |

### משפחות דלק (FUEL)

| חתימה | Markers | מקור |
|-------|---------|------|
| `BTEX_cluster` | Benzene, Toluene, Ethylbenzene, Xylenes | דלף דלק, מיכלים תת-קרקעיים (UST) |
| `oxygenate_cluster` | MTBE, ETBE, TAME | תוספי דלק (1980s–2000s) |

### שימוש בקוד

```python
from signalkit.forensics_engine import match_source_signatures, classify_contamination_family

detected = {"Cr(VI)": [120, 89], "Cr(III)": [45]}
matches = match_source_signatures(detected)
# → {'chromium_complex': {'confidence': 'HIGH', 'source': 'Electroplating...', 'markers_found': 1}}

families = classify_contamination_family(["PCE", "TCE", "Benzene", "Cr"])
# → {'PCE': 'CVOC', 'TCE': 'CVOC', 'Benzene': 'FUEL', 'Cr': 'METALS'}
```

---

## חלק ג — שרשראות פירוק (Decay Chains)

נוכחות תוצרי-פירוק היא ראיה חזקה למקור CVOC ולתהליך ריקבון פעיל.

| שרשרת | <bdi>Parent → Children</bdi> | מסלול | משמעות פורנזית |
|-------|-------------------|--------|----------------|
| `PCE_to_TCE` | <bdi>PCE → TCE</bdi> → DCE → VC | reductive dechlorination | VC (מסרטן) = ריקבון מתקדם; מקור ישן |
| `TCA_to_DCA` | 1,1,1-TCA → 1,1-<bdi>DCA → chloroethane</bdi> | hydrolysis + reduction | מבחין מקור TCA ממקור PCE |
| `TCM_series` | <bdi>TCM → DCM</bdi> → CM | reductive dehalogenation | מקור chloroform |

```python
from signalkit.forensics_engine import build_decay_chains

chains = build_decay_chains(["PCE", "TCE", "DCE", "VC"])
# → {'PCE_to_TCE': {'detected_members': [...], 'completeness': 1.0, ...}}
```

**אינדיקטורים לבדוק**:
- **completeness גבוה** (כל חברי השרשרת נוכחים)  — מקור ותיק, ריקבון מתקדם
- **VC נוכח**  — תוצר סופי מסרטן; דה-הלוגנציה פעילה; הוסף VC + ethene לפאנל
- **יחס DCE:TCE עולה לאורך זמן**  — האצת ריקבון ביולוגי
- **דומיננטיות 1,1-DCE**  — עשוי לרמז על מקור TCA ולא PCE

---

## חלק ד — מבנה רשומת מתקן (Facility Record Schema)

כל מתקן ב-`facility_attribution.json` (או `source_candidates_index.csv` לאזורים חדשים):

```json
{
  "facility_id": "F-001",
  "name_he": "שם המתקן",
  "addresses_he": ["כתובת בפוליגון"],
  "in_zone_polygon": "YES",
  "industry_sector": "מגזר; תת-מגזר",
  "contamination_family": ["CVOC", "HEAVY_METALS"],
  "suspected_contaminants": ["Cr", "TCE", "VOC"],
  "evidence_he": "תיאור הראיה + הקשר",
  "confidence": "HIGH",                        // HIGH/MEDIUM/LOW
  "evidence_type": "confirmed_address",        // → Evidence Class
  "source": "pdf_extraction",
  "page_refs": [{"source_file": "...", "page": 3}],
  "operating_years": "1962-2006",
  "coordinates_itm": {"easting": null, "northing": null},
  "associated_boreholes": []                    // קידוחים מקושרים
}
```

**שדות חובה לשיוך מהימן**:
- `confidence` — תמיד מאוכלס (HIGH/MEDIUM/LOW)
- `page_refs` — להפניית מקור (Evidence Class A/B)
- `suspected_contaminants` — לcross-check מול חתימת הקידוח
- `associated_boreholes` — הקישור הגיאוגרפי בפועל

---

## חלק ה — תהליך שיוך (Attribution Workflow)

```
1. זהה קידוח בחריגה (severity_index ≥ 5)
      ↓
2. חלץ חתימת מזהמים מהקידוח (אילו משפחות? אילו תרכובות מפתח?)
      ↓
3. match_source_signatures()  — סוג מתקן מרומז
      ↓
4. חפש ב-facility_attribution.json מתקנים ב-<500m עם contamination_family תואם
      ↓
5. לכל מועמד — בדוק 3 קריטריונים  — HIGH/MEDIUM/LOW
      ↓
6. בדוק Evidence Class של מקור המידע (A–E)
      ↓
7. הצג כל ההשערות עם רמות ביטחון; אל תבחר בשתיקה
      ↓
8. תעד אי-ודאות + איזו ראיה נוספת תחזק את השיוך
```

---

## חלק ו — אזהרות (Pitfalls)

| מלכודת | סיכון | מניעה |
|--------|-------|--------|
| **ערבוב Evidence Class ו-Confidence** | בלבול בין "מקור מידע אמין" ל"קישור חזק" | שמור שתי המערכות נפרדות במפורש |
| **Web כהוכחת זיהום** | סטטוס web (C) ≠ הוכחת מקור | C = סטטוס בלבד; דרוש A/B + נתוני ניטור |
| **שיוך יחיד בלעדי** | התעלמות מהשערות מתחרות | תמיד הצג כל המועמדים הסבירים |
| **ערך קיצוני בודד** | שיוך מבוסס מדידה לא-מאוששת | דרוש דופליקט / אישוש לפני שיוך חזק |
| **selection bias** | קידוחי ניטור ליד מקורות מטים את התמונה | ציין מפורשות; אל תכליל לכלל המרחב |
| **שם מנתוני אימון** | המצאת מתקן שלא בחומר המצורף | הסתמך רק על facility JSON / context pack |

---

## חלק ז — Checklist לשיוך מקור (לכל מוקד)

- [ ] חתימת מזהמים חולצה מהקידוח (משפחות + תרכובות מפתח)
- [ ] `match_source_signatures()` הורץ  — סוג מתקן מרומז
- [ ] מועמדים ב-<500m זוהו מ-facility JSON
- [ ] כל מועמד דורג HIGH/MEDIUM/LOW (3 קריטריונים)
- [ ] Evidence Class (A–E) צוין לכל מועמד
- [ ] decay chains נבדקו (אם CVOC) — completeness + VC
- [ ] co-occurrence נבדק (מתכת + VOC = ציפוי)
- [ ] השערות מתחרות הוצגו (לא שיוך יחיד בלעדי)
- [ ] אי-ודאות תועדה + ראיה משלימה נדרשת צוינה
- [ ] selection bias caveat נכלל

---

## הפניות

### Root SSOT (Methodology)
📍 **Evidence Classification (A–E)**: [`ZONE_REPORT_PROCESS_GUIDE.md`](../../../ZONE_REPORT_PROCESS_GUIDE.md) §I  
📍 **Attribution Confidence Criteria**: [`ZONE_REPORT_PROCESS_GUIDE.md`](../../../ZONE_REPORT_PROCESS_GUIDE.md) §I.2  
📍 **Forensics Rule**: [`CLAUDE.md`](../../../CLAUDE.md) §5 Data Integrity Rule #4 (Forensics Probabilistic)

### Code & Data
🔧 **Signature Definitions**: [`toolkit/pylib/signalkit/forensics_engine.py`](../../pylib/signalkit/forensics_engine.py)  
📊 **Example Attribution JSON**: `Holon/data/facility_attribution.json` (60 מתקנים, reference only)

### Toolkit Playbooks
📋 **Zone Diagnosis (using attribution)**: [`toolkit/playbooks/zone_diagnosis_template.md`](../zone_diagnosis_template.md) §5

---

**Version**: 1.0  
**Status**: ✓ TEMPLATE READY  
**Last Updated**: 2026-05-27
