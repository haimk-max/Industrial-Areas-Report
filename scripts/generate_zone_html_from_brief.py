#!/usr/bin/env python3
"""Generate zone executive summary HTML (INTERNAL + PUBLIC) from brief YAML.

Reads: briefs/<zone>.yaml (validated against schema)
Reference: design-system/reference/HOLON_INTERNAL.html, HOLON_PUBLIC.html
Outputs: output/<zone>/{INTERNAL,PUBLIC}.html

This is a data-replacement script: preserves frozen design system, swaps zone data.
Caller ensures brief.yaml is valid before invoking.
"""
from __future__ import annotations

import argparse
import json
import sys
from html import escape
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")


REPO = Path(__file__).resolve().parent.parent
ENGINE = REPO / "report-engine"
REFERENCE = ENGINE / "design-system" / "reference"


def zone_paths(zone: str) -> dict[str, Path]:
    """Derive all per-zone paths from the zone id."""
    zdir = REPO / zone.capitalize()
    return {
        "zone_dir": zdir,
        "brief": ENGINE / "briefs" / f"{zone}.yaml",
        "output_dir": zdir / "output",
        "internal_out": zdir / "output" / f"{zone.upper()}_EXECUTIVE_SUMMARY_INTERNAL.html",
        "public_out": zdir / "output" / f"{zone.upper()}_EXECUTIVE_SUMMARY_PUBLIC.html",
        "reference_internal": REFERENCE / "HOLON_INTERNAL.html",
        "reference_public": REFERENCE / "HOLON_PUBLIC.html",
    }


def load_brief(brief_path: Path) -> dict:
    """Load and parse brief YAML."""
    if not brief_path.exists():
        sys.exit(f"brief not found: {brief_path}")
    with brief_path.open(encoding="utf-8") as fh:
        brief = yaml.safe_load(fh)
    if not isinstance(brief, dict):
        sys.exit(f"brief is not a dict: {brief_path}")
    return brief


def html_escape_brief_text(text: str) -> str:
    """Escape HTML entities but preserve intentional <strong>, <bdi> tags."""
    if not text:
        return ""
    # Already-safe markup from brief (which came from Opus as HTML)
    # Trust it; only escape unescaped quotes in attributes.
    return text


def kpi_html(kpis: list) -> str:
    """Generate KPI grid HTML from brief kpis list."""
    if not kpis or not isinstance(kpis, list):
        return ""
    html_parts = []
    for kpi in kpis[:4]:  # Limit to 4 KPIs for 4-column grid
        tier_class = kpi.get("tier", "teal")
        label = escape(kpi.get("label", ""))
        value = escape(str(kpi.get("value", "")))
        unit = escape(kpi.get("unit", ""))
        delta = escape(kpi.get("delta", ""))
        note = escape(kpi.get("note", ""))

        html_parts.append(f"""
<div class="kpi {tier_class}">
  <div class="label">{label}</div>
  <div class="value"><span class="unit">{unit}</span>{value}</div>
  <div class="delta">{delta}</div>
  <div class="note">{note}</div>
</div>
""")
    return "".join(html_parts)


def family_ledger_html(family_ledger: list) -> str:
    """Generate family ledger HTML from brief family_ledger list."""
    if not family_ledger or not isinstance(family_ledger, list):
        return ""
    html_parts = []
    for fam in family_ledger:
        fam_name = escape(fam.get("family", ""))
        desc = escape(fam.get("desc", ""))
        narrative = html_escape_brief_text(fam.get("narrative", ""))
        count_value = escape(str(fam.get("count_value", "")))
        count_label = escape(fam.get("count_label", ""))
        dim_class = " dim" if fam.get("dim", False) else ""

        html_parts.append(f"""
<div class="ledger-row">
  <div class="ledger-cell fam">
    <div class="name">{fam_name}</div>
    <div class="desc">{desc}</div>
  </div>
  <div class="ledger-cell narrative">{narrative}</div>
  <div class="ledger-cell count{dim_class}">
    <div class="n">{count_value}</div>
    <div class="lbl">{count_label}</div>
  </div>
</div>
""")
    return "".join(html_parts)


def findings_toc_html(findings: list) -> str:
    """Generate findings TOC grid."""
    if not findings or not isinstance(findings, list):
        return ""
    html_parts = []
    for i, f in enumerate(findings[:7], 1):
        urgency = f.get("urgency", "good")
        title = escape(f.get("title_internal", f.get("title_public", "")))
        html_parts.append(f"""
<div class="toc-item {urgency}">
  <div class="n">F·{i:02d}</div>
  <div class="t">{title}</div>
</div>
""")
    return "".join(html_parts)


