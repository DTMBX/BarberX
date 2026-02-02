# Evident Week 1 Security Setup - Master Script
# Run this script to automate Day 1-7 security tasks
# Created: January 28, 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Evident Week 1 Security Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to repository root
$repoRoot = "C:\web-dev\github-repos\Evident.info"
Set-Location $repoRoot

Write-Host "Repository: $repoRoot" -ForegroundColor Green
Write-Host ""

# ============================================
# DAY 1: GIT AUDIT & GITIGNORE
# ============================================

Write-Host "[DAY 1] Starting Git Audit & .gitignore Setup..." -ForegroundColor Yellow
Write-Host ""

# Task 1.1: Audit git history for sensitive data
Write-Host "Task 1.1: Auditing git history for sensitive files..." -ForegroundColor Cyan

$auditDate = Get-Date -Format "yyyyMMdd"
$auditFile = "git-audit-$auditDate.txt"

Write-Host "  Searching for INVESTOR* files..." -ForegroundColor Gray
git log --all --full-history --source --pretty=format:"%H %s" -- "*INVESTOR*" | Out-File -FilePath $auditFile -Append

Write-Host "  Searching for financial keywords..." -ForegroundColor Gray
git log --all --full-history -S "margin" -S "MRR" -S "ARR" -S "profit" --oneline | Out-File -FilePath $auditFile -Append

Write-Host "  Searching for dollar amounts..." -ForegroundColor Gray
git log --all --full-history -G "\`$\d+,\d+" --oneline | Out-File -FilePath $auditFile -Append

Write-Host "  Audit saved to: $auditFile" -ForegroundColor Green
Write-Host ""

# Task 1.2: Check if INVESTOR-LOG.md was ever committed
Write-Host "Task 1.2: Checking if INVESTOR-LOG.md was committed..." -ForegroundColor Cyan

$investorLogHistory = git log --all --full-history -- "INVESTOR-LOG.md" 2>&1

if ($investorLogHistory -match "fatal|error") {
    Write-Host "  ✓ INVESTOR-LOG.md was NEVER committed (GOOD)" -ForegroundColor Green
} else {
    Write-Host "  ⚠ WARNING: INVESTOR-LOG.md was committed to git!" -ForegroundColor Red
    Write-Host "  See $auditFile for details. Consider using git filter-branch to remove." -ForegroundColor Yellow
}
Write-Host ""

# Task 1.3: Create/update .gitignore
Write-Host "Task 1.3: Creating/updating .gitignore..." -ForegroundColor Cyan

$gitignoreContent = @"
# Evident Confidential Financial Data
INVESTOR-LOG.md
*INVESTOR*.md
*CONFIDENTIAL*.md
*financial*.xlsx
*revenue*.csv
*margins*.csv

# Environment variables (may contain API keys)
.env
.env.local
.env.production
.env.staging

