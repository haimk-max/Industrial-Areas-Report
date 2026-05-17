#!/usr/bin/env python3
"""
Generate Holon Structured Data Pack (7 CSVs) for V5 hybrid pipeline.

Reference: DATA_PIPELINE_SPEC.md

Output:
  Holon/02_data/zone_wells.csv
  Holon/02_data/measurements_scoped.csv
  Holon/02_data/latest_results.csv
  Holon/02_data/severity_by_well_family.csv
  Holon/02_data/trends_by_well_parameter.csv
  Holon/02_data/monitoring_gaps.csv
  Holon/02_data/figure_ready_series.csv
"""

import os
import sys
import csv
from pathlib import Path
from datetime import datetime, timedelta
import json
from collections import defaultdict

import pandas as pd
import numpy as np


def ensure_output_dir():
    """Create Holon/02_data/ directory if it doesn't exist."""
    output_dir = Path("Holon/02_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def load_existing_data():
    """Load existing Holon CSV files."""
    boreholes = pd.read_csv("Holon/data/boreholes.csv")
    measurements = pd.read_csv("Holon/data/measurements.csv")
    parameters = pd.read_csv("Holon/data/parameters.csv")
    trends = pd.read_csv("Holon/data/trends.csv")

    print(f"Loaded: {len(boreholes)} boreholes, {len(measurements)} measurements, "
          f"{len(parameters)} parameters, {len(trends)} trend rows")

    return boreholes, measurements, parameters, trends


def create_zone_wells(boreholes, output_dir):
    """
    Create zone_wells.csv: list of all boreholes in scope.

    Columns (minimal):
      canonical_well_id, name_he, itm_easting, itm_northing, well_type, zone_scope_source
    """
    wells = boreholes[["canonical_id", "name_he", "itm_easting", "itm_northing",
                        "borehole_type", "monitoring_site"]].copy()
    wells.columns = ["canonical_well_id", "name_he", "itm_easting", "itm_northing",
                     "well_type", "monitoring_site"]

    # Set zone_scope_source to "Holon_main_industrial"
    wells["zone_scope_source"] = "Holon_main_industrial"

    # Reorder columns for readability
    wells = wells[["canonical_well_id", "name_he", "itm_easting", "itm_northing",
                   "well_type", "zone_scope_source", "monitoring_site"]]

    output_path = output_dir / "zone_wells.csv"
    wells.to_csv(output_path, index=False)
    print(f"✓ {output_path} ({len(wells)} rows)")

    return wells


def create_measurements_scoped(measurements, parameters, boreholes, output_dir):
    """
    Create measurements_scoped.csv: all scoped measurements with full traceability.

    Columns (mandatory):
      canonical_well_id, original_well_name, well_type, zone_scope_source,
      parameter_canonical, parameter_original, unit_original, unit_standardized,
      dws_value, result_value, result_date, result_qualifier, source_file, source_row_or_page
    """

    # Measurements already has param_code, param_name, unit, drinking_water_standard
    m = measurements.copy()

    # Add borehole metadata (well_type, name_he)
    b_meta = boreholes[["canonical_id", "borehole_type", "name_he"]].copy()
    merged = m.merge(b_meta, left_on="canonical_id", right_on="canonical_id",
                     how="left", suffixes=("_meas", "_bore"))

    # Construct mandatory columns
    scoped = pd.DataFrame()
    scoped["canonical_well_id"] = merged["canonical_id"]
    scoped["original_well_name"] = merged["name_he_bore"]
    scoped["well_type"] = merged["borehole_type"].fillna("monitoring")
    scoped["zone_scope_source"] = "Holon_main_industrial"
    scoped["parameter_canonical"] = merged["param_code"]
    scoped["parameter_original"] = merged["param_name"]
    scoped["unit_original"] = merged["unit"]
    scoped["unit_standardized"] = "µg/L"  # All standardized to µg/L (unit conversion not yet implemented)
    scoped["dws_value"] = merged["drinking_water_standard"]
    scoped["result_value"] = merged["concentration"]
    scoped["result_date"] = pd.to_datetime(merged["date"]).dt.strftime("%Y-%m-%d")

    # result_qualifier: infer from is_below_lod
    scoped["result_qualifier"] = "="
    scoped.loc[merged.get("is_below_lod", False) == True, "result_qualifier"] = "<"

    scoped["source_file"] = "Holon_current_monitoring_2024"  # Placeholder; would come from original source
    scoped["source_row_or_page"] = ""  # Placeholder; would come from original extraction metadata

    # Remove rows with NULL result_value
    scoped = scoped[scoped["result_value"].notna()]

    output_path = output_dir / "measurements_scoped.csv"
    scoped.to_csv(output_path, index=False)
    print(f"✓ {output_path} ({len(scoped)} rows)")

    return scoped


def create_latest_results(scoped, output_dir):
    """
    Create latest_results.csv: per-well × parameter, latest value only.

    Columns:
      canonical_well_id, parameter_canonical, latest_value, latest_date,
      unit_standardized, dws_value, ratio_to_dws, severity_index, last_updated_from
    """

    # Group by well and parameter, keep latest date
    latest = scoped.sort_values("result_date").groupby(
        ["canonical_well_id", "parameter_canonical"]
    ).tail(1).reset_index(drop=True)

    # Calculate severity index (0–8 bucket)
    # Formula: bucket(ratio_to_dws / 100), where ratio_to_dws = result_value / dws_value * 100
    latest["ratio_to_dws"] = (latest["result_value"] / latest["dws_value"] * 100).round(1)
    latest["severity_index"] = latest["ratio_to_dws"].apply(lambda x: bucket_severity(x))

    result = pd.DataFrame()
    result["canonical_well_id"] = latest["canonical_well_id"]
    result["parameter_canonical"] = latest["parameter_canonical"]
    result["latest_value"] = latest["result_value"]
    result["latest_date"] = latest["result_date"]
    result["unit_standardized"] = latest["unit_standardized"]
    result["dws_value"] = latest["dws_value"]
    result["ratio_to_dws"] = latest["ratio_to_dws"]
    result["severity_index"] = latest["severity_index"]
    result["last_updated_from"] = latest["source_file"]

    output_path = output_dir / "latest_results.csv"
    result.to_csv(output_path, index=False)
    print(f"✓ {output_path} ({len(result)} rows)")

    return result


def create_severity_by_well_family(scoped, output_dir, window_days=365*5):
    """
    Create severity_by_well_family.csv: per-well × family, max in 5y window.

    Families: CVOC, METALS, PFAS, FUEL

    Columns:
      canonical_well_id, family, max_value_window, max_value_date,
      window_start, window_end, lead_parameter_by_family, ratio_to_dws,
      severity_index, dws_reference_value
    """

    # Family mapping (simplified; real implementation would use param_families.py)
    family_map = {
        # CVOC: chlorinated volatile organic compounds
        "TCE": "CVOC", "TRICHLOROETHYLENE": "CVOC",
        "PCE": "CVOC", "PERCHLOROETHYLENE": "CVOC",
        "1,2-DCA": "CVOC", "1,2-DICHLOROETHANE": "CVOC",
        "VC": "CVOC", "VINYL CHLORIDE": "CVOC",
        "CVOC": "CVOC",
        "1,1,2-TRICHLOROETHANE": "CVOC",
        "1,1-DICHLOROETHANE": "CVOC",
        "1,2-DICHLOROPROPANE": "CVOC",
        "1,4 DIOXANE": "CVOC",

        # FUEL: petroleum products and benzene/toluene series
        "MTBE": "FUEL", "METHYL TERT-BUTYL ETHER": "FUEL",
        "BTEX": "FUEL",
        "BENZENE": "FUEL",
        "TOLUENE": "FUEL",
        "XYLENE": "FUEL",
        "ETHYLBENZENE": "FUEL",
        "1,2,4 TRIMETHYLBENZENE": "FUEL",
        "1,3,5 TRIMETHYLBENZENE": "FUEL",
        "2-CHLOROTOLUENE": "FUEL",
        "4-CHLOROTOLUENE": "FUEL",

        # METALS
        "CHROMIUM": "METALS",
        "CR(VI)": "METALS",
        "NICKEL": "METALS",
        "CADMIUM": "METALS",
        "COPPER": "METALS",
        "LEAD": "METALS",
        "IRON": "METALS",
        "MANGANESE": "METALS",

        # PFAS: per- and poly-fluoroalkyl substances
        "PFOA": "PFAS",
        "PERFLUOROOCTANOIC ACID": "PFAS",
        "PFOHXS": "PFAS",
        "PFHXS": "PFAS",
        "PERFLUOROHEXANE SULFONIC ACID": "PFAS",
        "PFOS": "PFAS",
        "PERFLUOROOCTANE SULFONIC ACID": "PFAS",
    }

    scoped_copy = scoped.copy()
    scoped_copy["result_date"] = pd.to_datetime(scoped_copy["result_date"])

    max_date = scoped_copy["result_date"].max()
    window_start = max_date - timedelta(days=window_days)

    # Filter to 5-year window
    windowed = scoped_copy[scoped_copy["result_date"] >= window_start].copy()

    # Assign family based on parameter
    windowed["family"] = windowed["parameter_canonical"].map(family_map).fillna("OTHER")

    # Group by well and family, find max
    family_results = []
    for (well_id, family), group in windowed.groupby(["canonical_well_id", "family"]):
        if family == "OTHER":
            continue

        max_row = group.loc[group["result_value"].idxmax()]

        family_results.append({
            "canonical_well_id": well_id,
            "family": family,
            "max_value_window": max_row["result_value"],
            "max_value_date": max_row["result_date"].strftime("%Y-%m-%d"),
            "window_start": window_start.strftime("%Y-%m-%d"),
            "window_end": max_date.strftime("%Y-%m-%d"),
            "lead_parameter_by_family": max_row["parameter_canonical"],
            "ratio_to_dws": (max_row["result_value"] / max_row["dws_value"] * 100),
            "severity_index": bucket_severity(max_row["result_value"] / max_row["dws_value"] * 100),
            "dws_reference_value": max_row["dws_value"],
        })

    result_df = pd.DataFrame(family_results)
    if len(result_df) > 0:
        result_df["ratio_to_dws"] = result_df["ratio_to_dws"].round(1)

    output_path = output_dir / "severity_by_well_family.csv"
    result_df.to_csv(output_path, index=False)
    print(f"✓ {output_path} ({len(result_df)} rows)")

    return result_df


def create_trends_by_well_parameter(trends_df, output_dir):
    """
    Create trends_by_well_parameter.csv: Mann-Kendall results per well × parameter.

    Columns:
      canonical_well_id, parameter_canonical, mann_kendall_z, mann_kendall_p, snr,
      soft_trigger_met, trend_classification, n_measurements, time_span_years, notes
    """

    trends_copy = trends_df.copy()

    # Rename columns to match schema
    trends_copy = trends_copy.rename(columns={
        "borehole_id": "canonical_well_id",
        "parameter": "parameter_canonical",
        "mk_z_5y": "mann_kendall_z",
        "mk_p_5y": "mann_kendall_p",
        "snr_5y": "snr",
        "n5": "n_measurements",
        "classification": "trend_classification",
    })

    # Add soft_trigger logic (2 consecutive rising values in 5y window)
    # Placeholder: assume True if classification is not STABLE/DECLINING/NONE
    trends_copy["soft_trigger_met"] = trends_copy["trend_classification"].isin(["RISING"]).astype(int)

    # Time span: assume 5 years for 5y analysis
    trends_copy["time_span_years"] = 5.0

    # Notes
    trends_copy["notes"] = ""
    trends_copy.loc[trends_copy["n_measurements"] < 5, "notes"] = "Low measurement count"

    result = trends_copy[[
        "canonical_well_id", "parameter_canonical", "mann_kendall_z", "mann_kendall_p",
        "snr", "soft_trigger_met", "trend_classification", "n_measurements",
        "time_span_years", "notes"
    ]].copy()

    # Remove rows where all MK values are NaN
    result = result[result[["mann_kendall_z", "mann_kendall_p", "snr"]].notna().any(axis=1)]

    output_path = output_dir / "trends_by_well_parameter.csv"
    result.to_csv(output_path, index=False)
    print(f"✓ {output_path} ({len(result)} rows)")

    return result


def create_monitoring_gaps(boreholes, trends_df, scoped, output_dir):
    """
    Create monitoring_gaps.csv: closed wells, low-n parameters, time gaps.

    Columns:
      canonical_well_id, parameter_canonical, last_measurement_date, is_active,
      reason_if_inactive, n_measurements_total, n_measurements_last_5y, coverage_note
    """

    gaps = []

    # Check for wells with no recent measurements (closing detection)
    for well_id in boreholes["canonical_id"].unique():
        well_measurements = scoped[scoped["canonical_well_id"] == well_id]

        if len(well_measurements) == 0:
            gaps.append({
                "canonical_well_id": well_id,
                "parameter_canonical": "overall",
                "last_measurement_date": "",
                "is_active": "false",
                "reason_if_inactive": "no_measurements",
                "n_measurements_total": 0,
                "n_measurements_last_5y": 0,
                "coverage_note": "No measurements found",
            })
        else:
            last_date = well_measurements["result_date"].max()

            # Check if well is closed (no measurements in last 2 years)
            days_since_last = (datetime.now() - pd.to_datetime(last_date)).days
            is_active = "true" if days_since_last < 730 else "false"
            reason = "closed" if days_since_last >= 730 else ""

            for param in well_measurements["parameter_canonical"].unique():
                param_meas = well_measurements[well_measurements["parameter_canonical"] == param]
                n_total = len(param_meas)
                n_5y = len(param_meas[param_meas["result_date"] >= (datetime.now() - timedelta(days=365*5)).strftime("%Y-%m-%d")])

                if n_5y < 5:
                    gaps.append({
                        "canonical_well_id": well_id,
                        "parameter_canonical": param,
                        "last_measurement_date": param_meas["result_date"].max(),
                        "is_active": is_active,
                        "reason_if_inactive": reason,
                        "n_measurements_total": n_total,
                        "n_measurements_last_5y": n_5y,
                        "coverage_note": f"Only {n_5y} measurements in 5y window" if n_5y > 0 else "No recent measurements",
                    })

    gaps_df = pd.DataFrame(gaps)

    output_path = output_dir / "monitoring_gaps.csv"
    gaps_df.to_csv(output_path, index=False)
    print(f"✓ {output_path} ({len(gaps_df)} rows)")

    return gaps_df


def create_figure_ready_series(scoped, output_dir):
    """
    Create figure_ready_series.csv: long-format time series for charting.

    Columns:
      canonical_well_id, parameter_canonical, date, value, severity_index,
      unit_standardized, include_in_trend_figure
    """

    series = scoped[[
        "canonical_well_id", "parameter_canonical", "result_date", "result_value",
        "unit_standardized"
    ]].copy()

    series.columns = ["canonical_well_id", "parameter_canonical", "date", "value",
                      "unit_standardized"]

    # Calculate severity index for each row
    series["severity_index"] = series["value"].apply(lambda x: bucket_severity(x) if pd.notna(x) else 0)

    # include_in_trend_figure: initially True for all active wells
    series["include_in_trend_figure"] = "true"

    output_path = output_dir / "figure_ready_series.csv"
    series.to_csv(output_path, index=False)
    print(f"✓ {output_path} ({len(series)} rows)")

    return series


def bucket_severity(ratio_to_dws):
    """
    Calculate severity index (0-8) from ratio to drinking water standard.

    Formula: bucket(ratio_to_dws / 100)

    0: 0-1%
    1: 1-5%
    2: 5-10%
    3: 10-50%
    4: 50-100%
    5: 100-200%
    6: 200-500%
    7: 500-1000%
    8: 1000%+
    """
    if pd.isna(ratio_to_dws) or ratio_to_dws <= 0:
        return 0

    if ratio_to_dws <= 1:
        return 0
    elif ratio_to_dws <= 5:
        return 1
    elif ratio_to_dws <= 10:
        return 2
    elif ratio_to_dws <= 50:
        return 3
    elif ratio_to_dws <= 100:
        return 4
    elif ratio_to_dws <= 200:
        return 5
    elif ratio_to_dws <= 500:
        return 6
    elif ratio_to_dws <= 1000:
        return 7
    else:
        return 8


def main():
    """Generate all 7 CSVs for Holon Structured Data Pack."""

    print("🔄 Generating Holon Structured Data Pack (7 CSVs)...\n")

    output_dir = ensure_output_dir()
    boreholes, measurements, parameters, trends = load_existing_data()

    print("\n📊 Creating CSVs...\n")

    wells = create_zone_wells(boreholes, output_dir)
    scoped = create_measurements_scoped(measurements, parameters, boreholes, output_dir)
    latest = create_latest_results(scoped, output_dir)
    severity = create_severity_by_well_family(scoped, output_dir)
    trends_result = create_trends_by_well_parameter(trends, output_dir)
    gaps = create_monitoring_gaps(boreholes, trends, scoped, output_dir)
    series = create_figure_ready_series(scoped, output_dir)

    print("\n✅ Holon Structured Data Pack complete!")
    print(f"   Output: {output_dir}/\n")


if __name__ == "__main__":
    main()
