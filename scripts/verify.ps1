# scripts/verify.ps1 — Cross-platform site verification for Evident Technologies
# Usage: pwsh -NoProfile -File scripts/verify.ps1
# Exit codes: 0 = pass, 1 = fail

$ErrorActionPreference = 'Continue'
$fail = 0

function Step($msg) { Write-Host "`n--- $msg ---" }
function Pass($msg) { Write-Host "PASS: $msg" -ForegroundColor Green }
function Fail($msg) { Write-Host "FAIL: $msg" -ForegroundColor Red; $script:fail = 1 }

# 1. Check Node.js
Step "Node.js version"
try {
    $nodeVer = node -v
    Pass "Node $nodeVer"
} catch {
    Fail "Node.js not found"
}

# 2. Install dependencies
Step "npm install"
$npmResult = npm ci --no-audit --no-fund 2>&1
if ($LASTEXITCODE -eq 0) { Pass "Dependencies installed" } else { Fail "npm ci failed" }

# 3. Lint
Step "Lint check"
$lintResult = npm run lint 2>&1
if ($LASTEXITCODE -eq 0) { Pass "Lint passed" } else { Fail "Lint failed" }

# 4. Build site
Step "Eleventy build"
$buildResult = npm run build 2>&1
if ($LASTEXITCODE -eq 0) { Pass "Site built" } else { Fail "Build failed" }

# 5. Verify output
Step "Build output verification"
if (Test-Path "_site/index.html") {
    $pageCount = (Get-ChildItem -Path "_site" -Recurse -Filter "*.html" | Measure-Object).Count
    Pass "_site/index.html present ($pageCount pages)"
} else {
    Fail "_site/index.html not found"
}

# 6. Python tests (optional)
Step "Python tests"
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
    $pytestCheck = python -m pytest --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        python -m pytest tests/ -q --tb=short 2>&1
        if ($LASTEXITCODE -eq 0) { Pass "Python tests passed" } else { Fail "Python tests failed" }
    } else {
        Write-Host "SKIP: pytest not installed"
    }
} else {
    Write-Host "SKIP: Python not available"
}

# Summary
Step "Summary"
if ($fail -eq 0) {
    Write-Host "All checks passed." -ForegroundColor Green
    exit 0
} else {
    Write-Host "One or more checks failed." -ForegroundColor Red
    exit 1
}
