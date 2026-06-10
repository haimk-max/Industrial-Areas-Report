"""Phase C: Generate all charts for Raanana zone report.

Charts produced:
  PFAS:    Raanana/charts/pfas_absolute.png + pfas_percent.png
  CVOC:    Raanana/charts/cvoc_nt1_absolute.png + cvoc_nt3_absolute.png + percent variants
  BTEX:    Raanana/charts/btex_paz_absolute.png
  Trends:  Raanana/charts/trend_<borehole>_<param>.png for key parameters

Usage:
    python scripts/generate_charts.py [--zone raanana] [--config ...]
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.charts.grouped_stacked import build_grouped_stacked
from scripts.charts.trend_chart import build_trend_chart
from scripts.cli_common import load_config, make_parser, merged_config
from scripts.logging_setup import get_logger

log = get_logger("generate_charts")

MEAS_PATH = REPO_ROOT / "Raanana" / "data" / "measurements.csv"
TRENDS_PATH = REPO_ROOT / "Raanana" / "data" / "trends.csv"
PRESETS_PATH = REPO_ROOT / "scripts" / "chart_presets.json"
OUTPUT_DIR = REPO_ROOT / "Raanana" / "charts"

# Short display names for boreholes (for chart x-axis labels)
BOREHOLE_DISPLAY = {
    "raanana_nt_1":           "נת רעננה 1",
    "raanana_nt_2":           "נת רעננה 2",
    "raanana_nt_3":           "נת רעננה 3",
    "raanana_nd_paz_hanofer": "נד פז הנופר",
    "raanana_nd_turbine":     "נד תחנת טורבינות",
    "raanana_p_18":           "פ רעננה 18",
    "raanana_p_25":           "פ רעננה 25",
}

# Key trend charts to generate (borehole_id, param_code)
KEY_TRENDS = [
    ("raanana_nt_1",           "TCEY"),   # TCE — critical contamination
    ("raanana_nt_3",           "TECE"),   # PCE
    ("raanana_nd_paz_hanofer", "BENZ"),   # Benzene at fuel station
    ("raanana_nd_turbine",     "PFOA"),   # PFOA at gas turbine
    ("raanana_nd_turbine",     "PFHxS"),  # PFHxS (highest PFAS)
    ("raanana_p_25",           "NO3"),    # Nitrate ALERT
    ("raanana_p_25",           "CHLF"),   # Chloroform WATCH
]


def _load_measurements_by_key(meas_path: Path) -> dict[tuple[str, str], list[dict]]:
    groups: dict[tuple[str, str], list[dict]] = {}
    with open(meas_path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = (row["canonical_id"], row["param_code"])
            groups.setdefault(key, []).append(row)
    return groups


def _load_max_concs(meas_path: Path) -> dict[str, dict[str, float]]:
    """Max concentration per (borehole, param_code)."""
    result: dict[str, dict[str, float]] = {}
    with open(meas_path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            bh = row["canonical_id"]
            code = row["param_code"]
            conc_str = row.get("concentration", "")
            if not conc_str or not conc_str.strip():
                continue
            try:
                conc = float(conc_str)
            except ValueError:
                continue
            result.setdefault(bh, {})
            result[bh][code] = max(result[bh].get(code, 0.0), conc)
    return result


def _load_trends(trends_path: Path) -> dict[tuple[str, str], dict]:
    trends: dict[tuple[str, str], dict] = {}
    with open(trends_path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            trends[(row["borehole_id"], row["parameter"])] = row
    return trends


def _build_stacked_data(
    max_concs: dict[str, dict[str, float]],
    borehole_ids: list[str],
    codes: list[str],
) -> dict[str, dict[str, float]]:
    """Build {borehole_display_name: {code: max_conc}} for chart input."""
    result = {}
    for bh_id in borehole_ids:
        display = BOREHOLE_DISPLAY.get(bh_id, bh_id)
        bh_data = max_concs.get(bh_id, {})
        result[display] = {code: bh_data.get(code, 0.0) for code in codes}
    return result


def _generate_trend_chart(
    bh_id: str,
    param_code: str,
    meas_groups: dict,
    trends: dict,
    output_dir: Path,
) -> Path | None:
    rows = meas_groups.get((bh_id, param_code), [])
    if not rows:
        return None

    rows_sorted = sorted(rows, key=lambda r: r.get("date", ""))
    dates = [r["date"] for r in rows_sorted]
    concs = [float(r["concentration"]) if r.get("concentration") else None for r in rows_sorted]
    blod = [r.get("is_below_lod", "").lower() in ("true", "1") for r in rows_sorted]

    trend = trends.get((bh_id, param_code), {})
    classification = trend.get("classification", "NONE")
    std_str = trend.get("drinking_water_standard", "")
    try:
        std = float(std_str) if std_str else None
    except ValueError:
        std = None

    param_name = rows[0].get("param_name", param_code)
    unit = rows[0].get("unit", "µg/L")
    borehole_display = BOREHOLE_DISPLAY.get(bh_id, bh_id)

    out = output_dir / f"trend_{bh_id}_{param_code}.png"
    build_trend_chart(
        dates=dates,
        concentrations=concs,
        is_below_lod=blod,
        borehole_name=borehole_display,
        parameter_code=param_code,
        parameter_name=param_name,
        classification=classification,
        unit=unit,
        drinking_water_standard=std,
        output_path=out,
    )
    return out


def main() -> None:
    parser = make_parser("Phase C: Generate Raanana zone charts.")
    args = parser.parse_args()
    cfg = merged_config(args.zone or "raanana", args.config)

    output_dir = Path(args.output) if args.output else OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(PRESETS_PATH, encoding="utf-8") as fh:
        presets_data = json.load(fh)
    presets = presets_data["presets"]

    log.info("loading_data")
    max_concs = _load_max_concs(MEAS_PATH)
    meas_groups = _load_measurements_by_key(MEAS_PATH)
    trends = _load_trends(TRENDS_PATH)
    log.info("data_loaded", boreholes=len(max_concs))

    all_bh = list(BOREHOLE_DISPLAY.keys())
    generated: list[str] = []

    # ── PFAS charts (turbine station focus) ──────────────────────────────────
    log.info("generating_pfas_charts")
    pfas_preset = presets["pfas"]
    pfas_codes = (
        pfas_preset["groups"]["S"]["codes"] +
        pfas_preset["groups"]["A"]["codes"]
    )
    pfas_data = _build_stacked_data(max_concs, all_bh, pfas_codes)

    out_abs = output_dir / "pfas_absolute.png"
    build_grouped_stacked(pfas_data, pfas_preset, out_abs, mode="absolute")
    generated.append(str(out_abs))
    log.info("chart_saved", path=str(out_abs))

    out_pct = output_dir / "pfas_percent.png"
    build_grouped_stacked(pfas_data, pfas_preset, out_pct, mode="percent_100")
    generated.append(str(out_pct))
    log.info("chart_saved", path=str(out_pct))

    # ── CVOC charts ───────────────────────────────────────────────────────────
    log.info("generating_cvoc_charts")
    cvoc_preset = presets["cvoc"]
    cvoc_codes = cvoc_preset["codes"]

    # All boreholes
    cvoc_all = _build_stacked_data(max_concs, all_bh, cvoc_codes)
    out = output_dir / "cvoc_all_absolute.png"
    build_grouped_stacked(cvoc_all, cvoc_preset, out, mode="absolute")
    generated.append(str(out))

    out = output_dir / "cvoc_all_percent.png"
    build_grouped_stacked(cvoc_all, cvoc_preset, out, mode="percent_100")
    generated.append(str(out))

    # nt_1 focus (TCE dominant)
    cvoc_nt1 = _build_stacked_data(max_concs, ["raanana_nt_1"], cvoc_codes)
    out = output_dir / "cvoc_nt1_absolute.png"
    build_grouped_stacked(cvoc_nt1, cvoc_preset, out, mode="absolute")
    generated.append(str(out))

    # nt_3 focus (PCE dominant)
    cvoc_nt3 = _build_stacked_data(max_concs, ["raanana_nt_3"], cvoc_codes)
    out = output_dir / "cvoc_nt3_absolute.png"
    build_grouped_stacked(cvoc_nt3, cvoc_preset, out, mode="absolute")
    generated.append(str(out))

    # ── BTEX charts ───────────────────────────────────────────────────────────
    log.info("generating_btex_charts")
    btex_preset = presets["btex"]
    btex_codes = btex_preset["codes"]

    btex_all = _build_stacked_data(max_concs, all_bh, btex_codes)
    out = output_dir / "btex_all_absolute.png"
    build_grouped_stacked(btex_all, btex_preset, out, mode="absolute")
    generated.append(str(out))

    # ── THM charts ────────────────────────────────────────────────────────────
    log.info("generating_thm_charts")
    thm_preset = presets["thm"]
    thm_data = _build_stacked_data(max_concs, all_bh, thm_preset["codes"])
    out = output_dir / "thm_all_absolute.png"
    build_grouped_stacked(thm_data, thm_preset, out, mode="absolute")
    generated.append(str(out))

    # ── Trend charts for key parameters ──────────────────────────────────────
    log.info("generating_trend_charts")
    for bh_id, param_code in KEY_TRENDS:
        out = _generate_trend_chart(bh_id, param_code, meas_groups, trends, output_dir)
        if out:
            generated.append(str(out))
            log.info("trend_chart_saved", borehole=bh_id, param=param_code)

    log.info("all_charts_done", count=len(generated))
    print(f"[Phase C] Done — {len(generated)} charts → {output_dir}")
    for p in generated:
        print(f"  {Path(p).name}")


if __name__ == "__main__":
    main()
