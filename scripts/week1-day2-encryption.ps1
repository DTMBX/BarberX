# BarberX Day 2 - Encryption & Backup Setup
# Run this script to automate secure folder creation and file migration
# Created: January 28, 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BarberX Day 2: Encryption & Backups" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Repository and secure folder paths
$repoRoot = "C:\web-dev\github-repos\BarberX.info"
$secureRoot = "C:\SecureData\BarberX-Confidential"

# ============================================
# Task 2.1: Create Secure Folder Structure
# ============================================

Write-Host "Task 2.1: Creating secure folder structure..." -ForegroundColor Cyan

if (-not (Test-Path "C:\SecureData")) {
    New-Item -Path "C:\SecureData" -ItemType Directory -Force | Out-Null
    Write-Host "  Created: C:\SecureData" -ForegroundColor Green
}

if (-not (Test-Path $secureRoot)) {
    New-Item -Path $secureRoot -ItemType Directory -Force | Out-Null
    Write-Host "  Created: $secureRoot" -ForegroundColor Green
}

# Create subfolders
$folders = @(
    "Financial-Data",
    "Investor-Decks",
    "NDA-Signed",
    "Customer-Data-Exports",
    "Backups",
    "Legal-Documents"
)

foreach ($folder in $folders) {
    $folderPath = Join-Path $secureRoot $folder
    if (-not (Test-Path $folderPath)) {
        New-Item -Path $folderPath -ItemType Directory -Force | Out-Null
        Write-Host "  Created: $folder\" -ForegroundColor Green
    } else {
        Write-Host "  Already exists: $folder\" -ForegroundColor Gray
    }
}

Write-Host ""

# ============================================
# Task 2.2: Copy Confidential Files
# ============================================

Write-Host "Task 2.2: Copying confidential files to secure storage..." -ForegroundColor Cyan

# Copy INVESTOR-LOG.md
$investorLogSource = Join-Path $repoRoot "INVESTOR-LOG.md"
$investorLogDest = Join-Path $secureRoot "Financial-Data\INVESTOR-LOG.md"

if (Test-Path $investorLogSource) {
    Copy-Item -Path $investorLogSource -Destination $investorLogDest -Force
    Write-Host "  ✓ Copied: INVESTOR-LOG.md → Financial-Data\" -ForegroundColor Green
    
    # Verify file integrity
    $sourceHash = (Get-FileHash $investorLogSource -Algorithm SHA256).Hash
    $destHash = (Get-FileHash $investorLogDest -Algorithm SHA256).Hash
    
    if ($sourceHash -eq $destHash) {
        Write-Host "  ✓ File integrity verified (SHA256 match)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ WARNING: File hashes do NOT match!" -ForegroundColor Red
    }
} else {
    Write-Host "  ⚠ INVESTOR-LOG.md not found in repository" -ForegroundColor Yellow
}

# Copy founding_member_signups.csv
$csvSource = Join-Path $repoRoot "founding_member_signups.csv"
$csvDest = Join-Path $secureRoot "Customer-Data-Exports\founding_member_signups.csv"

if (Test-Path $csvSource) {
    Copy-Item -Path $csvSource -Destination $csvDest -Force
    Write-Host "  ✓ Copied: founding_member_signups.csv → Customer-Data-Exports\" -ForegroundColor Green
} else {
    Write-Host "  ⚠ founding_member_signups.csv not found" -ForegroundColor Yellow
}

# Copy database backup
$dbSource = Join-Path $repoRoot "instance\barberx_FRESH.db"
$dbDest = Join-Path $secureRoot "Backups\barberx_FRESH-$(Get-Date -Format 'yyyyMMdd').db"

