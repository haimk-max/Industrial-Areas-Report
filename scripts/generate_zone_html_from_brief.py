#!/usr/bin/env python3
"""Generate zone executive summary HTML (INTERNAL + PUBLIC) from brief YAML.

Reads: report-engine/briefs/<zone>.yaml
Reference: report-engine/design-system/reference/HOLON_{INTERNAL,PUBLIC}.html (FROZEN)
Outputs: <Zone>/output/<ZONE>_EXECUTIVE_SUMMARY_{INTERNAL,PUBLIC}.html

This is a DATA-replacement script: it preserves the frozen design system
(every CSS rule, font link, Leaflet include, structural element) and swaps
ONLY the data-bearing inner HTML of each section, driven by the brief.

Field -> section mapping is authoritative in report-engine/CLAUDE.md section 5.

Because the reference uses nested <div>s, regex cannot balance them. We use a
depth-counting helper (`replace_container_inner`) that finds the matching
closing </div> for a container's opening tag and replaces the inner HTML.

Prose fields from the brief contain intentional inline HTML (<strong>, <bdi>,
<span class="...">) produced by Opus -- those are injected as-is. Only plain
scalar values (labels, numbers) are HTML-escaped.
"""
from __future__ import annotations

import argparse
import re
import sys
from html import escape
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")


REPO = Path(__file__).resolve().parent.parent
ENGINE = REPO / "report-engine"
REFERENCE = ENGINE / "design-system" / "reference"


# ─────────────────────────── paths / loading ───────────────────────────

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


# ─────────────────────────── html helpers ───────────────────────────

def raw(text) -> str:
    """Inject brief prose as-is (it already carries intentional inline HTML)."""
    if text is None:
        return ""
    return str(text).strip()


def bdi_if_latin(value: str) -> str:
    """Wrap a scalar in <bdi> only if it contains a Latin letter or digit.

    Pure-Hebrew values are left bare (matches the reference, which isolates only
    opposite-direction tokens). Value is HTML-escaped first.
    """
    v = esc(value)
    if not v:
        return ""
    if re.search(r"[A-Za-z0-9]", v):
        return f"<bdi>{v}</bdi>"
    return v


def esc(text) -> str:
    """Escape a plain scalar value (labels, numbers, codes)."""
    if text is None:
        return ""
    return escape(str(text))


def replace_container_inner(html: str, open_tag: str, inner: str) -> str:
    """Replace the inner HTML of a <div> container identified by `open_tag`.

    `open_tag` is the literal opening tag, e.g. '<div class="stats">'. The
    matching closing </div> is located by depth-counting nested <div>/<div ...>
    and </div> tokens, so nested containers are handled correctly (regex cannot
    balance these). Returns html unchanged (and warns) if the tag is not found.
    """
    start = html.find(open_tag)
    if start == -1:
        sys.stderr.write(f"warning: container not found, skipped: {open_tag}\n")
        return html
    inner_start = start + len(open_tag)

    # Depth scan from inner_start: every <div...> opens, every </div> closes.
    token = re.compile(r"<div\b|</div>")
    depth = 1
    pos = inner_start
    inner_end = None
    for m in token.finditer(html, inner_start):
        if m.group() == "</div>":
            depth -= 1
            if depth == 0:
                inner_end = m.start()
                break
        else:
            depth += 1
    if inner_end is None:
        sys.stderr.write(f"warning: no matching </div> for: {open_tag}\n")
        return html

    return html[:inner_start] + inner + html[inner_end:]


def replace_between(html: str, start_marker: str, end_marker: str, inner: str) -> str:
    """Replace content between two literal markers (e.g. banner comments)."""
    s = html.find(start_marker)
    if s == -1:
        sys.stderr.write(f"warning: start marker not found: {start_marker}\n")
        return html
    s_end = s + len(start_marker)
    e = html.find(end_marker, s_end)
    if e == -1:
        sys.stderr.write(f"warning: end marker not found: {end_marker}\n")
        return html
    return html[:s_end] + inner + html[e:]


# urgency: brief value -> (css class, hebrew label)
URGENCY_MAP = {
    "critical": ("crit", "קריטי"),
    "crit": ("crit", "קריטי"),
    "high": ("high", "גבוה"),
    "good": ("good", "חיובי"),
    "medium": ("med", "בינוני"),
}

# certainty: brief value -> badge text
CERT_MAP = {
    "high": ("high", "HIGH"),
    "medium": ("med", "MEDIUM"),
    "med": ("med", "MEDIUM"),
    "low": ("low", "LOW"),
}

