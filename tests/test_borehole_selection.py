"""Tests for select_boreholes.py — Tier 1/2/3 selection logic."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def tier1_data():
    path = REPO_ROOT / "zone_definitions" / "tier1_historical_boreholes.json"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def polygon_data():
    path = REPO_ROOT / "zone_definitions" / "zone_polygons.json"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def tier3_data():
    path = REPO_ROOT / "zone_definitions" / "tier3_cross_zone_boreholes.json"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def raanana_boreholes():
    from scripts.select_boreholes import _load_boreholes_csv
    path = REPO_ROOT / "Raanana" / "data" / "boreholes.csv"
    return _load_boreholes_csv(path)


def test_raanana_selects_all_7_boreholes(raanana_boreholes, tier1_data, polygon_data, tier3_data):
    """Raanana zone must yield all 7 known boreholes."""
    from scripts.select_boreholes import select_boreholes
    results = select_boreholes("raanana", raanana_boreholes, tier1_data, polygon_data, tier3_data)
    assert len(results) == 7, f"Expected 7 boreholes for Raanana; got {len(results)}"


def test_tier1_boreholes_included(raanana_boreholes, tier1_data, polygon_data, tier3_data):
    """All Tier 1 historical boreholes must be in the result."""
    from scripts.select_boreholes import select_boreholes
    results = select_boreholes("raanana", raanana_boreholes, tier1_data, polygon_data, tier3_data)
    result_ids = {r.canonical_id for r in results}
    expected_t1 = {"raanana_nt_1", "raanana_nt_2", "raanana_nt_3",
                   "raanana_nd_paz_hanofer", "raanana_nd_turbine"}
    missing = expected_t1 - result_ids
    assert not missing, f"Tier 1 boreholes missing from selection: {missing}"


def test_tier1_boreholes_tagged_correctly(raanana_boreholes, tier1_data, polygon_data, tier3_data):
    """Tier 1 boreholes must have tier=1 tag."""
    from scripts.select_boreholes import select_boreholes
    results = select_boreholes("raanana", raanana_boreholes, tier1_data, polygon_data, tier3_data)
    t1_results = {r.canonical_id: r.tier for r in results
                  if r.canonical_id in {"raanana_nt_1", "raanana_nt_2", "raanana_nt_3"}}
    for bh_id, tier in t1_results.items():
        assert tier == 1, f"{bh_id} must be Tier 1; got {tier}"


def test_point_in_polygon():
    """Point inside polygon returns True; outside returns False."""
    from scripts.select_boreholes import _point_in_polygon
    polygon = [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]
    assert _point_in_polygon(5, 5, polygon) is True
    assert _point_in_polygon(15, 5, polygon) is False
    assert _point_in_polygon(0.1, 0.1, polygon) is True


def test_point_near_polygon_buffer():
    """Point outside polygon but within buffer returns True."""
    from scripts.select_boreholes import _point_near_polygon
    polygon = [[0, 0], [1000, 0], [1000, 1000], [0, 1000], [0, 0]]
    assert _point_near_polygon(1200, 500, polygon, buffer_m=300) is True
    assert _point_near_polygon(1600, 500, polygon, buffer_m=300) is False


def test_unknown_zone_returns_empty(raanana_boreholes, tier1_data, polygon_data, tier3_data):
    """Unknown zone with no polygon and no Tier 1 entries returns empty list."""
    from scripts.select_boreholes import select_boreholes
    results = select_boreholes("nonexistent_zone", raanana_boreholes, tier1_data, polygon_data, tier3_data)
    assert results == [], "Unknown zone must return empty list"


def test_18_zones_defined_in_tier1(tier1_data):
    """tier1_historical_boreholes.json must cover all 18 zones."""
    zones = [k for k in tier1_data if not k.startswith("_")]
    assert len(zones) == 18, f"Expected 18 zones in tier1 data; got {len(zones)}"


def test_18_zones_defined_in_polygons(polygon_data):
    """zone_polygons.json must cover all 18 zones."""
    zones = [k for k in polygon_data if not k.startswith("_")]
    assert len(zones) == 18, f"Expected 18 zones in polygon data; got {len(zones)}"
