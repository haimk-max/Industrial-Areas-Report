"""Tests for borehole classification in scripts/parse_excel.py.

Covers the dual-check hierarchy (purpose authoritative + name-prefix fallback)
that maps Hebrew purpose / name fields to the well_type enum. SSOT:
docs/BOREHOLE_CLASSIFICATION_GLOSSARY.md

Regression guard: the original `_borehole_type` silently mapped מק (Mekorot
public-supply) and יו (hydrological-service) wells to the generic "monitoring"
fallback. These tests pin every well_type plus the fallback / conflict paths.
"""
from pathlib import Path

from scripts.parse_excel import (
    _borehole_type,
    _classify_by_prefix,
    _classify_by_purpose,
    WELL_TYPES,
)

REPO = Path(__file__).resolve().parent.parent


# ── purpose-driven classification (authoritative) ──────────────────────────────

def test_mekorot_via_purpose():
    wt, src = _borehole_type("חברת מקורות", "מק חולון 12")
    assert wt == "mekorot_production"
    assert src == "purpose+prefix"


def test_private_via_purpose():
    wt, src = _borehole_type("פרטי", "פ אזור מקור חקלאי")
    assert wt == "private_production"


def test_research_yozem_via_purpose():
    wt, src = _borehole_type("יוזום", "יו מקוה ישראל 29/2")
    assert wt == "research_monitoring"


def test_research_mehkar_purpose():
    assert _classify_by_purpose("מחקר") == "research_monitoring"


def test_industrial_via_purpose():
    wt, _ = _borehole_type("ניטור תעשיה", "נת חולון 1")
    assert wt == "industrial_monitoring"


def test_fuel_via_purpose():
    wt, _ = _borehole_type("ניטור דלק", "נד אגד אזור 1")
    assert wt == "fuel_monitoring"


# ── name-prefix fallback (purpose missing/unrecognized) ────────────────────────

def test_mekorot_via_prefix_when_purpose_missing():
    wt, src = _borehole_type(None, "מק חולון 5")
    assert wt == "mekorot_production"
    assert src == "prefix"


def test_research_mehkar_prefix():
    wt, src = _borehole_type("", "מח דוגמה 1")
    assert wt == "research_monitoring"
    assert src == "prefix"


def test_underscore_name_form():
    # canonical IDs use underscores, name_he uses spaces — both must match
    assert _classify_by_prefix("פ_רעננה_25") == "private_production"
    assert _classify_by_prefix("פ רעננה 25") == "private_production"


def test_unrecognized_purpose_falls_back_to_prefix():
    wt, src = _borehole_type("ערך לא במילון", "נד פז סיירים 1")
    assert wt == "fuel_monitoring"
    assert src == "prefix"


# ── conflict + unknown paths ───────────────────────────────────────────────────

def test_conflict_prefers_purpose():
    # purpose says mekorot, prefix says fuel -> purpose wins, flagged
    wt, src = _borehole_type("חברת מקורות", "נד משהו 1")
    assert wt == "mekorot_production"
    assert "conflict" in src


def test_both_unknown_returns_unknown():
    wt, src = _borehole_type("ערך לא ידוע", "שם בלי קידומת")
    assert wt == "unknown"
    assert src == "unclassified"


def test_single_char_prefix_not_overmatched():
    # 'פז' must NOT match the 'פ' private prefix (no space/underscore boundary)
    assert _classify_by_prefix("פז סיירים") == "unknown"


# ── enum integrity ─────────────────────────────────────────────────────────────

def test_all_return_values_in_enum():
    samples = ["חברת מקורות", "פרטי", "יוזום", "מחקר", "תעשיה", "דלק", None, "xxx"]
    for p in samples:
        wt, _ = _borehole_type(p, "נת חולון 1")
        assert wt in WELL_TYPES


# ── cross-zone regression (real data parsed into data/boreholes.csv) ──────────

def _load_types(zone: str) -> dict[str, int]:
    import csv
    path = REPO / zone / "data" / "boreholes.csv"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    dist: dict[str, int] = {}
    for r in rows:
        dist[r["borehole_type"]] = dist.get(r["borehole_type"], 0) + 1
    return dist


def test_holon_distribution_regression():
    dist = _load_types("Holon")
    if not dist:
        return  # data not parsed in this checkout — skip silently
    assert dist.get("mekorot_production") == 5
    assert dist.get("research_monitoring") == 1
    # the legacy mis-classification must be gone
    assert dist.get("monitoring", 0) == 0


def test_raanana_distribution_regression():
    dist = _load_types("Raanana")
    if not dist:
        return
    # Raanana has no Mekorot / research wells — must stay that way
    assert dist.get("mekorot_production", 0) == 0
    assert dist.get("research_monitoring", 0) == 0
    assert dist.get("private_production") == 2
