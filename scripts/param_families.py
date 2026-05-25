"""Cross-zone parameter family classifier.

Different zones' Excel files use different naming conventions for the same
contaminants — short codes (TCEY, PCE) vs full names (TRICHLORO ETHYLENE).
This module classifies parameters into canonical contaminant families using
regex patterns that match common variants across all zones.

Families (per DATA_PIPELINE_SPEC.md §3):
  CVOC  — chlorinated volatile organic compounds (TCE, PCE, DCE, VC, etc.)
  METALS  — heavy metals (Chromium, Lead, Nickel, etc.)
  PFAS  — perfluoroalkyl substances (PFOS, PFOA, PFHxS, etc.)
  FUEL  — petroleum hydrocarbons & BTEX (benzene, toluene, xylene, MTBE, naphthalene, etc.)
  OTHER — anything not matching the above families
"""
from __future__ import annotations

import re

# Patterns are matched case-insensitively against `param_code` AND `param_name`.
# Order matters slightly only for performance — first match wins.
_FAMILY_PATTERNS = {
    "CVOC": re.compile(
        r"(?:TRICHLORO|PERCHLORO|TETRACHLORO|DICHLORO|MONOCHLORO|"
        r"CHLOROFORM|CHLOROETH|CHLOROMETH|VINYL\s*CHLORIDE|"
        r"CARBON\s*TETRACHLORIDE|METHYLENE\s*CHLORIDE|"
        r"\bTCE\b|\bPCE\b|\bDCE\b|\bVC\b|\bDCA\b|"
        r"\bTCEY\b|\bCHLF\b|\bCCLA\b|\bTCAM\b|\bCHCL3\b|"
        r"CIS.*DICHLOR|TRANS.*DICHLOR|TETRACHLOR\s*ETHANE|TRICHLOR\s*ETHANE|"
        r"1,4\s*DIOXANE)",
        re.IGNORECASE,
    ),
    "METALS": re.compile(
        r"(?:CHROMIUM|CHROME|\bCR\(VI\)|\bCR\b|NICKEL|CADMIUM|COPPER|"
        r"LEAD|\bPB\b|IRON|MANGANESE|\bMN\b|ARSENIC|BARIUM|SELENIUM|ZINC|"
        r"\bNI\b|\bCD\b|\bCU\b|\bAS\b|\bBA\b|\bSE\b|\bZN\b|\bFE\b)",
        re.IGNORECASE,
    ),
    "PFAS": re.compile(
        r"(?:PFAS|PFOS|PFOA|PFHX|PFBA|PFBS|PFNA|PFDA|PFEESA|"
        r"PER[-\s]?FLUORO|PERFLUORO|PFOSA|PFHpA|PFPeA)",
        re.IGNORECASE,
    ),
    "FUEL": re.compile(
        r"(?:BTEX|\bBENZENE\b|TOLUENE|XYLENE|ETHYL\s*BENZENE|ETHYLBENZENE|"
        r"MTBE|METHYL\s*TERT|STYRENE|NAPHTHALENE|NAPTHALENE|"
        r"METHYLBENZENE|ETHYLBENZENE|PROPYLBENZENE|BUTYLBENZENE|"
        r"TRIMETHYLBENZENE|ALKYLBENZENE|CHLOROTOLUENE|CHLOROBENZENE|"
        r"DIMETHYLBENZENE|ISOPROPYL\s*BENZENE|\bo-Xylene\b|\bp-xylene\b|\bm-xylene\b|"
        r"\bETHYLB\b|\bMXYL\b|\bPXYL\b|\bOXYL\b|"
        r"ETHYLENE\s*DI\s*BROMIDE|DIBROMO|TRIBROMO|DIBROMOCHLORO)",
        re.IGNORECASE,
    ),
}


def classify_family(param_code: str | None, param_name: str | None = None) -> str:
    """Classify a parameter into CVOC / METALS / PFAS / FUEL / OTHER.

    Checks param_code first, then param_name. Returns "OTHER" if no match
    or if both inputs are empty/None.
    """
    fields = [str(f) for f in (param_code, param_name) if f]
    if not fields:
        return "OTHER"
    text = " | ".join(fields)
    for family, pattern in _FAMILY_PATTERNS.items():
        if pattern.search(text):
            return family
    return "OTHER"


def is_cvoc(param_code: str | None, param_name: str | None = None) -> bool:
    return classify_family(param_code, param_name) == "CVOC"


def is_metals(param_code: str | None, param_name: str | None = None) -> bool:
    return classify_family(param_code, param_name) == "METALS"


def is_pfas(param_code: str | None, param_name: str | None = None) -> bool:
    return classify_family(param_code, param_name) == "PFAS"


def is_fuel(param_code: str | None, param_name: str | None = None) -> bool:
    return classify_family(param_code, param_name) == "FUEL"
