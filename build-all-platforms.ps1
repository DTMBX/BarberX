# Evident Multi-Platform Build Script
# Builds all platform targets: Windows, Android, iOS, Web API, and Flask

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Debug',
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipMobile,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipWebAPI,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipFlask,
    
    [Parameter(Mandatory=$false)]
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Evident Multi-Platform Build" -ForegroundColor Cyan
Write-Host "Configuration: $Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Helper function for colored output
function Write-Step {
    param([string]$Message)
    Write-Host "`n▶ $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "  ✗ $Message" -ForegroundColor Red
}

# Get repository root
$RepoRoot = $PSScriptRoot
Set-Location $RepoRoot

# Clean if requested
if ($Clean) {
    Write-Step "Cleaning build artifacts..."
    
    Get-ChildItem -Path $RepoRoot -Include bin,obj -Recurse -Directory | Remove-Item -Recurse -Force
    Write-Success "Cleaned all bin/obj folders"
}

# Build Shared Library
Write-Step "Building Evident.Shared..."
try {
    dotnet build "$RepoRoot\src\Evident.Shared\Evident.Shared.csproj" -c $Configuration
    Write-Success "Evident.Shared built successfully"
} catch {
    Write-Error "Failed to build Evident.Shared: $_"
    exit 1
}

# Build Mobile App
if (-not $SkipMobile) {
    Write-Step "Building Evident.Mobile..."
    
    $MobileProject = "$RepoRoot\src\Evident.Mobile\Evident.Mobile.csproj"
    
    # Build for Windows
    if ($IsWindows -or $env:OS -eq "Windows_NT") {
        Write-Host "  Building for Windows..." -ForegroundColor Cyan
        try {
            dotnet build $MobileProject -f net10.0-windows -c $Configuration
            Write-Success "Windows build completed"
        } catch {
            Write-Error "Windows build failed: $_"
        }
    }
    
    # Build for Android
    Write-Host "  Building for Android..." -ForegroundColor Cyan
    try {
        dotnet build $MobileProject -f net10.0-android -c $Configuration
        Write-Success "Android build completed"
    } catch {
        Write-Error "Android build failed: $_"
    }
    
    # Build for iOS (requires macOS)
    if ($IsMacOS) {
        Write-Host "  Building for iOS..." -ForegroundColor Cyan
        try {
            dotnet build $MobileProject -f net10.0-ios -c $Configuration
            Write-Success "iOS build completed"
        } catch {
            Write-Error "iOS build failed: $_"
        }
    } else {
        Write-Host "  ⊘ Skipping iOS build (requires macOS)" -ForegroundColor Gray
    }
}

# Build Web API
if (-not $SkipWebAPI) {
    Write-Step "Building Evident.Web API..."
    try {
        dotnet build "$RepoRoot\src\Evident.Web\Evident.Web.csproj" -c $Configuration
        Write-Success "Web API built successfully"
    } catch {
        Write-Error "Failed to build Web API: $_"
    }
}

# Setup Flask Backend
if (-not $SkipFlask) {
    Write-Step "Setting up Flask backend..."
    
    # Check if virtual environment exists
    $VenvPath = "$RepoRoot\.venv"
    if (-not (Test-Path $VenvPath)) {
        Write-Host "  Creating Python virtual environment..." -ForegroundColor Cyan
        python -m venv $VenvPath
        Write-Success "Virtual environment created"
    }
    
    # Activate virtual environment
    if ($IsWindows -or $env:OS -eq "Windows_NT") {
        & "$VenvPath\Scripts\Activate.ps1"
    } else {
        & "$VenvPath/bin/Activate.ps1"
    }
    
    # Install/update dependencies
    Write-Host "  Installing Python dependencies..." -ForegroundColor Cyan
    try {
        pip install --upgrade pip -q
        pip install -r "$RepoRoot\requirements.txt" -q
        Write-Success "Python dependencies installed"
    } catch {
        Write-Error "Failed to install Python dependencies: $_"
    }
}

# Build Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Build Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nBuilt Components:" -ForegroundColor White
Write-Host "  ✓ Evident.Shared (.NET library)" -ForegroundColor Green

if (-not $SkipMobile) {
    Write-Host "  ✓ Evident.Mobile (MAUI app)" -ForegroundColor Green
    if ($IsWindows -or $env:OS -eq "Windows_NT") {
        Write-Host "    - Windows" -ForegroundColor Gray
    }
    Write-Host "    - Android" -ForegroundColor Gray
    if ($IsMacOS) {
        Write-Host "    - iOS" -ForegroundColor Gray
    }
}

if (-not $SkipWebAPI) {
    Write-Host "  ✓ Evident.Web (ASP.NET Core API)" -ForegroundColor Green
}

if (-not $SkipFlask) {
    Write-Host "  ✓ Flask Backend (Python)" -ForegroundColor Green
}

Write-Host "`nNext Steps:" -ForegroundColor White
Write-Host "  • Run mobile app: dotnet run --project src\Evident.Mobile -f net10.0-windows" -ForegroundColor Gray
Write-Host "  • Run Web API: dotnet run --project src\Evident.Web" -ForegroundColor Gray
Write-Host "  • Run Flask: python app.py" -ForegroundColor Gray

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
