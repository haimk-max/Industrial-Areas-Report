# Playbook: Structured Data Pack (6-CSV Schema)

> **Deterministic specification** for the 6 CSVs produced in Step 2 of V5 hybrid pipeline.

---

## Overview

**Structured Data Pack** = 6 CSVs containing all measurements, trends, and severity calculations for a zone.

**Location**: `{zone}/02_data/`

**Workflow**:
1. Parse zone Excel file → raw measurements
2. Normalize units, filter for 5-year window
3. Calculate severity buckets, trends, forensics
4. Aggregate into 6 CSVs

**Consumption**: Used by Zone Diagnosis (Step 4) and V5 Report generation (Step 5)

---

## CSV 1: measurements_scoped.csv

**Purpose**: All measurements for boreholes in scope (Tiers 1, 2, 3)

**Rows**: One per measurement  
**Approx. Count**: 2,000–5,000 (depends on zone)

| Column | Type | Example | Required | Notes |
|--------|------|---------|----------|-------|
| `borehole_id` | str | `holon_nt_1` | ✓ | Canonical ID |
| `measurement_date` | str (YYYY-MM-DD) | `2026-01-15` | ✓ | ISO format |
| `parameter` | str | `TCE` | ✓ | Contaminant name (English) |
| `concentration` | float | `5.23` | ✓ | Normalized to ppb (µg/L) |
| `original_unit` | str | `ppb` | ✓ | Original unit before normalization |
| `detection_limit` | float | `0.5` | □ | If non-detect, use as LOD |
| `source` | str | `TAHAL_2021_Report_p53` | □ | Source document reference |

**Constraints**:
- Only measurements from past 5 years (as of report date)
- Concentration must be numeric (no "<" notation; convert to detection_limit)
- Must be sorted by borehole_id, then by measurement_date (ascending)

**CSV Template**:
```csv
borehole_id,measurement_date,parameter,concentration,original_unit,detection_limit,source
holon_nt_1,2020-01-15,TCE,5.23,ppb,0.5,TAHAL_2021_Report_p53
holon_nt_1,2020-06-22,TCE,6.8,ppb,0.5,TAHAL_2021_Report_p53
holon_nt_1,2021-03-10,TCE,7.2,ppb,0.5,Excel_2021
```

---

## CSV 2: latest_results.csv

**Purpose**: Most recent measurement per (borehole, parameter) pair

**Rows**: One per (borehole, parameter) combination with data  
**Approx. Count**: 300–800

| Column | Type | Example | Required | Notes |
|--------|------|---------|----------|-------|
| `borehole_id` | str | `holon_nt_1` | ✓ | Canonical ID |
| `parameter` | str | `TCE` | ✓ | Contaminant |
| `latest_date` | str (YYYY-MM-DD) | `2026-01-05` | ✓ | Date of latest measurement |
| `latest_concentration` | float | `35.2` | ✓ | Value at latest_date |
| `c_max_5y` | float | `45.6` | ✓ | Maximum in past 5 years |
| `dws` | float | `10` | ✓ | Drinking water standard (ppb) |
| `unit` | str | `ppb` | ✓ | Unit (all normalized) |
| `trend_status` | str | `ALERT` | □ | From trend_by_well_parameter.csv |
| `family` | str | `CVOC` | □ | Contamination family (derived) |

**Constraints**:
- One row per (borehole, parameter)
- c_max_5y ≥ latest_concentration (always)
- dws > 0 (no null DWS)
- Sorted by c_max_5y descending (for filtering top contaminants)

**CSV Template**:
```csv
borehole_id,parameter,latest_date,latest_concentration,c_max_5y,dws,unit,trend_status,family
holon_nt_1,TCE,2026-01-05,35.2,45.6,10,ppb,ALERT,CVOC
holon_nt_2,Cr(VI),2025-11-20,22.5,89.3,100,ppb,WATCH,METALS
```

---

## CSV 3: severity_by_well_family.csv

