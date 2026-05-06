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


def _load_existing_manifest(manifest_path: Path) -> dict:
    """Load existing _pdf_index.json if present, else return empty structure."""
    if manifest_path.exists():
        try:
            with open(manifest_path, encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _manifest_has_pdf(manifest: dict, pdf_filename: str) -> dict | None:
    """Check if PDF already tracked in manifest by filename. Returns entry if found."""
    for entry in manifest.get("pdfs", []):
        if entry.get("filename") == pdf_filename:
            return entry
    return None


def _pdf_needs_extraction(pdf_path: Path, manifest_entry: dict | None, force: bool) -> bool:
    """Determine if PDF needs extraction based on manifest state and --force flag."""
    if force:
        return True
    if not manifest_entry:
        return True
    # If extraction previously failed, retry
    if not manifest_entry.get("extraction_ok", False):
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from a zone's PDFs for AI consumption.")
    parser.add_argument("--zone", required=True, help="Zone id (e.g., 'holon')")
    parser.add_argument("--force", action="store_true",
                        help="Re-extract text even if .txt already exists")
    parser.add_argument("--include-shared", action="store_true",
                        help="Also process shared Base-Report/ PDFs (TAHAL 2008, Water Authority 2021)")
    args = parser.parse_args()

    zone = args.zone.lower()
    zone_dir = REPO_ROOT / zone.capitalize()
    if not zone_dir.exists():
        sys.exit(f"Zone directory not found: {zone_dir}")

    if not shutil.which("pdftotext"):
        sys.exit("ERROR: pdftotext not found in PATH. Install poppler-utils.")

    out_text_dir = zone_dir / "data" / "external" / "_raw_text"
    out_text_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = zone_dir / "data" / "external" / "_pdf_index.json"
    manifest = _load_existing_manifest(manifest_path)

    # Initialize manifest if new
    if not manifest:
        manifest = {
            "zone_id": zone,
            "extraction_date_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "pdf_count": 0,
            "pdfs": [],
        }

    pdf_dirs_to_process = _gather_pdf_dirs(zone_dir)
    if args.include_shared:
        # Add shared Base-Report directory if it exists
        shared_base_report = REPO_ROOT / "Base-Report"
        if shared_base_report.exists():
            pdf_dirs_to_process.append(shared_base_report)

    processed_count = 0
    skipped_count = 0

    for pdf_dir in pdf_dirs_to_process:
        for pdf_path in sorted(pdf_dir.glob("*.pdf")):
            # Check if already processed
            manifest_entry = _manifest_has_pdf(manifest, pdf_path.name)
            if not _pdf_needs_extraction(pdf_path, manifest_entry, args.force):
                status = "SKIP (cached)"
                skipped_count += 1
            else:
                # Extract text
                txt_path = out_text_dir / f"{pdf_path.stem}.txt"
                page_count = _pdf_page_count(pdf_path)
                extracted_ok = _extract_text(pdf_path, txt_path)
                char_count = txt_path.stat().st_size if txt_path.exists() else 0

                # Update or add manifest entry
                entry = {
                    "filename": pdf_path.name,
                    "source_dir": str(pdf_dir.relative_to(REPO_ROOT)),
                    "raw_text": str(txt_path.relative_to(REPO_ROOT)) if extracted_ok else None,
                    "page_count": page_count,
                    "char_count": char_count,
                    "extraction_ok": extracted_ok,
                    "extraction_date_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }

                if manifest_entry:
                    # Update existing entry
                    idx = next(i for i, e in enumerate(manifest["pdfs"]) if e["filename"] == pdf_path.name)
                    manifest["pdfs"][idx] = entry
                else:
                    # Add new entry
                    manifest["pdfs"].append(entry)

                status = "OK" if extracted_ok else "FAILED"
                processed_count += 1

            print(f"  {status}  {pdf_path.name}  ({pdf_dir.name})")

    # Update manifest
    manifest["pdf_count"] = len(manifest["pdfs"])
    manifest["last_extraction_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"\n[extract_zone_pdfs] Done — {processed_count} processed, {skipped_count} cached")
    print(f"  Manifest: {manifest_path.relative_to(REPO_ROOT)}")
    print(f"  Raw text: {out_text_dir.relative_to(REPO_ROOT)}/")
    print(f"\nNext step: merge extracted findings with scripts/merge_extracted_findings.py")
    print(f"  Then run AI agent on raw text → produce extracted_findings.json")


if __name__ == "__main__":
    main()
