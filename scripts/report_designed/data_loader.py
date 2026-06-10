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
# Zone-generic: pass zone name to override (default "holon" for backwards compatibility).
# The repo convention is a CAPITALIZED zone directory (holon -> Holon), so always
# capitalize when building filesystem paths.
DEFAULT_ZONE = "holon"


def _zone_dir(zone: str = DEFAULT_ZONE) -> Path:
    """Return the zone's directory (capitalized per repo convention: holon -> Holon)."""
    return REPO_ROOT / zone.capitalize()


def _workspace_for_zone(zone: str = DEFAULT_ZONE) -> Path:
    """Return workspace path for a given zone (V4 lean_workspace layout)."""
    return _zone_dir(zone) / "lean_workspace"


def _report_v4_path(zone: str = DEFAULT_ZONE) -> Path:
    """Return path to zone's V4 report (legacy, used for extraction fallback)."""
    return _zone_dir(zone) / "output" / f"{zone.upper()}_REPORT_V4.md"


LEAN_WORKSPACE = _workspace_for_zone(DEFAULT_ZONE)
REPORT_V4 = _report_v4_path(DEFAULT_ZONE)


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


def extract_narrative_sections(report_path: Path = None, zone: str = DEFAULT_ZONE) -> dict:
    """Extract key narrative sections from zone's V4 report.

    Returns dict with narrative content for template substitution.
    Terminology cleanup: 'מורש'→'היסטורי' (clearer for non-specialist readers).
    """
    if report_path is None:
        report_path = _report_v4_path(zone)
    sections = {}

    if not report_path.exists():
        return sections

    text = report_path.read_text(encoding="utf-8")

    # V4.2: masthead intro = §1.1 רקע והיקף content (between "### 1.1 רקע והיקף" and next "### 1.2")
    # Fallback to V4.1 patterns
    match = re.search(r"### 1\.1 רקע והיקף\n\n(.+?)\n\n### 1\.2", text, re.DOTALL)
    if not match:
        match = re.search(r"## 1\. תקציר מנהלים\n\n(.+?)\n\n\*\*(ממצאים עיקריים|ארבעה)", text, re.DOTALL)
    if match:
        sections["masthead_intro"] = _clarify_terms(match.group(1).strip())

    # V4.2: contamination foci = §1.2 table (between "### 1.2 חמשת מוקדי" and next "### 1.3")
    match = re.search(r"### 1\.2 חמשת מוקדי הזיהום המרכזיים\n\n(.+?)\n\n### 1\.3", text, re.DOTALL)
    if not match:
        # Fallback to V4.1 numbered list patterns
        match = re.search(r"\*\*ממצאים עיקריים:\*\*\n\n(.+?)\n\n(?:מבין|\*\*הסיפור|על פי דוח)", text, re.DOTALL)
        if not match:
            match = re.search(r"\*\*ארבעה מוקדי זיהום.+?\n\n(.+?)\n\n\*\*הסיפור העדכני", text, re.DOTALL)
    if match:
        foci = _clarify_terms(match.group(1).strip())
        # Only apply reorder for old numbered-list format, not for new table format
        if not foci.startswith("|"):
            foci = _reorder_foci_fuel_last(foci)
        sections["four_foci"] = foci

    # V4.2: operative conclusion = §1.8 (between "### 1.8" and next "---")
    match = re.search(r"### 1\.8 מסקנה אופרטיבית\n\n(.+?)\n\n---", text, re.DOTALL)
    if not match:
        match = re.search(r"\*\*הסיפור העדכני\*\*:(.+?)\n\n---", text, re.DOTALL)
    if not match:
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


