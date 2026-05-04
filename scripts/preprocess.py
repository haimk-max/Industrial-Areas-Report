"""Phase B: Statistical engine — Mann-Kendall + SNR gating + trend classification.

Implements the methodology from the water-quality-trends-dashboard project (V2 simplification):

Entry criteria:  n ≥ 4  AND  has_detection  AND  n5 ≥ 1
Mann-Kendall:    tie-corrected variance + continuity-corrected Z
                 5-year window (2020+) drives classification; full record informational
SNR gating:      ≥1.0 strong (p<0.10), 0.3–1.0 moderate (p<0.05), <0.3 → NONE
Below-LOD:       half_lod (default per config)

Classification: INCREASING | DECREASING | STABLE | NONE
trend_description: plain-language string with Mann-Kendall Z and p-value
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal

import numpy as np


Classification = Literal["INCREASING", "DECREASING", "STABLE", "NONE"]

WINDOW_5Y_START = date(2020, 1, 1)


# ── Data structures ──────────────────────────────────────────────────────────

@dataclass
class Observation:
    date: date
    concentration: float | None
    is_below_lod: bool = False
    lod: float | None = None    # limit of detection (numeric part of '<X')


@dataclass
class TrendResult:
    borehole_id: str
    parameter: str
    # Count fields
    n: int = 0
    n5: int = 0
    has_detection: bool = False
    # MK 5-year window
    mk_z_5y: float | None = None
    mk_p_5y: float | None = None
    snr_5y: float | None = None
    # MK full record (informational; also drives classification when 5y sparse)
    mk_z_full: float | None = None
    mk_p_full: float | None = None
    snr_full: float | None = None
    # Which window drove classification: "5y" | "full_record" | "none"
    analysis_mode: Literal["5y", "full_record", "none"] = "none"
    # Classification components
    classification: Classification = "NONE"
    trend_description: str = ""
    crossed_standard: bool = False
    drinking_water_standard: float | None = None
    # Config snapshot
    snr_thresholds: dict = field(default_factory=dict)


# ── Mann-Kendall implementation ───────────────────────────────────────────────

def _mk_stat(values: list[float]) -> tuple[float, float]:
    """Compute tie-corrected Mann-Kendall Z and two-tailed p-value.

    Returns (Z, p). If fewer than 3 values → (nan, nan).
    Implements: tie-corrected variance + continuity correction.
    """
    n = len(values)
    if n < 3:
        return float("nan"), float("nan")

    arr = np.array(values, dtype=float)
    # S statistic
    s = 0.0
    for i in range(n - 1):
        for j in range(i + 1, n):
            diff = arr[j] - arr[i]
            if diff > 0:
                s += 1
            elif diff < 0:
                s -= 1

    # Tie correction for variance
    # Find groups of ties
    unique, counts = np.unique(arr, return_counts=True)
    tie_sum = sum(c * (c - 1) * (2 * c + 5) for c in counts if c > 1)
    var_s = (n * (n - 1) * (2 * n + 5) - tie_sum) / 18.0

    if var_s <= 0:
        return float("nan"), float("nan")

    # Continuity correction
    if s > 0:
        z = (s - 1) / math.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / math.sqrt(var_s)
    else:
        z = 0.0

    # Two-tailed p-value from standard normal
    from scipy import stats
    p = 2 * stats.norm.sf(abs(z))
    return float(z), float(p)


def _snr(values: list[float]) -> float:
    """Signal-to-Noise Ratio: mean(abs(diff between first and last half)) / std.

    SNR ≥ 1.0 = strong, 0.3–1.0 = moderate, < 0.3 = weak.
    Returns 0.0 if std is zero or insufficient data.
    """
    if len(values) < 4:
        return 0.0
    arr = np.array(values, dtype=float)
    mid = len(arr) // 2
    signal = abs(arr[mid:].mean() - arr[:mid].mean())
    noise = arr.std(ddof=1)
    return float(signal / noise) if noise > 0 else 0.0


# ── Below-LOD treatment ───────────────────────────────────────────────────────

def _adjusted_value(obs: Observation, treatment: str = "half_lod") -> float | None:
    """Convert an observation to its 'adjusted' numeric value for statistical tests."""
    if obs.concentration is not None and not obs.is_below_lod:
        return obs.concentration
    # Below-LOD
    if treatment == "half_lod":
        if obs.lod is not None:
            return obs.lod / 2
        if obs.concentration is not None:
            return obs.concentration / 2
        return 0.0
    if treatment == "zero":
        return 0.0
    if treatment == "lod":
        return obs.lod or obs.concentration or 0.0
    # omit: return None
    return None


# ── Main analysis function ────────────────────────────────────────────────────

def analyze_series(
    borehole_id: str,
    parameter: str,
    observations: list[Observation],
    cfg: dict,
    drinking_water_standard: float | None = None,
) -> TrendResult:
    """Run the full trend analysis pipeline for one (borehole, parameter) series."""
    result = TrendResult(
        borehole_id=borehole_id,
        parameter=parameter,
        drinking_water_standard=drinking_water_standard,
    )

    # ── Config extraction ────────────────────────────────────────────────────
    trend_cfg = cfg.get("trend_analysis", {})
    entry_cfg = trend_cfg.get("entry_criteria", {})
    mk_cfg = trend_cfg.get("mann_kendall", {})
    snr_cfg = trend_cfg.get("snr_thresholds", {})
    lod_treatment = trend_cfg.get("below_lod", {}).get("treatment", "half_lod")
    min_n = entry_cfg.get("min_n", 4)
    min_n5 = entry_cfg.get("min_n5", 1)
    min_n5_for_mk = mk_cfg.get("min_n5_for_classification", 3)
    cfg_fallback = mk_cfg.get("full_record_fallback", False)
    min_n_for_full = mk_cfg.get("min_n_for_full_record", 3)
    window_5y_start_str = mk_cfg.get("window_5y_start", "2020-01-01")
    window_5y_start = date.fromisoformat(window_5y_start_str)
    snr_strong_min = snr_cfg.get("strong", {}).get("min_snr", 1.0)
    snr_strong_p = snr_cfg.get("strong", {}).get("mk_p_cutoff", 0.10)
    snr_moderate_min = snr_cfg.get("moderate", {}).get("min_snr", 0.3)
    snr_moderate_p = snr_cfg.get("moderate", {}).get("mk_p_cutoff", 0.05)

    result.snr_thresholds = {"strong": snr_strong_min, "moderate": snr_moderate_min}

    # ── Sort observations by date ────────────────────────────────────────────
    obs_sorted = sorted(observations, key=lambda o: o.date)
    n = len(obs_sorted)
    result.n = n

    # ── Compute adjusted values ───────────────────────────────────────────────
    adj_pairs: list[tuple[date, float]] = []
    has_detection = False
    for obs in obs_sorted:
        adj = _adjusted_value(obs, lod_treatment)
        if adj is None:
            continue
        adj_pairs.append((obs.date, adj))
        if not obs.is_below_lod and obs.concentration is not None and obs.concentration > 0:
            has_detection = True
        elif obs.is_below_lod and obs.lod is not None:
            pass  # below-LOD doesn't count as detection
    result.has_detection = has_detection

    # ── Entry criteria ────────────────────────────────────────────────────────
    idx5 = [i for i, (dt, _) in enumerate(adj_pairs) if dt >= window_5y_start]
    result.n5 = len(idx5)

    # ── Crossed standard check (always computed, regardless of entry criteria) ──
    if drinking_water_standard and drinking_water_standard > 0:
        result.crossed_standard = any(
            obs.concentration is not None and obs.concentration > drinking_water_standard
            for obs in obs_sorted
            if not obs.is_below_lod
        )

    if n < min_n or not has_detection or result.n5 < min_n5:
        result.classification = "NONE"
        return result

    adj_vals = [v for _, v in adj_pairs]

    # ── MK full record ────────────────────────────────────────────────────────
    if len(adj_vals) >= 3:
        z_full, p_full = _mk_stat(adj_vals)
        result.mk_z_full = z_full if not math.isnan(z_full) else None
        result.mk_p_full = p_full if not math.isnan(p_full) else None

    # ── MK 5-year window ─────────────────────────────────────────────────────
    vals5 = [adj_vals[i] for i in idx5]
    if result.n5 >= min_n5_for_mk:
        z5, p5 = _mk_stat(vals5)
        result.mk_z_5y = z5 if not math.isnan(z5) else None
        result.mk_p_5y = p5 if not math.isnan(p5) else None
        result.snr_5y = _snr(vals5)
    else:
        result.mk_z_5y = None
        result.mk_p_5y = None
        result.snr_5y = _snr(vals5) if vals5 else None

    # ── Select analysis window ────────────────────────────────────────────────
    use_full_record = (
        result.n5 < min_n5_for_mk
        and len(adj_vals) >= min_n_for_full
        and cfg_fallback
    )

    if result.n5 >= min_n5_for_mk:
        result.analysis_mode = "5y"
        snr = result.snr_5y or 0.0
        z_cls = result.mk_z_5y
        p_cls = result.mk_p_5y
    elif use_full_record:
        result.analysis_mode = "full_record"
        result.snr_full = _snr(adj_vals)
        snr = result.snr_full or 0.0
        z_cls = result.mk_z_full
        p_cls = result.mk_p_full
    else:
        result.analysis_mode = "none"
        result.classification = "NONE"
        result.trend_description = "Insufficient data for trend assessment"
        return result

    # ── SNR gating + classification ───────────────────────────────────────────
    if snr < snr_moderate_min:
        result.classification = "NONE"
        result.trend_description = "Insufficient signal for trend assessment (SNR below threshold)"
        return result

    # Determine significance threshold based on SNR tier
    if snr >= snr_strong_min:
        p_threshold = snr_strong_p
    else:  # moderate
        p_threshold = snr_moderate_p

    mk_significant = (z_cls is not None and p_cls is not None and p_cls <= p_threshold)
    increasing = (z_cls is not None and z_cls > 0)
    decreasing = (z_cls is not None and z_cls < 0)

    if mk_significant and increasing:
        result.classification = "INCREASING"
    elif mk_significant and decreasing:
        result.classification = "DECREASING"
    else:
        result.classification = "STABLE"

    mode_suffix = " (full record — 5-year window insufficient)" if result.analysis_mode == "full_record" else ""

    # Plain-language description with Mann-Kendall statistics
    if z_cls is not None and p_cls is not None:
        if result.classification == "INCREASING":
            result.trend_description = f"Rising trend (p={p_cls:.3f}); Mann-Kendall Z={z_cls:.2f}{mode_suffix}"
        elif result.classification == "DECREASING":
            result.trend_description = f"Declining trend (p={p_cls:.3f}); Mann-Kendall Z={z_cls:.2f}{mode_suffix}"
        else:
            result.trend_description = f"No significant trend (p={p_cls:.3f}); Mann-Kendall Z={z_cls:.2f}{mode_suffix}"
    else:
        result.trend_description = f"Insufficient data for Mann-Kendall classification{mode_suffix}"

    return result


# ── Utility: parse concentration from measurements.csv row ───────────────────

def parse_observation(
    date_str: str,
    concentration_str: str,
    is_below_lod_str: str,
    drinking_standard_str: str = "",
) -> Observation | None:
    """Parse a CSV row into an Observation. Returns None on parse failure."""
    try:
        if not date_str:
            return None
        dt = date.fromisoformat(date_str[:10])
        is_below_lod = str(is_below_lod_str).strip().lower() in ("true", "1", "yes")

        conc = None
        if concentration_str and concentration_str.strip():
            try:
                conc = float(concentration_str)
            except ValueError:
                return None

        lod = None
        if is_below_lod and conc is not None:
            lod = conc  # The recorded value IS the LOD

        return Observation(date=dt, concentration=conc, is_below_lod=is_below_lod, lod=lod)
    except (ValueError, TypeError):
        return None
