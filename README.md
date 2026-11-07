<p align="center">
  <img src="assets/hyperscrub-wordmark.png" alt="HyperScrub — Parallel PDF Redaction" width="640">
</p>HyperScrub
HyperScrub is a local command-line project for redacting sensitive information from large PDFs. It analyzes pages across multiple CPU cores, then applies the detected redactions in a single write pass.

Status: Prototype. The portable release, bundled OCR, and commands below describe the planned first release.
Architecture & core features
- Structural PDF redaction. PyMuPDF applies redactions to matched page content and saves a separate output file.
- Multicore processing. Worker processes analyze pages in parallel and return the coordinates of matches. A single writer applies the redactions and saves the PDF.
- Native text and local OCR. Searchable pages use native text extraction. Pages without selectable text use local OCR, with English language data planned for the portable release.
- Configurable rules. A YAML file defines regex patterns for sensitive values and keywords for terms such as Splunk, AWS, and Okta. Documents are processed locally.
Installation and usage
The planned release is a portable archive for each supported platform. Download it from the repository’s Releases tab, extract it, and run the executable. The archive is designed to include Python, the required libraries, and English OCR data so users can run it without installing dependencies on the host.
Single document
macOS and Linux
./hyperscrub --input raw_document.pdf --output redacted_document.pdf --config config.yaml
Windows PowerShell
.\hyperscrub.exe --input raw_document.pdf --output redacted_document.pdf --config config.yaml
Batch directory processing
Batch mode was specified in the original design. The intended command uses a directory as input and a separate directory for the redacted copies.
./hyperscrub --input ./raw_logs_folder/ --output ./clean_exports/ --config presets/devops_audit.yaml
Configuration
Use regex patterns for structured values and plain-text keywords for names and terms. The example birthday rule matches any date written as MM/DD/YYYY, so narrow it when other dates should be preserved.
patterns:
  ssn: '\b\d{3}-\d{2}-\d{4}\b'
  birthday: '\b\d{2}/\d{2}/\d{4}\b'

keywords:
  - 'Splunk'
  - 'AWS'
  - 'Okta'
Architecture and trust model
HyperScrub is designed to process documents locally. Text extraction, OCR, and matching run on the host. The engine applies redactions to the matched page content and writes a separate PDF with visible redaction marks.
1. Inspect each page. Distribute pages to worker processes. Each worker checks for a native text layer and selects native extraction or local OCR.
2. Reconstruct and match lines. Collect words and their bounding boxes, group tokens by line, and match the configured patterns and keywords against reconstructed text. Map each match back to page coordinates. OCR coordinates are converted from image pixels to PDF page coordinates.
3. Collect redaction coordinates. Workers return page numbers and match rectangles to the controller. The controller owns the output document.
4. Apply redactions and save. The controller applies the collected redactions with PyMuPDF and saves a new file. One writer coordinates updates to the PDF objects and cross-reference table. The prototype saves with garbage collection and stream compression.
Technical security verification
Use test PDFs containing known sensitive values. Re-extract text from the redacted output, inspect the relevant PDF content, and render scanned pages to verify that targeted text is gone from the image regions. A raw byte search can serve as a supplementary check, since compressed or encoded streams may hide matches from it.

The original design calls for separately checking document metadata, embedded attachments, and form data. Page-content redaction and sanitization of those additional surfaces require separate implementation and verification.
Operational constraints
- Serial output. Page analysis can run on multiple cores, while the write pass remains serial. On large documents, measure analysis and output writing separately to see which phase limits speedup.
- OCR coverage and quality. Low resolution, skew, and character substitutions can break pattern matching. A selectable header can also cause the current page-level fallback to skip an embedded scan. The original design proposes a --force-ocr option for cases requiring another pass. Review low-quality scans and mixed-content pages before sharing.
- Fragmented native text. PDF generators can split a visually continuous value across tokens or insert invisible characters. The design calls for normalizing layout text before matching and testing that reconstructed matches still map to the correct coordinates.
- Over-redaction. Short keywords can match inside unrelated words. The design calls for whole-word matching by default and explicit rules for broader matching. Test for both missed matches and unwanted redactions.
Proposed repository layout
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
The original layout includes automated tests and security scanning in GitHub Actions. The proposed GDPR and HIPAA preset names identify use cases. Compliance depends on the full workflow and its controls. The original draft considered MIT and Apache 2.0 for the license.
Security policy
Report vulnerabilities privately through the repository’s security reporting channel once configured. Include reproduction steps and a synthetic or sanitized PDF that demonstrates the issue. Keep sensitive source documents out of public issues.
