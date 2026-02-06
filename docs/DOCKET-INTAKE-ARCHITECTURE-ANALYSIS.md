# Docket Intake & Integrity System - Architecture Analysis Report

**Date:** January 19, 2026  
**Prepared by:** Design & Architecture Agent  
**Platform:** Evident.info - Citizen-Led Legal Documentation Platform

--

## Executive Summary

This report provides a comprehensive analysis of the Evident.info docket intake
system, identifying critical integrity issues, architectural inconsistencies,
and providing prioritized recommendations for improvement. The system currently
supports 10+ active legal cases with hundreds of court filings, making data
integrity paramount.

--

## 1. Current State Analysis

### 1.1 System Overview

The docket intake system is a Jekyll-based static site architecture with
automated PDF processing capabilities:

```
┌─────────────────────────────────────────────────────────────────┐
│                     INTAKE WORKFLOW                             │
├─────────────────────────────────────────────────────────────────┤
│  _inbox/              │  GitHub Actions     │  cases/<slug>/    │
│  ├── *.pdf            │  ──────────────────►│  └── filings/     │
│  └── <case-slug>/     │  docket-intake.js   │      └── *.pdf    │
│      └── *.pdf        │                     │                   │
├─────────────────────────────────────────────────────────────────┤
│                     DATA STORES                                 │
├─────────────────────────────────────────────────────────────────┤
│  _data/cases-map.yml    → Docket number → case slug mapping     │
│  _data/docket/*.yml     → Legacy docket metadata (deprecated?)  │
│  _data/docket_index/*.yml → Current docket index files          │
│  _data/checksums/*.yml  → SHA256 file checksums                 │
│  _cases/*.md            → Case front matter & documentation     │
│  cases/<slug>/docket/   → Duplicate PDF storage (!)             │
│  cases/<slug>/filings/  → Canonical filing storage              │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Current Data Models

#### Case Map Schema (\_data/cases-map.yml)

```yaml
# Docket number → case slug mapping
A-000313-25: a-000313-25
ATL-L-002794-25: atl-l-002794-25
1:22-cv-06206-KMW-EAP: usdj-1-22-cv-06206
```

#### Docket Entry Schema (\_data/docket_index/\*.yml)

```yaml
- id: 2026-01-10-2026-01-10_Order_order-dismissing-first-otsc
  date: '2026-01-10'
  type: Order
  title: 2026 01 10 Order order dismissing first otsc
  file: /cases/atl-l-003252-25/filings/2026-01-10_Order_order-dismissing-first-otsc.pdf
  court_stamp: null
  notes: Scanned by audit
```

#### Checksum Schema (\_data/checksums/\*.yml)

```yaml
20251207-verified-complaint-and-cis.pdf: 67d3cfc8c38de145520eaea517fb92390e4254e67004554eceb9bdea9467b7f7
```

### 1.3 Key Components Identified

| Component                    | Location | Purpose                          | Status             |
| ---------------------------- | -------- | -------------------------------- | ------------------ |
| `docket-intake.js`           | scripts/ | Primary automated PDF intake     | ✅ Active          |
| `batch-pdf-intake.js`        | scripts/ | Legacy batch upload (deprecated) | ⚠️ Legacy          |
| `validate-docket-files.js`   | scripts/ | Pre-commit validation            | ✅ Active          |
| `validate-case-integrity.js` | scripts/ | Case folder validation           | ✅ Active          |
| `generate-checksums.js`      | tools/   | SHA256 checksum generation       | ✅ Active          |
| `check-docket-integrity.ps1` | scripts/ | PowerShell diagnostics           | ⚠️ Diagnostic only |
| `enforce-filing-schema.js`   | tools/   | Filename normalization           | ✅ Active          |
| `repair-docket-system.js`    | scripts/ | One-time repair utility          | ⚠️ Emergency       |

### 1.4 Intake Workflow (Current)

1. **Drop PDFs** → `_inbox/` or `_inbox/<case-slug>/`
2. **Git commit & push** → Triggers GitHub Actions
3. **`docket-intake.js` runs:**
   - Scans `_inbox/` and `assets/uploads/`
   - Extracts docket number from filename patterns
   - Maps docket → case slug via `_data/cases-map.yml`
   - Moves PDF to `cases/<slug>/filings/`
   - Renames to `YYYY-MM-DD_Type_description.pdf` format
   - Updates `_data/docket_index/<slug>.yml`
   - Extracts court stamp (attempts OCR)
   - Generates placeholder PDFs if missing
4. **PR created** for review
5. **Merge** → Site rebuilds via Jekyll

--

## 2. Integrity Issues Identified

### 2.1 Critical Issues 🔴

#### Issue #1: Duplicate File Storage Locations

**Severity:** CRITICAL

Files exist in **three separate locations** for the same case:

| Location                      | Example for ATL-L-003252-25 |
| ----------------------------- | --------------------------- |
| `cases/<slug>/filings/`       | 50 PDFs (canonical)         |
| `cases/<slug>/docket/`        | 74 PDFs (duplicate/legacy)  |
| `assets/cases/<slug>/docket/` | Referenced in old YAML      |

**Impact:**

- Storage bloat (2-3x duplication)
- Path confusion in docket YAML files
- Risk of file version divergence

**Evidence:**

```
cases/atl-l-003252-25/filings/   → 50 files
cases/atl-l-003252-25/docket/   → 74 files (many duplicates with different naming)
```

#### Issue #2: Inconsistent File Path References

**Severity:** CRITICAL

Docket YAML files reference **inconsistent path formats:**

```yaml
# _data/docket/atl-l-003252-25.yml references:
file: /assets/cases/atl-l-003252-25/docket/20251207-verified-complaint.pdf

