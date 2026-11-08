"""Tests for HyperScrub YAML configuration handling."""

from pathlib import Path

import pytest

from hyperscrub.config import load_config


def test_loads_valid_configuration(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        r"""
patterns:
  ssn: '\b\d{3}-\d{2}-\d{4}\b'

keywords:
  - 'Confidential'
  - 'Internal Use Only'
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.patterns == {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b"
    }
    assert config.keywords == (
        "Confidential",
        "Internal Use Only",
    )


def test_rejects_empty_configuration(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("{}\n", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="at least one pattern or keyword",
    ):
        load_config(config_path)


def test_rejects_unknown_fields(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "unsupported_option: true\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Unknown configuration fields",
    ):
        load_config(config_path)


def test_removes_duplicate_keywords(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
keywords:
  - Confidential
  - Confidential
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.keywords == ("Confidential",)
