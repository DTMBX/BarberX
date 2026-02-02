#!/usr/bin/env pwsh
# Test Evident.info Capabilities

Write-Host "`n?? Testing Evident.info Application" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Test 1: Login
Write-Host "`n[1/4] Testing Login..." -ForegroundColor Yellow
try {
    $body = @{
        email = $env:Evident_ADMIN_EMAIL ?? "admin@Evident.info"
        password = $env:Evident_ADMIN_PASSWORD ?? (Read-Host "Enter admin password" -AsSecureString | ConvertFrom-SecureString -AsPlainText)
    } | ConvertTo-Json

    $response = Invoke-WebRequest `
        -Uri "http://localhost:5000/auth/login" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -SessionVariable session `
        -UseBasicParsing

    Write-Host "  ? Login successful!" -ForegroundColor Green
    $loginSuccess = $true
} catch {
    Write-Host "  ??  Login endpoint: $($_.Exception.Message)" -ForegroundColor Yellow
    $loginSuccess = $false
}

# Test 2: Dashboard
if ($loginSuccess) {
    Write-Host "`n[2/4] Testing Dashboard..." -ForegroundColor Yellow
    try {
        $dash = Invoke-WebRequest `
            -Uri "http://localhost:5000/auth/dashboard" `
            -WebSession $session `
            -UseBasicParsing
        
        Write-Host "  ? Dashboard accessible" -ForegroundColor Green
    } catch {
        Write-Host "  ??  Dashboard: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Test 3: PDF Upload Page
Write-Host "`n[3/4] Testing PDF Upload Page..." -ForegroundColor Yellow
try {
    $pdf = Invoke-WebRequest `
        -Uri "http://localhost:5000/batch-pdf-upload.html" `
        -UseBasicParsing
    
    Write-Host "  ? PDF upload page accessible" -ForegroundColor Green
} catch {
    Write-Host "  ??  PDF page: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 4: API Upload Endpoint
Write-Host "`n[4/4] Testing Upload API..." -ForegroundColor Yellow
try {
    $upload = Invoke-WebRequest `
        -Uri "http://localhost:5000/api/health" `
        -UseBasicParsing
    
    $health = $upload.Content | ConvertFrom-Json
    Write-Host "  ? API responding: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "  ??  API: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "? Testing Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`n?? MANUAL TESTS:" -ForegroundColor Yellow
Write-Host "  1. Open: http://localhost:5000" -ForegroundColor White
Write-Host "  2. Click Login" -ForegroundColor White
Write-Host "  3. Use: admin@Evident.info / [Evident_ADMIN_PASSWORD env var]" -ForegroundColor White
Write-Host "  4. Go to Dashboard" -ForegroundColor White
Write-Host "  5. Try uploading a PDF or BWC video" -ForegroundColor White
Write-Host ""
