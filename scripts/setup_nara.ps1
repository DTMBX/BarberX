# National Archives API - Quick Setup Script
# Windows PowerShell

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  National Archives API - Quick Setup & Test" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check for Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check for .env file
Write-Host ""
Write-Host "[2/5] Checking .env configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✅ .env file exists" -ForegroundColor Green
    
    # Check for NARA_API_KEY
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "NARA_API_KEY=(\S+)") {
        $apiKey = $matches[1]
        if ($apiKey -ne "your-nara-api-key-here" -and $apiKey.Length -gt 10) {
            Write-Host "  ✅ NARA_API_KEY is configured" -ForegroundColor Green
            $hasApiKey = $true
        } else {
            Write-Host "  ⚠️  NARA_API_KEY not configured" -ForegroundColor Yellow
            $hasApiKey = $false
        }
    } else {
        Write-Host "  ⚠️  NARA_API_KEY not found in .env" -ForegroundColor Yellow
        $hasApiKey = $false
    }
} else {
    Write-Host "  ⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "  Creating .env from template..." -ForegroundColor Yellow
    Copy-Item ".env.template" ".env"
    Write-Host "  ✅ Created .env file" -ForegroundColor Green
    $hasApiKey = $false
}

if (-not $hasApiKey) {
    Write-Host ""
    Write-Host "  📧 To get an API key, contact:" -ForegroundColor Cyan
    Write-Host "     Email: Catalog_API@nara.gov" -ForegroundColor White
    Write-Host "     Subject: API Key Request - Evident Technologies" -ForegroundColor White
    Write-Host ""
    Write-Host "  Then add it to your .env file:" -ForegroundColor Cyan
    Write-Host "     NARA_API_KEY=your-actual-api-key" -ForegroundColor White
    Write-Host ""
    
    $continue = Read-Host "  Do you want to continue with setup anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host ""
        Write-Host "Setup cancelled. Get your API key and run this script again." -ForegroundColor Yellow
        exit 0
    }
}

# Install dependencies
Write-Host ""
Write-Host "[3/5] Installing dependencies..." -ForegroundColor Yellow
try {
    pip install requests python-dotenv -q
    Write-Host "  ✅ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host ""
Write-Host "[4/5] Creating directories..." -ForegroundColor Yellow
$directories = @("documents/founding", "cache/nara", "logs")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✓ Exists: $dir" -ForegroundColor Gray
    }
}

# Run tests if API key is configured
if ($hasApiKey) {
    Write-Host ""
    Write-Host "[5/5] Running setup tests..." -ForegroundColor Yellow
    Write-Host ""
    
    python scripts/test_nara_setup.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "  ✅ Setup Complete! National Archives API is ready to use" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "  • Fetch documents: python scripts\fetch_founding_documents.py" -ForegroundColor White
        Write-Host "  • Run examples: python examples\nara_integration_examples.py" -ForegroundColor White
        Write-Host "  • Read docs: docs\NARA_QUICKSTART.md" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "⚠️  Setup tests failed. Check the output above for details." -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host ""
    Write-Host "[5/5] Skipping tests (no API key configured)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Yellow
    Write-Host "  ⚠️  Setup Complete (pending API key)" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Get API key from Catalog_API@nara.gov" -ForegroundColor White
    Write-Host "  2. Add to .env: NARA_API_KEY=your-key" -ForegroundColor White
    Write-Host "  3. Run this script again to test" -ForegroundColor White
    Write-Host ""
}

Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  • Quick Start: docs\NARA_QUICKSTART.md" -ForegroundColor White
Write-Host "  • Full Guide: docs\NATIONAL_ARCHIVES_API.md" -ForegroundColor White
Write-Host "  • Examples: examples\nara_integration_examples.py" -ForegroundColor White
Write-Host ""
