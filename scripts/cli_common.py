"""Shared CLI parser used by every script. Standardizes --zone, --config, --input, --output."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO_ROOT / "config" / "analysis_config.yaml"


def make_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--zone",
        type=str,
        default=None,
        help="Zone id (e.g., 'raanana'). Required for zone-scoped scripts.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"Path to analysis config YAML (default: {DEFAULT_CONFIG.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional input path override.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path override.",
    )
    return parser


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_zone_overrides(zone: str, config_dir: Path | None = None) -> dict:
    """Load optional config/zone_overrides/{zone}.yaml. Returns {} if absent."""
    base = config_dir if config_dir is not None else (REPO_ROOT / "config" / "zone_overrides")
    path = base / f"{zone}.yaml"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def merged_config(zone: str | None, config_path: Path) -> dict:
    """Merge base config with optional zone overrides (deep merge)."""
    base = load_config(config_path)
    if not zone:
        return base
    overrides = load_zone_overrides(zone)
    return _deep_merge(base, overrides)


def _deep_merge(base: dict, overrides: dict) -> dict:
    result = dict(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
