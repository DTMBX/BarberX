#!/usr/bin/env pwsh
# Render Deployment Diagnostic Tool

Write-Host "`n?? Evident Render Deployment Diagnostics" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Set-Location "C:\web-dev\github-repos\Evident.info"

Write-Host "`n[1/6] Checking Configuration Files..." -ForegroundColor Yellow

# Check runtime.txt
if (Test-Path "runtime.txt") {
    $runtime = Get-Content "runtime.txt" -Raw
    Write-Host "  ? runtime.txt exists: $($runtime.Trim())" -ForegroundColor Green
} else {
    Write-Host "  ? runtime.txt MISSING!" -ForegroundColor Red
}

# Check .python-version
if (Test-Path ".python-version") {
    $pyversion = Get-Content ".python-version" -Raw
    Write-Host "  ? .python-version exists: $($pyversion.Trim())" -ForegroundColor Green
} else {
    Write-Host "  ? .python-version missing (optional)" -ForegroundColor Yellow
}

# Check requirements.txt
if (Test-Path "requirements.txt") {
    $reqLines = (Get-Content "requirements.txt").Count
    Write-Host "  ? requirements.txt exists ($reqLines packages)" -ForegroundColor Green
    
    # Check for problematic packages
    $requirements = Get-Content "requirements.txt"
    
    if ($requirements -match "Flask==") {
        Write-Host "    ? Flask version pinned" -ForegroundColor Green
    } else {
        Write-Host "    ? Flask version not pinned" -ForegroundColor Yellow
    }
    
    if ($requirements -match "gunicorn==") {
        Write-Host "    ? gunicorn present" -ForegroundColor Green
    } else {
        Write-Host "    ? gunicorn MISSING!" -ForegroundColor Red
    }
    
    if ($requirements -match "psycopg2-binary") {
        Write-Host "    ? PostgreSQL driver present" -ForegroundColor Green
    } else {
        Write-Host "    ? PostgreSQL driver missing" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ? requirements.txt MISSING!" -ForegroundColor Red
}

# Check build.sh
if (Test-Path "build.sh") {
    Write-Host "  ? build.sh exists" -ForegroundColor Green
    $buildContent = Get-Content "build.sh" -Raw
    if ($buildContent -match "pip install") {
        Write-Host "    ? Contains pip install command" -ForegroundColor Green
    }
} else {
    Write-Host "  ? build.sh missing (Render will use default)" -ForegroundColor Yellow
}

# Check Procfile
if (Test-Path "Procfile") {
    Write-Host "  ? Procfile exists" -ForegroundColor Green
} else {
    Write-Host "  ? Procfile missing (will use render.yaml)" -ForegroundColor Yellow
}

# Check render.yaml
if (Test-Path "render.yaml") {
    Write-Host "  ? render.yaml exists" -ForegroundColor Green
    $renderYaml = Get-Content "render.yaml" -Raw
    if ($renderYaml -match "startCommand") {
        Write-Host "    ? Has startCommand" -ForegroundColor Green
    }
    if ($renderYaml -match "buildCommand") {
        Write-Host "    ? Has buildCommand" -ForegroundColor Green
    }
} else {
    Write-Host "  ? render.yaml missing" -ForegroundColor Yellow
}

Write-Host "`n[2/6] Testing Local Build..." -ForegroundColor Yellow

# Test if requirements can install locally
Write-Host "  Testing pip install..." -ForegroundColor Gray
$installTest = python -m pip install -r requirements.txt --dry-run 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ? requirements.txt is valid" -ForegroundColor Green
} else {
    Write-Host "  ? requirements.txt has issues" -ForegroundColor Red
    Write-Host "    Error: $installTest" -ForegroundColor Red
}

Write-Host "`n[3/6] Testing App Import..." -ForegroundColor Yellow

$appTest = python -c @"
import sys
sys.path.insert(0, '.')
try:
    from app import app
    print('? App imports successfully')