# Database files (contain user data)
*.db
*.sqlite
*.sqlite3
instance/*.db

# Logs (may contain sensitive debug info)
logs/
*.log

# Python cache
__pycache__/
*.py[cod]
*`$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
.venv/
ENV/
env/

# IDEs
.vscode/settings.json
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Backup files
*.bak
*.backup
*.old

# Temporary files
tmp/
temp/
*.tmp

# CSV data files (may contain PII)
founding_member_signups.csv
user_exports/
customer_data/

# Investor materials
investor-deck-*.pptx
investor-deck-*.pdf
data-room/
nda-signed/

# Stripe/Payment test data
stripe-test-data/
payment-exports/

# Security audit files
git-audit-*.txt
security-audit-*.md

# Week 1 secure data folder (if local)
SecureData/
Evident-Confidential/
"@

$gitignorePath = ".gitignore"

if (Test-Path $gitignorePath) {
    Write-Host "  .gitignore exists. Appending Evident rules..." -ForegroundColor Gray
    Add-Content -Path $gitignorePath -Value "`n# Evident Security Rules (Added $(Get-Date -Format 'yyyy-MM-dd'))`n$gitignoreContent"
} else {
    Write-Host "  Creating new .gitignore..." -ForegroundColor Gray
    Set-Content -Path $gitignorePath -Value $gitignoreContent
}

Write-Host "  ✓ .gitignore updated" -ForegroundColor Green
Write-Host ""

# Task 1.4: Verify .gitignore is working
Write-Host "Task 1.4: Testing .gitignore..." -ForegroundColor Cyan

New-Item -Path "TEST-INVESTOR-CONFIDENTIAL.md" -ItemType File -Force | Out-Null
$gitStatus = git status --porcelain

if ($gitStatus -match "TEST-INVESTOR-CONFIDENTIAL.md") {
    Write-Host "  ⚠ WARNING: .gitignore not working correctly!" -ForegroundColor Red
} else {
    Write-Host "  ✓ .gitignore working correctly (test file ignored)" -ForegroundColor Green
}

Remove-Item "TEST-INVESTOR-CONFIDENTIAL.md" -Force
Write-Host ""

# Task 1.5: Commit .gitignore
Write-Host "Task 1.5: Committing .gitignore..." -ForegroundColor Cyan

git add .gitignore
git commit -m "SECURITY: Add .gitignore rules for confidential financial data

- Exclude INVESTOR-LOG.md and all *INVESTOR*.md files
- Exclude database files and user data CSVs
- Exclude environment variables and API keys
- Prevent accidental disclosure of margins, revenue, costs"

Write-Host "  ✓ .gitignore committed" -ForegroundColor Green
Write-Host ""

Write-Host "[DAY 1] Complete! ✓" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review $auditFile for any sensitive data in git history" -ForegroundColor Gray
Write-Host "  2. If found, consider using git filter-branch to remove (BACKUP FIRST)" -ForegroundColor Gray
Write-Host "  3. Proceed to Day 2: Encryption & Backups (run week1-day2-encryption.ps1)" -ForegroundColor Gray
Write-Host ""

# ============================================
# DAY 2-3: Placeholder reminders
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Remaining Week 1 Tasks (Manual)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[DAY 2] Encryption & Backups:" -ForegroundColor Yellow
Write-Host "  □ Choose encryption method (BitLocker/VeraCrypt/Google Drive)" -ForegroundColor Gray
Write-Host "  □ Create C:\SecureData\Evident-Confidential folder structure" -ForegroundColor Gray
Write-Host "  □ Copy INVESTOR-LOG.md to encrypted folder" -ForegroundColor Gray
Write-Host "  □ Set up automated backups (Task Scheduler or Google Drive sync)" -ForegroundColor Gray
Write-Host "  □ Delete INVESTOR-LOG.md from repository after verifying secure copy" -ForegroundColor Gray
Write-Host ""

Write-Host "[DAY 3] Monitoring & Alerts:" -ForegroundColor Yellow
Write-Host "  □ Set up Google Alerts (brand monitoring, leak detection)" -ForegroundColor Gray
Write-Host "  □ Enable GitHub Dependabot and secret scanning" -ForegroundColor Gray
Write-Host "  □ Create OpenAI usage monitoring script" -ForegroundColor Gray
Write-Host ""

Write-Host "[DAY 4-5] Password Manager & 2FA:" -ForegroundColor Yellow
Write-Host "  □ Sign up for Bitwarden password manager" -ForegroundColor Gray
Write-Host "  □ Enable 2FA on Bitwarden" -ForegroundColor Gray
Write-Host "  □ Migrate all service passwords to Bitwarden" -ForegroundColor Gray
Write-Host "  □ Enable 2FA on: GitHub, Render, Proton, Stripe, OpenAI" -ForegroundColor Gray
Write-Host ""

Write-Host "[DAY 6-7] Security Audit:" -ForegroundColor Yellow
Write-Host "  □ Complete security audit checklist (30-DAY-IMPLEMENTATION-ROADMAP.md)" -ForegroundColor Gray
Write-Host "  □ Create .env.example template" -ForegroundColor Gray
Write-Host "  □ Calculate security score (target: 93%+)" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Day 1 Automation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
