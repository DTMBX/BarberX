# Docket Intake & Integrity Architecture v2.0

**Date:** January 19, 2026  
**Status:** 🔴 Action Required  
**Author:** Design & Architecture Agent

---

## Executive Summary

Critical integrity issues identified in current docket system:

- **Duplicate data directories** (`_data/docket/` and `_data/docket_index/`)
- **Inconsistent path references** between directories
- **Missing unified validation layer**
- **No automated integrity verification**

---

## 1. Current State Analysis

### 1.1 Directory Structure (Problematic)

```
_data/
├── docket/              # Source of truth? 13 files
│   └── {case-id}.yml    # Uses: /assets/cases/{id}/docket/*.pdf
├── docket_index/        # Duplicate? 13 files
│   └── {case-id}.yml    # Uses: /cases/{id}/filings/*.pdf
├── checksums/           # 9 files (incomplete coverage)
│   └── {case-id}.yml    # SHA-256 hashes
├── analysis/            # AI analysis outputs
└── cases-map.yml        # Case metadata mapping

_inbox/
├── {case-id}/           # Intake staging area
│   ├── *.pdf            # Raw uploads
│   └── metadata.yml     # Optional metadata
└── README.md
```

### 1.2 Critical Issues Identified

| Issue                   | Severity    | Impact                                 |
| ----------------------- | ----------- | -------------------------------------- |
| Dual docket directories | 🔴 Critical | Data inconsistency, maintenance burden |
| Different path formats  | 🔴 Critical | Broken file links, 404 errors          |
| Missing checksums       | 🟠 High     | Cannot verify file integrity           |
| No schema validation    | 🟠 High     | Invalid data can enter system          |
| Incomplete audit trail  | 🟡 Medium   | Cannot trace file provenance           |

### 1.3 Path Inconsistency Detail

**`_data/docket/` format:**

```yaml
file: /assets/cases/usdj-1-22-cv-06206/docket/20250827-motion.pdf
```

**`_data/docket_index/` format:**

```yaml
file: /cases/usdj-1-22-cv-06206/filings/20250827-motion.pdf
```

This creates confusion about canonical file locations.

---

## 2. Proposed Architecture

### 2.1 Unified Directory Structure

```
_data/
├── docket/                    # SINGLE source of truth
│   └── {case-id}.yml          # Standardized docket entries
├── checksums/                 # File integrity verification
│   └── {case-id}.yml          # SHA-256 for all files
├── audit/                     # NEW: Audit trail logs
│   └── {case-id}.yml          # Provenance tracking
├── schemas/                   # NEW: Validation schemas
│   ├── docket-entry.schema.json
│   └── case-metadata.schema.json
└── cases-map.yml              # Case metadata

_inbox/
├── {case-id}/                 # Staging area
│   ├── *.pdf                  # Uploads
│   └── intake-manifest.yml    # NEW: Required manifest
└── .intake-rules.yml          # NEW: Validation rules

assets/cases/                  # CANONICAL file storage
└── {case-id}/
    └── docket/                # All PDFs here
        └── {date}-{slug}.pdf

# DEPRECATED - To be removed after migration
_data/docket_index/            # Remove after consolidation
```

### 2.2 Standardized Docket Entry Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "docket-entry.schema.json",
  "title": "Docket Entry",
  "type": "object",
  "required": ["id", "date", "type", "title", "file"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[0-9]{8}-[a-z0-9-]+$",
      "description": "Format: YYYYMMDD-slug"
    },
    "date": {
      "type": "string",
      "format": "date",
      "description": "ISO 8601 date"
    },
    "type": {
      "type": "string",
      "enum": [
        "Order",
        "Motion",
        "Brief",
        "Filing",
        "Notice",
        "Opinion",
        "Judgment",
        "Subpoena",
        "Summons",
        "Other"
      ]
    },
    "title": {
      "type": "string",
      "minLength": 5,
      "maxLength": 200
    },
    "file": {
      "type": "string",
      "pattern": "^/assets/cases/[a-z0-9-]+/docket/[a-z0-9-]+\\.pdf$"
    },
    "court_stamp": {
      "type": ["string", "null"],
      "format": "date-time"
    },
    "checksum": {
      "type": "string",
      "pattern": "^sha256:[a-f0-9]{64}$"
    },
    "notes": {
      "type": "string"
    },
    "intake_date": {
      "type": "string",
      "format": "date-time"
    },
    "source": {
      "type": "string",
      "enum": ["manual", "ecf", "mail", "fax", "email"]
    }
  }
}
```

### 2.3 Intake Manifest Schema

```yaml
# _inbox/{case-id}/intake-manifest.yml
case_id: usdj-1-22-cv-06206
intake_date: 2026-01-19T14:30:00Z
source: ecf
operator: system
files:
  - filename: 20260119-order-granting-motion.pdf
    type: Order
    title: "Order Granting Motion to Compel"
    date: "2026-01-19"
    checksum: sha256:abc123...
  - filename: 20260119-memorandum.pdf
    type: Filing
    title: "Memorandum in Support"
    date: "2026-01-19"
    checksum: sha256:def456...
