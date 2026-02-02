#!/usr/bin/env pwsh
# Evident.info - Complete Dependency Installation Script
# Installs ALL required packages for Flask backend

Write-Host "`n?? Evident.info - Installing All Dependencies" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

Set-Location "C:\web-dev\github-repos\Evident.info"

# Step 1: Verify Python
Write-Host "`n[1/5] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ? $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ? Python not found!" -ForegroundColor Red
    exit 1
}

# Step 2: Remove old broken venv
Write-Host "`n[2/5] Cleaning old virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Remove-Item "venv" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ? Old venv removed" -ForegroundColor Green
}

# Step 3: Create fresh virtual environment
Write-Host "`n[3/5] Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv --without-pip

if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "  ? Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  ? Failed to create venv" -ForegroundColor Red
    exit 1
}

# Step 4: Install pip manually
Write-Host "`n[4/5] Installing pip..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "get-pip.py"
& venv\Scripts\python.exe get-pip.py --quiet
Remove-Item "get-pip.py"
Write-Host "  ? pip installed" -ForegroundColor Green

# Step 5: Install all dependencies
Write-Host "`n[5/5] Installing Flask and all dependencies..." -ForegroundColor Yellow

$packages = @(
    "Flask==3.0.0",
    "Flask-CORS==4.0.0",
    "Flask-SQLAlchemy==3.1.1",
    "Flask-Login==0.6.3",
    "Werkzeug==3.0.1",
    "python-dotenv==1.0.0",
    "Pillow",
    "PyPDF2==3.0.1",
    "SQLAlchemy==2.0.23",
    "requests==2.31.0"
)

$total = $packages.Count
$current = 0

foreach ($pkg in $packages) {
    $current++
    $pkgName = $pkg.Split("==")[0]
    Write-Host "  [$current/$total] Installing $pkgName..." -ForegroundColor Gray
    
    & venv\Scripts\python.exe -m pip install $pkg --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ? Installed" -ForegroundColor Green
    } else {
        Write-Host "    ? May have failed" -ForegroundColor Yellow
    }
}

Write-Host "`n=============================================" -ForegroundColor Cyan
Write-Host "? All Dependencies Installed!" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "=============================================" -ForegroundColor Cyan

# Verify installations
Write-Host "`n?? Verification:" -ForegroundColor Cyan
$testImports = & venv\Scripts\python.exe -c @"
import sys
packages = ['flask', 'flask_cors', 'flask_sqlalchemy', 'flask_login', 'werkzeug', 'sqlalchemy']
failed = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f'? {pkg}')
    except ImportError as e:
        failed.append(pkg)
        print(f'? {pkg}: {e}')
if failed:
    sys.exit(1)
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n? All critical packages working!" -ForegroundColor Green
} else {
    Write-Host "`n? Some packages may have issues" -ForegroundColor Yellow
}

Write-Host "`n?? Installed Packages:" -ForegroundColor Cyan
& venv\Scripts\python.exe -m pip list --format=columns

Write-Host "`n=============================================" -ForegroundColor Cyan
Write-Host "?? Ready to Start Flask!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "`nRun these commands:" -ForegroundColor Yellow
Write-Host "  1. Remove old database: Remove-Item Evident.db -Force -ErrorAction SilentlyContinue" -ForegroundColor White
Write-Host "  2. Start Flask: python app.py" -ForegroundColor White
Write-Host "`nFlask will run on: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
