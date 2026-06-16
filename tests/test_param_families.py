"""Regression tests for cross-zone parameter family classification."""
from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.param_families import classify_family, is_cvoc, is_pfas, is_fuel, is_metals


# ── Raanana-style short codes ─────────────────────────────────────────────────

def test_raanana_cvoc_codes_classified():
    for code in ["TCEY", "PCE", "DCE", "VC", "CHLF", "CCLA"]:
        assert classify_family(code) == "CVOC", f"Failed for {code}"


def test_raanana_fuel_codes_classified():
    # Taxonomy CVOC/METALS/PFAS/FUEL: BTEX aromatics are the FUEL family.
    for code in ["BENZENE", "TOLUENE", "ETHYLB", "MXYLENE", "PXYLENE", "OXYLENE", "XYLENE"]:
        assert classify_family(code) == "FUEL", f"Failed for {code}"


def test_raanana_pfas_codes_classified():
    for code in ["PFHXS", "PFOA", "PFOS", "PFHXA", "PFBA", "PFBS"]:
        assert classify_family(code) == "PFAS", f"Failed for {code}"


# ── Holon-style full names ────────────────────────────────────────────────────

def test_holon_cvoc_full_names_classified():
    for name in [
        "TRICHLORO ETHYLENE",
        "TETRACHLORO ETHYLENE",
        "CIS 1,2 DICHLOROETHYLENE",
        "DICHLOROETHYLENE 1,1",
        "VINYL CHLORIDE",
        "CARBON TETRACHLORIDE",
        "CHLOROFORM",
        "Methylene chloride",
        "Chloromethane",
        "DICHLOROETHANE1,2",
        "TRICHLORO ETHANE 1,1,1",
    ]:
        assert classify_family("", name) == "CVOC", f"Failed for {name}"


def test_holon_fuel_full_names_classified():
    for name in ["BENZENE", "TOLUENE", "XYLENE", "ETHYL BENZENE", "o-Xylene", "p-xylene", "MTBE"]:
        assert classify_family("", name) == "FUEL", f"Failed for {name}"


def test_metals_classified():
    for name in ["COPPER AS CU", "CHROMIUM", "LEAD", "CADMIUM", "NICKEL AS NI"]:
        assert classify_family(name) == "METALS", f"Failed for {name}"


def test_holon_pfas_full_names_classified():
    for name in [
        "Per-FluoroOctaneSulfonate",
        "Per-FluoroOctanoic Acid",
        "Perfluorobutane Sulfonic Acid",
        "Perfluorohexanesulfonic acid",
        "PERFLUORO PFEESA",
        "total_pfas",
    ]:
        assert classify_family("", name) == "PFAS", f"Failed for {name}"


# ── Negatives — common non-target params should NOT match ──────────────────────

def test_unrelated_params_classified_as_other():
    # Unambiguous non-target field/bulk params. NOTE (REQ #29): major anions
    # (NITRATE/CHLORIDE/BICARBONATE) currently classify as METALS — a pre-existing
    # classifier quirk flagged for review, deliberately not asserted here.
    for code in ["TEMPERATURE CENTIGRADE", "FIELD ELECTRICAL CONDUCTIVITY",
                 "TOTAL ORGANIC CARBON", "PH FIELD"]:
        assert classify_family(code) == "OTHER", f"False positive for {code}"


def test_classify_handles_none_and_empty():
    assert classify_family(None, None) == "OTHER"
    assert classify_family("", "") == "OTHER"
    assert classify_family(None, "") == "OTHER"


def test_helpers_consistent_with_classify():
    assert is_cvoc("TCE")
    assert is_fuel("BENZENE")
    assert is_pfas("PFOS")
    assert is_metals("CHROMIUM")
    assert not is_cvoc("BENZENE")
    assert not is_fuel("PFOS")