except ImportError as e:
    print(f'? Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'? Error: {e}')
    sys.exit(1)
"@ 2>&1

Write-Host "  $appTest" -ForegroundColor $(if($LASTEXITCODE -eq 0){"Green"}else{"Red"})

Write-Host "`n[4/6] Checking Database Configuration..." -ForegroundColor Yellow

$dbTest = python -c @"
import sys
sys.path.insert(0, '.')
try:
    from app import app
    print(f'Database URI type: {app.config.get("SQLALCHEMY_DATABASE_URI", "NOT SET")[:20]}...')
    print('? Database configuration present')
except Exception as e:
    print(f'? Database config error: {e}')
"@ 2>&1

Write-Host "  $dbTest" -ForegroundColor Green

Write-Host "`n[5/6] Git Status..." -ForegroundColor Yellow

$gitStatus = git status --short
if ($gitStatus) {
    Write-Host "  ? Uncommitted changes:" -ForegroundColor Yellow
    Write-Host $gitStatus -ForegroundColor Gray
} else {
    Write-Host "  ? All changes committed" -ForegroundColor Green
}

$gitRemote = git remote get-url origin
Write-Host "  Remote: $gitRemote" -ForegroundColor Gray

$gitBranch = git branch --show-current
Write-Host "  Branch: $gitBranch" -ForegroundColor Gray

Write-Host "`n[6/6] Render Deployment Checklist..." -ForegroundColor Yellow

$checklist = @(
    @{Name="Python version specified"; Check=(Test-Path "runtime.txt")},
    @{Name="Dependencies listed"; Check=(Test-Path "requirements.txt")},
    @{Name="Gunicorn in requirements"; Check=((Get-Content "requirements.txt") -match "gunicorn")},
    @{Name="Flask in requirements"; Check=((Get-Content "requirements.txt") -match "Flask")},
    @{Name="PostgreSQL driver present"; Check=((Get-Content "requirements.txt") -match "psycopg2")},
    @{Name="Start command configured"; Check=(Test-Path "render.yaml")},
    @{Name="All changes committed"; Check=(-not (git status --short))}
)

foreach ($item in $checklist) {
    if ($item.Check) {
        Write-Host "  ? $($item.Name)" -ForegroundColor Green
    } else {
        Write-Host "  ? $($item.Name)" -ForegroundColor Red
    }
}

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "?? COMMON RENDER BUILD ERRORS:" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host @"

1. Python Version Error:
   Symptom: "Python 3.13" in logs but expecting 3.11
   Fix: Ensure runtime.txt contains exactly: 3.11.9

2. Pillow Build Error:
   Symptom: "KeyError: '__version__'" or build fails
   Fix: Update Pillow to 10.4.0 in requirements.txt

3. SQLAlchemy Error:
   Symptom: "AssertionError" or "TypingOnly" error
   Fix: Use SQLAlchemy==2.0.23 with Python 3.11

4. Gunicorn Not Found:
   Symptom: "gunicorn: command not found"
   Fix: Add gunicorn==21.2.0 to requirements.txt

5. Database Connection Error:
   Symptom: "could not connect to database"
   Fix: Create PostgreSQL database in Render dashboard

"@ -ForegroundColor Gray

Write-Host "`n?? NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Go to Render dashboard: https://dashboard.render.com" -ForegroundColor White
Write-Host "2. Click on your service" -ForegroundColor White
Write-Host "3. Go to 'Logs' tab" -ForegroundColor White
Write-Host "4. Copy the LAST 30-50 LINES of the error" -ForegroundColor White
Write-Host "5. Paste them here so I can fix it" -ForegroundColor White

Write-Host "`n?? OR - Try these quick fixes:" -ForegroundColor Cyan
Write-Host ".\scripts\FIX-RENDER-BUILD.ps1  # Run automatic fixes" -ForegroundColor White

Write-Host ""
