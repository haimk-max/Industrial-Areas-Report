"""Tests for chart_presets.json and grouped_stacked chart builder."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PRESETS_PATH = REPO_ROOT / "scripts" / "chart_presets.json"


@pytest.fixture(scope="session")
def presets():
    with open(PRESETS_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    return data["presets"]


def test_pfas_s_group_is_blue(presets):
    """PFAS S-group first color must be dark blue (#0D47A1)."""
    pfas = presets["pfas"]
    s_colors = pfas["groups"]["S"]["colors"]
    assert s_colors[0] == "#0D47A1", f"PFAS S-group first color must be #0D47A1; got {s_colors[0]}"


def test_pfas_a_group_is_orange(presets):
    """PFAS A-group first color must be dark orange (#BF360C)."""
    pfas = presets["pfas"]
    a_colors = pfas["groups"]["A"]["colors"]
    assert a_colors[0] == "#BF360C", f"PFAS A-group first color must be #BF360C; got {a_colors[0]}"


def test_pfas_tpfas_excluded(presets):
    """TPFAS must not appear in any PFAS group (no double-counting)."""
    pfas = presets["pfas"]
    all_codes = pfas["groups"]["S"]["codes"] + pfas["groups"]["A"]["codes"]
    assert "TPFAS" not in all_codes, "TPFAS must never appear in PFAS chart codes (calculated sum)"


def test_cvoc_orange_palette(presets):
    """CVOC first color must be in orange/warm range."""
    cvoc = presets["cvoc"]
    first_color = cvoc["colors"][0]
    assert first_color.upper().startswith("#E"), (
        f"CVOC first color should be orange/warm (starts with #E...); got {first_color}"
    )


def test_thm_grey_palette(presets):
    """THM colors must be grey scale (#2x or #4x or #7x or #Bx)."""
    thm = presets["thm"]
    for color in thm["colors"]:
        assert color.upper()[1] in ("2", "4", "7", "B"), (
            f"THM color {color} does not look like a grey shade"
        )


def test_all_presets_have_required_fields(presets):
    """Each preset must have title_template, codes or groups, unit."""
    for name, preset in presets.items():
        assert "title_template" in preset, f"Preset '{name}' missing title_template"
        assert "unit" in preset, f"Preset '{name}' missing unit"
        assert "codes" in preset or "groups" in preset, (
            f"Preset '{name}' must have either 'codes' or 'groups'"
        )


def test_color_count_matches_code_count(presets):
    """For non-grouped presets, colors list must be >= codes list length."""
    for name, preset in presets.items():
        if "groups" in preset:
            for grp_name, grp in preset["groups"].items():
                assert len(grp["colors"]) == len(grp["codes"]), (
                    f"Preset '{name}' group '{grp_name}': colors ({len(grp['colors'])}) "
                    f"!= codes ({len(grp['codes'])})"
                )
        else:
            n_codes = len(preset.get("codes", []))
            n_colors = len(preset.get("colors", []))
            assert n_colors >= n_codes, (
                f"Preset '{name}': colors ({n_colors}) < codes ({n_codes})"
            )


def test_chart_builder_produces_file(tmp_path, presets):
    """build_grouped_stacked must produce a PNG file without error."""
    from scripts.charts.grouped_stacked import build_grouped_stacked

    df_dict = {
        "Test Station A": {"PFOS": 0.5, "PFOA": 0.3, "PFHxS": 0.1},
        "Test Station B": {"PFOS": 0.0, "PFOA": 0.2, "PFHxS": 0.4},
    }
    out = tmp_path / "test_pfas.png"
    result = build_grouped_stacked(df_dict, presets["pfas"], out, mode="absolute")
    assert out.exists(), "build_grouped_stacked must produce output PNG"


def test_chart_builder_percent_mode(tmp_path, presets):
    """percent_100 mode must produce a file without error."""
    from scripts.charts.grouped_stacked import build_grouped_stacked

    df_dict = {"Station X": {"TECE": 10.0, "TCEY": 5.0, "CDCE": 2.0}}
    out = tmp_path / "test_cvoc_pct.png"
    build_grouped_stacked(df_dict, presets["cvoc"], out, mode="percent_100")
    assert out.exists()
