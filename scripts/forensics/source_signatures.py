"""Match borehole contamination profiles to known source signatures.

Signatures:
  AFFF_foam    — PFAS with S-chain dominance (PFOS, PFHxS high ratio)
  Industrial_PFAS — PFAS with A-chain dominance (PFOA, PFHxA dominant)
  Fuel_station — BTEX present (benzene lead), MTBE confirms
  CVOC_industry — chlorinated solvents (PCE/TCE family)
  Mixed        — multiple signatures co-occurring
"""
from __future__ import annotations

from dataclasses import dataclass, field

PFAS_S_CODES = {"PFOS", "PFBS", "PFHxS", "PFHpS", "PFDS", "6:2FT", "82FTS", "FOSA"}
PFAS_A_CODES = {"PFOA", "PFHxA", "PFHpA", "PFNA", "PFDA", "PFDoA", "PFUnA",
                "PFBA", "PFPeA", "PFESA", "ADONA"}
BTEX_CODES   = {"BENZ", "TOLU", "ETBN", "XYLE", "OXYL", "PXYL"}
CVOC_CODES   = {"TECE", "TCEY", "CDCE", "TDCE", "DCEY", "VYCL", "CCL4", "DCET", "DCET1",
                "TCET", "TCEN", "DCLM"}
THM_CODES    = {"CHLF", "DCBM", "DBRMT", "TRBRM"}
FUEL_CODES   = {"MTBE", "MOL", "TPH"}


@dataclass
class SignatureMatch:
    signature: str
    confidence: str          # HIGH | MEDIUM | LOW
    detected_indicators: list[str] = field(default_factory=list)
    dominant_compound: str | None = None
    max_concentration: float | None = None
    notes: str = ""


def match_source_signatures(
    borehole_id: str,
    latest_detections: dict[str, float],  # param_code → max non-zero concentration
) -> list[SignatureMatch]:
    matches = []

    pfas_s = {c: latest_detections[c] for c in PFAS_S_CODES if latest_detections.get(c, 0) > 0}
    pfas_a = {c: latest_detections[c] for c in PFAS_A_CODES if latest_detections.get(c, 0) > 0}
    btex = {c: latest_detections[c] for c in BTEX_CODES if latest_detections.get(c, 0) > 0}
    cvoc = {c: latest_detections[c] for c in CVOC_CODES if latest_detections.get(c, 0) > 0}
    fuel_other = {c: latest_detections[c] for c in FUEL_CODES if latest_detections.get(c, 0) > 0}

    # ── PFAS ─────────────────────────────────────────────────────────────────
    if pfas_s or pfas_a:
        total_s = sum(pfas_s.values())
        total_a = sum(pfas_a.values())
        all_pfas = {**pfas_s, **pfas_a}
        dominant = max(all_pfas, key=all_pfas.get)
        if total_s > total_a * 2:
            sig = "AFFF_foam"
            note = "Sulfonate-chain PFAS dominates — consistent with AFFF firefighting foam"
            conf = "HIGH" if len(pfas_s) >= 2 else "MEDIUM"
        elif total_a > total_s * 2:
            sig = "Industrial_PFAS"
            note = "Carboxylate-chain PFAS dominates — consistent with industrial fluorochemical use"
            conf = "HIGH" if len(pfas_a) >= 2 else "MEDIUM"
        else:
            sig = "Mixed_PFAS"
            note = "Mixed S/A PFAS profile — source unclear (AFFF + industrial or industrial fluorinated)"
            conf = "MEDIUM"
        matches.append(SignatureMatch(
            signature=sig, confidence=conf,
            detected_indicators=list(all_pfas.keys()),
            dominant_compound=dominant,
            max_concentration=max(all_pfas.values()),
            notes=note,
        ))

    # ── Fuel (BTEX + MTBE) ────────────────────────────────────────────────────
    if btex:
        dominant = max(btex, key=btex.get)
        has_mtbe = "MTBE" in fuel_other
        note = "BTEX contamination"
        if has_mtbe:
            note += " with MTBE — confirms fuel station source (gasoline)"
        matches.append(SignatureMatch(
            signature="Fuel_station",
            confidence="HIGH" if has_mtbe else "MEDIUM",
            detected_indicators=list(btex.keys()) + (["MTBE"] if has_mtbe else []),
            dominant_compound=dominant,
            max_concentration=max(btex.values()),
            notes=note,
        ))

    # ── CVOC ─────────────────────────────────────────────────────────────────
    if cvoc:
        dominant = max(cvoc, key=cvoc.get)
        matches.append(SignatureMatch(
            signature="CVOC_industry",
            confidence="HIGH" if len(cvoc) >= 3 else "MEDIUM",
            detected_indicators=list(cvoc.keys()),
            dominant_compound=dominant,
            max_concentration=max(cvoc.values()),
            notes="Chlorinated solvent contamination — likely industrial degreasing/dry cleaning source",
        ))

    # ── THM ──────────────────────────────────────────────────────────────────
    thm = {c: latest_detections[c] for c in THM_CODES if latest_detections.get(c, 0) > 0}
    if thm:
        matches.append(SignatureMatch(
            signature="THM_disinfection_byproduct",
            confidence="MEDIUM",
            detected_indicators=list(thm.keys()),
            dominant_compound=max(thm, key=thm.get),
            max_concentration=max(thm.values()),
            notes="Trihalomethanes — likely disinfection byproducts from treated water",
        ))

    return matches
