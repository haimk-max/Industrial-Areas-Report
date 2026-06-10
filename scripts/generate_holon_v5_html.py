"""Generate the designed Holon V5 report (full content, academic monochrome design).

Renders ALL sections of HOLON_REPORT_V5.md inside the V4 design language
(masthead, sec-h, figure.frame, data-table). Unlike generate_holon_designed.py
(fixed four-foci slots), this generator is dynamic: it walks the V5 markdown,
renders each section, and injects inline SVG figures at the `**איור N**` anchors.

Figures are produced by the SAME engine as the V4 designed report
(scripts/report_designed/svg_charts.py) using boreholes_override extracted
from the V5 report narrative (PROCESS_GUIDE §VIII.1).

Reads:
  Holon/output/HOLON_REPORT_V5.md
  Holon/lean_workspace/ (chart engine data)
  scripts/report_designed/template.html (CSS head only)

Writes:
  Holon/output/HOLON_REPORT_V5.html

Usage:
  python scripts/generate_holon_v5_html.py
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
from scripts.report_designed import md_utils


# Figure anchor → (engine builder key, English sublabel for fig-h)
# The V5 report references 5 figures by image-markdown + **איור N** caption.
FIGURE_SUBLABELS = {
    1: "ZONE MAP · SEVERITY",
    2: "CVOC · TIME SERIES",
    3: "METALS · TIME SERIES",
    4: "FUEL · TIME SERIES",
    5: "MONITORING GAPS",
}


def md_inline_to_html(text: str) -> str:
    """Inline markdown: **bold**, `code`, and [text](url) stripped to text."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # links → text
    return md_utils.inline(text)


def render_markdown_block(md: str) -> str:
    """Convert a markdown block (no figures) to HTML.

    Handles: ## / ### / #### headers, tables, ordered/unordered lists,
    blockquotes, horizontal rules, and paragraphs.
    """
    lines = md.split("\n")
    out = []
    in_list = False
    list_type = None
    i = 0

    def close_list():
        nonlocal in_list, list_type
        if in_list:
            out.append(f"</{list_type}>")
            in_list = False
            list_type = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Table
        if stripped.startswith("|") and i + 1 < len(lines) and \
                re.match(r"^\|[\s\-:|]+\|\s*$", lines[i + 1].strip()):
            close_list()
            header_cells = [c.strip() for c in stripped.strip("|").split("|")]
            out.append('<table class="data-table">')
            out.append("<thead><tr>")
            for c in header_cells:
                out.append(f"<th>{md_inline_to_html(c)}</th>")
            out.append("</tr></thead><tbody>")
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                out.append("<tr>" + "".join(
                    f"<td>{md_inline_to_html(c)}</td>" for c in row) + "</tr>")
                i += 1
            out.append("</tbody></table>")
            continue

        # Headers (sub-section h3/h4 within a section)
        m_h4 = re.match(r"^####\s+(.+)", stripped)
        m_h3 = re.match(r"^###\s+(.+)", stripped)
        if m_h4:
            close_list()
            out.append(f'<h4 class="sub-h">{md_inline_to_html(m_h4.group(1))}</h4>')
            i += 1
            continue
        if m_h3:
            close_list()
            out.append(f'<h3 class="sub-h">{md_inline_to_html(m_h3.group(1))}</h3>')
            i += 1
            continue

        # Horizontal rule
        if stripped == "---":
            close_list()
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            close_list()
            out.append(f'<blockquote class="note">{md_inline_to_html(stripped.lstrip("> ").strip())}</blockquote>')
            i += 1
            continue

        # Lists
        m_ol = re.match(r"^(\d+)\.\s+(.+)", stripped)
        m_ul = re.match(r"^[-*]\s+(.+)", stripped)
        if m_ol:
            if not in_list or list_type != "ol":
                close_list()
                out.append("<ol>")
                in_list, list_type = True, "ol"
            out.append(f'<li value="{int(m_ol.group(1))}">{md_inline_to_html(m_ol.group(2))}</li>')
        elif m_ul:
            if not in_list or list_type != "ul":
                close_list()
                out.append("<ul>")
                in_list, list_type = True, "ul"
            out.append(f"<li>{md_inline_to_html(m_ul.group(1))}</li>")
        elif stripped == "":
            close_list()
        else:
            close_list()
            out.append(f"<p>{md_inline_to_html(stripped)}</p>")
        i += 1

    close_list()
    return "\n".join(out)


def build_figure_html(fig_num: int, caption_text: str, svg: str) -> str:
    """Wrap an inline SVG in the design-language <figure> structure."""
    sublabel = FIGURE_SUBLABELS.get(fig_num, "")
    caption_html = md_utils.wrap_bidi(md_inline_to_html(caption_text))
    # The SVG is embedded raw — NOT through wrap_bidi. wrap_bidi wraps Latin/numeric
    # runs in <bdi>, which is an HTML element invalid inside SVG <text>; injecting it
    # there silently breaks rendering of year ticks, DWS labels and contaminant
    # labels. The chart engine already handles bidi internally (direction="ltr" root
    # + rtl-title class). Caption text, being HTML, still goes through wrap_bidi.
    return (
        '<figure>\n'
        '  <div class="fig-h">\n'
        f'    <span class="ttl">איור {fig_num}</span>\n'
        f'    <span>{sublabel}</span>\n'
        '  </div>\n'
        f'  <div class="frame">\n{svg}\n  </div>\n'
        f'  <figcaption><span class="lbl">איור {fig_num}</span><span>{caption_html}</span></figcaption>\n'
        '</figure>'
    )


