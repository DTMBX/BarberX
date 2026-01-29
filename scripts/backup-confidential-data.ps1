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