# _data/docket_index/atl-l-003252-25.yml references:
file: /cases/atl-l-003252-25/filings/2026-01-10_Order_order-dismissing.pdf
```

**Impact:** Broken links, 404 errors, inconsistent user experience

#### Issue #3: Duplicate Docket Data Directories

**Severity:** HIGH

Two parallel docket data directories exist:

- `_data/docket/` (13 files)
- `_data/docket_index/` (13 files)

Both contain similar but **non-identical** content for the same cases.

#### Issue #4: Missing Audit Trail for File Changes

**Severity:** HIGH

No systematic tracking of:

- When files were added/modified
- Who uploaded files
- File provenance chain
- Version history

### 2.2 High Priority Issues 🟠

#### Issue #5: Inconsistent Filename Formats

Multiple naming conventions in use:

```
20251207-verified-complaint-and-cis.pdf          # YYYYMMDD-name.pdf
2025-12-27_Motion_proposed-amended-complaint.pdf  # YYYY-MM-DD_Type_name.pdf
12-07-2025-dtb-certification-of-facts.pdf         # MM-DD-YYYY-name.pdf (!)
```

#### Issue #6: Duplicate IDs in Docket YAML

The `validate-case-integrity.js` identifies but doesn't auto-fix:

```javascript
const duplicateIds = ids.filter((id, idx) => ids.indexOf(id) !== idx);
// Found in docket_index files: repeated IDs like "2025-12-23-2025-12-23_Filing_..."
```

#### Issue #7: No Schema Validation

No JSON Schema or formal validation beyond runtime checks. Validation is:

- Runtime JavaScript (can be bypassed)
- Inconsistent between scripts
- Missing for front matter in `_cases/*.md`

#### Issue #8: Orphaned Files

Files exist that aren't registered in any docket YAML:

- Identified by `validate-case-integrity.js`
- No automated cleanup mechanism

### 2.3 Medium Priority Issues 🟡

#### Issue #9: Court Stamp Extraction Failures

```javascript
// docket-intake.js
courtStamp = getCourtStamp(destPath);
// Returns null for many files - no fallback verification
```

#### Issue #10: No Backup/Recovery Strategy

- No automated backups before destructive operations
- `repair-docket-system.js` doesn't create rollback points
- Git history is only safety net

#### Issue #11: Missing GitHub Actions Workflow for Intake

The `pages.yml` workflow only builds Jekyll - no docket intake automation:

```yaml
# .github/workflows/pages.yml - only does build/deploy
# Missing: docket-intake job
```

--

## 3. Architecture Recommendations

### 3.1 Proposed Folder Structure

```
Evident.info/
├── _data/
│   ├── cases-map.yml           # Docket → slug mapping
│   ├── cases-schema.json       # NEW: JSON Schema for validation
│   ├── docket/                  # DEPRECATED: Remove after migration
│   └── docket_index/           # RENAME TO: docket/
│       └── <slug>.yml          # Consolidated docket metadata
│
├── _cases/                      # Case definitions (Jekyll collection)
│   └── <slug>.md               # Case front matter & content
│
├── _inbox/                      # Intake staging area
│   ├── .gitkeep
│   ├── README.md
│   └── <slug>/                 # Case-specific inbox folders
│       └── *.pdf
│
├── cases/                       # PUBLIC: Served case content
│   └── <slug>/
│       ├── index.md            # Case landing page
│       ├── docket.yml          # REMOVE: Migrate to _data/docket/
│       └── filings/            # CANONICAL: All PDFs here
│           └── *.pdf
│
├── _data/
│   ├── audit/                  # NEW: Audit trail logs
│   │   └── <slug>-audit.yml
│   └── checksums/              # KEEP: SHA256 verification
│       └── <slug>.yml
│
└── scripts/
    ├── docket-intake.js        # ENHANCE: Add validation layer
    └── integrity/               # NEW: Integrity tooling
        ├── validate-all.js
        ├── migrate-legacy.js
        └── generate-audit.js
```

### 3.2 Data Validation Layer Design

#### Proposed JSON Schema for Docket Entries

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://Evident.info/schemas/docket-entry.json",
  "title": "Docket Entry",
  "type": "object",
  "required": ["id", "date", "type", "title", "file"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "description": "Unique identifier for this filing"
    },
    "date": {
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
      "description": "Filing date in YYYY-MM-DD format"
    },
    "type": {
      "type": "string",
      "enum": [
        "Filing",
        "Order",
        "Notice",
        "Brief",
        "Exhibit",
        "Motion",
        "Complaint",
        "Certification",
        "Proof of Service",
        "Request",
        "Proposed Order",
        "Other"
      ],
      "description": "Document type classification"
    },
    "title": {
      "type": "string",
      "minLength": 3,
      "maxLength": 200,
      "description": "Human-readable document title"
    },
    "file": {
      "type": "string",
      "pattern": "^/cases/[a-z0-9-]+/filings/[A-Za-z0-9_-]+\\.pdf$",
      "description": "Canonical file path"
    },
    "court_stamp": {
      "type": ["string", "null"],
      "description": "Extracted court stamp date/ID"
    },
    "sha256": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "description": "SHA256 checksum for integrity verification"
    },
    "intake_date": {
      "type": "string",
      "format": "date-time",
      "description": "When file was ingested into system"
    },
    "source": {
      "type": "string",
      "enum": ["inbox", "manual", "repair", "migration"],
      "description": "How file entered the system"
    },
    "notes": {
      "type": "string",
      "description": "Optional notes about the filing"
    }
  },
  "additionalProperties": false
}
```

### 3.3 Checksum/Hash Verification System

```
┌────────────────────────────────────────────────────────────┐
│                 INTEGRITY VERIFICATION FLOW                │
├────────────────────────────────────────────────────────────┤
│  1. INTAKE                                                 │
│     PDF → SHA256 hash → Store in docket entry + checksums/ │
│                                                            │
│  2. PERIODIC VERIFICATION (GitHub Actions)                 │
│     For each case:                                         │
│       - Load _data/checksums/<slug>.yml                    │
│       - Hash all files in cases/<slug>/filings/            │
│       - Compare hashes                                     │
│       - Flag mismatches in audit log                       │
│                                                            │
│  3. PRE-DEPLOY GATE                                        │
│     Jekyll build fails if integrity check fails            │
└────────────────────────────────────────────────────────────┘
```

### 3.4 Backup and Recovery Strategy

```yaml
# Proposed: .github/workflows/backup.yml
name: Weekly Backup & Integrity Check

on:
  schedule:
    - cron: '0 3 * * 0' # Sundays at 3 AM
  workflow_dispatch: {}

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Create backup archive
        run: |
          tar -czf backup-$(date +%Y%m%d).tar.gz \
            _data/docket/ \
            _data/checksums/ \
            _cases/ \
            cases/*/filings/

      - name: Upload to artifact storage
        uses: actions/upload-artifact@v4
        with:
          name: docket-backup-${{ github.run_id }}
          path: backup-*.tar.gz
          retention-days: 90

  integrity-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: node scripts/validate-case-integrity.js
      - run: node tools/generate-checksums.js -verify
