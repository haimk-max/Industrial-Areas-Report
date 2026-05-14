"""Data loading and narrative extraction for designed Holon V4 report.

Reads directly from Holon/lean_workspace/ (V4 evidence base):
  - 02_data_filtered/measurements_alert.csv (2,672 rows, 25 ALERT boreholes)
  - 02_data_filtered/trends_alert.csv (357 rows, Mann-Kendall stats)
  - 04_deterministic_anchors/severity_index_2025_holon.csv (159 rows, pre-computed)
  - 03_evidence_index/ (data availability, latest, max since 2018)
  - 02_data_filtered/facility_candidates_holon.md (60 candidates, 17 HIGH)
  - 01_inputs/previous_reports/ (5 historical PDFs as MD)

Narrative extracted directly from HOLON_REPORT_V4.md.
"""

from pathlib import Path
import pandas as pd
import re


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LEAN_WORKSPACE = REPO_ROOT / "Holon" / "lean_workspace"
REPORT_V4 = REPO_ROOT / "Holon" / "output" / "HOLON_REPORT_V4.md"


def _clarify_terms(text: str) -> str:
    """Replace ambiguous Hebrew terminology with clearer phrasing.

    'מורש' (legacy/inherited) — opaque to non-domain readers; replace with 'היסטורי' (historic).
    Applied to all extracted narrative so wording stays consistent.
    """
    if not text:
        return text
    # Match 'מורש' as a whole word (with optional Hebrew prefix letters ה/ב/ל/כ/מ/ש/ו)
    # so we don't accidentally hit 'מורשת' (heritage — different meaning).
    text = re.sub(r"(?<![א-ת])([הבלכמשו]?)מורש(?![א-ת])", r"\1היסטורי", text)
    return text


def _reorder_foci_fuel_last(four_foci_md: str) -> str:
    """Move the FUEL focus block to the end and renumber 1..N.

    The four_foci block is markdown with numbered items '1. **...** ... 2. **...**'
    each item possibly containing sub-bullets. Source V4 has FUEL at position #2;
    this function reorders so any block whose header mentions 'דלקים' (fuel) is last,
    matching the convention of presenting fuel after CVOC/metals.
    """
    if not four_foci_md:
        return four_foci_md

    # Split by top-level numbered items (line that starts with 'N. **')
    blocks = re.split(r"\n(?=\d+\.\s\*\*)", four_foci_md.strip())
    if len(blocks) < 2:
        return four_foci_md

    # Drop the leading number from each block
    cleaned = []
    for b in blocks:
        cleaned.append(re.sub(r"^\d+\.\s+", "", b.strip()))

    # Move fuel blocks to the end (preserve relative order of non-fuel)
    fuel_idx = [i for i, b in enumerate(cleaned)
                if b.startswith("**") and "דלקים" in b.split("\n", 1)[0]]
    non_fuel = [b for i, b in enumerate(cleaned) if i not in fuel_idx]
    fuel = [cleaned[i] for i in fuel_idx]
    reordered = non_fuel + fuel

    # Renumber
    return "\n\n".join(f"{i+1}. {b}" for i, b in enumerate(reordered))


