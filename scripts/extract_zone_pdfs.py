"""extract_zone_pdfs.py — Extract text from a zone's PDF reports for AI-agent consumption.

Reads PDFs from `<Zone>/data/external/*.pdf` and `<Zone>/Base-Report/*.pdf` (if exists),
extracts plain text via pdftotext (with -layout flag for Hebrew), and writes:

  <Zone>/data/external/_raw_text/<filename>.txt   — extracted text per PDF
  <Zone>/data/external/_pdf_index.json            — manifest with metadata + page counts

The AI agent (run separately, see CLAUDE.md § Adding a New Zone) reads the
manifest and raw text files, then produces `<Zone>/data/external/extracted_findings.json`
with structured contamination findings, borehole references, and historical context.

Usage:
    python scripts/extract_zone_pdfs.py --zone <zone_id>
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _pdf_page_count(pdf_path: Path) -> int | None:
    """Return page count via pdfinfo, or None if unavailable."""
    try:
        out = subprocess.check_output(
            ["pdfinfo", str(pdf_path)], stderr=subprocess.DEVNULL, text=True
        )
        for line in out.splitlines():
            if line.startswith("Pages:"):
                return int(line.split()[1])
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return None
    return None


def _extract_text(pdf_path: Path, txt_path: Path) -> bool:
    """Run `pdftotext -layout` to extract Hebrew/RTL-friendly text. Returns True on success."""
    try:
        subprocess.check_call(
            ["pdftotext", "-layout", str(pdf_path), str(txt_path)],
            stderr=subprocess.DEVNULL,
        )
        return txt_path.exists() and txt_path.stat().st_size > 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _gather_pdf_dirs(zone_dir: Path) -> list[Path]:
    """Directories where zone-specific PDFs may live."""
    candidates = [
        zone_dir / "data" / "external",
        zone_dir / "Base-Report",
    ]
    return [d for d in candidates if d.exists()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from a zone's PDFs for AI consumption.")
    parser.add_argument("--zone", required=True, help="Zone id (e.g., 'holon')")
    parser.add_argument("--force", action="store_true",
                        help="Re-extract text even if .txt already exists")
    args = parser.parse_args()

    zone = args.zone.lower()
    zone_dir = REPO_ROOT / zone.capitalize()
    if not zone_dir.exists():
        sys.exit(f"Zone directory not found: {zone_dir}")

    if not shutil.which("pdftotext"):
        sys.exit("ERROR: pdftotext not found in PATH. Install poppler-utils.")

    out_text_dir = zone_dir / "data" / "external" / "_raw_text"
    out_text_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "zone_id": zone,
        "extraction_date_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pdf_count": 0,
        "pdfs": [],
    }

    for pdf_dir in _gather_pdf_dirs(zone_dir):
        for pdf_path in sorted(pdf_dir.glob("*.pdf")):
            txt_path = out_text_dir / f"{pdf_path.stem}.txt"
            page_count = _pdf_page_count(pdf_path)

            need_extract = args.force or not txt_path.exists()
            extracted_ok = txt_path.exists()
            if need_extract:
                extracted_ok = _extract_text(pdf_path, txt_path)

            char_count = txt_path.stat().st_size if txt_path.exists() else 0
            manifest["pdfs"].append({
                "filename": pdf_path.name,
                "source_dir": str(pdf_dir.relative_to(REPO_ROOT)),
                "raw_text": str(txt_path.relative_to(REPO_ROOT)) if extracted_ok else None,
                "page_count": page_count,
                "char_count": char_count,
                "extraction_ok": extracted_ok,
            })
            status = "OK" if extracted_ok else "FAILED"
            print(f"  {status}  {pdf_path.name}  ({page_count} pages, {char_count:,} chars)")

    manifest["pdf_count"] = len(manifest["pdfs"])
    manifest_path = zone_dir / "data" / "external" / "_pdf_index.json"
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"\n[extract_zone_pdfs] Done — {manifest['pdf_count']} PDFs processed")
    print(f"  Manifest: {manifest_path.relative_to(REPO_ROOT)}")
    print(f"  Raw text: {out_text_dir.relative_to(REPO_ROOT)}/")
    print(f"\nNext step: run AI agent on raw text → produce extracted_findings.json")
    print(f"  See CLAUDE.md § 8 ('Adding a New Zone') for the agent prompt template")


if __name__ == "__main__":
    main()
