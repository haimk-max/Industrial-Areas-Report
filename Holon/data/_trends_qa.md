# Phase B QA Report — Trend Analysis

## Classification summary

| Classification | Count |
|---|---|
| ALERT | 0 |
| WATCH | 0 |
| STABLE | 613 |
| DECREASING | 80 |
| NONE | 4021 |

- Total (borehole, parameter) pairs: 4762
- Pairs with insufficient data (n<4): 3026
- Pairs that crossed drinking water standard: 567

## ALERT classifications

| Borehole | Parameter | n5 | SNR | MK p-value |
|---|---|---|---|---|

## WATCH classifications (first 20)

| Borehole | Parameter | n5 | SNR | MK p-value |
|---|---|---|---|---|

## Validation
- Entry criteria applied (n≥4, has_detection, n5≥1): ✅
- Soft trigger: 2 most recent 5y measurements compared: ✅
- Mann-Kendall: tie-corrected variance, continuity-corrected Z: ✅
- SNR gating: <0.3 → NONE regardless of MK: ✅
- TPFAS absent from all results: ✅