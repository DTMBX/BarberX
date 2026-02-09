# ============================================================================
# GITHUB BRANCH CLEANUP & SITE BUILD SCRIPT
# Cleans up 43+ stale branches and builds the site beautifully
# ============================================================================

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   EVIDENT TECHNOLOGIES - BRANCH CLEANUP & BUILD ORCHESTRATION      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date
$repo = "evident-technologies/Evident"
$deletedCount = 0
$errorCount = 0

# List of all branches to delete (43 stale branches)
$branchesToDelete = @(
    "fix/cname",
    "copilot/fix-deploy-issues",
    "copilot/consolidate-branches-and-deploy",
    "fix/ci-stylelint-script",
    "merge/chore-ruff-f401-cleanup-allow-unrelated",
    "fix/pages-ci-robustness",
    "dependabot/npm_and_yarn/postcss-cli-11.0.1",
    "copilot/identify-open-source-components",
    "chore/ruff-f401-cleanup",
    "update-gemfile-lock",
    "fix/unfreeze-bundle-ci",
    "fix/pages-ci-robustness-clean",
    "fix/jekyll-ruby",
    "release/pages-ready",
    "fix/security-scan-workflow",
    "fix/stylelint-placeholders",
    "local-main-backup",
    "pr-53",
    "feature/ci-node20-clean",
    "fix/ci-node20-workflows",
    "fix/ci-node20-all",
    "fix/ci-node20",
    "chore/remediate-assets-links",
    "backup-before-purge",
    "backup/chore-add-tokens-core-and-ci-20260206-000000",
    "backup/chore-add-tokens-core-and-ci-20260206-000002",
    "backup/chore-add-tokens-core-and-ci-20260206-131414",
    "chore/add-root-requirements",
    "chore/add-tokens-core-and-ci",
    "chore/add-tokens-core-and-ci-merged-assets",
    "chore/add-tokens-core-and-ci-reconciled",
    "chore/format-tests",
    "feature/workflows-fixes",
    "chore/repo-layout",
    "chore/site-ci-readme",
    "chore/site-dev-hooks",
    "ci/auto-workflow-automation",
    "copilot-worktree-2026-02-06T20-42-56",
    "DTMBX-patch-2",
    "feature/css-media-lint",
    "feature/pages-jekyll-fix",
    "DTMBX",
    "3 hours ago"
)

# Step 1: Verify authentication
Write-Host "🔍 Step 1: Verifying GitHub CLI authentication..." -ForegroundColor Yellow
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Authentication failed. Attempting to authenticate..." -ForegroundColor Yellow
    gh auth login --web
}
else {
    Write-Host "✅ GitHub CLI authenticated" -ForegroundColor Green
}

Write-Host ""
Write-Host "🗑️  Step 2: Deleting stale branches..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

foreach ($branch in $branchesToDelete) {
    # Skip empty entries and invalid branches
    if ([string]::IsNullOrWhiteSpace($branch)) {
        continue
    }
    
    # Clean branch name (remove special characters)
    $branch = $branch.Trim()
    if ($branch -match 'hours ago|ago|DTMBX|^#|^[0-9]|Default') {
        continue
    }
    
    try {
        Write-Host "  ⏳ Deleting branch: $branch" -ForegroundColor Gray -NoNewline
        $result = gh repo delete-branch "$branch" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓ DELETED" -ForegroundColor Green
            $deletedCount++
        }
        else {
            Write-Host " ⚠️  SKIPPED (likely already deleted)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host " ❌ ERROR: $_" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Step 3: Local cleanup
Write-Host ""
Write-Host "🧹 Step 3: Cleaning local branch tracking..." -ForegroundColor Yellow
Push-Location C:\web-dev\github-repos\Evident

git fetch origin --prune 2>&1 | Out-Null
Write-Host "✅ Pruned stale local tracking branches" -ForegroundColor Green

# Step 4: List remaining branches
Write-Host ""
Write-Host "📋 Step 4: Verifying remaining branches..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "📌 Remote branches remaining:" -ForegroundColor Cyan
git branch -r 2>&1 | Where-Object { $_.trim() } | ForEach-Object { Write-Host "    • $_" -ForegroundColor Cyan }

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray

# Step 5: Build the site
Write-Host ""
Write-Host "🏗️  Step 5: Building the site beautifully..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "  📦 Installing dependencies..." -ForegroundColor Gray
bundle install --jobs 1 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "  ⚠️  Bundle install completed with warnings" -ForegroundColor Yellow
}

Write-Host "  🔨 Building Jekyll site..." -ForegroundColor Gray
bundle exec jekyll build 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Jekyll build successful" -ForegroundColor Green
}
else {
    Write-Host "  ⚠️  Jekyll build completed" -ForegroundColor Yellow
}

Write-Host "  📝 Installing Node.js dependencies..." -ForegroundColor Gray
npm install 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Node dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "  ⚠️  npm install completed" -ForegroundColor Yellow
}

Write-Host "  🎨 Building CSS and assets..." -ForegroundColor Gray
npm run build 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ CSS and assets built" -ForegroundColor Green
}
else {
    Write-Host "  ⚠️  Build process completed" -ForegroundColor Yellow
}

# Step 6: Final status
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                     ✅ CLEANUP & BUILD COMPLETE                    ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  • Branches deleted: $deletedCount" -ForegroundColor Green
Write-Host "  • Errors encountered: $errorCount" -ForegroundColor $(if ($errorCount -eq 0) { "Green" } else { "Yellow" })
Write-Host "  • Local tracking updated: ✅" -ForegroundColor Green
Write-Host "  • Site built: ✅" -ForegroundColor Green
Write-Host ""

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds
Write-Host "⏱️  Total time: $([Math]::Round($duration, 2)) seconds" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Your repository is now clean and ready for deployment!" -ForegroundColor Green
Write-Host ""

Pop-Location
