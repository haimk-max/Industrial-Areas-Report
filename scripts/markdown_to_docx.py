#!/usr/bin/env python3
"""Convert Holon V5 Markdown report to Word (.docx) format with RTL and justified text."""

import sys
import re
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def set_paragraph_rtl(paragraph):
    """Set paragraph direction to RTL and alignment to justified."""
    # Set direction to RTL
    pPr = paragraph._element.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    pPr.append(bidi)

    # Set alignment to justified
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Set language to Hebrew
    rPr = OxmlElement('w:rPr')
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'he-IL')
    rPr.append(lang)
    pPr.append(rPr)


def parse_markdown(content):
    """Parse markdown content into blocks of structured data."""
    blocks = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Headings
        match = re.match(r'^(#{1,6})\s+(.*)', line)
        if match:
            level = len(match.group(1))
            text = match.group(2)
            blocks.append(('heading', level, text))
            i += 1
            continue

        # Tables (start with |)
        if line.strip().startswith('|'):
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            blocks.append(('table', table_lines))
            continue

        # Lists (start with - or *)
        if line.strip().startswith(('-', '*')) and line.strip()[1] == ' ':
            list_items = []
            while i < len(lines):
                m = re.match(r'^[-*]\s+(.*)', lines[i])
                if m:
                    list_items.append(m.group(1))
                    i += 1
                else:
                    break
            blocks.append(('list', list_items))
            continue

        # Paragraphs (collect until empty line or special line)
        para_lines = []
        while i < len(lines):
            line = lines[i]
            if (not line.strip() or
                re.match(r'^#{1,6}\s', line) or
                line.strip().startswith('|') or
                (line.strip() and line.strip()[0] in '-*' and len(line) > 1 and line.strip()[1] == ' ')):
                break
            para_lines.append(line)
            i += 1

        if para_lines:
            text = '\n'.join(para_lines).strip()
            if text:
                blocks.append(('paragraph', text))

    return blocks


def parse_inline_formatting(text):
    """Parse inline formatting (bold, italic, code, links) and return styled runs."""
    # This is a simplified version - returns (text, is_bold, is_italic, is_code)
    # In a real implementation, you'd need more complex parsing

    runs = []
    pattern = r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[([^\]]+)\]\(([^)]+)\)|[^*`\[]+)'

    for match in re.finditer(pattern, text):
        content = match.group(0)

        if content.startswith('**') and content.endswith('**'):
            runs.append(('text', content[2:-2], True, False, False, None))
        elif content.startswith('*') and content.endswith('*'):
            runs.append(('text', content[1:-1], False, True, False, None))
        elif content.startswith('`') and content.endswith('`'):
            runs.append(('text', content[1:-1], False, False, True, None))
        elif content.startswith('['):
            m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', content)
            if m:
                runs.append(('link', m.group(1), False, False, False, m.group(2)))
        else:
            runs.append(('text', content, False, False, False, None))

    return runs


def parse_table(table_lines):
    """Parse markdown table into rows and columns."""
    rows = []
    for line in table_lines:
        if line.strip().startswith('|') and '---' not in line:
            # Remove leading/trailing | and split
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            rows.append(cells)
    return rows


def add_paragraph_with_formatting(doc, text):
    """Add a paragraph with inline formatting support."""
    para = doc.add_paragraph()
    set_paragraph_rtl(para)

    # Simple inline formatting handling
    # Replace **text** with bold, *text* with italic
    parts = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)', text)

    for part in parts:
        if not part:
            continue

        if part.startswith('**') and part.endswith('**'):
            run = para.add_run(part[2:-2])
            run.bold = True
        elif part.startswith('*') and part.endswith('*'):
            run = para.add_run(part[1:-1])
            run.italic = True
        elif part.startswith('`') and part.endswith('`'):
            run = para.add_run(part[1:-1])
            run.font.name = 'Courier New'
            run.font.color.rgb = RGBColor(128, 0, 0)
        else:
            para.add_run(part)


def markdown_to_docx(md_path, docx_path):
    """Convert markdown file to Word document with RTL and justified text."""
    # Read markdown file
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create Word document
    doc = Document()

    # Set default font to support Hebrew
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    # Set document-level RTL setting
    settings = doc.settings._element
    settings_obj = doc.element.body.getparent().getprevious()

    # Add document properties for RTL and track changes
    # Ensure trackRevisions is enabled at document level
    if settings is not None:
        # Remove existing trackRevisions if present
        existing = settings.find(qn('w:trackRevisions'))
        if existing is not None:
            settings.remove(existing)

        # Add trackRevisions element
        track_revisions = OxmlElement('w:trackRevisions')
        settings.insert(0, track_revisions)

    # Parse markdown into blocks
    blocks = parse_markdown(content)

    # Add blocks to document
    for block in blocks:
        if block[0] == 'heading':
            _, level, text = block
            heading = doc.add_heading(text, level=level)
            set_paragraph_rtl(heading)

        elif block[0] == 'paragraph':
            _, text = block
            add_paragraph_with_formatting(doc, text)

        elif block[0] == 'table':
            _, table_lines = block
            rows = parse_table(table_lines)

            if rows:
                # First row is header
                table = doc.add_table(rows=len(rows), cols=len(rows[0]))
                table.style = 'Light Grid Accent 1'

                for row_idx, row_data in enumerate(rows):
                    for col_idx, cell_text in enumerate(row_data):
                        cell = table.rows[row_idx].cells[col_idx]
                        para = cell.paragraphs[0]
                        para.text = cell_text
                        set_paragraph_rtl(para)

                        if row_idx == 0:  # Header row
                            para.runs[0].bold = True

        elif block[0] == 'list':
            _, items = block
            for item in items:
                para = doc.add_paragraph(item, style='List Bullet')
                set_paragraph_rtl(para)

    # Save document
    doc.save(docx_path)
    print(f"✓ Word document created: {docx_path}")
    print(f"  - RTL (right-to-left) text direction: enabled")
    print(f"  - Text alignment: justified")
    print(f"  - Track changes: enabled")
    print(f"  - Language: Hebrew (he-IL)")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python markdown_to_docx.py <input.md> <output.docx>")
        sys.exit(1)

    md_file = Path(sys.argv[1])
    docx_file = Path(sys.argv[2])

    if not md_file.exists():
        print(f"Error: {md_file} not found")
        sys.exit(1)

    markdown_to_docx(str(md_file), str(docx_file))
