"""Tests for the HyperScrub PDF redaction engine."""

from pathlib import Path

import fitz
import pytest

from hyperscrub.engine import redact_pdf


def create_test_pdf(pdf_path: Path) -> None:
    with fitz.open() as document:
        page = document.new_page()
        page.insert_text(
            (72, 72),
            "Employee SSN: 123-45-6789",
        )
        page.insert_text(
            (72, 100),
            "Status: Confidential",
        )
        page.insert_text(
            (72, 128),
            "This sentence must remain visible.",
        )
        document.save(pdf_path)


def extract_text(pdf_path: Path) -> str:
    with fitz.open(pdf_path) as document:
        return "\n".join(page.get_text() for page in document)


def test_redacts_patterns_and_keywords(tmp_path: Path) -> None:
    input_path = tmp_path / "input.pdf"
    output_path = tmp_path / "output.pdf"
    create_test_pdf(input_path)

    result = redact_pdf(
        input_path=input_path,
        output_path=output_path,
        patterns={
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        },
        keywords=("Confidential",),
    )

    output_text = extract_text(output_path)

    assert output_path.is_file()
    assert "123-45-6789" not in output_text
    assert "Confidential" not in output_text
    assert "This sentence must remain visible." in output_text
    assert result.pages_processed == 1
    assert result.matches_redacted == 2
    assert result.output_path == output_path.resolve()


def test_rejects_same_input_and_output_path(
    tmp_path: Path,
) -> None:
    pdf_path = tmp_path / "document.pdf"
    create_test_pdf(pdf_path)

    with pytest.raises(
        ValueError,
        match="Input and output paths must be different",
    ):
        redact_pdf(
            input_path=pdf_path,
            output_path=pdf_path,
            patterns={"ssn": r"\d{3}-\d{2}-\d{4}"},
            keywords=(),
        )


def test_rejects_invalid_regex(tmp_path: Path) -> None:
    input_path = tmp_path / "input.pdf"
    output_path = tmp_path / "output.pdf"
    create_test_pdf(input_path)

    with pytest.raises(
        ValueError,
        match="Invalid regex pattern",
    ):
        redact_pdf(
            input_path=input_path,
            output_path=output_path,
            patterns={"broken": r"["},
            keywords=(),
        )