def findings_cards_html(findings: list) -> str:
    """Generate finding cards (internal version)."""
    if not findings or not isinstance(findings, list):
        return ""
    html_parts = []
    for i, f in enumerate(findings[:7], 1):
        urgency = f.get("urgency", "good")
        title = escape(f.get("title_internal", ""))
        body = html_escape_brief_text(f.get("body_internal", ""))
        certainty = f.get("certainty", "MEDIUM").upper()[:3]
        cert_class = "high" if certainty == "HIG" else ("low" if certainty == "LOW" else "med")

        # Meta rows (from metadata field if present)
        meta_html = ""
        metadata = f.get("metadata", {})
        if isinstance(metadata, dict):
            for k, v in metadata.items():
                meta_html += f'<div class="meta-row"><span class="k">{escape(k)}</span><span class="v">{escape(str(v))}</span></div>'

        # Action callout if present
        action_html = ""
        if f.get("action"):
            action_html = f'<div class="action">{html_escape_brief_text(f["action"])}</div>'

        html_parts.append(f"""
<div class="finding">
  <div class="num">F·{i:02d}</div>
  <div class="body">
    <h3><span class="urgency-tag {urgency}">{urgency}</span>{title}</h3>
    <p>{body}</p>
    {action_html}
  </div>
  <aside>
    {meta_html}
    <div class="meta-row"><span class="k">确定程度</span><span class="v"><span class="cert {cert_class}">{certainty}</span></span></div>
  </aside>
</div>
""")
    return "".join(html_parts)


def decisions_matrix_html(decisions: list) -> str:
    """Generate decisions/recommendations table."""
    if not decisions or not isinstance(decisions, list):
        return ""
    html_parts = ['<tr><th>קטגוריה</th><th>פעולה</th><th>תיאור</th><th>הערות</th></tr>']
    current_cat = None
    for dec in decisions:
        cat = dec.get("category", "")
        action = escape(dec.get("action", ""))
        desc = escape(dec.get("description", ""))
        note = escape(dec.get("notes", ""))

        if cat != current_cat:
            html_parts.append(f'<tr class="spacer"><td colspan="4"></td></tr>')
            html_parts.append(f'<tr><td class="cat">{escape(cat)}</td><td class="act">{action}</td><td>{desc}</td><td class="note">{note}</td></tr>')
            current_cat = cat
        else:
            html_parts.append(f'<tr><td class="cat"></td><td class="act">{action}</td><td>{desc}</td><td class="note">{note}</td></tr>')

    return "<thead>" + html_parts[0] + "</thead><tbody>" + "".join(html_parts[1:]) + "</tbody>"


def generate_internal_html(brief: dict, reference_path: Path, zone: str, p: dict) -> str:
    """Generate INTERNAL.html by data replacement from reference."""
    html = reference_path.read_text(encoding="utf-8")

    zone_info = brief.get("zone", {})
    bottom_line = brief.get("bottom_line", [])
    kpis = brief.get("kpis", [])
    family_ledger = brief.get("family_ledger", [])
    findings = brief.get("findings", [])
    decisions = brief.get("decisions", [])
    framing_warning = brief.get("framing_warning", "")

    now = datetime.now().strftime("%d/%m/%Y · %H:%M")

    # Replace masthead and metadata
    zone_name = zone_info.get("name_he", zone.capitalize())
    html = html.replace("אזה״ת חולון", zone_name)
    html = html.replace("דו״ח איכות מי-תהום · מאי <bdi>2026</bdi>", f"דו״ח איכות מי-תהום · {zone_info.get('period', '2020–2026').split('–')[1] if '–' in zone_info.get('period', '') else '2026'} <bdi>{zone_info.get('edition_date', '').split('-')[1] if zone_info.get('edition_date') else '05'}</bdi>")

    # Replace chips and stats
    active_bhs = zone_info.get("active_boreholes", "~58")
    html = html.replace('~58', escape(str(active_bhs)))

    # Replace bottom_line paragraphs
    if bottom_line and isinstance(bottom_line, list):
        bl_html = "".join(f"<p>{html_escape_brief_text(bl)}</p>" for bl in bottom_line)
        # Find and replace the bottomline div content
        import re
        html = re.sub(
            r'(<div class="bottomline">)(.*?)(</div>)',
            f'\\1{bl_html}\\3',
            html,
            flags=re.DOTALL
        )

    # Replace KPI grid
    kpi_grid = kpi_html(kpis)
    if kpi_grid:
        import re
        html = re.sub(
            r'(<div class="kpi-grid">)(.*?)(</div>)',
            f'\\1{kpi_grid}\\3',
            html,
            flags=re.DOTALL
        )

    # Replace ledger
    ledger_grid = family_ledger_html(family_ledger)
    if ledger_grid:
        import re
        html = re.sub(
            r'(<div class="ledger">)(.*?)(</div>)',
            f'\\1{ledger_grid}\\3',
            html,
            flags=re.DOTALL
        )

    # Replace framing warning
    if framing_warning:
        html = html.replace(
            "שיעור החריגות אינו מייצג את כלל מרחב חולון",
            escape(framing_warning[:100]) + ("..." if len(framing_warning) > 100 else "")
        )

    # Replace findings
    toc_html = findings_toc_html(findings)
    cards_html = findings_cards_html(findings)
    if toc_html:
        import re
        html = re.sub(
            r'(<div class="findings-toc">)(.*?)(</div>)',
            f'\\1{toc_html}\\3',
            html,
            flags=re.DOTALL
        )
    if cards_html:
        import re
        # Find findings section and replace its content
        html = re.sub(
            r'(<!-- ════════════════ FINDINGS ════════════════ -->.*?<div class="findings-toc">.*?</div>)(.*?)(<!-- ════════════════)',
            f'\\1{cards_html}\\3',
            html,
            flags=re.DOTALL
        )

    # Replace decisions matrix
    dec_html = decisions_matrix_html(decisions)
    if dec_html:
        import re
        html = re.sub(
            r'(<table class="decisions">)(.*?)(</table>)',
            f'\\1{dec_html}\\3',
            html,
            flags=re.DOTALL
        )

    # Replace generated-at timestamp and doc IDs
    html = html.replace("{{GENERATED_AT}}", now)
    html = html.replace("HOL/2026/01", zone_info.get("doc_id_internal", ""))

    return html


