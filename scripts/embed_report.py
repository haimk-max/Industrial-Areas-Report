"""embed_report.py — Convert zone report Markdown to self-contained HTML.

Reads the Markdown report, embeds all referenced PNG images as base64 data URIs,
applies RTL-ready Hebrew CSS, and writes a single .html file.

Usage:
  python scripts/embed_report.py
  python scripts/embed_report.py --input Raanana/output/RAANANA_REPORT_V2.md
  python scripts/embed_report.py --output Raanana/output/RAANANA_REPORT_V2.html
"""

import argparse
import base64
import re
import sys
from pathlib import Path

DEFAULT_INPUT  = "Raanana/output/RAANANA_REPORT_V2.md"
DEFAULT_OUTPUT = "Raanana/output/RAANANA_REPORT_V2.html"

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{
    --text: #1A1A2E;
    --bg: #FAFAFA;
    --accent: #1565C0;
    --border: #DDD;
    --warning-bg: #FFF3E0;
    --warning-border: #F9A825;
  }}
  body {{
    font-family: 'David', 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    line-height: 1.7;
    color: var(--text);
    background: var(--bg);
    max-width: 960px;
    margin: 0 auto;
    padding: 24px 32px;
    direction: rtl;
    text-align: right;
  }}
  h1 {{ font-size: 1.7em; border-bottom: 3px solid var(--accent); padding-bottom: 6px; }}
  h2 {{ font-size: 1.3em; border-right: 4px solid var(--accent); padding-right: 10px; margin-top: 2em; }}
  h3 {{ font-size: 1.1em; color: var(--accent); margin-top: 1.5em; }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    font-size: 0.92em;
  }}
  th {{ background: var(--accent); color: white; padding: 6px 10px; }}
  td {{ border: 1px solid var(--border); padding: 5px 10px; }}
  tr:nth-child(even) td {{ background: #F5F8FF; }}
  img {{
    max-width: 100%;
    border: 1px solid var(--border);
    border-radius: 4px;
    display: block;
    margin: 12px auto;
  }}
  figcaption, p > strong:first-child + * {{ color: #555; font-size: 0.9em; }}
  blockquote {{
    border-right: 4px solid var(--warning-border);
    background: var(--warning-bg);
    margin: 1em 0;
    padding: 8px 16px;
    border-radius: 0 4px 4px 0;
  }}
  code {{ background: #EEE; padding: 1px 5px; border-radius: 3px; font-size: 0.9em; }}
  hr {{ border: none; border-top: 1px solid var(--border); margin: 2em 0; }}
  .page-meta {{
    font-size: 0.85em;
    color: #888;
    border-top: 1px solid var(--border);
    margin-top: 3em;
    padding-top: 8px;
  }}
</style>
</head>
<body>
{body}
<div class="page-meta">נוצר אוטומטית מ-{source_file} | {timestamp}</div>
</body>
</html>
"""


def md_to_html_minimal(md: str) -> str:
    """Minimal Markdown → HTML conversion (headings, bold, tables, images, hr, lists)."""
    try:
        import markdown
        return markdown.markdown(md, extensions=['tables', 'fenced_code'])
    except ImportError:
        pass

    # Fallback — hand-rolled (covers structures used in the report)
    lines = md.splitlines()
    html_lines = []
    in_table = False

    for line in lines:
        # HR
        if re.match(r'^---+$', line.strip()):
            if in_table:
                html_lines.append('</table>')
                in_table = False
            html_lines.append('<hr>')
            continue

        # Headings
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            if in_table:
                html_lines.append('</table>')
                in_table = False
            level = len(m.group(1))
            content = _inline(m.group(2))
            html_lines.append(f'<h{level}>{content}</h{level}>')
            continue

        # Tables
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if re.match(r'^[\|\s:\-]+$', line):  # separator row
                continue
            if not in_table:
                html_lines.append('<table>')
                in_table = True
                tag = 'th'
            else:
                tag = 'td'
            html_lines.append('<tr>' + ''.join(f'<{tag}>{_inline(c)}</{tag}>' for c in cells) + '</tr>')
            continue

        if in_table:
            html_lines.append('</table>')
            in_table = False

        # Blank line
        if not line.strip():
            html_lines.append('')
            continue

        # Bullet list
        if re.match(r'^\s*[-*]\s+', line):
            html_lines.append('<li>' + _inline(re.sub(r'^\s*[-*]\s+', '', line)) + '</li>')
            continue

        # Numbered list
        if re.match(r'^\s*\d+\.\s+', line):
            html_lines.append('<li>' + _inline(re.sub(r'^\s*\d+\.\s+', '', line)) + '</li>')
            continue

        # Regular paragraph line
        html_lines.append('<p>' + _inline(line) + '</p>')

    if in_table:
        html_lines.append('</table>')

    return '\n'.join(html_lines)


def _inline(text: str) -> str:
    """Process inline Markdown: bold, italic, code, links, images."""
    # Images — replaced by embed_images() before this is called, so just pass through
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Bold+italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def embed_images(md: str, base_dir: Path) -> str:
    """Replace all ![alt](relative/path.png) with data URI base64 inline."""
    def replace_img(m):
        alt  = m.group(1)
        path = m.group(2)
        img_path = (base_dir / path).resolve()
        if img_path.exists() and img_path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif'):
            data = base64.b64encode(img_path.read_bytes()).decode('ascii')
            mime = 'image/png' if img_path.suffix.lower() == '.png' else 'image/jpeg'
            return f'![{alt}](data:{mime};base64,{data})'
        return m.group(0)  # leave unchanged if not found

    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_img, md)


def extract_title(md: str) -> str:
    m = re.search(r'^#\s+(.+)', md, re.MULTILINE)
    return m.group(1) if m else 'דו"ח ניטור'


def main():
    parser = argparse.ArgumentParser(description="Embed images and convert Markdown report to HTML")
    parser.add_argument("--input",  default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    in_path  = Path(args.input)
    out_path = Path(args.output)

    if not in_path.exists():
        sys.exit(f"Input not found: {in_path}")

    md = in_path.read_text(encoding='utf-8')
    md_embedded = embed_images(md, in_path.parent)

    body = md_to_html_minimal(md_embedded)
    title = extract_title(md)

    from datetime import date
    html = HTML_TEMPLATE.format(
        title=title,
        body=body,
        source_file=in_path.name,
        timestamp=date.today().isoformat()
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding='utf-8')

    size_kb = out_path.stat().st_size // 1024
    print(f"✓ Written: {out_path}  ({size_kb} KB — self-contained with embedded images)")


if __name__ == "__main__":
    main()
