"""Zone borehole selector — Tier 1 / Tier 2 / Tier 3 logic.

Tier 1: Historically documented boreholes (TAHAL 2008 + 2021 Report).
Tier 2: Spatial filter — borehole coordinates inside zone polygon ± buffer.
Tier 3: Manual additions (upgradient, downgradient, neighboring plumes).

Usage:
    python scripts/select_boreholes.py --zone raanana [--boreholes-csv PATH] [--config PATH]
    python scripts/select_boreholes.py --zone raanana --list-tiers
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.cli_common import make_parser, merged_config
from scripts.logging_setup import get_logger

log = get_logger("select_boreholes")

ZONE_DEF_DIR = REPO_ROOT / "zone_definitions"
TIER1_PATH = ZONE_DEF_DIR / "tier1_historical_boreholes.json"
POLYGONS_PATH = ZONE_DEF_DIR / "zone_polygons.json"
TIER3_PATH = ZONE_DEF_DIR / "tier3_cross_zone_boreholes.json"
# Default boreholes CSV derived from zone name in main()


class BoreholeRecord(NamedTuple):
    canonical_id: str
    name_he: str
    easting: float
    northing: float


def _load_boreholes_csv(path: Path) -> list[BoreholeRecord]:
    records: list[BoreholeRecord] = []
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                e = float(row.get("itm_easting", row.get("easting_itm", row.get("easting", 0))))
                n = float(row.get("itm_northing", row.get("northing_itm", row.get("northing", 0))))
            except (ValueError, TypeError):
                e, n = 0.0, 0.0
            records.append(BoreholeRecord(
                canonical_id=row["canonical_id"],
                name_he=row.get("name_he", row.get("name", "")),
                easting=e,
                northing=n,
            ))
    return records


def _point_in_polygon(x: float, y: float, polygon: list[list[float]]) -> bool:
    """Ray-casting point-in-polygon test."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _point_near_polygon(x: float, y: float, polygon: list[list[float]], buffer_m: float) -> bool:
    """True if point is inside polygon OR within buffer_m of any polygon edge."""
    if _point_in_polygon(x, y, polygon):
        return True
    for i in range(len(polygon) - 1):
        x1, y1 = polygon[i]
        x2, y2 = polygon[i + 1]
        dx, dy = x2 - x1, y2 - y1
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq == 0:
            dist = ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
        else:
            t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / seg_len_sq))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            dist = ((x - proj_x) ** 2 + (y - proj_y) ** 2) ** 0.5
        if dist <= buffer_m:
            return True
    return False


class BoreholeTierResult(NamedTuple):
    canonical_id: str
    name_he: str
    easting: float
    northing: float
    tier: int
    tier_source: str


