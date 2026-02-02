#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Migrate Evident to a fresh GitHub repository with proper git-crypt encryption
    
.DESCRIPTION
    This script creates a clean repository with git-crypt initialized BEFORE
    any commits, ensuring sensitive files are encrypted from the start.
    
.PARAMETER NewRepoUrl
    The URL of the new GitHub repository (e.g., https://github.com/DTMBX/Evident-Clean)
    
.PARAMETER BackupPath
    Path where backup of current repo will be saved (default: parent directory)
    
.EXAMPLE
    .\migrate-to-fresh-repo.ps1 -NewRepoUrl "https://github.com/DTMBX/Evident-Clean"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$NewRepoUrl,
    
    [Parameter(Mandatory=$false)]
    [string]$BackupPath = "C:\web-dev\github-repos\Evident.info-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
)

$ErrorActionPreference = "Stop"
$CurrentRepo = "C:\web-dev\github-repos\Evident.info"
$NewRepo = "C:\web-dev\github-repos\Evident-Fresh"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Evident Fresh Repository Migration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Backup current repository
Write-Host "[1/10] Backing up current repository..." -ForegroundColor Yellow
if (Test-Path $BackupPath) {
    Write-Host "⚠️  Backup path already exists: $BackupPath" -ForegroundColor Red
    $continue = Read-Host "Delete existing backup and continue? (yes/no)"
    if ($continue -ne "yes") {
        Write-Host "Migration cancelled." -ForegroundColor Red
        exit 1
    }
    Remove-Item -Path $BackupPath -Recurse -Force
}

Copy-Item -Path $CurrentRepo -Destination $BackupPath -Recurse -Force
Write-Host "✅ Backed up to: $BackupPath" -ForegroundColor Green

# Step 2: Create new repository directory
Write-Host "`n[2/10] Creating new repository directory..." -ForegroundColor Yellow
if (Test-Path $NewRepo) {
    Write-Host "⚠️  New repo path already exists: $NewRepo" -ForegroundColor Red
    Remove-Item -Path $NewRepo -Recurse -Force
}
New-Item -ItemType Directory -Path $NewRepo | Out-Null
Set-Location $NewRepo
Write-Host "✅ Created: $NewRepo" -ForegroundColor Green

# Step 3: Initialize Git
Write-Host "`n[3/10] Initializing Git repository..." -ForegroundColor Yellow
git init
git config user.name "Devon Tyler"
git config user.email "devontyler396@gmail.com"
Write-Host "✅ Git initialized" -ForegroundColor Green

# Step 4: Initialize git-crypt FIRST (before any commits)
Write-Host "`n[4/10] Initializing git-crypt (BEFORE any commits)..." -ForegroundColor Yellow
git-crypt init
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ git-crypt initialization failed. Is git-crypt installed?" -ForegroundColor Red
    Write-Host "Install: winget install git-crypt" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ git-crypt initialized" -ForegroundColor Green

# Step 5: Export encryption key
Write-Host "`n[5/10] Exporting git-crypt key..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "secure" -Force | Out-Null
git-crypt export-key "secure/Evident-git-crypt-FRESH.key"
Write-Host "✅ Encryption key exported to: secure/Evident-git-crypt-FRESH.key" -ForegroundColor Green
Write-Host "⚠️  IMPORTANT: Save this key file securely - you'll need it to decrypt files!" -ForegroundColor Magenta

# Step 6: Configure .gitattributes for encryption
Write-Host "`n[6/10] Configuring encryption patterns..." -ForegroundColor Yellow
$gitattributes = @"
# Git-crypt encryption patterns
# These files will be encrypted in the repository

# Environment and secrets
.env* filter=git-crypt diff=git-crypt
secrets.enc filter=git-crypt diff=git-crypt
*.key filter=git-crypt diff=git-crypt
*.pem filter=git-crypt diff=git-crypt
*.p12 filter=git-crypt diff=git-crypt
*.pfx filter=git-crypt diff=git-crypt

# Secure directory (contains encryption key backup)
secure/** filter=git-crypt diff=git-crypt

# Mobile app signing and configuration
**/signing.properties filter=git-crypt diff=git-crypt
**/appsettings.json filter=git-crypt diff=git-crypt
**/appsettings.*.json filter=git-crypt diff=git-crypt

