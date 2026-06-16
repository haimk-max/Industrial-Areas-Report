#!/usr/bin/env python3
"""
Fix RTL arrow direction issues in MD/HTML deliverables.

Strategy (per commit 0c4b9eb):
1. Technical identifiers (all-English terms) → wrap in <bdi> to force LTR
   e.g., <bdi>diagnosis → prompt</bdi>
2. Pipeline step references → wrap in <bdi>
   e.g., <bdi><code>render-diagnosis</code>→#1</bdi>
3. Prose arrows in Hebrew → replace with em-dash (—) or restructure

This script:
- Scans all .md and .html files (excludes _backup, .git)
- Detects arrow context (Hebrew/English, technical/prose)
- Applies fixes
- Generates summary of changes per file
"""

import re
import os
import argparse
from pathlib import Path
from collections import defaultdict
import json

# Hebrew letter ranges (UTF-8 codepoints)
HEBREW_RANGE = (0x0590, 0x05FF)

def is_hebrew_char(c):
    """Check if character is Hebrew."""
    return HEBREW_RANGE[0] <= ord(c) <= HEBREW_RANGE[1]

def has_hebrew(text):
    """Check if text contains Hebrew characters."""
    return any(is_hebrew_char(c) for c in text)

def is_english_term(text):
    """Check if text is all-English (letters, digits, underscores, hyphens)."""
    return bool(re.match(r'^[a-zA-Z0-9_\-\s]+$', text))

class ArrowFixer:
    def __init__(self, debug=False):
        self.debug = debug
        self.changes = defaultdict(list)

    def fix_file(self, filepath):
        """Fix arrows in a single file. Returns (original_text, fixed_text, changes_list)."""
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()

        fixed = original
        file_changes = []

        # Determine file type
        is_html = filepath.endswith('.html')
        is_md = filepath.endswith('.md')

        if not (is_html or is_md):
            return original, fixed, file_changes

        # Strategy 1: Find arrows in HTML context; wrap technical terms
        # Pattern: look for text containing → or ← not already in <bdi>

        # First, extract all arrow occurrences with context
        arrow_pattern = r'(.{0,50}[→←].{0,50})'
        matches = list(re.finditer(arrow_pattern, fixed))

        # Process from end to start to maintain string positions
        for match in reversed(matches):
            context = match.group(0)
            start_idx = match.start()

            # Skip if already in <bdi> or <pre> or <code> (except special cases)
            before = fixed[:start_idx]
            bdi_count = before.count('<bdi>') - before.count('</bdi>')
            pre_count = before.count('<pre>') - before.count('</pre>')
            code_count = before.count('<code>') - before.count('</code>')

            # Already in bdi context: skip
            if bdi_count > 0:
                continue

            # In pre/code: analyze further
            if pre_count > 0:
                continue  # Pre-formatted: keep as-is

            # Analyze context to determine fix strategy
            fix = self._analyze_and_fix_arrow(context, filepath)
            if fix:
                original_snippet = fix['original']
                fixed_snippet = fix['fixed']

                # Replace in document
                idx = fixed.rfind(original_snippet, 0, start_idx + len(context))
                if idx >= 0:
                    fixed = fixed[:idx] + fixed_snippet + fixed[idx + len(original_snippet):]
                    file_changes.append({
                        'original': original_snippet,
                        'fixed': fixed_snippet,
                        'reason': fix['reason'],
                        'line_context': self._get_line_context(original, idx)
                    })

        return original, fixed, file_changes

    def _analyze_and_fix_arrow(self, context, filepath):
        """Analyze arrow in context and decide on fix strategy."""

        # Strategy 1: Technical identifiers with arrows
        # Pattern: all-English terms connected by → or ←
        # Example: "diagnosis → prompt" → wrap in <bdi>

        tech_pattern = r'([a-zA-Z_][a-zA-Z0-9_\-]*\s*[→←]\s*[a-zA-Z_][a-zA-Z0-9_\-]*)'
        if re.search(tech_pattern, context):
            match = re.search(tech_pattern, context)
            if match:
                term = match.group(0)
                # Check if it's not already in bdi
                if '<bdi>' not in context or '</bdi>' not in context:
                    return {
                        'original': term,
                        'fixed': f'<bdi>{term}</bdi>',
                        'reason': 'Technical identifier: wrap in <bdi> to force LTR'
                    }

        # Strategy 2: Code references with arrows
        # Pattern: <code>something</code>→#N or ←#N
        code_arrow_pattern = r'(<code>[^<]+</code>\s*[→←]\s*#?\d+)'
        if re.search(code_arrow_pattern, context):
            match = re.search(code_arrow_pattern, context)
            if match:
                term = match.group(0)
                if '<bdi>' not in term:
                    return {
                        'original': term,
                        'fixed': f'<bdi>{term}</bdi>',
                        'reason': 'Code reference with arrow: wrap in <bdi> to force LTR'
                    }

        # Strategy 3: Prose arrows in Hebrew
        # Pattern: Hebrew text with → or ← (not technical)
        if has_hebrew(context):
            # Check if it's not a technical term
            if not is_english_term(context):
                # Look for bare → or ← arrows (not in technical context)
                if '→' in context:
                    # Replace with em-dash followed by "תוצאה:" for clarity
                    fixed = context.replace('→', ' —')
                    if fixed != context:
                        return {
                            'original': context,
                            'fixed': fixed,
                            'reason': 'Prose arrow in Hebrew: replace → with em-dash (—)'
                        }
                if '←' in context:
                    fixed = context.replace('←', '—')
                    if fixed != context:
                        return {
                            'original': context,
                            'fixed': fixed,
                            'reason': 'Prose arrow in Hebrew: replace ← with em-dash (—)'
                        }

        return None

    def _get_line_context(self, text, position):
        """Get line number and surrounding context."""
        line_num = text[:position].count('\n') + 1
        lines = text.split('\n')
        idx = line_num - 1
        context_lines = []
        if idx > 0:
            context_lines.append(f"  {lines[idx-1][:80]}")
        context_lines.append(f"> {lines[idx][:80]}")
        if idx + 1 < len(lines):
            context_lines.append(f"  {lines[idx+1][:80]}")
        return f"Line {line_num}:\n" + '\n'.join(context_lines)

    def generate_report(self, target='main'):
        """Generate summary report of all changes."""
        report = []
        report.append(f"\n{'='*70}")
        report.append(f"RTL ARROW FIX REPORT (target: {target})")
        report.append(f"{'='*70}\n")

        total_changes = 0
        for filepath, changes in sorted(self.changes.items()):
            if changes:
                report.append(f"\n{filepath}")
                report.append(f"  Changes: {len(changes)}")
                for i, change in enumerate(changes[:3], 1):  # Show top 3
                    report.append(f"\n  [{i}] {change['reason']}")
                    report.append(f"      Original: {change['original'][:60]}")
                    report.append(f"      Fixed:    {change['fixed'][:60]}")
                if len(changes) > 3:
                    report.append(f"\n  ... and {len(changes) - 3} more changes")
                total_changes += len(changes)

        report.append(f"\n{'='*70}")
        report.append(f"TOTAL CHANGES: {total_changes}")
        report.append(f"{'='*70}\n")

        return '\n'.join(report)

