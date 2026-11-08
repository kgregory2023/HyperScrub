"""Command-line interface for HyperScrub."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from .config import load_config
from .engine import redact_pdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hyperscrub",
        description="Redact configured patterns and keywords from a PDF.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the source PDF.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path for the redacted PDF.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to the YAML rules file.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)

    try:
        rules = load_config(arguments.config)
        result = redact_pdf(
            input_path=arguments.input,
            output_path=arguments.output,
            patterns=rules.patterns,
            keywords=rules.keywords,
        )
    except (FileNotFoundError, OSError, TypeError, ValueError) as error:
        parser.error(str(error))

    print(
        f"HyperScrub processed {result.pages_processed} page(s) and "
        f"applied {result.matches_redacted} redaction(s)."
    )
    print(f"Output saved to: {result.output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
