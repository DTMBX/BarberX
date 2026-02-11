# Evident Celery Worker Startup
# Usage: .\scripts\start_worker.ps1
#
# Prerequisites:
#   - Redis running on localhost:6379
#   - Python 3.12 with celery installed

$ErrorActionPreference = "Stop"

# Check Redis
Write-Host "Checking Redis connectivity..."
$redisCheck = py -3.12 -c "import redis; r = redis.Redis(); print('OK' if r.ping() else 'FAIL')" 2>&1
if ($redisCheck -ne "OK") {
    Write-Host "ERROR: Redis is not running. Start Redis first." -ForegroundColor Red
    Write-Host "  Option A: Start-Process 'C:\tools\redis\redis-server.exe' -ArgumentList 'C:\tools\redis\redis.windows.conf'"
    Write-Host "  Option B: wsl -- redis-server --daemonize yes"
    exit 1
}
Write-Host "Redis: OK" -ForegroundColor Green

# Start worker
Write-Host "Starting Celery worker..."
Set-Location (Split-Path $PSScriptRoot)
py -3.12 -m celery -A celery_app worker --loglevel=info --pool=solo --concurrency=1
