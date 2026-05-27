"""
Forensics engine for contamination pattern analysis.

Includes:
  - Decay chains (VOCs, metals, PFAS pathways)
  - Source signature matching (co-occurrence patterns)
  - Contamination family classification
"""

from typing import List, Dict, Tuple, Optional
import json


# VOC Decay Chains (chlorinated ethenes, chloromethanes, etc.)
VOC_DECAY_CHAINS = {
    "PCE_to_TCE": {
        "parent": "PCE",
        "children": ["TCE", "DCE", "VC"],
        "pathway": "reductive dechlorination",
        "description": "Tetrachloroethene degrades to trichloroethene, then dichloroethene, then vinyl chloride (carcinogen)",
    },
    "TCA_to_DCA": {
        "parent": "1,1,1-TCA",
        "children": ["1,1-DCA", "chloroethane"],
        "pathway": "hydrolysis + reduction",
        "description": "1,1,1-trichloroethane degrades to 1,1-dichloroethane, then chloroethane",
    },
    "TCM_series": {
        "parent": "TCM (chloroform)",
        "children": ["DCM", "CM"],
        "pathway": "reductive dehalogenation",
        "description": "Trichloromethane to dichloromethane to chloromethane",
    },
}

# Metal families (primary + secondary indicators)
METAL_FAMILIES = {
    "chromium_complex": {
        "primary": ["Cr(VI)"],
        "secondary": ["Cr(III)", "Cr_total"],
        "source_indicator": "Electroplating, metal finishing, leather tanning",
    },
    "nickel_cluster": {
        "primary": ["Ni"],
        "secondary": ["Co"],
        "source_indicator": "Metal recycling, electroplating, batteries",
    },
    "lead_zinc_pair": {
        "primary": ["Pb"],
        "secondary": ["Zn"],
        "source_indicator": "Historical mining, smelting, battery disposal",
    },
    "mercury_indicator": {
        "primary": ["Hg"],
        "secondary": ["MeHg"],
        "source_indicator": "Historic chlor-alkali, thermometer manufacturing",
    },
}

# PFAS families (per- and polyfluoroalkyl substances)
PFAS_FAMILIES = {
    "legacy_AFFF": {
        "markers": ["PFOS", "PFOA"],
        "source": "Firefighting foam (airports, military, fire training)",
        "timeline": "1970s–2000s (phased out post-2000)",
    },
    "emerging_PFAS": {
        "markers": ["PFHxS", "PFBS", "GenX", "ADONA"],
        "source": "Replacement AFFF formulations, industrial use",
        "timeline": "2000s onwards",
    },
    "telomer_series": {
        "markers": ["8-2 FTS", "10-2 FTS"],
        "source": "Fluoropolymer manufacturing, textiles, food packaging",
        "timeline": "Industrial use ongoing",
    },
}

# Fuel hydrocarbons (BTEX, MTBE, TPH)
FUEL_FAMILIES = {
    "BTEX_cluster": {
        "markers": ["Benzene", "Toluene", "Ethylbenzene", "Xylenes"],
        "source": "Gasoline spills, underground storage tanks (USTs)",
    },
    "oxygenate_cluster": {
        "markers": ["MTBE", "ETBE", "TAME"],
        "source": "Gasoline additives (1980s–2000s formulations)",
    },
    "TPH_indicator": {
        "markers": ["TPH (gasoline range)", "TPH (diesel range)"],
        "source": "Total petroleum hydrocarbons from any spill",
    },
}

# Contamination families
CONTAMINATION_FAMILIES = {
    "CVOC": "Chlorinated Volatile Organic Compounds",
    "FUEL": "Fuel Hydrocarbons & Oxygenates",
    "METALS": "Heavy Metals & Trace Elements",
    "PFAS": "Per- & Polyfluoroalkyl Substances",
}