```

--

## 4. Intake Workflow Improvements

### 4.1 Optimized Intake Process

```
┌─────────────────────────────────────────────────────────────┐
│              PROPOSED INTAKE WORKFLOW v2.0                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: UPLOAD                                             │
│  ───────────────                                            │
│  User drops PDF(s) to _inbox/<case-slug>/                   │
│  Filename: <YYYYMMDD>-<description>.pdf (optional format)   │
│                                                             │
│  STEP 2: PRE-VALIDATION (local, pre-commit)                 │
│  ──────────────────────────────────────────                 │
│  ✓ PDF magic number check (%PDF-)                           │
│  ✓ Minimum file size (>1KB)                                 │
│  ✓ Case slug exists in cases-map.yml                        │
│  ✓ No duplicate filenames in destination                    │
│                                                             │
│  STEP 3: GIT COMMIT & PUSH                                  │
│  ────────────────────────                                   │
│  Conventional commit: "intake(<slug>): <description>"       │
│                                                             │
│  STEP 4: GITHUB ACTIONS PROCESSING                          │
│  ─────────────────────────────────                          │
│  a) docket-intake.js processes _inbox/                      │
│  b) For each PDF:                                           │
│     - Extract date from filename or file metadata           │
│     - Classify document type (Order, Motion, etc.)          │
│     - Generate canonical filename                           │
│     - Compute SHA256 checksum                               │
│     - Move to cases/<slug>/filings/                         │
│     - Update _data/docket/<slug>.yml                        │
│     - Update _data/checksums/<slug>.yml                     │
│     - Log to _data/audit/<slug>-audit.yml                   │
│  c) Run integrity validation                                │
│  d) Create PR with summary                                  │
│                                                             │
│  STEP 5: REVIEW & MERGE                                     │
│  ───────────────────────                                    │
│  Human reviews:                                             │
│  - File classifications correct?                            │
│  - Dates accurate?                                          │
│  - No duplicates?                                           │
│  Merge triggers Jekyll rebuild                              │
│                                                             │
│  STEP 6: POST-DEPLOY VERIFICATION                           │
│  ────────────────────────────────                           │
│  - Verify PDFs accessible via URLs                          │
│  - Checksum verification                                    │
│  - Link checker on docket pages                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Automation Opportunities

