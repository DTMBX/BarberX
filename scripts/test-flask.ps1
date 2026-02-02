#!/usr/bin/env pwsh
# Direct Flask Test - See actual errors

Write-Host "`n?? Flask Direct Test" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

Set-Location "C:\web-dev\github-repos\Evident.info"

# Step 1: Install Flask dependencies
Write-Host "`n[1/3] Installing Flask dependencies..." -ForegroundColor Yellow

# Use ensurepip to get pip working
Write-Host "  Ensuring pip is installed..." -ForegroundColor Gray
.\venv\Scripts\python.exe -m ensurepip --upgrade 2>&1 | Out-Null

# Upgrade pip
Write-Host "  Upgrading pip..." -ForegroundColor Gray
.\venv\Scripts\python.exe -m pip install --upgrade pip --quiet 2>&1 | Out-Null

# Install Flask and dependencies
Write-Host "  Installing packages..." -ForegroundColor Gray
$packages = @(
    "flask",
    "flask-cors",
    "flask-sqlalchemy",
    "flask-login",
    "werkzeug"
)

foreach ($pkg in $packages) {
    Write-Host "    - $pkg" -ForegroundColor Gray
    .\venv\Scripts\python.exe -m pip install $pkg --quiet
}

Write-Host "  ? Packages installed" -ForegroundColor Green

# Step 2: Test imports
Write-Host "`n[2/3] Testing imports..." -ForegroundColor Yellow

$testScript = @"
import sys
sys.path.insert(0, '.')

try:
    import flask
    print('? Flask')
except Exception as e:
    print(f'? Flask: {e}')

try:
    import flask_cors
    print('? Flask-CORS')
except Exception as e:
    print(f'? Flask-CORS: {e}')

try:
    import flask_sqlalchemy
    print('? Flask-SQLAlchemy')
except Exception as e:
    print(f'? Flask-SQLAlchemy: {e}')

try:
    import flask_login
    print('? Flask-Login')
except Exception as e:
    print(f'? Flask-Login: {e}')

try:
    import werkzeug
    print('? Werkzeug')
except Exception as e:
    print(f'? Werkzeug: {e}')
"@

$env:PYTHONIOENCODING = "utf-8"
$importResults = .\venv\Scripts\python.exe -c $testScript 2>&1
Write-Host $importResults

# Step 3: Run Flask
Write-Host "`n[3/3] Starting Flask server..." -ForegroundColor Yellow
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Run Flask in foreground
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
$env:PYTHONIOENCODING = "utf-8"

.\venv\Scripts\python.exe app.py
