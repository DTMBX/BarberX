# Evident Repository Cleanup Script
# Organizes untracked files and identifies what to commit vs archive

Write-Host "📦 Evident Repository Cleanup" -ForegroundColor Cyan
Write-Host "=" * 60

# Create archive directory for old documentation
$archiveDir = "archive"
if (-not (Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
}

# Move old/redundant documentation to archive
Write-Host "`n📂 Moving redundant docs to archive/..." -ForegroundColor Yellow
$archiveDocs = @(
    "DAY-*-*.md",
    "PHASE-*-*.md", 
    "SESSION-*.md",
    "OVERNIGHT-*.md",
    "*-STATUS.md",
    "DEPLOY-*.md",
    "PRICING-*.md",
    "STRIPE-*-*.md",
    "WEBHOOK-*.md"
)

foreach ($pattern in $archiveDocs) {
    Get-ChildItem -Path . -Filter $pattern -File | ForEach-Object {
        Write-Host "  → $($_.Name)" -ForegroundColor Gray
        Move-Item $_.FullName -Destination $archiveDir -Force
    }
}

# Move test/utility Python scripts to scripts/
Write-Host "`n🐍 Moving utility scripts to scripts/..." -ForegroundColor Yellow
$scriptsDir = "scripts"
if (-not (Test-Path $scriptsDir)) {
    New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
}

$utilityScripts = @(
    "audit_*.py",
    "check_*.py",
    "create_*.py",
    "fix_*.py",
    "integrate_*.py",
    "migrate_*.py",
    "test_*.py",
    "verify_*.py",
    "validate_*.py"
)

foreach ($pattern in $utilityScripts) {
    Get-ChildItem -Path . -Filter $pattern -File | ForEach-Object {
        if ($_.Name -notin @("test_mobile.html")) {
            Write-Host "  → $($_.Name)" -ForegroundColor Gray
            Move-Item $_.FullName -Destination $scriptsDir -Force
        }
    }
}

# Move variant HTML files to archive
Write-Host "`n🌐 Moving HTML variants to archive/..." -ForegroundColor Yellow
$variantHtml = @(
    "pricing-*.html",
    "*-old.html",
    "*-backup.html",
    "*-test.html"
)

foreach ($pattern in $variantHtml) {
    Get-ChildItem -Path . -Filter $pattern -File | ForEach-Object {
        Write-Host "  → $($_.Name)" -ForegroundColor Gray
        Move-Item $_.FullName -Destination $archiveDir -Force
    }
}

Write-Host "`n✅ Cleanup Complete!" -ForegroundColor Green
Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "  • Archive: $(Get-ChildItem $archiveDir | Measure-Object | Select-Object -ExpandProperty Count) files" -ForegroundColor White
Write-Host "  • Scripts: $(Get-ChildItem $scriptsDir -Filter *.py | Measure-Object | Select-Object -ExpandProperty Count) files" -ForegroundColor White

Write-Host "`n💡 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review archive/ folder - move to docs/archive/ or delete" -ForegroundColor White
Write-Host "  2. Update .gitignore to exclude archive/ permanently" -ForegroundColor White
Write-Host "  3. Run: git add . && git commit -m 'Organize project structure'" -ForegroundColor White
Write-Host "  4. Optional: Delete archive/ if not needed" -ForegroundColor White
