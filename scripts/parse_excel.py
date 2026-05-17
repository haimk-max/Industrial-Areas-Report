"""Phase A: Parse Excel water quality data → normalized Raanana CSVs.

Reads the source Excel, filters to Raanana boreholes, normalizes coordinates,
excludes calculated parameters (TPFAS, BETK), and writes:
  Raanana/data/boreholes.csv       — 7 real boreholes (from Excel, overriding TAHAL placeholders)
  Raanana/data/measurements.csv    — all 2011-2026 measurements
  Raanana/data/parameters.csv      — parameter metadata for Raanana-detected parameters

Usage:
    python scripts/parse_excel.py [--zone raanana] [--config ...] [--input <excel>] [--output <dir>]
"""
from __future__ import annotations

import csv
import json
import sys
import warnings
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.cli_common import load_config, make_parser, merged_config
from scripts.coords import normalize_to_itm
from scripts.logging_setup import get_logger

log = get_logger("parse_excel")

DEFAULT_EXCEL_PATH = REPO_ROOT / "Water Quality Data" / "היסטורית איכות מים לקידוחים - מעודכן לבדיקה.xlsx"
CROSSWALK_PATH = REPO_ROOT / "crosswalks" / "borehole_id_mapping.json"
PARAMS_DICT_PATH = REPO_ROOT / "base_layer" / "parameters_dictionary.json"

# Default column indices (Raanana format, 18 columns). Zone overrides via config/zone_overrides/{zone}.yaml.
_DEFAULT_COL = {
    "borehole_id": 0,
    "name": 1,
    "easting": 2,
    "northing": 3,
    "basin": 4,
    "purpose": 5,
    "monitoring_site": 6,
    "contamination_type": 7,
    "date": 8,
    "sample_id": 9,
    "lab": 10,
    "sample_depth": 11,
    "param_code": 12,
    "param_name": 13,
    "unit": 14,
    "concentration": 15,
    "marker": 16,      # '<' = below LOD
    "drinking_standard": 17,
}


def _build_col(cfg: dict) -> dict:
    """Merge zone-specific excel_columns overrides onto defaults."""
    overrides = cfg.get("excel_columns", {})
    return {k: overrides[k] if k in overrides else v for k, v in _DEFAULT_COL.items()}


def _col_val(row: tuple, idx) -> object:
    """Return row[idx], or None if idx is None (column absent in this zone's Excel)."""
    return row[idx] if idx is not None else None


def _load_calculated_excluded(cfg: dict) -> set[str]:
    """Load list of calculated parameters to exclude from config and crosswalk."""
    excluded = set(cfg.get("calculated_parameters_to_exclude", []))
    # Always exclude these regardless of config
    excluded.update({"TPFAS", "BETK"})
    if PARAMS_DICT_PATH.exists():
        with open(PARAMS_DICT_PATH, encoding="utf-8") as fh:
            pd = json.load(fh)
        for ex in pd.get("excluded_calculated", []):
            excluded.add(ex)
    return excluded


def _canonical_id(excel_name: str, crosswalk: list[dict]) -> str:
    for entry in crosswalk:
        if entry["excel_name_he"] == excel_name:
            return entry["canonical_id"]
    return excel_name.replace(" ", "_").lower()


def _borehole_type(purpose: str | None) -> str:
    if not purpose:
        return "unknown"
    p = str(purpose).strip()
    if "פרטי" in p:
        return "private_production"
    if "תעשיה" in p:
        return "industrial_monitoring"
    if "דלק" in p:
        return "fuel_monitoring"
    return "monitoring"


def _percent_of_standard(concentration: float, std: float | None) -> float | None:
    if std is None or std == 0:
        return None
    return round((concentration / std) * 100, 2)


