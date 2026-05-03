"""Phase 0a: Seed base_layer/tahal_2008/ from existing Raanana manual data + stubs for 17 others.

TAHAL 2008 Part B PDFs are image-based (scanned). Raanana data was manually extracted
during Phase 1. All other zones are marked manual_pending until data is available.

Usage:
    python scripts/build_tahal_base.py [--config config/analysis_config.yaml]
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.cli_common import load_config, make_parser
from scripts.logging_setup import get_logger
from scripts.schemas import (
    Borehole,
    Coordinates,
    Industry,
    Measurement,
    RiskAssessment,
    TahalZoneData,
)

log = get_logger("build_tahal_base")

OUTPUT_DIR = REPO_ROOT / "base_layer" / "tahal_2008"

# All 18 zones from the 2021 Report (ground truth for zone names)
# Maps zone_id → (zone_name_he, notes)
ZONE_REGISTRY: dict[str, tuple[str, str]] = {
    "raanana":                     ("אזה\"ת רעננה",              "Seeded from manually extracted TAHAL 2008 Part B pages 53-67"),
    "ashkelon_south":              ("אזה\"ת אשקלון דרום",        ""),
    "ashkelon_north":              ("אזה\"ת אשקלון צפון",        ""),
    "ashdod_south":                ("אזה\"ת אשדוד דרום",         ""),
    "yavne":                       ("אזה\"ת יבנה",                ""),
    "bnei_ram":                    ("אזה\"ת בני ראם",             ""),
    "rehovot_kramtech":            ("אזה\"ת רכטמן רחובות",       ""),
    "nes_ziona_rehovot_sci_park":  ("אזה\"ת מדע פארק נס-ציונה-רחובות", ""),
    "nes_ziona":                   ("אזה\"ת נס ציונה",            ""),
    "rishon_letzion_west":         ("אזה\"ת ראשון לציון מערב",   ""),
    "rishon_letzion_east":         ("אזה\"ת ראשון לציון מזרח",   ""),
    "bat_yam":                     ("אזה\"ת בתים",                ""),
    "holon":                       ("אזה\"ת חולון",               ""),
    "even_yehuda":                 ("אזה\"ת אבן יהודה",          ""),
    "sapir_netanya":               ("אזה\"ת ספיר נתניה",         ""),
    "kiryat_eliezer_netanya":      ("אזה\"ת קריית אליעזר נתניה",""),
    "hadera":                      ("אזה\"ת חדרה",                ""),
    "or_akiva":                    ("אזה\"ת אור עקיבא",          ""),
}


def _load_raanana_boreholes() -> list[Borehole]:
    path = REPO_ROOT / "Raanana" / "data" / "boreholes.csv"
    boreholes = []
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            bh = Borehole(
                id=row["borehole_id"],
                name=row["name"],
                coordinates=Coordinates(
                    easting=float(row["easting"]),
                    northing=float(row["northing"]),
                    crs="EPSG:2039",
                ),
                depth_m=float(row["depth_m"]) if row.get("depth_m") else None,
                geological_layer=row.get("geological_layer") or None,
                classification=row.get("classification") or None,
                source_document_page=_extract_page(row.get("source_document", "")),
            )
            boreholes.append(bh)
    return boreholes


def _load_raanana_measurements() -> list[Measurement]:
    path = REPO_ROOT / "Raanana" / "data" / "concentrations.csv"
    measurements = []
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            conc_str = row.get("concentration", "")
            conc = float(conc_str) if conc_str else None
            meas = Measurement(
                borehole_id=row["borehole_id"],
                parameter=row["parameter"],
                unit=row.get("unit", "ppb"),
                year=int(row["year"]),
                concentration=conc,
                source_page=_extract_page(row.get("source_document", "")),
            )
            measurements.append(meas)
    return measurements


def _load_raanana_industries() -> list[Industry]:
    path = REPO_ROOT / "Raanana" / "data" / "industries.json"
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    industries = []
    for item in raw.get("industries", []):
        ind = Industry(
            id=item["id"],
            name=item["name"],
            name_he=item.get("name_he"),
            coordinates=Coordinates(
                easting=float(item["easting"]),
                northing=float(item["northing"]),
                crs="EPSG:2039",
            ),
            type=item["type"],
            category=item.get("category"),
            potential_contaminants=item.get("potential_contaminants", []),
            risk_level=item["risk_level"],
            notes=item.get("notes"),
        )
        industries.append(ind)
    return industries


def _extract_page(source_str: str) -> int | None:
    """Parse page number from a source string like 'TAHAL 2008 Part B p.53'."""
    import re
    m = re.search(r"p\.(\d+)", source_str)
    return int(m.group(1)) if m else None


def build_raanana() -> TahalZoneData:
    log.info("build_raanana_start")
    boreholes = _load_raanana_boreholes()
    measurements = _load_raanana_measurements()
    industries = _load_raanana_industries()
    risk = RiskAssessment(
        overall_risk="medium-high",
        aquifer_type="Coastal aquifer",
        vulnerability="High",
        contamination_spread_rate="Fast",
        source_document_page=53,
    )
    data = TahalZoneData(
        zone_id="raanana",
        zone_name_he=ZONE_REGISTRY["raanana"][0],
        source_document="TAHAL 2008 Part B pages 53-67 (manual extraction)",
        extraction_status="complete",
        extraction_notes=ZONE_REGISTRY["raanana"][1],
        boreholes=boreholes,
        measurements_1999_2008=measurements,
        industries=industries,
        risk_assessment=risk,
    )
    log.info("build_raanana_done",
             boreholes=len(boreholes),
             measurements=len(measurements),
             industries=len(industries))
    return data


def build_stub(zone_id: str) -> TahalZoneData:
    name_he, notes = ZONE_REGISTRY[zone_id]
    return TahalZoneData(
        zone_id=zone_id,
        zone_name_he=name_he,
        source_document="TAHAL 2008 Part B (image-based PDF — manual entry required)",
        extraction_status="manual_pending",
        extraction_notes=notes or "Awaiting manual extraction from scanned TAHAL 2008 Part B PDF.",
    )


def write_json(data: TahalZoneData) -> Path:
    out_path = OUTPUT_DIR / f"{data.zone_id}.json"
    out_path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
    return out_path


def main() -> None:
    parser = make_parser("Phase 0a: Seed base_layer/tahal_2008/ from Raanana data + stubs for 17 zones.")
    args = parser.parse_args()
    cfg = load_config(args.config)  # noqa: F841 — validates config exists

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []

    for zone_id in ZONE_REGISTRY:
        if zone_id == "raanana":
            data = build_raanana()
        else:
            data = build_stub(zone_id)

        out = write_json(data)
        log.info("zone_written", zone_id=zone_id, status=data.extraction_status, path=str(out))
        results.append({
            "zone_id": zone_id,
            "status": data.extraction_status,
            "boreholes": len(data.boreholes),
            "measurements": len(data.measurements_1999_2008),
            "industries": len(data.industries),
        })

    _write_qa_report(results)
    log.info("phase_0a_complete", zones_written=len(results))
    print(f"[Phase 0a] Done — {len(results)} zone JSONs written to {OUTPUT_DIR}")


def _write_qa_report(results: list[dict]) -> None:
    qa_path = OUTPUT_DIR / "_qa_report.md"
    complete = [r for r in results if r["status"] == "complete"]
    pending = [r for r in results if r["status"] == "manual_pending"]

    lines = [
        "# Phase 0a QA Report — TAHAL 2008 Base Layer",
        "",
        f"## Summary",
        f"- Total zones: {len(results)}",
        f"- Complete (manual extraction): {len(complete)}",
        f"- Manual pending (stubs): {len(pending)}",
        "",
        "## Complete zones",
    ]
    for r in complete:
        lines.append(f"- **{r['zone_id']}**: {r['boreholes']} boreholes, "
                     f"{r['measurements']} measurements, {r['industries']} industries")
    lines += ["", "## Pending zones (manual entry required)"]
    for r in pending:
        lines.append(f"- {r['zone_id']}")
    lines += [
        "",
        "## Validation",
        "- All JSONs written successfully: ✅",
        "- Pydantic schema validation passed: ✅",
        "- Raanana data seeded from Raanana/data/ files: ✅",
        "- 17 stubs created with extraction_status=manual_pending: ✅",
    ]
    qa_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
