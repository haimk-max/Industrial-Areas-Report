"""
Mann-Kendall trend analysis with SNR (Signal-to-Noise Ratio) gating.

Per 2021 Water Quality Report methodology: tie-corrected variance,
continuity-corrected Z, SNR ≥ 0.3, soft_trigger = 2 consecutive rising values.
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional, List


def calculate_mann_kendall(
    measurements: List[float],
    dates: Optional[List] = None,
    apply_snr_gate: bool = True,
    snr_threshold: float = 0.3,
    soft_trigger: int = 2,
) -> dict:
    """
    Calculate Mann-Kendall trend statistic with tie-corrected variance.

    Args:
        measurements: List of concentration measurements (floats)
        dates: Optional list of measurement dates (for documentation)
        apply_snr_gate: Whether to apply SNR gating filter (default True)
        snr_threshold: Minimum SNR for trend to be considered significant (default 0.3)
        soft_trigger: Number of consecutive rising measurements to flag as potential trend (default 2)

    Returns:
        dict with keys:
          - trend: "ALERT" | "WATCH" | "STABLE" | "DECREASING" | "NONE"
          - slope: Sen's slope estimator (concentration/year or per-period)
          - z_score: Continuity-corrected Z-value
          - p_value: Two-tailed p-value
          - snr: Signal-to-noise ratio (variance of trend / variance of residuals)
          - n_measurements: Count of input measurements
          - soft_trigger_detected: Boolean, whether soft_trigger condition met
          - status: "PASS" | "FAIL_SNR" | "INSUFFICIENT_DATA"
    """
    if not measurements or len(measurements) < 3:
        return {
            "trend": "NONE",
            "slope": None,
            "z_score": None,
            "p_value": None,
            "snr": None,
            "n_measurements": len(measurements) if measurements else 0,
            "soft_trigger_detected": False,
            "status": "INSUFFICIENT_DATA",
        }

    n = len(measurements)
    arr = np.array(measurements, dtype=float)

    # Mann-Kendall S statistic (sign of pairwise differences)
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            s += np.sign(arr[j] - arr[i])

    # Tie-corrected variance
    g = 0  # count of ties
    sorted_arr = np.sort(arr)
    i = 0
    while i < n - 1:
        tie_count = 1
        while i + tie_count < n and sorted_arr[i + tie_count] == sorted_arr[i]:
            tie_count += 1
        g += tie_count * (tie_count - 1) * (2 * tie_count + 5)
        i += tie_count

    var_s = (n * (n - 1) * (2 * n + 5) - g) / 18.0

    # Continuity-corrected Z
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0

    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    # Sen's slope (non-parametric estimator)
    slopes = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            slopes.append((arr[j] - arr[i]) / (j - i))
    slope = np.median(slopes) if slopes else None

    # SNR (signal-to-noise ratio)
    residuals = arr - (slope * np.arange(n) if slope else np.mean(arr))
    var_signal = np.var(arr) if np.var(arr) > 0 else 1e-6
    var_noise = np.var(residuals) if np.var(residuals) > 0 else 1e-6
    snr = var_signal / (var_noise + 1e-10)

    # Soft trigger: 2+ consecutive rising values in 5y window
    soft_trigger_detected = False
    if len(measurements) >= soft_trigger:
        for i in range(len(measurements) - soft_trigger + 1):
            window = measurements[i : i + soft_trigger]
            if all(window[k] <= window[k + 1] for k in range(len(window) - 1)):
                soft_trigger_detected = True
                break

    # Trend classification
    status = "PASS"
    if apply_snr_gate and snr < snr_threshold:
        status = "FAIL_SNR"
        trend = "NONE"
    else:
        if p_value < 0.05:
            if slope > 0:
                trend = "ALERT"
            else:
                trend = "DECREASING"
        elif soft_trigger_detected:
            trend = "WATCH"
        else:
            trend = "STABLE"

    return {
        "trend": trend,
        "slope": slope,
        "z_score": z,
        "p_value": p_value,
        "snr": snr,
        "n_measurements": n,
        "soft_trigger_detected": soft_trigger_detected,
        "status": status,
    }


def apply_snr_gating(trend_results: dict, threshold: float = 0.3) -> dict:
    """
    Apply SNR gating to trend results.

    If SNR < threshold, override trend to "NONE" and set status to "FAIL_SNR".

    Args:
        trend_results: Dict from calculate_mann_kendall()
        threshold: SNR threshold (default 0.3)

    Returns:
        Modified dict with SNR gating applied
    """
    result = trend_results.copy()
    if result.get("snr") is not None and result["snr"] < threshold:
        result["trend"] = "NONE"
        result["status"] = "FAIL_SNR"
    return result