validation:
  schema_valid: true
  checksums_verified: true
  duplicates_checked: true
```

---

## 3. Integrity Verification System

### 3.1 Checksum Generation Script

```python
#!/usr/bin/env python3
"""
scripts/generate-checksums.py
Generate SHA-256 checksums for all docket PDFs
"""
import hashlib
import yaml
from pathlib import Path

def generate_checksum(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"

def process_case(case_id: str, assets_path: Path, output_path: Path):
    docket_dir = assets_path / case_id / 'docket'
    if not docket_dir.exists():
        return

    checksums = []
    for pdf in sorted(docket_dir.glob('*.pdf')):
        checksums.append({
            'file': f"/assets/cases/{case_id}/docket/{pdf.name}",
            'checksum': generate_checksum(pdf),
            'size_bytes': pdf.stat().st_size,
            'verified_at': datetime.now().isoformat()
        })

    output_file = output_path / f"{case_id}.yml"
    with open(output_file, 'w') as f:
        yaml.dump(checksums, f, default_flow_style=False)

if __name__ == '__main__':
    assets = Path('assets/cases')
    output = Path('_data/checksums')
    output.mkdir(exist_ok=True)

    for case_dir in assets.iterdir():
        if case_dir.is_dir():
            process_case(case_dir.name, assets, output)
```

### 3.2 Validation Script

```python
#!/usr/bin/env python3
"""
scripts/validate-docket.py
Validate docket entries against schema and verify file integrity
"""
import json
import yaml
import jsonschema
from pathlib import Path

def load_schema():
    with open('_data/schemas/docket-entry.schema.json') as f:
        return json.load(f)

def validate_docket_file(filepath: Path, schema: dict) -> list:
    errors = []
    with open(filepath) as f:
        entries = yaml.safe_load(f)

    for i, entry in enumerate(entries):
        try:
            jsonschema.validate(entry, schema)
        except jsonschema.ValidationError as e:
            errors.append(f"{filepath.name}[{i}]: {e.message}")

        # Verify file exists
        pdf_path = Path(entry['file'].lstrip('/'))
        if not pdf_path.exists():
            errors.append(f"{filepath.name}[{i}]: File not found: {entry['file']}")

    return errors

def main():
    schema = load_schema()
    all_errors = []

    for docket_file in Path('_data/docket').glob('*.yml'):
        errors = validate_docket_file(docket_file, schema)
        all_errors.extend(errors)

    if all_errors:
        print("❌ Validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        exit(1)
    else:
        print("✅ All docket entries valid")
        exit(0)

if __name__ == '__main__':
    main()
```

---

## 4. GitHub Actions Workflow

### 4.1 Automated Intake Pipeline

```yaml
# .github/workflows/docket-intake.yml
name: Docket Intake Pipeline

on:
  push:
    paths:
      - '_inbox/**'
  workflow_dispatch:
    inputs:
      case_id:
        description: 'Case ID to process'
        required: true

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install pyyaml jsonschema

      - name: Validate intake manifests
        run: python scripts/validate-intake.py

      - name: Check for duplicates
        run: python scripts/check-duplicates.py

      - name: Generate checksums
        run: python scripts/generate-checksums.py

      - name: Validate all dockets
        run: python scripts/validate-docket.py

  process:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Process intake files
        run: python scripts/process-intake.py

      - name: Move files to canonical location
        run: python scripts/move-to-assets.py

      - name: Update docket index
        run: python scripts/update-docket.py

      - name: Create PR with changes
        uses: peter-evans/create-pull-request@v6
        with:
          title: {% raw %}"📁 Docket Intake: ${{ github.event.inputs.case_id || 'Batch' }}"{% endraw %}
          body: |
            Automated docket intake processing.

            ## Files Added
            {% raw %}${{ steps.process.outputs.files_added }}{% endraw %}

            ## Validation
            - ✅ Schema validated
            - ✅ Checksums generated
            - ✅ No duplicates found
          branch: docket-intake/${{ github.run_id }}
```

### 4.2 Integrity Verification (Scheduled)

```yaml
# .github/workflows/verify-integrity.yml
name: Docket Integrity Verification

on:
  schedule:
    - cron: "0 6 * * *" # Daily at 6 AM
  workflow_dispatch:

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Verify checksums
        run: python scripts/verify-checksums.py

      - name: Check for orphaned files
        run: python scripts/find-orphans.py

      - name: Validate all schemas
        run: python scripts/validate-all.py

      - name: Generate integrity report
        run: python scripts/integrity-report.py

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: integrity-report
          path: reports/integrity-*.md
```

---

## 5. Migration Plan

### Phase 1: Consolidation (Week 1)

1. **Backup current state**

   ```bash
   cp -r _data/docket _data/docket.bak
   cp -r _data/docket_index _data/docket_index.bak
   ```

2. **Audit current duplicates**

   ```bash
   python scripts/audit-duplicates.py > reports/duplicate-audit.md
   ```

3. **Consolidate to single `_data/docket/`**
   - Use `_data/docket/` as canonical (has correct `/assets/cases/` paths)
   - Merge any unique entries from `docket_index/`
   - Add missing fields (`checksum`, `intake_date`, `source`)

4. **Remove deprecated directory**
   ```bash
   rm -rf _data/docket_index
   ```

### Phase 2: Validation Layer (Week 2)

1. Create `_data/schemas/` directory
2. Add JSON Schema files
3. Create validation scripts
4. Run initial validation, fix errors

### Phase 3: Automation (Week 3)

1. Set up GitHub Actions workflows
2. Create intake processing scripts
3. Test with sample intake
4. Document procedures

### Phase 4: Audit Trail (Week 4)

1. Create `_data/audit/` structure
2. Backfill audit entries for existing files
3. Implement audit logging in intake scripts

---

## 6. Implementation Priority Matrix

| Priority | Task                            | Effort | Impact   |
| -------- | ------------------------------- | ------ | -------- |
| 🔴 P0    | Consolidate docket directories  | 2 hrs  | Critical |
| 🔴 P0    | Fix path inconsistencies        | 1 hr   | Critical |
| 🔴 P1    | Create JSON Schema              | 1 hr   | High     |
| 🔴 P1    | Add validation script           | 2 hrs  | High     |
| 🟠 P2    | Generate all checksums          | 1 hr   | High     |
| 🟠 P2    | GitHub Actions intake workflow  | 4 hrs  | High     |
| 🟠 P2    | Integrity verification workflow | 2 hrs  | Medium   |
| 🟡 P3    | Audit trail system              | 4 hrs  | Medium   |
| 🟡 P3    | Documentation updates           | 2 hrs  | Medium   |

---

## 7. Immediate Action Items

### Today (P0 Critical)

1. **Run this command to identify differences:**

   ```bash
   diff -q _data/docket _data/docket_index
   ```

2. **Verify canonical path format:**
   All files should use: `/assets/cases/{case-id}/docket/{filename}.pdf`

3. **Create backup before changes:**
   ```bash
   git stash
   tar -czvf docket-backup-$(date +%Y%m%d).tar.gz _data/docket _data/docket_index
   ```

### This Week (P1 High)

1. Create `_data/schemas/docket-entry.schema.json`
2. Create `scripts/validate-docket.py`
3. Remove `_data/docket_index/` after verification
4. Update any templates referencing old paths

---

## Appendix A: Canonical Path Reference

| Component        | Canonical Path                                    |
| ---------------- | ------------------------------------------------- |
| Case docket YAML | `_data/docket/{case-id}.yml`                      |
| Checksums YAML   | `_data/checksums/{case-id}.yml`                   |
| PDF files        | `assets/cases/{case-id}/docket/{date}-{slug}.pdf` |
| Intake staging   | `_inbox/{case-id}/`                               |
| Case page        | `_cases/{case-id}.md`                             |

## Appendix B: Document Type Enum

```yaml
valid_types:
  - Order # Court orders
  - Motion # Motions filed
  - Brief # Legal briefs
  - Filing # General filings
  - Notice # Notices
  - Opinion # Court opinions
  - Judgment # Final judgments
  - Subpoena # Subpoenas
  - Summons # Summons
  - Other # Catch-all
```
