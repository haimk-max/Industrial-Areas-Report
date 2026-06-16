"""Build the figure-engine lean_workspace inputs for a V5 zone.

Context: the figure layer (scripts/report_designed/data_loader.py + svg_charts.py)
was written for the Holon V4 "lean_workspace" layout. New V5 zones produce data
under {Zone}/02_data/ (Structured Data Pack) and {Zone}/data/ (raw parse output)
instead. This adapter reshapes the existing zone data into the exact CSVs the
figure engine consumes — WITHOUT recomputing anything (no new severity, no new
trends). It is a pure data-reshaping bridge so the generic V5 HTML generator
(generate_holon_v5_html.py --zone <z>) can render figures for any V5 zone.

Outputs (under {Zone}/lean_workspace/):
  02_data_filtered/measurements_alert.csv
  04_deterministic_anchors/severity_index_2025_{zone}.csv
  04_deterministic_anchors/borehole_classification_all.csv
  03_evidence_index/data_availability_index.csv

Inputs:
  {Zone}/data/measurements.csv          (raw parse — already in alert schema)
  {Zone}/data/boreholes.csv             (ITM coords, name_he)
  {Zone}/02_data/severity_by_well_family.csv  (V5 severity, C_max_5y based)

Usage:
  python scripts/build_zone_lean_workspace.py --zone Raanana
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent

# Family classification by canonical short param_code (matches scripts/param_families.py intent).
CVOC_CODES = {"TCEY", "TECE", "TCET", "TCEN", "CCL4", "CHLF", "MDCB", "PDCB", "MCBZ",
              "DCB13", "TEC12", "TEC22", "TRPR3", "TCFM"}
METALS_CODES = {"CR", "NI", "AS", "SE", "U", "BA", "ZN", "PB", "CD", "FE", "AL", "MN", "CU", "MO"}
FUEL_CODES = {"BENZ", "MTBE", "TOLU", "ETBN", "TRMB4", "TRMB5"}
PFAS_CODES = {"PFHxS", "PFOA", "PFBS", "PFDS", "PFHpS", "PFHxA", "82FTS", "ADONA", "PFBA"}


def _family_for(code) -> str | None:
    if not isinstance(code, str):
        return None
    c = code.strip()
    if c in CVOC_CODES:
        return "CVOC"
    if c in METALS_CODES:
        return "METALS"
    if c in FUEL_CODES:
        return "FUEL"
    if c in PFAS_CODES:
        return "PFAS"
    return None


def build(zone_dir: Path, zone_lc: str) -> None:
    ws = zone_dir / "lean_workspace"
    (ws / "02_data_filtered").mkdir(parents=True, exist_ok=True)
    (ws / "03_evidence_index").mkdir(parents=True, exist_ok=True)
    (ws / "04_deterministic_anchors").mkdir(parents=True, exist_ok=True)

    meas = pd.read_csv(zone_dir / "data" / "measurements.csv")
    boreholes = pd.read_csv(zone_dir / "data" / "boreholes.csv")
    sev = pd.read_csv(zone_dir / "02_data" / "severity_by_well_family.csv")

    # 1) measurements_alert.csv — figure engine matches on param_code = FULL NAME
    #    (Holon's param_code held full names). Raanana's param_code holds short codes
    #    and param_name holds the full names. Bridge by setting param_code = param_name.
    m = meas.copy()
    m["param_code"] = m["param_name"]
    m.to_csv(ws / "02_data_filtered" / "measurements_alert.csv", index=False)

    # 2) severity_index_2025_{zone}.csv — engine columns: borehole, name_he, family, max_bucket
    name_map = dict(zip(boreholes["canonical_id"], boreholes["name_he"]))
    sev_out = sev.rename(columns={
        "canonical_well_id": "borehole",
        "severity_index": "max_bucket",
        "lead_parameter_by_family": "contributing_param",
        "ratio_to_dws": "contributing_pct",
        "max_value_date": "contributing_date",
    }).copy()
    sev_out["name_he"] = sev_out["borehole"].map(name_map)
    sev_out = sev_out[["borehole", "name_he", "family", "max_bucket",
                       "contributing_param", "contributing_pct", "contributing_date"]]
    sev_out.to_csv(ws / "04_deterministic_anchors" / f"severity_index_2025_{zone_lc}.csv", index=False)

    # 3) borehole_classification_all.csv — for the map. Columns the engine reads:
    #    borehole_id, borehole_name, east_itm, north_itm, severity_bucket, families
    sev_pivot = sev.pivot_table(index="canonical_well_id", columns="family",
                                values="severity_index", aggfunc="max").fillna(0)
    rows = []
    for _, b in boreholes.iterrows():
        bid = b["canonical_id"]
        fam_buckets = sev_pivot.loc[bid].to_dict() if bid in sev_pivot.index else {}
        present = [f for f in ["CVOC", "METALS", "PFAS", "FUEL"] if fam_buckets.get(f, 0) > 0]
        max_bucket = max(fam_buckets.values()) if fam_buckets else 0.0
        rows.append({
            "borehole_id": bid,
            "borehole_name": b["name_he"],
            "east_itm": b["itm_easting"],
            "north_itm": b["itm_northing"],
            "severity_bucket": float(max_bucket),
            "families": ";".join(present),
            "num_families": len(present),
            "classification": "STABLE",
            "is_alert": max_bucket >= 5,
        })
    pd.DataFrame(rows).to_csv(
        ws / "04_deterministic_anchors" / "borehole_classification_all.csv", index=False)

    # 4) data_availability_index.csv — for monitoring gaps figure.
    #    Columns: borehole, name_he, family, param_code, param_name,
    #    first_sample_date, last_sample_date, n_samples
    m2 = meas.copy()
    m2["family"] = m2["param_code"].map(_family_for)
    m2 = m2.dropna(subset=["family"])
    da = m2.groupby(["canonical_id", "name_he", "family", "param_code", "param_name"]).agg(
        first_sample_date=("date", "min"),
        last_sample_date=("date", "max"),
        n_samples=("date", "count"),
    ).reset_index().rename(columns={"canonical_id": "borehole"})
    da.to_csv(ws / "03_evidence_index" / "data_availability_index.csv", index=False)

    print(f"✓ lean_workspace built for {zone_dir.name}")
    print(f"  measurements_alert.csv: {len(m)} rows")
    print(f"  severity_index_2025_{zone_lc}.csv: {len(sev_out)} rows")
    print(f"  borehole_classification_all.csv: {len(rows)} rows")
    print(f"  data_availability_index.csv: {len(da)} rows")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build figure-engine lean_workspace for a V5 zone.")
    ap.add_argument("--zone", required=True, help="Zone dir name (e.g., Raanana)")
    args = ap.parse_args()
    zone_dir = REPO_ROOT / args.zone.capitalize()
    if not zone_dir.exists():
        raise FileNotFoundError(f"Zone dir not found: {zone_dir}")
    build(zone_dir, args.zone.lower())


if __name__ == "__main__":
    main()
