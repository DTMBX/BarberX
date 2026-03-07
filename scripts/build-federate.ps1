<#
.SYNOPSIS
    Federation build pipeline — clones canonical repos and builds satellite apps.

.DESCRIPTION
    Reads workspace-registry.json to identify federated satellite apps
    (entries with hasWorkspaceCopy), clones them from their canonical
    GitHub repos into .federation-cache/, installs dependencies, runs
    builds, and copies output to _site/apps/.

    Supports dual-mode versionLock:
    - dev: fetches HEAD of branch (fast iteration)
    - release: fetches exact tag or SHA (audit-grade determinism)

    See docs/architecture/BUILD-FEDERATION-SPEC.md for the full protocol.
    See docs/architecture/RELEASE-PINNING-RULES.md for the pinning policy.

.PARAMETER RegistryPath
    Path to workspace-registry.json. Defaults to tools/web-builder/workspace-registry.json.

.PARAMETER CacheDir
    Directory for cloned repos. Defaults to .federation-cache.

.PARAMETER OutputDir
    Directory for built output. Defaults to _site/apps.

.PARAMETER ManifestPath
    Path for the committed federation manifest. Defaults to federation-manifest.json.

.PARAMETER DryRun
    If set, logs what would happen without cloning or building.

.EXAMPLE
    .\scripts\build-federate.ps1
    .\scripts\build-federate.ps1 -DryRun
    .\scripts\build-federate.ps1 -CacheDir "C:\temp\fed-cache"

.NOTES
    Phase 3C — release determinism hardening.
    Copyright 2024-2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
    PROPRIETARY — See LICENSE.
#>