| Task                    | Current               | Proposed Automation             |
| ----------------------- | --------------------- | ------------------------------- |
| PDF date extraction     | Filename pattern only | + PDF metadata + OCR fallback   |
| Document classification | Simple keyword match  | + ML-based classification       |
| Duplicate detection     | By filename only      | + SHA256 + fuzzy title matching |
| Court stamp extraction  | Basic text extraction | + OCR with NJ court patterns    |
| Broken link detection   | Manual                | + Automated link checker in CI  |
| Integrity verification  | On-demand script      | + Scheduled GitHub Action       |

### 4.3 Error Handling & Recovery

```javascript
// Proposed: Enhanced error handling in docket-intake.js

const IntakeError = {
  INVALID_PDF: 'INVALID_PDF',
  CASE_NOT_FOUND: 'CASE_NOT_FOUND',
  DUPLICATE_FILE: 'DUPLICATE_FILE',
  CHECKSUM_MISMATCH: 'CHECKSUM_MISMATCH',
  MOVE_FAILED: 'MOVE_FAILED',
};

async function processWithRecovery(pdfPath) {
  const backup = createTempBackup(pdfPath);

  try {
    await validatePdf(pdfPath);
    const result = await processIntake(pdfPath);
    await verifyIntegrity(result);
    removeTempBackup(backup);
    return { success: true, result };
  } catch (error) {
    await restoreFromBackup(backup);
    logIntakeError(pdfPath, error);
    return {
      success: false,
      error: error.code,
      quarantine: moveToQuarantine(pdfPath),
    };
  }
}
```

--

## 5. Implementation Priority Matrix

### 5.1 High Priority (Critical for Integrity) 🔴

| #   | Task                                            | Effort | Impact | Dependencies |
| --- | ----------------------------------------------- | ------ | ------ | ------------ |
| H1  | Consolidate duplicate PDF storage               | 4h     | HIGH   | None         |
| H2  | Unify `_data/docket/` and `_data/docket_index/` | 2h     | HIGH   | H1           |
| H3  | Fix inconsistent file path references           | 3h     | HIGH   | H1, H2       |
| H4  | Add JSON Schema validation                      | 4h     | HIGH   | H2           |
| H5  | Create GitHub Actions intake workflow           | 3h     | HIGH   | H4           |

