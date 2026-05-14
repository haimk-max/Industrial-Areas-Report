"""Generate the designed Holon V4 report (HTML with academic monochrome design).

Reads:
  Holon/lean_workspace/02_data_filtered/measurements_alert.csv
  Holon/lean_workspace/02_data_filtered/trends_alert.csv
  Holon/lean_workspace/04_deterministic_anchors/severity_index_2025_holon.csv
  Holon/lean_workspace/03_evidence_index/data_availability_index.csv
  Holon/output/HOLON_REPORT_V4.md (for narrative extraction)
  scripts/report_designed/template.html

Writes:
  Holon/output/HOLON_REPORT_DESIGNED.html

Usage:
  python scripts/generate_holon_designed.py
  python scripts/generate_holon_designed.py --output some/other/path.html
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.report_designed import data_loader as dl
from scripts.report_designed import svg_charts as sc


def md_to_html(md: str) -> str:
    """Convert minimal markdown (bold, lists, paragraphs, tables) to HTML.

    Preserves explicit numbering for ordered lists (uses <li value="N">) so that
    items separated by <ul> blocks continue counting correctly.
    """
    if not md:
        return ""

    lines = md.split("\n")
    html_parts = []
    in_list = False
    list_type = None
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Markdown table detection: header line followed by separator line (|---|---|)
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|\s*$", lines[i + 1].strip()):
            if in_list:
                html_parts.append(f"</{list_type}>")
                in_list = False
                list_type = None
            # Parse table
            header_cells = [c.strip() for c in stripped.strip("|").split("|")]
            html_parts.append('<table class="data-table">')
            html_parts.append("<thead><tr>")
            for c in header_cells:
                html_parts.append(f"<th>{_inline(c)}</th>")
            html_parts.append("</tr></thead>")
            html_parts.append("<tbody>")
            i += 2  # Skip header and separator
            while i < len(lines) and lines[i].strip().startswith("|"):
                row_cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                html_parts.append("<tr>")
                for c in row_cells:
                    html_parts.append(f"<td>{_inline(c)}</td>")
                html_parts.append("</tr>")
                i += 1
            html_parts.append("</tbody></table>")
            continue

        # Ordered list item (1. ... )
        m_ol = re.match(r"^(\d+)\.\s+(.+)", stripped)
        # Unordered list item (- ... )
        m_ul = re.match(r"^[-*]\s+(.+)", stripped)

        if m_ol:
            num = int(m_ol.group(1))
            if not in_list or list_type != "ol":
                if in_list:
                    html_parts.append(f"</{list_type}>")
                html_parts.append("<ol>")
                in_list = True
                list_type = "ol"
            html_parts.append(f'<li value="{num}">{_inline(m_ol.group(2))}</li>')
        elif m_ul:
            if not in_list or list_type != "ul":
                if in_list:
                    html_parts.append(f"</{list_type}>")
                html_parts.append("<ul>")
                in_list = True
                list_type = "ul"
            html_parts.append(f"<li>{_inline(m_ul.group(1))}</li>")
        elif stripped == "":
            if in_list:
                html_parts.append(f"</{list_type}>")
                in_list = False
                list_type = None
            html_parts.append("")
        else:
            if in_list:
                html_parts.append(f"<br>{_inline(stripped)}")
            else:
                html_parts.append(f"<p>{_inline(stripped)}</p>")
        i += 1

    if in_list:
        html_parts.append(f"</{list_type}>")

    return "\n".join(html_parts)


def _inline(text: str) -> str:
    """Inline markdown: **bold**, `code`."""
    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


# Pollutant names + units that must be isolated for proper RTL flow in mixed Hebrew text.
_BIDI_POLLUTANTS = (
    "TCE|PCE|MTBE|BTEX|CVOC|PFAS|PFHxS|PFOA|PFOS|PFNA|DCE|VC|DNAPL|AFFF|PVDC|"
    "DWS|NMVOC|ITM|PRTR|WMS|OSM|AFFF|SNR"
)
_BIDI_PATTERNS = [
    # Numbers + units: "27,860 µg/L", "85,000%", "8.5 mg/L"
    (re.compile(r'(\d[\d,\.]*\s*(?:µg/L|mg/L|ng/L|µS/cm|%|דונם|מ"ק|ק"ג/שנה))'), r'<bdi>\1</bdi>'),
    # Statistics: Z=2.60, p=0.009, SNR=1.32, n=5
    (re.compile(r'\b(Z=\d+\.?\d*|p=\d+\.?\d*|SNR=\d+\.?\d*|n=\d+)'), r'<bdi>\1</bdi>'),
    # Compound CVOC names with digits/commas/hyphens: 1,1-DCE, cis-1,2-DCE, 1,4-dioxane
    (re.compile(r'\b(cis-1,2-DCE|trans-1,2-DCE|1,1-DCE|1,2-DCA|1,4-[Dd]ioxane|1,1,1-TCA|CCl[₄4])'), r'<bdi>\1</bdi>'),
    # Standalone pollutant names
    (re.compile(rf'\b({_BIDI_POLLUTANTS})\b'), r'<bdi>\1</bdi>'),
    # Metal symbols: Cr, Ni, Pb, As, Fe, Al, Cd
    (re.compile(r'\b(Cr|Ni|Pb|As|Fe|Al|Cd)\b(?![<>])'), r'<bdi>\1</bdi>'),
    # Standalone years inside Hebrew text: 2012, 2026
    (re.compile(r'(?<![\d/-])\b(20\d{2})\b(?![\d/-])'), r'<bdi>\1</bdi>'),
]


def wrap_bidi(html: str) -> str:
    """Wrap LTR tokens (numbers, units, pollutants) in <bdi> for RTL flow.

    Avoids double-wrapping and skips content inside existing tags.
    """
    if not html:
        return html
    # Split into segments alternating between tag content and text content.
    # Apply bidi wrapping only to text content.
    parts = []
    last_end = 0
    for m in re.finditer(r'<[^>]+>', html):
        # Text before this tag — apply wrapping
        text_segment = html[last_end:m.start()]
        for pattern, repl in _BIDI_PATTERNS:
            text_segment = pattern.sub(repl, text_segment)
        parts.append(text_segment)
        # Tag itself — preserve as-is
        parts.append(m.group(0))
        last_end = m.end()
    # Final text segment after last tag
    text_segment = html[last_end:]
    for pattern, repl in _BIDI_PATTERNS:
        text_segment = pattern.sub(repl, text_segment)
    parts.append(text_segment)
    result = "".join(parts)
    # Prevent double wrapping if a pattern already inside <bdi>
    result = re.sub(r'<bdi><bdi>([^<]+)</bdi></bdi>', r'<bdi>\1</bdi>', result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Holon designed report variant")
    parser.add_argument("--output", type=Path,
                        default=REPO_ROOT / "Holon" / "output" / "HOLON_REPORT_DESIGNED.html")
    parser.add_argument("--template", type=Path,
                        default=REPO_ROOT / "scripts" / "report_designed" / "template.html")
    parser.add_argument("--report-v4", type=Path,
                        default=REPO_ROOT / "Holon" / "output" / "HOLON_REPORT_V4.md")
    args = parser.parse_args()

    print("Loading data from Holon/lean_workspace/ ...")
    measurements = dl.load_measurements_alert()
    trends = dl.load_trends_alert()
    severity = dl.load_severity_index()
    data_avail = dl.load_data_availability()
    alert = dl.load_alert_boreholes()
    classification = dl.load_borehole_classification()

    print(f"  measurements_alert: {len(measurements):,} rows")
    print(f"  trends_alert: {len(trends)} rows")
    print(f"  severity_index: {len(severity)} pairs")
    print(f"  alert_boreholes: {len(alert)} wells")
    print(f"  borehole_classification: {len(classification)} boreholes")

    print(f"Extracting narrative from {args.report_v4.name} ...")
    narrative = dl.extract_narrative_sections(args.report_v4)
    print(f"  extracted sections: {list(narrative.keys())}")

    print("Building SVG figures ...")
    # Filter severity to only ALERT boreholes
    alert_borehole_ids = set(measurements['canonical_id'].unique())
    severity_alert = severity[severity['borehole'].isin(alert_borehole_ids)].copy()

    # PROCESS_GUIDE §VIII.1: Opus picks boreholes via V4.md; chart engine renders them per style guide.
    report_boreholes = dl.extract_report_boreholes(args.report_v4, severity)
    print(f"  V4.md boreholes_override: {len(report_boreholes)} mentioned")

    ledger_f1 = sc.svg_severity_ledger(severity_alert)
    matrix_f2 = sc.svg_severity_matrix(severity_alert, trends, data_avail)
    cvoc_f3 = sc.svg_cvoc_panels(measurements, severity, boreholes_override=report_boreholes)
    chromium_f4 = sc.svg_chromium_panels(measurements, boreholes_override=report_boreholes)
    btex_f5 = sc.svg_btex_panels(measurements, boreholes_override=report_boreholes)
    gaps_f6 = sc.svg_monitoring_gaps(data_avail, severity)
    recs_f7 = sc.html_recommendations_table()

    # Generate borehole classification visualizations (Phase 2 - statistical analysis)
    # Include classification definitions extracted from V4
    class_intro = narrative.get("classification_intro", "")
    class_table_f8 = sc.svg_borehole_classification_table(classification, class_intro)
    class_map_f9 = sc.svg_borehole_map_html(classification)

    print("Filling template ...")
    template = args.template.read_text(encoding="utf-8")

    # Count INCREASING trends
    n_increasing = 0
    if not trends.empty:
        n_increasing = (trends.classification == "INCREASING").sum()

    n_alert = len(alert) if not alert.empty else 25

    replacements = {
        "{{GENERATED_AT}}": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "{{N_MEASUREMENTS}}": f"{len(measurements):,}",
        "{{N_ALERT}}": str(n_alert),
        "{{N_INCREASING}}": str(int(n_increasing)),
        "{{MASTHEAD_INTRO}}": wrap_bidi(_strip_md(narrative.get("masthead_intro", ""))),
        "{{FOUR_FOCI}}": wrap_bidi(md_to_html(narrative.get("four_foci", ""))),
        "{{CURRENT_STORY}}": wrap_bidi(md_to_html(narrative.get("current_story", ""))),
        "{{LEDGER_F1}}": wrap_bidi(ledger_f1),
        "{{MATRIX_F2}}": matrix_f2,
        "{{CVOC_PANELS_F3}}": cvoc_f3,
        "{{CHROMIUM_PANELS_F4}}": chromium_f4,
        "{{BTEX_PANELS_F5}}": btex_f5,
        "{{GAPS_F6}}": gaps_f6,
        "{{RECOMMENDATIONS_F7}}": wrap_bidi(recs_f7),
        "{{CLASSIFICATION_TABLE_F8}}": wrap_bidi(class_table_f8),
        "{{BOREHOLE_MAP_F9}}": class_map_f9,
    }

    html = template
    for key, val in replacements.items():
        html = html.replace(key, str(val))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"Wrote {args.output} ({len(html):,} bytes)")


def _strip_md(text: str) -> str:
    """Strip MD bold markers from inline text for masthead use."""
    if not text:
        return ""
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = text.replace("\n", " ")
    return text


if __name__ == "__main__":
    main()
