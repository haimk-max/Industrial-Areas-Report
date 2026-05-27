# Skill: trend-detective

## מהו?

**trend-detective** = יומן interactive לזיהוי מגמות בנתונים היסטוריים של זיהום.

בהינתן **סדרה של ריכוזים בזמן** (למשל TCE בקידוח holon_nt_2 מ-2020 עד 2026), הכלי:

1. **מחשב Mann-Kendall trend** (שיטה לא-פרמטרית)
2. **בודק SNR** (Signal-to-Noise Ratio) — תחושני לרעש בנתונים
3. **זוהה soft triggers** — 2+ מדידות עולות רצופות (אזהרה מוקדמת)
4. **מסווג מגמה**: ALERT | WATCH | STABLE | DECREASING | NONE

---

## Input

```
/<trend-detective> --borehole <id> --parameter <name> [--data <csv> | --interactive]

Arguments:
  --borehole <id>        Borehole ID (e.g., "holon_nt_2") — required
  --parameter <name>     Parameter name (e.g., "TCE") — required
  --data <csv>           Path to CSV file with columns: date, concentration
  --interactive          Paste measurements interactively (comma-separated)
  --unit <str>           Unit (ppb, mg/L, etc.) — for display; doesn't affect trend
  --snr-threshold <val>  SNR threshold (default 0.3)
```

---

## Output

```json
{
  "borehole": "holon_nt_2",
  "parameter": "TCE",
  "trend": "ALERT",
  "slope": 15.3,
  "z_score": 2.45,
  "p_value": 0.014,
  "snr": 0.52,
  "n_measurements": 12,
  "soft_trigger_detected": true,
  "status": "PASS",
  "interpretation": "Rising trend detected with high confidence. Recommend urgent investigation."
}
```

---

## Example 1: From CSV

```bash
/<trend-detective> --borehole holon_nt_2 --parameter TCE --data ./measurements.csv
```

CSV format (minimal):
```
date,concentration
2020-01-15,5
2021-03-22,8
2022-06-10,12
2023-11-05,18
2024-04-20,25
2025-08-12,31
2026-01-05,35
```

---

## Example 2: Interactive

```bash
/<trend-detective> --borehole holon_nt_2 --parameter TCE --interactive
```

Paste (comma-separated):
```
5, 8, 12, 18, 25, 31, 35
```

---

## תוצא: Trend Classifications

| סיווג | משמעות | פעולה |
|--------|--------|--------|
| **ALERT** | p < 0.05 + slope > 0 | Urgent investigation, enhanced monitoring |
| **WATCH** | Soft trigger detected (2+ consecutive rises) | Increased monitoring frequency |
| **STABLE** | No significant trend + no soft trigger | Continue standard monitoring |
| **DECREASING** | p < 0.05 + slope < 0 | Positive sign; continue monitoring |
| **NONE** | SNR < threshold (noisy data) | Insufficient signal; more measurements needed |

---

## Methodology

**Mann-Kendall Test**:
- Non-parametric trend estimator (doesn't assume normal distribution)
- Robust to outliers
- Returns: Z-score, p-value, Sen's slope (non-parametric slope estimator)

**SNR Gating**:
- If SNR < 0.3 (default), trend is considered "noise" → NONE
- Prevents false alarms on noisy data

**Soft Trigger**:
- If ≥2 consecutive measurements rise (even if not statistically significant), flag as WATCH
- Early warning for incipient trends

---

## קובץ מקור

🔧 **Implementation**: [`toolkit/pylib/signalkit/trend_analysis.py`](../../pylib/signalkit/trend_analysis.py)

---

## מטבח (Kitchen — מימוש)

```python
from signalkit.trend_analysis import calculate_mann_kendall

measurements = [5, 8, 12, 18, 25, 31, 35]
result = calculate_mann_kendall(
    measurements,
    apply_snr_gate=True,
    snr_threshold=0.3,
    soft_trigger=2,
)

print(result)
```

---

**Status**: ✓ READY FOR USE
