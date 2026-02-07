This directory contains full license texts for all third-party software used in
Evident Legal Technologies.

## Required Licenses

### MIT License Projects:

- OpenAI Whisper
- pyannote.audio
- spaCy
- Flask-Login
- Flask-CORS
- SQLAlchemy
- Bootstrap
- Bootstrap Icons
- Pydub
- python-docx
- Stripe Python SDK

### BSD-3-Clause License Projects:

- Flask
- Flask-SQLAlchemy
- Werkzeug
- Pandas
- NumPy
- ReportLab

### Apache 2.0 License Projects:

- Hugging Face Transformers
- SentenceTransformers
- cryptography (dual licensed)

### LGPL 2.1 License:

- FFmpeg (ensure using LGPL build, not GPL)

### PostgreSQL License:

- PostgreSQL

### Public Domain:

- CourtListener (CC0 1.0 Universal)

---

## How to Add New License

When adding a new dependency:

1. Identify the license (check GitHub, PyPI, or project website)
2. Download the full license text
3. Save as `LICENSES/<project-name>-LICENSE.txt`
4. Update `THIRD-PARTY-LICENSES.md`
5. Update `ATTRIBUTION.md`
6. Add to export manifest in `data_rights.py`

---

## Compliance Verification

Before each release:

- [ ] Verify all dependencies have licenses in this directory
- [ ] Check for any license changes in updated dependencies
- [ ] Ensure ATTRIBUTION.md is current
- [ ] Verify export manifests include all tools

---

See also:

- THIRD-PARTY-LICENSES.md - Complete license documentation
- ATTRIBUTION.md - Acknowledgments and credits
- COPYRIGHT-QUICK-START.md - Copyright compliance guide
