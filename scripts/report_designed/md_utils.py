"""Shared markdown and HTML utilities for report generators.

Functions for inline markdown processing, RTL text wrapping, and table/list parsing.
Used by both generate_holon_full_html.py and generate_holon_designed.py.
"""

import re

# ─────────────────────── Inline Markdown Processing ───────────────────────

# Pre-compiled regex patterns for inline markdown and wrapping
_RE_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_RE_CODE = re.compile(r"`([^`]+)`")
_RE_TAG = re.compile(r'<[^>]+>')
_RE_DOUBLE_BDI = re.compile(r'<bdi><bdi>([^<]+)</bdi></bdi>')


def inline(text: str) -> str:
    """Process inline markdown: **bold**, `code`.

    Note: This is called _inline in both generator files; exposed as inline here
    for clarity in the shared module.
    """
    text = _RE_BOLD.sub(r"<strong>\1</strong>", text)
    text = _RE_CODE.sub(r"<code>\1</code>", text)
    return text


# ─────────────────────── Bidirectional Text Wrapping ───────────────────────

# Pollutant names + units that must be isolated for proper RTL flow in mixed Hebrew text.
_BIDI_POLLUTANTS = (
    "TCE|PCE|MTBE|BTEX|CVOC|PFAS|PFHxS|PFOA|PFOS|PFNA|DCE|VC|DNAPL|AFFF|PVDC|"
    "DWS|NMVOC|ITM|PRTR|WMS|OSM|AFFF|SNR"
)
_BIDI_PATTERNS = [
    # Numbers + units: "27,860 µg/L", "85,000%", "8.5 mg/L"
    (re.compile(r'(\d[\d,\.]*\s*(?:µg/L|mg/L|ng/L|µS/cm|%|דונם|מ"ק|ק"ג/שנה))'), r'<bdi>\1</bdi>'),
    # Statistics: Z=2.60, p=0.009, SNR=1.32, n=5
    (re.compile(r'\b(Z=\d+\.?\d*|p=\d+\.?\d*|SNR=\d+\.?\d*|n=\d+)'), r'<bdi>\1</bdi>'),
    # Compound CVOC names with digits/commas/hyphens: 1,1-DCE, cis-1,2-DCE, 1,4-dioxane
    (re.compile(r'\b(cis-1,2-DCE|trans-1,2-DCE|1,1-DCE|1,2-DCA|1,4-[Dd]ioxane|1,1,1-TCA|CCl[₄4])'), r'<bdi>\1</bdi>'),
    # Standalone pollutant names
    (re.compile(rf'\b({_BIDI_POLLUTANTS})\b'), r'<bdi>\1</bdi>'),
    # Metal symbols: Cr, Ni, Pb, As, Fe, Al, Cd
    (re.compile(r'\b(Cr|Ni|Pb|As|Fe|Al|Cd)\b(?![<>])'), r'<bdi>\1</bdi>'),
    # Standalone years inside Hebrew text: 2012, 2026
    (re.compile(r'(?<![\d/-])\b(20\d{2})\b(?![\d/-])'), r'<bdi>\1</bdi>'),
]


def wrap_bidi(html: str) -> str:
    """Wrap LTR tokens (numbers, units, pollutants) in <bdi> for RTL flow.

    Avoids double-wrapping and skips content inside existing tags.
    """
    if not html:
        return html
    # Split into segments alternating between tag content and text content.
    # Apply bidi wrapping only to text content.
    parts = []
    last_end = 0
    for m in _RE_TAG.finditer(html):
        # Text before this tag — apply wrapping
        text_segment = html[last_end:m.start()]
        for pattern, repl in _BIDI_PATTERNS:
            text_segment = pattern.sub(repl, text_segment)
        parts.append(text_segment)
        # Tag itself — preserve as-is
        parts.append(m.group(0))
        last_end = m.end()
    # Final text segment after last tag
    text_segment = html[last_end:]
    for pattern, repl in _BIDI_PATTERNS:
        text_segment = pattern.sub(repl, text_segment)
    parts.append(text_segment)
    result = "".join(parts)
    # Prevent double wrapping if a pattern already inside <bdi>
    result = _RE_DOUBLE_BDI.sub(r'<bdi>\1</bdi>', result)
    return result
