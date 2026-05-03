"""Tests for preprocess.py — MK trend engine golden dataset regression."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _default_cfg():
    from scripts.cli_common import load_config
    return load_config(REPO_ROOT / "config" / "analysis_config.yaml")


def _load_golden_measurements(golden_dir: Path) -> dict[tuple[str, str], list[dict]]:
    path = golden_dir / "raanana_measurements.csv"
    groups: dict[tuple[str, str], list[dict]] = {}
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = (row["canonical_id"], row["param_code"])
            groups.setdefault(key, []).append(row)
    return groups


def _load_golden_trends(golden_dir: Path) -> dict[tuple[str, str], dict]:
    path = golden_dir / "expected_trends.csv"
    trends = {}
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            trends[(row["borehole_id"], row["parameter"])] = row
    return trends


def _obs_from_rows(rows: list[dict]):
    """Convert CSV row dicts to Observation objects."""
    from scripts.preprocess import parse_observation
    obs = []
    for r in rows:
        o = parse_observation(
            date_str=r.get("date", ""),
            concentration_str=r.get("concentration", ""),
            is_below_lod_str=r.get("is_below_lod", "False"),
            drinking_standard_str=r.get("drinking_water_standard", ""),
        )
        if o is not None:
            obs.append(o)
    return obs


def _run(bh_id: str, param: str, rows: list[dict], std: float | None):
    from scripts.preprocess import analyze_series
    obs = _obs_from_rows(rows)
    return analyze_series(bh_id, param, obs, _default_cfg(), drinking_water_standard=std)


@pytest.fixture(scope="session")
def golden_measurements(golden_dir):
    return _load_golden_measurements(golden_dir)


@pytest.fixture(scope="session")
def golden_trends(golden_dir):
    return _load_golden_trends(golden_dir)


def test_golden_increasing_classification(golden_dir):
    """NO3 at p_25 must be classified INCREASING (strong rising MK trend)."""
    meas = _load_golden_measurements(golden_dir)
    rows = meas.get(("raanana_p_25", "NO3"), [])
    assert rows, "NO3 measurements for p_25 must exist in golden dataset"

    result = _run("raanana_p_25", "NO3", rows, 70.0)
    assert result.classification == "INCREASING", (
        f"NO3 at p_25 must be INCREASING; got {result.classification}. "
        "Check if MK gating changed."
    )
    assert "Rising trend" in result.trend_description, (
        f"trend_description must contain 'Rising trend'; got: {result.trend_description}"
    )


def test_golden_chlf_increasing_classification(golden_dir):
    """Chloroform at p_25 must be classified INCREASING (significant MK rising)."""
    meas = _load_golden_measurements(golden_dir)
    rows = meas.get(("raanana_p_25", "CHLF"), [])
    assert rows, "CHLF measurements for p_25 must exist"

    result = _run("raanana_p_25", "CHLF", rows, 80.0)
    assert result.classification == "INCREASING", (
        f"CHLF at p_25 must be INCREASING; got {result.classification}"
    )


def test_tce_crossed_standard_before_entry_criteria(golden_dir):
    """TCE at nt_1 must have crossed_standard=True even though n5<min_n5."""
    meas = _load_golden_measurements(golden_dir)
    rows = meas.get(("raanana_nt_1", "TCEY"), [])
    assert rows, "TCE measurements for nt_1 must exist"

    result = _run("raanana_nt_1", "TCEY", rows, 7.5)
    assert result.crossed_standard is True, (
        "TCE at nt_1 must have crossed_standard=True (817 µg/L >> 7.5 µg/L). "
        "crossed_standard check must precede entry-criteria early return."
    )


def test_pfas_single_measurement_crossed_standard(golden_dir):
    """PFHxS at turbine (n=1) must have crossed_standard=True despite NONE classification."""
    meas = _load_golden_measurements(golden_dir)
    rows = meas.get(("raanana_nd_turbine", "PFHxS"), [])
    assert rows, "PFHxS measurements for turbine must exist"

    result = _run("raanana_nd_turbine", "PFHxS", rows, 0.1)
    assert result.crossed_standard is True, "PFHxS=1.16 µg/L >> 0.1 µg/L standard; crossed_standard must be True"
    assert result.classification == "NONE", "Single measurement must yield NONE (n<min_n=4)"


def test_no_soft_trigger_field():
    """TrendResult must NOT have a soft_trigger field (V2 removal)."""
    from scripts.preprocess import TrendResult
    result = TrendResult(borehole_id="test", parameter="TEST")
    assert not hasattr(result, "soft_trigger"), (
        "soft_trigger field must be removed from TrendResult in V2. "
        "Do NOT re-add it."
    )


def test_trend_description_populated():
    """analyze_series must always populate trend_description."""
    # Enough data across 5y window + older years for strong SNR
    rows = [
        {"date": "2015-01-01", "concentration": "1.0", "is_below_lod": "False"},
        {"date": "2017-01-01", "concentration": "3.0", "is_below_lod": "False"},
        {"date": "2020-01-01", "concentration": "5.0", "is_below_lod": "False"},
        {"date": "2021-01-01", "concentration": "8.0", "is_below_lod": "False"},
        {"date": "2022-01-01", "concentration": "12.0", "is_below_lod": "False"},
        {"date": "2023-01-01", "concentration": "18.0", "is_below_lod": "False"},
    ]
    result = _run("test_bh", "TEST", rows, None)
    assert result.trend_description, "trend_description must be non-empty"
    assert "Mann-Kendall" in result.trend_description, (
        "trend_description must include Mann-Kendall statistics"
    )


def test_snr_below_threshold_gives_none():
    """SNR < 0.3 must yield NONE classification even if MK is significant."""
    rows = [
        {"date": f"202{i}-01-01", "concentration": f"{1.0 + i * 0.001}", "is_below_lod": "False"}
        for i in range(5)
    ]
    result = _run("test_bh", "TEST", rows, None)
    assert result.snr_5y is not None, "5y SNR must be computable when all data in window"
    if result.snr_5y < 0.3:
        assert result.classification == "NONE", (
            "SNR < 0.3 must produce NONE regardless of MK significance (SNR gating rule)."
        )


def test_below_lod_half_lod_treatment():
    """Below-LOD values must be treated as LOD/2 (not zero, not LOD)."""
    from scripts.preprocess import _adjusted_value, Observation

    obs = Observation(date="2020-01-01", concentration=4.0, is_below_lod=True, lod=4.0)
    val = _adjusted_value(obs)
    assert abs(val - 2.0) < 1e-9, f"half-LOD expected 2.0, got {val}"


def test_classifications_match_golden(golden_dir):
    """All golden trend classifications must match current engine output."""
    meas = _load_golden_measurements(golden_dir)
    expected = _load_golden_trends(golden_dir)

    mismatches = []
    for (bh_id, param), exp_row in expected.items():
        rows = meas.get((bh_id, param), [])
        if not rows:
            continue
        std_str = exp_row.get("drinking_water_standard", "")
        std = float(std_str) if std_str else None
        result = _run(bh_id, param, rows, std)
        if result.classification != exp_row["classification"]:
            mismatches.append(
                f"{bh_id}/{param}: expected {exp_row['classification']}, got {result.classification}"
            )

    assert not mismatches, "Classification regressions detected:\n" + "\n".join(mismatches)
