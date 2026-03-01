#!/usr/bin/env pwsh
<#
.SYNOPSIS
Reorganize Jekyll _includes directory according to Tillerstead taxonomy.

.DESCRIPTION
Moves files from _includes root into proper subdirectories and updates all references.
SAFE: Creates backup, updates references, validates build before committing changes.

.PARAMETER RepoRoot
Root of the repository. Default: current directory.

.PARAMETER WhatIf
Preview changes without making them.

.PARAMETER Force
Skip confirmation prompts.

.EXAMPLE
.\tools\reorganize-includes.ps1 -WhatIf
Preview the reorganization.

.EXAMPLE
.\tools\reorganize-includes.ps1
Execute the reorganization with confirmation.

.EXAMPLE
.\tools\reorganize-includes.ps1 -Force
Execute without prompts.
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$RepoRoot = (Get-Location).Path,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Colors
function Write-Section($msg) { Write-Host "`n$msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Info($msg) { Write-Host "  • $msg" -ForegroundColor Gray }
function Write-Warn($msg) { Write-Host "  ⚠ $msg" -ForegroundColor Yellow }
function Write-Error-Custom($msg) { Write-Host "  ✗ $msg" -ForegroundColor Red }

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║  TILLERSTEAD INCLUDES REORGANIZATION                       ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow

# Validate repo
$includesDir = Join-Path $RepoRoot "_includes"
if (-not (Test-Path $includesDir)) {
    Write-Error-Custom "_includes directory not found at: $includesDir"
    exit 1
}

# Define reorganization plan
$reorganizationPlan = @{
    "layout" = @(
        "head.html",
        "header.html",
        "footer.html",
        "scripts.html"
    )
    "navigation" = @(
        "nav-drawer.html",
        "breadcrumbs.html",
        "ts-breadcrumbs.html",
        "toc.html"
    )
    "sections" = @(
        "about-section.html",
        "blog-highlights.html",
        "faq-section.html",
        "home-cta-final.html",
        "home-faq.html",
        "home-portfolio-preview.html",
        "home-services-preview.html",
        "home-simple.html",
        "home-trust-stats.html",
        "portfolio-highlights.html",
        "portfolio.html",
        "process.html",
        "services.html",
        "testimonials.html",
        "section-trust-bar.html",
        "ts-peace-of-mind.html",
        "ts-portfolio.html",
        "ts-process.html",
        "ts-services.html"
    )
    "components" = @(
        "build-phase-cta.html",
        "build-prev-next.html",
        "build-sidebar.html",
        "build-sidenav.html",
        "cta-estimate.html",
        "cta.html",
        "logo-header.html",
        "logo-sprite-inline.html",
        "pattern-showcase.html",
        "responsive-image.html",
        "social-links.html",
        "ts-icon-sprite.html",
        "ts-icon.html",
        "ts-plans.html",
        "ts-service-card.html"
    )
    "hero" = @(
        "hero.html",
        "page-hero.html"
    )
    "forms" = @(
        "contact-long.html",
        "contact-options.html",
        "contact-page.html",
        "contact.html"
    )
    "schema" = @(
        "schema-combined.js"
    )
}

# Step 1: Validate all files exist
Write-Section "📋 Step 1: Validating files..."
$missingFiles = @()
$totalFiles = 0

foreach ($folder in $reorganizationPlan.Keys) {
    foreach ($file in $reorganizationPlan[$folder]) {
        $totalFiles++
        $sourcePath = Join-Path $includesDir $file
        if (-not (Test-Path $sourcePath)) {
            $missingFiles += $file
            Write-Warn "Missing: $file"
        } else {
            Write-Info "Found: $file → $folder\"
        }
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Warn "$($missingFiles.Count) files not found in root (may already be organized)"
    Write-Info "Continuing with available files..."
}

Write-Success "Validated $totalFiles files"

# Step 2: Create backup
Write-Section "💾 Step 2: Creating backup..."
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $RepoRoot "archive\includes-reorganization\$timestamp"

if (-not $WhatIfPreference) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    Copy-Item -Path $includesDir -Destination $backupDir -Recurse -Force
    Write-Success "Backup created: $backupDir"
} else {
    Write-Info "Would create backup at: $backupDir"
}

# Step 3: Find all references
Write-Section "🔍 Step 3: Finding references..."

function Find-AllReferences {
    param([string]$fileName)
    
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($fileName)
    $extension = [System.IO.Path]::GetExtension($fileName)
    
    $patterns = @(
        "{% include `"$fileName`"",
        "{% include '$fileName'",
        "{% include $fileName",
        "{% include_relative `"$fileName`"",
        "{% include_relative '$fileName'",
        "{% include_relative $fileName"
    )
    
    $excludeDirs = @("_site", ".git", "node_modules", "vendor", ".bundle", ".jekyll-cache", "archive", "_reports")
    $searchExtensions = @("*.html", "*.md", "*.liquid", "*.markdown", "*.yml", "*.yaml")
    
    $allRefs = @()
    
    foreach ($pattern in $patterns) {
        foreach ($ext in $searchExtensions) {
            $files = Get-ChildItem -Path $RepoRoot -Filter $ext -Recurse -File -ErrorAction SilentlyContinue | 
                Where-Object {
                    $exclude = $false
                    foreach ($dir in $excludeDirs) {
                        if ($_.FullName -like "*\$dir\*") { $exclude = $true; break }
                    }
                    -not $exclude
                }
            
            foreach ($file in $files) {
                $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
                if ($content -and $content -match [regex]::Escape($fileName)) {
                    $lineNum = 0
                    foreach ($line in (Get-Content $file.FullName)) {
                        $lineNum++
                        if ($line -match [regex]::Escape($fileName)) {
                            $allRefs += [PSCustomObject]@{
                                File = $file.FullName.Replace($RepoRoot, "").TrimStart('\')
                                Line = $lineNum
                                Content = $line.Trim()
                            }
                        }
                    }
                }
            }
        }
    }
    
    return $allRefs
}

# Build reference map
$referenceMap = @{}
$totalRefs = 0

foreach ($folder in $reorganizationPlan.Keys) {
    foreach ($file in $reorganizationPlan[$folder]) {
        $sourcePath = Join-Path $includesDir $file
        if (Test-Path $sourcePath) {
            $refs = Find-AllReferences -fileName $file
            if ($refs) {
                $referenceMap[$file] = @{
                    Folder = $folder
                    References = $refs
                }
                $totalRefs += $refs.Count
                Write-Info "$file → $($refs.Count) references"
            } else {
                $referenceMap[$file] = @{
                    Folder = $folder
                    References = @()
                }
                Write-Info "$file → no references"
            }
        }
    }
}

Write-Success "Found $totalRefs total references across $(($referenceMap.Keys | Measure-Object).Count) files"

# Step 4: Move files
Write-Section "📦 Step 4: Moving files..."

$moveCount = 0
foreach ($file in $referenceMap.Keys) {
    $folder = $referenceMap[$file].Folder
    $sourcePath = Join-Path $includesDir $file
    $destFolder = Join-Path $includesDir $folder
    $destPath = Join-Path $destFolder $file
    
    if (-not (Test-Path $sourcePath)) {
        Write-Warn "Skip $file (not in root)"
        continue
    }
    
    if ($PSCmdlet.ShouldProcess($file, "Move to $folder\")) {
        # Create destination folder
        if (-not (Test-Path $destFolder)) {
            New-Item -ItemType Directory -Path $destFolder -Force | Out-Null
        }
        
        # Move file
        Move-Item -Path $sourcePath -Destination $destPath -Force
        $moveCount++
        Write-Success "$file → $folder\"
    } else {
        Write-Info "Would move: $file → $folder\"
    }
}

Write-Success "Moved $moveCount files"

# Step 5: Update references
Write-Section "🔧 Step 5: Updating references..."

$updateCount = 0
foreach ($file in $referenceMap.Keys) {
    $folder = $referenceMap[$file].Folder
    $refs = $referenceMap[$file].References
    
    if ($refs.Count -eq 0) { continue }
    
    $newPath = "$folder/$file"
    
    foreach ($ref in $refs) {
        $refFile = Join-Path $RepoRoot $ref.File
        
        if (-not (Test-Path $refFile)) { continue }
        
        if ($PSCmdlet.ShouldProcess($refFile, "Update reference to $newPath")) {
            $content = Get-Content $refFile -Raw
            
            # Replace all variants
            $content = $content -replace "{% include `"$file`"", "{% include `"$newPath`""
            $content = $content -replace "{% include '$file'", "{% include '$newPath'"
            $content = $content -replace "{% include $file(\s+[^%])", "{% include $newPath`$1"
            $content = $content -replace "{% include $file\s*%}", "{% include $newPath %}"
            
            Set-Content -Path $refFile -Value $content -NoNewline
            $updateCount++
            Write-Success "Updated: $($ref.File):$($ref.Line)"
        } else {
            Write-Info "Would update: $($ref.File):$($ref.Line) → $newPath"
        }
    }
}

Write-Success "Updated $updateCount file references"

# Step 6: Validate Jekyll build
if (-not $WhatIfPreference) {
    Write-Section "🧪 Step 6: Validating Jekyll build..."
    
    $buildResult = & bundle exec jekyll build 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Jekyll build successful!"
    } else {
        Write-Error-Custom "Jekyll build FAILED! Rolling back..."
        Write-Host ""
        Write-Host $buildResult -ForegroundColor Red
        
        # Restore from backup
        Write-Warn "Restoring from backup..."
        Remove-Item -Path $includesDir -Recurse -Force
        Copy-Item -Path (Join-Path $backupDir "_includes") -Destination $RepoRoot -Recurse -Force
        
        Write-Error-Custom "Reorganization rolled back. Check errors above."
        exit 1
    }
}

# Summary
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ REORGANIZATION COMPLETE                                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  Files moved: $moveCount" -ForegroundColor Green
Write-Host "  References updated: $updateCount" -ForegroundColor Green
Write-Host "  Backup location: $backupDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Test site locally: bundle exec jekyll serve"
Write-Host "  2. Verify all pages load correctly"
Write-Host "  3. Commit changes: git add . && git commit -m 'refactor: reorganize includes directory'"
Write-Host ""