# timeline layer -> (leader height px, card bottom px)
LAYER_GEOMETRY = {
    "A": (20, 10),
    "B": (120, 110),
    "C": (220, 210),
    "D": (320, 310),
}


# ─────────────────────────── INTERNAL builders ───────────────────────────

def build_bottomline(bottom_line: list) -> str:
    if not isinstance(bottom_line, list):
        return ""
    return "\n" + "\n".join(f"      <p>{raw(p)}</p>" for p in bottom_line) + "\n    "


def build_kpi_grid(kpis: list) -> str:
    if not isinstance(kpis, list):
        return ""
    parts = []
    for k in kpis[:4]:
        tier = esc(k.get("tier", "teal"))
        label = raw(k.get("label", ""))
        value = esc(k.get("value", ""))
        unit = k.get("unit")
        delta = raw(k.get("delta", ""))
        note = raw(k.get("note", ""))
        unit_html = f'<span class="unit">{esc(unit)}</span>' if unit else ""
        delta_cls = " up" if str(k.get("delta", "")).strip().startswith("▲") else ""
        parts.append(
            f'''      <div class="kpi {tier}">
        <div class="label">{label}</div>
        <div class="value"><bdi>{value}</bdi>{unit_html}</div>
        <div class="delta{delta_cls}">{delta}</div>
        <div class="note">{note}</div>
      </div>'''
        )
    return "\n" + "\n".join(parts) + "\n    "


def build_ledger(family_ledger: list) -> str:
    if not isinstance(family_ledger, list):
        return ""
    parts = []
    for fam in family_ledger:
        name = esc(fam.get("family", ""))
        desc = esc(fam.get("desc", ""))
        narrative = raw(fam.get("narrative", ""))
        cnt_v = esc(fam.get("count_value", ""))
        cnt_l = esc(fam.get("count_label", ""))
        dim = " dim" if fam.get("dim") else ""
        parts.append(
            f'''      <div class="ledger-row">
        <div class="ledger-cell fam">
          <span class="name">{name}</span>
          <span class="desc">{desc}</span>
        </div>
        <div class="ledger-cell narrative">
          {narrative}
        </div>
        <div class="ledger-cell count{dim}">
          <span class="n"><bdi>{cnt_v}</bdi></span>
          <span class="lbl">{cnt_l}</span>
        </div>
      </div>'''
        )
    return "\n" + "\n".join(parts) + "\n    "


def build_findings_toc(findings: list) -> str:
    if not isinstance(findings, list):
        return ""
    parts = []
    for i, f in enumerate(findings, 1):
        cls, _ = URGENCY_MAP.get(str(f.get("urgency", "good")).lower(), ("good", ""))
        title = raw(f.get("title_internal", f.get("title_public", "")))
        parts.append(
            f'      <div class="toc-item {cls}"><span class="n">F·{i:02d}</span>'
            f'<span class="t">{title}</span></div>'
        )
    return "\n" + "\n".join(parts) + "\n    "


def _meta_rows_internal(f: dict) -> str:
    """Build aside meta-rows from metadata[] + certainty."""
    rows = []
    metadata = f.get("metadata", [])
    if isinstance(metadata, list):
        for item in metadata:
            k = esc(item.get("k", ""))
            v = bdi_if_latin(item.get("v", ""))
            color = item.get("color")
            vcls = f" {esc(color)}" if color else ""
            rows.append(
                f'        <div class="meta-row"><span class="k">{k}</span>'
                f'<span class="v{vcls}">{v}</span></div>'
            )
    cert_cls, cert_txt = CERT_MAP.get(str(f.get("certainty", "medium")).lower(), ("med", "MEDIUM"))
    rows.append(
        f'        <div class="meta-row"><span class="k">ודאות מקור</span>'
        f'<span class="v"><span class="cert {cert_cls}">{cert_txt}</span></span></div>'
    )
    return "\n".join(rows)


def build_findings_cards_internal(findings: list) -> str:
    if not isinstance(findings, list):
        return ""
    cards = []
    for i, f in enumerate(findings, 1):
        cls, label = URGENCY_MAP.get(str(f.get("urgency", "good")).lower(), ("good", ""))
        title = raw(f.get("title_internal", ""))
        body = raw(f.get("body_internal", ""))
        action = raw(f.get("action_internal", f.get("action", "")))
        action_html = f'\n        <div class="action">{action}</div>' if action else ""
        meta = _meta_rows_internal(f)
        cards.append(
            f'''    <!-- F{i} -->
    <article class="finding">
      <div class="num">{i:02d}</div>
      <div class="body">
        <h3><span class="urgency-tag {cls}">{label}</span>{title}</h3>
        <p>{body}</p>{action_html}
      </div>
      <aside>
{meta}
      </aside>
    </article>'''
        )
    return "\n\n" + "\n\n".join(cards) + "\n  "


