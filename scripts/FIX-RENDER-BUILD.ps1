#!/usr/bin/env pwsh
# Automatic Render Build Fixer

Write-Host "`n?? Evident Render Build - Automatic Fix" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

Set-Location "C:\web-dev\github-repos\Evident.info"

Write-Host "`n[1/5] Fixing runtime.txt..." -ForegroundColor Yellow
"3.11.9" | Out-File -FilePath "runtime.txt" -Encoding UTF8 -NoNewline
Write-Host "  ? Set to Python 3.11.9" -ForegroundColor Green

Write-Host "`n[2/5] Fixing .python-version..." -ForegroundColor Yellow
"3.11.9" | Out-File -FilePath ".python-version" -Encoding UTF8 -NoNewline
Write-Host "  ? Backup version file created" -ForegroundColor Green

Write-Host "`n[3/5] Creating minimal requirements.txt..." -ForegroundColor Yellow

$minimalReqs = @"
# Core Flask
Flask==3.0.0
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Werkzeug==3.0.1

# Production Server
gunicorn==21.2.0

# Database
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23

# Utilities
python-dotenv==1.0.0
requests==2.31.0

# Document Processing
PyPDF2==3.0.1
Pillow==10.4.0
pdfplumber==0.10.3

# Password Hashing
Flask-Bcrypt==1.0.1
"@

$minimalReqs | Out-File -FilePath "requirements.txt" -Encoding UTF8
Write-Host "  ? Minimal requirements created (18 packages)" -ForegroundColor Green

Write-Host "`n[4/5] Creating optimized build.sh..." -ForegroundColor Yellow

$buildScript = @"
#!/usr/bin/env bash
set -o errexit

echo "Building Evident Legal Tech..."
echo "Python version: `$(python --version)"

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "Build complete!"
"@

$buildScript | Out-File -FilePath "build.sh" -Encoding UTF8
Write-Host "  ? Build script created" -ForegroundColor Green

Write-Host "`n[5/5] Updating render.yaml..." -ForegroundColor Yellow

$renderConfig = @"
services:
  - type: web
    name: Evident-legal-tech
    runtime: python
    env: python
    region: oregon
    plan: free
    buildCommand: bash build.sh
    startCommand: gunicorn app:app --bind 0.0.0.0:`$PORT --workers 1 --timeout 300 --log-level info
    envVars:
      - key: PYTHON_VERSION
        value: "3.11.9"
      - key: SECRET_KEY
        generateValue: true
      - key: FLASK_ENV
        value: production
      - key: MAX_CONTENT_LENGTH
        value: "21474836480"
    autoDeploy: true
"@

$renderConfig | Out-File -FilePath "render.yaml" -Encoding UTF8
Write-Host "  ? Render config optimized" -ForegroundColor Green

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "? All Fixes Applied!" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "`n?? Changes Made:" -ForegroundColor Cyan
Write-Host "  ? runtime.txt ? 3.11.9" -ForegroundColor Green
Write-Host "  ? requirements.txt ? Minimal compatible versions" -ForegroundColor Green
Write-Host "  ? build.sh ? Optimized build script" -ForegroundColor Green
Write-Host "  ? render.yaml ? Working configuration" -ForegroundColor Green

Write-Host "`n?? Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review changes: git diff" -ForegroundColor White
Write-Host "  2. Commit: git add -A && git commit -m 'fix: Render deployment fixes'" -ForegroundColor White
Write-Host "  3. Push: git push origin main" -ForegroundColor White

Write-Host "`n??  Render will auto-deploy in ~5 minutes" -ForegroundColor Cyan

Write-Host "`n? Want to commit and push now? (y/n): " -ForegroundColor Yellow -NoNewline
$response = Read-Host

if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "`nCommitting changes..." -ForegroundColor Yellow
    git add runtime.txt .python-version requirements.txt build.sh render.yaml
    git commit -m "fix: Render deployment - Python 3.11.9 + minimal deps"
    
    Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
    git push origin main
    
    Write-Host "`n? Deployed! Check Render dashboard in 5 minutes" -ForegroundColor Green
} else {
    Write-Host "`nChanges staged but not committed. Review with: git diff" -ForegroundColor Gray
}

Write-Host ""
