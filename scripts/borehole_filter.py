"""Helper: load `selected_boreholes.json` produced by select_boreholes.py.

Downstream scripts (trend_analysis, forensics_analyzer, generate_charts_v2)
use this to filter measurements to the boreholes relevant to the zone
(Tier 1 historical + Tier 2 polygon intersection + Tier 3 manual additions).

Returns None if the selection file does not exist — callers should treat this
as "use all boreholes" (backwards-compatible with pre-Phase 5 runs).
"""
from __future__ import annotations

import json
from pathlib import Path


def load_selected_ids(zone_dir: Path) -> set[str] | None:
    """Return canonical_ids for selected boreholes, or None if no selection file exists."""
    sel_file = zone_dir / "data" / "selected_boreholes.json"
    if not sel_file.exists():
        return None
    with open(sel_file, encoding="utf-8") as fh:
        data = json.load(fh)
    return {b["canonical_id"] for b in data.get("boreholes", [])}