def select_boreholes(
    zone_id: str,
    all_boreholes: list[BoreholeRecord],
    tier1_data: dict,
    polygon_data: dict,
    tier3_data: dict,
) -> list[BoreholeTierResult]:
    """Return all boreholes relevant to zone_id, tagged by tier."""
    selected: dict[str, BoreholeTierResult] = {}
    bh_by_id = {b.canonical_id: b for b in all_boreholes}

    # ── Tier 1: historical documents ─────────────────────────────────────────
    zone_t1 = tier1_data.get(zone_id, {})
    t1_ids: set[str] = set(zone_t1.get("tahal_2008_boreholes", []) +
                            zone_t1.get("report_2021_boreholes", []))
    for bh_id in t1_ids:
        bh = bh_by_id.get(bh_id)
        if bh:
            selected[bh_id] = BoreholeTierResult(
                canonical_id=bh_id, name_he=bh.name_he,
                easting=bh.easting, northing=bh.northing,
                tier=1, tier_source="Tier 1: historical documents",
            )
        else:
            log.warning("tier1_borehole_not_in_csv", borehole_id=bh_id, zone=zone_id)

    # ── Tier 2: spatial filter ────────────────────────────────────────────────
    zone_poly = polygon_data.get(zone_id, {})
    polygon = zone_poly.get("polygon", [])
    buffer_m = float(zone_poly.get("buffer_m", 500))

    if len(polygon) >= 3:
        for bh in all_boreholes:
            if bh.canonical_id in selected:
                continue
            if _point_near_polygon(bh.easting, bh.northing, polygon, buffer_m):
                selected[bh.canonical_id] = BoreholeTierResult(
                    canonical_id=bh.canonical_id, name_he=bh.name_he,
                    easting=bh.easting, northing=bh.northing,
                    tier=2, tier_source=f"Tier 2: spatial (polygon ±{buffer_m}m)",
                )
    else:
        log.warning("no_polygon_defined", zone=zone_id)

    # ── Tier 3: manual additions ──────────────────────────────────────────────
    zone_t3 = tier3_data.get(zone_id, {})
    for direction in ("upgradient", "downgradient", "influencing_neighbors"):
        for entry in zone_t3.get(direction, []):
            bh_id = entry.get("borehole_id", "")
            if not bh_id or bh_id in selected:
                continue
            bh = bh_by_id.get(bh_id)
            reason = entry.get("reason", direction)
            if bh:
                selected[bh_id] = BoreholeTierResult(
                    canonical_id=bh_id, name_he=bh.name_he,
                    easting=bh.easting, northing=bh.northing,
                    tier=3, tier_source=f"Tier 3: {direction} — {reason[:60]}",
                )
            else:
                log.warning("tier3_borehole_not_in_csv", borehole_id=bh_id, zone=zone_id)

    return sorted(selected.values(), key=lambda r: (r.tier, r.canonical_id))


def main() -> None:
    parser = make_parser("Phase E: Select boreholes for a zone (Tier 1/2/3).")
    parser.add_argument("--list-tiers", action="store_true",
                        help="Print selection result with tier attribution and exit")
    args = parser.parse_args()
    zone_id = args.zone or "raanana"

    default_csv = REPO_ROOT / zone_id.capitalize() / "data" / "boreholes.csv"
    boreholes_csv = Path(args.input) if args.input else default_csv
    if not boreholes_csv.exists():
        log.error("boreholes_csv_not_found", path=str(boreholes_csv))
        sys.exit(1)

    with open(TIER1_PATH, encoding="utf-8") as fh:
        tier1_data = json.load(fh)
    with open(POLYGONS_PATH, encoding="utf-8") as fh:
        polygon_data = json.load(fh)
    with open(TIER3_PATH, encoding="utf-8") as fh:
        tier3_data = json.load(fh)

    all_boreholes = _load_boreholes_csv(boreholes_csv)
    results = select_boreholes(zone_id, all_boreholes, tier1_data, polygon_data, tier3_data)

    print(f"\nZone: {zone_id} — {len(results)} boreholes selected")
    print(f"{'Tier':<6} {'ID':<30} {'Name':<25} {'E':>9} {'N':>9}")
    print("-" * 85)
    for r in results:
        print(f"  {r.tier}    {r.canonical_id:<30} {r.name_he:<25} {r.easting:>9.0f} {r.northing:>9.0f}")

    if args.list_tiers:
        print("\nTier sources:")
        for r in results:
            print(f"  {r.canonical_id}: {r.tier_source}")

    # Persist selection so downstream scripts (trend_analysis, forensics, charts) can filter
    output_path = (Path(args.output) if args.output
                   else REPO_ROOT / zone_id.capitalize() / "data" / "selected_boreholes.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "zone_id": zone_id,
        "n_selected": len(results),
        "boreholes": [
            {
                "canonical_id": r.canonical_id,
                "name_he": r.name_he,
                "tier": r.tier,
                "tier_source": r.tier_source,
                "itm_easting": r.easting,
                "itm_northing": r.northing,
            }
            for r in results
        ],
    }
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"\nSaved selection → {output_path}")

    log.info("selection_complete", zone=zone_id, n_selected=len(results), output=str(output_path))
    return results


if __name__ == "__main__":
    main()
