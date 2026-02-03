# Visual Studio 2026 Optimization Configuration
# Run this AFTER Visual Studio has been installed
# Run as Administrator

$vsVersion = "18.0" # VS 2026

Write-Host "Configuring Visual Studio 2026 for optimal performance..." -ForegroundColor Cyan

# Performance Optimizations
Write-Host "`n[Performance] Applying optimizations..." -ForegroundColor Yellow

# Use PowerShell native registry commands (fixes variable expansion issue)
$vsRegBase = "HKCU:\Software\Microsoft\VisualStudio\$vsVersion"

# Create registry paths if they don't exist
$regPaths = @("$vsRegBase\General", "$vsRegBase\Settings", "$vsRegBase\TextEditor\CSharp", "$vsRegBase\ProjectsAndSolutions")
foreach ($path in $regPaths) {
    if (-not (Test-Path $path)) {
        New-Item -Path $path -Force | Out-Null
    }
}

# Enable hardware acceleration
Set-ItemProperty -Path "$vsRegBase\General" -Name "HardwareAccelerationMode" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue

# Disable synchronized settings (for speed)
Set-ItemProperty -Path "$vsRegBase\Settings" -Name "EnableRoaming" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue

# Editor Optimizations
Write-Host "`n[Editor] Configuring editor settings..." -ForegroundColor Yellow

# Format on save
Set-ItemProperty -Path "$vsRegBase\TextEditor\CSharp" -Name "AutoFormatOnSave" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue

# Track active item in Solution Explorer
Set-ItemProperty -Path "$vsRegBase\ProjectsAndSolutions" -Name "TrackActiveItem" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue

# Configure Git settings for your repo
Write-Host "`n[Git] Configuring Git for Evident.info..." -ForegroundColor Yellow
git config --global user.name "DTB396"
git config --global core.autocrlf true
git config --global init.defaultBranch main
git config --global pull.rebase false

# Create VS settings file for Evident.info workspace
Write-Host "`n[Workspace] Creating .vscode settings for Evident.info..." -ForegroundColor Yellow
$repoPath = "C:\web-dev\github-repos\Evident.info"

if (Test-Path $repoPath) {
    $vscodePath = Join-Path $repoPath ".vscode"
    New-Item -ItemType Directory -Path $vscodePath -Force | Out-Null
    
    # Create recommended extensions file
    $extensionsJson = @'
{
  "recommendations": [
    "ms-dotnettools.csharp",
    "ms-dotnettools.csdevkit",
    "ms-azuretools.vscode-docker",
    "ms-vscode.vscode-node-azure-pack",
    "GitHub.copilot",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode"
  ]
}
'@
    $extensionsJson | Out-File -FilePath (Join-Path $vscodePath "extensions.json") -Encoding UTF8
    
    # Create settings file
    $settingsJson = @'
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[csharp]": {
    "editor.defaultFormatter": "ms-dotnettools.csharp"
  },
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  "dotnet.defaultSolution": "Evident.sln"
}
'@
    $settingsJson | Out-File -FilePath (Join-Path $vscodePath "settings.json") -Encoding UTF8
    
    Write-Host "Workspace settings created at $vscodePath" -ForegroundColor Green
} else {
    Write-Host "Warning: Repository path not found at $repoPath" -ForegroundColor Red
}

Write-Host "`n✓ Visual Studio 2026 configuration complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Restart your computer to complete Docker installation" -ForegroundColor White
Write-Host "2. Open Visual Studio 2026" -ForegroundColor White
Write-Host "3. Sign in with your Microsoft/GitHub account" -ForegroundColor White
Write-Host "4. Install Extensions: Tools > Extensions > Manage Extensions" -ForegroundColor White
Write-Host "   - GitHub Copilot" -ForegroundColor Gray
Write-Host "   - Web Essentials" -ForegroundColor Gray
Write-Host "   - Productivity Power Tools" -ForegroundColor Gray
Write-Host "5. Open your Evident.info solution: File > Open > Project/Solution" -ForegroundColor White
Write-Host "   Location: C:\web-dev\github-repos\Evident.info" -ForegroundColor Gray