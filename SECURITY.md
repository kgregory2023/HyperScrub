# Security Policy

## Project status

HyperScrub is currently a pre-alpha project. No release is considered
production-ready, and the current implementation should only be tested with
synthetic documents.

## Supported versions

HyperScrub has not published a stable release. Security fixes are applied to the
latest version of the `main` branch during active development.

| Version | Supported |
| --- | --- |
| `main` | Yes |
| Earlier commits | No |
| Published releases | None available |

## Reporting a vulnerability

Please do not report security vulnerabilities through public GitHub issues.

Use GitHub's private vulnerability reporting feature:

1. Open the repository's **Security and quality** tab.
2. Select **Advisories**.
3. Select **Report a vulnerability**.
4. Include reproduction steps and the expected security impact.

Use synthetic or sanitized documents in vulnerability reports. Do not upload
documents containing genuine personal, financial, medical, authentication, or
confidential business information.

A useful report should include:

- the affected commit or version;
- operating system and Python version;
- a minimal synthetic PDF and YAML configuration;
- the command that triggered the problem;
- the observed and expected behavior; and
- whether sensitive content remains visually visible, extractable, or otherwise
  recoverable.

## Security-relevant issues

Examples include:

- targeted content remaining extractable after redaction;
- redacted content being recoverable from PDF objects or streams;
- a pattern or keyword bypass affecting supported searchable PDFs;
- unintended modification or deletion of files;
- arbitrary file access or path-handling vulnerabilities;
- denial-of-service conditions caused by malformed documents; and
- dependency or build-process vulnerabilities.

## Current limitations

The current implementation supports searchable PDFs only. OCR, scanned-document
processing, metadata sanitization, attachment sanitization, form-data
sanitization, batch processing, and multiprocessing are not implemented.

Failures involving these planned features should be submitted as feature
requests unless they also expose a vulnerability in currently supported
functionality.
