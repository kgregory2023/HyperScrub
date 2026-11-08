"""End-to-end tests for the HyperScrub command-line interface."""

from pathlib import Path

import fitz

from hyperscrub.cli import main


def create_test_pdf(pdf_path: Path) -> None:
    with fitz.open() as document:
        page = document.new_page()
        page.insert_text(
            (72, 72),
            "Synthetic SSN: 123-45-6789",
        )
        document.save(pdf_path)


def extract_text(pdf_path: Path) -> str:
    with fitz.open(pdf_path) as document:
        return "\n".join(page.get_text() for page in document)


def test_cli_redacts_synthetic_pdf(
    tmp_path: Path,
    capsys,
) -> None:
    input_path = tmp_path / "input.pdf"
    output_path = tmp_path / "output.pdf"
    config_path = tmp_path / "config.yaml"

    create_test_pdf(input_path)
    config_path.write_text(
        r"""
patterns:
  ssn: '\b\d{3}-\d{2}-\d{4}\b'
""".strip(),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr()
    output_text = extract_text(output_path)

    assert exit_code == 0
    assert output_path.is_file()
    assert "123-45-6789" not in output_text
    assert "processed 1 page(s)" in captured.out
    assert "applied 1 redaction(s)" in captured.out
