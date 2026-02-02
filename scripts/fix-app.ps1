#!/usr/bin/env pwsh
# Evident.info - Application Health Check & Fix Script
# Diagnoses and fixes common front-end and back-end issues

param(
    [switch]$SkipPython,
    [switch]$SkipDotNet,
    [switch]$SkipFrontend,
    [switch]$AutoFix = $true,
    [switch]$RunAfterFix
)

$ErrorActionPreference = "Continue"
$repoRoot = "C:\web-dev\github-repos\Evident.info"

# Color coding
function Write-Section($text) { Write-Host "`n$text" -ForegroundColor Cyan -BackgroundColor DarkBlue }
function Write-Success($text) { Write-Host "? $text" -ForegroundColor Green }
function Write-Error($text) { Write-Host "? $text" -ForegroundColor Red }
function Write-Warning($text) { Write-Host "??  $text" -ForegroundColor Yellow }
function Write-Info($text) { Write-Host "??  $text" -ForegroundColor Gray }
function Write-Fix($text) { Write-Host "?? $text" -ForegroundColor Magenta }

Set-Location $repoRoot

Write-Section "?? Evident.info Health Check & Fix"
Write-Host "Repository: $repoRoot" -ForegroundColor Gray
Write-Host ""

$issues = @()
$fixes = @()

# ============================================================================
# 1. PYTHON FLASK BACKEND CHECK
# ============================================================================
if (-not $SkipPython) {
    Write-Section "?? Python Flask Backend Check"
    
    # Check Python installation
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    } else {
        Write-Error "Python not found"
        $issues += "Python not installed"
        $fixes += "Install Python 3.9+ from https://python.org"
    }
    
    # Check Flask app exists
    if (Test-Path "app.py") {
        Write-Success "Flask app.py found"
        
        # Check for virtual environment
        if (Test-Path "venv\Scripts\activate.ps1") {
            Write-Success "Virtual environment found"
        } else {
            Write-Warning "Virtual environment not found"
            if ($AutoFix) {
                Write-Fix "Creating Python virtual environment..."
                python -m venv venv
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Virtual environment created"
                }
            } else {
                $issues += "No Python virtual environment"
                $fixes += "Run: python -m venv venv"
            }
        }
        
        # Check requirements.txt
        if (Test-Path "requirements.txt") {
            Write-Success "requirements.txt found"
            
            if ($AutoFix) {
                Write-Fix "Installing Python dependencies..."
                .\venv\Scripts\Activate.ps1
                pip install -r requirements.txt --quiet
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Python dependencies installed"
                } else {
                    Write-Error "Failed to install Python dependencies"
                    $issues += "Python dependency installation failed"
                }
                deactivate
            }
        } else {
            Write-Warning "requirements.txt not found"
            $issues += "Missing requirements.txt"
        }
        
        # Check Flask imports
        Write-Info "Checking Flask app syntax..."
        $flaskCheck = python -c "import sys; sys.path.insert(0, '.'); import app" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Flask app syntax valid"
        } else {
            Write-Error "Flask app has syntax errors:"
            Write-Host $flaskCheck -ForegroundColor Red
            $issues += "Flask app syntax errors"
        }
        
    } else {
        Write-Error "app.py not found"
        $issues += "Missing Flask app.py"
    }
}

