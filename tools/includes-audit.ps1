<#
.SYNOPSIS
    Audit Jekyll _includes directory for redundancy and generate cleanup plan.

.DESCRIPTION
    Scans _includes recursively, identifies duplicates (exact and normalized),
    finds references in the repo, and proposes a safe cleanup plan.

.PARAMETER RepoRoot
    Path to repository root. Default: current directory.

.PARAMETER ArchiveRedundant
    Archive redundant files to archive\includes-redundant\<timestamp>\.

.PARAMETER FixReferences
    Rewrite include references to use canonical paths.

.PARAMETER DeleteAfterArchive
    Delete redundant files after archiving (requires -ArchiveRedundant).

.EXAMPLE
    .\tools\includes-audit.ps1
    Run audit and generate reports only.

.EXAMPLE
    .\tools\includes-audit.ps1 -ArchiveRedundant -WhatIf
    Preview archiving redundant includes.

.EXAMPLE
    .\tools\includes-audit.ps1 -ArchiveRedundant -FixReferences
    Archive redundant files and update references.
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter()]
    [string]$RepoRoot = (Get-Location).Path,
    
    [Parameter()]
    [switch]$ArchiveRedundant,
    
    [Parameter()]
    [switch]$FixReferences,
    
    [Parameter()]
    [switch]$DeleteAfterArchive
)

#Requires -Version 7.0

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ============================================================================
# CONFIGURATION
# ============================================================================

$IncludesDir = Join-Path $RepoRoot '_includes'
$ReportsDir = Join-Path $RepoRoot '_reports'
$ArchiveBaseDir = Join-Path $RepoRoot 'archive' 'includes-redundant'
$ExcludeDirs = @('_site', '.git', 'node_modules', 'vendor', '.bundle', '.jekyll-cache', 'archive', '_reports')

# ============================================================================
# VALIDATION
# ============================================================================

Write-Host "`n🔍 Jekyll Includes Auditor v1.0" -ForegroundColor Cyan
Write-Host ("="*60) -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $IncludesDir)) {
    Write-Error "Includes directory not found: $IncludesDir"
    exit 1
}

if ($DeleteAfterArchive -and -not $ArchiveRedundant) {
    Write-Error "-DeleteAfterArchive requires -ArchiveRedundant"
    exit 1
}

