"""Generate the FULL Holon V4 report as standalone HTML (all 10 sections).

Converts HOLON_REPORT_V4.md → HOLON_REPORT_V4.html with:
  - Full markdown → HTML conversion (H1-H4, tables, lists, paragraphs, code, bold)
  - Inline SVG charts for figures 2-6 (replacing PNG references)
  - PNG kept only for figure 1 (zone site map, static)
  - Sticky sidebar TOC generated from H2 headers
  - RTL handling with md_utils.wrap_bidi() for mixed Hebrew/English content
  - Same visual style as DESIGNED.html (academic monochrome)

Writes:
  Holon/output/HOLON_REPORT_V4.html (replaces markdown as primary delivery)

Usage:
  python scripts/generate_holon_full_html.py
  python scripts/generate_holon_full_html.py --output some/other/path.html
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


def _slugify(text: str) -> str:
    """Create URL-safe anchor from Hebrew/English heading."""
    text = re.sub(r"[^\w֐-׿\s\-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text


def _render_table(lines: list, start: int) -> tuple[str, int]:
    """Parse a markdown table starting at lines[start]. Returns (html, lines_consumed)."""
    header_cells = [c.strip() for c in lines[start].strip().strip("|").split("|")]
    parts = ['<table class="data-table">', "<thead><tr>"]
    for c in header_cells:
        parts.append(f"<th>{md_utils.inline(c)}</th>")
    parts.append("</tr></thead><tbody>")
    i = start + 2
    while i < len(lines) and lines[i].strip().startswith("|"):
        row_cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        parts.append("<tr>")
        for c in row_cells:
            parts.append(f"<td>{md_utils.inline(c)}</td>")
        parts.append("</tr>")
        i += 1
    parts.append("</tbody></table>")
    return "".join(parts), i - start


_FIGURE_CAPTION_RE = re.compile(r"^\*\*איור (\d+)\*\*:", re.MULTILINE)


def _inject_missing_figure_images(md: str, figure_svgs: dict) -> str:
    """Safety net: insert `![alt](path)` before any '**איור N**:' caption that lacks one.

    Failure mode this addresses: Opus writes the caption but omits the image markdown
    (observed for fig_02 in Holon V4.2). PROCESS_GUIDE §VII validation would catch
    this, but rather than fail the render we auto-recover from figure_svgs.

    Mapping: 'איור N' → figure_svgs key with substring 'fig_0N_'. Caption text is
    used as alt. Inserted line points to the canonical PNG path so legacy/static
    fallbacks also work; the inline-SVG resolver in _render_image matches the key.
    """
    keys_by_num = {}
    for key in figure_svgs:
        m = re.match(r"fig_(\d+)_", key)
        if m:
            keys_by_num[int(m.group(1))] = key

    new_lines = []
    lines = md.split("\n")
    for i, line in enumerate(lines):
        cap_match = _FIGURE_CAPTION_RE.match(line)
        if cap_match:
            fig_num = int(cap_match.group(1))
            # Scan back ≤6 non-blank lines for an existing ![ for this fig
            has_image = False
            for j in range(i - 1, max(-1, i - 7), -1):
                if not lines[j].strip():
                    continue
                if "![" in lines[j] and f"fig_{fig_num:02d}_" in lines[j]:
                    has_image = True
                    break
                if lines[j].startswith("**איור ") or lines[j].startswith("## ") or lines[j].startswith("### "):
                    break
            if not has_image and fig_num in keys_by_num:
                key = keys_by_num[fig_num]
                alt = cap_match.group(0).rstrip(":")
                new_lines.append(f"![{alt}](../charts_v2/designed/{key}.png)")
                new_lines.append("")
        new_lines.append(line)
    return "\n".join(new_lines)


def _render_image(alt: str, src: str, figure_svgs: dict) -> str:
    """Render image: replace SVG figures inline, keep PNG (static) figures as <img>.

    figure_svgs: dict mapping path-fragment → SVG string.

    Note: Figure numbering relies on the '**איור N**:' caption that follows the
    image in V4.md (rendered as a regular paragraph). We do NOT emit a separate
    'איור N' header to avoid mismatched numbering when V4.md has gaps/offsets.
    """

    # Check if this image should be replaced with inline SVG
    for key, svg_html in figure_svgs.items():
        if key in src:
            return (f'<figure class="full-figure">'
                    f'<div class="frame">{svg_html}</div>'
                    f'<figcaption>{md_utils.wrap_bidi(md_utils.inline(alt))}</figcaption></figure>')

    # Default: render as PNG image (zone site map etc.)
    return (f'<figure class="full-figure">'
            f'<div class="frame"><img src="{src}" alt="{alt}" style="width:100%;display:block"/></div>'
            f'<figcaption>{md_utils.wrap_bidi(md_utils.inline(alt))}</figcaption></figure>')


def render_markdown(md: str, figure_svgs: dict) -> tuple[str, list]:
    """Render full V4.md to HTML. Returns (html, toc_entries).

    toc_entries: list of {level, text, id} dicts for TOC generation.
    """
    lines = md.split("\n")
    html_parts = []
    toc = []
    in_list = False
    list_type = None
    i = 0

    def close_list():
        nonlocal in_list, list_type
        if in_list:
            html_parts.append(f"</{list_type}>")
            in_list = False
            list_type = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Horizontal rule
        if stripped == "---":
            close_list()
            html_parts.append('<hr class="sec-divider">')
            i += 1
            continue

        # Image: ![alt](path)
        img_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", stripped)
        if img_match:
            close_list()
            alt, src = img_match.group(1), img_match.group(2)
            html_parts.append(_render_image(alt, src, figure_svgs))
            i += 1
            continue

        # Heading: # / ## / ### / ####
        h_match = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if h_match:
            close_list()
            level = len(h_match.group(1))
            text = h_match.group(2).strip()
            anchor = _slugify(text)
            # Skip H1 (rendered from masthead) and version metadata H2
            if level == 1:
                i += 1
                continue
            if level == 2 and text.startswith("גרסה"):
                # Version line — metadata, not a section; skip entirely
                i += 1
                continue
            html_parts.append(f'<h{level} id="{anchor}">{md_utils.wrap_bidi(md_utils.inline(text))}</h{level}>')
            if level == 2:
                toc.append({"level": level, "text": text, "id": anchor})
            i += 1
            continue

        # Markdown table: header line + separator line (|---|---|)
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|\s*$", lines[i + 1].strip()):
            close_list()
            table_html, consumed = _render_table(lines, i)
            html_parts.append(md_utils.wrap_bidi(table_html))
            i += consumed
            continue

        # Ordered list (1. text)
        m_ol = re.match(r"^(\d+)\.\s+(.+)", stripped)
        # Unordered list (- text)
        m_ul = re.match(r"^[-*]\s+(.+)", stripped)

        if m_ol:
            num = int(m_ol.group(1))
            if not in_list or list_type != "ol":
                close_list()
                html_parts.append("<ol>")
                in_list = True
                list_type = "ol"
            html_parts.append(f'<li value="{num}">{md_utils.wrap_bidi(md_utils.inline(m_ol.group(2)))}</li>')
            i += 1
            continue
        if m_ul:
            if not in_list or list_type != "ul":
                close_list()
                html_parts.append("<ul>")
                in_list = True
                list_type = "ul"
            html_parts.append(f"<li>{md_utils.wrap_bidi(md_utils.inline(m_ul.group(1)))}</li>")
            i += 1
            continue

        # Blank line — close list, add paragraph break
        if stripped == "":
            close_list()
            i += 1
            continue

        # Default: paragraph
        if in_list:
            # Continuation inside list item — append as <br>
            html_parts.append(f"<br>{md_utils.wrap_bidi(md_utils.inline(stripped))}")
        else:
            html_parts.append(f"<p>{md_utils.wrap_bidi(md_utils.inline(stripped))}</p>")
        i += 1

    close_list()
    return "\n".join(html_parts), toc


# ─────────────────────── HTML template ───────────────────────

TEMPLATE = """<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<title>{TITLE}</title>
<link href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@400;500;700;900&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
<style>
  :root{{
    --paper:#fdfcf9;
    --ink:#1a1a1a;
    --ink-2:#3a3a3a;
    --soft:#6b6b6b;
    --rule:#1a1a1a;
    --rule-light:#cfcfcf;
    --rule-faint:#e6e3dd;
    --red:#a82a1c;
    --red-soft:#d99a93;
    --grey-1:#f0ede6;
    --grey-2:#d8d3c8;
    --grey-3:#a8a29a;
    --grey-4:#5a564f;
  }}
  *{{box-sizing:border-box}}
  html,body{{margin:0;background:var(--paper);color:var(--ink);font-family:"Frank Ruhl Libre","Times New Roman",serif;-webkit-font-smoothing:antialiased;font-feature-settings:"kern","liga","tnum"}}
  body{{padding:0 0 80px;font-size:15px;line-height:1.65}}

  /* Bidi handling */
  bdi{{unicode-bidi:isolate}}
  p,li,td,th,h1,h2,h3,h4,figcaption{{unicode-bidi:isolate}}

  /* Layout: single centered column */
  .layout{{max-width:880px;margin:0 auto;padding:0 32px}}
  @media (max-width:980px){{.layout{{padding:0 20px}}}}

  /* Main column */
  .doc{{padding:48px 0 0;min-width:0}}

  /* Masthead */
  .masthead{{border-bottom:2px solid var(--ink);padding-bottom:22px;margin-bottom:36px}}
  .masthead .top{{display:flex;justify-content:space-between;align-items:baseline;font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--soft);padding-bottom:14px;border-bottom:1px solid var(--rule-light)}}
  .masthead h1{{font-weight:900;font-size:34px;line-height:1.18;margin:18px 0 8px;letter-spacing:-0.005em}}
  .masthead .sub{{font-size:15.5px;color:var(--ink-2);font-weight:400;line-height:1.55;margin-bottom:14px}}
  .masthead .meta{{display:flex;flex-wrap:wrap;gap:24px;font-family:"Source Sans 3",sans-serif;font-size:12.5px;color:var(--soft);padding-top:14px;border-top:1px solid var(--rule-light)}}
  .masthead .meta b{{color:var(--ink);font-weight:600}}

  /* Headings */
  h2{{font-weight:800;font-size:24px;letter-spacing:-0.005em;margin:48px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--ink);scroll-margin-top:20px}}
  h3{{font-weight:700;font-size:17px;margin:28px 0 10px;color:var(--ink);scroll-margin-top:20px}}
  h4{{font-weight:600;font-size:14.5px;margin:18px 0 8px;color:var(--ink-2);font-family:"Source Sans 3",sans-serif;letter-spacing:.02em}}

  /* Paragraphs */
  p{{line-height:1.7;color:var(--ink-2);margin:0 0 12px;text-align:justify;text-justify:inter-word}}
  strong{{color:var(--ink);font-weight:700}}
  code{{font-family:"IBM Plex Mono",monospace;font-size:13px;background:var(--grey-1);padding:1px 5px;border-radius:2px;color:var(--ink)}}

  /* Lists */
  ol,ul{{margin:8px 0 16px;padding-inline-start:24px;line-height:1.7;color:var(--ink-2)}}
  ol li,ul li{{margin-bottom:6px}}
  ol{{counter-reset:none}}

  /* Tables */
  table.data-table{{width:100%;border-collapse:collapse;font-size:13px;font-family:"Frank Ruhl Libre","Times New Roman",serif;margin:18px 0 22px;background:var(--paper)}}
  table.data-table thead th{{border-top:1.5px solid var(--ink);border-bottom:1px solid var(--ink);font-family:"Source Sans 3",sans-serif;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--soft);font-weight:600;padding:9px 10px 8px;text-align:right;background:var(--grey-1)}}
  table.data-table tbody td{{padding:9px 10px;text-align:right;border-bottom:1px solid var(--rule-faint);vertical-align:top;line-height:1.5;color:var(--ink-2)}}
  table.data-table tbody tr:nth-child(even) td{{background:rgba(240,237,230,.4)}}
  table.data-table tbody tr:hover td{{background:var(--grey-1)}}
  table.data-table tbody tr:last-child td{{border-bottom:1.5px solid var(--ink)}}
  table.data-table strong{{color:var(--ink);font-weight:700}}
  table.data-table td:first-child{{font-weight:600;color:var(--ink);font-family:"Source Sans 3",sans-serif;font-size:12.5px;white-space:nowrap}}

  /* Figures */
  figure.full-figure{{margin:32px 0;padding:0}}
  figure.full-figure .fig-h{{display:flex;justify-content:space-between;font-family:"Source Sans 3",sans-serif;font-size:11.5px;color:var(--soft);text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--rule-faint)}}
  figure.full-figure .fig-h .ttl{{color:var(--ink);font-weight:700}}
  figure.full-figure .fig-h .fig-meta{{color:var(--soft);text-transform:none;letter-spacing:0;max-width:65%;text-align:left}}
  figure.full-figure .frame{{border:1px solid var(--ink);background:var(--paper);padding:24px 22px 18px;overflow-x:auto}}
  figure.full-figure figcaption{{margin-top:10px;font-size:12.5px;color:var(--soft);line-height:1.5;padding-top:6px;border-top:1px solid var(--rule-faint);font-style:italic}}

  /* --- Severity matrix (fig_02) --- */
  table.matrix{{width:100%;border-collapse:collapse;font-size:12.5px;font-family:"IBM Plex Mono",monospace}}
  table.matrix th, table.matrix td{{padding:7px 10px;text-align:right;border-bottom:1px solid var(--rule-faint)}}
  table.matrix thead th{{border-bottom:1px solid var(--ink);font-family:"Source Sans 3",sans-serif;font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--soft);font-weight:600;padding-bottom:6px;text-align:center}}
  table.matrix thead th:first-child{{text-align:right}}
  table.matrix td.lbl{{font-family:"Source Sans 3",sans-serif;font-weight:500;font-size:12.5px;line-height:1.35}}
  table.matrix td.lbl small{{display:block;font-family:"IBM Plex Mono",monospace;font-size:10.5px;color:var(--soft);font-weight:400;margin-top:2px;letter-spacing:.01em}}
  table.matrix td.val{{text-align:center;font-feature-settings:"tnum";color:var(--ink);white-space:nowrap}}
  table.matrix td.val .b{{display:inline-block;min-width:22px;height:20px;line-height:18px;padding:0 4px;text-align:center;font-size:11.5px;font-weight:700;border:1px solid var(--ink);vertical-align:middle;font-family:"IBM Plex Mono",monospace}}
  table.matrix td.val.empty{{color:var(--rule-light)}}
  table.matrix tbody tr:hover td{{background:rgba(240,237,230,.4)}}

  /* --- Ledger (fig_01 severity ledger) --- */
  .ledger{{border-top:2px solid var(--ink);border-bottom:2px solid var(--ink)}}
  .ledger .row{{display:grid;grid-template-columns:200px 1fr 140px;gap:24px;padding:18px 0;border-bottom:1px solid var(--rule-light);align-items:start}}
  .ledger .row:last-child{{border-bottom:none}}
  .ledger .row.appendix{{background:#f4f1ea;padding:14px 18px;margin:0 -18px -1px;border-bottom:none;color:var(--ink-2)}}
  .ledger .fam{{font-weight:700;font-size:15px;line-height:1.3}}
  .ledger .fam small{{display:block;font-weight:400;font-size:11.5px;color:var(--soft);margin-top:4px;line-height:1.4}}
  .ledger .row.appendix .fam{{font-weight:600;font-size:13px;color:var(--ink-2)}}
  .ledger .row.appendix .fam small{{font-size:11px}}
  .ledger .body{{font-size:13px;line-height:1.55;color:var(--ink-2)}}
  .ledger .body b{{color:var(--ink);font-weight:600}}
  .ledger .row.appendix .body{{font-size:12px;color:#6b6b6b}}
  .ledger .metric{{text-align:left;font-family:"IBM Plex Mono",monospace}}
  .ledger .metric .big{{font-size:28px;font-weight:500;line-height:1;color:var(--red);display:block}}
  .ledger .metric .ratio{{font-size:12px;color:var(--soft);margin-top:4px;display:block;letter-spacing:.02em}}
  .ledger .row.appendix .metric .big{{font-size:16px;color:var(--ink-2);font-weight:500}}
  .ledger .row.appendix .metric .ratio{{font-size:10.5px}}

  /* --- Gap timeline (fig_06) --- */
  .gap-grid{{display:grid;grid-template-columns:170px 1fr 80px;gap:10px 14px;font-size:12.5px;align-items:center}}
  .gap-grid .hd{{font-family:"Source Sans 3",sans-serif;font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--soft);padding-bottom:6px;border-bottom:1px solid var(--ink);margin-bottom:4px;font-weight:600}}
  .gap-grid .nm{{font-weight:500;line-height:1.35}}
  .gap-grid .nm small{{display:block;font-family:"IBM Plex Mono",monospace;font-size:10.5px;color:var(--soft);font-weight:400;margin-top:2px}}
  .gap-grid .last{{font-family:"IBM Plex Mono",monospace;font-size:11.5px;text-align:left;color:var(--red)}}
  .gap-bar{{position:relative;height:14px;background:var(--paper);border-top:1px solid var(--rule-light);border-bottom:1px solid var(--rule-light)}}
  .gap-bar .a{{position:absolute;top:0;bottom:0;background:var(--ink-2)}}
  .gap-bar .m{{position:absolute;top:0;bottom:0;background:repeating-linear-gradient(90deg,var(--paper) 0 4px,var(--red-soft) 4px 5px)}}

  /* Horizontal section divider */
  hr.sec-divider{{border:none;border-top:1px solid var(--rule-light);margin:36px 0 0}}

  /* TOC at top of document */
  .toc-box{{margin:0 0 48px;padding:24px 28px;background:var(--grey-1);border-top:1.5px solid var(--ink);border-bottom:1.5px solid var(--ink);font-family:"Source Sans 3",sans-serif}}
  .toc-title{{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--soft);margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid var(--rule-light);font-weight:600}}
  .toc-box ol{{list-style:none;padding:0;margin:0;column-count:2;column-gap:32px;column-rule:1px solid var(--rule-light)}}
  @media (max-width:680px){{.toc-box ol{{column-count:1}}}}
  .toc-box li{{margin:0 0 8px;line-height:1.45;font-size:13.5px;break-inside:avoid}}
  .toc-box a{{color:var(--ink-2);text-decoration:none;display:block;padding:2px 0;border-bottom:1px dotted transparent;transition:all .15s}}
  .toc-box a:hover{{color:var(--red);border-bottom-color:var(--red)}}

  /* Print */
  @media print{{
    body{{font-size:11pt;padding:0}}
    .toc-box{{break-after:page}}
    .layout{{max-width:none;padding:0}}
    figure.full-figure{{break-inside:avoid}}
    h2{{break-after:avoid}}
  }}

  /* SVG defaults */
  svg{{display:block;max-width:100%;height:auto}}
</style>
</head>
<body>
<div class="layout">
  <main class="doc">
    <header class="masthead">
      <div class="top">
        <span>{ZONE_LABEL}</span>
        <span>{REPORT_VERSION}</span>
      </div>
      <h1>{TITLE}</h1>
      <p class="sub">{SUBTITLE}</p>
      <div class="meta">
        <span><b>נוצר:</b> {GENERATED_AT}</span>
        <span><b>מדידות:</b> {N_MEASUREMENTS}</span>
        <span><b>קידוחים פעילים:</b> {N_WELLS}</span>
        <span><b>חורגים מובהקים:</b> {N_ALERT}</span>
        <span><b>מגמות עולות מובהקות:</b> {N_INCREASING}</span>
      </div>
    </header>
    <nav class="toc-box">
      <div class="toc-title">תוכן עניינים</div>
      <ol>{TOC_ITEMS}</ol>
    </nav>
    {BODY}
  </main>
</div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate full Holon V4 HTML report")
    parser.add_argument("--output", type=Path,
                        default=REPO_ROOT / "Holon" / "output" / "HOLON_REPORT_V4.html")
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

    print("Building inline SVG figures ...")
    alert_borehole_ids = set(measurements['canonical_id'].unique())
    severity_alert = severity[severity['borehole'].isin(alert_borehole_ids)].copy()
    # PROCESS_GUIDE §VIII.1: Opus picks boreholes via V4.md; chart engine renders them per style guide.
    report_boreholes = dl.extract_report_boreholes(args.report_v4, severity)
    print(f"  V4.md boreholes_override: {len(report_boreholes)} mentioned")
    # Figures referenced in V4.md, in order.
    figure_svgs = {
        "fig_01_severity_ledger": sc.svg_severity_ledger(severity_alert),
        "fig_02_severity_matrix": sc.svg_severity_matrix(severity_alert, trends, data_avail),
        "fig_03_cvoc_panels": sc.svg_cvoc_panels(measurements, severity, boreholes_override=report_boreholes),
        "fig_04_chromium_panels": sc.svg_chromium_panels(measurements, boreholes_override=report_boreholes),
        "fig_05_btex_panels": sc.svg_btex_panels(measurements, boreholes_override=report_boreholes),
        "fig_06_monitoring_gaps": sc.svg_monitoring_gaps(data_avail, severity),
    }

    print(f"Reading {args.report_v4.name} ...")
    md = args.report_v4.read_text(encoding="utf-8")

    print("Rendering markdown → HTML ...")
    body_html, toc = render_markdown(md, figure_svgs)
    print(f"  {len(toc)} TOC entries (H2 sections)")

    toc_items = "\n".join(
        f'<li><a href="#{e["id"]}">{e["text"]}</a></li>' for e in toc
    )

    n_increasing = 0
    if not trends.empty:
        n_increasing = (trends.classification == "INCREASING").sum()

    html = TEMPLATE.format(
        TITLE="דוח ניטור איכות מי תהום — אזור התעשייה חולון",
        SUBTITLE="ניתוח מצב מי התהום באקוויפר החוף על בסיס 2,672 מדידות מ-80 קידוחי ניטור פעילים (2010–2026), משולב עם רקע היסטורי משלוש סדרות סקרים (תה\"ל 2007, אקולוג 2009–2017, רשות המים 2021).",
        ZONE_LABEL="HOLON · אזה\"ת חולון",
        REPORT_VERSION="V4.2 · MAY 2026",
        GENERATED_AT=datetime.now().strftime("%Y-%m-%d %H:%M"),
        N_MEASUREMENTS=f"{len(measurements):,}",
        N_WELLS="80",
        N_ALERT=str(len(alert) if not alert.empty else 25),
        N_INCREASING=str(int(n_increasing)),
        TOC_ITEMS=toc_items,
        BODY=body_html,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"Wrote {args.output} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
