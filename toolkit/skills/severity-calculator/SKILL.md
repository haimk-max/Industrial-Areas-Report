# Skill: severity-calculator

## מהו?

**severity-calculator** = יומן interactive לחישוב אינדקס חומרה (bucket) מריכוזים ותקנים בתקן האב (2021 Report).

בהינתן:
- ריכוז מקסימלי בחמש שנים (C_max_5y)
- תקן שתיה (DWS)

הכלי מחזיר:
- **Bucket** (0–8): סולם חומרה
- **Label**: תיאור בעברית (למשל "Critical (500–1,000%)")
- **Color**: קוד CSS לחזותי
- **Risk Level**: סיווג סיכון (CLEAN, LOW, MODERATE, CRITICAL, וכדו')
- **Recommended Action**: פעולה מומלצת

---

## Input

```
/<severity-calculator> --c_max <value> --dws <value> [--unit ppb]

Arguments:
  --c_max <value>        Maximum concentration in past 5y (required)
  --dws <value>          Drinking water standard (required, same units as c_max)
  --unit <str>           Unit (ppb, mg/L, etc.) — default "ppb"
  --parameter <name>     Parameter name (TCE, PFOS, Cr, etc.) — for context
  --borehole <id>        Borehole ID — for context
```

---

## Output

```json
{
  "bucket": 5,
  "label": "Very High (200–500%)",
  "color": "#5a564f",
  "risk_level": "HIGH",
  "recommended_action": "Urgent investigation + remediation planning",
  "percentage_of_standard": 345.6,
  "context": {
    "parameter": "TCE",
    "borehole": "holon_nt_2",
    "c_max_5y": 3456,
    "dws": 10
  }
}
```

---

## Example

```bash
/<severity-calculator> --c_max 3456 --dws 10 --parameter TCE --borehole holon_nt_2
```

**Output**:
```
Bucket: 5 (Very High)
Risk Level: HIGH
Recommended Action: Urgent investigation + remediation planning
```

---

## זמן ההפעלה

~1 second (pure calculation, no external calls)

---

## טעויות נפוצות

| שגיאה | גורם | פתרון |
|-------|------|---------|
| `DWS missing` | לא סיפקת תקן שתיה | הוסף `--dws <value>` |
| `Negative concentration` | C_max הוא שלילי | בדוק את הנתונים (ריכוז לא יכול להיות שלילי) |
| `DWS = 0` | תקן שתיה אפס | בדוק את הערך; כל תקן חייב להיות > 0 |

---

## קובץ מקור

קוד הכלי בנו מ-`toolkit/pylib/signalkit/severity_calculator.py`.

---

## מטבח (Kitchen — מימוש)

הפעלה מחייבת את signalkit להיות installed locally:

```bash
pip install -e ./toolkit/pylib
```

לאחר מכן:
```python
from signalkit.severity_calculator import calculate_bucket, classify_severity

bucket = calculate_bucket(c_max_5y=3456, dws=10)
classification = classify_severity(bucket)
print(classification)
```

---

**Status**: ✓ READY FOR USE
