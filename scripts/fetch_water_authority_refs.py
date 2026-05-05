"""Fetch and extract Water Authority monitoring PDFs from gov.il.

Usage:
    python scripts/fetch_water_authority_refs.py --zone raanana --year 2013
    python scripts/fetch_water_authority_refs.py --zone raanana --years 2013 2015 2018

Saves PDF to {zone}/data/external/water_authority_{zone}_{year}.pdf
Saves extracted text to {zone}/data/external/monitoring_{year}_{zone}.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# URL patterns to try, in priority order
URL_PATTERNS = [
    "https://www.gov.il/BlobFolder/reports/industry/he/water-sources-status_tehom_{zone}-{year}.pdf",
    "https://www.gov.il/BlobFolder/reports/industry/he/tehom_{zone}_{year}.pdf",
    "https://water.gov.il/Hebrew/ProfessionalInfoAndData/Allocation-Consumption-andProductionData/DocLib/{zone}_{year}.pdf",
]

KNOWN_FACILITIES = [
    "Aidchem", "אידכם",
    "Edge Medical", "אדג'",
    "Richardson", "ריצ'רדסון",
    "פז", "Paz",
    "חשמל", "IEC",
    "BTEX", "TCE", "PCE", "PFAS",
    "בנזן", "טריכלורואתילן", "טטרכלורואתילן",
]


def _make_headers() -> dict:
    return {
        "User-Agent": "Mozilla/5.0 (compatible; GovILReader/1.0; research use)",
        "Accept": "application/pdf,*/*",
        "Accept-Language": "he,en;q=0.9",
        "Referer": "https://www.gov.il/he/departments/topics/water_quality",
    }


def _try_fetch(url: str, dest: Path) -> bool:
    """Try to download PDF from url to dest. Returns True on success."""
    try:
        import requests
        r = requests.get(url, headers=_make_headers(), timeout=45, stream=True)
        if r.status_code == 200 and b"%PDF" in r.content[:8]:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(r.content)
            print(f"  Downloaded: {url} → {dest.name} ({len(r.content)//1024} KB)")
            return True
        else:
            print(f"  HTTP {r.status_code}: {url}")
            return False
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return False


def _extract_with_pdftotext(pdf_path: Path) -> list[str] | None:
    """Extract per-page text using poppler pdftotext. Returns list of page texts, or None on failure.

    pdftotext handles CID-encoded Hebrew fonts correctly where pdfplumber/pdfminer fail.
    """
    import subprocess
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=60, check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    # pdftotext separates pages with form-feed (\f)
    pages = result.stdout.split("\f")
    # Drop trailing empty page if present
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    return pages


def _extract_text(pdf_path: Path, zone: str, year: int) -> str:
    """Extract relevant text from PDF.

    Prefers pdftotext (poppler) — handles Hebrew CID fonts. Falls back to pdfplumber.
    """
    facility_pattern = re.compile("|".join(re.escape(f) for f in KNOWN_FACILITIES), re.IGNORECASE)
    conc_pattern = re.compile(r"\d+\.?\d*\s*(µg/L|mg/L|ppb|ppm|μg/L)", re.IGNORECASE)
    lines_out: list[str] = []

    pages = _extract_with_pdftotext(pdf_path)
    if pages is not None:
        total = len(pages)
        lines_out.append(f"# Water Authority Monitoring Report — {zone.title()} {year}")
        lines_out.append(f"Source: {pdf_path.name} ({total} pages, extracted via pdftotext)\n")
        for page_num, text in enumerate(pages, 1):
            if not text.strip():
                continue
            include = page_num <= 5
            if not include and facility_pattern.search(text):
                include = True
            if not include and conc_pattern.search(text):
                include = True
            if include:
                lines_out.append(f"\n## עמוד {page_num}\n")
                lines_out.append(text.strip())
        return "\n".join(lines_out)

    # Fallback: pdfplumber (does not handle CID-encoded Hebrew correctly, but try anyway)
    try:
        import pdfplumber
    except ImportError:
        return "pdftotext unavailable and pdfplumber not installed"

    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        lines_out.append(f"# Water Authority Monitoring Report — {zone.title()} {year}")
        lines_out.append(f"Source: {pdf_path.name} ({total} pages, extracted via pdfplumber fallback)\n")
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            if not text.strip():
                continue
            include = page_num <= 5
            if not include and facility_pattern.search(text):
                include = True
            if not include and conc_pattern.search(text):
                include = True
            if include:
                lines_out.append(f"\n## עמוד {page_num}\n")
                lines_out.append(text.strip())
                tables = page.extract_tables()
                for t in tables:
                    if t and any(any(cell for cell in row) for row in t):
                        lines_out.append("\n### טבלה\n")
                        for row in t:
                            clean = " | ".join(str(c or "").strip() for c in row)
                            if clean.strip("| "):
                                lines_out.append(f"| {clean} |")
    return "\n".join(lines_out)


def fetch_report(zone: str, year: int, out_dir: Path) -> dict:
    """Attempt to fetch and extract a single report. Returns status dict."""
    result = {
        "zone": zone,
        "year": year,
        "urls_tried": [],
        "status": "not_found",
        "local_pdf": None,
        "local_md": None,
        "extraction_summary": "",
    }

    pdf_dest = out_dir / f"water_authority_{zone}_{year}.pdf"
    md_dest = out_dir / f"monitoring_{year}_{zone}.md"

    # If already downloaded, skip network
    if pdf_dest.exists():
        print(f"  Already downloaded: {pdf_dest.name}")
        result["status"] = "found"
        result["local_pdf"] = str(pdf_dest.relative_to(REPO_ROOT))
    else:
        for pattern in URL_PATTERNS:
            url = pattern.format(zone=zone, year=year)
            result["urls_tried"].append(url)
            if _try_fetch(url, pdf_dest):
                result["status"] = "found"
                result["local_pdf"] = str(pdf_dest.relative_to(REPO_ROOT))
                break

    if result["status"] == "found" and pdf_dest.exists():
        print(f"  Extracting text from {pdf_dest.name}...")
        text = _extract_text(pdf_dest, zone, year)
        md_dest.write_text(text, encoding="utf-8")
        result["local_md"] = str(md_dest.relative_to(REPO_ROOT))
        lines = text.splitlines()
        result["extraction_summary"] = f"{len(lines)} lines extracted from {pdf_dest.stat().st_size//1024} KB PDF"
        print(f"  Extraction: {result['extraction_summary']}")

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zone", default="raanana")
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--years", type=int, nargs="+", default=None)
    args = parser.parse_args()

    years = []
    if args.years:
        years = args.years
    elif args.year:
        years = [args.year]
    else:
        parser.error("Provide --year YYYY or --years YYYY YYYY ...")

    out_dir = REPO_ROOT / args.zone.title() / "data" / "external"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_results = []
    for year in years:
        print(f"\nFetching {args.zone} {year}...")
        res = fetch_report(args.zone, year, out_dir)
        all_results.append(res)
        print(f"  Status: {res['status']}")

    # Write search summary
    summary_path = out_dir / "water_authority_fetch_log.json"
    existing = []
    if summary_path.exists():
        try:
            existing = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    # Merge by zone+year
    merged = {(r["zone"], r["year"]): r for r in existing}
    for r in all_results:
        merged[(r["zone"], r["year"])] = r
    summary_path.write_text(
        json.dumps(list(merged.values()), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nFetch log → {summary_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
