#!/usr/bin/env python3
"""Generate a report-engine zone brief (YAML) from a zone's FULL report.

Zone-agnostic pipeline component. The full V5 report is the single source of
truth for all CONTENT; the only thing pulled deterministically from the data
tables is exact well COORDINATES (the full report does not carry map-grade
ITM/WGS-84 positions, and LLM-guessed coordinates have been observed off by ~1 km).

Two stages:

  prepare   Read zone_wells.csv -> ITM(EPSG:2039)->WGS-84 lookup + well inventory,
            assemble the Opus prompt from scripts/templates/zone_brief_prompt_template.md.
            Output: <build_dir>/prompt.md  and  <build_dir>/coords.json

  finalize  Take the Opus-produced raw brief, inject exact coords by name match,
            run structural validation against the schema's required fields/enums,
            and write report-engine/briefs/<zone>.yaml

Opus runs BETWEEN the two stages (via Claude Code / agent), consistent with the
rest of the V5 pipeline where LLM steps are separate from deterministic scripts.

Usage:
    python scripts/generate_zone_brief.py prepare  --zone holon
    # (run the prompt in build_dir/prompt.md with Opus, save output as raw_brief.yaml)
    python scripts/generate_zone_brief.py finalize --zone holon --raw <build_dir>/raw_brief.yaml
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

try:
    from pyproj import Transformer
except ImportError:
    sys.exit("pyproj required: pip install pyproj")


REPO = Path(__file__).resolve().parent.parent
ENGINE = REPO / "report-engine"
TEMPLATE = REPO / "scripts" / "templates" / "zone_brief_prompt_template.md"

# Israeli TM (EPSG:2039) -> WGS-84 (EPSG:4326)
_ITM_TO_WGS84 = Transformer.from_crs("EPSG:2039", "EPSG:4326", always_xy=True)


def itm_to_wgs84(easting: float, northing: float) -> list[float]:
    """Return [lat, lon] rounded to 5 dp from ITM easting/northing meters."""
    lon, lat = _ITM_TO_WGS84.transform(easting, northing)
    return [round(lat, 5), round(lon, 5)]


def _norm(name: str) -> str:
    """Normalize a Hebrew well name for matching (collapse whitespace)."""
    return re.sub(r"\s+", " ", (name or "").strip())


def zone_paths(zone: str) -> dict[str, Path]:
    """Derive all per-zone paths from the zone id. Zone dir is capitalized
    (holon -> Holon), matching the repo convention."""
    zdir = REPO / zone.capitalize()
    return {
        "zone_dir": zdir,
        "wells_csv": zdir / "02_data" / "zone_wells.csv",
        "report_v5": zdir / "output" / f"{zone.upper()}_REPORT_V5.md",
        "build_dir": zdir / "05_brief_build",
        "out_brief": ENGINE / "briefs" / f"{zone}.yaml",
    }


def load_coords_lookup(wells_csv: Path) -> dict[str, list[float]]:
    """Build {normalized_name_he: [lat, lon]} from zone_wells.csv."""
    import csv

    lookup: dict[str, list[float]] = {}
    with wells_csv.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            e, n = row.get("itm_easting"), row.get("itm_northing")
            if not e or not n:
                continue
            try:
                lookup[_norm(row["name_he"])] = itm_to_wgs84(float(e), float(n))
            except (ValueError, KeyError):
                continue
    return lookup


def build_well_inventory(wells_csv: Path) -> str:
    """Markdown table of name_he | well_type for the prompt (NO coords)."""
    import csv

    lines = ["| name_he | well_type |", "| --- | --- |"]
    with wells_csv.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            lines.append(f"| {row.get('name_he','')} | {row.get('well_type','')} |")
    return "\n".join(lines)


def cmd_prepare(zone: str) -> None:
    p = zone_paths(zone)
    for key in ("wells_csv", "report_v5"):
        if not p[key].exists():
            sys.exit(f"missing required input: {p[key]}")

    coords = load_coords_lookup(p["wells_csv"])
    inventory = build_well_inventory(p["wells_csv"])

    schema = (ENGINE / "schemas" / "zone-brief.schema.json").read_text(encoding="utf-8")
    voice = (ENGINE / "design-system" / "voice.md").read_text(encoding="utf-8")
    architecture = (ENGINE / "design-system" / "architecture.md").read_text(encoding="utf-8")
    full_report = p["report_v5"].read_text(encoding="utf-8")

    ref_path = ENGINE / "briefs" / "holon.yaml"
    reference = ref_path.read_text(encoding="utf-8") if ref_path.exists() else "(none)"

    # Read zone identity from the report's first lines, fall back to id/name.
    zone_name_he = zone.capitalize()
    m = re.search(r"name_he\"?\s*[:=]\s*\"?([^\"\n]+)", full_report)
    if m:
        zone_name_he = m.group(1).strip()

    prompt = TEMPLATE.read_text(encoding="utf-8")
    repl = {
        "{ZONE_ID}": zone.upper(),
        "{ZONE_NAME_HE}": zone_name_he,
        "{FULL_REPORT}": full_report,
        "{SCHEMA}": schema,
        "{VOICE_RULES}": voice,
        "{ARCHITECTURE}": architecture,
        "{WELL_INVENTORY}": inventory,
        "{REFERENCE_BRIEF}": reference,
    }
    for k, v in repl.items():
        prompt = prompt.replace(k, v)

    p["build_dir"].mkdir(parents=True, exist_ok=True)
    (p["build_dir"] / "prompt.md").write_text(prompt, encoding="utf-8")
    (p["build_dir"] / "coords.json").write_text(
        json.dumps(coords, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"prepared: {p['build_dir']/'prompt.md'}")
    print(f"coords lookup: {len(coords)} wells -> {p['build_dir']/'coords.json'}")
    print("next: run prompt.md with Opus, save output as raw_brief.yaml, then `finalize`.")


# ── finalize ────────────────────────────────────────────────────────────────

REQUIRED_TOP = ["zone", "kpis", "family_ledger", "framing_warning", "findings", "boreholes"]
URGENCY = {"critical", "high", "good"}


_INJECT_RE = re.compile(r"coords:\s*\[\s*0\s*,\s*0\s*\]\s*#\s*COORDS-INJECT:(.+)")


def inject_coords_text(raw: str, coords: dict[str, list[float]]) -> tuple[str, list[str]]:
    """Textually replace `coords: [0,0]  # COORDS-INJECT:<name>` markers with exact
    WGS-84 coords, preserving all other formatting/comments. Returns (text, warnings)."""
    warns: list[str] = []

    def repl(m: re.Match) -> str:
        name = _norm(m.group(1))
        indent = m.string[m.start():].split("coords:")[0]
        if name in coords:
            lat, lon = coords[name]
            return f"coords: [{lat}, {lon}]"
        warns.append(f"'{name}' not in well table — coords left as [0, 0]")
        return "coords: [0, 0]"

    return _INJECT_RE.sub(repl, raw), warns


def validate(brief: dict) -> list[str]:
    """Lightweight structural validation (jsonschema not assumed available)."""
    errs: list[str] = []
    for key in REQUIRED_TOP:
        if key not in brief:
            errs.append(f"missing required top-level key: {key}")
    for i, f in enumerate(brief.get("findings", [])):
        for req in ("id", "urgency", "title_internal", "title_public",
                    "body_internal", "body_public"):
            if req not in f:
                errs.append(f"findings[{i}] missing '{req}'")
        if f.get("urgency") not in URGENCY:
            errs.append(f"findings[{i}].urgency invalid: {f.get('urgency')}")
    n = len(brief.get("findings", []))
    if not (5 <= n <= 9):
        errs.append(f"findings count {n} outside 5–9")
    # Public-leak guard: no borehole real name should appear in its public block.
    for bh in brief.get("boreholes", []):
        pub = json.dumps(bh.get("public", {}), ensure_ascii=False)
        if bh.get("name_he") and bh["name_he"] in pub:
            errs.append(f"borehole '{bh['name_he']}' real name leaked into public block")
    return errs


def cmd_finalize(zone: str, raw: Path) -> None:
    p = zone_paths(zone)
    if not raw.exists():
        sys.exit(f"raw brief not found: {raw}")
    coords_file = p["build_dir"] / "coords.json"
    if not coords_file.exists():
        sys.exit(f"coords.json not found — run `prepare` first: {coords_file}")

    raw_text = raw.read_text(encoding="utf-8")
    coords = json.loads(coords_file.read_text(encoding="utf-8"))

    # Validate the parsed structure (read-only) before touching text.
    errs = validate(yaml.safe_load(raw_text))
    if errs:
        print("VALIDATION FAILED:")
        for e in errs:
            print(f"  error: {e}")
        sys.exit(1)

    # Inject coords textually so Opus's formatting + comments survive intact.
    final_text, warns = inject_coords_text(raw_text, coords)
    for w in warns:
        print(f"  warn: {w}")

    # Re-parse after injection to confirm the file is still valid YAML.
    try:
        yaml.safe_load(final_text)
    except yaml.YAMLError as ex:
        sys.exit(f"coord injection produced invalid YAML: {ex}")

    p["out_brief"].parent.mkdir(parents=True, exist_ok=True)
    p["out_brief"].write_text(final_text, encoding="utf-8")
    print(f"wrote validated brief: {p['out_brief']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("prepare", help="assemble Opus prompt + coords lookup")
    pp.add_argument("--zone", required=True)

    pf = sub.add_parser("finalize", help="inject coords + validate -> briefs/<zone>.yaml")
    pf.add_argument("--zone", required=True)
    pf.add_argument("--raw", required=True, type=Path, help="Opus-produced raw brief YAML")

    args = ap.parse_args()
    if args.cmd == "prepare":
        cmd_prepare(args.zone)
    elif args.cmd == "finalize":
        cmd_finalize(args.zone, args.raw)


if __name__ == "__main__":
    main()