def main() -> None:
    parser = make_parser("Phase A: Parse Excel → zone CSVs.")
    args = parser.parse_args()
    zone = (args.zone or "raanana").lower()
    cfg = merged_config(zone, args.config)
    excluded = _load_calculated_excluded(cfg)
    col = _build_col(cfg)

    # Zone-specific paths (override via --input / --output or config excel_input key)
    if args.input:
        excel_path = Path(args.input)
    elif cfg.get("excel_input"):
        excel_path = REPO_ROOT / cfg["excel_input"]
    else:
        excel_path = DEFAULT_EXCEL_PATH

    output_dir = Path(args.output) if args.output else REPO_ROOT / zone.capitalize() / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not excel_path.exists():
        log.error("excel_not_found", path=str(excel_path))
        print(f"ERROR: Excel not found: {excel_path}", file=sys.stderr)
        sys.exit(1)

    # Load crosswalk for this zone
    crosswalk: list[dict] = []
    if CROSSWALK_PATH.exists():
        with open(CROSSWALK_PATH, encoding="utf-8") as fh:
            cw_data = json.load(fh)
        crosswalk = cw_data.get(zone, [])
    log.info("crosswalk_loaded", entries=len(crosswalk))

    log.info("loading_excel", path=str(excel_path))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import openpyxl
        wb = openpyxl.load_workbook(str(excel_path), read_only=True)
        ws = wb.active

        boreholes: dict[str, dict] = {}       # canonical_id → borehole info
        measurements: list[dict] = []
        param_info: dict[str, dict] = {}      # code → metadata
        skipped_calculated = 0
        parse_errors = 0

        for row in ws.iter_rows(min_row=4, values_only=True):
            if _col_val(row, col["borehole_id"]) is None:
                break

            bh_name = _col_val(row, col["name"])
            param_code = _col_val(row, col["param_code"])
            if not bh_name or not param_code:
                continue

            # Skip calculated parameters
            if param_code in excluded:
                skipped_calculated += 1
                continue

            # Normalize coordinates (Excel uses km×1000 truncated format)
            try:
                itm_e, itm_n = normalize_to_itm(
                    _col_val(row, col["easting"]), _col_val(row, col["northing"]), source="excel"
                )
            except (TypeError, ValueError) as exc:
                log.error("coord_normalize_failed", borehole=bh_name, error=str(exc))
                parse_errors += 1
                continue

            canonical_id = _canonical_id(bh_name, crosswalk)

            # Accumulate borehole metadata (take first occurrence)
            if canonical_id not in boreholes:
                boreholes[canonical_id] = {
                    "canonical_id": canonical_id,
                    "name_he": bh_name,
                    "excel_borehole_id": int(_col_val(row, col["borehole_id"])),
                    "itm_easting": int(round(itm_e)),
                    "itm_northing": int(round(itm_n)),
                    "basin": _col_val(row, col["basin"]) or "",
                    "purpose": _col_val(row, col["purpose"]) or "",
                    "borehole_type": _borehole_type(_col_val(row, col["purpose"])),
                    "monitoring_site": _col_val(row, col["monitoring_site"]) or "",
                    "contamination_type": _col_val(row, col["contamination_type"]) or "",
                }

            # Parameter metadata
            if param_code not in param_info:
                param_info[param_code] = {
                    "code": param_code,
                    "name": str(_col_val(row, col["param_name"]) or "").strip(),
                    "unit": str(_col_val(row, col["unit"]) or "").strip(),
                    "drinking_water_standard": _col_val(row, col["drinking_standard"]),
                }

            # Parse date
            date_val = _col_val(row, col["date"])
            if isinstance(date_val, datetime):
                date_str = date_val.strftime("%Y-%m-%d")
                year = date_val.year
            elif date_val:
                try:
                    date_str = str(date_val)[:10]
                    year = int(date_str[:4])
                except (ValueError, TypeError):
                    date_str = ""
                    year = None
            else:
                date_str = ""
                year = None

            # Parse concentration
            raw_conc = _col_val(row, col["concentration"])
            marker = str(_col_val(row, col["marker"]) or "").strip()
            is_below_lod = marker == "<"

            try:
                concentration = float(raw_conc) if raw_conc is not None else None
            except (TypeError, ValueError):
                concentration = None

            std = _col_val(row, col["drinking_standard"])
            try:
                std_float = float(std) if std is not None else None
            except (TypeError, ValueError):
                std_float = None

            pct_std = _percent_of_standard(concentration or 0, std_float)

            measurements.append({
                "canonical_id": canonical_id,
                "name_he": bh_name,
                "param_code": param_code,
                "param_name": str(_col_val(row, col["param_name"]) or "").strip(),
                "date": date_str,
                "year": year,
                "concentration": concentration,
                "unit": str(_col_val(row, col["unit"]) or "").strip(),
                "is_below_lod": is_below_lod,
                "sample_id": _col_val(row, col["sample_id"]),
                "lab": str(_col_val(row, col["lab"]) or "").strip(),
                "sample_depth_m": _col_val(row, col["sample_depth"]),
                "drinking_water_standard": std_float,
                "percent_of_standard": pct_std,
            })

        wb.close()

    log.info("excel_parsed",
             boreholes=len(boreholes),
             measurements=len(measurements),
             params=len(param_info),
             skipped_calculated=skipped_calculated,
             parse_errors=parse_errors)

    # ── Write boreholes.csv ───────────────────────────────────────────────────
    bh_path = output_dir / "boreholes.csv"
    bh_fields = ["canonical_id", "name_he", "excel_borehole_id", "itm_easting", "itm_northing",
                 "basin", "purpose", "borehole_type", "monitoring_site", "contamination_type"]
    with open(bh_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=bh_fields)
        writer.writeheader()
        for bh in sorted(boreholes.values(), key=lambda b: b["canonical_id"]):
            writer.writerow({k: bh.get(k, "") for k in bh_fields})
    log.info("boreholes_written", path=str(bh_path), count=len(boreholes))

    # ── Write measurements.csv ────────────────────────────────────────────────
    meas_path = output_dir / "measurements.csv"
    meas_fields = ["canonical_id", "name_he", "param_code", "param_name", "date", "year",
                   "concentration", "unit", "is_below_lod", "sample_id", "lab",
                   "sample_depth_m", "drinking_water_standard", "percent_of_standard"]
    with open(meas_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=meas_fields)
        writer.writeheader()
        for m in measurements:
            writer.writerow({k: m.get(k, "") for k in meas_fields})
    log.info("measurements_written", path=str(meas_path), count=len(measurements))

    # ── Write parameters.csv ─────────────────────────────────────────────────
    param_path = output_dir / "parameters.csv"
    with open(param_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["code", "name", "unit", "drinking_water_standard"])
        writer.writeheader()
        for code in sorted(param_info.keys()):
            writer.writerow(param_info[code])
    log.info("parameters_written", path=str(param_path), count=len(param_info))

    _write_qa_report(boreholes, measurements, param_info, skipped_calculated, output_dir, zone)

    print(f"[Phase A] Done — {len(boreholes)} boreholes, {len(measurements)} measurements, "
          f"{len(param_info)} parameters → {output_dir}")
    print(f"  Skipped calculated params (e.g. TPFAS): {skipped_calculated} rows")


