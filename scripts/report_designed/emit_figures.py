"""Emit Holon DESIGNED figures as standalone PNG files.

Reads:
  scripts/report_designed/template.html (CSS block)
  Holon/lean_workspace/02_data_filtered/measurements_alert.csv
  Holon/lean_workspace/02_data_filtered/trends_alert.csv
  Holon/lean_workspace/04_deterministic_anchors/severity_index_2025_holon.csv
  Holon/lean_workspace/03_evidence_index/data_availability_index.csv

Writes:
  Holon/charts_v2/designed/fig_01_severity_ledger.png
  Holon/charts_v2/designed/fig_02_severity_matrix.png
  Holon/charts_v2/designed/fig_03_cvoc_panels.png
  Holon/charts_v2/designed/fig_04_chromium_panels.png
  Holon/charts_v2/designed/fig_05_btex_panels.png
  Holon/charts_v2/designed/fig_06_monitoring_gaps.png

Pipeline: figure HTML+CSS -> weasyprint PDF -> pdftoppm PNG (300 DPI).
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

import weasyprint
from PIL import Image, ImageChops

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.report_designed import data_loader as dl
from scripts.report_designed import svg_charts as sc


OUTPUT_DIR = REPO_ROOT / "Holon" / "charts_v2" / "designed"
TEMPLATE = REPO_ROOT / "scripts" / "report_designed" / "template.html"


def extract_css(template_path: Path) -> str:
    text = template_path.read_text(encoding="utf-8")
    m = re.search(r"<style>(.*?)</style>", text, re.DOTALL)
    if not m:
        raise RuntimeError("No <style> block in template.html")
    return m.group(1)


def render_figure(figure_html: str, css: str, out_path: Path,
                  page_width_mm: int = 320, page_height_mm: int = 240,
                  dpi: int = 200) -> None:
    """Render a figure HTML fragment to PNG via weasyprint PDF + pdftoppm."""
    page_rule = f"@page {{ size: {page_width_mm}mm {page_height_mm}mm; margin: 8mm; }}"
    html_doc = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head><meta charset="UTF-8"><style>{page_rule}{css}
  body {{ padding: 0; }}
  .doc {{ padding: 0; max-width: none; }}
</style></head>
<body><div class="doc">{figure_html}</div></body></html>"""

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_tmp:
        pdf_path = Path(pdf_tmp.name)
    try:
        weasyprint.HTML(string=html_doc).write_pdf(str(pdf_path))
        # Convert PDF to PNG via pdftoppm (first page only)
        out_stem = out_path.with_suffix("")
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi), "-f", "1", "-l", "1",
             str(pdf_path), str(out_stem)],
            check=True, capture_output=True,
        )
        # pdftoppm writes <stem>-1.png; rename
        produced = out_stem.parent / f"{out_stem.name}-1.png"
        if produced.exists():
            produced.rename(out_path)
        else:
            raise RuntimeError(f"pdftoppm did not produce {produced}")
    finally:
        pdf_path.unlink(missing_ok=True)

    _trim_whitespace(out_path)


def _trim_whitespace(png_path: Path, padding: int = 40, threshold: int = 25) -> None:
    """Auto-trim background borders (white page margin + cream body bg), keeping a small padding.

    Treats any pixel close to cream (#fdfcf9) or white as background.
    """
    img = Image.open(png_path).convert("RGB")
    # Mask: True for "content" pixels (not background)
    import numpy as np
    arr = np.array(img)
    # Cream background
    cream = np.array([253, 252, 249])
    white = np.array([255, 255, 255])
    near_cream = np.all(np.abs(arr - cream) <= threshold, axis=2)
    near_white = np.all(np.abs(arr - white) <= threshold, axis=2)
    bg_mask = near_cream | near_white
    content_mask = ~bg_mask
    if not content_mask.any():
        return
    rows = np.where(content_mask.any(axis=1))[0]
    cols = np.where(content_mask.any(axis=0))[0]
    upper, lower = int(rows[0]), int(rows[-1]) + 1
    left, right = int(cols[0]), int(cols[-1]) + 1
    left = max(0, left - padding)
    upper = max(0, upper - padding)
    right = min(img.width, right + padding)
    lower = min(img.height, lower + padding)
    cropped = img.crop((left, upper, right, lower))
    cropped.save(png_path, optimize=True)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    css = extract_css(TEMPLATE)

    print("Loading data ...")
    measurements = dl.load_measurements_alert()
    trends = dl.load_trends_alert()
    severity = dl.load_severity_index()
    data_avail = dl.load_data_availability()

    alert_borehole_ids = set(measurements["canonical_id"].unique())
    severity_alert = severity[severity["borehole"].isin(alert_borehole_ids)].copy()

    figures = [
        ("fig_01_severity_ledger.png",
         lambda: sc.svg_severity_ledger(severity_alert),
         dict(page_width_mm=280, page_height_mm=140)),
        ("fig_02_severity_matrix.png",
         lambda: sc.svg_severity_matrix(severity_alert, trends, data_avail),
         dict(page_width_mm=320, page_height_mm=700)),
        ("fig_03_cvoc_panels.png",
         lambda: sc.svg_cvoc_panels(measurements, severity),
         dict(page_width_mm=320, page_height_mm=400)),
        ("fig_04_chromium_panels.png",
         lambda: sc.svg_chromium_panels(measurements),
         dict(page_width_mm=320, page_height_mm=300)),
        ("fig_05_btex_panels.png",
         lambda: sc.svg_btex_panels(measurements),
         dict(page_width_mm=320, page_height_mm=300)),
        ("fig_06_monitoring_gaps.png",
         lambda: sc.svg_monitoring_gaps(data_avail, severity),
         dict(page_width_mm=280, page_height_mm=220)),
    ]

    for name, builder, page_args in figures:
        print(f"Rendering {name} ...")
        html = builder()
        out = OUTPUT_DIR / name
        render_figure(html, css, out, **page_args)
        size = out.stat().st_size
        print(f"  wrote {out.relative_to(REPO_ROOT)} ({size:,} bytes)")

    print("Done.")


if __name__ == "__main__":
    main()
