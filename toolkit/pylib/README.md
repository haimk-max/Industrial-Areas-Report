# signalkit — Python Library for Groundwater Quality Analysis

> Trend detection, severity calculation, forensics, and data pipeline tools for groundwater contamination monitoring.

## Installation

### Development (Editable Install)

```bash
cd /path/to/Industrial-Areas-Report
pip install -e ./toolkit/pylib
```

This allows you to edit source code in `toolkit/pylib/signalkit/` and changes are immediately reflected in Python imports.

### Production

```bash
pip install signalkit
# (Future: after publishing to PyPI)
```

## Quick Start

### 1. Trend Analysis (Mann-Kendall)

```python
from signalkit.trend_analysis import calculate_mann_kendall

measurements = [5, 8, 12, 18, 25, 31, 35]  # ppb over time
result = calculate_mann_kendall(measurements)

print(result)
# Output:
# {
#   'trend': 'ALERT',
#   'slope': 4.29,
#   'z_score': 2.45,
#   'p_value': 0.014,
#   'snr': 0.52,
#   'n_measurements': 7,
#   'soft_trigger_detected': True,
#   'status': 'PASS'
# }
```

### 2. Severity Calculation (Bucket Index)

```python
from signalkit.severity_calculator import calculate_bucket, classify_severity

# TCE: measured 101 ppb, standard is 10 ppb
c_max_5y = 101
dws = 10

bucket = calculate_bucket(c_max_5y, dws)
severity = classify_severity(bucket)

print(severity)
# Output:
# {
#   'label': 'Elevated (100–150%)',
#   'color': '#cfcfcf',
#   'risk_level': 'ELEVATED',
#   'recommended_action': 'Detailed investigation recommended'
# }
```

### 3. Forensics (Contamination Attribution)

```python
from signalkit.forensics_engine import (
    build_decay_chains,
    match_source_signatures,
    classify_contamination_family
)

detected_vocs = ["PCE", "TCE", "DCE", "VC"]
chains = build_decay_chains(detected_vocs)

print(chains)
# Output:
# {
#   'PCE_to_TCE': {
#     'detected_members': ['pce', 'tce', 'dce', 'vc'],
#     'pathway': 'reductive dechlorination',
#     'description': '...',
#     'completeness': 1.0
#   }
# }
```

### 4. Data Pipeline (CSV Parsing)

```python
from signalkit.data_pipeline import parse_measurements_csv, batch_normalize_measurements

measurements = parse_measurements_csv(
    filepath="./measurements.csv",
    borehole_col="borehole_id",
    date_col="date",
    parameter_col="parameter",
    concentration_col="concentration",
    unit_col="unit",
)

# Filter valid records
valid = batch_normalize_measurements(measurements)

print(f"Parsed {len(measurements)} records; {len(valid)} valid")
```

## Modules

### `signalkit.trend_analysis`

**Functions**:
- `calculate_mann_kendall(measurements, dates=None, apply_snr_gate=True, snr_threshold=0.3, soft_trigger=2)` → dict
  - Mann-Kendall trend test with SNR gating
  - Returns: trend, slope, z_score, p_value, snr, status
  
- `apply_snr_gating(trend_results, threshold=0.3)` → dict
  - Apply SNR filter to existing trend results

**Methodology**: Tie-corrected variance, continuity-corrected Z, Sen's slope estimator

---

### `signalkit.severity_calculator`

**Functions**:
- `calculate_bucket(c_max_5y, dws)` → int
  - Severity bucket (0–8) based on 2021 Report formula
  
- `classify_severity(bucket)` → dict
  - Label, color, risk level, recommended action
  
- `batch_calculate_buckets(measurements_df, c_max_col, dws_col)` → numpy.ndarray
  - Batch processing for pandas DataFrames

**Scale**: 0 = Clean (0–25%) through 8 = Extreme (>10,000%)

---

### `signalkit.forensics_engine`

**Functions**:
- `build_decay_chains(detected_vocs)` → dict
  - Identify VOC dechlorination pathways (<bdi>PCE→TCE</bdi>→DCE→VC, etc.)
  
- `match_source_signatures(detected_contaminants)` → dict
  - Match patterns to facility types (electroplating, AFFF, petroleum, etc.)
  
- `classify_contamination_family(contaminants)` → dict
  - Assign each contaminant to family: CVOC, FUEL, METALS, PFAS

**Data**: Preconfigured decay chains, metal families, PFAS series, fuel clusters

---

### `signalkit.data_pipeline`

**Functions**:
- `parse_measurements_csv(filepath, borehole_col, date_col, ...)` → list[dict]
  - Parse CSV; normalize units to ppb
  
- `normalize_units(concentration, unit)` → float
  - Convert any unit (mg/L, ppm, ng/L) to ppb (µg/L)
  
- `validate_measurement(measurement, min_conc, max_conc)` → (bool, str)
  - Sanity check for a single record
  
- `batch_normalize_measurements(measurements)` → list[dict]
  - Filter invalid records

**Units Supported**: ppb, µg/L, ng/L, ppt, mg/L, ppm, %

---

## Configuration

### Default Thresholds

Edit `signalkit/__init__.py` or pass as function arguments:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `snr_threshold` | 0.3 | Minimum SNR for trend to be "real" |
| `soft_trigger` | 2 | Consecutive rising <bdi>measurements → WATCH</bdi> |
| `p_value_threshold` | 0.05 | Statistical significance |

---

## Testing

```bash
cd toolkit/pylib
pip install -e ".[dev]"
pytest tests/
```

(Tests TBD)

---

## Contributing

1. Write a function in `signalkit/<module>.py`
2. Add to `__all__` in `signalkit/__init__.py`
3. Update `README.md` (this file)
4. Test on sample data

---

## License

MIT (pending formal declaration)

---

## References

- 2021 Water Quality Report (methodology for severity index)
- TAHAL 2008 (hydrogeologic baseline)
- Mann-Kendall Trend Test (Kendall, 1975; Mann, 1945)

---

**Version**: 0.1.0  
**Status**: ✓ Alpha (functions stable; API may change)  
**Last Updated**: 2026-05-27