# ============================================================================
# 2. .NET BACKEND CHECK
# ============================================================================
if (-not $SkipDotNet) {
    Write-Section "?? .NET Backend Check"
    
    # Check .NET SDK
    $dotnetCmd = Get-Command dotnet -ErrorAction SilentlyContinue
    if ($dotnetCmd) {
        $dotnetVersion = dotnet --version
        Write-Success ".NET SDK found: $dotnetVersion"
    } else {
        Write-Error ".NET SDK not found"
        $issues += ".NET SDK not installed"
        $fixes += "Install .NET 9.0 SDK from https://dotnet.microsoft.com"
    }
    
    # Check solution file
    if (Test-Path "Evident.sln") {
        Write-Success "Solution file found: Evident.sln"
        
        if ($AutoFix) {
            Write-Fix "Restoring .NET packages..."
            dotnet restore Evident.sln --verbosity quiet
            if ($LASTEXITCODE -eq 0) {
                Write-Success ".NET packages restored"
            } else {
                Write-Error "Failed to restore .NET packages"
                $issues += ".NET package restore failed"
            }
            
            Write-Fix "Building .NET solution..."
            $buildOutput = dotnet build Evident.sln --verbosity quiet --no-restore 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success ".NET solution built successfully"
            } else {
                Write-Error "Build failed:"
                Write-Host $buildOutput -ForegroundColor Red
                $issues += ".NET build errors"
            }
        }
        
    } else {
        Write-Warning "Evident.sln not found"
        $issues += "Missing .NET solution file"
    }
    
    # Check Web API project
    if (Test-Path "src\Evident.Web\Evident.Web.csproj") {
        Write-Success "Web API project found"
    } else {
        Write-Warning "Web API project not found"
        $issues += "Missing Evident.Web project"
    }
}

# ============================================================================
# 3. FRONTEND CHECK
# ============================================================================
if (-not $SkipFrontend) {
    Write-Section "?? Frontend Check"
    
    # Check for HTML files
    $htmlFiles = Get-ChildItem -Path . -Filter "*.html" -Recurse -Depth 2 | Where-Object { $_.FullName -notmatch "\\(node_modules|venv|bin|obj|\\_site)" }
    if ($htmlFiles.Count -gt 0) {
        Write-Success "Found $($htmlFiles.Count) HTML files"
    } else {
        Write-Warning "No HTML files found"
        $issues += "No frontend HTML files"
    }
    
    # Check for CSS
    $cssFiles = Get-ChildItem -Path "assets\css" -Filter "*.css" -ErrorAction SilentlyContinue
    if ($cssFiles) {
        Write-Success "CSS files found in assets\css"
    } else {
        Write-Warning "No CSS files in assets\css"
        $issues += "Missing CSS files"
    }
    
    # Check for JavaScript
    $jsFiles = Get-ChildItem -Path "assets\js" -Filter "*.js" -ErrorAction SilentlyContinue
    if ($jsFiles) {
        Write-Success "JavaScript files found in assets\js"
    } else {
        Write-Warning "No JavaScript files in assets\js"
        $issues += "Missing JavaScript files"
    }
    
    # Check if Node.js is needed
    if (Test-Path "package.json") {
        Write-Info "package.json found - checking Node.js..."
        
        $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
        if ($nodeCmd) {
            $nodeVersion = node --version
            Write-Success "Node.js found: $nodeVersion"
            
            if ($AutoFix) {
                Write-Fix "Installing npm packages..."
                npm install --silent
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "npm packages installed"
                } else {
                    Write-Error "npm install failed"
                    $issues += "npm package installation failed"
                }
            }
        } else {
            Write-Warning "Node.js not found (optional)"
        }
    }
    
    # Check for index.html
    if (Test-Path "index.html") {
        Write-Success "Main index.html found"
    } else {
        Write-Warning "No index.html in root"
    }
}

# ============================================================================
# 4. DATABASE CHECK
# ============================================================================
Write-Section "?? Database Check"

# Check for SQLite database (Flask)
if (Test-Path "instance\Evident.db") {
    Write-Success "SQLite database found (Flask)"
} else {
    Write-Warning "SQLite database not found"
    if ($AutoFix) {
        Write-Fix "Creating database directory..."
        New-Item -ItemType Directory -Path "instance" -Force | Out-Null
        $issues += "Database needs initialization"
        $fixes += "Run Flask app to create database: python app.py"
    }
}

# ============================================================================
# 5. CONFIGURATION CHECK
# ============================================================================
Write-Section "??  Configuration Check"

