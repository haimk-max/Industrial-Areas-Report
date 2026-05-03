"""Coordinate normalization to Israeli Transverse Mercator (EPSG:2039).

Handles different formats found across data sources:
- TAHAL 2008: ITM in meters (e.g., 191392, 707257)
- Excel water quality: appears as km*1000 truncated (e.g., 187.951, 677.569)
- Report 2021: ITM in meters

All outputs in EPSG:2039 meters.
"""
from __future__ import annotations


def normalize_to_itm(easting: float, northing: float, source: str) -> tuple[float, float]:
    """Convert raw coordinates to ITM (EPSG:2039) meters.

    Args:
        easting, northing: raw coordinate values from the source
        source: one of "tahal_2008", "report_2021", "excel"

    Returns:
        (easting_m, northing_m) in EPSG:2039
    """
    if source in ("tahal_2008", "report_2021"):
        return float(easting), float(northing)

    if source == "excel":
        # Excel format: km truncated with 3-digit decimal (e.g., 187.951 → 187951 m)
        # Northing similarly: 677.569 → 677569 m, but ITM northing is 6-7 digits
        # so this is a 6-digit ITM coordinate where the prefix digit is dropped.
        # Standard Israeli ITM range: easting 100000-300000, northing 400000-800000.
        e = float(easting) * 1000.0
        n = float(northing) * 1000.0
        return e, n

    raise ValueError(f"Unknown coordinate source: {source!r}")


def is_in_itm_bounds(easting: float, northing: float) -> bool:
    """Sanity check that coordinates fall within Israel's ITM grid."""
    return 100_000 <= easting <= 300_000 and 400_000 <= northing <= 800_000
