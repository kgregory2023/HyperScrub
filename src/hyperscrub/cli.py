"""Command-line interface for HyperScrub."""

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hyperscrub",
        description="Local, multicore PDF redaction.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the source PDF or directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path for the redacted PDF or output directory.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to the YAML rules file.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    parser.parse_args()
    parser.error("The redaction engine is not implemented yet.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
