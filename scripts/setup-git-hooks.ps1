param(
  [string]$RepoRoot = (git rev-parse --show-toplevel 2>$null)
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
  throw "Not inside a git repo. CD into the repo root and re-run."
}

Set-Location $RepoRoot

# 1) Create a versioned hooks dir
$hooksDir = Join-Path $RepoRoot ".githooks"
New-Item -ItemType Directory -Force -Path $hooksDir | Out-Null

# 2) Point git at it (repo-local config)
git config core.hooksPath .githooks | Out-Null

# 3) Write PRE-COMMIT hook (fast checks; runs on every commit)
$preCommit = @'
#!/usr/bin/env sh
set -eu

echo ""
echo "[pre-commit] Tillerstead checks..."

# Fail if PowerShell scripts were saved with broken encoding patterns in them
# (we keep this in PS, but this is a light guard)
# If you want this stricter, we can add a dedicated node/ps scan.
# echo "[pre-commit] quick encoding scan..."

# Run your audit script (should be fast — if it’s heavy, move to pre-push)
if [ -f "./scripts/audit-site.ps1" ]; then
  # Prefer pwsh; fall back to powershell
  if command -v pwsh >/dev/null 2>&1; then
    pwsh -NoProfile -ExecutionPolicy Bypass -File "./scripts/audit-site.ps1"
  else
    powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\audit-site.ps1"
  fi
fi

# Optional: quick CSS build (keep it fast)
if [ -f "./scripts/build-css.js" ]; then
  node "./scripts/build-css.js"
fi

echo "[pre-commit] OK"
echo ""
'@

# 4) Write PRE-PUSH hook (full build; blocks broken pushes)
$prePush = @'
#!/usr/bin/env sh
set -eu

echo ""
echo "[pre-push] Full build gate..."

# Build site (this is what actually catches front matter / YAML / liquid breakage)
if command -v bundle >/dev/null 2>&1; then
  bundle exec jekyll build --trace
else
  echo "[pre-push] ERROR: bundle not found. Install ruby/bundler or run via your activate-ruby.ps1."
  exit 1
fi

# Optional link check (if script exists)
if [ -f "./scripts/check-links.js" ]; then
  node "./scripts/check-links.js"
fi

echo "[pre-push] OK — push allowed"
echo ""
'@

$preCommitPath = Join-Path $hooksDir "pre-commit"
$prePushPath   = Join-Path $hooksDir "pre-push"

Set-Content -Path $preCommitPath -Value $preCommit -Encoding UTF8
Set-Content -Path $prePushPath   -Value $prePush   -Encoding UTF8

# 5) Make hook files executable-ish for Git Bash environments
# On Windows, Git uses sh to run hooks; executable bit isn't always required,
# but setting it helps across environments.
try {
  git add .githooks 2>$null | Out-Null
} catch { }

Write-Host ""
Write-Host "Installed repo hooks at: $hooksDir"
Write-Host "Git configured: core.hooksPath = .githooks"
Write-Host ""
Write-Host "Behavior:"
Write-Host " - On COMMIT: audit-site.ps1 + build-css.js"
Write-Host " - On PUSH:   bundle exec jekyll build --trace (+ optional link check)"
Write-Host ""
Write-Host "Done."