**Purpose**: Severity distribution per (borehole, contamination_family) pair

**Rows**: One per (borehole, family) that has data  
**Approx. Count**: 150–400

| Column | Type | Example | Required | Notes |
|--------|------|---------|----------|-------|
| `borehole_id` | str | `holon_nt_1` | ✓ | Canonical ID |
| `family` | str | `CVOC` | ✓ | Family: CVOC, METALS, PFAS, FUEL |
| `max_bucket` | int | 5 | ✓ | Highest bucket (0–8) in family |
| `max_bucket_label` | str | `Very High (200–500%)` | □ | Human-readable label |
| `parameter_at_max` | str | `TCE` | □ | Which parameter hit max_bucket |
| `crossed_standard_count` | int | 3 | □ | How many parameters exceeded DWS in family |
| `total_parameters_tested` | int | 6 | □ | Total parameters checked for this family |

**Constraints**:
- max_bucket ∈ [0, 8]
- crossed_standard_count ≤ total_parameters_tested
- Only include families that have ≥1 measurement
- Sorted by borehole_id, then by max_bucket descending

**CSV Template**:
```csv
borehole_id,family,max_bucket,max_bucket_label,parameter_at_max,crossed_standard_count,total_parameters_tested
holon_nt_1,CVOC,5,Very High (200–500%),TCE,3,6
holon_nt_1,METALS,3,Elevated (100–150%),Cr(VI),1,4
holon_nt_2,FUEL,2,Moderate (50–100%),Benzene,0,4
```

---

## CSV 4: trends_by_well_parameter.csv

**Purpose**: Mann-Kendall trend analysis results per (borehole, parameter) pair

**Rows**: One per (borehole, parameter) with ≥3 measurements  
**Approx. Count**: 200–600

| Column | Type | Example | Required | Notes |
|--------|------|---------|----------|-------|
| `borehole_id` | str | `holon_nt_1` | ✓ | Canonical ID |
| `parameter` | str | `TCE` | ✓ | Contaminant |
| `trend` | str | `ALERT` | ✓ | ALERT, WATCH, STABLE, DECREASING, NONE |
| `z_score` | float | `2.45` | ✓ | Mann-Kendall Z (continuity-corrected) |
| `p_value` | float | `0.014` | ✓ | Two-tailed p-value |
| `snr` | float | `0.52` | ✓ | Signal-to-Noise Ratio |
| `slope` | float | `4.29` | ✓ | Sen's slope (ppb per period) |
| `n_measurements` | int | 7 | ✓ | Number of measurements used |
| `soft_trigger_detected` | bool | `true` | ✓ | 2+ consecutive rises? |
| `status` | str | `PASS` | ✓ | PASS = SNR gate met; FAIL_SNR = below threshold |

**Constraints**:
- Only if n_measurements ≥ 3
- trend = NONE if status = FAIL_SNR (despite p < 0.05)
- z_score sign matches slope sign
- snr ≥ 0
- Sorted by p_value ascending (highest confidence trends first)

**CSV Template**:
```csv
borehole_id,parameter,trend,z_score,p_value,snr,slope,n_measurements,soft_trigger_detected,status
holon_nt_1,TCE,ALERT,2.45,0.014,0.52,4.29,7,true,PASS
holon_nt_2,Ni,WATCH,1.23,0.218,0.31,2.1,6,true,PASS
holon_nt_3,PFOA,NONE,0.5,0.614,0.12,0.3,5,false,FAIL_SNR
```

---

## CSV 5: monitoring_gaps.csv

**Purpose**: Identify boreholes with long monitoring silence

**Rows**: One per borehole with gap ≥12 months  
**Approx. Count**: 10–50

