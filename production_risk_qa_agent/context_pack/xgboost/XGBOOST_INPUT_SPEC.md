# XGBOOST Risk Classification Interface — Input/Output Specification

**Purpose**: Generic interface for XGBOOST risk classification model outputs to be consumed by the Q&A system prompt.

**Status**: SCHEMA DEFINITION — External system ("המערכת ההיא") will populate this format with real predictions. This file defines the expected schema and sample format.

---

## Input Format (What the Q&A System Expects)

The XGBOOST model produces predictions and feature importance scores for wells in the zone. The Q&A system consumes these as CSV files with the following schema:

### 1. Well-Level Risk Predictions (`xgboost_well_predictions.csv`)

**Columns**:
```
canonical_well_id | predicted_risk_class | risk_probability | model_version | prediction_date_utc | comments
```

**Data Types**:
- `canonical_well_id` (string): Must match exactly with `zone_wells.csv`
- `predicted_risk_class` (enum): One of `{low, moderate, high, very_high}`
- `risk_probability` (float, 0–1): Normalized probability; higher = more risk
- `model_version` (string): Semantic version, e.g., "1.0.0", "1.1.0-beta"
- `prediction_date_utc` (ISO 8601): When prediction was made
- `comments` (string, optional): Notes on prediction (e.g., "insufficient data", "recent change")

**Example Row**:
```
מק_חולון_12,moderate,0.62,1.0.0,2026-06-17T10:30:00Z,Sufficient recent data
פ_אזור_מקור_חקלאי,high,0.78,1.0.0,2026-06-17T10:30:00Z,
```

### 2. Feature Importance / SHAP Explanations (`xgboost_feature_importance.csv`)

**Columns**:
```
canonical_well_id | feature_name | feature_value | shap_contribution | contribution_direction | feature_category
```

**Data Types**:
- `canonical_well_id` (string): Well ID
- `feature_name` (string): Name of the feature used in prediction (e.g., "latest_cvoc_concentration", "trend_mann_kendall_z", "distance_to_facility")
- `feature_value` (string): The actual value of the feature (e.g., "8,750 µg/L", "2.13", "45 meters")
- `shap_contribution` (float): SHAP value (positive = increases risk, negative = decreases risk)
- `contribution_direction` (enum): `{↑ risk, ↓ risk, ~neutral}` — human-readable summary
- `feature_category` (enum): One of `{contamination, trend, hydrogeology, distance, monitoring_gap, other}`

**Example Rows**:
```
מק_חולון_12,latest_cvoc_concentration,8750 µg/L,0.35,↑ risk,contamination
מק_חולון_12,trend_mann_kendall_z,1.87,0.12,↑ risk,trend
מק_חולון_12,distance_to_facility_m,45,0.08,↑ risk,distance
פ_אזור_מקור_חקלאי,latest_cvoc_concentration,0 µg/L,-0.02,↓ risk,contamination
```

---

## Output Format (What the Q&A System Produces)

The Q&A system does NOT produce XGBOOST predictions. It consumes the above CSV files and outputs:
- **Short answer text** (Hebrew, 2–4 sentences) to the user's question
- **Standardized risk cards** for each affected production/supply well

See `SYSTEM_PROMPT.md` for output template.

---

## Schema Validation

Before the Q&A system processes XGBOOST input, it performs these checks (manually or via script):

1. ✓ All `canonical_well_id` in XGBOOST files exist in `zone_wells.csv`
2. ✓ `predicted_risk_class` values are valid enum members
3. ✓ `risk_probability` values in range [0, 1]
4. ✓ No duplicate rows (one prediction per well per model version)
5. ✓ `prediction_date_utc` is valid ISO 8601

**Failure mode**: If validation fails, the Q&A system should **clearly state** which wells have invalid data and proceed with available data only.

---

## Multi-Model Support

If multiple XGBOOST model versions exist, the Q&A system prioritizes by `model_version` (latest first). When models disagree on risk classification:
- **Report both** (e.g., "Model 1.0.0 predicts HIGH, Model 1.1.0 predicts MODERATE")
- **Explicitly flag** uncertainty to the user
- Do NOT silently choose one model

---

## Example: Full Integration

**File 1: `xgboost_well_predictions.csv`**
```csv
canonical_well_id,predicted_risk_class,risk_probability,model_version,prediction_date_utc,comments
מק_חולון_12,moderate,0.62,1.0.0,2026-06-17T10:30:00Z,Data from last 3 years
מק_חולון_14,moderate,0.54,1.0.0,2026-06-17T10:30:00Z,Moderate Cr; monitoring active
פ_אזור_מקור_חקלאי,low,0.18,1.0.0,2026-06-17T10:30:00Z,Lowest contamination in zone
פ_מקוה_ישראל_רוטשילד,moderate,0.59,1.0.0,2026-06-17T10:30:00Z,TCE detected but stable
```

**File 2: `xgboost_feature_importance.csv`**
```csv
canonical_well_id,feature_name,feature_value,shap_contribution,contribution_direction,feature_category
מק_חולון_12,latest_cvoc_concentration,8750 µg/L,0.35,↑ risk,contamination
מק_חולון_12,severity_index,8,0.18,↑ risk,contamination
מק_חולון_12,trend_mann_kendall_z,1.87,0.09,↑ risk,trend
מק_חולון_12,distance_to_facility_m,45,0.02,↑ risk,distance
מק_חולון_14,latest_cr_concentration,331 µg/L,0.20,↑ risk,contamination
מק_חולון_14,distance_to_facility_m,120,0.18,↑ risk,distance
מק_חולון_14,trend_mann_kendall_p,0.062,-0.02,↓ risk,trend
פ_אזור_מקור_חקלאי,latest_cvoc_concentration,0 µg/L,-0.18,↓ risk,contamination
פ_אזור_מקור_חקלאי,latest_metals_concentration,5 µg/L,-0.10,↓ risk,contamination
פ_מקוה_ישראל_רוטשילד,latest_cvoc_concentration,120 µg/L,0.15,↑ risk,contamination
פ_מקוה_ישראל_רוטשילד,trend_mann_kendall_p,0.34,-0.01,↓ risk,trend
```

**Q&A System Usage**:
When answering "What is the risk to our production wells?", the system:
1. Reads the two XGBOOST CSVs
2. Matches wells to `zone_wells.csv` (filter `well_type == private_production`)
3. Reads severity + trends from deterministic data CSVs
4. For each production well, outputs a risk card like:

```
**מק חולון 12 (קידוח מעורבב)**
─────────────────────────────
רמת סיכון: MODERATE (Severity 8, XGBOOST 62%)
מזהמים מובילים: TCE (8,750 µg/L, 175,000% DWS), 1,1-DCE (1,939 µg/L)
מקור משוער: נת חולון ± 50m (Cr+Ni + TCE decay chain) — רמת ודאות: בינונית
מגמה: TCE יציב; PCE עולה (p=0.034)
פער ניטור: אין (מעודכן 2026)
המלצה: המשך ניטור רבעוני TCE + תרכובות דעיכה; זקוק לבדיקה מקורות
```

---

## Notes for System Integration

- The Q&A system is **NOT** responsible for producing XGBOOST predictions
- The Q&A system **DOES** integrate XGBOOST outputs with deterministic data (severity, trends, forensics)
- If XGBOOST data is unavailable, the Q&A system falls back to deterministic risk assessment only
- XGBOOST results are treated as **supporting evidence**, not definitive proof of source attribution
