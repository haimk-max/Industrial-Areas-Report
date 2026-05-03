# Phase B QA Report — Trend Analysis

## Classification summary

| Classification | Count |
|---|---|
| ALERT | 1 |
| WATCH | 2 |
| STABLE | 25 |
| DECREASING | 0 |
| NONE | 548 |

- Total (borehole, parameter) pairs: 576
- Pairs with insufficient data (n<4): 271
- Pairs that crossed drinking water standard: 36

## ALERT classifications

| Borehole | Parameter | n5 | SNR | MK p-value |
|---|---|---|---|---|
| raanana_p_25 | NO3 | 85 | 0.569 | 0.0000 |

## WATCH classifications (first 20)

| Borehole | Parameter | n5 | SNR | MK p-value |
|---|---|---|---|---|
| raanana_nd_paz_hanofer | ORP | 4 | 1.575 | 0.3082 |
| raanana_p_25 | CHLF | 8 | 1.498 | 0.0171 |

## Validation
- Entry criteria applied (n≥4, has_detection, n5≥1): ✅
- Soft trigger: 2 most recent 5y measurements compared: ✅
- Mann-Kendall: tie-corrected variance, continuity-corrected Z: ✅
- SNR gating: <0.3 → NONE regardless of MK: ✅
- TPFAS absent from all results: ✅