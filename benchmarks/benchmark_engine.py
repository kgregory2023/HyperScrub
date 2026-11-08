"""Benchmark the HyperScrub redaction engine."""

import argparse
import os
import platform
import statistics
import tempfile
import time
from pathlib import Path

import fitz

from hyperscrub.engine import redact_pdf


def create_synthetic_pdf(
    pdf_path: Path,
    page_count: int,
) -> None:
    with fitz.open() as document:
        for page_number in range(page_count):
            page = document.new_page()
            page.insert_text(
                (72, 72),
                f"Synthetic record {page_number}",
            )
            page.insert_text(
                (72, 100),
                "Synthetic SSN: 123-45-6789",
            )
            page.insert_text(
                (72, 128),
                "Classification: Confidential",
            )
            page.insert_text(
                (72, 156),
                "This text should remain visible.",
            )

        document.save(pdf_path)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark sequential HyperScrub processing.",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=100,
        help="Number of synthetic PDF pages.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of timed benchmark runs.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()

    if arguments.pages < 1:
        raise ValueError("--pages must be at least 1.")

    if arguments.runs < 1:
        raise ValueError("--runs must be at least 1.")

    durations: list[float] = []
    redactions_per_run = 0

    with tempfile.TemporaryDirectory() as temporary_directory:
        benchmark_directory = Path(temporary_directory)
        input_path = benchmark_directory / "synthetic_input.pdf"

        create_synthetic_pdf(
            input_path,
            arguments.pages,
        )

        for run_number in range(arguments.runs):
            output_path = (
                benchmark_directory
                / f"redacted_output_{run_number}.pdf"
            )

            start_time = time.perf_counter()

            result = redact_pdf(
                input_path=input_path,
                output_path=output_path,
                patterns={
                    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
                },
                keywords=("Confidential",),
            )

            duration = time.perf_counter() - start_time
            durations.append(duration)
            redactions_per_run = result.matches_redacted

    median_duration = statistics.median(durations)
    mean_duration = statistics.mean(durations)
    pages_per_second = arguments.pages / median_duration

    print("HyperScrub sequential benchmark")
    print(f"Platform: {platform.platform()}")
    print(f"Python: {platform.python_version()}")
    print(f"Logical CPUs: {os.cpu_count() or 1}")
    print(f"Pages: {arguments.pages}")
    print(f"Runs: {arguments.runs}")
    print(f"Redactions per run: {redactions_per_run}")
    print(f"Fastest time: {min(durations):.4f} seconds")
    print(f"Median time: {median_duration:.4f} seconds")
    print(f"Mean time: {mean_duration:.4f} seconds")
    print(f"Median throughput: {pages_per_second:.2f} pages/second")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
