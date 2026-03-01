# UI Testing Guide

> Playwright E2E tests for the Evident forensic evidence platform.

## Quick Start

```bash
# Install dependencies (if not already)
pnpm install

# Install browser (Chromium headless)
npx playwright install chromium

# Run all E2E tests (headless)
pnpm test:e2e

# Run with browser visible
pnpm test:e2e:headed

# Run a single spec
pnpm exec playwright test e2e/smoke.spec.ts

# Open HTML report after run
pnpm test:e2e:report
```

## Test Architecture

### Spec Files (8)

| File                          | Flows | Description                                                |
| ----------------------------- | ----- | ---------------------------------------------------------- |
| `e2e/smoke.spec.ts`           | 7     | Homepage load, health, nav links, quick actions, keyboard  |
| `e2e/cases.spec.ts`           | 6     | CRUD lifecycle, empty state, tab renders                   |
| `e2e/evidence-upload.spec.ts` | 5     | Drag-drop PDF, hashing progress, evidence table            |
| `e2e/timeline.spec.ts`        | 3     | Chronological ordering, event badges, empty state          |
| `e2e/issues.spec.ts`          | 4     | Create issue, status/confidence badges, keyboard           |
| `e2e/jobs.spec.ts`            | 4     | Run pipeline, job rows, state badges                       |
| `e2e/exports-verify.spec.ts`  | 5     | Export manifest, verify SHA-256+HMAC, audit replay         |
| `e2e/chat.spec.ts`            | 8     | Mode switching, legal search, resource panel, send/receive |

### Fixtures (`e2e/fixtures.ts`)

All tests use shared fixtures:

- **`seededCase`** — Auto-seeds a fresh case via API before each test
- **`waitForStable`** — Waits for loading spinners to disappear
- **`seedCase()`** / **`seedEvidenceInit()`** / **`completeEvidence()`** — API
  helpers
- **`makeTestPdf()`** / **`makeTestVideo()`** / **`makeTextFile()`** —
  Deterministic file generators (no random data)

### Selectors Policy

All interactive controls use `data-testid` attributes. **Never use CSS
selectors, XPath, or text content for element targeting in tests.** Use
Playwright's `getByTestId()` locator exclusively.

Naming convention: `{page}-{element}` or `{section}-{element}`, e.g.:

- `dashboard-header`, `dashboard-action-new-case`
- `case-detail-tab-evidence`, `case-detail-upload-zone`
- `chat-mode-legal-btn`, `chat-message-input`

## SAFE_MODE

Set `SAFE_MODE=1` to disable all artifact capture (trace, video, screenshots).
**Always enabled in CI** to prevent forensic data from leaking into build
artifacts.

```bash
# Run with SAFE_MODE (no artifacts)
SAFE_MODE=1 pnpm test:e2e

# Run locally with full artifacts
pnpm test:e2e
```

### How SAFE_MODE Works

In `playwright.config.ts`:

```typescript
const SAFE = process.env.SAFE_MODE === '1';
// trace, video, screenshot all set to 'off' when SAFE_MODE=1
```

## Running Tests

### Local Development

```bash
# Start backend + frontend first
pnpm dev  # or use VS Code task "dev:stack"

# In another terminal, run tests
pnpm test:e2e
```

### Docker / Codespace

```bash
# Tests auto-start the webServer defined in playwright.config.ts
pnpm test:e2e
```

### CI Pipeline

Tests run automatically in the `e2e` job of the GitHub Actions CI workflow:

- `SAFE_MODE=1` prevents artifact leakage
- HTML report uploaded as GitHub Actions artifact
- Chromium headless shell only (no GPU)

## Debugging

### VS Code Debugger

Use the "Playwright: debug tests" or "Playwright: debug current file" launch
configurations. These set `PWDEBUG=1` which:

- Opens the Playwright Inspector
- Pauses before each action
- Shows live selectors

### Trace Viewer

```bash
# Run with trace capture
pnpm exec playwright test --trace on

# Open the trace viewer
pnpm exec playwright show-trace test-results/*/trace.zip
```

### Screenshots on Failure

By default (non-SAFE_MODE), screenshots are captured on test failure. Find them
in `test-results/`.

## Environment Variables

| Variable              | Default                 | Description                            |
| --------------------- | ----------------------- | -------------------------------------- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL                        |
| `PLAYWRIGHT_BASE_URL` | `http://localhost:3000` | Frontend URL for tests                 |
| `SAFE_MODE`           | `0`                     | Set to `1` to disable artifact capture |
| `CI`                  | —                       | Auto-set in CI; enables retries (2)    |

## Adding New Tests

1. Create spec file in `e2e/` directory
2. Import from `./fixtures` (not `@playwright/test` directly)
3. Use `data-testid` selectors exclusively
4. Use `seededCase` fixture for tests that need case data
5. Use deterministic file generators (`makeTestPdf`, etc.)
6. **No `setTimeout` or `sleep`** — use Playwright auto-waits and
   `expect().toBeVisible()`
7. Run `pnpm exec playwright test your-spec.spec.ts` to verify

## Forensic Integrity

Tests must **never**:

- Hardcode API keys or secrets
- Disable HMAC/SHA-256 verification
- Modify immutable storage (WORM) settings
- Skip audit trail checks
- Generate non-deterministic test data

Tests **always**:

- Use API seeders for test data (ephemeral DB)
- Verify SHA-256 hashing occurs during upload
- Check that chain-of-custody features are active
- Use deterministic file generators