def scan_target(target_path, exclude_patterns=None, critical_only=False):
    """Scan target directory for .md and .html files.

    Args:
        target_path: Root directory to scan
        exclude_patterns: List of patterns to exclude (default: _backup, .git, etc)
        critical_only: If True, scan only critical deliverable files (main branch)
    """
    if exclude_patterns is None:
        exclude_patterns = ['_backup', '.git', '__pycache__', 'node_modules', 'worktree']

    files = []

    if critical_only:
        # Define critical deliverable paths (main branch only)
        critical_globs = [
            'CLAUDE.md',
            'PROCESS.md',
            'ZONE_REPORT_PROCESS_GUIDE.md',
            'REPORT_V5_SCHEMA.md',
            'DATA_DICTIONARY.md',
            'DATA_PIPELINE_SPEC.md',
            'docs/TECHNICAL_OVERVIEW.md',
            'docs/TECHNICAL_OVERVIEW.html',
            'docs/TECHNICAL_OVERVIEW.en.md',
            'docs/TECHNICAL_OVERVIEW.en.html',
            'Holon/output/HOLON_REPORT_V*.md',
            'Holon/output/HOLON_REPORT_V*.html',
            'Holon/output/HOLON_EXECUTIVE_SUMMARY*.html',
            'Raanana/output/RAANANA_REPORT_V*.md',
            'Raanana/output/drilling_card*.md',
        ]
        base = Path(target_path)
        for pattern in critical_globs:
            for filepath in base.glob(pattern):
                if '_backup' not in str(filepath) and '.git' not in str(filepath) and 'worktree' not in str(filepath):
                    files.append(str(filepath))
    else:
        for root, dirs, filenames in os.walk(target_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not any(excl in d for excl in exclude_patterns)]

            for filename in filenames:
                if filename.endswith(('.md', '.html')):
                    filepath = os.path.join(root, filename)
                    files.append(filepath)

    return sorted(files)

def main():
    parser = argparse.ArgumentParser(
        description='Fix RTL arrow rendering in MD/HTML deliverables.'
    )
    parser.add_argument(
        '--target',
        default='main',
        help='Target branch or directory (default: main)'
    )
    parser.add_argument(
        '--report',
        default='rtl_fix_summary.txt',
        help='Output report file (default: rtl_fix_summary.txt)'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply fixes (default: dry-run, report only)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    parser.add_argument(
        '--critical-only',
        action='store_true',
        help='Scan only critical deliverable files (main branch)'
    )

    args = parser.parse_args()

    # Get list of files to process
    repo_root = '/home/user/Industrial-Areas-Report'
    files = scan_target(repo_root, critical_only=args.critical_only)

    if args.debug:
        print(f"Found {len(files)} deliverable files to scan")

    fixer = ArrowFixer(debug=args.debug)

    files_with_changes = 0
    total_changes = 0

    for filepath in files:
        original, fixed, changes = fixer.fix_file(filepath)

        if changes:
            files_with_changes += 1
            total_changes += len(changes)
            fixer.changes[filepath] = changes

            if args.debug:
                print(f"\n{filepath}: {len(changes)} changes")
                for change in changes:
                    print(f"  - {change['reason']}")

            if args.apply:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed)
                if args.debug:
                    print(f"  ✓ Applied")

    # Generate and save report
    report = fixer.generate_report(args.target)
    print(report)

    with open(args.report, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport saved to: {args.report}")
    print(f"Files with changes: {files_with_changes}")
    print(f"Total changes identified: {total_changes}")

    if not args.apply:
        print("\n⚠ DRY RUN: No changes applied.")
        print(f"Run with --apply to write fixes to disk.")

if __name__ == '__main__':
    main()
