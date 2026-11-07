<p align="center">
  <img src="assets/hyperscrub-wordmark.png" alt="HyperScrub — Parallel PDF Redaction" width="420">
</p>

<p align="center">
  <strong>Local, multicore redaction for large PDFs.</strong><br>
  <em>Prototype · Portable release in development</em>
</p>

## What HyperScrub does

HyperScrub looks for sensitive text using YAML rules. Worker processes scan pages in parallel, then a single writer applies the redactions and saves a separate PDF.

- **Structural redaction** removes matched content from PDF pages.
- **Native text and local OCR** cover searchable pages and image-only scans.
- **Configurable rules** match patterns such as Social Security numbers and keywords such as Splunk, AWS, and Okta.

## Quick start

Once published, download the archive for your platform from **Releases** and extract it. The planned bundle includes Python, the required libraries, and English OCR data.

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

HyperScrub is designed to process documents locally. Text extraction, OCR, and matching run on the host. The engine applies redactions to the matched page content and writes a separate PDF with visible redaction marks.

1. **Inspect each page.** Distribute pages to worker processes. Each worker checks for a native text layer and selects native extraction or local OCR.
2. **Reconstruct and match lines.** Collect words and their bounding boxes, group tokens by line, and match the configured patterns and keywords against reconstructed text. Map each match back to page coordinates. OCR coordinates are converted from image pixels to PDF page coordinates.
3. **Collect redaction coordinates.** Workers return page numbers and match rectangles to the controller. The controller owns the output document.
4. **Apply redactions and save.** The controller applies the collected redactions with PyMuPDF and saves a new file. One writer coordinates updates to the PDF objects and cross-reference table. The prototype saves with garbage collection and stream compression.

</details>

<details>
<summary>Verification and operational constraints</summary>

Use test PDFs containing known sensitive values. Re-extract text from the redacted output, inspect the relevant PDF content, and render scanned pages to verify that targeted text is gone from the image regions. A raw byte search can serve as a supplementary check, since compressed or encoded streams may hide matches from it.

The original design calls for separately checking document metadata, embedded attachments, and form data. Page-content redaction and sanitization of those additional surfaces require separate implementation and verification.

### Operational constraints

- **Serial output.** Page analysis can run on multiple cores, while the write pass remains serial. On large documents, measure analysis and output writing separately to see which phase limits speedup.
- **OCR coverage and quality.** Low resolution, skew, and character substitutions can break pattern matching. A selectable header can also cause the current page-level fallback to skip an embedded scan. The original design proposes a `--force-ocr` option for cases requiring another pass. Review low-quality scans and mixed-content pages before sharing.
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
│       ├── engine.py
│       └── utils.py
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

Report vulnerabilities privately through the repository’s security reporting channel once configured. Include reproduction steps and a synthetic or sanitized PDF that demonstrates the issue. Keep sensitive source documents out of public issues.

</details>
