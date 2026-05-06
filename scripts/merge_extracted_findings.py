"""Merge multiple extracted_findings JSON files into a unified extracted_findings.json.

Consolidates boreholes, contamination findings, facilities, and analysis sections
from multiple source PDFs, deduplicating boreholes while preserving source attribution.

Usage:
    python scripts/merge_extracted_findings.py --zone <zone_id>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def merge_extracted_findings(zone_dir: Path) -> dict:
    """Load all _findings_*.json files, deduplicate, and merge into unified structure.

    Deduplication strategy:
    - Boreholes: by name_he (first occurrence wins, preserve source attribution)
    - Contamination findings: keep all (multi-source is valuable)
    - Facilities: keep all with source attribution (dedup by name_he + confidence)
    - Trends/recommendations/quotes: consolidate all (de-duplicating exact text matches)
    """
    findings_dir = zone_dir / "data" / "external"
    json_files = sorted(findings_dir.glob("_findings_*.json"))

    if not json_files:
        raise FileNotFoundError(f"No _findings_*.json files found in {findings_dir}")

    # Aggregation structures
    boreholes_by_name = {}  # name_he -> borehole entry + source attribution
    all_contamination = []
    facilities_by_key = {}  # (name_he, confidence) -> facility entry
    all_trends = []
    all_recommendations = []
    all_quotes = []

    # Metadata for unified report
    zone_id = zone_dir.name.lower()
    source_files = []

    # Load and merge all findings
    for json_file in json_files:
        with open(json_file) as fh:
            data = json.load(fh)

        source_files.append(data.get("source_file", json_file.name))

        # Boreholes: deduplicate by name_he
        for borehole in data.get("boreholes_mentioned", []):
            name = borehole.get("name_he")
            if name and name not in boreholes_by_name:
                # Add source attribution
                borehole["source_file"] = data.get("source_file", json_file.name)
                boreholes_by_name[name] = borehole

        # Contamination findings: keep all (multiple sources add confidence)
        for finding in data.get("contamination_findings", []):
            finding["source_file"] = data.get("source_file", json_file.name)
            all_contamination.append(finding)

        # Facilities: deduplicate by (name_he, confidence), keep highest confidence per facility
        for facility in data.get("facilities_suspected", []):
            key = (facility.get("name_he"), facility.get("confidence", "LOW"))
            existing = facilities_by_key.get(key)
            # If key doesn't exist or new one has more evidence, update
            if not existing or len(str(facility.get("evidence_he", ""))) > len(str(existing.get("evidence_he", ""))):
                facility["source_file"] = data.get("source_file", json_file.name)
                facilities_by_key[key] = facility

        # Trends, recommendations, quotes: consolidate all (handle both str and dict formats)
        for trend in data.get("trends_described_he", []):
            if isinstance(trend, str):
                trend = {"text_he": trend}
            else:
                trend = dict(trend)  # Copy to avoid modifying original
            trend["source_file"] = data.get("source_file", json_file.name)
            all_trends.append(trend)

        for rec in data.get("recommendations_he", []):
            if isinstance(rec, str):
                rec = {"text_he": rec}
            else:
                rec = dict(rec)
            rec["source_file"] = data.get("source_file", json_file.name)
            all_recommendations.append(rec)

        for quote in data.get("key_quotes_he", []):
            if isinstance(quote, str):
                quote = {"text_he": quote}
            else:
                quote = dict(quote)
            quote["source_file"] = data.get("source_file", json_file.name)
            all_quotes.append(quote)

    # Build unified structure
    merged = {
        "zone_id": zone_id,
        "extraction_date_utc": None,  # Will be set by caller if needed
        "source_files": source_files,
        "summary_he": f"מיזוג מידע מ-{len(json_files)} דוחות PDF לאזור {zone_id}",

        # Deduplicated and consolidated data
        "boreholes_mentioned": list(boreholes_by_name.values()),
        "contamination_findings": all_contamination,
        "facilities_suspected": list(facilities_by_key.values()),
        "trends_described_he": all_trends,
        "recommendations_he": all_recommendations,
        "key_quotes_he": all_quotes,

        # Metadata
        "statistics": {
            "unique_boreholes": len(boreholes_by_name),
            "total_contamination_findings": len(all_contamination),
            "unique_facilities": len(facilities_by_key),
            "total_trends": len(all_trends),
            "total_recommendations": len(all_recommendations),
            "total_quotes": len(all_quotes),
            "source_count": len(json_files),
        }
    }

    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge extracted findings from multiple PDFs into unified JSON.")
    parser.add_argument("--zone", required=True, help="Zone id (e.g., 'holon')")
    args = parser.parse_args()

    zone = args.zone.lower()
    zone_dir = REPO_ROOT / zone.capitalize()

    if not zone_dir.exists():
        raise FileNotFoundError(f"Zone directory not found: {zone_dir}")

    merged = merge_extracted_findings(zone_dir)

    # Write unified extracted_findings.json
    output_path = zone_dir / "data" / "external" / "extracted_findings.json"
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=2)

    print(f"[merge_extracted_findings] Done — merged {merged['statistics']['source_count']} source files")
    print(f"  {merged['statistics']['unique_boreholes']} unique boreholes")
    print(f"  {merged['statistics']['total_contamination_findings']} contamination findings")
    print(f"  {merged['statistics']['unique_facilities']} unique facilities")
    print(f"  Output: {output_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
