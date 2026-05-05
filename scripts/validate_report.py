"""validate_report.py — three automated validators for the zone report.

Validators:
  1. chart_refs    — every ![...](../charts_v2/xxx.png) in report points to an existing file
  2. tone          — no banned phrases from STYLE_GUIDE (narrative storytelling, wrong terminology)
  3. attribution   — key numerical claims are accompanied by a source citation nearby

Usage:
  python scripts/validate_report.py [--report Raanana/output/RAANANA_REPORT_V2.md] [--charts-dir Raanana/charts_v2]
  python scripts/validate_report.py --validator chart_refs
  python scripts/validate_report.py --validator tone
  python scripts/validate_report.py --validator attribution
"""

import argparse
import re
import sys
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

DEFAULT_REPORT = "Raanana/output/RAANANA_REPORT_V2.md"
DEFAULT_CHARTS_DIR = "Raanana/charts_v2"

# Phrases that violate STYLE_GUIDE §A, §C, §J (narrative storytelling, wrong terms)
BANNED_PHRASES = [
    # Narrative / emotional — STYLE_GUIDE §J, §A.1
    "שקט מדומה",
    "מציאות אחרת",
    "עדויות שנחשפו",
    "לפתע",
    "מחריד",
    "מדהים",
    "מסתתר",
    "מסתיר",
    # Wrong terminology — STYLE_GUIDE §A.3
    "ממסים כלוריניים",         # → תרכובות אורגניות מוכלרות
    "ממסים כלורוגניים",
    "טרנד",                    # → מגמה
    "מתחם",                    # → קריית אתגרים / אזה"ת
    # Attribution terms that overstate certainty — STYLE_GUIDE §A.1, §J.3
    "בוודאות גורמת",
    "אחראי לזיהום",
    "בוודאות מקור",
    # Prohibited reporting language — REQ-C9
    "לדווח לרשות המים",
    "לדווח למשרד הגנת הסביבה",
    "דיווח לרשות",
    "דיווח למשרד",
    # Wrong analysis method name — CLAUDE.md §Trend Methodology, REQ-A4
    "רגרסיה לינארית",
    "linear regression",
    "ניתוח רגרסיה",
    # Wrong borehole classification name
    "בארות ייצור",              # → בארות הפקה
    "באר ייצור",                # → קידוח הפקה
]

# Source citation patterns that count as attribution (broad — avoids false alarms)
CITATION_PATTERNS = [
    r"דוח\s+20\d\d",           # "דוח 2013", "דוח 2021"
    r"עמ['\"׳]\s*\d+",         # "עמ' 35", "עמ׳ 35"
    r"טבלה\s+\d+",             # "טבלה 5"
    r"איור\s+\d+",             # "איור 29"
    r"Excel\s*:",               # "Excel: ..."
    r"facility_attribution",    # reference to facility JSON
    r"סעיף\s+\d+",             # "סעיף 3.2"
    r"\(20(1[1-9]|2[0-6])\)",  # "(2011)".."(2026)" — data year in parentheses
    r"TAHAL",
    r"PRTR",
    r"Mann-Kendall\s+Z=",      # MK result = self-contained statistical attribution
    r"p=\d+\.\d+",             # p-value — accompanies statistical claim
    r"SNR=\d",                  # SNR value
    r"יולי\s+201[0-9]|יולי\s+202[0-9]",  # explicit measurement date (month+year)
    r"ב-201\d|ב-202\d",        # "ב-2015", "ב-2023" — year reference (measurement attribution)
    r"web search",
]

# Patterns that indicate a numerical claim requiring attribution
CLAIM_PATTERNS = [
    r"\d+\.?\d*\s*מקג",        # "94.8 מקג" / "817 מקג"
    r"\d+,?\d*%\s*מהתקן",     # "1,264% מהתקן"
    r"Mann-Kendall\s+Z=",      # Z-score claim
    r"SNR=\d",                  # SNR value
    r"\d+\s*מ[\"׳]\s*(עומק|מפני)", # depth measurement
]


# ── Validator 1: chart_refs ───────────────────────────────────────────────────

def validate_chart_refs(report_path: Path, charts_dir: Path) -> list[str]:
    """Check every chart reference in the report exists on disk."""
    errors = []
    content = report_path.read_text(encoding='utf-8')

    # Pattern: ![...](../charts_v2/filename.png) or relative to report
    refs = re.findall(r'!\[.*?\]\(([^)]+\.png)\)', content)

    for ref in refs:
        # Resolve path relative to report file
        resolved = (report_path.parent / ref).resolve()
        if not resolved.exists():
            errors.append(f"  MISSING: {ref}  →  {resolved}")
        else:
            print(f"  OK: {ref}")

    return errors