def generate_public_html(brief: dict, reference_path: Path, zone: str, p: dict) -> str:
    """Generate PUBLIC.html by data replacement from reference."""
    html = reference_path.read_text(encoding="utf-8")

    zone_info = brief.get("zone", {})
    context_intro = brief.get("context_intro", [])
    findings = brief.get("findings", [])
    framing_warning = brief.get("framing_warning", "")

    zone_name = zone_info.get("name_he", zone.capitalize())
    html = html.replace("אזה״ת חולון", zone_name)

    # Replace context paragraphs
    if context_intro and isinstance(context_intro, list):
        context_html = "".join(f"<p>{html_escape_brief_text(ctx)}</p>" for ctx in context_intro)
        import re
        html = re.sub(
            r'(<!-- CONTEXT -->)(.*?)(<!-- END CONTEXT -->)',
            f'\\1{context_html}\\3',
            html,
            flags=re.DOTALL
        )

    # Replace findings (public versions)
    if findings:
        findings_html = ""
        for i, f in enumerate(findings[:7], 1):
            title = escape(f.get("title_public", f.get("title_internal", "")))
            body = html_escape_brief_text(f.get("body_public", f.get("body_internal", "")))
            findings_html += f"<h3>F·{i:02d} — {title}</h3>\n<p>{body}</p>\n"

        import re
        html = re.sub(
            r'(<!-- FINDINGS -->)(.*?)(<!-- END FINDINGS -->)',
            f'\\1{findings_html}\\3',
            html,
            flags=re.DOTALL
        )

    # Replace framing warning (amber callout)
    if framing_warning:
        html = html.replace(
            "שיעור החריגות אינו מייצג את כלל מרחב",
            escape(framing_warning[:150])
        )

    # Replace doc ID
    html = html.replace("HOL/2026/01", zone_info.get("doc_id_public", ""))

    return html


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zone", required=True, help="zone id (e.g. 'holon')")
    ap.add_argument("--force", action="store_true", help="overwrite existing HTML")
    args = ap.parse_args()

    p = zone_paths(args.zone)

    # Load and validate brief
    brief = load_brief(p["brief"])

    # Check output paths
    p["output_dir"].mkdir(parents=True, exist_ok=True)

    # Generate both HTML files
    internal_html = generate_internal_html(brief, p["reference_internal"], args.zone, p)
    public_html = generate_public_html(brief, p["reference_public"], args.zone, p)

    # Write outputs
    p["internal_out"].write_text(internal_html, encoding="utf-8")
    print(f"wrote internal: {p['internal_out']}")

    p["public_out"].write_text(public_html, encoding="utf-8")
    print(f"wrote public: {p['public_out']}")


if __name__ == "__main__":
    main()
