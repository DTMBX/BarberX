#!/usr/bin/env pwsh
# Evident.info - Quick Start Script
# Starts both Flask and .NET backends with one command

param(
    [switch]$FlaskOnly,
    [switch]$DotNetOnly,
    [switch]$OpenBrowser = $true
)

$repoRoot = "C:\web-dev\github-repos\Evident.info"
Set-Location $repoRoot

Write-Host "?? Starting Evident.info Application" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if apps are already running
$port5000 = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
$port5001 = Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue

if ($port5000 -and -not $DotNetOnly) {
    Write-Host "??  Flask already running on port 5000" -ForegroundColor Yellow
    $FlaskOnly = $true
}

if ($port5001 -and -not $FlaskOnly) {
    Write-Host "??  .NET API already running on port 5001" -ForegroundColor Yellow
    $DotNetOnly = $true
}

$jobs = @()

# Start Flask Backend
if (-not $DotNetOnly) {
    Write-Host "Starting Flask Backend (Port 5000)..." -ForegroundColor Green
    
    $flaskJob = Start-Job -Name "Flask-Backend" -ScriptBlock {
        Set-Location "C:\web-dev\github-repos\Evident.info"
        if (Test-Path "venv\Scripts\Activate.ps1") {
            .\venv\Scripts\Activate.ps1
        }
        python app.py
    }
    
    $jobs += $flaskJob
    Write-Host "  ? Flask job started (ID: $($flaskJob.Id))" -ForegroundColor Gray
}

# Start .NET Backend
if (-not $FlaskOnly) {
    Write-Host "Starting .NET Web API (Port 5001)..." -ForegroundColor Green
    
    if (Test-Path "src\Evident.Web") {
        $dotnetJob = Start-Job -Name "DotNet-API" -ScriptBlock {
            Set-Location "C:\web-dev\github-repos\Evident.info\src\Evident.Web"
            dotnet run
        }
        
        $jobs += $dotnetJob
        Write-Host "  ? .NET API job started (ID: $($dotnetJob.Id))" -ForegroundColor Gray
    } else {
        Write-Host "  ??  .NET Web API project not found" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "? Services Starting..." -ForegroundColor Green
Write-Host ""

# Wait for services to start
Write-Host "Waiting for services to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Show URLs
Write-Host "?? Application URLs:" -ForegroundColor Cyan
if (-not $DotNetOnly) {
    Write-Host "  Flask (BWC Analysis):  http://localhost:5000" -ForegroundColor White
}
if (-not $FlaskOnly) {
    Write-Host "  .NET Web API:          http://localhost:5001" -ForegroundColor White
    Write-Host "  Swagger UI:            http://localhost:5001/swagger" -ForegroundColor White
}
Write-Host ""

# Open browser
if ($OpenBrowser -and -not $DotNetOnly) {
    Write-Host "Opening browser..." -ForegroundColor Gray
    Start-Process "http://localhost:5000"
}

Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Monitor jobs
try {
    while ($true) {
        Start-Sleep -Seconds 2
        
        foreach ($job in $jobs) {
            if ($job.State -eq "Failed") {
                Write-Host ""
                Write-Host "? Job '$($job.Name)' failed!" -ForegroundColor Red
                Receive-Job -Job $job | Write-Host -ForegroundColor Red
            }
        }
    }
} finally {
    Write-Host ""
    Write-Host "Stopping services..." -ForegroundColor Yellow
    
    foreach ($job in $jobs) {
        Stop-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job -ErrorAction SilentlyContinue
        Write-Host "  ? Stopped $($job.Name)" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "? All services stopped" -ForegroundColor Green
}
