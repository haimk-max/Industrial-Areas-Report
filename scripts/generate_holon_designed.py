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
    """Convert minimal markdown (bold, lists, paragraphs) to HTML."""
    if not md:
        return ""

    lines = md.split("\n")
    html_parts = []
    in_list = False
    list_type = None

    for line in lines:
        stripped = line.strip()

        # Ordered list item (1. ... )
        m_ol = re.match(r"^(\d+)\.\s+(.+)", stripped)
        # Unordered list item (- ... )
        m_ul = re.match(r"^[-*]\s+(.+)", stripped)

        if m_ol:
            if not in_list or list_type != "ol":
                if in_list:
                    html_parts.append(f"</{list_type}>")
                html_parts.append("<ol>")
                in_list = True
                list_type = "ol"
            html_parts.append(f"<li>{_inline(m_ol.group(2))}</li>")
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
                # Continuation of last list item — append inside
                html_parts.append(f"<br>{_inline(stripped)}")
            else:
                html_parts.append(f"<p>{_inline(stripped)}</p>")

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

    print(f"  measurements_alert: {len(measurements):,} rows")
    print(f"  trends_alert: {len(trends)} rows")
    print(f"  severity_index: {len(severity)} pairs")
    print(f"  alert_boreholes: {len(alert)} wells")

    print(f"Extracting narrative from {args.report_v4.name} ...")
    narrative = dl.extract_narrative_sections(args.report_v4)
    print(f"  extracted sections: {list(narrative.keys())}")

    print("Building SVG figures ...")
    # Filter severity to only ALERT boreholes
    alert_borehole_ids = set(measurements['canonical_id'].unique())
    severity_alert = severity[severity['borehole'].isin(alert_borehole_ids)].copy()

    ledger_f1 = sc.svg_severity_ledger(severity_alert)
    matrix_f2 = sc.svg_severity_matrix(severity_alert, trends, data_avail)
    cvoc_f3 = sc.svg_cvoc_panels(measurements, severity)
    chromium_f4 = sc.svg_chromium_panels(measurements)
    btex_f5 = sc.svg_btex_panels(measurements)
    gaps_f6 = sc.svg_monitoring_gaps(data_avail, severity)
    recs_f7 = sc.html_recommendations_table()

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
        "{{MASTHEAD_INTRO}}": _strip_md(narrative.get("masthead_intro", "")),
        "{{FOUR_FOCI}}": md_to_html(narrative.get("four_foci", "")),
        "{{CURRENT_STORY}}": md_to_html(narrative.get("current_story", "")),
        "{{LEDGER_F1}}": ledger_f1,
        "{{MATRIX_F2}}": matrix_f2,
        "{{CVOC_PANELS_F3}}": cvoc_f3,
        "{{CHROMIUM_PANELS_F4}}": chromium_f4,
        "{{BTEX_PANELS_F5}}": btex_f5,
        "{{GAPS_F6}}": gaps_f6,
        "{{RECOMMENDATIONS_F7}}": recs_f7,
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
