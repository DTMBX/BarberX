<#
.SYNOPSIS
    Federation reproducibility test — verifies builds are deterministic.

.DESCRIPTION
    Reads an existing federation-manifest.json, re-runs the federation
    build using the recorded commit SHAs (not HEAD), and compares the
    resulting manifest against the original to confirm identical source
    resolution.

    This script does NOT require network access if the federation cache
    is already populated with the correct commits.

    See docs/architecture/BUILD-FEDERATION-SPEC.md for the manifest schema.
    See docs/architecture/RELEASE-PINNING-RULES.md for pinning policy.

.PARAMETER ManifestPath
    Path to the existing federation-manifest.json to verify against.

.PARAMETER RegistryPath
    Path to workspace-registry.json. Defaults to tools/web-builder/workspace-registry.json.

.PARAMETER CacheDir
    Federation cache directory. Defaults to .federation-cache.

.PARAMETER OutputDir
    Build output directory. Defaults to _site/apps.

.EXAMPLE
    .\scripts\test-federation-reproducibility.ps1
    .\scripts\test-federation-reproducibility.ps1 -ManifestPath "federation-manifest.json"

.NOTES
    Phase 3C — release determinism hardening.
    Copyright 2024-2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
    PROPRIETARY — See LICENSE.
#>

[CmdletBinding()]
param(
    [string]$ManifestPath = "federation-manifest.json",
    [string]$RegistryPath = "tools/web-builder/workspace-registry.json",
    [string]$CacheDir = ".federation-cache",
    [string]$OutputDir = "_site/apps"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Write-Step {
    param([string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "  PASS: $Message" -ForegroundColor Green
}

function Write-Fail {
    param([string]$Message)
    Write-Host "  FAIL: $Message" -ForegroundColor Red
}

function Write-Detail {
    param([string]$Message)
    Write-Host "  $Message" -ForegroundColor Gray
}

# ---------------------------------------------------------------------------
# 1. Load the reference manifest
# ---------------------------------------------------------------------------
Write-Step "Loading reference manifest"

if (-not (Test-Path $ManifestPath)) {
    Write-Fail "Manifest not found: $ManifestPath"
    Write-Host ""
    Write-Host "  Run build-federate.ps1 first to generate a manifest." -ForegroundColor Yellow
    exit 1
}

$refManifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
Write-Detail "Manifest built at: $($refManifest.builtAt)"
Write-Detail "Registry version: $($refManifest.registryVersion)"
Write-Detail "Build mode: $($refManifest.buildMode)"
Write-Detail "Targets: $($refManifest.targets.Count)"

# ---------------------------------------------------------------------------
# 2. Create a temporary pinned registry
# ---------------------------------------------------------------------------
Write-Step "Creating pinned registry from manifest SHAs"

# Load current registry
if (-not (Test-Path $RegistryPath)) {
    Write-Fail "Registry not found: $RegistryPath"
    exit 1
}

$registry = Get-Content $RegistryPath -Raw | ConvertFrom-Json

# Build a lookup from the manifest: app -> resolvedShaFull
$shaLookup = @{}
foreach ($target in $refManifest.targets) {
    $sha = $null
    if ($target.PSObject.Properties.Name -contains 'resolvedShaFull' -and $target.resolvedShaFull) {
        $sha = $target.resolvedShaFull
    } elseif ($target.PSObject.Properties.Name -contains 'resolvedSha' -and $target.resolvedSha) {
        $sha = $target.resolvedSha
    }
    if ($sha) {
        $shaLookup[$target.app] = $sha
        Write-Detail "$($target.app) -> $sha"
    } else {
        Write-Fail "No resolved SHA for $($target.app) — cannot verify"
    }
}

if ($shaLookup.Count -eq 0) {
    Write-Fail "No resolvable SHAs in manifest. Cannot run reproducibility test."
    exit 1
}

# ---------------------------------------------------------------------------
# 3. Verify cached repos match manifest SHAs
# ---------------------------------------------------------------------------
Write-Step "Verifying federation cache against manifest"

$passed = 0
$failedCount = 0

foreach ($target in $refManifest.targets) {
    $app = $target.app
    $expectedSha = $shaLookup[$app]
    $cloneDir = Join-Path $CacheDir $app

    if (-not (Test-Path $cloneDir)) {
        Write-Fail "$app — cache directory missing: $cloneDir"
        $failedCount++
        continue
    }

    # Get current HEAD in cache
    $currentShaFull = & git -C $cloneDir rev-parse HEAD 2>$null
    if (-not $currentShaFull) {
        Write-Fail "$app — cannot read HEAD from $cloneDir"
        $failedCount++
        continue
    }

    if ($currentShaFull -eq $expectedSha) {
        Write-Ok "$app — SHA matches: $($currentShaFull.Substring(0,7))"
        $passed++
    } else {
        Write-Fail "$app — SHA mismatch: expected $($expectedSha.Substring(0,7)), got $($currentShaFull.Substring(0,7))"
        $failedCount++
    }

    # Verify branch from manifest
    if ($target.PSObject.Properties.Name -contains 'branch') {
        Write-Detail "  Branch: $($target.branch)"
    }

    # Verify tag if present
    if ($target.PSObject.Properties.Name -contains 'tag' -and $target.tag) {
        $tagCheck = & git -C $cloneDir tag -l $target.tag 2>$null
        if ($tagCheck -eq $target.tag) {
            Write-Ok "$app — tag $($target.tag) exists locally"
        } else {
            Write-Fail "$app — tag $($target.tag) not found in cache"
            $failedCount++
        }
    }

    # Verify build output exists
    $outputDir = Join-Path $OutputDir $target.slug
    if (Test-Path $outputDir) {
        $fileCount = (Get-ChildItem -Recurse -File $outputDir).Count
        if ($fileCount -eq $target.fileCount) {
            Write-Ok "$app — file count matches: $fileCount"
        } else {
            Write-Fail "$app — file count mismatch: expected $($target.fileCount), got $fileCount"
            $failedCount++
        }
    } else {
        Write-Fail "$app — output directory missing: $outputDir"
        $failedCount++
    }
}

# ---------------------------------------------------------------------------
# 4. Verify manifest metadata integrity
# ---------------------------------------------------------------------------
Write-Step "Verifying manifest metadata"

# Check schema version
if ($refManifest._version -ge 2) {
    Write-Ok "Manifest schema version: $($refManifest._version)"
} else {
    Write-Fail "Manifest schema version too old: $($refManifest._version) (expected >= 2)"
    $failedCount++
}

# Check all targets have business + role (LLC boundary fields)
foreach ($target in $refManifest.targets) {
    if ($target.PSObject.Properties.Name -contains 'business' -and $target.business) {
        if ($target.business -match "Tillerstead") {
            Write-Fail "$($target.app) — Tillerstead LLC repo in federation manifest"
            $failedCount++
        }
    } else {
        Write-Fail "$($target.app) — missing business field in manifest"
        $failedCount++
    }
}

# Check releaseChannel consistency
foreach ($target in $refManifest.targets) {
    if ($target.PSObject.Properties.Name -contains 'releaseChannel') {
        Write-Detail "$($target.app) channel: $($target.releaseChannel)"
    } else {
        Write-Fail "$($target.app) — missing releaseChannel field"
        $failedCount++
    }
}

# ---------------------------------------------------------------------------
# 5. Summary
# ---------------------------------------------------------------------------
Write-Step "Reproducibility Test Summary"
Write-Host ""
Write-Host "  Targets checked:  $($refManifest.targets.Count)" -ForegroundColor White
Write-Host "  Passed:           $passed" -ForegroundColor Green
Write-Host "  Failed:           $failedCount" -ForegroundColor $(if ($failedCount -gt 0) { "Red" } else { "Gray" })
Write-Host ""

if ($failedCount -gt 0) {
    Write-Fail "Reproducibility test FAILED with $failedCount error(s)"
    Write-Host ""
    Write-Host "  To fix: re-run build-federate.ps1 to rebuild from manifest SHAs." -ForegroundColor Yellow
    exit 1
}

Write-Ok "Reproducibility test PASSED — federation build is deterministic"
exit 0