| Column | Type | Example | Required | Notes |
|--------|------|---------|----------|-------|
| `borehole_id` | str | `holon_nt_2` | ✓ | Canonical ID |
| `last_measurement_date` | str (YYYY-MM-DD) | `2022-06-10` | ✓ | Date of most recent measurement |
| `months_silent` | int | 47 | ✓ | Months since last measurement (as of report date) |
| `previous_max_bucket` | int | 6 | ✓ | Highest bucket before silence |
| `previous_max_parameter` | str | `TCE` | □ | Which parameter was at max |
| `last_concentration` | float | `5000` | □ | Final measured concentration |
| `assessment` | str | `HIGH` | □ | Priority: HIGH (was at high bucket), MEDIUM, LOW |

**Constraints**:
- Only include if months_silent ≥ 12
- previous_max_bucket derived from prior measurements before gap
- Sorted by months_silent descending (longest silence first)

**CSV Template**:
```csv
borehole_id,last_measurement_date,months_silent,previous_max_bucket,previous_max_parameter,last_concentration,assessment
holon_nt_2,2022-06-10,47,6,TCE,5000,HIGH
holon_p_08,2023-11-15,30,4,Cr(VI),850,MEDIUM
```

---

## CSV 6: figure_ready_series.csv

**Purpose**: Time series data formatted for chart rendering (one row per measurement + derived fields)

**Rows**: Superset of measurements_scoped.csv with added bucket info  
**Approx. Count**: 2,000–5,000

| Column | Type | Example | Required | Notes |
|--------|------|---------|----------|-------|
| `borehole_id` | str | `holon_nt_1` | ✓ | Canonical ID |
| `parameter` | str | `TCE` | ✓ | Contaminant |
| `date` | str (YYYY-MM-DD) | `2026-01-15` | ✓ | Measurement date |
| `concentration` | float | `35.2` | ✓ | Measured value (ppb) |
| `dws` | float | `10` | ✓ | DWS for this parameter |
| `c_max_5y_at_date` | float | `45.6` | ✓ | What was C_max as of this date? |
| `bucket_at_date` | int | 5 | ✓ | What was bucket as of this date? |
| `percentage_of_dws` | float | `352` | □ | (concentration / dws) × 100 |

**Constraints**:
- One row per measurement (not aggregated)
- c_max_5y_at_date = max of measurements up to and including this date (rolling max)
- bucket_at_date = calculate_bucket(c_max_5y_at_date, dws)
- Sorted by borehole_id, parameter, date ascending

**CSV Template**:
```csv
borehole_id,parameter,date,concentration,dws,c_max_5y_at_date,bucket_at_date,percentage_of_dws
holon_nt_1,TCE,2020-01-15,5.23,10,5.23,2,52.3
holon_nt_1,TCE,2020-06-22,6.8,10,6.8,2,68
holon_nt_1,TCE,2026-01-05,35.2,10,45.6,5,352
```

---

## Generation Scripts (Phase H+ Implementation)

```bash
# 1. Parse Excel → raw measurements
python scripts/parse_excel.py --zone holon \
  --output holon/02_data/measurements_scoped.csv

# 2. Calculate trends, severity, etc.
python scripts/trend_analysis.py --zone holon \
  --output holon/02_data/trends_by_well_parameter.csv

python scripts/forensics_analyzer.py --zone holon \
  --output holon/02_data/severity_by_well_family.csv

# 3. Aggregate into 6 CSVs
python scripts/generate_data_pack.py --zone holon \
  --output-dir holon/02_data/
```

**Output**: All 6 CSVs in `holon/02_data/`

---

## Quality Assurance

Before using Data Pack:

- [ ] All 6 CSVs present
- [ ] No null values in "Required" columns
- [ ] Concentrations are numeric (no "<LOD" strings)
- [ ] Dates in ISO format (YYYY-MM-DD)
- [ ] Bucket values ∈ [0, 8]
- [ ] DWS values > 0
- [ ] Boreholes match zone scope
- [ ] Units are all "ppb" (normalized)

---

**Version**: 1.0  
**Status**: ✓ SPECIFICATION FINAL (Implementation in progress)  
**Last Updated**: 2026-05-27
