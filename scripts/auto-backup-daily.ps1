<#
.SYNOPSIS
    Automatic Daily Git Backup - Creates dated backup of repository
.DESCRIPTION
    Checks for git changes and creates a dated backup folder at root level.
    Copies the entire repository (excluding .git, node_modules, _site, etc.)
    Only runs if there are uncommitted changes or new commits since last backup.
.PARAMETER RepoRoot
    Path to the repository root. Defaults to script's parent directory.
.PARAMETER Force
    Force backup even if no changes detected
.EXAMPLE
    .\auto-backup-daily.ps1
    .\auto-backup-daily.ps1 -Force
.NOTES
    Tillerstead.com - Automated Daily Backup System
    Schedule this script to run daily via Task Scheduler
#>

[CmdletBinding()]
param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [switch]$Force
)

# Color output functions
function Write-Success { param([string]$msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Info { param([string]$msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Warning { param([string]$msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error { param([string]$msg) Write-Host "❌ $msg" -ForegroundColor Red }

# Ensure we're in the repo root
Set-Location $RepoRoot
Write-Info "Repository: $RepoRoot"

# Check if this is a git repository
if (-not (Test-Path ".git")) {
    Write-Error "Not a git repository. Cannot create backup."
    exit 1
}

# Industry standard: backups outside repository, in parent directory
$backupRootDir = Join-Path (Split-Path -Parent $RepoRoot) "tillerstead-backups"
$today = Get-Date -Format "yyyy-MM-dd"
$backupFolder = $today
$backupPath = Join-Path $backupRootDir $backupFolder

# Create backup root directory if it doesn't exist
if (-not (Test-Path $backupRootDir)) {
    New-Item -Path $backupRootDir -ItemType Directory -Force | Out-Null
    Write-Info "Created backup directory: $backupRootDir"
}

Write-Info "Backup location: $backupPath"

# Check if backup already exists for today
if (Test-Path $backupPath) {
    Write-Warning "Backup already exists for today: $backupPath"
    if (-not $Force) {
        Write-Info "Use -Force to overwrite existing backup"
        exit 0
    }
    Write-Warning "Force flag detected - removing existing backup"
    Remove-Item $backupPath -Recurse -Force
}

# Check for changes (uncommitted or unpushed)
$hasChanges = $false
$statusOutput = git status --porcelain 2>&1

if ($statusOutput) {
    Write-Info "Uncommitted changes detected:"
    $statusOutput | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
    $hasChanges = $true
}

# Check for unpushed commits
$unpushedCommits = git log '@{u}..' --oneline 2>&1
if ($LASTEXITCODE -eq 0 -and $unpushedCommits) {
    Write-Info "Unpushed commits detected:"
    $unpushedCommits | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
    $hasChanges = $true
}

# Check if we should proceed
if (-not $hasChanges -and -not $Force) {
    Write-Success "No changes detected - backup not needed"
    exit 0
}

Write-Info "Creating backup..."

# Create backup directory
New-Item -Path $backupPath -ItemType Directory -Force | Out-Null

# Directories and files to EXCLUDE from backup
$excludePatterns = @(
    '.git',
    'node_modules',
    '_site',
    '.venv',
    '__pycache__',
    '*.pyc',
    '.pytest_cache',
    'test-results',
    'playwright-report',
    '.DS_Store',
    'Thumbs.db',
    '*.log',
    '.env',
    '.env.local'
)

# Build robocopy exclude list
$excludeDirs = @()
$excludeFiles = @()

foreach ($pattern in $excludePatterns) {
    if ($pattern.StartsWith('*.')) {
        # File extension pattern
        $excludeFiles += $pattern
    } elseif ($pattern.Contains('*')) {
        # Wildcard pattern - add as file
        $excludeFiles += $pattern
    } else {
        # Directory name
        $excludeDirs += $pattern
    }
}

Write-Info "Copying files (this may take a moment)..."

# Use robocopy for efficient copying (Windows native)
$robocopyArgs = @(
    $RepoRoot,
    $backupPath,
    '/E',           # Copy subdirectories including empty
    '/XD',          # Exclude directories
    $excludeDirs,
    '/XF',          # Exclude files
    $excludeFiles,
    '/NFL',         # No file list
    '/NDL',         # No directory list
    '/NP',          # No progress
    '/NS',          # No size
    '/NC',          # No class
    '/BYTES',       # Show sizes in bytes
    '/R:1',         # Retry once
    '/W:1'          # Wait 1 second between retries
)

$robocopyResult = robocopy @robocopyArgs 2>&1

# Robocopy exit codes: 0-7 are success, 8+ are errors
$robocopyExitCode = $LASTEXITCODE
if ($robocopyExitCode -ge 8) {
    Write-Error "Backup failed with robocopy error code: $robocopyExitCode"
    Write-Host $robocopyResult -ForegroundColor Red
    exit 1
}

# Create backup metadata file
$metadata = @{
    "backup_date" = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    "source_repo" = $RepoRoot
    "git_branch" = (git branch --show-current 2>&1)
    "git_commit" = (git rev-parse HEAD 2>&1)
    "git_status" = ($statusOutput | Out-String).Trim()
    "backup_reason" = if ($Force) { "Manual backup (forced)" } else { "Automatic backup - changes detected" }
    "created_by" = "auto-backup-daily.ps1"
} | ConvertTo-Json -Depth 3

$metadataPath = Join-Path $backupPath "_BACKUP_INFO.json"
$metadata | Out-File -FilePath $metadataPath -Encoding UTF8

# Calculate backup size
$backupSize = (Get-ChildItem -Path $backupPath -Recurse -File | Measure-Object -Property Length -Sum).Sum
$backupSizeMB = [math]::Round($backupSize / 1MB, 2)

Write-Success "Backup created successfully!"
Write-Info "Location: $backupPath"
Write-Info "Size: $backupSizeMB MB"
Write-Info "Files: $(( Get-ChildItem -Path $backupPath -Recurse -File | Measure-Object ).Count)"

# Clean up old backups (keep last 7 days)
Write-Info "Checking for old backups..."
if (Test-Path $backupRootDir) {
    $oldBackups = Get-ChildItem -Path $backupRootDir -Directory | 
        Where-Object { $_.Name -match '^\d{4}-\d{2}-\d{2}$' } |
        Where-Object { $_.Name -ne $backupFolder } |
        Sort-Object Name -Descending |
        Select-Object -Skip 7

    if ($oldBackups) {
        Write-Warning "Removing old backups (keeping last 7 days):"
        foreach ($old in $oldBackups) {
            Write-Host "  Removing: $($old.Name)" -ForegroundColor DarkGray
            Remove-Item $old.FullName -Recurse -Force
        }
        Write-Success "Cleaned up $($oldBackups.Count) old backup(s)"
    } else {
        Write-Info "No old backups to remove"
    }
}

# Summary
Write-Host ""
Write-Success "=== Backup Complete ==="
Write-Host "Backup location: $backupPath" -ForegroundColor Cyan
Write-Host "Total size: $backupSizeMB MB" -ForegroundColor Cyan
Write-Host "Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""
Write-Info "All backups stored in: $backupRootDir"
Write-Host ""

exit 0
