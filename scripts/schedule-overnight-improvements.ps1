# Schedule Overnight Improvements
# Run this to schedule the improvement script to run every night at 2 AM

$TaskName = "Evident-Overnight-Improvements"
$ScriptPath = "C:\web-dev\github-repos\Evident.info\scripts\overnight-improvements.ps1"
$LogPath = "C:\web-dev\github-repos\Evident.info\overnight-improvements\scheduled-run.log"

Write-Host "?? Setting up Overnight Improvement Task" -ForegroundColor Cyan
Write-Host "=" * 60

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "??  Task already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create action
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`" > `"$LogPath`" 2>&1"

# Create trigger (runs at 2 AM daily)
$trigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Create principal (run with highest privileges)
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

# Register task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Evident repository overnight improvements - runs automated code quality, security, and optimization tasks"

Write-Host "`n? Task scheduled successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Task Details:" -ForegroundColor Cyan
Write-Host "  Name: $TaskName" -ForegroundColor Gray
Write-Host "  Schedule: Daily at 2:00 AM" -ForegroundColor Gray
Write-Host "  Script: $ScriptPath" -ForegroundColor Gray
Write-Host "  Log: $LogPath" -ForegroundColor Gray

Write-Host "`n?? Task Management:" -ForegroundColor Cyan
Write-Host "  View tasks:   Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "  Run now:      Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "  Disable:      Disable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "  Remove:       Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor Gray

Write-Host "`n?? Want to run it NOW to test?" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White

Write-Host "`n? The script will run automatically every night at 2 AM!" -ForegroundColor Green
Write-Host ""
