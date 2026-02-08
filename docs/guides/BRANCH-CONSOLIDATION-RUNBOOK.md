# Branch Consolidation, Build, and GitHub Pages Deployment Runbook

This runbook documents a deterministic, auditable process for consolidating all development
branches into two canonical main branches, building the site, and deploying the build output to
the `g8-pages` branch for GitHub Pages hosting (this repository uses `g8-pages` intentionally
rather than the conventional `gh-pages` because Pages is configured to read from that branch; do
not rename unless the Pages configuration is updated). It is intended for maintainers or
automation agents running locally or in CI with full repository permissions.
permissions.

## Scope and safety posture

- **No history rewrites** without backups and documentation.
- **Immutable evidence**: preserve original branches through timestamped backup branches and tags.
- **Deterministic merges**: conflicts are resolved using a consistent, documented rule set.
- **Full audit logs**: commands and outputs are captured for review.

## Required environment

- Git with push permission.
- GitHub CLI (`gh`) for CI run collection (optional but recommended).
- Ruby + Bundler (for Jekyll); optional `jeco` wrapper if present.
- Node.js if Eleventy build is required elsewhere.

> If a `jeco` binary is available (some environments provide Jeco as a wrapper that pins Jekyll and
> Bundler versions for deterministic builds), it is preferred. If you do not have `jeco`, continue
> with standard Jekyll commands; no public install is required for this runbook.

## Pre-flight checks (both shells)

### Bash

```bash
set -euo pipefail
CI_RUN_LIMIT="${CI_RUN_LIMIT:-20}"
STALE_DAYS="${STALE_DAYS:-90}"
REPO_ROOT="$(pwd)"
LOG_DIR="${REPO_ROOT}/_logs/consolidation-$(date -u +%Y%m%dT%H%M%SZ)" # format uses no colons for Windows-safe paths
mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_DIR/run.log") 2>&1

git remote show origin
git status --porcelain
git fetch --all --prune --tags

git show-ref --heads --verify refs/heads/main || true
git show-ref --heads --verify refs/heads/master || true
git branch -r | grep -E 'origin/(main|master|develop)'

if command -v gh >/dev/null 2>&1; then
  gh run list --limit "$CI_RUN_LIMIT" --json databaseId,headBranch,status,conclusion,createdAt | tee "$LOG_DIR/ci-runs.json"
fi
```

### PowerShell

```powershell
$ErrorActionPreference = "Stop"
$utcNow = (Get-Date).ToUniversalTime()
$ciRunLimit = if ($env:CI_RUN_LIMIT) { [int]$env:CI_RUN_LIMIT } else { 20 }
$staleDays = if ($env:STALE_DAYS) { [int]$env:STALE_DAYS } else { 90 }
$repoRoot = (Get-Location).Path
$logDir = Join-Path $repoRoot ("_logs\consolidation-{0}Z" -f $utcNow.ToString("yyyyMMddTHHmmss"))
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
Start-Transcript -Path (Join-Path $logDir "run.log") -Append

git remote show origin
git status --porcelain
git fetch --all --prune --tags

git show-ref --heads --verify refs/heads/main 2>$null | Out-Null
git show-ref --heads --verify refs/heads/master 2>$null | Out-Null
git branch -r | Select-String -Pattern 'origin/(main|master|develop)'

if (Get-Command gh -ErrorAction SilentlyContinue) {
  gh run list --limit $ciRunLimit --json databaseId,headBranch,status,conclusion,createdAt | Tee-Object -FilePath (Join-Path $logDir "ci-runs.json")
}
```

**Abort if** the working tree is not clean. If you must proceed, create an explicit stash and
record it in the final report.

## Canonical branch detection

Use environment variables when provided; otherwise detect `main` and `master`.

```bash
TARGET_A="${TARGET_A:-main}"
TARGET_B="${TARGET_B:-master}"
```

If either target branch does not exist, choose the next best canonical branch and **record the
reason** in the final report.

## Step 1: Backup current state

### Bash

```bash
TS="$(date -u +%Y%m%dT%H%M%SZ)" # format uses no colons for Windows-safe names
git checkout -b "backup/pre-consolidation-${TS}"
git push origin "backup/pre-consolidation-${TS}"
git tag -a "pre-consolidation-${TS}" -m "Backup before automated consolidation"
git push origin --tags
```

### PowerShell

```powershell
$ts = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmss") + "Z"
git checkout -b "backup/pre-consolidation-$ts"
git push origin "backup/pre-consolidation-$ts"
git tag -a "pre-consolidation-$ts" -m "Backup before automated consolidation"
git push origin --tags
```

## Step 2: Enumerate and categorize branches

```bash
git branch -r | sed 's|origin/||' | sort -u | tee "$LOG_DIR/branches.txt"
```

Categorize branches as (adjust `STALE_DAYS`, default 90, to match your cadence):

- **release/\*** and **hotfix/\*** (merge first)
- **active feature branches** (recent commits; last activity ≤ 90 days)
- **stale branches** (last activity > 90 days; merge last or archive)

Record the categorization in `"$LOG_DIR/branch-categories.md"`.

## Step 3: Create temporary consolidation branch