def extract_report_boreholes(report_path: Path = None, severity_df: pd.DataFrame = None, zone: str = DEFAULT_ZONE) -> list:
    """Extract canonical_ids of boreholes explicitly mentioned in zone's V4 report.

    Used to drive `boreholes_override` in svg_charts.py — Opus picks which
    boreholes to illustrate (via mentions in the narrative); the chart engine
    just renders them per style guide. See PROCESS_GUIDE §VIII.1.

    Match strategy: scan V4 report for each name_he from severity_df.
    Returns canonical_ids in the order they first appear (de-duplicated).

    Args:
        report_path: override path to V4 report; auto-detected if None
        severity_df: DataFrame with columns 'borehole' (canonical_id), 'name_he'
        zone: zone name (used to auto-detect report path if report_path is None)

    Returns:
        Ordered list of canonical_ids mentioned in report, or [] if file/df missing.
    """
    if report_path is None:
        report_path = _report_v4_path(zone)
    if not report_path.exists() or severity_df is None or severity_df.empty:
        return []

    text = report_path.read_text(encoding="utf-8")

    # Build (first_position, canonical_id) pairs for ordered, de-duplicated output
    seen = {}
    for _, row in severity_df.iterrows():
        name_he = str(row.get("name_he", "")).strip()
        canonical_id = str(row.get("borehole", "")).strip()
        if not name_he or not canonical_id or canonical_id in seen:
            continue
        pos = text.find(name_he)
        if pos >= 0:
            seen[canonical_id] = pos

    return [cid for cid, _ in sorted(seen.items(), key=lambda kv: kv[1])]


def load_measurements_alert(zone: str = DEFAULT_ZONE, workspace: Path = None) -> pd.DataFrame:
    """Load ALERT measurements (25 boreholes, 4 families, 2,672 rows)."""
    if workspace is None:
        workspace = _workspace_for_zone(zone)
    path = workspace / "02_data_filtered" / "measurements_alert.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_trends_alert(zone: str = DEFAULT_ZONE, workspace: Path = None) -> pd.DataFrame:
    """Load ALERT trends (Mann-Kendall analysis, 357 rows)."""
    if workspace is None:
        workspace = _workspace_for_zone(zone)
    path = workspace / "02_data_filtered" / "trends_alert.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_severity_index(zone: str = DEFAULT_ZONE, workspace: Path = None) -> pd.DataFrame:
    """Load pre-computed severity index (159 borehole × family pairs, bucket 0-8)."""
    if workspace is None:
        workspace = _workspace_for_zone(zone)
    path = workspace / "04_deterministic_anchors" / "severity_index_2025_holon.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_param_level_severity(zone: str = DEFAULT_ZONE, workspace: Path = None) -> pd.DataFrame:
    """Load parameter-level severity (per borehole × param, with concentration + DWS)."""
    if workspace is None:
        workspace = _workspace_for_zone(zone)
    path = workspace / "04_deterministic_anchors" / "severity_index_2025_holon_param_level.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_alert_boreholes(zone: str = DEFAULT_ZONE, workspace: Path = None) -> pd.DataFrame:
    """Load 25 ALERT borehole IDs with alert criteria."""
    if workspace is None:
        workspace = _workspace_for_zone(zone)
    path = workspace / "02_data_filtered" / "alert_boreholes.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_data_availability(zone: str = DEFAULT_ZONE, workspace: Path = None) -> pd.DataFrame:
    """Load data availability index (monitoring gaps, stopped wells)."""
    if workspace is None:
        workspace = _workspace_for_zone(zone)
    path = workspace / "03_evidence_index" / "data_availability_index.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_latest_per_borehole(zone: str = DEFAULT_ZONE, workspace: Path = None) -> pd.DataFrame:
    """Load latest measurement per (borehole, param) pair."""
    if workspace is None:
        workspace = _workspace_for_zone(zone)
    path = workspace / "03_evidence_index" / "latest_per_borehole_param.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_max_since_2018(zone: str = DEFAULT_ZONE, workspace: Path = None) -> pd.DataFrame:
    """Load max concentration since 2018 per (borehole, param)."""
    if workspace is None:
        workspace = _workspace_for_zone(zone)
    path = workspace / "03_evidence_index" / "max_since_2018_index.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_borehole_classification(zone: str = DEFAULT_ZONE, workspace: Path = None) -> pd.DataFrame:
    """Load borehole classification for all boreholes (2021-2026 recent data)."""
    if workspace is None:
        workspace = _workspace_for_zone(zone)
    path = workspace / "04_deterministic_anchors" / "borehole_classification_all.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def get_alert_count(zone: str = DEFAULT_ZONE, trends: pd.DataFrame = None) -> int:
    """Get count of ALERT wells from trends_alert."""
    if trends is None:
        trends = load_trends_alert(zone=zone)

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
