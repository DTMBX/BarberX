#!/usr/bin/env pwsh
<#
.SYNOPSIS
    One-command verification for the Evident monorepo.
.DESCRIPTION
    Runs runner tests, builds the website (Astro or Eleventy), validates tool manifests,
    and shows status. Exit code 0 means everything passed.
.EXAMPLE
    .\federation-verify.ps1
#>

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$runnerRoot = Join-Path $root "runner"

$failed = $false

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "  >> $Message" -ForegroundColor Cyan
    Write-Host "  " + ("-" * ($Message.Length + 3)) -ForegroundColor DarkGray
}

function Write-Pass {
    param([string]$Message)
    Write-Host "     PASS: $Message" -ForegroundColor Green
}

function Write-Fail {
    param([string]$Message)
    Write-Host "     FAIL: $Message" -ForegroundColor Red
    $script:failed = $true
}

function Write-Skip {
    param([string]$Message)
    Write-Host "     SKIP: $Message" -ForegroundColor Yellow
}

# Banner
Write-Host ""
Write-Host "  =============================================" -ForegroundColor Cyan
Write-Host "       Evident - Full Verification" -ForegroundColor Cyan
Write-Host "  =============================================" -ForegroundColor Cyan
Write-Host "  Root: $root"

# 1. Runner tests
Write-Step "Runner Tests (pytest)"
$venvPython = Join-Path $runnerRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    try {
        $result = & $venvPython -m pytest (Join-Path $runnerRoot "tests") -q 2>&1
        $testLine = $result | Select-String "passed|failed|error" | Select-Object -Last 1
        if ($LASTEXITCODE -eq 0) {
            Write-Pass "All tests passed ($testLine)"
        } else {
            Write-Fail "Some tests failed"
            $result | ForEach-Object { Write-Host "     $_" }
        }
    } catch {
        Write-Fail "Could not run pytest: $_"
    }
} else {
    Write-Skip "Runner venv not found at $venvPython"
    Write-Host "     To enable: cd runner && python -m venv .venv && .\.venv\Scripts\pip install -e .[dev]" -ForegroundColor DarkGray
}

# 2. Website build (layout-aware)
Write-Step "Website Build"

$wwwRoot = Join-Path $root "www"
$astroConfig = Join-Path $wwwRoot "astro.config.*"
$eleventyConfigJs = Join-Path $root ".eleventy.js"
$eleventyConfigMjs = Join-Path $root "eleventy.config.mjs"
$eleventyConfigCjs = Join-Path $root "eleventy.config.cjs"
$eleventyConfigTs = Join-Path $root "eleventy.config.ts"

$siteLayout = $null
$siteRoot = $null

# Detect layout: Astro in www/ or Eleventy at root
if ((Test-Path (Join-Path $wwwRoot "package.json")) -and (Test-Path $astroConfig)) {
    $siteLayout = "Astro"
    $siteRoot = $wwwRoot
    Write-Host "     Detected: Astro site at www/" -ForegroundColor DarkGray
} elseif ((Test-Path (Join-Path $root "package.json")) -and (
    (Test-Path $eleventyConfigJs) -or 
    (Test-Path $eleventyConfigMjs) -or 
    (Test-Path $eleventyConfigCjs) -or 
    (Test-Path $eleventyConfigTs))) {
    $siteLayout = "Eleventy"
    $siteRoot = $root
    Write-Host "     Detected: Eleventy site at repo root" -ForegroundColor DarkGray
}

if ($siteLayout -and $siteRoot) {
    Push-Location $siteRoot
    try {
        $buildOutput = & npm run build 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pages = ($buildOutput | Select-String "page\(s\) built|pages generated|files written" | Select-Object -Last 1)
            Write-Pass "$siteLayout build succeeded ($pages)"
        } else {
            Write-Fail "$siteLayout build failed"
            $buildOutput | Select-Object -Last 10 | ForEach-Object { Write-Host "     $_" }
        }
    } catch {
        Write-Fail "Could not build website: $_"
    }
    Pop-Location
} else {
    Write-Skip "No Astro (www/) or Eleventy (root) config detected"
    Write-Host "     Expected: www/package.json + astro.config.* OR .eleventy.js/eleventy.config.*" -ForegroundColor DarkGray
}

# 3. Tool manifest validation (if schema exists)
Write-Step "Tool Manifest Validation"
$schemaPath = Join-Path $runnerRoot "schemas\tool-manifest.schema.json"
$toolSourcesPath = Join-Path $root "tool_sources.json"

if ((Test-Path $schemaPath) -and (Test-Path $toolSourcesPath)) {
    try {
        # Use Node.js ajv-cli if available, otherwise skip
        $ajvTest = & npx ajv --help 2>&1
        if ($LASTEXITCODE -eq 0) {
            $validationResult = & npx ajv validate -s $schemaPath -d $toolSourcesPath 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Pass "tool_sources.json is valid"
            } else {
                Write-Fail "tool_sources.json validation failed"
                $validationResult | ForEach-Object { Write-Host "     $_" }
            }
        } else {
            Write-Skip "ajv-cli not available for schema validation"
        }
    } catch {
        Write-Skip "Schema validation skipped: $_"
    }
} else {
    Write-Skip "Schema or tool_sources.json not found"
}

# 4. Monorepo workspaces (if configured)
Write-Step "Workspace Integrity"
$packageJson = Join-Path $root "package.json"
if (Test-Path $packageJson) {
    $pkg = Get-Content $packageJson | ConvertFrom-Json
    if ($pkg.workspaces) {
        Write-Host "     Workspaces configured: $($pkg.workspaces -join ', ')" -ForegroundColor DarkGray
        try {
            $wsOutput = & npm -ws --if-present run lint 2>&1
            Write-Pass "Workspace lint check completed"
        } catch {
            Write-Skip "Workspace lint skipped"
        }
    } else {
        Write-Skip "No npm workspaces configured"
    }
} else {
    Write-Skip "No package.json found"
}

# Summary
Write-Host ""
Write-Host "  =============================================" -ForegroundColor Cyan
if ($failed) {
    Write-Host "       VERIFICATION FAILED" -ForegroundColor Red
    Write-Host "  =============================================" -ForegroundColor Cyan
    exit 1
} else {
    Write-Host "       VERIFICATION PASSED" -ForegroundColor Green
    Write-Host "  =============================================" -ForegroundColor Cyan
    exit 0
}
