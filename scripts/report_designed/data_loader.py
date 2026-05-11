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


def extract_narrative_sections(report_path: Path = REPORT_V4) -> dict:
    """Extract key narrative sections from HOLON_REPORT_V4.md.

    Returns dict with narrative content for template substitution.
    """
    sections = {}

    if not report_path.exists():
        return sections

    text = report_path.read_text(encoding="utf-8")

    # Executive summary intro (first paragraph)
    match = re.search(r"## 1\. תקציר מנהלים\n\n(.+?)\n\n\*\*ארבעה", text, re.DOTALL)
    if match:
        sections["masthead_intro"] = match.group(1).strip()

    # Four contamination foci
    match = re.search(r"\*\*ארבעה מוקדי זיהום.+?\n\n(.+?)\n\n\*\*הסיפור העדכני", text, re.DOTALL)
    if match:
        sections["four_foci"] = match.group(1).strip()

    # Current situation summary
    match = re.search(r"\*\*הסיפור העדכני\*\*:(.+?)\n\n---", text, re.DOTALL)
    if match:
        sections["current_story"] = match.group(1).strip()

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