def build_decay_chains(
    detected_vocs: List[str],
) -> Dict[str, List[str]]:
    """
    Identify VOC decay chains present in borehole measurements.

    Args:
        detected_vocs: List of VOC names (e.g., ["PCE", "TCE", "DCE"])

    Returns:
        dict mapping chain name to list of detected members
        Example: {"PCE_to_TCE": ["PCE", "TCE", "DCE"]}
    """
    detected_vocs_lower = [v.lower() for v in detected_vocs]
    chains = {}

    for chain_name, chain_info in VOC_DECAY_CHAINS.items():
        parent = chain_info["parent"].lower()
        children = [c.lower() for c in chain_info["children"]]
        chain_members = [parent] + children

        # Check if any member of this chain is detected
        detected_in_chain = [m for m in chain_members if m in detected_vocs_lower]

        if len(detected_in_chain) > 0:
            chains[chain_name] = {
                "detected_members": detected_in_chain,
                "pathway": chain_info["pathway"],
                "description": chain_info["description"],
                "completeness": len(detected_in_chain) / len(chain_members),
            }

    return chains


def match_source_signatures(
    detected_contaminants: Dict[str, List[float]],
) -> Dict[str, dict]:
    """
    Match contamination pattern to facility source signatures.

    Args:
        detected_contaminants: Dict mapping contaminant name to concentrations
                              Example: {"PCE": [100, 150], "TCE": [50, 75]}

    Returns:
        dict mapping signature name to match quality
        Example: {"Electroplating (Cr+Co)": {"confidence": "HIGH", "markers_found": 2}}
    """
    matches = {}

    # Match metal families
    for family_name, family_info in METAL_FAMILIES.items():
        primary = [p.lower() for p in family_info["primary"]]
        secondary = [s.lower() for s in family_info["secondary"]]

        detected_lower = {k.lower(): v for k, v in detected_contaminants.items()}

        primary_count = sum(1 for p in primary if p in detected_lower)
        secondary_count = sum(1 for s in secondary if s in detected_lower)

        if primary_count > 0:
            confidence = "HIGH" if primary_count == len(primary) else "MEDIUM"
            matches[f"{family_name}"] = {
                "confidence": confidence,
                "source": family_info["source_indicator"],
                "markers_found": primary_count,
                "secondary_indicators": secondary_count,
            }

    # Match PFAS families
    for family_name, family_info in PFAS_FAMILIES.items():
        markers_lower = [m.lower() for m in family_info["markers"]]
        detected_lower = {k.lower(): v for k, v in detected_contaminants.items()}

        markers_found = sum(1 for m in markers_lower if m in detected_lower)
        if markers_found > 0:
            confidence = "HIGH" if markers_found >= 2 else "MEDIUM"
            matches[f"PFAS_{family_name}"] = {
                "confidence": confidence,
                "source": family_info["source"],
                "timeline": family_info["timeline"],
                "markers_found": markers_found,
            }

    return matches


def classify_contamination_family(
    contaminants: List[str],
) -> Dict[str, str]:
    """
    Classify detected contaminants into families (CVOC, FUEL, METALS, PFAS).

    Args:
        contaminants: List of contaminant names

    Returns:
        dict mapping contaminant to family
        Example: {"PCE": "CVOC", "Benzene": "FUEL", "Cr": "METALS"}
    """
    classification = {}
    contaminants_lower = [c.lower() for c in contaminants]

    # CVOC indicators
    cvoc_keywords = ["cve", "tce", "dce", "vc", "pce", "tca", "dca", "tcm", "dcm", "cm"]
    for cont in contaminants:
        if any(kw in cont.lower() for kw in cvoc_keywords):
            classification[cont] = "CVOC"

    # FUEL indicators
    fuel_keywords = ["benzene", "toluene", "ethylbenzene", "xylene", "btex", "mtbe", "etbe", "tph"]
    for cont in contaminants:
        if any(kw in cont.lower() for kw in fuel_keywords):
            classification[cont] = "FUEL"

    # METALS indicators
    metal_keywords = ["cr", "ni", "pb", "zn", "cu", "cd", "hg", "chromium", "nickel", "lead", "zinc"]
    for cont in contaminants:
        if any(kw in cont.lower() for kw in metal_keywords):
            classification[cont] = "METALS"

    # PFAS indicators
    pfas_keywords = ["pfos", "pfoa", "pfhxs", "pfbs", "genx", "adona", "pf"]
    for cont in contaminants:
        if any(kw in cont.lower() for kw in pfas_keywords):
            classification[cont] = "PFAS"

    return classification
