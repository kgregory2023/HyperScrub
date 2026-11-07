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

<details>
<summary>Page worker and engine controller from the original design</summary>

This is the original code sketch transcribed from the PDF. The extraction preserves the draft’s rough formatting. It shows the earlier `pytesseract` approach, while the portable release design uses integrated OCR.

```text
import fitz # PyMuPDF
import re
import yaml
import io
import os
from pathlib import Path
from PIL import Image
import pytesseract
from concurrent.futures import ProcessPoolExecutor

# --- WORKER FUNCTION (Executed in parallel across separate CPU cores) ---
def _process_single_page_worker(pdf_path, page_num, pattern_strings, keyword_list):
   """Processes a single page in absolute isolation to prevent cross-process memory leaks."""
   # Re-compile regex patterns inside the worker process (regex objects aren't picklable)
   compiled_patterns = {cat: re.compile(pat) for cat, pat in pattern_strings.items()}

  # Open a lightweight, thread-safe read-only handle to the PDF file
  doc = fitz.open(pdf_path)
  page = doc[page_num]

  # 1. Gated Execution: Check for native text layer first
  has_native_text = bool(page.get_text().strip())

  if has_native_text:
      # Digital Native Path (Executes in milliseconds)
      for category, pattern in compiled_patterns.items():
         text_instances = page.search_for(pattern, use_regex=True)
         for inst in text_instances:
            page.add_redact_annot(inst, fill=(0, 0, 0))

     for keyword in keyword_list:
        text_instances = page.search_for(keyword, flags=fitz.TEXTFLAGS_SEARCH)
        for inst in text_instances:
           page.add_redact_annot(inst, fill=(0, 0, 0))
  else:
     # Scanned Image Path (In-Memory OCR Process)
     pix = page.get_pixmap(dpi=300)
     img = Image.open(io.BytesIO(pix.tobytes("png")))
     ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

     # Line reconstruction optimization block
     lines = {}
     for i in range(len(ocr_data['text'])):
        word = ocr_data['text'][i].strip()
       if not word: continue
       line_key = (ocr_data['block_num'][i], ocr_data['par_num'][i], ocr_data['line_num'][i])
       if line_key not in lines: lines[line_key] = []
       lines[line_key].append({
            'text': word, 'left': ocr_data['left'][i], 'top': ocr_data['top'][i],
            'width': ocr_data['width'][i], 'height': ocr_data['height'][i]
       })

    scale_x, scale_y = page.rect.width / pix.width, page.rect.height / pix.height
    keyword_patterns = [re.compile(rf'\b{re.escape(kw)}\b', re.IGNORECASE) for kw in
keyword_list]
    all_patterns = list(compiled_patterns.values()) + keyword_patterns

     for words in lines.values():
        line_string = " ".join([w['text'] for w in words])
        for pattern in all_patterns:
           for match in pattern.finditer(line_string):
              start_char, end_char = match.start(), match.end()
              current_char_idx = 0
              match_rects = []

            for w in words:
               word_len = len(w['text'])
               word_start = current_char_idx
               word_end = word_start + word_len

               if not (word_end <= start_char or word_start >= end_char):
                   rect = fitz.Rect(w['left']*scale_x, w['top']*scale_y,
                               (w['left']+w['width'])*scale_x, (w['top']+w['height'])*scale_y)
                   match_rects.append(rect)
               current_char_idx += word_len + 1

            if match_rects:
               combined_rect = match_rects[0]
               for r in match_rects[1:]: combined_rect |= r
               page.add_redact_annot(combined_rect, fill=(0, 0, 0))

   # Compile the coordinates of all added redaction bounding boxes
   redaction_rects = [annot.rect for annot in page.annots() if annot.type[0] == 11] # 11 is Redact
type
   doc.close()

  return page_num, redaction_rects
# --- MASTER ENGINE CONTROLLER ---
def hyperscrub_multiprocess_engine(input_path, output_path, config_path=None):
   """Orchestrates parallel extraction pipelines and safely handles byte-stripping write actions."""
   # 1. Load config layout maps simply
   default_patterns = {
      "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
      "birthday": r'\b\d{2}/\d{2}/\d{4}\b',
   }
   keywords = []

  if config_path and Path(config_path).exists():
      with open(config_path, 'r') as file:
         config_data = yaml.safe_load(file) or {}
         default_patterns.update(config_data.get('patterns', {}))
         keywords = config_data.get('keywords', [])

  # Open document to count structural workload size
  master_doc = fitz.open(input_path)
  total_pages = len(master_doc)

  # 2. Parallel Processing Distribution Phase
  # Automatically scales worker allocation to maximize active hardware threads
  workers = min(os.cpu_count() or 4, total_pages)
  print(f"[HyperScrub] Processing {total_pages} pages across {workers} parallel worker cores...")

  all_redaction_maps = {}
  with ProcessPoolExecutor(max_workers=workers) as executor:
     futures = [
        executor.submit(_process_single_page_worker, input_path, p_num, default_patterns,
keywords)
        for p_num in range(total_pages)
     ]
     for fut in futures:
        p_num, rect_list = fut.result()
        all_redaction_maps[p_num] = rect_list

  # 3. Serialization & Structural Byte-Stripping Phase
  # Parallel processes find targets, but the final file MUST be written sequentially to avoid race
conditions.
  print("[HyperScrub] Applying structural byte-stripping updates to the file stream...")
  for page_num, rects in all_redaction_maps.items():
     page = master_doc[page_num]
     for r in rects:
       page.add_redact_annot(r, fill=(0, 0, 0))
     # This core C-level hook completely purges text bytes from the file layout maps
     page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_ALL)

  # Clean file structural duplicates and save with stream inflation compression
  master_doc.save(output_path, garbage=4, deflate=True)
  master_doc.close()
  print(f"[HyperScrub] Complete! Optimized document saved securely to: {output_path}")
```

</details>