def render_section(section_md: str, figures: dict) -> str:
    """Render one ## section: header + body, injecting figures at anchors.

    A figure anchor is the pattern:
        ![](...)
        **איור N**: caption text
    """
    lines = section_md.split("\n")
    # First line is the "## N. Title" header
    header_line = lines[0].strip()
    m = re.match(r"^##\s+(.+)", header_line)
    title = m.group(1) if m else header_line
    # Split "N. Title" into number + title
    m_num = re.match(r"^(\d+)\.\s+(.+)", title)
    if m_num:
        num_label = f"§{m_num.group(1)}"
        title_text = m_num.group(2)
    else:
        num_label = ""
        title_text = title

    body_md = "\n".join(lines[1:])

    # Split body into segments at figure anchors.
    # Anchor: optional image markdown line, then **איור N**: caption (until blank line)
    fig_pattern = re.compile(
        r"!\[[^\]]*\]\([^)]*\)\s*\n+\s*\*\*איור\s+(\d+)\*\*[::]?\s*(.+?)(?=\n\s*\n|\Z)",
        re.DOTALL,
    )

    parts = []
    last = 0
    for fm in fig_pattern.finditer(body_md):
        # Text before the figure
        pre = body_md[last:fm.start()]
        if pre.strip():
            parts.append(md_utils.wrap_bidi(render_markdown_block(pre)))
        fig_num = int(fm.group(1))
        caption = fm.group(2).strip()
        svg = figures.get(fig_num)
        if svg:
            parts.append(build_figure_html(fig_num, caption, svg))
        last = fm.end()
    # Remaining text
    rest = body_md[last:]
    if rest.strip():
        parts.append(md_utils.wrap_bidi(render_markdown_block(rest)))

    body_html = "\n".join(parts)

    header_html = (
        '<div class="sec-h">'
        + (f'<span class="num">{num_label}</span>' if num_label else "")
        + f'<h2>{md_inline_to_html(title_text)}</h2></div>'
    )
    return f'<section>\n{header_html}\n{body_html}\n</section>'


