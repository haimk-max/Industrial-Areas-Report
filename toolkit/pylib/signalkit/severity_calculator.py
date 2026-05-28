"""
Severity index calculation per 2021 Water Quality Report methodology.

Bucket classification: bucket(C_max_5y / DWS × 100)
Scale: 0–8 (9 levels)
"""

import numpy as np
from typing import Optional, Tuple


BUCKET_THRESHOLDS = [
    (0, 25),
    (25, 50),
    (50, 100),
    (100, 150),
    (150, 200),
    (200, 500),
    (500, 1000),
    (1000, 10000),
    (10000, float('inf')),
]

BUCKET_LABELS = {
    0: "Clean (0–25%)",
    1: "Low (25–50%)",
    2: "Moderate (50–100%)",
    3: "Elevated (100–150%)",
    4: "High (150–200%)",
    5: "Very High (200–500%)",
    6: "Critical (500–1,000%)",
    7: "Severe (1,000–10,000%)",
    8: "Extreme (>10,000%)",
}

BUCKET_COLORS = {
    0: "#f0ede6",  # light grey
    1: "#f0ede6",  # light grey
    2: "#d8d3c8",  # light-medium grey
    3: "#cfcfcf",  # medium grey
    4: "#a8a29a",  # medium-dark grey
    5: "#5a564f",  # dark grey
    6: "#5a564f",  # dark grey
    7: "#a82a1c",  # red
    8: "#a82a1c",  # red
}


def calculate_bucket(
    c_max_5y: float,
    dws: float,
) -> int:
    """
    Calculate severity bucket from max concentration in 5y and drinking water standard.

    Args:
        c_max_5y: Maximum concentration in past 5 years (ppb, µg/L, etc.)
        dws: Drinking water standard (same units as c_max_5y)

    Returns:
        int: Bucket index 0–8
    """
    if dws <= 0:
        return 0  # Invalid DWS → bucket 0 (clean)

    if c_max_5y < 0:
        return 0  # Negative concentration → bucket 0

    percentage = (c_max_5y / dws) * 100

    for bucket_idx, (lower, upper) in enumerate(BUCKET_THRESHOLDS):
        if lower <= percentage < upper:
            return bucket_idx

    return 8  # Fallback to highest bucket


def classify_severity(bucket: int) -> dict:
    """
    Classify severity level by bucket.

    Args:
        bucket: Bucket index 0–8

    Returns:
        dict with keys:
          - label: Human-readable label (e.g., "Critical (500–1,000%)")
          - color: CSS color code
          - risk_level: "CLEAN" | "LOW" | "MODERATE" | "ELEVATED" | "HIGH" | "CRITICAL" | "SEVERE"
          - recommended_action: Action string
    """
    if bucket not in BUCKET_LABELS:
        bucket = 8  # Fallback

    risk_levels = ["CLEAN", "LOW", "LOW", "MODERATE", "ELEVATED", "HIGH", "CRITICAL", "SEVERE", "CRITICAL"]
    action_levels = [
        "Monitor per standard schedule",
        "Monitor per standard schedule",
        "Monitor increased frequency",
        "Detailed investigation recommended",
        "Immediate detailed investigation",
        "Urgent investigation + remediation planning",
        "Urgent investigation + remediation planning",
        "Emergency response + source containment",
        "Emergency response + source containment",
    ]

    return {
        "label": BUCKET_LABELS[bucket],
        "color": BUCKET_COLORS[bucket],
        "risk_level": risk_levels[bucket],
        "recommended_action": action_levels[bucket],
    }


def batch_calculate_buckets(
    measurements_df,
    c_max_col: str = "c_max_5y",
    dws_col: str = "dws",
) -> np.ndarray:
    """
    Batch calculate buckets for DataFrame (used in trend analysis pipelines).

    Args:
        measurements_df: pandas DataFrame with c_max_col and dws_col
        c_max_col: Column name for max concentration
        dws_col: Column name for drinking water standard

    Returns:
        numpy array of bucket indices
    """
    try:
        import pandas as pd
        buckets = measurements_df.apply(
            lambda row: calculate_bucket(row[c_max_col], row[dws_col]),
            axis=1,
        )
        return buckets.values
    except ImportError:
        raise ImportError("pandas is required for batch_calculate_buckets()")
