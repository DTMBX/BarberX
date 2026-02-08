# Branch Consolidation, Build, and GitHub Pages Deployment Runbook

This runbook documents a deterministic, auditable process for consolidating all development
branches into two canonical main branches, building the site, and deploying the build output to
the `g8-pages` branch for GitHub Pages hosting. It is intended for maintainers or automation
agents running locally or in CI with full repository permissions.

## Scope and safety posture

- **No history rewrites** without backups and documentation.
- **Immutable evidence**: preserve original branches through timestamped backup branches and tags.
- **Deterministic merges**: conflicts are resolved using a consistent, documented rule set.
- **Full audit logs**: commands and outputs are captured for review.

## Required environment

- Git with push permission.
- GitHub CLI (`gh`) for CI run collection (optional but recommended).
- Ruby + Bundler (for Jekyll) or `jeco` if present.
- Node.js if Eleventy build is required elsewhere.

> If a `jeco` binary is available, it is preferred over Jekyll. Otherwise use Jekyll.

## Pre-flight checks (both shells)

### Bash

```bash
set -euo pipefail
LOG_DIR="_logs/consolidation-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_DIR/run.log") 2>&1

git remote show origin
git status --porcelain
git fetch --all --prune --tags

git show-ref --heads --hash=8 --verify refs/heads/main || true
git show-ref --heads --hash=8 --verify refs/heads/master || true
git branch -r | grep -E 'origin/(main|master|develop)'

if command -v gh >/dev/null 2>&1; then
  gh run list --limit 20 --json databaseId,headBranch,status,conclusion,createdAt | tee "$LOG_DIR/ci-runs.json"
fi
```

### PowerShell

```powershell
$ErrorActionPreference = "Stop"
$logDir = "_logs\consolidation-{0:yyyyMMddTHHmmssZ}" -f (Get-Date).ToUniversalTime()
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
Start-Transcript -Path (Join-Path $logDir "run.log") -Append

git remote show origin
git status --porcelain
git fetch --all --prune --tags

git show-ref --heads --hash=8 --verify refs/heads/main; if ($LASTEXITCODE -ne 0) { $null }
git show-ref --heads --hash=8 --verify refs/heads/master; if ($LASTEXITCODE -ne 0) { $null }
git branch -r | Select-String -Pattern 'origin/(main|master|develop)'

if (Get-Command gh -ErrorAction SilentlyContinue) {
  gh run list --limit 20 --json databaseId,headBranch,status,conclusion,createdAt | Tee-Object -FilePath (Join-Path $logDir "ci-runs.json")
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
TS="$(date -u +%Y%m%dT%H%M%SZ)"
git checkout -b "backup/pre-consolidation-${TS}"
git push origin "backup/pre-consolidation-${TS}"
git tag -a "pre-consolidation-${TS}" -m "Backup before automated consolidation"
git push origin --tags
```

### PowerShell

```powershell
$ts = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
git checkout -b "backup/pre-consolidation-$ts"
git push origin "backup/pre-consolidation-$ts"
git tag -a "pre-consolidation-$ts" -m "Backup before automated consolidation"
git push origin --tags
```

## Step 2: Enumerate and categorize branches

```bash
git branch -r | sed 's|origin/||' | sort -u | tee "$LOG_DIR/branches.txt"
```

Categorize branches as:

- **release/\*** and **hotfix/\*** (merge first)
- **active feature branches** (recent commits; last activity ≤ 90 days)
- **stale branches** (last activity > 90 days; merge last or archive)

Record the categorization in `"$LOG_DIR/branch-categories.md"`.

## Step 3: Create temporary consolidation branch

```bash
git checkout -B "consolidation/temp-merge-${USER:-agent}-$(date -u +%Y%m%dT%H%M%SZ)"
git reset --hard "origin/${TARGET_A}"
```

## Step 4: Deterministic merge order

1. `release/*`
2. `hotfix/*`
3. Active feature branches
4. Stale branches (squash or archive)

For each branch:

```bash
git merge --no-ff "origin/${BRANCH}" || true
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
git checkout --orphan g8-pages
git rm -rf .
cp -R site/_site/* .
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
  gh run list --limit 20 --json databaseId,headBranch,status,conclusion,createdAt | tee "$LOG_DIR/ci-runs-post.json"
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