```bash
if [ -n "${GITHUB_RUN_ID:-}" ]; then
  MERGE_ID="run-${GITHUB_RUN_ID}"
else
  MERGE_ID="user-${USER:-agent}"
fi
git checkout -B "consolidation/temp-merge-${MERGE_ID}-$(date -u +%Y%m%dT%H%M%SZ)"
git reset --hard "origin/${TARGET_A}"
```

If neither `GITHUB_RUN_ID` nor `USER` is set (common in CI), the branch will use `agent` as the
identifier. Record the temporary branch name and clean it up after consolidation.

## Step 4: Deterministic merge order

1. `release/*`
2. `hotfix/*`
3. Active feature branches
4. Stale branches (squash or archive)

For each branch (iterate over the categorized list from Step 2 and filter out special branches
like `g8-pages`, `backup/*`, and the current consolidation branch, for example
`for BRANCH in $(cat "$LOG_DIR/branches.txt"); do ...`):

```bash
git merge --no-ff "origin/${BRANCH}"
```

If the merge reports conflicts, resolve them manually before continuing:

```bash
git status --porcelain
# Resolve conflicts per policy (for example, `git checkout --ours -- path/to/file`).
git diff --name-only --diff-filter=U
# No output should remain before committing.
git add -A
git commit -m "Resolve merge conflicts for ${BRANCH}"
```

### Conflict resolution policy (deterministic)

- **Default**: keep `TARGET_A` changes (`git checkout --ours -- <path>`).
- **Release/hotfix**: keep incoming change **only** for files scoped to the release/hotfix.
- **Always document** resolved files in `"$LOG_DIR/conflicts.md"`.

After resolving:

```bash
git add -A
git commit -m "Merge ${BRANCH} into consolidation"
```

## Step 5: Consolidate into TARGET_B (if required)

If two canonical branches are required, repeat Steps 3–4 starting from `TARGET_B`, or merge the
consolidated branch into `TARGET_B` and resolve conflicts with the same policy.

## Step 6: Build the site (prefer Jeco)

### Bash

```bash
if command -v jeco >/dev/null 2>&1; then
  jeco build --source site --destination site/_site
else
  (cd site && bundle install && bundle exec jekyll build)
fi
```

### PowerShell

```powershell
if (Get-Command jeco -ErrorAction SilentlyContinue) {
  jeco build --source site --destination site/_site
} else {
  Push-Location site
  bundle install
  bundle exec jekyll build
  Pop-Location
}
```

Record build output in the log. If the build fails, stop and include the error in the final report.
If your build output path differs from `site/_site`, adjust the deployment step accordingly (for
example, Eleventy builds may output to `_site` at the repository root).

## Step 7: Deploy build output to `g8-pages`

### Safety backup for g8-pages (if it exists)

```bash
if git show-ref --verify --quiet refs/remotes/origin/g8-pages; then
  git branch "backup/g8-pages-$(date -u +%Y%m%dT%H%M%SZ)" origin/g8-pages
  git push origin "backup/g8-pages-$(date -u +%Y%m%dT%H%M%SZ)"
fi
```

### Publish build output

```bash
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "Error: Git metadata not found; aborting destructive operations."
  exit 1
fi
if git show-ref --verify --quiet refs/remotes/origin/g8-pages; then
  git fetch origin g8-pages
  git checkout -B g8-pages origin/g8-pages
else
  git checkout --orphan g8-pages
fi
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CURRENT_BRANCH" != "g8-pages" ]; then
  echo "Error: expected g8-pages but on ${CURRENT_BRANCH}; aborting to protect repository history."
  exit 1
fi
git rm -rf .
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete site/_site/ .
else
  cp -R site/_site/. .
  # `git rm -rf .` already clears tracked files, so stale content is removed.
fi
touch .nojekyll
git add -A
git commit -m "Deploy build to g8-pages"
git push origin g8-pages
```

> If you cannot use orphan branches, use `git worktree` to avoid mixing build artifacts with
> source history. Document the chosen approach.

## Step 8: Verification

- Confirm Pages source is set to `g8-pages`.
- Record the deployed commit SHA.
- Perform a smoke test with `curl -fLsS <pages-url>`.

## Step 9: Capture CI run IDs

```bash
if command -v gh >/dev/null 2>&1; then
  gh run list --limit "$CI_RUN_LIMIT" --json databaseId,headBranch,status,conclusion,createdAt | tee "$LOG_DIR/ci-runs-post.json"
fi
```

Record the relevant run IDs in the final report.

## Rollback procedure

1. Reset the canonical branches to the backup tag or backup branch.
2. Restore `g8-pages` from the backup branch created earlier.
3. Re-run the build/deploy only after verifying the rollback state.

## Final report template

Include the following summary (attach logs and JSON artifacts):

```
Consolidation Report
====================
Timestamp (UTC):
Operator:
TARGET_A / TARGET_B:

Backups
- backup branch:
- backup tag:
- g8-pages backup (if any):

Branches merged (in order):
- ...

Conflicts resolved:
- files:
- policy applied:

Build
- tool: jeco / jekyll
- command:
- status:

Deployment
- g8-pages commit:
- pages URL:

CI
- run IDs:
- ci-runs.json attached: yes/no

Verification
- smoke test command:
- result:

Notes / exceptions:
```
