#!/usr/bin/env pwsh
# Satellite sync verification script
# Compares standalone repos with monorepo apps/

$ErrorActionPreference = "Continue"

$satellites = @(
    @{ Name = "civics-hierarchy"; Standalone = "c:\web-dev\github-repos\civics-hierarchy-main\civics-hierarchy"; Mono = "c:\web-dev\github-repos\Evident\apps\civics-hierarchy" },
    @{ Name = "epstein-library-evid"; Standalone = "c:\web-dev\github-repos\epstein-library-evid"; Mono = "c:\web-dev\github-repos\Evident\apps\epstein-library-evid" },
    @{ Name = "essential-goods-ledg"; Standalone = "c:\web-dev\github-repos\essential-goods-ledg"; Mono = "c:\web-dev\github-repos\Evident\apps\essential-goods-ledg" },
    @{ Name = "geneva-bible-study-t"; Standalone = "c:\web-dev\github-repos\geneva-bible-study-t-1"; Mono = "c:\web-dev\github-repos\Evident\apps\geneva-bible-study-t" }
)

$results = @()

foreach ($sat in $satellites) {
    Write-Host "`n=== $($sat.Name) ===" -ForegroundColor Cyan
    
    $standaloneExists = Test-Path $sat.Standalone
    $monoExists = Test-Path $sat.Mono
    
    if (-not $standaloneExists) {
        Write-Host "  Standalone: NOT FOUND at $($sat.Standalone)" -ForegroundColor Red
        continue
    }
    if (-not $monoExists) {
        Write-Host "  Monorepo: NOT FOUND at $($sat.Mono)" -ForegroundColor Red
        continue
    }
    
    # Count source files (excluding node_modules, .git, lock files)
    $standaloneFiles = Get-ChildItem -Path $sat.Standalone -Recurse -File | 
        Where-Object { $_.FullName -notmatch '(node_modules|\.git|package-lock\.json)' }
    $monoFiles = Get-ChildItem -Path $sat.Mono -Recurse -File | 
        Where-Object { $_.FullName -notmatch '(node_modules|\.git|package-lock\.json)' }
    
    Write-Host "  Standalone files: $($standaloneFiles.Count)" -ForegroundColor Gray
    Write-Host "  Monorepo files:   $($monoFiles.Count)" -ForegroundColor Gray
    
    # Compare key source files
    $srcStandalone = Join-Path $sat.Standalone "src"
    $srcMono = Join-Path $sat.Mono "src"
    
    if ((Test-Path $srcStandalone) -and (Test-Path $srcMono)) {
        $srcStandaloneFiles = Get-ChildItem -Path $srcStandalone -Recurse -File
        $srcMonoFiles = Get-ChildItem -Path $srcMono -Recurse -File
        Write-Host "  src/ standalone: $($srcStandaloneFiles.Count)" -ForegroundColor Gray
        Write-Host "  src/ monorepo:   $($srcMonoFiles.Count)" -ForegroundColor Gray
        
        # Check for differences in key files
        $appTsx = Join-Path $srcStandalone "App.tsx"
        $appTsxMono = Join-Path $srcMono "App.tsx"
        if ((Test-Path $appTsx) -and (Test-Path $appTsxMono)) {
            $hashStandalone = (Get-FileHash $appTsx).Hash
            $hashMono = (Get-FileHash $appTsxMono).Hash
            if ($hashStandalone -eq $hashMono) {
                Write-Host "  App.tsx: IDENTICAL" -ForegroundColor Green
            } else {
                Write-Host "  App.tsx: DIFFERS" -ForegroundColor Yellow
            }
        }
    }
    
    # Check package.json version
    $pkgStandalone = Join-Path $sat.Standalone "package.json"
    $pkgMono = Join-Path $sat.Mono "package.json"
    if ((Test-Path $pkgStandalone) -and (Test-Path $pkgMono)) {
        $hashS = (Get-FileHash $pkgStandalone).Hash
        $hashM = (Get-FileHash $pkgMono).Hash
        if ($hashS -eq $hashM) {
            Write-Host "  package.json: IDENTICAL" -ForegroundColor Green
        } else {
            Write-Host "  package.json: DIFFERS (expected)" -ForegroundColor Yellow
        }
    }
    
    $results += @{ Name = $sat.Name; StandaloneCount = $standaloneFiles.Count; MonoCount = $monoFiles.Count }
}

Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
$allSync = $true
foreach ($r in $results) {
    $diff = [Math]::Abs($r.StandaloneCount - $r.MonoCount)
    if ($diff -le 5) {
        Write-Host "  $($r.Name): OK (diff: $diff files)" -ForegroundColor Green
    } else {
        Write-Host "  $($r.Name): CHECK NEEDED (diff: $diff files)" -ForegroundColor Yellow
        $allSync = $false
    }
}

if ($allSync) {
    Write-Host "`nAll satellites appear synced with monorepo." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nSome satellites may need manual review." -ForegroundColor Yellow
    exit 1
}