[CmdletBinding()]
param(
    [string]$RegistryPath = "tools/web-builder/workspace-registry.json",
    [string]$CacheDir = ".federation-cache",
    [string]$OutputDir = "_site/apps",
    [string]$ManifestPath = "federation-manifest.json",
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Clear GIT_DIR to prevent parent repo interference in cloned directories
$env:GIT_DIR = $null

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
$GITHUB_BASE = "https://github.com"

# Slug mapping: workspace copy directory name -> output slug in _site/apps/
$SLUG_MAP = @{
    "civics-hierarchy"      = "civics-hierarchy"
    "epstein-library-evid"  = "epstein-library"
    "essential-goods-ledg"  = "essential-goods"
    "geneva-bible-study-t"  = "geneva-bible-study"
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Write-Step {
    param([string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Write-Detail {
    param([string]$Message)
    Write-Host "  $Message" -ForegroundColor Gray
}

function Write-Ok {
    param([string]$Message)
    Write-Host "  OK: $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "  WARN: $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "  FAIL: $Message" -ForegroundColor Red
}

# ---------------------------------------------------------------------------
# 1. Read registry and extract federation targets
# ---------------------------------------------------------------------------
Write-Step "Reading workspace registry"

if (-not (Test-Path $RegistryPath)) {
    Write-Fail "Registry not found: $RegistryPath"
    exit 1
}

$registry = Get-Content $RegistryPath -Raw | ConvertFrom-Json
$targets = @()

foreach ($item in $registry.items) {
    # Only federate entries that have a workspace copy (the 4 dual-copy apps)
    $hasWsCopy = $null
    if ($item.PSObject.Properties.Name -contains 'hasWorkspaceCopy') {
        $hasWsCopy = $item.hasWorkspaceCopy
    }
    if (-not $hasWsCopy) { continue }

    # LLC boundary enforcement: skip Tillerstead repos
    if ($item.business -match "Tillerstead") {
        Write-Warn "Skipping $($item.name) — Tillerstead LLC boundary"
        continue
    }

    # Extract repo owner/name from remoteUrl
    $repoPath = $item.remoteUrl -replace "^https://github\.com/", ""

    # Extract directory name from hasWorkspaceCopy (e.g., "apps/civics-hierarchy/")
    $dirName = ($hasWsCopy -replace "^apps/", "") -replace "/$", ""

    # Lookup output slug
    $slug = $SLUG_MAP[$dirName]
    if (-not $slug) {
        Write-Warn "No slug mapping for $dirName — skipping"
        continue
    }

    # Resolve version lock (default to main/HEAD/dev if missing)
    $branch = "main"
    $pin = "HEAD"
    $tag = $null
    $releaseChannel = "dev"
    if ($item.PSObject.Properties.Name -contains 'versionLock' -and $item.versionLock) {
        $branch = $item.versionLock.branch
        $pin = $item.versionLock.pin
        if ($item.versionLock.PSObject.Properties.Name -contains 'tag') {
            $tag = $item.versionLock.tag
        }
        if ($item.versionLock.PSObject.Properties.Name -contains 'releaseChannel') {
            $releaseChannel = $item.versionLock.releaseChannel
        }
    }

    # Release channel enforcement: release mode requires tag or non-HEAD pin
    if ($releaseChannel -eq "release" -and -not $tag -and $pin -eq "HEAD") {
        Write-Fail "$($item.name): releaseChannel is 'release' but no tag or SHA pin set"
        $failed++
        continue
    }

    $targets += [PSCustomObject]@{
        Name           = $item.name
        Repo           = $repoPath
        DirName        = $dirName
        Slug           = $slug
        Branch         = $branch
        Pin            = $pin
        Tag            = $tag
        ReleaseChannel = $releaseChannel
        Business       = $item.business
        Role           = $item.role
        RemoteUrl      = $item.remoteUrl
    }
}

Write-Detail "Found $($targets.Count) federation target(s):"
foreach ($t in $targets) {
    $ref = if ($t.Tag) { "tag=$($t.Tag)" } elseif ($t.Pin -ne "HEAD") { "sha=$($t.Pin)" } else { "HEAD" }
    Write-Detail "  $($t.Name) -> $($t.Repo) @ $($t.Branch)/$ref [$($t.ReleaseChannel)]"
}

if ($DryRun) {
    Write-Step "DRY RUN — no cloning or building will occur"
}

# ---------------------------------------------------------------------------
# 2. Prepare directories
# ---------------------------------------------------------------------------
Write-Step "Preparing directories"

if (-not (Test-Path $CacheDir)) {
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null
    }
    Write-Detail "Created cache: $CacheDir"
} else {
    Write-Detail "Cache exists: $CacheDir"
}

if (-not (Test-Path $OutputDir)) {
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }
    Write-Detail "Created output: $OutputDir"
} else {
    Write-Detail "Output exists: $OutputDir"
}

# ---------------------------------------------------------------------------
# 3. Clone or update each target
# ---------------------------------------------------------------------------
$manifest = @{
    _schema         = "evident-federation-manifest"
    _version        = 2
    builtAt         = (Get-Date -Format "o")
    registryVersion = $registry._version
    buildMode       = "mixed"
    targets         = @()
    summary         = @{
        totalTargets = 0
        succeeded    = 0
        failed       = 0
        channel      = "mixed"
    }
}

# Determine overall build mode from targets
$channels = @($targets | ForEach-Object { $_.ReleaseChannel } | Sort-Object -Unique)
if ($channels.Count -eq 1) {
    $manifest.buildMode = $channels[0]
}

$built = 0
$failed = 0

foreach ($target in $targets) {
    Write-Step "Federating: $($target.Name)"

    $cloneDir = Join-Path $CacheDir $target.DirName
    $cloneUrl = "$GITHUB_BASE/$($target.Repo).git"
    $resolvedSha = $null
    $resolvedShaFull = $null

    # --- Determine fetch ref (tag takes precedence) ---
    $fetchRef = $target.Branch
    $useTag = $false
    if ($target.Tag) {
        $fetchRef = $target.Tag
        $useTag = $true
        Write-Detail "Resolving tag: $($target.Tag)"
    } elseif ($target.Pin -ne "HEAD") {
        Write-Detail "Resolving SHA pin: $($target.Pin)"
    }

    # --- Clone or fetch ---
    if (-not (Test-Path $cloneDir)) {
        if ($useTag) {
            Write-Detail "Cloning $cloneUrl (tag: $($target.Tag))..."
        } else {
            Write-Detail "Cloning $cloneUrl (branch: $($target.Branch))..."
        }
        if (-not $DryRun) {
            try {
                if ($useTag) {
                    & git clone --depth 1 --branch $target.Tag $cloneUrl $cloneDir 2>&1 | Out-Null
                } else {
                    & git clone --depth 1 --branch $target.Branch $cloneUrl $cloneDir 2>&1 | Out-Null
                }
                if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
                Write-Ok "Cloned"
            } catch {
                Write-Fail "Clone failed: $_"
                $failed++
                continue
            }
        } else {
            Write-Detail "[DRY RUN] Would clone $cloneUrl -> $cloneDir"
        }
    } else {
        Write-Detail "Cache hit — fetching updates..."
        if (-not $DryRun) {
            try {
                & git -C $cloneDir fetch origin $target.Branch 2>&1 | Out-Null
                if ($useTag) {
                    & git -C $cloneDir fetch origin "refs/tags/$($target.Tag):refs/tags/$($target.Tag)" 2>&1 | Out-Null
                    & git -C $cloneDir checkout "tags/$($target.Tag)" 2>&1 | Out-Null
                } else {
                    & git -C $cloneDir checkout "origin/$($target.Branch)" 2>&1 | Out-Null
                }
                if ($LASTEXITCODE -ne 0) { throw "git fetch/checkout failed" }
                Write-Ok "Updated from origin"
            } catch {
                Write-Fail "Fetch failed: $_"
                $failed++
                continue
            }
        } else {
            Write-Detail "[DRY RUN] Would fetch + checkout in $cloneDir"
        }
    }

    # --- Resolve SHA (short + full) ---
    if (-not $DryRun -and (Test-Path $cloneDir)) {
        $resolvedSha = & git -C $cloneDir rev-parse --short HEAD 2>$null
        $resolvedShaFull = & git -C $cloneDir rev-parse HEAD 2>$null
        Write-Detail "Resolved SHA: $resolvedSha ($resolvedShaFull)"

        # Verify pin if not HEAD and not using tag
        if (-not $useTag -and $target.Pin -ne "HEAD") {
            if (-not $resolvedShaFull.StartsWith($target.Pin)) {
                # Attempt to checkout the pinned commit
                try {
                    & git -C $cloneDir fetch --depth 1 origin $target.Pin 2>&1 | Out-Null
                    & git -C $cloneDir checkout $target.Pin 2>&1 | Out-Null
                    $resolvedSha = & git -C $cloneDir rev-parse --short HEAD 2>$null
                    $resolvedShaFull = & git -C $cloneDir rev-parse HEAD 2>$null
                    Write-Ok "Pinned to $resolvedSha"
                } catch {
                    Write-Fail "Pin verification failed: expected $($target.Pin), got $resolvedSha"
                    $failed++
                    continue
                }
            } else {
                Write-Ok "Pin verified: $resolvedSha"
            }
        }
    }

    # --- Install dependencies ---
    Write-Detail "Installing dependencies..."
    if (-not $DryRun) {
        $lockFile = Join-Path $cloneDir "package-lock.json"
        try {
            Push-Location $cloneDir
            if (Test-Path $lockFile) {
                & npm ci --no-audit --no-fund 2>&1 | Out-Null
                if ($LASTEXITCODE -ne 0) {
                    Write-Warn "npm ci failed (stale lockfile?) — falling back to npm install"
                    & npm install --no-audit --no-fund 2>&1 | Out-Null
                }
            } else {
                & npm install --no-audit --no-fund 2>&1 | Out-Null
            }
            if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
            Pop-Location
            Write-Ok "Dependencies installed"
        } catch {
            Pop-Location
            Write-Fail "Install failed: $_"
            $failed++
            continue
        }
    } else {
        Write-Detail "[DRY RUN] Would run npm ci in $cloneDir"
    }

    # --- Build ---
    Write-Detail "Building..."
    if (-not $DryRun) {
        try {
            Push-Location $cloneDir
            & npm run build 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }
            Pop-Location
            Write-Ok "Build complete"
        } catch {
            Pop-Location
            Write-Fail "Build failed: $_"
            $failed++
            continue
        }
    } else {
        Write-Detail "[DRY RUN] Would run npm run build in $cloneDir"
    }

    # --- Copy dist output ---
    $distPath = Join-Path $cloneDir "dist"
    $targetOutputDir = Join-Path $OutputDir $target.Slug

    if (-not $DryRun) {
        if (Test-Path $distPath) {
            if (Test-Path $targetOutputDir) {
                Remove-Item -Recurse -Force $targetOutputDir
            }
            Copy-Item -Recurse -Path $distPath -Destination $targetOutputDir
            $fileCount = (Get-ChildItem -Recurse -File $targetOutputDir).Count
            Write-Ok "Copied $fileCount files -> $targetOutputDir"
            $built++

            # Record in manifest
            $manifest.targets += @{
                app             = $target.DirName
                slug            = $target.Slug
                repo            = $target.Repo
                business        = $target.Business
                role            = $target.Role
                branch          = $target.Branch
                tag             = $target.Tag
                pin             = $target.Pin
                releaseChannel  = $target.ReleaseChannel
                resolvedSha     = $resolvedSha
                resolvedShaFull = $resolvedShaFull
                buildSuccess    = $true
                fileCount       = $fileCount
            }
        } else {
            Write-Fail "No dist/ directory after build"
            $failed++
            $manifest.targets += @{
                app             = $target.DirName
                slug            = $target.Slug
                repo            = $target.Repo
                business        = $target.Business
                role            = $target.Role
                branch          = $target.Branch
                tag             = $target.Tag
                pin             = $target.Pin
                releaseChannel  = $target.ReleaseChannel
                resolvedSha     = $resolvedSha
                resolvedShaFull = $resolvedShaFull
                buildSuccess    = $false
                fileCount       = 0
            }
        }
    } else {
        Write-Detail "[DRY RUN] Would copy $distPath -> $targetOutputDir"
    }
}

# ---------------------------------------------------------------------------
# 4. Write build manifest (both committed and cache copies)
# ---------------------------------------------------------------------------
if (-not $DryRun) {
    Write-Step "Writing federation manifest"

    # Populate summary
    $manifest.summary.totalTargets = $targets.Count
    $manifest.summary.succeeded = $built
    $manifest.summary.failed = $failed
    $summaryChannels = @($targets | ForEach-Object { $_.ReleaseChannel } | Sort-Object -Unique)
    if ($summaryChannels.Count -eq 1) {
        $manifest.summary.channel = $summaryChannels[0]
    } else {
        $manifest.summary.channel = "mixed"
    }

    $manifestJson = $manifest | ConvertTo-Json -Depth 4

    # Primary manifest (committed to repo)
    $manifestJson | Set-Content -Path $ManifestPath -Encoding utf8
    Write-Ok "Primary manifest: $ManifestPath"

    # Cache manifest (gitignored, local reference)
    $cacheManifestPath = Join-Path $CacheDir "build-manifest.json"
    $manifestJson | Set-Content -Path $cacheManifestPath -Encoding utf8
    Write-Ok "Cache manifest: $cacheManifestPath"
}

# ---------------------------------------------------------------------------
# 5. Summary
# ---------------------------------------------------------------------------
Write-Step "Federation Summary"
Write-Host ""
Write-Host "  Targets:  $($targets.Count)" -ForegroundColor White
Write-Host "  Built:    $built" -ForegroundColor Green
Write-Host "  Failed:   $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Gray" })
Write-Host "  Dry run:  $DryRun" -ForegroundColor Gray
Write-Host ""

if ($failed -gt 0) {
    Write-Fail "Federation completed with $failed failure(s)"
    exit 1
}

Write-Ok "Federation complete"
exit 0