### 5.2 Medium Priority (Workflow Improvements) 🟠

| #   | Task                                    | Effort | Impact | Dependencies |
| --- | --------------------------------------- | ------ | ------ | ------------ |
| M1  | Standardize filename format enforcement | 2h     | MEDIUM | H1           |
| M2  | Add audit trail logging                 | 3h     | MEDIUM | H5           |
| M3  | Implement checksum verification in CI   | 2h     | MEDIUM | H5           |
| M4  | Create backup workflow                  | 2h     | MEDIUM | None         |
| M5  | Add pre-commit hook for validation      | 1h     | MEDIUM | H4           |

### 5.3 Low Priority (Nice-to-Have) 🟢

| #   | Task                                | Effort | Impact | Dependencies |
| --- | ----------------------------------- | ------ | ------ | ------------ |
| L1  | ML-based document classification    | 8h     | LOW    | M2           |
| L2  | OCR-enhanced court stamp extraction | 6h     | LOW    | None         |
| L3  | Interactive intake dashboard        | 8h     | LOW    | M2           |
| L4  | Duplicate detection by content hash | 3h     | LOW    | M3           |

### 5.4 Recommended Implementation Order

```
Week 1: Foundation
├── H1: Consolidate PDF storage
├── H2: Unify docket directories
└── H3: Fix path references

Week 2: Validation
├── H4: JSON Schema validation
├── M1: Filename standardization
└── M5: Pre-commit hooks

Week 3: Automation
├── H5: GitHub Actions intake
├── M3: Checksum verification CI
└── M4: Backup workflow

Week 4: Audit & Polish
├── M2: Audit trail logging
└── Review & documentation
```

--

## 6. Specific Code/Config Recommendations

### 6.1 New Files to Create

#### 6.1.1 JSON Schema File

**Location:** `_data/schemas/docket-entry-schema.json`

See Section 3.2 for full schema.

#### 6.1.2 GitHub Actions Workflow

**Location:** `.github/workflows/docket-intake.yml`

```yaml
name: Docket Intake Processing

on:
  push:
    branches: [main]
    paths:
      - '_inbox/**'
      - 'assets/uploads/**'

permissions:
  contents: write
  pull-requests: write

jobs:
  intake:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run docket intake
        run: node scripts/docket-intake.js

      - name: Validate integrity
        run: node scripts/validate-case-integrity.js

      - name: Generate checksums
        run: node tools/generate-checksums.js

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          title: 'intake: Automated docket processing'
          commit-message: 'chore: Process docket intake files'
          branch: automated/docket-intake
          delete-branch: true
          body: |
            ## Automated Docket Intake

            This PR was automatically generated by the docket intake workflow.

            ### Changes
            - Processed files from `_inbox/`
            - Updated docket YAML files
            - Generated/updated checksums

            Please review file classifications and dates before merging.
```

#### 6.1.3 Audit Trail Schema

**Location:** `_data/audit/README.md` and example format

```yaml
# _data/audit/<slug>-audit.yml
# Audit trail for case: atl-l-003252-25

- timestamp: '2026-01-19T14:30:00Z'
  action: FILE_ADDED
  file: /cases/atl-l-003252-25/filings/2026-01-19_Motion_example.pdf
  sha256: abc123...
  source: inbox
  user: github-actions[bot]

- timestamp: '2026-01-19T14:30:01Z'
  action: DOCKET_UPDATED
  file: _data/docket/atl-l-003252-25.yml
  entries_added: 1
  entries_total: 51
```

### 6.2 Files to Modify

#### 6.2.1 Enhanced docket-intake.js

Key additions needed:

1. Schema validation before writing YAML
2. Checksum generation inline
3. Audit log writing
4. Quarantine directory for failures

