#!/usr/bin/env python3
"""Extract and categorize comments from reviewed Word documents.

Processes track changes and comments in Word files, separating:
1. Point-specific comments (direct edits/suggestions for specific text)
2. General comments (process-level improvements for report generation)
"""

import sys
import json
from pathlib import Path
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import qn


def extract_track_changes(docx_path):
    """Extract all track changes (insertions, deletions, modifications) from Word document."""
    doc = Document(docx_path)
    changes = []

    # Extract changes from document.xml
    for element in doc.element.body.iter():
        # Look for tracked changes
        if element.tag == qn('w:ins'):  # Insertion
            author = element.get(qn('w:author'), 'Unknown')
            date = element.get(qn('w:date'), 'Unknown')
            text = ''.join(element.itertext())
            changes.append({
                'type': 'insertion',
                'author': author,
                'date': date,
                'text': text,
            })

        elif element.tag == qn('w:del'):  # Deletion
            author = element.get(qn('w:author'), 'Unknown')
            date = element.get(qn('w:date'), 'Unknown')
            text = ''.join(element.itertext())
            changes.append({
                'type': 'deletion',
                'author': author,
                'date': date,
                'text': text,
            })

    return changes


def extract_comments(docx_path):
    """Extract all comments (annotations) from Word document."""
    doc = Document(docx_path)
    comments_list = []

    # Access comments part
    try:
        comments_part = doc.part.relate_to(
            'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments',
            is_external=False
        )
    except Exception:
        # If no comments part, return empty list
        return []

    try:
        comments_elem = parse_xml(comments_part.blob)
        for comment in comments_elem:
            comment_id = comment.get(qn('w:id'))
            author = comment.get(qn('w:author'))
            date = comment.get(qn('w:date'))
            initials = comment.get(qn('w:initials'))

            # Extract comment text
            text_elem = comment.find(qn('w:p'))
            text = ''.join(text_elem.itertext()) if text_elem is not None else ''

            comments_list.append({
                'id': comment_id,
                'author': author,
                'date': date,
                'initials': initials,
                'text': text,
            })
    except Exception as e:
        print(f"Warning: Could not extract comments: {e}", file=sys.stderr)

    return comments_list


def categorize_comments(changes, comments):
    """Categorize comments as point-specific or general."""
    categorized = {
        'point_specific': [],  # Comments on specific text/locations
        'general': [],         # Process-level suggestions
        'track_changes': changes,
    }

    for comment in comments:
        text = comment.get('text', '').lower()

        # Heuristics for categorization
        general_keywords = [
            'process', 'workflow', 'methodology', 'approach', 'structure',
            'organization', 'format', 'style', 'generation', 'template',
            'pipeline', 'consider', 'suggest', 'recommend', 'improve'
        ]

        is_general = any(keyword in text for keyword in general_keywords)

        if is_general:
            categorized['general'].append(comment)
        else:
            categorized['point_specific'].append(comment)

    return categorized


def generate_comment_report(docx_path, output_json_path=None, output_md_path=None):
    """Generate a report of all comments and track changes."""
    print(f"Processing: {docx_path}")

    # Extract changes and comments
    changes = extract_track_changes(docx_path)
    comments = extract_comments(docx_path)

    # Categorize
    categorized = categorize_comments(changes, comments)

    # Output JSON
    if output_json_path:
        output_data = {
            'source_file': str(docx_path),
            'summary': {
                'total_track_changes': len(changes),
                'total_comments': len(comments),
                'point_specific_comments': len(categorized['point_specific']),
                'general_comments': len(categorized['general']),
            },
            'track_changes': changes,
            'comments': categorized,
        }

        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved JSON report: {output_json_path}")

    # Output Markdown
    if output_md_path:
        with open(output_md_path, 'w', encoding='utf-8') as f:
            f.write("# דוח הערות וטרקינג שינויים\n\n")
            f.write(f"**קובץ מקור**: {Path(docx_path).name}\n\n")

            f.write("## סיכום\n\n")
            summary = categorized['summary'] if 'summary' in categorized else {
                'total_track_changes': len(changes),
                'total_comments': len(comments),
            }
            f.write(f"- טרקינג שינויים: {len(changes)}\n")
            f.write(f"- הערות כוללות: {len(comments)}\n")
            f.write(f"- הערות נקודתיות: {len(categorized['point_specific'])}\n")
            f.write(f"- הערות כלליות: {len(categorized['general'])}\n\n")

            # Track changes section
            if changes:
                f.write("## שינויים שנעקבו (Track Changes)\n\n")
                for i, change in enumerate(changes, 1):
                    f.write(f"### שינוי {i}\n\n")
                    f.write(f"- **סוג**: {change.get('type', 'unknown')}\n")
                    f.write(f"- **מחבר**: {change.get('author', 'Unknown')}\n")
                    f.write(f"- **תאריך**: {change.get('date', 'Unknown')}\n")
                    f.write(f"- **תוכן**: {change.get('text', '')}\n\n")

            # Point-specific comments
            if categorized['point_specific']:
                f.write("## הערות נקודתיות (לשיבוץ ישיר)\n\n")
                for i, comment in enumerate(categorized['point_specific'], 1):
                    f.write(f"### הערה {i}\n\n")
                    f.write(f"- **מחבר**: {comment.get('author', 'Unknown')}\n")
                    f.write(f"- **תאריך**: {comment.get('date', 'Unknown')}\n")
                    f.write(f"- **תוכן**: {comment.get('text', '')}\n\n")

            # General comments
            if categorized['general']:
                f.write("## הערות כלליות (לשיפור התהליך)\n\n")
                for i, comment in enumerate(categorized['general'], 1):
                    f.write(f"### הערה {i}\n\n")
                    f.write(f"- **מחבר**: {comment.get('author', 'Unknown')}\n")
                    f.write(f"- **תאריך**: {comment.get('date', 'Unknown')}\n")
                    f.write(f"- **תוכן**: {comment.get('text', '')}\n\n")

        print(f"✓ Saved Markdown report: {output_md_path}")

    return categorized


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python process_word_comments.py <input.docx> [output.json] [output.md]")
        sys.exit(1)

    docx_file = Path(sys.argv[1])
    json_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    md_file = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    if not docx_file.exists():
        print(f"Error: {docx_file} not found")
        sys.exit(1)

    categorized = generate_comment_report(str(docx_file), str(json_file) if json_file else None,
                                          str(md_file) if md_file else None)

    print(f"\nSummary:")
    print(f"  Point-specific comments: {len(categorized['point_specific'])}")
    print(f"  General comments: {len(categorized['general'])}")
