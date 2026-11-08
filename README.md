<p align="center">
  <img src="assets/hyperscrub-wordmark.png" alt="HyperScrub — Parallel PDF Redaction" width="420">
</p>

<p align="center">
  <a href="https://github.com/kgregory2023/HyperScrub/actions/workflows/tests.yml">
    <img src="https://github.com/kgregory2023/HyperScrub/actions/workflows/tests.yml/badge.svg" alt="Tests">
  </a>
</p>

<p align="center">
  <strong>Configurable redaction for searchable PDF documents.</strong><br>
  <em>Pre-alpha · Active development · Not approved for sensitive data</em>
</p>

> [!WARNING]
> HyperScrub has not completed security or redaction-correctness testing. Use
> synthetic documents during development. Do not rely on the current build to
> protect genuine sensitive information.

## Project status

HyperScrub is an early development prototype. The current source code provides:

- a Python command-line interface;
- validated YAML pattern and keyword rules;
- native text extraction for searchable PDFs; and
- sequential page-content redaction with PyMuPDF.

The following capabilities are planned and are not implemented yet:

- multicore page analysis;
- OCR for scanned and image-only pages;
- batch directory processing;
- metadata, attachment, and form-data sanitization; and
- portable executables with bundled dependencies.

## Current functionality

HyperScrub looks for sensitive text in searchable PDFs using YAML rules. The
current engine analyzes pages sequentially, applies matching redactions, and
saves a separate output PDF.

- **Structural redaction** removes matched content from PDF pages.
- **Native text extraction** processes PDFs that already contain searchable text.
- **Configurable rules** match patterns such as Social Security numbers and keywords such as Splunk, AWS, and Okta.

## Planned command interface

These commands document the intended release interface. No stable release has
been published yet.

### Single document

**macOS and Linux**

```bash
./hyperscrub --input raw_document.pdf --output redacted_document.pdf --config config.yaml
```

**Windows PowerShell**

```powershell
.\hyperscrub.exe --input raw_document.pdf --output redacted_document.pdf --config config.yaml
```

<details>
<summary>Batch directory processing</summary>

The planned batch command takes an input directory and saves redacted copies in a separate directory.

```bash
./hyperscrub --input ./raw_logs_folder/ --output ./clean_exports/ --config presets/devops_audit.yaml
```

</details>

## Configuration

Use regex patterns for structured values and plain-text keywords for names and terms. The example `birthday` rule matches any date written as `MM/DD/YYYY`, so narrow it when other dates should be preserved.

```yaml
patterns:
  ssn: '\b\d{3}-\d{2}-\d{4}\b'
  birthday: '\b\d{2}/\d{2}/\d{4}\b'

keywords:
  - 'Splunk'
  - 'AWS'
  - 'Okta'
```

## Technical details

<details>
<summary>Architecture and trust model</summary>

HyperScrub is designed to process documents locally. The current engine extracts
native text, matches configured rules, applies redactions, and writes a separate
PDF with visible redaction marks.

1. **Inspect each page.** Extract words and coordinates from the native text layer.
2. **Reconstruct and match lines.** Group words by line, evaluate configured patterns and keywords, and map matches back to page coordinates.
3. **Apply redactions.** Add redaction annotations and remove matched page content with PyMuPDF.
4. **Save a separate file.** Write the result with PDF garbage collection and stream compression.

The planned parallel architecture will move page analysis into worker processes
while retaining one coordinated writer for the output document.

</details>

<details>
<summary>Verification and operational constraints</summary>

Use searchable test PDFs containing known synthetic values. Re-extract text from
the redacted output and inspect the rendered pages to verify the result. A raw
byte search can serve as a supplementary check, since compressed or encoded
streams may hide matches from it.

The original design calls for separately checking document metadata, embedded attachments, and form data. Page-content redaction and sanitization of those additional surfaces require separate implementation and verification.

### Operational constraints

- **Sequential processing.** The current implementation does not use multiple cores. Its runtime will serve as the correctness and performance baseline for later parallel development.
- **No OCR.** Image-only scans and text embedded in images are not processed by the current implementation.
- **Fragmented native text.** PDF generators can split a visually continuous value across tokens or insert invisible characters. The design calls for normalizing layout text before matching and testing that reconstructed matches still map to the correct coordinates.
- **Over-redaction.** Short keywords can match inside unrelated words. The design calls for whole-word matching by default and explicit rules for broader matching. Test for both missed matches and unwanted redactions.

</details>

<details>
<summary>Proposed repository layout</summary>

```text
hyperscrub/
├── .github/
│   └── workflows/
├── assets/
│   └── hyperscrub-wordmark.png
├── src/
│   └── hyperscrub/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       └── engine.py
├── presets/
│   ├── devops_audit.yaml
│   ├── gdpr.yaml
│   └── hipaa.yaml
├── tests/
│   └── test_engine.py
├── ARCHITECTURE.md
├── LICENSE
├── README.md
├── SECURITY.md
└── pyproject.toml
```

The original layout includes automated tests and security scanning in GitHub Actions. The proposed GDPR and HIPAA preset names identify use cases. Compliance depends on the full workflow and its controls. The original draft considered MIT and Apache 2.0 for the license.

</details>

<details>
<summary>Security policy</summary>

Report vulnerabilities privately through the repository’s security reporting channel. Include reproduction steps and a synthetic or sanitized PDF that demonstrates the issue. Keep sensitive source documents out of public issues.

</details>

