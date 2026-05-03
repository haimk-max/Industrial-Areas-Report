"""Detect reductive dechlorination decay chains in borehole data.

Chains recognized:
  PCE → TCE → cis-1,2-DCE → vinyl chloride
  1,1,1-TCA → 1,1-DCA → 1,1-DCE

For each borehole, compute:
  - which chain members are detected
  - presence ratio (detected / total chain length)
  - daughter > parent flag (indicates active degradation)
  - confidence: HIGH (≥3 members) | MEDIUM (2 members) | LOW (1 member)
"""
from __future__ import annotations

from dataclasses import dataclass, field

CHAINS: list[tuple[str, list[str]]] = [
    ("PCE_TCE_DCE_VC", ["TECE", "TCEY", "CDCE", "TDCE", "DCEY", "VYCL"]),
    ("TCA_DCA_DCE",    ["TCET", "DCET1", "DCEY"]),
]

# Typical parent → daughter pairs to check for active reductive dechlorination
DAUGHTER_PAIRS: list[tuple[str, str]] = [
    ("TECE", "TCEY"),   # PCE → TCE
    ("TCEY", "CDCE"),   # TCE → cis-DCE
    ("TCEY", "TDCE"),   # TCE → trans-DCE
    ("CDCE", "VYCL"),   # cis-DCE → VC
    ("TCET", "DCET1"),  # 1,1,1-TCA → 1,1-DCA
    ("DCET1", "DCEY"),  # 1,1-DCA → 1,1-DCE
]


@dataclass
class ChainResult:
    borehole_id: str
    chain_name: str
    detected_members: list[str] = field(default_factory=list)
    presence_ratio: float = 0.0
    daughter_exceeds_parent: list[tuple[str, str]] = field(default_factory=list)
    confidence: str = "LOW"
    interpretation: str = ""


def analyze_decay_chains(
    borehole_id: str,
    latest_detections: dict[str, float],  # param_code → max_concentration
) -> list[ChainResult]:
    """Return chain analysis for one borehole given latest detections."""
    results = []
    for chain_name, members in CHAINS:
        detected = [m for m in members if latest_detections.get(m, 0) > 0]
        if not detected:
            continue

        ratio = len(detected) / len(members)
        confidence = "HIGH" if len(detected) >= 3 else ("MEDIUM" if len(detected) >= 2 else "LOW")

        daughter_pairs = []
        for parent, daughter in DAUGHTER_PAIRS:
            if parent in detected and daughter in detected:
                if latest_detections.get(daughter, 0) > latest_detections.get(parent, 0):
                    daughter_pairs.append((parent, daughter))

        interp = ""
        if len(detected) >= 3:
            interp = "Active reductive dechlorination likely — multiple chain members detected"
            if daughter_pairs:
                interp += "; daughter products exceed parent (ongoing degradation)"
        elif len(detected) == 2:
            interp = "Partial chain detected — possible degradation"
        else:
            interp = "Single chain member — source without degradation evidence"

        results.append(ChainResult(
            borehole_id=borehole_id,
            chain_name=chain_name,
            detected_members=detected,
            presence_ratio=round(ratio, 3),
            daughter_exceeds_parent=daughter_pairs,
            confidence=confidence,
            interpretation=interp,
        ))
    return results
