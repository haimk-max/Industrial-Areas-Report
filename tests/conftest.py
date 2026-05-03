"""Shared pytest fixtures."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def golden_dir(repo_root: Path) -> Path:
    return repo_root / "tests" / "golden"


@pytest.fixture(scope="session")
def config_path(repo_root: Path) -> Path:
    return repo_root / "config" / "analysis_config.yaml"
