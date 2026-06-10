"""Systematic Water Authority reference search — pipeline methodology step.

Scans the zone's base report excerpt for literary references (numbered citations),
then tries a set of URL patterns on gov.il / water.gov.il to locate each reference.
Produces {zone}/data/external/authority_refs_search.json with per-reference status.

Usage:
    python scripts/search_water_authority.py --zone raanana
    python scripts/search_water_authority.py --zone raanana --dry-run

This script is intended as step 0 in the zone report pipeline, run before
writing zone summaries and drilling cards so attribution confidence is up to date.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# URL patterns to probe, in priority order.
# {zone} = zone slug (e.g. "raanana"), {year} = 4-digit year.
URL_PATTERNS = [
    "https://www.gov.il/BlobFolder/reports/industry/he/water-sources-status_tehom_{zone}-{year}.pdf",
    "https://www.gov.il/BlobFolder/reports/industry/he/tehom_{zone}_{year}.pdf",
    "https://www.gov.il/BlobFolder/reports/industry/he/water-sources-status_{zone}_{year}.pdf",
    "https://water.gov.il/Hebrew/ProfessionalInfoAndData/Allocation-Consumption-andProductionData/DocLib/{zone}_{year}.pdf",
    "https://water.gov.il/Hebrew/ProfessionalInfoAndData/Docs/{zone}-monitoring-{year}.pdf",
]

# Regex patterns for extracting reference numbers + metadata from Markdown excerpts.
# Supports:
#   <!-- ref: 19 | year: 2013 | title: ... -->   (structured comment — most reliable)
#   "[19] מערך ניטור..."  or  "19. מערך ניטור..."  (numbered bibliography lines)
_STRUCTURED_REF_RE = re.compile(
    r"<!--\s*ref:\s*(\d+)\s*\|\s*year:\s*(\d{4})\s*\|\s*title:\s*(.+?)\s*-->",
    re.IGNORECASE,
)
_REF_LINE_RE = re.compile(
    r"^\s*[\[\(]?(\d{1,3})[\]\)\.]\s+(.+)$", re.MULTILINE
)
_YEAR_IN_TITLE_RE = re.compile(r"\b(19|20)\d{2}\b")


def _extract_references(excerpt_md: str) -> list[dict]:
    """Parse numbered references from a Markdown excerpt file.

    Prefers structured <!-- ref: N | year: YYYY | title: ... --> comments,
    then falls back to numbered lines like '[19] title...' or '19. title...'.
    Structured comments take priority over line-based matches for the same ref number.
    """
    refs: dict[int, dict] = {}

    # Structured comments (highest reliability)
    for m in _STRUCTURED_REF_RE.finditer(excerpt_md):
        ref_num = int(m.group(1))
        year = int(m.group(2))
        title = m.group(3).strip()
        refs[ref_num] = {"ref_number": ref_num, "title": title, "years": [year]}

    # Numbered lines (fallback — only add refs not already captured above)
    for m in _REF_LINE_RE.finditer(excerpt_md):
        ref_num = int(m.group(1))
        if ref_num in refs:
            continue  # already captured via structured comment
        title = m.group(2).strip()
        years = [int(y) for y in _YEAR_IN_TITLE_RE.findall(title)]
        if years:  # skip numbered items without a year (section headers, etc.)
            refs[ref_num] = {"ref_number": ref_num, "title": title, "years": years}

    return sorted(refs.values(), key=lambda r: r["ref_number"])


def _probe_url(url: str, timeout: int = 30) -> str:
    """Return 'found', 'not_found', or 'forbidden'."""
    try:
        import requests
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WaterAuthRefSearch/1.0; research)",
            "Accept": "application/pdf,*/*",
            "Accept-Language": "he,en;q=0.9",
        }
        r = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            # Verify content-type hints at PDF
            ct = r.headers.get("Content-Type", "")
            if "pdf" in ct or "octet" in ct:
                return "found"
            # Fall back to GET to check body
            r2 = requests.get(url, headers=headers, timeout=timeout, stream=True)
            chunk = r2.raw.read(8)
            if b"%PDF" in chunk:
                return "found"
            return "not_found"
        if r.status_code == 403:
            return "forbidden"
        return "not_found"
    except Exception:
        return "not_found"


def search_zone(zone: str, dry_run: bool = False) -> list[dict]:
    """Search all references found in the zone's excerpt file."""
    excerpt_path = (
        REPO_ROOT / zone.title() / "data" / "external" / "report_2021_raanana_excerpt.md"
    )
    if not excerpt_path.exists():
        # Try generic name
        excerpt_path = (
            REPO_ROOT / zone.title() / "data" / "external" / f"report_2021_{zone}_excerpt.md"
        )
    if not excerpt_path.exists():
        print(f"WARNING: No excerpt file found for zone '{zone}'. "
              f"Expected: {excerpt_path}", file=sys.stderr)
        return []

    excerpt_text = excerpt_path.read_text(encoding="utf-8")
    refs = _extract_references(excerpt_text)
    print(f"Found {len(refs)} references in {excerpt_path.name}")

    # Also add any known URLs supplied in the excerpt as <!-- url: ... --> comments
    inline_urls = re.findall(r"<!--\s*url:\s*(https?://\S+)\s*-->", excerpt_text)

    results = []
    for ref in refs:
        ref_result = {
            "ref_number": ref["ref_number"],
            "title": ref["title"],
            "years_in_title": ref["years"],
            "urls_tried": [],
            "status": "not_searched",
            "local_pdf": None,
            "extraction_summary": "",
        }

        if not ref["years"]:
            ref_result["status"] = "no_year_in_title"
            results.append(ref_result)
            continue

        urls_to_try = []
        for year in ref["years"]:
            for pattern in URL_PATTERNS:
                urls_to_try.append(pattern.format(zone=zone, year=year))

        # Remove duplicates while preserving order
        seen = set()
        urls_to_try = [u for u in urls_to_try if not (u in seen or seen.add(u))]

        ref_result["urls_tried"] = urls_to_try

        if dry_run:
            ref_result["status"] = "dry_run"
            results.append(ref_result)
            continue

        found_url = None
        for url in urls_to_try:
            status = _probe_url(url)
            if status == "found":
                found_url = url
                ref_result["status"] = "found"
                ref_result["found_url"] = url
                break
            elif status == "forbidden":
                ref_result["status"] = "forbidden"
                # Still try other patterns
            time.sleep(0.5)  # polite delay between requests

        if ref_result["status"] not in ("found", "forbidden"):
            ref_result["status"] = "not_found"

        # If found, trigger download via fetch_water_authority_refs
        if found_url and ref["years"]:
            ref_result["extraction_summary"] = (
                f"Use: python scripts/fetch_water_authority_refs.py "
                f"--zone {zone} --year {ref['years'][0]}"
            )

        results.append(ref_result)
        print(f"  [{ref['ref_number']:>3}] {ref['title'][:50]:<50} → {ref_result['status']}")

    # Add inline URLs from excerpt
    for url in inline_urls:
        year_m = _YEAR_IN_TITLE_RE.search(url)
        year = int(year_m.group()) if year_m else None
        entry = {
            "ref_number": "inline",
            "title": url,
            "years_in_title": [year] if year else [],
            "urls_tried": [url],
            "status": "dry_run" if dry_run else _probe_url(url),
            "local_pdf": None,
            "extraction_summary": "",
        }
        results.append(entry)
        if not dry_run:
            print(f"  [inline] {url[:60]} → {entry['status']}")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zone", default="raanana")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse references and list URLs to try, without making network requests",
    )
    args = parser.parse_args()

    print(f"Water Authority reference search — zone: {args.zone}"
          + (" [DRY RUN]" if args.dry_run else ""))

    results = search_zone(args.zone, dry_run=args.dry_run)

    out_dir = REPO_ROOT / args.zone.title() / "data" / "external"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "authority_refs_search.json"

    summary = {
        "zone": args.zone,
        "search_date": str(date.today()),
        "dry_run": args.dry_run,
        "total_refs": len(results),
        "found": sum(1 for r in results if r["status"] == "found"),
        "forbidden": sum(1 for r in results if r["status"] == "forbidden"),
        "not_found": sum(1 for r in results if r["status"] == "not_found"),
        "references": results,
    }

    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults → {out_path.relative_to(REPO_ROOT)}")
    print(f"  found={summary['found']} forbidden={summary['forbidden']} not_found={summary['not_found']}")


if __name__ == "__main__":
    main()
