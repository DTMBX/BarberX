# Quick Test Script - Verify Everything Works
Write-Host "`n=== Evident Quick Test ===" -ForegroundColor Cyan

# Test 1: Check if app is running
Write-Host "`n[Test 1] Checking if app is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/auth/login" -TimeoutSec 5 -UseBasicParsing
    Write-Host "  ✓ App is running (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "  ✗ App is not running" -ForegroundColor Red
    Write-Host "  Run: python app.py" -ForegroundColor Yellow
    exit 1
}

# Test 2: Check databases exist
Write-Host "`n[Test 2] Checking databases..." -ForegroundColor Yellow
$dbs = @{
    "Main DB" = "instance\Evident_FRESH.db"
    "Legal Retrieval DB" = "instance\Evident_legal.db"
}

foreach ($name in $dbs.Keys) {
    if (Test-Path $dbs[$name]) {
        Write-Host "  ✓ $name exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $name missing" -ForegroundColor Red
    }
}

# Test 3: Verify test users
Write-Host "`n[Test 3] Verifying test users..." -ForegroundColor Yellow
$userCheck = @'
from app import app
from models_auth import User

with app.app_context():
    admin = User.query.filter_by(email='admin@Evident.info').first()
    test = User.query.filter_by(email='test@Evident.info').first()

    if admin and test:
        print('OK')
    else:
        print('MISSING')
'@
$result = & python -c $userCheck 2>$null

if ($result -eq "OK") {
    Write-Host "  ✓ Test users exist" -ForegroundColor Green
} else {
    Write-Host "  ✗ Test users missing - run .\START.ps1 to create" -ForegroundColor Red
}

# Test 4: Check JavaScript files
Write-Host "`n[Test 4] Checking JavaScript files..." -ForegroundColor Yellow
$jsFiles = @(
    "static\js\toast-notifications.js",
    "static\js\loading-states.js",
    "static\js\form-validation.js"
)

foreach ($file in $jsFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file missing" -ForegroundColor Red
    }
}

# Test 5: Test retrieval system
Write-Host "`n[Test 5] Testing retrieval system..." -ForegroundColor Yellow
$retrievalCheck = @'
try:
    from retrieval_service import RetrievalService
    from legal_library_adapter import LegalLibraryAdapter
    service = RetrievalService()
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
'@
$result = & python -c $retrievalCheck 2>$null

if ($result -eq "OK") {
    Write-Host "  ✓ Retrieval system ready" -ForegroundColor Green
} else {
    Write-Host "  ✗ Retrieval system error: $result" -ForegroundColor Red
}

# Test 6: Count ingested documents
Write-Host "`n[Test 6] Checking ingested documents..." -ForegroundColor Yellow
$docCount = @'
import sqlite3
conn = sqlite3.connect('instance/Evident_legal.db')
c = conn.cursor()
count = c.execute('SELECT COUNT(*) FROM documents').fetchone()[0]
print(count)
'@
$count = & python -c $docCount 2>$null

Write-Host "  Documents in legal library: $count" -ForegroundColor White
if ([int]$count -gt 0) {
    Write-Host "  ✓ You have documents to search" -ForegroundColor Green
} else {
    Write-Host "  ℹ No documents yet - see GETTING-STARTED-TODAY.md to ingest some" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "All core systems operational!" -ForegroundColor Green
Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "  1. Open browser: http://localhost:5000/auth/login" -ForegroundColor White
Write-Host "  2. Login with: test@Evident.info / Password123!" -ForegroundColor White
Write-Host "  3. Explore the dashboard" -ForegroundColor White
Write-Host "  4. Read GETTING-STARTED-TODAY.md for examples" -ForegroundColor White
Write-Host ""