def build_decisions(decisions: list) -> str:
    """Build the decisions table inner HTML (thead + tbody).

    Brief shape: decisions[] = {category, actions[]} where each action is
    {action, need, notes}. Categories are grouped via rowspan on the first
    action's cell, separated by spacer rows.
    """
    if not isinstance(decisions, list):
        return ""
    head = (
        "\n      <thead>\n        <tr><th>קטגוריית פעילות</th><th>פעולה</th>"
        "<th>מה צריך</th><th>הערות</th></tr>\n      </thead>\n      <tbody>"
    )
    body_parts = []
    for ci, group in enumerate(decisions):
        cat = esc(group.get("category", ""))
        actions = group.get("actions", [])
        if not isinstance(actions, list) or not actions:
            continue
        if ci > 0:
            body_parts.append('        <tr class="spacer"><td colspan="4"></td></tr>')
        span = len(actions)
        for ai, act in enumerate(actions):
            action = raw(act.get("action", ""))
            need = raw(act.get("need", act.get("description", "")))
            notes = raw(act.get("notes", ""))
            note_html = notes.replace(" | ", "<br/>") if notes else ""
            if ai == 0:
                body_parts.append(
                    f'        <tr><td class="cat" rowspan="{span}">{cat}</td>\n'
                    f'            <td class="act">{action}</td>\n'
                    f'            <td>{need}</td>\n'
                    f'            <td class="note">{note_html}</td></tr>'
                )
            else:
                body_parts.append(
                    f'        <tr><td class="act">{action}</td>\n'
                    f'            <td>{need}</td>\n'
                    f'            <td class="note">{note_html}</td></tr>'
                )
    return head + "\n" + "\n".join(body_parts) + "\n      </tbody>\n    "


# ─────────────────────────── PUBLIC builders ───────────────────────────

def build_context_prose(context_intro: list) -> str:
    """First paragraph keeps the .drop drop-cap span on its first letter."""
    if not isinstance(context_intro, list) or not context_intro:
        return ""
    parts = []
    for idx, p in enumerate(context_intro):
        text = raw(p)
        if idx == 0 and text and not text.startswith("<"):
            text = f'<span class="drop">{text[0]}</span>{text[1:]}'
        parts.append(f"        <p>{text}</p>")
    return "\n" + "\n".join(parts) + "\n      "


def build_framing_card_body(framing_warning: str) -> str:
    return "\n          " + raw(framing_warning) + "\n        "


def build_stats_public(stats_public: list) -> str:
    if not isinstance(stats_public, list):
        return ""
    parts = []
    for s in stats_public:
        k = raw(s.get("k", ""))
        v = esc(s.get("v", ""))
        tier = esc(s.get("tier", "teal"))
        note = raw(s.get("note", ""))
        # Wrap numeric/code value in <bdi>; keep leading symbol (×) outside.
        if v.startswith("×"):
            v_html = "×<bdi>" + v[1:] + "</bdi>"
        else:
            v_html = f"<bdi>{v}</bdi>"
        parts.append(
            f'''      <div class="stat">
        <div class="k">{k}</div>
        <div class="v {tier}">{v_html}</div>
        <div class="note">{note}</div>
      </div>'''
        )
    return "\n" + "\n".join(parts) + "\n    "


def build_timeline(timeline: list) -> str:
    if not isinstance(timeline, list):
        return ""
    events = []
    for ev in timeline:
        etype = esc(ev.get("type", "hist"))
        period = raw(ev.get("period", ""))
        label = raw(ev.get("label", ""))
        text = raw(ev.get("text", ""))
        pos = esc(ev.get("position_pct", 0))
        layer = str(ev.get("layer", "B")).upper()
        leader_h, card_b = LAYER_GEOMETRY.get(layer, LAYER_GEOMETRY["B"])
        edge = ev.get("edge")
        edge_cls = ""
        if edge == "left":
            edge_cls = " edge-l"
        elif edge == "right":
            edge_cls = " edge-r"
        events.append(
            f'''      <div class="event {etype}{edge_cls}" style="left:{pos}%">
        <div class="dot"></div>
        <div class="leader" style="height:{leader_h}px"></div>
        <div class="card" style="bottom:{card_b}px">
          <div class="y">{period} · {label}</div>
          <div class="t">{text}</div>
        </div>
      </div>'''
        )
    return "\n\n" + "\n\n".join(events) + "\n\n        "


