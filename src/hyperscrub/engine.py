"""Core PDF redaction engine for HyperScrub."""

import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass(frozen=True)
class RedactionResult:
    pages_processed: int
    matches_redacted: int
    output_path: Path


def _compile_rules(
    patterns: Mapping[str, str],
    keywords: Sequence[str],
) -> list[re.Pattern[str]]:
    compiled_rules: list[re.Pattern[str]] = []

    for name, expression in patterns.items():
        try:
            compiled_rules.append(re.compile(expression, re.IGNORECASE))
        except re.error as error:
            raise ValueError(f"Invalid regex pattern '{name}': {error}") from error

    for keyword in keywords:
        keyword = keyword.strip()
        if keyword:
            expression = rf"(?<!\w){re.escape(keyword)}(?!\w)"
            compiled_rules.append(re.compile(expression, re.IGNORECASE))

    return compiled_rules


def _find_page_matches(
    page: fitz.Page,
    rules: Sequence[re.Pattern[str]],
) -> list[fitz.Rect]:
    lines: dict[tuple[int, int], list[tuple]] = defaultdict(list)

    for word in page.get_text("words", sort=True):
        block_number = int(word[5])
        line_number = int(word[6])
        lines[(block_number, line_number)].append(word)

    matched_rectangles: list[fitz.Rect] = []
    seen_rectangles: set[tuple[float, float, float, float]] = set()

    for words in lines.values():
        line_text = " ".join(str(word[4]) for word in words)
        word_ranges: list[tuple[int, int, fitz.Rect]] = []
        character_index = 0

        for word in words:
            text = str(word[4])
            start = character_index
            end = start + len(text)

            word_ranges.append(
                (
                    start,
                    end,
                    fitz.Rect(word[0], word[1], word[2], word[3]),
                )
            )
            character_index = end + 1

        for rule in rules:
            for match in rule.finditer(line_text):
                rectangles = [
                    rectangle
                    for start, end, rectangle in word_ranges
                    if end > match.start() and start < match.end()
                ]

                if not rectangles:
                    continue

                combined = fitz.Rect(rectangles[0])
                for rectangle in rectangles[1:]:
                    combined |= rectangle

                rectangle_key = tuple(round(value, 2) for value in combined)
                if rectangle_key not in seen_rectangles:
                    seen_rectangles.add(rectangle_key)
                    matched_rectangles.append(combined)

    return matched_rectangles


def redact_pdf(
    input_path: Path,
    output_path: Path,
    patterns: Mapping[str, str],
    keywords: Sequence[str],
) -> RedactionResult:
    input_path = input_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()

    if not input_path.is_file():
        raise FileNotFoundError(f"Input PDF does not exist: {input_path}")

    if input_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must have a .pdf extension.")

    if input_path == output_path:
        raise ValueError("Input and output paths must be different.")

    rules = _compile_rules(patterns, keywords)
    if not rules:
        raise ValueError("At least one pattern or keyword is required.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    matches_redacted = 0

    with fitz.open(input_path) as document:
        for page in document:
            rectangles = _find_page_matches(page, rules)

            for rectangle in rectangles:
                page.add_redact_annot(rectangle, fill=(0, 0, 0))

            if rectangles:
                page.apply_redactions()
                matches_redacted += len(rectangles)

        pages_processed = document.page_count
        document.save(output_path, garbage=4, deflate=True)

    return RedactionResult(
        pages_processed=pages_processed,
        matches_redacted=matches_redacted,
        output_path=output_path,
    )
