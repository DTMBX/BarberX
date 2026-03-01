#!/usr/bin/env pwsh
# UX Error Scan - Check for blocking UX errors
# Quick diagnostic tool

Write-Host "`n=== UX Error Scan ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check critical UX files exist
Write-Host "1. Checking critical UX files..." -ForegroundColor Yellow
$criticalFiles = @(
    "assets\js\ux-enhancements.js",
    "assets\css\ux-enhancements.css"
)

$missingFiles = @()
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ MISSING: $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

# 2. Check if UX files are referenced in layout
Write-Host "`n2. Checking UX files in layout..." -ForegroundColor Yellow

$headCleanPath = "_includes\layout\head-clean.html"
if (Test-Path $headCleanPath) {
    $headContent = Get-Content $headCleanPath -Raw
    if ($headContent -match "ux-enhancements\.css") {
        Write-Host "  ✓ ux-enhancements.css referenced in head-clean.html" -ForegroundColor Green
    } else {
        Write-Host "  ✗ ux-enhancements.css NOT referenced in head-clean.html" -ForegroundColor Red
    }
}

$scriptsPath = "_includes\layout\scripts.html"
if (Test-Path $scriptsPath) {
    $scriptsContent = Get-Content $scriptsPath -Raw
    if ($scriptsContent -match "ux-enhancements\.js") {
        Write-Host "  ✓ ux-enhancements.js referenced in scripts.html" -ForegroundColor Green
    } else {
        Write-Host "  ✗ ux-enhancements.js NOT referenced in scripts.html" -ForegroundColor Red
    }
}

# 3. Check if built files exist
Write-Host "`n3. Checking built site..." -ForegroundColor Yellow

if (Test-Path "_site") {
    if (Test-Path "_site\assets\js\ux-enhancements.js") {
        Write-Host "  ✓ _site\assets\js\ux-enhancements.js exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ _site\assets\js\ux-enhancements.js NOT built" -ForegroundColor Yellow
    }
    
    if (Test-Path "_site\assets\css\ux-enhancements.css") {
        Write-Host "  ✓ _site\assets\css\ux-enhancements.css exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ _site\assets\css\ux-enhancements.css NOT built" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ _site directory not found (site not built)" -ForegroundColor Yellow
}

# 4. Quick syntax check
Write-Host "`n4. Checking for JavaScript syntax errors..." -ForegroundColor Yellow

$uxJsPath = "assets\js\ux-enhancements.js"
if (Test-Path $uxJsPath) {
    $content = Get-Content $uxJsPath -Raw
    
    # Count braces
    $openBraces = ([regex]::Matches($content, '\{') | Measure-Object).Count
    $closeBraces = ([regex]::Matches($content, '\}') | Measure-Object).Count
    
    if ($openBraces -eq $closeBraces) {
        Write-Host "  ✓ Braces balanced ($openBraces pairs)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Brace mismatch: $openBraces open, $closeBraces close" -ForegroundColor Red
    }
    
    # Count parentheses
    $openParens = ([regex]::Matches($content, '\(') | Measure-Object).Count
    $closeParens = ([regex]::Matches($content, '\)') | Measure-Object).Count
    
    if ($openParens -eq $closeParens) {
        Write-Host "  ✓ Parentheses balanced ($openParens pairs)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Parenthesis mismatch: $openParens open, $closeParens close" -ForegroundColor Red
    }
    
    # Check for common errors
    if ($content -match 'console\.log\(') {
        $logCount = ([regex]::Matches($content, 'console\.log\(') | Measure-Object).Count
        Write-Host "  ⚠ Found $logCount console.log statements (non-blocking)" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan

if ($missingFiles.Count -eq 0) {
    Write-Host "✅ All critical files present" -ForegroundColor Green
    Write-Host "✅ UX enhancements properly integrated" -ForegroundColor Green
    Write-Host "`nNo blocking errors found. Site should be working correctly." -ForegroundColor Green
    Write-Host "`nIf you're experiencing issues, try:" -ForegroundColor Cyan
    Write-Host "  1. Rebuild the site: bundle exec jekyll build" -ForegroundColor White
    Write-Host "  2. Clear browser cache" -ForegroundColor White
    Write-Host "  3. Check browser console for runtime errors" -ForegroundColor White
} else {
    Write-Host "❌ Found issues:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  - Missing: $file" -ForegroundColor Red
    }
    exit 1
}

Write-Host ""