```javascript
// Add to top of docket-intake.js
import Ajv from 'ajv';
import crypto from 'crypto';

const ajv = new Ajv();
const schema = JSON.parse(fs.readFileSync('_data/schemas/docket-entry-schema.json'));
const validateEntry = ajv.compile(schema);

// Add to processIntake function
const sha256 = crypto.createHash('sha256')
  .update(fs.readFileSync(destPath))
  .digest('hex');

const entry = {
  id,
  date,
  type,
  title,
  file: fileUrl,
  sha256,  // NEW
  intake_date: new Date().toISOString(),  // NEW
  source: 'inbox',  // NEW
  court_stamp: courtStamp,
  notes: 'Intake: automated processing'
};

// Validate before saving
if (!validateEntry(entry)) {
  console.error('Schema validation failed:', validateEntry.errors);
  moveToQuarantine(destPath);
  continue;
}
```

#### 6.2.2 Pre-commit Hook

**Location:** `.husky/pre-commit`

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Run validation on staged docket files
npx node scripts/validate-docket-files.js

# Check for files in inbox that should be processed
if git diff -cached -name-only | grep -q "^_inbox/"; then
  echo "⚠️  Files in _inbox/ detected. They will be processed by GitHub Actions after push."
fi
```

### 6.3 Migration Script

**Location:** `scripts/migrate-docket-system.js`

```javascript
#!/usr/bin/env node
/**
 * One-time migration script to consolidate docket system
 *
 * Tasks:
 * 1. Merge _data/docket/ and _data/docket_index/ → _data/docket/
 * 2. Move cases/<slug>/docket/*.pdf → cases/<slug>/filings/
 * 3. Update all file path references
 * 4. Regenerate checksums
 * 5. Create backup before changes
 */

import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

const DRY_RUN = process.argv.includes('-dry-run');
const BACKUP_DIR = `backups/migration-${Date.now()}`;

async function main() {
  console.log('🔄 Docket System Migration');
  console.log(`Mode: ${DRY_RUN ? 'DRY RUN' : 'LIVE'}\n`);

  // Step 1: Create backup
  if (!DRY_RUN) {
    fs.mkdirSync(BACKUP_DIR, { recursive: true });
    // ... backup logic
  }

  // Step 2: Inventory current state
  const inventory = {
    docketFiles: fs
      .readdirSync('_data/docket')
      .filter((f) => f.endsWith('.yml')),
    docketIndexFiles: fs
      .readdirSync('_data/docket_index')
      .filter((f) => f.endsWith('.yml')),
    casesWithDocketFolder: [],
    casesWithFilingsFolder: [],
  };

  // ... migration logic

  console.log('\n✅ Migration complete');
}

main().catch(console.error);
```

--

## 7. Summary & Next Steps

### Immediate Actions (This Week)

1. **Create backup** of current `_data/docket*` and `cases/*/filings/`
2. **Run inventory script** to document current state
3. **Consolidate** `_data/docket/` and `_data/docket_index/`
4. **Remove duplicate** PDFs in `cases/*/docket/` (after verification)

### Short-term (2 Weeks)

1. Implement JSON Schema validation
2. Create GitHub Actions intake workflow
3. Add pre-commit validation hooks
4. Document new intake process

### Long-term (1 Month)

1. Implement full audit trail
2. Automated integrity verification
3. Enhanced court stamp extraction
4. Intake dashboard for monitoring

--

## Appendix A: File Inventory Summary

| Directory             | Files     | Size   | Notes             |
| --------------------- | --------- | ------ | ----------------- |
| `_data/docket/`       | 13 YAML   | ~50KB  | Legacy, to merge  |
| `_data/docket_index/` | 13 YAML   | ~60KB  | Current, keep     |
| `_data/checksums/`    | 9 YAML    | ~15KB  | Keep, enhance     |
| `cases/*/filings/`    | ~200 PDFs | ~150MB | Canonical         |
| `cases/*/docket/`     | ~100 PDFs | ~75MB  | Duplicate, remove |

## Appendix B: Supported Docket Patterns

```javascript
const patterns = [
  /\b(\d:\d{2}-cv-\d{5}(?:-[A-Z]{3}(?:-[A-Z]{3})?)?)\b/i, // Federal
  /\b(ATL-[A-Z]{1,2}-\d{6}-\d{2})\b/i, // NJ Law Division
  /\b(ATL-\d{2}-\d{6})\b/i, // NJ Legacy
  /\b(A-\d{6}-\d{2})\b/, // NJ Appellate
  /\b(MER-[A-Z]-\d{6}-\d{2})\b/i, // Mercer County
];
```

--

_Report generated by Design & Architecture Agent for Evident.info_  
_Last updated: January 19, 2026_
