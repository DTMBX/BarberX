#!/usr/bin/env powershell
<#
.SYNOPSIS
    Evident Platform - Setup Script (Windows)
    
.DESCRIPTION
    Complete setup of the Evident authentication and dashboard system
    
.EXAMPLE
    .\setup.ps1
#>

param(
    [switch]$Force = $false,
    [switch]$CreateAdmin = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n" + "="*80 -ForegroundColor Cyan
Write-Host "🚀 EVIDENT PLATFORM - SETUP" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Cyan

# Check Python
Write-Host "`n[1/5] Checking Python installation..." -ForegroundColor Yellow

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ Python not found. Please install Python 3.9+ from python.org" -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version
Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green

# Install dependencies
Write-Host "`n[2/5] Installing dependencies..." -ForegroundColor Yellow

$deps = @(
    'flask-login',
    'flask-sqlalchemy',
    'email-validator',
    'python-dotenv'
)

foreach ($dep in $deps) {
    Write-Host "  Installing $dep..." -ForegroundColor Gray
    pip install $dep --quiet
}

Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Check Flask
Write-Host "`n[3/5] Checking Flask configuration..." -ForegroundColor Yellow

$envFile = ".env"
if ((Test-Path $envFile) -and -not $Force) {
    Write-Host "✅ .env file exists (use -Force to overwrite)" -ForegroundColor Green
} else {
    Write-Host "  Creating .env file..." -ForegroundColor Gray
    @"
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
DEBUG=True

# Database
SQLALCHEMY_DATABASE_URI=sqlite:///Evident.db

# Security (CHANGE THIS IN PRODUCTION)
SECRET_KEY=dev-secret-key-change-in-production

# Email Configuration (Optional)
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-password
"@ | Out-File -FilePath $envFile -Encoding UTF8
    Write-Host "✅ .env file created" -ForegroundColor Green
}

# Initialize database
Write-Host "`n[4/5] Initializing database..." -ForegroundColor Yellow

python -m flask init-db 2>&1 | Out-String | ForEach-Object { 
    if ($_ -match 'error|failed') { 
        Write-Host "⚠️  $_" -ForegroundColor Yellow
    } else { 
        Write-Host "  $_" -ForegroundColor Gray
    }
}

Write-Host "✅ Database initialized" -ForegroundColor Green

# Create admin user
Write-Host "`n[5/5] Admin user setup..." -ForegroundColor Yellow

if ($CreateAdmin) {
    Write-Host "  Starting admin creation wizard..." -ForegroundColor Gray
    python -m flask create-admin
    Write-Host "✅ Admin user created" -ForegroundColor Green
} else {
    Write-Host "  Run 'python -m flask create-admin' to create an admin account" -ForegroundColor Gray
    Write-Host "  Or run this script with -CreateAdmin flag" -ForegroundColor Gray
}

# Summary
Write-Host "`n" + "="*80 -ForegroundColor Cyan
Write-Host "✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Cyan

Write-Host "`n📍 Start Development Server:" -ForegroundColor Cyan
Write-Host "  python app.py" -ForegroundColor White
Write-Host "  or" -ForegroundColor Gray
Write-Host "  flask run" -ForegroundColor White

Write-Host "`n📍 Access Application:" -ForegroundColor Cyan
Write-Host "  🏠 Home:      http://localhost:5000/" -ForegroundColor White
Write-Host "  🔐 Login:     http://localhost:5000/auth/login" -ForegroundColor White
Write-Host "  📝 Register:  http://localhost:5000/auth/register" -ForegroundColor White
Write-Host "  📊 Dashboard: http://localhost:5000/dashboard" -ForegroundColor White
Write-Host "  ⚙️  Admin:     http://localhost:5000/admin/" -ForegroundColor White

Write-Host "`n📚 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Run 'python app.py' to start the server" -ForegroundColor White
Write-Host "  2. Visit http://localhost:5000/auth/register to create a user" -ForegroundColor White
Write-Host "  3. Or create admin with 'python -m flask create-admin'" -ForegroundColor White
Write-Host "  4. Check docs/AUTH_SYSTEM.md for full documentation" -ForegroundColor White

Write-Host "`n" + "="*80 -ForegroundColor Cyan