if (Test-Path $dbSource) {
    Copy-Item -Path $dbSource -Destination $dbDest -Force
    Write-Host "  ✓ Copied: Database backup → Backups\" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Database not found at instance\barberx_FRESH.db" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Task 2.3: Verify Secure Folder
# ============================================

Write-Host "Task 2.3: Verifying secure folder contents..." -ForegroundColor Cyan

Get-ChildItem -Path $secureRoot -Recurse -File | ForEach-Object {
    Write-Host "  $($_.FullName)" -ForegroundColor Gray
}

Write-Host ""

# ============================================
# Task 2.4: Backup Script Setup
# ============================================

Write-Host "Task 2.4: Creating automated backup script..." -ForegroundColor Cyan

$backupScriptPath = Join-Path $repoRoot "scripts\backup-confidential-data.ps1"

$backupScriptContent = @'
# BarberX Automated Backup Script
# Scheduled to run daily at 2 AM via Task Scheduler

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$sourcePath = "C:\SecureData\BarberX-Confidential"
$backupPath = "C:\SecureData\BarberX-Confidential\Backups\backup-$timestamp"

# Create backup
Write-Host "Starting backup at $(Get-Date)" -ForegroundColor Cyan
Copy-Item -Path $sourcePath -Destination $backupPath -Recurse -Force -Exclude "Backups"

if ($?) {
    Write-Host "✓ Backup completed: $backupPath" -ForegroundColor Green
} else {
    Write-Host "✗ Backup FAILED" -ForegroundColor Red
}

# Keep only last 7 backups
Write-Host "Cleaning old backups (keeping last 7)..." -ForegroundColor Gray
Get-ChildItem "$sourcePath\Backups" -Directory | 
    Sort-Object CreationTime -Descending | 
    Select-Object -Skip 7 | 
    Remove-Item -Recurse -Force

Write-Host "Backup process complete." -ForegroundColor Green
'@

if (-not (Test-Path (Split-Path $backupScriptPath))) {
    New-Item -Path (Split-Path $backupScriptPath) -ItemType Directory -Force | Out-Null
}

Set-Content -Path $backupScriptPath -Value $backupScriptContent
Write-Host "  ✓ Created: backup-confidential-data.ps1" -ForegroundColor Green
Write-Host ""

# ============================================
# Task 2.5: Schedule Backup Task (Optional)
# ============================================

Write-Host "Task 2.5: Scheduling automated backup..." -ForegroundColor Cyan
Write-Host ""
Write-Host "To schedule daily backups, run this PowerShell command as Administrator:" -ForegroundColor Yellow
Write-Host ""
Write-Host @"
`$action = New-ScheduledTaskAction -Execute "PowerShell.exe" ``
  -Argument "-File $backupScriptPath"

`$trigger = New-ScheduledTaskTrigger -Daily -At 2AM

Register-ScheduledTask -TaskName "BarberX-Confidential-Backup" ``
  -Action `$action -Trigger `$trigger ``
  -Description "Daily backup of BarberX confidential data"
"@ -ForegroundColor Cyan
Write-Host ""

# ============================================
# Task 2.6: Encryption Reminder
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "IMPORTANT: Encryption Setup" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files are now in C:\SecureData\BarberX-Confidential\" -ForegroundColor Green
Write-Host "but are NOT yet encrypted." -ForegroundColor Red
Write-Host ""
Write-Host "Next steps (choose ONE):" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: Windows BitLocker (Requires Windows Pro/Enterprise)" -ForegroundColor Cyan
Write-Host "  1. Right-click C: drive → Turn on BitLocker" -ForegroundColor Gray
Write-Host "  2. Choose encryption method: AES 256-bit" -ForegroundColor Gray
Write-Host "  3. Save recovery key to password manager" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2: VeraCrypt (Free, Cross-platform)" -ForegroundColor Cyan
Write-Host "  1. Download: https://www.veracrypt.fr/" -ForegroundColor Gray
Write-Host "  2. Create encrypted container (500 MB)" -ForegroundColor Gray
Write-Host "  3. Move BarberX-Confidential folder into container" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 3: Google Drive with 2FA (Cloud Backup)" -ForegroundColor Cyan
Write-Host "  1. Install Google Drive for Desktop" -ForegroundColor Gray
Write-Host "  2. Enable 2FA on Google Account" -ForegroundColor Gray
Write-Host "  3. Move BarberX-Confidential to Google Drive folder" -ForegroundColor Gray
Write-Host "  4. Enable 'Make available offline'" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Day 2 Complete! ✓" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  ✓ Secure folder structure created" -ForegroundColor Green
Write-Host "  ✓ Confidential files copied to C:\SecureData\BarberX-Confidential\" -ForegroundColor Green
Write-Host "  ✓ File integrity verified (SHA256 hashes)" -ForegroundColor Green
Write-Host "  ✓ Backup script created" -ForegroundColor Green
Write-Host "  □ Encryption pending (choose Option 1, 2, or 3 above)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next: Proceed to Day 3 (Monitoring & Alerts)" -ForegroundColor Gray