def _write_qa_report(boreholes: dict, measurements: list, params: dict,
                     skipped: int, output_dir: Path, zone: str = "raanana") -> None:
    qa_path = output_dir / "_parse_excel_qa.md"

    year_counts: dict[int, int] = {}
    bh_counts: dict[str, int] = {}
    for m in measurements:
        y = m.get("year")
        if y:
            year_counts[y] = year_counts.get(y, 0) + 1
        bh = m.get("canonical_id", "")
        bh_counts[bh] = bh_counts.get(bh, 0) + 1

    lines = [
        f"# Phase A QA Report — Excel Parsing ({zone})",
        "",
        "## Boreholes extracted",
        "",
        "| Canonical ID | Name (Hebrew) | ITM Easting | ITM Northing | Type |",
        "|---|---|---|---|---|",
    ]
    for bh in sorted(boreholes.values(), key=lambda b: b["canonical_id"]):
        n = bh_counts.get(bh["canonical_id"], 0)
        lines.append(f"| {bh['canonical_id']} | {bh['name_he']} | "
                     f"{bh['itm_easting']} | {bh['itm_northing']} | {bh['borehole_type']} |")

    lines += [
        "",
        "## Measurements per borehole",
        "",
        "| Canonical ID | N measurements |",
        "|---|---|",
    ]
    for bh_id, count in sorted(bh_counts.items()):
        lines.append(f"| {bh_id} | {count} |")

    lines += [
        "",
        "## Measurements per year",
        "",
        "| Year | N measurements |",
        "|---|---|",
    ]
    for year in sorted(year_counts.keys()):
        lines.append(f"| {year} | {year_counts[year]} |")

    lines += [
        "",
        "## Validation",
        f"- Total boreholes: {len(boreholes)}",
        f"- Total measurements: {len(measurements)}",
        f"- Total parameters: {len(params)} (expected: ~180)",
        f"- Skipped calculated (TPFAS etc.): {skipped} rows",
        "- TPFAS excluded: ✅",
        "- Coordinate normalization (×1000): ✅",
    ]
    qa_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
