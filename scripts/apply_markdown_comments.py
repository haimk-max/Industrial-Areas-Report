#!/usr/bin/env python3
"""Apply point-specific comments from Word document to Markdown report.

Takes categorized comments and integrates them as inline notes in the markdown.
"""

import sys
import json
from pathlib import Path


def load_comment_report(json_path):
    """Load the categorized comments from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def apply_comments_to_markdown(md_path, comments_json_path, output_md_path):
    """Apply point-specific comments to markdown report."""
    # Load comments
    comment_data = load_comment_report(comments_json_path)
    point_specific = comment_data['comments'].get('point_specific', [])

    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # For each point-specific comment, add it as a note in the markdown
    # This is a simple implementation - in production, you'd want more sophisticated matching
    for comment in point_specific:
        text = comment.get('text', '')
        author = comment.get('author', 'Expert')
        date = comment.get('date', '')

        # Create a comment block
        comment_block = f"\n\n> **הערה מ-{author}** ({date}): {text}\n"

        # Simple heuristic: if comment contains keywords, insert at relevant location
        # In production, you'd match comments to specific paragraphs more accurately
        md_content += comment_block

    # Write output
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"✓ Applied {len(point_specific)} comments to markdown")
    print(f"✓ Saved to: {output_md_path}")


def generate_general_comment_summary(comments_json_path, output_md_path):
    """Generate a summary of general comments for review."""
    comment_data = load_comment_report(comments_json_path)
    general = comment_data['comments'].get('general', [])

    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write("# סיכום הערות כלליות לשיפור התהליך\n\n")
        f.write(f"**תאריך**: {general[0].get('date', 'Unknown') if general else 'N/A'}\n\n")

        if not general:
            f.write("אין הערות כלליות.\n")
        else:
            f.write(f"**סה\"כ הערות כלליות**: {len(general)}\n\n")

            for i, comment in enumerate(general, 1):
                f.write(f"## {i}. הערה מ-{comment.get('author', 'Unknown')}\n\n")
                f.write(f"{comment.get('text', '')}\n\n")
                f.write(f"*תאריך: {comment.get('date', 'Unknown')}*\n\n")

            f.write("---\n\n")
            f.write("## מדיניות יישום הערות כלליות\n\n")
            f.write("""
1. **ניתוח סמנטי**: כל הערה כללית תנותח כדי להבין את המטרה (שיפור מבנה, תוכן, וכו')
2. **עדכון תהליך**: הערות שחוזרות על עצמן יביאו לשיפור בתהליך ייצור הדוח (פרומפטים, דגשים)
3. **ללא ערבוב בנתונים**: הערות לא יגרמו לשיבוץ ישיר של טבלאות או חבילות קונטקסט בטקסט
4. **מעקב**: כל שיפור תהליך יתורגם לעדכון בסקריפטים/תבניות בעלי רלבנטיות
""")

    print(f"✓ Generated general comments summary: {output_md_path}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python apply_markdown_comments.py <input.md> <comments.json> <output.md> [general_summary.md]")
        sys.exit(1)

    md_file = Path(sys.argv[1])
    json_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])
    general_summary_file = Path(sys.argv[4]) if len(sys.argv) > 4 else None

    if not md_file.exists() or not json_file.exists():
        print(f"Error: Input files not found")
        sys.exit(1)

    apply_comments_to_markdown(str(md_file), str(json_file), str(output_file))

    if general_summary_file:
        generate_general_comment_summary(str(json_file), str(general_summary_file))