if (-not (Test-Path $ReportsDir)) {
    New-Item -ItemType Directory -Path $ReportsDir -Force | Out-Null
    Write-Host "✓ Created reports directory" -ForegroundColor Green
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Get-FileHashSHA256 {
    param([string]$FilePath)
    try {
        return (Get-FileHash -Path $FilePath -Algorithm SHA256).Hash
    }
    catch {
        return "ERROR_READING_FILE"
    }
}

function Get-NormalizedContentHash {
    param([string]$FilePath)
    try {
        $content = Get-Content -Path $FilePath -Raw -ErrorAction Stop
        if ([string]::IsNullOrEmpty($content)) { return "EMPTY_FILE" }
        
        # Normalize: trim trailing whitespace, normalize line endings
        $lines = $content -split "`r?`n"
        $normalized = ($lines | ForEach-Object { $_.TrimEnd() }) -join "`n"
        $normalized = $normalized.Trim()
        
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($normalized)
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        $hashBytes = $sha256.ComputeHash($bytes)
        return [BitConverter]::ToString($hashBytes) -replace '-', ''
    }
    catch {
        return "ERROR_NORMALIZING"
    }
}

function Get-CanonicalScore {
    param([string]$RelativePath)
    
    $score = 0
    $pathLower = $RelativePath.ToLower()
    
    # Prefer shorter paths (less nesting)
    $depth = ($RelativePath -split '[/\\]').Count
    $score += (10 - $depth) * 10
    
    # Prefer standard Jekyll folders
    if ($pathLower -match 'components') { $score += 50 }
    if ($pathLower -match 'sections') { $score += 40 }
    if ($pathLower -match 'layout') { $score += 40 }
    if ($pathLower -match 'navigation') { $score += 35 }
    if ($pathLower -match 'forms') { $score += 30 }
    if ($pathLower -match 'schema') { $score += 30 }
    
    # Penalize non-production folders
    if ($pathLower -match 'backup') { $score -= 100 }
    if ($pathLower -match 'old') { $score -= 100 }
    if ($pathLower -match 'temp') { $score -= 100 }
    if ($pathLower -match 'archive') { $score -= 100 }
    if ($pathLower -match 'deprecated') { $score -= 90 }
    if ($pathLower -match 'legacy') { $score -= 85 }
    if ($pathLower -match 'copy') { $score -= 80 }
    if ($pathLower -match 'v\d+') { $score -= 60 }
    if ($pathLower -match '\d{4}-\d{2}') { $score -= 70 }
    
    return $score
}

function Find-IncludeReferences {
    param(
        [string]$IncludeName,
        [string]$RelativePath,
        [string]$SearchRoot,
        [string[]]$ExcludeFolders
    )
    
    $references = @()
    
    try {
        $files = Get-ChildItem -Path $SearchRoot -Recurse -File -Include '*.html','*.md','*.liquid','*.markdown' -ErrorAction SilentlyContinue
        
        foreach ($file in $files) {
            # Skip excluded directories
            $skip = $false
            foreach ($exclude in $ExcludeFolders) {
                if ($file.FullName -match [regex]::Escape($exclude)) {
                    $skip = $true
                    break
                }
            }
            if ($skip) { continue }
            
            try {
                $lineNum = 0
                $lines = Get-Content -Path $file.FullName -ErrorAction Stop
                
                foreach ($line in $lines) {
                    $lineNum++
                    
                    # Check for include patterns
                    if ($line -match "{%\s*include\s+[`"']?$IncludeName" -or
                        $line -match "{%\s*include\s+[`"']?$RelativePath" -or
                        $line -match "{%\s*include_relative\s+[`"']?$IncludeName") {
                        
                        $references += [PSCustomObject]@{
                            File = $file.FullName.Replace($SearchRoot, '').TrimStart('\', '/')
                            Line = $lineNum
                            Content = $line.Trim()
                        }
                    }
                }
            }
            catch {
                # Skip files that can't be read
            }
        }
    }
    catch {
        Write-Warning "Error searching references: $_"
    }
    
    return $references
}

# ============================================================================
# PHASE 1: INVENTORY
# ============================================================================

Write-Host "📋 Phase 1: Scanning _includes directory..." -ForegroundColor Yellow

$inventory = @()
$files = Get-ChildItem -Path $IncludesDir -Recurse -File -ErrorAction Stop

foreach ($file in $files) {
    $relativePath = $file.FullName.Replace($IncludesDir, '').TrimStart('\', '/')
    Write-Host "  Processing: $relativePath" -ForegroundColor Gray
    
    $inventory += [PSCustomObject]@{
        FullPath = $file.FullName
        RelativePath = $relativePath
        Name = $file.Name
        Extension = $file.Extension
        SizeBytes = $file.Length
        LastWriteTime = $file.LastWriteTime
        SHA256 = Get-FileHashSHA256 -FilePath $file.FullName
        NormalizedHash = Get-NormalizedContentHash -FilePath $file.FullName
        CanonicalScore = Get-CanonicalScore -RelativePath $relativePath
    }
}

Write-Host "`n✓ Found $($inventory.Count) files" -ForegroundColor Green

# Save inventory
$inventoryCsv = Join-Path $ReportsDir 'includes-inventory.csv'
$inventory | Export-Csv -Path $inventoryCsv -NoTypeInformation
Write-Host "✓ Saved: $inventoryCsv" -ForegroundColor Green

# ============================================================================
# PHASE 2: IDENTIFY DUPLICATES
# ============================================================================

Write-Host "`n📊 Phase 2: Identifying duplicates..." -ForegroundColor Yellow

$duplicates = @{
    ExactDuplicates = @()
    NormalizedDuplicates = @()
    SameNameDifferentPath = @()
}

# Exact duplicates (same SHA256)
$exactGroups = $inventory | Where-Object { $_.SHA256 -ne "ERROR_READING_FILE" } | 
    Group-Object -Property SHA256 | Where-Object { $_.Count -gt 1 }

foreach ($group in $exactGroups) {
    $canonical = $group.Group | Sort-Object -Property CanonicalScore -Descending | Select-Object -First 1
    $redundant = $group.Group | Where-Object { $_.RelativePath -ne $canonical.RelativePath }
    
    $duplicates.ExactDuplicates += [PSCustomObject]@{
        Hash = $group.Name
        Count = $group.Count
        Canonical = $canonical.RelativePath
        CanonicalScore = $canonical.CanonicalScore
        AllFiles = @($group.Group.RelativePath)
        RedundantFiles = @($redundant.RelativePath)
    }
}

# Normalized duplicates (same content after normalization)
$normalizedGroups = $inventory | Where-Object { $_.NormalizedHash -ne "ERROR_NORMALIZING" -and $_.NormalizedHash -ne "EMPTY_FILE" } |
    Group-Object -Property NormalizedHash | Where-Object { $_.Count -gt 1 }

foreach ($group in $normalizedGroups) {
    # Skip if already in exact duplicates
    $alreadyInExact = $false
    foreach ($exactDup in $duplicates.ExactDuplicates) {
        if ($group.Group[0].SHA256 -in $exactDup.Hash) {
            $alreadyInExact = $true
            break
        }
    }
    if ($alreadyInExact) { continue }
    
    $canonical = $group.Group | Sort-Object -Property CanonicalScore -Descending | Select-Object -First 1
    $redundant = $group.Group | Where-Object { $_.RelativePath -ne $canonical.RelativePath }
    
    $duplicates.NormalizedDuplicates += [PSCustomObject]@{
        Hash = $group.Name
        Count = $group.Count
        Canonical = $canonical.RelativePath
        CanonicalScore = $canonical.CanonicalScore
        AllFiles = @($group.Group.RelativePath)
        RedundantFiles = @($redundant.RelativePath)
    }
}

# Same filename, different locations
$nameGroups = $inventory | Group-Object -Property Name | Where-Object { $_.Count -gt 1 }

foreach ($group in $nameGroups) {
    $canonical = $group.Group | Sort-Object -Property CanonicalScore -Descending | Select-Object -First 1
    
    $duplicates.SameNameDifferentPath += [PSCustomObject]@{
        Filename = $group.Name
        Count = $group.Count
        Canonical = $canonical.RelativePath
        CanonicalScore = $canonical.CanonicalScore
        AllFiles = @($group.Group.RelativePath)
    }
}

Write-Host "✓ Exact duplicates: $($duplicates.ExactDuplicates.Count) groups" -ForegroundColor Green
Write-Host "✓ Normalized duplicates: $($duplicates.NormalizedDuplicates.Count) groups" -ForegroundColor Green
Write-Host "✓ Same-name conflicts: $($duplicates.SameNameDifferentPath.Count) groups" -ForegroundColor Green

$duplicatesJson = Join-Path $ReportsDir 'includes-duplicates.json'
$duplicates | ConvertTo-Json -Depth 10 | Set-Content -Path $duplicatesJson
Write-Host "✓ Saved: $duplicatesJson" -ForegroundColor Green

# ============================================================================
# PHASE 3: FIND REFERENCES
# ============================================================================

Write-Host "`n🔎 Phase 3: Finding references..." -ForegroundColor Yellow

$allRedundant = @()
foreach ($group in $duplicates.ExactDuplicates) {
    $allRedundant += $group.RedundantFiles
}
foreach ($group in $duplicates.NormalizedDuplicates) {
    $allRedundant += $group.RedundantFiles
}
$allRedundant = $allRedundant | Where-Object { $_ } | Select-Object -Unique

$referenceMap = @{}
$totalRefs = 0

foreach ($redundantPath in $allRedundant) {
    $fileName = Split-Path -Leaf $redundantPath
    Write-Host "  Searching: $fileName" -ForegroundColor Gray
    
    $refs = Find-IncludeReferences -IncludeName $fileName -RelativePath $redundantPath -SearchRoot $RepoRoot -ExcludeFolders $ExcludeDirs
    $referenceMap[$redundantPath] = $refs
    if ($refs) {
        $totalRefs += $refs.Count
    }
}

Write-Host "✓ Found $totalRefs references to redundant files" -ForegroundColor Green

# ============================================================================
# PHASE 4: GENERATE CLEANUP PLAN
# ============================================================================

Write-Host "`n📝 Phase 4: Generating cleanup plan..." -ForegroundColor Yellow

$totalRedundantFiles = $allRedundant.Count

$planContent = @"
# Jekyll Includes Cleanup Plan

**Generated:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## Summary

- **Total files:** $($inventory.Count)
- **Exact duplicate groups:** $($duplicates.ExactDuplicates.Count)
- **Normalized duplicate groups:** $($duplicates.NormalizedDuplicates.Count)
- **Same-name conflicts:** $($duplicates.SameNameDifferentPath.Count)
- **Total redundant files:** $totalRedundantFiles
- **References to update:** $totalRefs

---

## 📌 Exact Duplicates

Byte-for-byte identical files that can be safely consolidated.

"@

if ($duplicates.ExactDuplicates.Count -eq 0) {
    $planContent += "`n✅ No exact duplicates found.`n"
} else {
    foreach ($dup in $duplicates.ExactDuplicates) {
        $planContent += @"

### Duplicate Group
- **Canonical:** ``$($dup.Canonical)`` (score: $($dup.CanonicalScore))
- **Total files:** $($dup.Count)

**Redundant files:**
"@
        foreach ($redundant in $dup.RedundantFiles) {
            $refs = $referenceMap[$redundant]
            if ($refs -and $refs.Count -gt 0) {
                $planContent += "`n- ``$redundant`` ⚠️ **$($refs.Count) reference(s)**"
                foreach ($ref in ($refs | Select-Object -First 3)) {
                    $planContent += "`n  - $($ref.File):$($ref.Line)"
                }
                if ($refs.Count -gt 3) {
                    $planContent += "`n  - ... and $($refs.Count - 3) more"
                }
            } else {
                $planContent += "`n- ``$redundant`` ✓ No references"
            }
        }
        $planContent += "`n"
    }
}

$planContent += @"

---

## 🔄 Normalized Duplicates

Same content after normalizing whitespace/line endings.

"@

if ($duplicates.NormalizedDuplicates.Count -eq 0) {
    $planContent += "`n✅ No normalized duplicates found.`n"
} else {
    foreach ($dup in $duplicates.NormalizedDuplicates) {
        $planContent += @"

### Duplicate Group
- **Canonical:** ``$($dup.Canonical)`` (score: $($dup.CanonicalScore))
- **Total files:** $($dup.Count)

**Redundant files:**
"@
        foreach ($redundant in $dup.RedundantFiles) {
            $refs = $referenceMap[$redundant]
            if ($refs -and $refs.Count -gt 0) {
                $planContent += "`n- ``$redundant`` ⚠️ **$($refs.Count) reference(s)**"
            } else {
                $planContent += "`n- ``$redundant`` ✓ No references"
            }
        }
        $planContent += "`n"
    }
}

$planContent += @"

---

## ⚠️ Same Name, Different Paths

Files with the same name in different locations. **Manual review recommended.**

"@

if ($duplicates.SameNameDifferentPath.Count -eq 0) {
    $planContent += "`n✅ No same-name conflicts.`n"
} else {
    foreach ($conflict in $duplicates.SameNameDifferentPath) {
        $planContent += @"

### Filename: ``$($conflict.Filename)``
- **Suggested canonical:** ``$($conflict.Canonical)`` (score: $($conflict.CanonicalScore))
- **All locations:**
"@
        foreach ($file in $conflict.AllFiles) {
            if ($file -eq $conflict.Canonical) {
                $planContent += "`n  - ``$file`` ✅ (recommended)"
            } else {
                $planContent += "`n  - ``$file``"
            }
        }
        $planContent += "`n"
    }
}

$planContent += @"

---

## 🎯 Next Steps

``````powershell
# Preview actions
.\tools\includes-audit.ps1 -ArchiveRedundant -FixReferences -WhatIf

# Execute cleanup
.\tools\includes-audit.ps1 -ArchiveRedundant -FixReferences

# Test site
bundle exec jekyll build
bundle exec jekyll serve
``````
"@

$cleanupPlan = Join-Path $ReportsDir 'includes-cleanup-plan.md'
$planContent | Set-Content -Path $cleanupPlan
Write-Host "✓ Saved: $cleanupPlan" -ForegroundColor Green

# ============================================================================
# PHASE 5: EXECUTE ACTIONS
# ============================================================================

if ($ArchiveRedundant) {
    Write-Host "`n🗄️  Phase 5: Archiving redundant files..." -ForegroundColor Yellow
    
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $archiveDir = Join-Path $ArchiveBaseDir $timestamp
    
    $archivedCount = 0
    
    foreach ($redundantPath in $allRedundant) {
        $sourcePath = Join-Path $IncludesDir $redundantPath
        $destPath = Join-Path $archiveDir $redundantPath
        $destDir = Split-Path -Parent $destPath
        
        if ($PSCmdlet.ShouldProcess($redundantPath, "Archive file")) {
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            
            Copy-Item -Path $sourcePath -Destination $destPath -Force
            $archivedCount++
            Write-Host "  ✓ Archived: $redundantPath" -ForegroundColor Green
            
            if ($DeleteAfterArchive) {
                if ($PSCmdlet.ShouldProcess($redundantPath, "Delete after archiving")) {
                    Remove-Item -Path $sourcePath -Force
                    Write-Host "    🗑️  Deleted: $redundantPath" -ForegroundColor Yellow
                }
            }
        }
    }
    
    # Create manifest
    $manifest = @{
        Timestamp = $timestamp
        TotalArchived = $archivedCount
        DeletedAfterArchive = $DeleteAfterArchive.IsPresent
        Files = $allRedundant
    }
    
    $manifestPath = Join-Path $archiveDir '_manifest.json'
    if ($PSCmdlet.ShouldProcess($manifestPath, "Create manifest")) {
        $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath
        Write-Host "`n✓ Archive complete: $archiveDir" -ForegroundColor Green
    }
}

if ($FixReferences) {
    Write-Host "`n🔧 Phase 6: Fixing references..." -ForegroundColor Yellow
    
    # Build map of redundant -> canonical
    $canonicalMap = @{}
    foreach ($group in $duplicates.ExactDuplicates + $duplicates.NormalizedDuplicates) {
        foreach ($redundant in $group.RedundantFiles) {
            $canonicalMap[$redundant] = $group.Canonical
        }
    }
    
    $filesUpdated = 0
    
    foreach ($redundantPath in $canonicalMap.Keys) {
        $canonicalPath = $canonicalMap[$redundantPath]
        $refs = $referenceMap[$redundantPath]
        
        if (-not $refs -or $refs.Count -eq 0) { continue }
        
        $redundantName = Split-Path -Leaf $redundantPath
        $canonicalName = Split-Path -Leaf $canonicalPath
        
        foreach ($ref in $refs) {
            $refFilePath = Join-Path $RepoRoot $ref.File
            
            if ($PSCmdlet.ShouldProcess($ref.File, "Update include reference")) {
                try {
                    $content = Get-Content -Path $refFilePath -Raw
                    $original = $content
                    
                    # Replace references
                    $content = $content -replace [regex]::Escape($redundantPath), $canonicalPath
                    $content = $content -replace "include\s+`"$redundantName`"", "include `"$canonicalName`""
                    $content = $content -replace "include\s+'$redundantName'", "include '$canonicalName'"
                    $content = $content -replace "include\s+$redundantName(\s|%)", "include $canonicalName`$1"
                    
                    if ($content -ne $original) {
                        $content | Set-Content -Path $refFilePath -NoNewline
                        $filesUpdated++
                        Write-Host "  ✓ Updated: $($ref.File)" -ForegroundColor Green
                    }
                }
                catch {
                    Write-Warning "Failed to update $($ref.File): $_"
                }
            }
        }
    }
    
    Write-Host "`n✓ Updated $filesUpdated file(s)" -ForegroundColor Green
}

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "`n" + ("="*60) -ForegroundColor Cyan
Write-Host "✅ Audit Complete!" -ForegroundColor Green
Write-Host ("="*60) -ForegroundColor Cyan

Write-Host "`n📊 Reports:" -ForegroundColor Yellow
Write-Host "  - $inventoryCsv"
Write-Host "  - $duplicatesJson"
Write-Host "  - $cleanupPlan"

if (-not $ArchiveRedundant -and -not $FixReferences) {
    Write-Host "`n📖 Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Review: $cleanupPlan"
    Write-Host "  2. Preview: .\tools\includes-audit.ps1 -ArchiveRedundant -WhatIf"
    Write-Host "  3. Execute: .\tools\includes-audit.ps1 -ArchiveRedundant -FixReferences"
}

Write-Host ""
