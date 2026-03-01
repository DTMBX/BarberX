param(
  [string]$Root = "C:\barber-cam\public",
  [string]$Repo = "tillerstead"
)

# Validate Root directory
if (-not (Test-Path $Root)) {
  Write-Host "Root directory does not exist: $Root" -ForegroundColor Red
  $Root = Read-Host "Please provide a valid Root directory"
  if (-not (Test-Path $Root)) {
    Write-Host "Invalid Root directory provided. Exiting." -ForegroundColor Red
    exit 1
  }
}

# Validate Repo directory
$repoPath = Join-Path $Root $Repo
if (-not (Test-Path $repoPath)) {
  Write-Host "Repo path does not exist: $repoPath" -ForegroundColor Red
  $Repo = Read-Host "Please provide a valid Repo name"
  $repoPath = Join-Path $Root $Repo
  if (-not (Test-Path $repoPath)) {
    Write-Host "Invalid Repo path provided. Exiting." -ForegroundColor Red
    exit 1
  }
}

Set-Location $repoPath

Write-Host "== FINALIZING TILLERSTEAD ==" -ForegroundColor Cyan

# 1. Safety check
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host "Git is not installed or not available in PATH." -ForegroundColor Red
  exit 1
}

git status --porcelain
if ($LASTEXITCODE -ne 0) {
  Write-Host "Not a git repo or git not available." -ForegroundColor Red
  exit 1
}

# 2. Ensure correct branch
try {
  Write-Host "Checking out branch: bypass-compliance" -ForegroundColor Yellow
  git checkout bypass-compliance
} catch {
  Write-Host "Failed to checkout branch: bypass-compliance" -ForegroundColor Red
  exit 1
}

# 3. Remove backup artifacts from build
$cleanup = @(
  ".backups",
  "reports",
  "*.bak_keep_*"
)

foreach ($item in $cleanup) {
  try {
    Write-Host "Removing: $item" -ForegroundColor Yellow
    Get-ChildItem -Recurse -Force -ErrorAction SilentlyContinue |
      Where-Object { $_.Name -like $item } |
      Remove-Item -Force -Recurse
  } catch {
    Write-Host "Failed to remove: $item" -ForegroundColor Red
  }
}

# 4. Enforce excludes
if (-not (Test-Path _config.yml)) {
  Write-Host "_config.yml not found. Skipping exclude enforcement." -ForegroundColor Yellow
} elseif (-not (Select-String "_bak_keep_" _config.yml -Quiet)) {
  Write-Host "Adding excludes to _config.yml" -ForegroundColor Yellow
  Add-Content _config.yml @"
exclude:
  - "*.bak_keep_*"
  - ".backups"
  - "reports"
"@
}

# 5. Merge footer gradient tokens (idempotent)
$tokens = "_sass/00-settings/_tokens-hybrid.scss"
$footerGradient = "--tiller-footer-bg: linear-gradient(180deg, #0a0a0a 0%, #065a24 100%);"

if (-not (Test-Path $tokens)) {
  Write-Host "Tokens file not found: $tokens" -ForegroundColor Yellow
} elseif (-not (Select-String "tiller-footer-bg" $tokens -Quiet)) {
  Write-Host "Adding footer gradient token" -ForegroundColor Yellow
  Add-Content $tokens $footerGradient
}

# 6. Commit
try {
  Write-Host "Staging changes for commit" -ForegroundColor Yellow
  git add .
  Write-Host "Committing changes" -ForegroundColor Yellow
  git commit -m "Finalize canonical Tillerstead build + preserve live footer gradient"
} catch {
  Write-Host "Failed to commit changes." -ForegroundColor Red
  exit 1
}

# 7. Build verification
if (-not (Get-Command bundle -ErrorAction SilentlyContinue)) {
  Write-Host "Jekyll (bundle) is not installed or not available in PATH." -ForegroundColor Red
  exit 1
}

try {
  Write-Host "Running Jekyll build" -ForegroundColor Yellow
  bundle exec jekyll build --trace
  Write-Host "✔ Final build completed" -ForegroundColor Green
} catch {
  Write-Host "Jekyll build failed." -ForegroundColor Red
  exit 1
}

Write-Host "== FINALIZATION COMPLETE ==" -ForegroundColor Cyan
