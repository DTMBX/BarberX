# Evident Quick Start Script
# Automatically sets up and runs the Evident development environment

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('android', 'ios', 'windows', 'web', 'all')]
    [string]$Platform = 'windows',
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipDependencies
)

Write-Host "🚀 Evident Quick Start" -ForegroundColor Cyan
Write-Host "Platform: $Platform" -ForegroundColor Yellow
Write-Host ""

# Check prerequisites
function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Cyan
    
    # Check .NET SDK
    try {
        $dotnetVersion = dotnet --version
        Write-Host "✅ .NET SDK: $dotnetVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ .NET SDK not found. Please install .NET 9.0 SDK" -ForegroundColor Red
        exit 1
    }
    
    # Check Python
    try {
        $pythonVersion = python --version
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Python not found. Web features may not work." -ForegroundColor Yellow
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version
        Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Node.js not found. Web build tools may not work." -ForegroundColor Yellow
    }
}

# Install dependencies
function Install-Dependencies {
    if ($SkipDependencies) {
        Write-Host "Skipping dependency installation..." -ForegroundColor Yellow
        return
    }
    
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    
    # .NET dependencies
    Write-Host "Restoring .NET packages..." -ForegroundColor Yellow
    Push-Location "src\Evident.Mobile"
    dotnet restore
    Pop-Location
    
    # Python dependencies
    if (Test-Path "venv") {
        Write-Host "Activating Python virtual environment..." -ForegroundColor Yellow
        .\venv\Scripts\Activate.ps1
    } else {
        Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
        python -m venv venv
        .\venv\Scripts\Activate.ps1
    }
    
    Write-Host "Installing Python packages..." -ForegroundColor Yellow
    pip install -r requirements.txt --quiet
    
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
}

# Build and run platform
function Start-Platform {
    param([string]$TargetPlatform)
    
    Write-Host ""
    Write-Host "Starting $TargetPlatform..." -ForegroundColor Cyan
    
    switch ($TargetPlatform) {
        'windows' {
            Write-Host "Building Windows app..." -ForegroundColor Yellow
            Push-Location "src\Evident.Mobile"
            dotnet build -f net10.0-windows10.0.19041.0 -c Debug
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Build successful. Launching app..." -ForegroundColor Green
                dotnet run -f net10.0-windows10.0.19041.0
            }
            Pop-Location
        }
        
        'android' {
            Write-Host "Building Android app..." -ForegroundColor Yellow
            Push-Location "src\Evident.Mobile"
            dotnet build -f net10.0-android -c Debug
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Build successful. Deploying to device..." -ForegroundColor Green
                dotnet build -f net10.0-android -c Debug -t:Run
            }
            Pop-Location
        }
        
        'ios' {
            if ($IsMacOS) {
                Write-Host "Building iOS app..." -ForegroundColor Yellow
                Push-Location "src\Evident.Mobile"
                dotnet build -f net10.0-ios -c Debug
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ Build successful. Launching simulator..." -ForegroundColor Green
                    dotnet build -f net10.0-ios -c Debug -t:Run
                }
                Pop-Location
            } else {
                Write-Host "❌ iOS development requires macOS" -ForegroundColor Red
            }
        }
        
        'web' {
            Write-Host "Starting Flask backend..." -ForegroundColor Yellow
            Start-Process python -ArgumentList "app.py" -NoNewWindow
            Write-Host "✅ Web server starting at http://localhost:5000" -ForegroundColor Green
            Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        }
        
        'all' {
            Write-Host "Starting all platforms..." -ForegroundColor Yellow
            Start-Platform -TargetPlatform 'web'
            Start-Sleep -Seconds 2
            Start-Platform -TargetPlatform 'windows'
        }
    }
}

# Main execution
try {
    Test-Prerequisites
    Install-Dependencies
    Start-Platform -TargetPlatform $Platform
    
    Write-Host ""
    Write-Host "🎉 Evident is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  - Open http://localhost:5000 for web interface" -ForegroundColor White
    Write-Host "  - Mobile app should be running on your device/emulator" -ForegroundColor White
    Write-Host "  - Check BUILD-GUIDE.md for detailed documentation" -ForegroundColor White
    
} catch {
    Write-Host ""
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "Check BUILD-GUIDE.md for troubleshooting" -ForegroundColor Yellow
    exit 1
}
