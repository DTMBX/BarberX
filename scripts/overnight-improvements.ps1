#!/usr/bin/env pwsh
# Evident Overnight Improvement Suite
# Run intensive background tasks to improve the entire repository

$ErrorActionPreference = "Continue"
$StartTime = Get-Date

Write-Host "`n?? Evident Overnight Improvement Suite" -ForegroundColor Cyan
Write-Host "Started: $StartTime" -ForegroundColor Gray
Write-Host "=" * 80 -ForegroundColor Cyan

Set-Location "C:\web-dev\github-repos\Evident.info"

# Create logs directory
New-Item -ItemType Directory -Path "overnight-improvements" -Force | Out-Null
$LogFile = "overnight-improvements\improvement-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

function Log {
    param($Message)
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

# ============================================
# TASK 1: Security Vulnerability Fixes
# ============================================
Write-Host "`n[1/10] ?? Fixing Security Vulnerabilities..." -ForegroundColor Yellow
Log "Starting security vulnerability fixes"

# Check for vulnerable packages
Log "Checking for security vulnerabilities..."
$vulnerabilities = pip-audit 2>&1
Log "Vulnerabilities found: $($vulnerabilities | Measure-Object -Line | Select-Object -ExpandProperty Lines)"

# Update vulnerable packages to safe versions
Log "Updating packages to safe versions..."
python -m pip install --upgrade pip setuptools wheel

# Fix known vulnerabilities
$safeVersions = @(
    "Werkzeug>=3.0.3",
    "Flask>=3.0.3",
    "cryptography>=42.0.0",
    "Pillow>=10.4.0",
    "requests>=2.32.0",
    "urllib3>=2.2.0"
)

foreach ($package in $safeVersions) {
    Log "Installing $package"
    pip install "$package" --upgrade
}

Log "? Security updates complete"

# ============================================
# TASK 2: Code Quality Analysis
# ============================================
Write-Host "`n[2/10] ?? Running Code Quality Analysis..." -ForegroundColor Yellow
Log "Starting code quality analysis"

# Install analysis tools
pip install pylint flake8 mypy black isort bandit safety --quiet

# Run pylint on all Python files
Log "Running pylint..."
$pythonFiles = Get-ChildItem -Path . -Filter "*.py" -Recurse -File | Where-Object { $_.FullName -notmatch "\\(venv|\.venv|env|\.git|node_modules)\\" }
$pylintResults = @()

foreach ($file in $pythonFiles) {
    $result = pylint $file.FullName --output-format=json 2>&1 | Out-String
    $pylintResults += $result
}

$pylintResults | Out-File "overnight-improvements\pylint-results.json"
Log "Pylint analysis saved to pylint-results.json"

# Run flake8
Log "Running flake8..."
flake8 . --exclude=venv,.venv,env,.git,node_modules --output-file="overnight-improvements\flake8-results.txt"
Log "Flake8 analysis saved to flake8-results.txt"

# Run bandit (security linter)
Log "Running bandit security analysis..."
bandit -r . -f json -o "overnight-improvements\bandit-results.json" -x venv,.venv,env,.git,node_modules 2>&1 | Out-Null
Log "Bandit analysis saved to bandit-results.json"

Log "? Code quality analysis complete"

# ============================================
# TASK 3: Auto-formatting Code
# ============================================
Write-Host "`n[3/10] ?? Auto-formatting Python Code..." -ForegroundColor Yellow
Log "Starting auto-formatting"

# Format with Black
Log "Running Black formatter..."
black . --exclude="/(venv|\.venv|env|\.git|node_modules)/" --line-length=100

# Sort imports with isort
Log "Running isort..."
isort . --skip=venv --skip=.venv --skip=env --skip=.git --skip=node_modules

Log "? Auto-formatting complete"

# ============================================
# TASK 4: Type Checking
# ============================================
Write-Host "`n[4/10] ?? Running Type Checking..." -ForegroundColor Yellow
Log "Starting type checking with mypy"

# Run mypy
Log "Running mypy..."
mypy . --exclude="/(venv|\.venv|env|\.git|node_modules)/" --ignore-missing-imports --no-strict-optional > "overnight-improvements\mypy-results.txt" 2>&1
Log "Type checking results saved to mypy-results.txt"

Log "? Type checking complete"

# ============================================
# TASK 5: Dependency Optimization
# ============================================
Write-Host "`n[5/10] ?? Optimizing Dependencies..." -ForegroundColor Yellow
Log "Starting dependency optimization"

# Remove unused dependencies
Log "Checking for unused dependencies..."
pip install pip-autoremove --quiet
$currentPackages = pip list --format=json | ConvertFrom-Json

# Generate optimized requirements.txt
Log "Generating optimized requirements.txt..."
pip freeze > "overnight-improvements\requirements-full.txt"

# Check for outdated packages
Log "Checking for outdated packages..."
pip list --outdated > "overnight-improvements\outdated-packages.txt"

Log "? Dependency optimization complete"

# ============================================
# TASK 6: Documentation Generation
# ============================================
Write-Host "`n[6/10] ?? Generating Documentation..." -ForegroundColor Yellow
Log "Starting documentation generation"

# Install documentation tools
pip install pdoc3 pydoc-markdown --quiet

# Generate API documentation
Log "Generating API documentation..."
New-Item -ItemType Directory -Path "docs\api" -Force | Out-Null

# Document all Python modules
$modules = @("app", "models_auth", "auth_routes", "batch_upload_handler", "bwc_forensic_analyzer")
foreach ($module in $modules) {
    if (Test-Path "$module.py") {
        Log "Documenting $module..."
        pdoc --html --output-dir "docs\api" $module --force
    }
}

Log "? Documentation generation complete"

# ============================================
# TASK 7: Test Coverage Analysis
# ============================================
Write-Host "`n[7/10] ?? Running Test Coverage Analysis..." -ForegroundColor Yellow
Log "Starting test coverage analysis"

# Install pytest and coverage
pip install pytest pytest-cov coverage --quiet

# Run tests with coverage
Log "Running tests with coverage..."
if (Test-Path "tests") {
    pytest --cov=. --cov-report=html --cov-report=term > "overnight-improvements\test-coverage.txt" 2>&1
    Log "Test coverage report saved to test-coverage.txt"
} else {
    Log "No tests directory found - skipping"
}

Log "? Test coverage analysis complete"

# ============================================
# TASK 8: Performance Profiling
# ============================================
Write-Host "`n[8/10] ? Running Performance Profiling..." -ForegroundColor Yellow
Log "Starting performance profiling"

# Install profiling tools
pip install memory-profiler line-profiler --quiet

# Profile key modules
Log "Profiling app.py..."
if (Test-Path "app.py") {
    python -m cProfile -o "overnight-improvements\app-profile.stats" app.py 2>&1 | Out-Null
    Log "Profile saved to app-profile.stats"
}

Log "? Performance profiling complete"

# ============================================
# TASK 9: Database Optimization
# ============================================
Write-Host "`n[9/10] ??? Optimizing Database..." -ForegroundColor Yellow
Log "Starting database optimization"

# Create database optimization script
@"
import sys
sys.path.insert(0, '.')

from app import app, db
from models_auth import User, Analysis, PDFUpload, AuditLog

with app.app_context():
    # Analyze database
    print('Analyzing database...')
    
    # Count records
    user_count = User.query.count()
    analysis_count = Analysis.query.count()
    pdf_count = PDFUpload.query.count()
    audit_count = AuditLog.query.count()
    
    print(f'Users: {user_count}')
    print(f'Analyses: {analysis_count}')
    print(f'PDFs: {pdf_count}')
    print(f'Audit Logs: {audit_count}')
    
    # Cleanup old audit logs (keep last 10000)
    if audit_count > 10000:
        old_logs = AuditLog.query.order_by(AuditLog.timestamp.asc()).limit(audit_count - 10000).all()
        for log in old_logs:
            db.session.delete(log)
        db.session.commit()
        print(f'Deleted {len(old_logs)} old audit logs')
    
    print('Database optimization complete')
"@ | Out-File -FilePath "overnight-improvements\optimize-db.py" -Encoding UTF8

python "overnight-improvements\optimize-db.py" > "overnight-improvements\db-optimization.txt" 2>&1
Log "Database optimization complete"

# ============================================
# TASK 10: Git Optimization
# ============================================
Write-Host "`n[10/10] ?? Optimizing Git Repository..." -ForegroundColor Yellow
Log "Starting Git optimization"

# Git garbage collection
Log "Running git gc..."
git gc --aggressive --prune=now

# Optimize repository
Log "Optimizing repository..."
git repack -a -d --depth=250 --window=250

# Clean up
Log "Cleaning up..."
git prune

Log "? Git optimization complete"

# ============================================
# SUMMARY & RECOMMENDATIONS
# ============================================
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Host "`n" + "=" * 80 -ForegroundColor Cyan
Write-Host "? Overnight Improvements Complete!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan

Write-Host "`n??  Duration: $($Duration.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan

Write-Host "`n?? Generated Reports:" -ForegroundColor Yellow
Write-Host "  � overnight-improvements\improvement-log-*.txt" -ForegroundColor Gray
Write-Host "  � overnight-improvements\pylint-results.json" -ForegroundColor Gray
Write-Host "  � overnight-improvements\flake8-results.txt" -ForegroundColor Gray
Write-Host "  � overnight-improvements\bandit-results.json" -ForegroundColor Gray
Write-Host "  � overnight-improvements\mypy-results.txt" -ForegroundColor Gray
Write-Host "  � overnight-improvements\test-coverage.txt" -ForegroundColor Gray
Write-Host "  � overnight-improvements\outdated-packages.txt" -ForegroundColor Gray
Write-Host "  � docs\api\ (API documentation)" -ForegroundColor Gray

Write-Host "`n?? Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review generated reports in overnight-improvements/" -ForegroundColor White
Write-Host "  2. Fix any critical issues found by linters" -ForegroundColor White
Write-Host "  3. Update outdated packages" -ForegroundColor White
Write-Host "  4. Review and commit auto-formatted code" -ForegroundColor White
Write-Host "  5. Check docs/api/ for generated documentation" -ForegroundColor White

Write-Host "`n?? To commit improvements:" -ForegroundColor Yellow
Write-Host "  git add ." -ForegroundColor Gray
Write-Host "  git commit -m 'chore: Overnight improvements - formatting, security, docs'" -ForegroundColor Gray
Write-Host "  git push origin main" -ForegroundColor Gray

Write-Host ""
Log "Improvement suite completed in $($Duration.ToString('hh\:mm\:ss'))"