def extract_narrative_sections(report_path: Path = REPORT_V4) -> dict:
    """Extract key narrative sections from HOLON_REPORT_V4.md.

    Returns dict with narrative content for template substitution.
    Terminology cleanup: 'מורש'→'היסטורי' (clearer for non-specialist readers).
    """
    sections = {}

    if not report_path.exists():
        return sections

    text = report_path.read_text(encoding="utf-8")

    # V4.1: masthead intro = first paragraph after "## 1. תקציר מנהלים" before "**ממצאים"
    # Fallback to V4 marker "**ארבעה" if needed
    match = re.search(r"## 1\. תקציר מנהלים\n\n(.+?)\n\n\*\*(ממצאים עיקריים|ארבעה)", text, re.DOTALL)
    if match:
        sections["masthead_intro"] = _clarify_terms(match.group(1).strip())

    # V4.1: findings list = numbered items after "**ממצאים עיקריים:**" until next "---" or "##"
    # Fallback to V4 marker "**ארבעה מוקדי זיהום"
    match = re.search(r"\*\*ממצאים עיקריים:\*\*\n\n(.+?)\n\n(?:מבין|\*\*הסיפור|על פי דוח)", text, re.DOTALL)
    if not match:
        match = re.search(r"\*\*ארבעה מוקדי זיהום.+?\n\n(.+?)\n\n\*\*הסיפור העדכני", text, re.DOTALL)
    if match:
        foci = _clarify_terms(match.group(1).strip())
        sections["four_foci"] = _reorder_foci_fuel_last(foci)

    # V4.1: closing summary paragraph of section 1 (between findings and ---)
    # Fallback to V4 marker "**הסיפור העדכני**:"
    match = re.search(r"\*\*הסיפור העדכני\*\*:(.+?)\n\n---", text, re.DOTALL)
    if not match:
        # V4.1 closing: paragraph(s) after findings list, before ## 2
        match = re.search(r"\n\n(מבין .+?|על פי דוח .+?)\n\n---\n\n## 2\.", text, re.DOTALL)
    if match:
        sections["current_story"] = _clarify_terms(match.group(1).strip())

    # Extract classification definitions from section 8
    match = re.search(r"## 8\. סיווג קידוחים.+?\n\n### הגדרת קטגוריות(.+?)\n\n### סטטיסטיקת", text, re.DOTALL)
    if match:
        sections["classification_intro"] = match.group(1).strip()

    match = re.search(r"### סטטיסטיקת התפלגות.+?\n\n(.+?)\n\n### התפלגות לפי משפחות", text, re.DOTALL)
    if match:
        sections["classification_stats"] = match.group(1).strip()

    return sections


def load_measurements_alert(workspace: Path = LEAN_WORKSPACE) -> pd.DataFrame:
    """Load ALERT measurements (25 boreholes, 4 families, 2,672 rows)."""
    path = workspace / "02_data_filtered" / "measurements_alert.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_trends_alert(workspace: Path = LEAN_WORKSPACE) -> pd.DataFrame:
    """Load ALERT trends (Mann-Kendall analysis, 357 rows)."""
    path = workspace / "02_data_filtered" / "trends_alert.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_severity_index(workspace: Path = LEAN_WORKSPACE) -> pd.DataFrame:
    """Load pre-computed severity index (159 borehole × family pairs, bucket 0-8)."""
    path = workspace / "04_deterministic_anchors" / "severity_index_2025_holon.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_param_level_severity(workspace: Path = LEAN_WORKSPACE) -> pd.DataFrame:
    """Load parameter-level severity (per borehole × param, with concentration + DWS)."""
    path = workspace / "04_deterministic_anchors" / "severity_index_2025_holon_param_level.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_alert_boreholes(workspace: Path = LEAN_WORKSPACE) -> pd.DataFrame:
    """Load 25 ALERT borehole IDs with alert criteria."""
    path = workspace / "02_data_filtered" / "alert_boreholes.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_data_availability(workspace: Path = LEAN_WORKSPACE) -> pd.DataFrame:
    """Load data availability index (monitoring gaps, stopped wells)."""
    path = workspace / "03_evidence_index" / "data_availability_index.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_latest_per_borehole(workspace: Path = LEAN_WORKSPACE) -> pd.DataFrame:
    """Load latest measurement per (borehole, param) pair."""
    path = workspace / "03_evidence_index" / "latest_per_borehole_param.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_max_since_2018(workspace: Path = LEAN_WORKSPACE) -> pd.DataFrame:
    """Load max concentration since 2018 per (borehole, param)."""
    path = workspace / "03_evidence_index" / "max_since_2018_index.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_borehole_classification(workspace: Path = LEAN_WORKSPACE) -> pd.DataFrame:
    """Load borehole classification for all boreholes (2021-2026 recent data)."""
    path = workspace / "04_deterministic_anchors" / "borehole_classification_all.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def get_alert_count(trends: pd.DataFrame = None) -> int:
    """Get count of ALERT wells from trends_alert."""
    if trends is None:
        trends = load_trends_alert()

    if trends.empty:
        return 0

    alert_ids = set()

    # INCREASING + crossed standard
    inc = trends[
        (trends.get("classification") == "INCREASING") &
        (trends.get("crossed_standard") == True)
    ]
    for _, row in inc.iterrows():
        alert_ids.add(row.get("borehole_id"))

    return len(alert_ids)


def esc(text: str) -> str:
    """XML escape for Hebrew text."""
    if not isinstance(text, str):
        return str(text)
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;"))