def build_findings_public(findings: list) -> str:
    if not isinstance(findings, list):
        return ""
    cards = []
    for i, f in enumerate(findings, 1):
        cls, label = URGENCY_MAP.get(str(f.get("urgency", "good")).lower(), ("good", ""))
        title = raw(f.get("title_public", f.get("title_internal", "")))
        desc = raw(f.get("body_public", f.get("body_internal", "")))
        means = raw(f.get("public_what_it_means", ""))
        do = raw(f.get("public_what_we_do", ""))

        stat = f.get("stat", {}) or {}
        stat_v = esc(stat.get("value", ""))
        stat_l = raw(stat.get("label", ""))
        stat_color = stat.get("color", "")
        vcls = f" {esc(stat_color)}" if stat_color and stat_color != "neutral" else ""
        # Split a leading symbol (×) out of the <bdi> wrapper for clean RTL.
        if stat_v.startswith("×"):
            stat_v_html = "×<bdi>" + stat_v[1:].strip() + "</bdi>"
        else:
            stat_v_html = f"<bdi>{stat_v}</bdi>"
        stat_l_html = stat_l.replace(" · ", "<br/>") if stat_l else ""

        cards.append(
            f'''      <!-- F{i} -->
      <article class="fp">
        <div class="lead">
          <span class="n">ממצא · <bdi>{i:02d}</bdi></span>
          <span class="badge {cls}">{label}</span>
        </div>
        <div>
          <div class="title">{title}</div>
          <div class="desc">{desc}</div>
          <div class="fp-stat">
            <span class="v{vcls}">{stat_v_html}</span>
            <span class="lbl">{stat_l_html}</span>
          </div>
        </div>
        <div class="panel">
          <div class="lbl">מה זה אומר</div>
          <div class="txt">{means}</div>
          <div class="lbl">מה אנחנו עושים</div>
          <div class="txt">{do}</div>
        </div>
      </article>'''
        )
    return "\n\n" + "\n\n".join(cards) + "\n\n    "


def build_means_grid(means_summary: list) -> str:
    if not isinstance(means_summary, list):
        return ""
    cards = []
    for m in means_summary:
        label = raw(m.get("label", ""))
        title = raw(m.get("title", ""))
        body = raw(m.get("body", ""))
        cards.append(
            f'''      <div class="means-card">
        <div class="num">{label}</div>
        <h3>{title}</h3>
        {body}
      </div>'''
        )
    return "\n\n" + "\n\n".join(cards) + "\n\n    "


def build_methodology(methodology: list) -> str:
    if not isinstance(methodology, list):
        return ""
    cells = []
    for i, m in enumerate(methodology, 1):
        title = raw(m.get("title", ""))
        body = raw(m.get("body", ""))
        cells.append(
            f'''      <div class="method-cell">
        <div class="num">{i:02d}</div>
        <h4>{title}</h4>
        <p>{body}</p>
      </div>'''
        )
    return "\n" + "\n".join(cells) + "\n    "


# ─────────────────────────── generators ───────────────────────────

