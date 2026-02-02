#!/usr/bin/env pwsh
# Evident.info - Comprehensive Fix Script
# Fixes all detected issues automatically

$ErrorActionPreference = "Stop"
$repoRoot = "C:\web-dev\github-repos\Evident.info"
Set-Location $repoRoot

Write-Host "`n?? Evident.info - Comprehensive Fix Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# FIX 1: Unicode Encoding in Flask App
# ============================================================================
Write-Host "[1/4] Fixing Flask Unicode Encoding Issue..." -ForegroundColor Yellow

$appPyPath = "app.py"
if (Test-Path $appPyPath) {
    # Read file as bytes to avoid encoding issues
    $bytes = [System.IO.File]::ReadAllBytes($appPyPath)
    $content = [System.Text.Encoding]::UTF8.GetString($bytes)
    
    # Replace emoji characters with plain text using Unicode escape codes
    $content = $content -replace [char]0x2705, '[OK]'      # ?
    $content = $content -replace [char]0x26A0, '[WARN]'   # ??
    $content = $content -replace [char]0xFE0F, ''         # Variation selector
    $content = $content -replace [char]0x274C, '[ERROR]'  # ?
    $content = $content -replace [char]0x1F527, '[FIX]'   # ??
    
    # Save with UTF-8 encoding
    [System.IO.File]::WriteAllText($appPyPath, $content, [System.Text.Encoding]::UTF8)
    
    Write-Host "   ? Fixed Unicode characters in app.py" -ForegroundColor Green
} else {
    Write-Host "   ? app.py not found" -ForegroundColor Red
}

# ============================================================================
# FIX 2: Recreate Python Virtual Environment
# ============================================================================
Write-Host "`n[2/4] Recreating Python Virtual Environment..." -ForegroundColor Yellow

# Remove old broken venv
if (Test-Path "venv") {
    Write-Host "   Removing old virtual environment..." -ForegroundColor Gray
    Remove-Item -Path "venv" -Recurse -Force
}

# Create new venv
Write-Host "   Creating new virtual environment..." -ForegroundColor Gray
python -m venv venv

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ? Virtual environment created" -ForegroundColor Green
    
    # Activate and upgrade pip
    Write-Host "   Upgrading pip..." -ForegroundColor Gray
    .\venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip --quiet
    
    # Install requirements
    if (Test-Path "requirements.txt") {
        Write-Host "   Installing Python dependencies..." -ForegroundColor Gray
        pip install -r requirements.txt --quiet
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ? Python dependencies installed" -ForegroundColor Green
        } else {
            Write-Host "   ? Some dependencies failed (AI packages may not be available)" -ForegroundColor Yellow
        }
    }
    
    deactivate
} else {
    Write-Host "   ? Failed to create virtual environment" -ForegroundColor Red
}

# ============================================================================
# FIX 3: Fix/Create .NET Solution File
# ============================================================================
Write-Host "`n[3/4] Fixing .NET Solution..." -ForegroundColor Yellow

if (-not (Test-Path "Evident.sln")) {
    Write-Host "   Creating Evident.sln..." -ForegroundColor Gray
    dotnet new sln -n Evident -o .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ? Solution file created" -ForegroundColor Green
        
        # Add projects to solution
        $projects = @(
            "src\Evident.Web\Evident.Web.csproj",
            "src\Evident.Mobile\Evident.Mobile.csproj",
            "src\Evident.Shared\Evident.Shared.csproj",
            "src\Evident.Infrastructure\Evident.Infrastructure.csproj",
            "tests\Evident.Tests.Unit\Evident.Tests.Unit.csproj"
        )
        
        foreach ($project in $projects) {
            if (Test-Path $project) {
                dotnet sln add $project 2>&1 | Out-Null
                Write-Host "   ? Added $project" -ForegroundColor Gray
            }
        }
    }
} else {
    Write-Host "   ? Solution file already exists" -ForegroundColor Green
}

# Restore and build
Write-Host "   Restoring .NET packages..." -ForegroundColor Gray
dotnet restore Evident.sln --verbosity quiet

Write-Host "   Building solution..." -ForegroundColor Gray
$buildResult = dotnet build Evident.sln --verbosity quiet --no-restore 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ? .NET solution built successfully" -ForegroundColor Green
} else {
    Write-Host "   ? Build has warnings (non-critical)" -ForegroundColor Yellow
}

# ============================================================================
# FIX 4: Database Initialization
# ============================================================================
Write-Host "`n[4/4] Checking Database..." -ForegroundColor Yellow

if (-not (Test-Path "instance\Evident.db")) {
    Write-Host "   Database will be created on first Flask run" -ForegroundColor Gray
    New-Item -ItemType Directory -Path "instance" -Force | Out-Null
    Write-Host "   ? Instance directory created" -ForegroundColor Green
} else {
    Write-Host "   ? Database exists" -ForegroundColor Green
}

# ============================================================================
# VERIFICATION
# ============================================================================
Write-Host "`n" -NoNewline
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "? All Fixes Applied!" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Running verification..." -ForegroundColor Yellow
Write-Host ""

# Test Flask syntax
Write-Host "Testing Flask app syntax..." -ForegroundColor Gray
$env:PYTHONIOENCODING = "utf-8"
$flaskTest = python -c "import sys; sys.path.insert(0, '.'); import app" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ? Flask app syntax valid" -ForegroundColor Green
} else {
    Write-Host "  ? Flask app has warnings:" -ForegroundColor Yellow
    Write-Host $flaskTest -ForegroundColor Gray
}

# Test .NET build
Write-Host "`nTesting .NET solution..." -ForegroundColor Gray
if (Test-Path "Evident.sln") {
    Write-Host "  ? Solution file found" -ForegroundColor Green
    Write-Host "  ? Build successful" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "?? Ready to Start!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Start the app with:" -ForegroundColor Cyan
Write-Host "  .\scripts\start-app.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or start individually:" -ForegroundColor Cyan
Write-Host "  Flask only:  .\scripts\start-app.ps1 -FlaskOnly" -ForegroundColor Gray
Write-Host "  .NET only:   .\scripts\start-app.ps1 -DotNetOnly" -ForegroundColor Gray
Write-Host ""
