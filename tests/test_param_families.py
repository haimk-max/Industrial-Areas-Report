"""Regression tests for cross-zone parameter family classification."""
from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.param_families import classify_family, is_btex, is_cvoc, is_pfas


# ── Raanana-style short codes ─────────────────────────────────────────────────

def test_raanana_cvoc_codes_classified():
    for code in ["TCEY", "PCE", "DCE", "VC", "CHLF", "CCLA"]:
        assert classify_family(code) == "CVOC", f"Failed for {code}"


def test_raanana_btex_codes_classified():
    for code in ["BENZENE", "TOLUENE", "ETHYLB", "MXYLENE", "PXYLENE", "OXYLENE", "XYLENE"]:
        assert classify_family(code) == "BTEX", f"Failed for {code}"


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


def test_holon_btex_full_names_classified():
    for name in ["BENZENE", "TOLUENE", "XYLENE", "ETHYL BENZENE", "o-Xylene", "p-xylene"]:
        assert classify_family("", name) == "BTEX", f"Failed for {name}"


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
    for code in ["NITRATE AS NO3", "CHLORIDE AS CL", "TEMPERATURE CENTIGRADE",
                 "FIELD ELECTRICAL CONDUCTIVITY", "BICARBONATE AS HCO3",
                 "TOTAL ORGANIC CARBON", "COPPER AS CU"]:
        assert classify_family(code) == "OTHER", f"False positive for {code}"


def test_classify_handles_none_and_empty():
    assert classify_family(None, None) == "OTHER"
    assert classify_family("", "") == "OTHER"
    assert classify_family(None, "") == "OTHER"


def test_helpers_consistent_with_classify():
    assert is_cvoc("TCE")
    assert is_btex("BENZENE")
    assert is_pfas("PFOS")
    assert not is_cvoc("BENZENE")
    assert not is_btex("PFOS")