# ── Validator 2: tone ─────────────────────────────────────────────────────────

def validate_tone(report_path: Path) -> list[str]:
    """Flag banned phrases that violate STYLE_GUIDE language rules."""
    errors = []
    content = report_path.read_text(encoding='utf-8')
    lines = content.splitlines()

    for phrase in BANNED_PHRASES:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        for lineno, line in enumerate(lines, start=1):
            if pattern.search(line):
                errors.append(f"  LINE {lineno}: banned phrase '{phrase}'\n    {line.strip()[:100]}")

    return errors


# ── Validator 3: attribution ──────────────────────────────────────────────────

def validate_attribution(report_path: Path) -> list[str]:
    """Check that sections with numerical claims contain at least one nearby citation.

    Strategy: scan each paragraph; if it contains a claim pattern,
    ensure the same paragraph contains at least one citation pattern.
    Flag paragraphs where claims exist but no citation found.

    Section 6 (Sources) is excluded from this check.
    """
    errors = []
    content = report_path.read_text(encoding='utf-8')

    # Split into paragraphs (separated by blank lines)
    paragraphs = re.split(r'\n\s*\n', content)

    # Rough section tracker to skip Section 6 (it's the citations itself)
    in_section_6 = False

    for i, para in enumerate(paragraphs):
        if re.search(r'^##\s*6\.', para, re.MULTILINE):
            in_section_6 = True
        if re.search(r'^##\s*[1-57-9]\.', para, re.MULTILINE):
            in_section_6 = False

        if in_section_6:
            continue

        # Skip headings-only paragraphs, image refs, and very short lines
        stripped = para.strip()
        if len(stripped) < 30 or stripped.startswith('#') or stripped.startswith('!'):
            continue

        # Check for numerical claims
        has_claim = any(re.search(p, para) for p in CLAIM_PATTERNS)

        if has_claim:
            # Check for at least one citation within the paragraph
            has_citation = any(re.search(p, para) for p in CITATION_PATTERNS)
            if not has_citation:
                # Show first 100 chars of paragraph + first claim found
                claim_found = next(
                    m.group() for p in CLAIM_PATTERNS
                    for m in [re.search(p, para)] if m
                )
                errors.append(
                    f"  PARAGRAPH {i+1}: claim '{claim_found}' without citation\n"
                    f"    {stripped[:120]}..."
                )

    return errors


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Validate zone report (chart_refs, tone, attribution)")
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--charts-dir", default=DEFAULT_CHARTS_DIR)
    parser.add_argument("--validator", choices=["chart_refs", "tone", "attribution"], default=None,
                        help="Run only one validator (default: all three)")
    args = parser.parse_args()

    report_path = Path(args.report)
    charts_dir = Path(args.charts_dir)

    if not report_path.exists():
        sys.exit(f"Report not found: {report_path}")

    run_all = args.validator is None

    total_errors = []
    total_warnings = 0

    # 1. chart_refs
    if run_all or args.validator == "chart_refs":
        print(f"\n[1] chart_refs — checking chart references in {report_path.name}")
        errs = validate_chart_refs(report_path, charts_dir)
        total_errors.extend(errs)
        status = "FAIL" if errs else "PASS"
        print(f"    → {status}: {len(errs)} issues")
        for e in errs:
            print(e)

    # 2. tone
    if run_all or args.validator == "tone":
        print(f"\n[2] tone — checking banned phrases")
        errs = validate_tone(report_path)
        total_errors.extend(errs)
        status = "FAIL" if errs else "PASS"
        print(f"    → {status}: {len(errs)} issues")
        for e in errs:
            print(e)

    # 3. attribution
    if run_all or args.validator == "attribution":
        print(f"\n[3] attribution — checking source citations in numerical claims")
        errs = validate_attribution(report_path)
        total_warnings += len(errs)
        status = "WARN" if errs else "PASS"
        print(f"    → {status}: {len(errs)} paragraphs with claims but no citation (soft check)")
        for e in errs:
            print(e)

    # Summary
    print(f"\n{'='*60}")
    print(f"ERRORS: {len(total_errors)}   WARNINGS: {total_warnings}")
    if total_errors:
        print("VALIDATION FAILED")
        sys.exit(1)
    elif total_warnings:
        print("VALIDATION PASSED WITH WARNINGS (review attribution items above)")
    else:
        print("VALIDATION PASSED")


if __name__ == "__main__":
    main()
