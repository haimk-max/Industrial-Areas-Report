"""Tests for scripts/generate_zone_html_from_brief.py (REQ #31.1).

Verifies the brief-driven HTML generator consumes every data-bearing section
(no silent no-ops) and that PUBLIC sections are brief-count-driven rather than
inheriting the frozen reference's hardcoded Holon numbers.

These are the regressions that blocked activating a second zone:
  - PUBLIC stats / timeline / means / methodology were never replaced.
  - PUBLIC context/findings markers did not exist -> replacements no-op'd.
"""
import importlib.util
import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

REPO = Path(__file__).resolve().parent.parent
GEN_PATH = REPO / "scripts" / "generate_zone_html_from_brief.py"
BRIEF_PATH = REPO / "report-engine" / "briefs" / "holon.yaml"
REF_DIR = REPO / "report-engine" / "design-system" / "reference"


def _load_module():
    spec = importlib.util.spec_from_file_location("brief_html_gen", GEN_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gen():
    return _load_module()


@pytest.fixture(scope="module")
def brief():
    with BRIEF_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture(scope="module")
def public_html(gen, brief):
    return gen.generate_public_html(brief, REF_DIR / "HOLON_PUBLIC.html")


@pytest.fixture(scope="module")
def internal_html(gen, brief):
    return gen.generate_internal_html(brief, REF_DIR / "HOLON_INTERNAL.html")


# ─── PUBLIC: the four previously-unreplaced sections are brief-count-driven ───

def test_stats_count_matches_brief(public_html, brief):
    assert public_html.count('<div class="stat">') == len(brief["stats_public"])


def test_timeline_event_count_matches_brief(public_html, brief):
    assert len(re.findall(r'<div class="event ', public_html)) == len(brief["timeline"])


def test_means_card_count_matches_brief(public_html, brief):
    assert public_html.count('<div class="means-card">') == len(brief["means_summary"])


def test_method_cell_count_matches_brief(public_html, brief):
    assert public_html.count('<div class="method-cell">') == len(brief["methodology"])


def test_public_findings_count_matches_brief(public_html, brief):
    assert public_html.count('<article class="fp">') == len(brief["findings"])


# ─── PUBLIC: content actually flows from the brief (not Holon hardcode) ───

def test_timeline_text_from_brief(public_html, brief):
    # A timeline label/text that only exists if the brief was consumed.
    assert brief["timeline"][0]["text"] in public_html


def test_methodology_body_from_brief(public_html, brief):
    assert brief["methodology"][0]["body"] in public_html


def test_means_title_from_brief(public_html, brief):
    assert brief["means_summary"][0]["title"] in public_html


# ─── PUBLIC: no facility/source name leaks ───

def test_no_source_facility_leaks(public_html, brief):
    leaks = []
    for src in brief.get("sources", []):
        nm = src.get("name_internal", "")
        # "אגד" / "פז" are substrings of generic words; require the full name.
        if nm and len(nm) >= 4 and nm in public_html:
            leaks.append(nm)
    assert not leaks, f"facility names leaked into PUBLIC: {leaks}"


# ─── INTERNAL: findings + decisions consumed from brief ───

def test_internal_findings_count_matches_brief(internal_html, brief):
    assert internal_html.count('<article class="finding">') == len(brief["findings"])


def test_internal_decisions_rowspans_match_brief(internal_html, brief):
    # Each decision category renders one rowspan equal to its action count.
    spans = sorted(int(m) for m in re.findall(r'class="cat" rowspan="(\d+)"', internal_html))
    expected = sorted(len(g["actions"]) for g in brief["decisions"])
    assert spans == expected


# ─── container helper: depth-balanced replacement ───

def test_replace_container_inner_handles_nesting(gen):
    src = '<div class="x">OLD<div class="y">keep</div>OLD2</div>TAIL'
    out = gen.replace_container_inner(src, '<div class="x">', "NEW")
    assert out == '<div class="x">NEW</div>TAIL'


def test_replace_container_inner_missing_is_noop(gen):
    src = "<div>nothing</div>"
    assert gen.replace_container_inner(src, '<div class="absent">', "NEW") == src
