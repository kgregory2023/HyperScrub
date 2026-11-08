"""YAML configuration loading and validation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RuleConfig:
    patterns: dict[str, str]
    keywords: tuple[str, ...]


def _validate_patterns(value: Any) -> dict[str, str]:
    if value is None:
        return {}

    if not isinstance(value, dict):
        raise ValueError("'patterns' must be a YAML mapping.")

    patterns: dict[str, str] = {}

    for name, expression in value.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Pattern names must be nonempty strings.")

        if not isinstance(expression, str) or not expression.strip():
            raise ValueError(
                f"Pattern '{name}' must contain a nonempty regex string."
            )

        patterns[name.strip()] = expression

    return patterns


def _validate_keywords(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()

    if not isinstance(value, list):
        raise ValueError("'keywords' must be a YAML list.")

    keywords: list[str] = []

    for keyword in value:
        if not isinstance(keyword, str) or not keyword.strip():
            raise ValueError("Keywords must be nonempty strings.")

        normalized = keyword.strip()
        if normalized not in keywords:
            keywords.append(normalized)

    return tuple(keywords)


def load_config(config_path: Path) -> RuleConfig:
    config_path = config_path.expanduser().resolve()

    if not config_path.is_file():
        raise FileNotFoundError(
            f"Configuration file does not exist: {config_path}"
        )

    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            data = yaml.safe_load(config_file) or {}
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML configuration: {error}") from error

    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a YAML mapping.")

    unknown_fields = set(data) - {"patterns", "keywords"}
    if unknown_fields:
        fields = ", ".join(sorted(str(field) for field in unknown_fields))
        raise ValueError(f"Unknown configuration fields: {fields}")

    patterns = _validate_patterns(data.get("patterns"))
    keywords = _validate_keywords(data.get("keywords"))

    if not patterns and not keywords:
        raise ValueError(
            "Configuration must define at least one pattern or keyword."
        )

    return RuleConfig(patterns=patterns, keywords=keywords)
