#!/usr/bin/env python3
"""Render a canonical V5 pipeline Opus prompt from its template + zone artifacts.

Two prompt steps are rendered from their canonical templates:
  --step diagnosis  → scripts/templates/zone_diagnosis_prompt_template.md
                      → {ZONE}/context_pack/05_prompt/zone_diagnosis_prompt.md
  --step report     → scripts/templates/zone_report_prompt_template_v5.md
                      → {ZONE}/context_pack/05_prompt/zone_report_prompt.md

The rendered prompt is a DERIVED artifact. It must never be hand-edited. Re-run
this script whenever the template OR the zone diagnosis changes, so the prompt
can never drift from the §IV focus-ordering SSOT.

Why this exists: REQ #24 made §IV the single source of truth for ordering and
converted the governance docs to references — but a rendered zone prompt is a
*materialized copy*, not a reference. A materialized copy drifts silently unless
it is (a) regenerated from the SSOT on demand, and (b) checked for staleness.
This script is (a); `qa_pipeline.py` gate 3 is (b). Each rendered prompt carries
a provenance stamp (template sha256) that gate 3 compares to the live template.

Usage:
    python scripts/render_zone_prompt.py --zone Holon --step diagnosis --name-he 'אזה״ת חולון'
    python scripts/render_zone_prompt.py --zone Holon --step report    --name-he 'אזה״ת חולון'
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = {
    "report": REPO_ROOT / "scripts" / "templates" / "zone_report_prompt_template_v5.md",
    "diagnosis": REPO_ROOT / "scripts" / "templates" / "zone_diagnosis_prompt_template.md",
}
DEST_NAME = {
    "report": "zone_report_prompt.md",
    "diagnosis": "zone_diagnosis_prompt.md",
}

FUEL_TYPES = {"fuel_monitoring"}


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def derive_metadata(zone: str) -> dict:
    """Borehole counts, measurement count, year range from the data pack.

    TOTAL_ACTIVE comes from the analysed measurement set (measurements_scoped),
    not zone_wells.csv, so it matches the count the QA gates enforce.
    """
    data = REPO_ROOT / zone / "02_data"
    wells = _read_csv(data / "zone_wells.csv")
    meas = _read_csv(data / "measurements_scoped.csv")

    analysed = {r["canonical_well_id"] for r in meas}
    well_type = {r["canonical_well_id"]: r.get("well_type", "") for r in wells}
    years = sorted(r["result_date"][:4] for r in meas if r.get("result_date"))
    if not years:
        sys.exit(f"ERROR: no result_date values in {data/'measurements_scoped.csv'}")

    return {
        "total_active": len(analysed),
        # "general" = every analysed well that is not a fuel monitor (production,
        # research and industrial all count here). Defined as the complement of
        # FUEL_TYPES so any future well_type is captured without code changes and
        # general + fuel == total_active always holds.
        "general": sum(1 for w in analysed if well_type.get(w) not in FUEL_TYPES),
        "fuel": sum(1 for w in analysed if well_type.get(w) in FUEL_TYPES),
        "n_measurements": len(meas),
        "year_start": years[0],
        "year_end": years[-1],
        "wells_in_scope": len(wells),
    }


def derive_focus_order(zone: str) -> str:
    """Lift the `## סדר מוקדים` table from the diagnosis into compact prompt lines."""
    diag = REPO_ROOT / zone / "context_pack" / "04_diagnosis" / "zone_diagnosis.md"
    if not diag.exists():
        sys.exit(f"ERROR: {diag} not found — run Step 4 (zone diagnosis) first")

    block = re.search(
        r"^##\s+סדר מוקדים(.*?)(?:^##\s|\Z)",
        diag.read_text(encoding="utf-8"),
        re.MULTILINE | re.DOTALL,
    )
    if not block:
        sys.exit(f"ERROR: no '## סדר מוקדים' block in {diag} — Gate 4 should have blocked this")

    rows: list[str] = []
    for line in block.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"\|\s*#", line) or re.match(r"\|[\s\-|]+\|?$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        idx, name, location, lead, bucket = cells[:5]
        if not (idx.isdigit() or "פערי" in name or idx == "N"):
            continue
        rows.append(f"{idx}. {name} — מוביל: {lead} (max_bucket={bucket}); מיקום: {location}")

    if not rows:
        sys.exit("ERROR: '## סדר מוקדים' found but no parseable rows")
    return "\n".join(rows)


def derive_terminology_block() -> str:
    """Lift the §B.5 mandatory-substitutions block from STYLE_GUIDE.md (the SSOT).

    The terminology rules live in exactly one place (STYLE_GUIDE §B.5). Both Opus
    prompts receive them by injection here — never by a hand-copied list in the
    template — so they cannot drift from the QA gate that enforces them.
    """
    style = REPO_ROOT / "docs" / "STYLE_GUIDE.md"
    if not style.exists():
        sys.exit(f"ERROR: {style} not found — terminology SSOT missing")
    block = re.search(
        r"^### B\.5 [^\n]*\n(.*?)(?=^---$)",
        style.read_text(encoding="utf-8"),
        re.MULTILINE | re.DOTALL,
    )
    if not block:
        sys.exit("ERROR: no '### B.5' block in docs/STYLE_GUIDE.md — terminology SSOT missing")
    return block.group(1).strip()


def strip_scaffold(text: str, step: str) -> str:
    """Remove template-authoring meta that should not reach Opus."""
    if step == "report":
        text = re.sub(
            r"^> \*\*כיצד להשתמש\*\*.*?\n> תבנית זו עוקבת.*?\n",
            "", text, flags=re.MULTILINE | re.DOTALL,
        )
        text = re.sub(r"\n## Workflow — Filling the Template.*\Z", "\n", text, flags=re.DOTALL)
    elif step == "diagnosis":
        # Drop the "Zone-agnostic / placeholders" and "Pilot status" authoring notes.
        text = re.sub(r"^> \*\*Zone-agnostic\*\*.*?\n", "", text, flags=re.MULTILINE)
        text = re.sub(r"^> \*\*Pilot status.*?\n", "", text, flags=re.MULTILINE)
    return text


def replacements_for(step: str, zone: str, args) -> dict:
    name_en = args.name_en or zone
    if step == "report":
        md = derive_metadata(zone)
        return {
            "ZONE": zone,
            "ZONE_NAME_HE": args.name_he,
            "ZONE_NAME_EN": name_en,
            "GENERAL_COUNT": str(md["general"]),
            "FUEL_COUNT": str(md["fuel"]),
            "TOTAL_ACTIVE": str(md["total_active"]),
            "N_MEASUREMENTS": str(md["n_measurements"]),
            "YEAR_START": md["year_start"],
            "YEAR_END": md["year_end"],
            "FOCUS_ORDER_LIST": derive_focus_order(zone),
            "TERMINOLOGY_BLOCK": derive_terminology_block(),
            "PRECEDENT_ZONE": args.precedent,
            "PRECEDENT_ZONE_REPORT_NAME": args.precedent_report,
        }, md
    # diagnosis: path-based placeholders (the diagnosis produces focus_order; it
    # does not consume it, so no FOCUS_ORDER_LIST here).
    return {
        "zone_id": zone.lower(),
        "zone_he": args.name_he,
        "data_dir": f"{zone}/02_data",
        "workspace_dir": f"{zone}/lean_workspace/04_deterministic_anchors",
        "forensics_dir": f"{zone}/forensics",
        "context_dir": f"{zone}/context_pack/03_context",
        "output_path": f"{zone}/context_pack/04_diagnosis/zone_diagnosis.md",
        "TERMINOLOGY_BLOCK": derive_terminology_block(),
    }, None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zone", required=True, help="Zone directory name, e.g. Holon")
    ap.add_argument("--step", required=True, choices=["diagnosis", "report"])
    ap.add_argument("--name-he", required=True, help="Hebrew zone name, e.g. 'אזה״ת חולון'")
    ap.add_argument("--name-en", default=None, help="English zone name (default: --zone)")
    ap.add_argument("--precedent", default="Raanana", help="Style-precedent zone (report step)")
    ap.add_argument("--precedent-report", default="RAANANA_REPORT_V2",
                    help="Precedent report basename (report step)")
    args = ap.parse_args()

    step, zone = args.step, args.zone
    template_path = TEMPLATES[step]
    template_text = template_path.read_text(encoding="utf-8")
    template_sha = hashlib.sha256(template_text.encode("utf-8")).hexdigest()[:12]

    # REQ #31.5 — the report step bakes a snapshot of the diagnosis focus_order
    # ({FOCUS_ORDER_LIST}) into the prompt. Stamp the diagnosis sha so gate 3 can
    # detect a stale snapshot if Step 4 (diagnosis) is re-run without re-rendering.
    diagnosis_sha = ""
    if step == "report":
        diag = REPO_ROOT / zone / "context_pack" / "04_diagnosis" / "zone_diagnosis.md"
        if diag.exists():
            diagnosis_sha = hashlib.sha256(
                diag.read_text(encoding="utf-8").encode("utf-8")
            ).hexdigest()[:12]

    repl, md = replacements_for(step, zone, args)

    out = strip_scaffold(template_text, step)
    for key, val in repl.items():
        out = out.replace("{" + key + "}", val)

    extra = ""
    if md is not None:
        extra = (f"  total_active={md['total_active']}  measurements={md['n_measurements']}  "
                 f"years={md['year_start']}-{md['year_end']}\n")
    diag_line = f"     diagnosis_sha256_12={diagnosis_sha}\n" if diagnosis_sha else ""
    stamp = (
        "<!-- RENDERED ARTIFACT — DO NOT EDIT BY HAND.\n"
        f"     Generated by scripts/render_zone_prompt.py --step {step} at "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"     template={template_path.name}\n"
        f"     template_sha256_12={template_sha}\n"
        f"{diag_line}"
        f"{extra}"
        "     Re-run after ANY change to the template or the zone diagnosis. -->\n\n"
    )
    out = stamp + out

    dest = REPO_ROOT / zone / "context_pack" / "05_prompt" / DEST_NAME[step]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")

    # Leftover-placeholder check (step-specific token shapes)
    if step == "report":
        leftover = sorted(set(re.findall(r"\{[A-Z_][A-Z0-9_]*\}", out)))
    else:
        leftover = sorted(set(re.findall(
            r"\{(?:zone_id|zone_he|data_dir|workspace_dir|forensics_dir|context_dir|output_path|TERMINOLOGY_BLOCK)\}",
            out)))

    print(f"✓ rendered {dest.relative_to(REPO_ROOT)}")
    print(f"  step={step}  template={template_path.name}  template_sha256_12={template_sha}"
          + (f"  diagnosis_sha256_12={diagnosis_sha}" if diagnosis_sha else ""))
    if md is not None:
        print(f"  total_active={md['total_active']} (scope wells={md['wells_in_scope']}) "
              f"general={md['general']} fuel={md['fuel']} "
              f"measurements={md['n_measurements']} years={md['year_start']}-{md['year_end']}")
        if md["wells_in_scope"] != md["total_active"]:
            print(f"  note: {md['wells_in_scope']} wells in zone_wells, "
                  f"{md['total_active']} analysed (using analysed count)")
    if leftover:
        print(f"  ✗ unreplaced placeholders remain: {leftover}", file=sys.stderr)
        sys.exit(1)
    print("  no unreplaced placeholders — OK")


if __name__ == "__main__":
    main()
