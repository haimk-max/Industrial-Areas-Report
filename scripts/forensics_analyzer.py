"""Phase B: Forensics analysis — decay chains, source signatures, co-occurrence.

Reads measurements.csv + trends.csv, runs forensic modules, writes:
  Raanana/forensics/contamination_families.json

Usage:
    python scripts/forensics_analyzer.py [--zone raanana] [--config ...]
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.cli_common import load_config, make_parser, merged_config
from scripts.forensics.co_occurrence import compute_co_occurrence
from scripts.forensics.decay_chains import analyze_decay_chains
from scripts.forensics.source_signatures import match_source_signatures
from scripts.logging_setup import get_logger

log = get_logger("forensics_analyzer")

# Paths derived from zone name in main()


def _load_detections(meas_path: Path) -> dict[str, dict[str, float]]:
    """Build {borehole_id → {param_code → max_concentration}} from measurements."""
    detections: dict[str, dict[str, float]] = {}
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
            if bh not in detections:
                detections[bh] = {}
            current_max = detections[bh].get(code, 0.0)
            detections[bh][code] = max(current_max, conc)
    return detections


def _load_exceedances(meas_path: Path) -> dict[str, list[dict]]:
    """Load measurements that exceed drinking water standard."""
    exceedances: dict[str, list[dict]] = {}
    with open(meas_path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            pct = row.get("percent_of_standard", "")
            if not pct or not pct.strip():
                continue
            try:
                pct_val = float(pct)
            except ValueError:
                continue
            if pct_val > 100:
                bh = row["canonical_id"]
                exceedances.setdefault(bh, []).append({
                    "param_code": row["param_code"],
                    "param_name": row["param_name"],
                    "date": row["date"],
                    "concentration": float(row["concentration"] or 0),
                    "unit": row["unit"],
                    "drinking_water_standard": float(row["drinking_water_standard"] or 0),
                    "percent_of_standard": pct_val,
                })
    # Sort each borehole's exceedances by percent desc
    for bh in exceedances:
        exceedances[bh].sort(key=lambda x: -x["percent_of_standard"])
    return exceedances


def main() -> None:
    parser = make_parser("Phase B: Forensics analysis for a zone.")
    args = parser.parse_args()
    zone = (args.zone or "raanana").lower()
    cfg = merged_config(zone, args.config)
    zone_data_dir = REPO_ROOT / zone.capitalize() / "data"

    meas_path = Path(args.input) if args.input else zone_data_dir / "measurements.csv"
    output_dir = Path(args.output) if args.output else REPO_ROOT / zone.capitalize() / "forensics"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not meas_path.exists():
        log.error("measurements_not_found", path=str(meas_path))
        sys.exit(1)

    log.info("loading_data")
    detections = _load_detections(meas_path)
    exceedances = _load_exceedances(meas_path)

    log.info("data_loaded", boreholes=len(detections))

    result: dict = {
        "zone_id": zone,
        "zone_name_he": f"אזה\"ת {zone}",
        "source": str(meas_path),
        "boreholes_analyzed": list(detections.keys()),
        "contamination_families": {},
        "decay_chains": {},
        "source_signatures": {},
        "co_occurrence": {},
        "critical_exceedances": {},
    }

    # ── Per-borehole forensics ────────────────────────────────────────────────
    for bh_id, bh_detections in sorted(detections.items()):
        # Decay chains
        chains = analyze_decay_chains(bh_id, bh_detections)
        if chains:
            result["decay_chains"][bh_id] = [
                {
                    "chain_name": c.chain_name,
                    "detected_members": c.detected_members,
                    "presence_ratio": c.presence_ratio,
                    "daughter_exceeds_parent": [list(p) for p in c.daughter_exceeds_parent],
                    "confidence": c.confidence,
                    "interpretation": c.interpretation,
                }
                for c in chains
            ]

        # Source signatures
        sigs = match_source_signatures(bh_id, bh_detections)
        if sigs:
            result["source_signatures"][bh_id] = [
                {
                    "signature": s.signature,
                    "confidence": s.confidence,
                    "detected_indicators": s.detected_indicators,
                    "dominant_compound": s.dominant_compound,
                    "max_concentration": s.max_concentration,
                    "notes": s.notes,
                }
                for s in sigs
            ]

        # Critical exceedances
        if bh_id in exceedances:
            top = exceedances[bh_id][:10]  # top 10 by % of standard
            result["critical_exceedances"][bh_id] = top

        log.info("borehole_analyzed", borehole=bh_id,
                 chains=len(chains), signatures=len(sigs),
                 exceedances=len(exceedances.get(bh_id, [])))

    # ── Zone-level co-occurrence ──────────────────────────────────────────────
    co = compute_co_occurrence(detections, min_count=2)
    result["co_occurrence"] = {
        "top_pairs": [{"param_a": a, "param_b": b, "n_boreholes": n}
                      for a, b, n in co.top_pairs[:30]],
        "detected_per_borehole": {
            bh: sorted(params)
            for bh, params in co.detected_per_borehole.items()
        },
    }

    # ── Contamination families summary ────────────────────────────────────────
    families: dict[str, list[str]] = {}
    for bh_id, bh_detections in detections.items():
        for code, conc in bh_detections.items():
            if conc > 0:
                families.setdefault(code, [])
                if bh_id not in families[code]:
                    families[code].append(bh_id)
    result["contamination_families"] = {
        code: {"boreholes": bhs, "n_boreholes": len(bhs)}
        for code, bhs in sorted(families.items(), key=lambda kv: -len(kv[1]))
        if len(bhs) >= 2  # only parameters detected in 2+ boreholes
    }

    # ── Write output ─────────────────────────────────────────────────────────
    out_path = output_dir / "contamination_families.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    log.info("forensics_written", path=str(out_path))

    # ── Print summary ─────────────────────────────────────────────────────────
    n_pfas_alerts = sum(
        1 for bh, excs in exceedances.items()
        for e in excs if "PF" in e["param_code"]
    )
    print(f"[Phase B Forensics] Done → {out_path}")
    print(f"  Decay chains detected: {sum(len(v) for v in result['decay_chains'].values())}")
    print(f"  Source signatures identified: {sum(len(v) for v in result['source_signatures'].values())}")
    print(f"  Co-occurrence pairs (≥2 boreholes): {len(co.top_pairs)}")
    print(f"  PFAS exceedance events: {n_pfas_alerts}")


if __name__ == "__main__":
    main()
