"""Compute co-occurrence matrix: which parameters are detected together across boreholes.

For each pair (param_a, param_b), count how many boreholes detect both.
High co-occurrence suggests shared source or linked process.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations


@dataclass
class CoOccurrenceResult:
    detected_per_borehole: dict[str, list[str]]   # borehole_id → [detected param codes]
    co_occurrence_counts: dict[tuple[str, str], int]  # (param_a, param_b) → n_boreholes
    top_pairs: list[tuple[str, str, int]] = field(default_factory=list)


def compute_co_occurrence(
    detection_map: dict[str, dict[str, float]],  # borehole_id → {param: max_conc}
    min_count: int = 2,
) -> CoOccurrenceResult:
    """
    detection_map: {borehole_id: {param_code: max_nonzero_concentration}}
    Returns co-occurrence counts for pairs detected in ≥ min_count boreholes.
    """
    detected_per_borehole: dict[str, list[str]] = {}
    for bh_id, detections in detection_map.items():
        detected = [code for code, conc in detections.items() if conc > 0]
        detected_per_borehole[bh_id] = detected

    co_counts: dict[tuple[str, str], int] = {}
    for bh_id, detected in detected_per_borehole.items():
        for a, b in combinations(sorted(set(detected)), 2):
            key = (a, b)
            co_counts[key] = co_counts.get(key, 0) + 1

    top_pairs = sorted(
        [(a, b, cnt) for (a, b), cnt in co_counts.items() if cnt >= min_count],
        key=lambda x: -x[2],
    )

    return CoOccurrenceResult(
        detected_per_borehole=detected_per_borehole,
        co_occurrence_counts=co_counts,
        top_pairs=top_pairs,
    )