def build_figures(zone: str = "holon", report_path: Path = None) -> dict:
    """Generate the 5 V5 figures via the shared chart engine.

    zone: zone name (e.g., "holon", "raanana") — used to load zone-specific data
    report_path: the report whose borehole mentions drive panel selection. Must be
    the SAME report being rendered (V7, V8, …) — otherwise the figures show a
    different report's wells. Defaults to latest V5+ report.
    """
    measurements = dl.load_measurements_alert(zone=zone)
    trends = dl.load_trends_alert(zone=zone)
    severity = dl.load_severity_index(zone=zone)
    data_avail = dl.load_data_availability(zone=zone)
    classification = dl.load_borehole_classification(zone=zone)

    if report_path is None:
        # Auto-detect latest report V5+
        report_path = next(
            (p for p in sorted((REPO_ROOT / zone / "output").glob("*_REPORT_V*.md"), reverse=True)),
            None
        )
        if report_path is None:
            report_path = REPO_ROOT / zone / "output" / f"{zone.upper()}_REPORT_V5.md"

    report_boreholes = dl.extract_report_boreholes(report_path, severity, zone=zone)
    print(f"  boreholes_override from {report_path.name}: {len(report_boreholes)} mentioned")

    alert_ids = set(measurements["canonical_id"].unique())
    severity_alert = severity[severity["borehole"].isin(alert_ids)].copy()

    # Load zone polygon for map background
    import json
    _poly_path = REPO_ROOT / "zone_definitions" / "zone_polygons.json"
    _zone_polygon = None
    try:
        with open(_poly_path, encoding="utf-8") as _f:
            _poly_data = json.load(_f)
        _zone_key = zone.lower()
        _zone_polygon = _poly_data.get(_zone_key, _poly_data.get(zone.upper(), {})).get("polygon")
    except Exception:
        pass

    figures = {
        1: sc.svg_borehole_map_html(classification, zone_polygon=_zone_polygon),
        2: sc.svg_cvoc_panels(measurements, severity, boreholes_override=report_boreholes),
        3: sc.svg_chromium_panels(measurements, boreholes_override=report_boreholes),
        4: sc.svg_btex_panels(measurements, boreholes_override=report_boreholes),
        5: sc.svg_monitoring_gaps(data_avail, severity),
    }
    return figures


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate zone V5 designed HTML (full content)")
    parser.add_argument("--zone", type=str, default="holon",
                        help="Zone name (e.g., holon, raanana)")
    parser.add_argument("--report", type=Path,
                        help="Override report path (auto-detected from --zone if not provided)")
    parser.add_argument("--template", type=Path,
                        default=REPO_ROOT / "scripts" / "report_designed" / "template.html")
    parser.add_argument("--output", type=Path,
                        help="Override output path (auto-detected from --zone if not provided)")
    args = parser.parse_args()

    # Auto-detect report/output paths if not provided
    zone = args.zone.lower()
    if args.report is None:
        # Try latest version V5+ of report
        args.report = next(
            (p for p in sorted((REPO_ROOT / zone / "output").glob("*_REPORT_V*.md"), reverse=True)),
            REPO_ROOT / zone / "output" / f"{zone.upper()}_REPORT_V5.md"
        )
    if args.output is None:
        # Output name matches highest input version
        version_match = __import__("re").search(r"_REPORT_V(\d+)", args.report.name)
        output_name = f"{zone.upper()}_REPORT_V{version_match.group(1)}" if version_match else f"{zone.upper()}_REPORT_V5"
        args.output = REPO_ROOT / zone / "output" / f"{output_name}.html"

    print(f"Reading V5 report: {args.report.name}")
    report_md = args.report.read_text(encoding="utf-8")

    print("Building SVG figures (shared engine)...")
    figures = build_figures(zone=zone, report_path=args.report)

    print("Extracting CSS head from template...")
    template = args.template.read_text(encoding="utf-8")
    head_match = re.search(r"<head>.*?</head>", template, re.DOTALL)
    head_html = head_match.group(0) if head_match else "<head><meta charset='utf-8'></head>"

    # V5-specific supplementary styles (sub-section headers + inline notes).
    # Injected here rather than in the shared template.html (used by V4).
    v5_style = '''<style>
  .sub-h{font-family:"Source Sans 3",sans-serif;font-weight:700;font-size:18px;
    color:var(--ink);margin:26px 0 10px;padding-bottom:4px;border-bottom:1px solid var(--rule-light)}
  h4.sub-h{font-size:15.5px;font-weight:600;border-bottom:none;margin:18px 0 6px;color:var(--ink-2)}
  blockquote.note{border-right:3px solid var(--rule);background:var(--paper-2,#f7f6f3);
    padding:12px 16px;margin:16px 0;color:var(--ink-2);font-size:14px;line-height:1.6}
  section p{line-height:1.75;margin:12px 0;text-align:justify;text-justify:inter-word}
</style>'''
    head_html = head_html.replace("</head>", f"{v5_style}\n</head>")

    # Split report into sections by "## " (level-2 headers).
    # The title line "# ..." and the "## גרסה V5" sub-header are handled as masthead.
    lines = report_md.split("\n")
    title_line = next((l for l in lines if l.startswith("# ")), "# דוח איכות מי תהום — אזה\"ת חולון")
    report_title = title_line.lstrip("# ").strip()

    # Find the intro blockquote (masthead sub) — first "> " block
    intro_match = re.search(r"^>\s*(.+?)(?=\n\s*\n)", report_md, re.MULTILINE | re.DOTALL)
    masthead_intro = ""
    if intro_match:
        masthead_intro = re.sub(r"\s*\n\s*", " ", intro_match.group(1)).strip()

    # Sections: everything starting with "## " — but skip the version sub-header
    section_blocks = re.split(r"\n(?=## )", report_md)
    rendered_sections = []
    for block in section_blocks:
        bstripped = block.strip()
        if not bstripped.startswith("## "):
            continue
        header = bstripped.split("\n", 1)[0]
        if "גרסה V5" in header:
            continue  # version sub-header → masthead meta
        rendered_sections.append(render_section(bstripped, figures))

    # Extract metadata from report (dynamic)
    boreholes_count = len(classification) if not classification.empty else "?"
    measurements_count = len(measurements) if not measurements.empty else "?"
    families_count = len(measurements["family"].unique()) if not measurements.empty else "?"

    masthead = f'''<header class="masthead">
  <div class="top">
    <span>{zone.upper()} / ZONE REPORT V5</span>
    <span>גרסה מעוצבת · {datetime.now().strftime("%Y-%m-%d %H:%M")}</span>
  </div>
  <h1>{md_inline_to_html(report_title)}</h1>
  <p class="sub">{md_utils.wrap_bidi(md_inline_to_html(masthead_intro))}</p>
  <div class="meta">
    <span><b>{boreholes_count}</b> קידוחים</span>
    <span><b>{measurements_count:,}</b> מדידות</span>
    <span><b>2010–2026</b> טווח</span>
    <span><b>{families_count}</b> משפחות מזהמים</span>
  </div>
</header>'''

    body = "\n\n".join(rendered_sections)

    html = f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
{head_html}
<body>
<div class="doc">
{masthead}
{body}
</div>
</body>
</html>'''

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"Wrote {args.output} ({len(html):,} bytes, {len(rendered_sections)} sections)")


if __name__ == "__main__":
    main()
