# Evident Technologies

**Evident Technologies** is a professional-grade evidence processing platform
for video, documents, and records—built for verification, chain of custody, and
court-ready analysis.

The system is designed to help litigants, advocates, and legal teams work with
**body-worn camera footage, discovery documents, and public-records data** in a
way that preserves **evidentiary integrity, transparency, and chain of
custody**—without reliance on cloud processing.

> Evidence is processed locally. Originals are preserved. Analysis is
> reproducible.

Note: This repository includes governance guidance for AI assistants in
`.github/copilot-instructions.md` and `copilot-instructions.md`.

---

## Purpose & Design Principles

Evident is built around several non-negotiable principles:

- **Local-first processing**  
  Evidence remains on the user’s system unless explicitly shared.

- **Integrity over automation**  
  The platform assists analysis; it does not replace legal judgment.

- **Chain of custody awareness**  
  Originals are immutable. Derivatives are traceable.

- **Civil-rights focused workflows**  
  Optimized for constitutional, public-accountability, and discovery review
  contexts.

- **Transparency and auditability**  
  Processing steps are inspectable and reproducible.

---

## Core Capabilities

### Evidence Processing

- Body-worn camera (BWC) and dash-cam video ingestion
- Audio transcription using local speech-to-text models
- Document OCR for PDFs and scanned records
- Metadata extraction and normalization

### Analysis & Organization

- Searchable transcripts and documents
- Timeline construction across multiple evidence sources
- Cross-referencing between video, reports, and records
- Structured notes and annotations

### Integrity & Reporting

- Hash-based file verification
- Immutable original evidence handling
- Audit-friendly processing records
- Court-ready exports (transcripts, reports, exhibits)

---

## Intended Use

Evident is intended for:

- Civil-rights and constitutional litigation
- Public-records analysis (e.g., OPRA / FOIA)
- Discovery review and evidence organization
- Pro se litigants, advocates, and legal professionals

It is **not** designed to provide legal advice or automated legal conclusions.

---

## Quick Start (Local Development)

### Requirements

- Python 3.9+
- FFmpeg (for media handling)
- Tesseract OCR (for document processing)

### Setup

```bash
pip install -r requirements.txt
python app.py
```

---

## Local linting

Run these checks locally before creating a PR to catch formatting and lint issues (these match CI):

- Prettier (formatting):

```bash
npx prettier --check .
```

- Stylelint (CSS):

```bash
npx stylelint "**/*.css"
```

- HTMLHint (HTML):

```bash
npx htmlhint "**/*.html"
```

