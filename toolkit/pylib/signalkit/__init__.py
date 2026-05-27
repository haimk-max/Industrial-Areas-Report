"""
signalkit — Signal analysis toolkit for groundwater quality monitoring.

Modules:
  - trend_analysis: Mann-Kendall trend detection with SNR gating
  - severity_calculator: Severity index (bucket) calculation
  - forensics_engine: Decay chains, source signatures
  - data_pipeline: CSV parsing, measurement normalization
"""

__version__ = "0.1.0"
__author__ = "Industrial Areas Report Team"

from .trend_analysis import calculate_mann_kendall, apply_snr_gating
from .severity_calculator import calculate_bucket, classify_severity
from .forensics_engine import build_decay_chains, match_source_signatures
from .data_pipeline import parse_measurements_csv, normalize_units

__all__ = [
    "calculate_mann_kendall",
    "apply_snr_gating",
    "calculate_bucket",
    "classify_severity",
    "build_decay_chains",
    "match_source_signatures",
    "parse_measurements_csv",
    "normalize_units",
]
