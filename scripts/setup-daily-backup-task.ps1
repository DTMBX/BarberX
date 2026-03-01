<#
.SYNOPSIS
    Setup Windows Task Scheduler for Automatic Daily Backups
.DESCRIPTION
    Creates a scheduled task to run auto-backup-daily.ps1 every day at 11:59 PM
    Only runs if there are uncommitted changes or new commits
    Automatically elevates to Administrator if needed
.EXAMPLE
    .\setup-daily-backup-task.ps1
.NOTES
    Will auto-elevate to Administrator if not already running as admin
#>

[CmdletBinding()]
param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$BackupTime = "23:59"  # 11:59 PM
)

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  This script requires Administrator privileges" -ForegroundColor Yellow
    Write-Host "🔄 Auto-elevating to Administrator..." -ForegroundColor Cyan
    Write-Host ""
    
    # Re-launch as administrator
    $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -RepoRoot `"$RepoRoot`" -BackupTime `"$BackupTime`""
    Start-Process PowerShell -Verb RunAs -ArgumentList $arguments -Wait
    exit
}

Write-Host "🔧 Setting up Daily Backup Task Scheduler" -ForegroundColor Cyan
Write-Host ""

# Paths
$scriptPath = Join-Path $PSScriptRoot "auto-backup-daily.ps1"
$taskName = "Tillerstead Daily Git Backup"
$taskDescription = "Automatically backup Tillerstead.com repository daily if changes detected"

# Verify script exists
if (-not (Test-Path $scriptPath)) {
    Write-Host "❌ Script not found: $scriptPath" -ForegroundColor Red
    exit 1
}

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "⚠️  Task already exists: $taskName" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (Y/N)"
    if ($overwrite -ne 'Y' -and $overwrite -ne 'y') {
        Write-Host "ℹ️  Task setup cancelled" -ForegroundColor Cyan
        exit 0
    }
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "✅ Removed existing task" -ForegroundColor Green
}

# Create the action
$action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" `
    -WorkingDirectory $RepoRoot

# Create the trigger (daily at specified time)
$trigger = New-ScheduledTaskTrigger -Daily -At $BackupTime

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -DontStopOnIdleEnd `
    -MultipleInstances IgnoreNew

# Create principal (run whether user is logged in or not)
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType S4U `
    -RunLevel Limited

# Register the task
Register-ScheduledTask `
    -TaskName $taskName `
    -Description $taskDescription `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Force | Out-Null

Write-Host ""
Write-Host "✅ Task Scheduler setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Task Details:" -ForegroundColor Cyan
Write-Host "  Name: $taskName" -ForegroundColor White
Write-Host "  Schedule: Daily at $BackupTime" -ForegroundColor White
Write-Host "  Script: $scriptPath" -ForegroundColor White
Write-Host "  User: $env:USERNAME" -ForegroundColor White
Write-Host ""
Write-Host "To verify the task:" -ForegroundColor Yellow
Write-Host "  1. Open Task Scheduler (taskschd.msc)" -ForegroundColor White
Write-Host "  2. Look for: $taskName" -ForegroundColor White
Write-Host ""
Write-Host "To test the backup manually:" -ForegroundColor Yellow
Write-Host "  PowerShell> .\scripts\auto-backup-daily.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To force a backup:" -ForegroundColor Yellow
Write-Host "  PowerShell> .\scripts\auto-backup-daily.ps1 -Force" -ForegroundColor White
Write-Host ""