# Body-worn camera proprietary code
barber-cam/** filter=git-crypt diff=git-crypt

# Core business logic and AI
app.py filter=git-crypt diff=git-crypt
bwc_web_app.py filter=git-crypt diff=git-crypt
ai_*.py filter=git-crypt diff=git-crypt
*_routes.py filter=git-crypt diff=git-crypt
chatgpt_*.py filter=git-crypt diff=git-crypt
citation_*.py filter=git-crypt diff=git-crypt

# Database and business data
*.db filter=git-crypt diff=git-crypt
*.sqlite filter=git-crypt diff=git-crypt
cases.json filter=git-crypt diff=git-crypt

# Business documentation
ADMIN-*.txt filter=git-crypt diff=git-crypt
COPYRIGHT-*.txt filter=git-crypt diff=git-crypt
*-GUIDE.md filter=git-crypt diff=git-crypt

# Exclusions (these should NOT be encrypted)
*.md !filter !diff
README.md !filter !diff
LICENSE !filter !diff
.gitignore !filter !diff
.gitattributes !filter !diff
"@

$gitattributes | Out-File -FilePath ".gitattributes" -Encoding utf8 -NoNewline
Write-Host "✅ Encryption patterns configured" -ForegroundColor Green

# Step 7: Copy files from current repo (excluding .git)
Write-Host "`n[7/10] Copying files from current repository..." -ForegroundColor Yellow
$excludeItems = @('.git', '.venv', '__pycache__', 'node_modules', '_site', 'obj', 'bin', '*.pyc')
Get-ChildItem -Path $CurrentRepo -Exclude $excludeItems | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $NewRepo -Recurse -Force
}
Write-Host "✅ Files copied" -ForegroundColor Green

# Step 8: Generate NEW secrets
Write-Host "`n[8/10] Generating NEW secure secrets..." -ForegroundColor Yellow
$newSecretKey = python -c "import secrets; print(secrets.token_urlsafe(32))"
$newAdminPassword = python -c "import secrets, string; chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-='; print(''.join(secrets.choice(chars) for _ in range(32)))"

$newSecrets = @"
# Encrypted Secrets for Evident
# This file is encrypted by git-crypt
SECRET_KEY=$newSecretKey
FLASK_ENV=production
ADMIN_EMAIL=admin@Evident.info
ADMIN_PASSWORD=$newAdminPassword
"@

$newSecrets | Out-File -FilePath "secrets.enc" -Encoding utf8 -NoNewline
Write-Host "✅ New secrets generated and encrypted" -ForegroundColor Green

# Step 9: Commit everything (files will be encrypted automatically)
Write-Host "`n[9/10] Committing files (sensitive data will be encrypted)..." -ForegroundColor Yellow
git add .
git commit -m "🔒 Initial commit with git-crypt encryption enabled

- All sensitive files encrypted from the start
- Mobile app data protected
- Business logic and AI code encrypted
- Body-worn camera code encrypted
- New secure secrets generated
"
Write-Host "✅ Files committed with encryption" -ForegroundColor Green

# Step 10: Add remote and prepare for push
Write-Host "`n[10/10] Configuring remote repository..." -ForegroundColor Yellow
git remote add origin $NewRepoUrl
git branch -M main
Write-Host "✅ Remote configured: $NewRepoUrl" -ForegroundColor Green

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 New repository: $NewRepo" -ForegroundColor White
Write-Host "💾 Backup location: $BackupPath" -ForegroundColor White
Write-Host "🔑 Encryption key: $NewRepo\secure\Evident-git-crypt-FRESH.key" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Review the new repository files:" -ForegroundColor White
Write-Host "   cd $NewRepo" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Verify encryption is working:" -ForegroundColor White
Write-Host "   git-crypt status" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Push to GitHub:" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. IMPORTANT: Securely store the encryption key!" -ForegroundColor Magenta
Write-Host "   $NewRepo\secure\Evident-git-crypt-FRESH.key" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Team members can unlock with:" -ForegroundColor White
Write-Host "   git-crypt unlock /path/to/Evident-git-crypt-FRESH.key" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  WARNING: The old repo at DTMBX/Evident still has exposed secrets!" -ForegroundColor Red
Write-Host "   Consider making it private or deleting it after pushing the fresh repo." -ForegroundColor Yellow
Write-Host ""