def generate_internal_html(brief: dict, reference_path: Path) -> str:
    html = reference_path.read_text(encoding="utf-8")
    zone = brief.get("zone", {})

    # Scalars (keep simple string replacements where they already work).
    name = zone.get("name_he", "")
    if name:
        html = html.replace("אזה״ת חולון", name)
    active = zone.get("active_boreholes")
    if active is not None:
        # reference uses a placeholder span "~58" for the borehole count
        html = html.replace('<span class="placeholder">~58</span>', esc(active))
        html = html.replace("~58", esc(active))

    # Section containers (depth-balanced).
    html = replace_container_inner(html, '<div class="bottomline">',
                                   build_bottomline(brief.get("bottom_line", [])))
    html = replace_container_inner(html, '<div class="kpi-grid">',
                                   build_kpi_grid(brief.get("kpis", [])))
    html = replace_container_inner(html, '<div class="ledger">',
                                   build_ledger(brief.get("family_ledger", [])))
    html = replace_container_inner(html, '<div class="findings-toc">',
                                   build_findings_toc(brief.get("findings", [])))

    # Findings cards region: between the TOC's closing comment area and the
    # severity-matrix banner. Replace the run of <article class="finding"> ...
    # </article> blocks that sits after the TOC and before SEVERITY MATRIX.
    findings = brief.get("findings", [])
    cards_html = build_findings_cards_internal(findings)
    if cards_html:
        # Anchor: from the first "<!-- F1 -->" comment up to the SEVERITY banner.
        sev_banner = "<!-- ════════════════ SEVERITY MATRIX ════════════════ -->"
        m_first = re.search(r'\n\s*<!-- F1 -->', html)
        sev_idx = html.find(sev_banner)
        if m_first and sev_idx != -1:
            # find the </section> that closes the findings section (last before banner)
            sec_close = html.rfind("</section>", m_first.start(), sev_idx)
            if sec_close != -1:
                html = html[:m_first.start()] + "\n" + cards_html + "\n  " + html[sec_close:]
            else:
                sys.stderr.write("warning: findings </section> anchor not found\n")
        else:
            sys.stderr.write("warning: findings cards region not found\n")

    # Decisions table (depth scan over <table>).
    dec_html = build_decisions(brief.get("decisions", []))
    if dec_html:
        html = _replace_table_inner(html, '<table class="decisions">', dec_html)

    # Doc id (treated as a dynamic field).
    doc_id = zone.get("doc_id_internal")
    if doc_id:
        html = html.replace("HOL/EXEC/INT/2026-01", esc(doc_id))
        html = html.replace("HOL/2026/01", esc(doc_id))

    return html


def _replace_table_inner(html: str, open_tag: str, inner: str) -> str:
    """Replace inner HTML of a <table> by locating its matching </table>."""
    start = html.find(open_tag)
    if start == -1:
        sys.stderr.write(f"warning: table not found: {open_tag}\n")
        return html
    inner_start = start + len(open_tag)
    end = html.find("</table>", inner_start)
    if end == -1:
        sys.stderr.write(f"warning: no </table> for: {open_tag}\n")
        return html
    return html[:inner_start] + inner + html[end:]


def generate_public_html(brief: dict, reference_path: Path) -> str:
    html = reference_path.read_text(encoding="utf-8")
    zone = brief.get("zone", {})

    name = zone.get("name_he", "")
    if name:
        html = html.replace("אזה״ת חולון", name)
    active = zone.get("active_boreholes")
    if active is not None:
        html = html.replace('<span class="placeholder">~58</span>', esc(active))
        html = html.replace("~58", esc(active))

    # §01 context prose + framing card body + stats.
    html = replace_container_inner(html, '<div class="context-prose">',
                                   build_context_prose(brief.get("context_intro", [])))
    # framing-card has a nested .body div we target directly.
    html = replace_container_inner(html, '<div class="body">',
                                   build_framing_card_body(brief.get("framing_warning", "")))
    html = replace_container_inner(html, '<div class="stats">',
                                   build_stats_public(brief.get("stats_public", [])))

    # §02 timeline events.
    html = replace_container_inner(html, '<div class="timeline-events">',
                                   build_timeline(brief.get("timeline", [])))

    # §03 public findings region.
    html = replace_container_inner(html, '<div class="findings-public">',
                                   build_findings_public(brief.get("findings", [])))

    # §05 means grid.
    html = replace_container_inner(html, '<div class="means-grid">',
                                   build_means_grid(brief.get("means_summary", [])))

    # §06 methodology.
    html = replace_container_inner(html, '<div class="methodology">',
                                   build_methodology(brief.get("methodology", [])))

    # Footer contact + doc id.
    contact = brief.get("contact", {})
    email = contact.get("email")
    if email:
        html = html.replace("water@water.gov.il", esc(email))
    doc_id = zone.get("doc_id_public")
    if doc_id:
        html = html.replace("HOL/EXEC/PUB/2026-01", esc(doc_id))
        html = html.replace("HOL/2026/01", esc(doc_id))

    return html


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zone", required=True, help="zone id (e.g. 'holon')")
    ap.add_argument("--force", action="store_true", help="overwrite existing HTML")
    args = ap.parse_args()

    p = zone_paths(args.zone)
    brief = load_brief(p["brief"])
    p["output_dir"].mkdir(parents=True, exist_ok=True)

    for key, gen, ref in (
        ("internal_out", generate_internal_html, "reference_internal"),
        ("public_out", generate_public_html, "reference_public"),
    ):
        out = p[key]
        if out.exists() and not args.force:
            sys.exit(f"refusing to overwrite (use --force): {out}")
        html = gen(brief, p[ref])
        out.write_text(html, encoding="utf-8")
        print(f"wrote: {out}")


if __name__ == "__main__":
    main()