# Check for .env file
if (Test-Path ".env") {
    Write-Success ".env configuration file found"
} else {
    Write-Warning ".env file not found"
    if ($AutoFix) {
        Write-Fix "Creating sample .env file..."
        @"
# Evident.info Environment Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///instance/Evident.db
ASPNETCORE_ENVIRONMENT=Development
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success ".env file created"
    } else {
        $issues += "Missing .env configuration"
        $fixes += "Create .env file with configuration"
    }
}

# Check appsettings.json for .NET
if (Test-Path "src\Evident.Web\appsettings.json") {
    Write-Success ".NET appsettings.json found"
} else {
    Write-Warning ".NET configuration not found"
}

# ============================================================================
# 6. PORT CONFLICTS CHECK
# ============================================================================
Write-Section "?? Port Availability Check"

$ports = @{
    "5000" = "Flask Backend"
    "5001" = ".NET Web API"
}

foreach ($port in $ports.Keys) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Warning "Port $port ($($ports[$port])) is in use by PID: $($connection.OwningProcess)"
        $issues += "Port $port conflict"
        $fixes += "Stop process on port $port or use different port"
    } else {
        Write-Success "Port $port ($($ports[$port])) available"
    }
}

# ============================================================================
# 7. GIT STATUS CHECK
# ============================================================================
Write-Section "?? Git Status"

$gitStatus = git status --porcelain 2>&1
if ($LASTEXITCODE -eq 0) {
    if ($gitStatus) {
        $changedFiles = ($gitStatus -split "`n").Count
        Write-Warning "$changedFiles file(s) with uncommitted changes"
        Write-Info "Run 'git status' for details"
    } else {
        Write-Success "Working directory clean"
    }
} else {
    Write-Warning "Not a git repository or git not installed"
}

# ============================================================================
# SUMMARY
# ============================================================================
Write-Section "?? Health Check Summary"

if ($issues.Count -eq 0) {
    Write-Host ""
    Write-Success "?? NO ISSUES FOUND! App is ready to run."
    Write-Host ""
} else {
    Write-Host ""
    Write-Error "Found $($issues.Count) issue(s):"
    foreach ($issue in $issues) {
        Write-Host "  � $issue" -ForegroundColor Red
    }
    Write-Host ""
    
    if ($fixes.Count -gt 0 -and -not $AutoFix) {
        Write-Host "?? Suggested fixes:" -ForegroundColor Yellow
        foreach ($fix in $fixes) {
            Write-Host "  � $fix" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Host "Run with -AutoFix to apply automatic fixes" -ForegroundColor Cyan
    }
}

# ============================================================================
# RUN APPS
# ============================================================================
if ($RunAfterFix -and $issues.Count -eq 0) {
    Write-Section "?? Starting Applications"
    
    Write-Host ""
    Write-Host "Starting Flask backend on http://localhost:5000" -ForegroundColor Green
    Write-Host "Starting .NET API on http://localhost:5001" -ForegroundColor Green
    Write-Host ""
    Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
    Write-Host ""
    
    # Start Flask in background
    $flaskJob = Start-Job -ScriptBlock {
        Set-Location "C:\web-dev\github-repos\Evident.info"
        .\venv\Scripts\Activate.ps1
        python app.py
    }
    
    # Start .NET API in background
    $dotnetJob = Start-Job -ScriptBlock {
        Set-Location "C:\web-dev\github-repos\Evident.info\src\Evident.Web"
        dotnet run
    }
    
    Write-Host "Flask Job ID: $($flaskJob.Id)" -ForegroundColor Gray
    Write-Host ".NET Job ID: $($dotnetJob.Id)" -ForegroundColor Gray
    Write-Host ""
    
    # Wait for user to stop
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    } finally {
        Write-Host "`nStopping services..." -ForegroundColor Yellow
        Stop-Job -Job $flaskJob, $dotnetJob
        Remove-Job -Job $flaskJob, $dotnetJob
        Write-Success "Services stopped"
    }
}

Write-Host ""
Write-Host "Script completed at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
Write-Host ""
