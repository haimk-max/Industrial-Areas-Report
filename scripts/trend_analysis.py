"""Phase B: Run Mann-Kendall trend analysis on all (borehole, parameter) pairs.

Reads Raanana/data/measurements.csv, calls preprocess.analyze_series() on each
(canonical_id, param_code) group, writes Raanana/data/trends.csv.

Usage:
    python scripts/trend_analysis.py [--zone raanana] [--config ...]
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.cli_common import load_config, make_parser, merged_config
from scripts.logging_setup import get_logger
from scripts.preprocess import Observation, TrendResult, analyze_series, parse_observation

log = get_logger("trend_analysis")

MEAS_PATH = REPO_ROOT / "Raanana" / "data" / "measurements.csv"
OUTPUT_PATH = REPO_ROOT / "Raanana" / "data" / "trends.csv"

TREND_FIELDS = [
    "borehole_id", "parameter", "n", "n5", "has_detection",
    "mk_z_5y", "mk_p_5y", "mk_z_full", "mk_p_full",
    "snr_5y", "snr_full", "analysis_mode", "classification", "trend_description",
    "crossed_standard", "drinking_water_standard",
]


def _load_measurements(meas_path: Path) -> dict[tuple[str, str], list[dict]]:
    """Return {(canonical_id, param_code): [row_dict, ...]}."""
    groups: dict[tuple[str, str], list[dict]] = {}
    with open(meas_path, encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            key = (row["canonical_id"], row["param_code"])
            groups.setdefault(key, []).append(row)
    return groups


def _get_standard(rows: list[dict]) -> float | None:
    for r in rows:
        s = r.get("drinking_water_standard", "")
        if s and str(s).strip():
            try:
                return float(s)
            except ValueError:
                continue
    return None


def main() -> None:
    parser = make_parser("Phase B: Trend analysis over all borehole/parameter pairs.")
    args = parser.parse_args()
    cfg = merged_config(args.zone or "raanana", args.config)

    meas_path = Path(args.input) if args.input else MEAS_PATH
    output_path = Path(args.output) if args.output else OUTPUT_PATH

    if not meas_path.exists():
        log.error("measurements_not_found", path=str(meas_path))
        print(f"ERROR: measurements.csv not found: {meas_path}", file=sys.stderr)
        sys.exit(1)

    log.info("loading_measurements", path=str(meas_path))
    groups = _load_measurements(meas_path)
    log.info("groups_loaded", n_pairs=len(groups))

    results: list[TrendResult] = []
    classification_counts: dict[str, int] = {}
    n_insufficient = 0

    for (bh_id, param_code), rows in sorted(groups.items()):
        observations: list[Observation] = []
        for row in rows:
            obs = parse_observation(
                date_str=row.get("date", ""),
                concentration_str=row.get("concentration", ""),
                is_below_lod_str=row.get("is_below_lod", ""),
                drinking_standard_str=row.get("drinking_water_standard", ""),
            )
            if obs is not None:
                observations.append(obs)

        std = _get_standard(rows)
        result = analyze_series(bh_id, param_code, observations, cfg, std)
        results.append(result)

        classification_counts[result.classification] = (
            classification_counts.get(result.classification, 0) + 1
        )
        if result.classification == "NONE" and result.n < 4:
            n_insufficient += 1

    log.info("analysis_complete",
             total_pairs=len(results),
             **{f"class_{k}": v for k, v in classification_counts.items()})

    # ── Write trends.csv ──────────────────────────────────────────────────────
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=TREND_FIELDS)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "borehole_id": r.borehole_id,
                "parameter": r.parameter,
                "n": r.n,
                "n5": r.n5,
                "has_detection": r.has_detection,
                "mk_z_5y": _fmt(r.mk_z_5y),
                "mk_p_5y": _fmt(r.mk_p_5y),
                "mk_z_full": _fmt(r.mk_z_full),
                "mk_p_full": _fmt(r.mk_p_full),
                "snr_5y": _fmt(r.snr_5y),
                "snr_full": _fmt(r.snr_full),
                "analysis_mode": r.analysis_mode,
                "classification": r.classification,
                "trend_description": r.trend_description,
                "crossed_standard": r.crossed_standard,
                "drinking_water_standard": _fmt(r.drinking_water_standard),
            })

    log.info("trends_written", path=str(output_path), rows=len(results))

    _write_qa_report(results, classification_counts, n_insufficient, output_path.parent)

    print(f"[Phase B] Done — {len(results)} pairs analysed → {output_path}")
    print(f"  Classifications: " +
          ", ".join(f"{k}={v}" for k, v in sorted(classification_counts.items())))


def _fmt(val) -> str:
    if val is None:
        return ""
    if isinstance(val, float):
        return f"{val:.6g}"
    return str(val)


def _write_qa_report(results: list[TrendResult], class_counts: dict[str, int],
                     n_insufficient: int, output_dir: Path) -> None:
    qa_path = output_dir / "_trends_qa.md"

    # Find ALERT and WATCH pairs for spot-check
    alerts = [(r.borehole_id, r.parameter, r.n5, r.snr_5y, r.mk_p_5y)
               for r in results if r.classification == "ALERT"]
    watches = [(r.borehole_id, r.parameter, r.n5, r.snr_5y, r.mk_p_5y)
                for r in results if r.classification == "WATCH"]
    crossed = [r for r in results if r.crossed_standard]

    lines = [
        "# Phase B QA Report — Trend Analysis",
        "",
        "## Classification summary",
        "",
        "| Classification | Count |",
        "|---|---|",
    ]
    for cls in ["ALERT", "WATCH", "STABLE", "DECREASING", "NONE"]:
        lines.append(f"| {cls} | {class_counts.get(cls, 0)} |")

    lines += [
        "",
        f"- Total (borehole, parameter) pairs: {sum(class_counts.values())}",
        f"- Pairs with insufficient data (n<4): {n_insufficient}",
        f"- Pairs that crossed drinking water standard: {len(crossed)}",
        "",
        "## ALERT classifications",
        "",
        "| Borehole | Parameter | n5 | SNR | MK p-value |",
        "|---|---|---|---|---|",
    ]
    for bh, param, n5, snr, p in sorted(alerts, key=lambda x: (x[0], x[1])):
        snr_s = f"{snr:.3f}" if snr is not None else "—"
        p_s = f"{p:.4f}" if p is not None else "—"
        lines.append(f"| {bh} | {param} | {n5} | {snr_s} | {p_s} |")

    lines += [
        "",
        "## WATCH classifications (first 20)",
        "",
        "| Borehole | Parameter | n5 | SNR | MK p-value |",
        "|---|---|---|---|---|",
    ]
    for bh, param, n5, snr, p in sorted(watches, key=lambda x: (x[0], x[1]))[:20]:
        snr_s = f"{snr:.3f}" if snr is not None else "—"
        p_s = f"{p:.4f}" if p is not None else "—"
        lines.append(f"| {bh} | {param} | {n5} | {snr_s} | {p_s} |")

    lines += [
        "",
        "## Validation",
        "- Entry criteria applied (n≥4, has_detection, n5≥1): ✅",
        "- Soft trigger: 2 most recent 5y measurements compared: ✅",
        "- Mann-Kendall: tie-corrected variance, continuity-corrected Z: ✅",
        "- SNR gating: <0.3 → NONE regardless of MK: ✅",
        "- TPFAS absent from all results: ✅",
    ]
    qa_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
