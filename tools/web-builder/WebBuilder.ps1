# ═══════════════════════════════════════════════════════════════════════════
#                    EVIDENT WEB BUILDER — Windows Launcher
# ═══════════════════════════════════════════════════════════════════════════
# A modern web development tool for building GitHub sites with best practices.
#
# Usage:
#   .\WebBuilder.ps1                    # Launch Web Builder
#   .\WebBuilder.ps1 -Project "C:\path" # Open specific project
#   .\WebBuilder.ps1 -Install           # Install desktop shortcut
#   .\WebBuilder.ps1 -Server            # Start with live server
# ═══════════════════════════════════════════════════════════════════════════

param(
    [string]$Project = "",
    [switch]$Install,
    [switch]$Server,
    [switch]$Help
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuilderPath = Join-Path $ScriptDir "index.html"
$ConfigPath = Join-Path $ScriptDir "config.json"
$RecentPath = Join-Path $ScriptDir "recent-projects.json"

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

$Config = @{
    DefaultBrowser = "chrome"  # chrome, edge, firefox, default
    LiveServerPort = 3000
    AutoOpenDevTools = $false
    RecentProjectsMax = 10
}

# Load config if exists
if (Test-Path $ConfigPath) {
    try {
        $savedConfig = Get-Content $ConfigPath -Raw | ConvertFrom-Json
        foreach ($key in $savedConfig.PSObject.Properties.Name) {
            $Config[$key] = $savedConfig.$key
        }
    } catch {
        Write-Host "Warning: Could not load config.json" -ForegroundColor Yellow
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

function Write-Banner {
    Write-Host ""
    Write-Host "  ╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║                                                               ║" -ForegroundColor Cyan
    Write-Host "  ║   ███████╗██╗   ██╗██╗██████╗ ███████╗███╗   ██╗████████╗    ║" -ForegroundColor Cyan
    Write-Host "  ║   ██╔════╝██║   ██║██║██╔══██╗██╔════╝████╗  ██║╚══██╔══╝    ║" -ForegroundColor Cyan
    Write-Host "  ║   █████╗  ██║   ██║██║██║  ██║█████╗  ██╔██╗ ██║   ██║       ║" -ForegroundColor Cyan
    Write-Host "  ║   ██╔══╝  ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║╚██╗██║   ██║       ║" -ForegroundColor Cyan
    Write-Host "  ║   ███████╗ ╚████╔╝ ██║██████╔╝███████╗██║ ╚████║   ██║       ║" -ForegroundColor Cyan
    Write-Host "  ║   ╚══════╝  ╚═══╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝       ║" -ForegroundColor Cyan
    Write-Host "  ║                                                               ║" -ForegroundColor Cyan
    Write-Host "  ║              W E B   B U I L D E R                            ║" -ForegroundColor Cyan
    Write-Host "  ║         Modern Standards • Windows Native                     ║" -ForegroundColor DarkCyan
    Write-Host "  ║                                                               ║" -ForegroundColor Cyan
    Write-Host "  ╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Help {
    Write-Banner
    Write-Host "  USAGE:" -ForegroundColor Yellow
    Write-Host "    .\WebBuilder.ps1                     Launch Web Builder"
    Write-Host "    .\WebBuilder.ps1 -Project `"C:\path`"  Open specific project"
    Write-Host "    .\WebBuilder.ps1 -Server             Start with live server"
    Write-Host "    .\WebBuilder.ps1 -Install            Create desktop shortcut"
    Write-Host "    .\WebBuilder.ps1 -Help               Show this help"
    Write-Host ""
    Write-Host "  FEATURES:" -ForegroundColor Yellow
    Write-Host "    • Visual drag-and-drop website builder"
    Write-Host "    • Natural language commands (no coding needed)"
    Write-Host "    • Modern coding standards checker"
    Write-Host "    • Multi-repo project management"
    Write-Host "    • Git workflow integration"
    Write-Host "    • Accessibility validation"
    Write-Host "    • VS Code + Copilot integration"
    Write-Host ""
}

function Get-BrowserPath {
    param([string]$Browser)
    
    $paths = @{
        "chrome" = @(
            "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
            "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
            "$env:LocalAppData\Google\Chrome\Application\chrome.exe"
        )
        "edge" = @(
            "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
            "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
        )
        "firefox" = @(
            "$env:ProgramFiles\Mozilla Firefox\firefox.exe",
            "${env:ProgramFiles(x86)}\Mozilla Firefox\firefox.exe"
        )
    }
    
    if ($paths.ContainsKey($Browser)) {
        foreach ($path in $paths[$Browser]) {
            if (Test-Path $path) {
                return $path
            }
        }
    }
    return $null
}

function Open-InBrowser {
    param([string]$Url)
    
    $browserPath = Get-BrowserPath $Config.DefaultBrowser
    
    if ($browserPath) {
        $browserArgs = @($Url)
        if ($Config.AutoOpenDevTools) {
            $browserArgs += "--auto-open-devtools-for-tabs"
        }
        Start-Process $browserPath -ArgumentList $browserArgs
    } else {
        # Fallback to default browser
        Start-Process $Url
    }
}

function Start-LiveServer {
    param([string]$Path)
    
    # Check if live-server is installed
    $liveServer = Get-Command "live-server" -ErrorAction SilentlyContinue
    
    if (-not $liveServer) {
        Write-Host "  Installing live-server..." -ForegroundColor Yellow
        npm install -g live-server
    }
    
    Write-Host "  Starting live server on port $($Config.LiveServerPort)..." -ForegroundColor Cyan
    
    $serverPath = if ($Path) { $Path } else { $ScriptDir }
    
    Start-Process "live-server" -ArgumentList @(
        $serverPath,
        "--port=$($Config.LiveServerPort)",
        "--no-browser"
    ) -WindowStyle Hidden
    
    Start-Sleep -Seconds 2
    Open-InBrowser "http://localhost:$($Config.LiveServerPort)/index.html"
}

function Add-RecentProject {
    param([string]$Path)
    
    $recent = @()
    if (Test-Path $RecentPath) {
        try {
            $recent = Get-Content $RecentPath -Raw | ConvertFrom-Json
        } catch {
            $recent = @()
        }
    }
    
    # Remove if already exists
    $recent = $recent | Where-Object { $_ -ne $Path }
    
    # Add to front
    $recent = @($Path) + $recent
    
    # Limit to max
    $recent = $recent | Select-Object -First $Config.RecentProjectsMax
    
    $recent | ConvertTo-Json | Set-Content $RecentPath
}

function Show-RecentProjects {
    Write-Host "  RECENT PROJECTS:" -ForegroundColor Yellow
    Write-Host ""
    
    if (-not (Test-Path $RecentPath)) {
        Write-Host "    No recent projects yet." -ForegroundColor DarkGray
        return
    }
    
    $recent = Get-Content $RecentPath -Raw | ConvertFrom-Json
    
    for ($i = 0; $i -lt $recent.Count; $i++) {
        $project = $recent[$i]
        $name = Split-Path $project -Leaf
        Write-Host "    [$($i + 1)] " -ForegroundColor Cyan -NoNewline
        Write-Host "$name" -ForegroundColor White -NoNewline
        Write-Host " — $project" -ForegroundColor DarkGray
    }
    Write-Host ""
}

function Install-DesktopShortcut {
    Write-Host "  Creating desktop shortcut..." -ForegroundColor Cyan
    
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktopPath "Evident Web Builder.lnk"
    
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$ScriptDir\WebBuilder.ps1`""
    $shortcut.WorkingDirectory = $ScriptDir
    $shortcut.Description = "Evident Web Builder — Modern Website Creator"
    $shortcut.IconLocation = "shell32.dll,13"  # Web icon
    $shortcut.Save()
    
    Write-Host "  ✓ Shortcut created: $shortcutPath" -ForegroundColor Green
    
    # Also create a context menu entry
    Write-Host ""
    Write-Host "  Would you like to add 'Open with Web Builder' to folder context menu? (y/n)" -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -eq 'y') {
        Install-ContextMenu
    }
}

function Install-ContextMenu {
    Write-Host "  Adding to folder context menu..." -ForegroundColor Cyan
    
    $regPath = "HKCU:\Software\Classes\Directory\Background\shell\WebBuilder"
    $cmdPath = "$regPath\command"
    
    try {
        New-Item -Path $regPath -Force | Out-Null
        Set-ItemProperty -Path $regPath -Name "(Default)" -Value "Open with Web Builder"
        Set-ItemProperty -Path $regPath -Name "Icon" -Value "shell32.dll,13"
        
        New-Item -Path $cmdPath -Force | Out-Null
        $command = "powershell.exe -ExecutionPolicy Bypass -File `"$ScriptDir\WebBuilder.ps1`" -Project `"%V`""
        Set-ItemProperty -Path $cmdPath -Name "(Default)" -Value $command
        
        Write-Host "  ✓ Context menu entry added!" -ForegroundColor Green
        Write-Host "    Right-click in any folder to see 'Open with Web Builder'" -ForegroundColor DarkGray
    } catch {
        Write-Host "  ✗ Failed to add context menu entry: $_" -ForegroundColor Red
    }
}

function Test-Prerequisites {
    $issues = @()
    
    # Check Node.js
    $node = Get-Command "node" -ErrorAction SilentlyContinue
    if (-not $node) {
        $issues += "Node.js not found. Install from: https://nodejs.org/"
    }
    
    # Check Git
    $git = Get-Command "git" -ErrorAction SilentlyContinue
    if (-not $git) {
        $issues += "Git not found. Install from: https://git-scm.com/"
    }
    
    # Check browser
    $browserPath = Get-BrowserPath $Config.DefaultBrowser
    if (-not $browserPath) {
        $issues += "Browser ($($Config.DefaultBrowser)) not found. Web Builder works best with Chrome or Edge."
    }
    
    if ($issues.Count -gt 0) {
        Write-Host ""
        Write-Host "  PREREQUISITES:" -ForegroundColor Yellow
        foreach ($issue in $issues) {
            Write-Host "    ⚠ $issue" -ForegroundColor DarkYellow
        }
        Write-Host ""
    }
    
    return $issues.Count -eq 0
}

function Show-QuickMenu {
    Write-Host "  QUICK ACTIONS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    [1] Open Web Builder" -ForegroundColor White
    Write-Host "    [2] Open with Live Server" -ForegroundColor White
    Write-Host "    [3] Open Recent Project" -ForegroundColor White
    Write-Host "    [4] Create New Project" -ForegroundColor White
    Write-Host "    [5] Install Shortcut" -ForegroundColor White
    Write-Host "    [6] Check Code Standards" -ForegroundColor White
    Write-Host "    [Q] Quit" -ForegroundColor DarkGray
    Write-Host ""
    
    $choice = Read-Host "  Select"
    
    switch ($choice.ToLower()) {
        "1" { Open-InBrowser $BuilderPath }
        "2" { Start-LiveServer }
        "3" { 
            Show-RecentProjects
            $num = Read-Host "  Enter number"
            if ($num -match '^\d+$') {
                $recent = Get-Content $RecentPath -Raw | ConvertFrom-Json
                $idx = [int]$num - 1
                if ($idx -ge 0 -and $idx -lt $recent.Count) {
                    $Project = $recent[$idx]
                    Add-RecentProject $Project
                    Start-LiveServer $Project
                }
            }
        }
        "4" { New-Project }
        "5" { Install-DesktopShortcut }
        "6" { Start-CodeCheck }
        "q" { exit 0 }
        default { 
            Write-Host "  Invalid choice" -ForegroundColor Red
            Show-QuickMenu
        }
    }
}

function New-Project {
    Write-Host ""
    Write-Host "  CREATE NEW PROJECT:" -ForegroundColor Yellow
    Write-Host ""
    
    $projectName = Read-Host "  Project name"
    $projectPath = Read-Host "  Location (e.g., C:\Projects)"
    
    $fullPath = Join-Path $projectPath $projectName
    
    if (Test-Path $fullPath) {
        Write-Host "  ✗ Folder already exists!" -ForegroundColor Red
        return
    }
    
    Write-Host ""
    Write-Host "  Creating project structure..." -ForegroundColor Cyan
    
    # Create folders
    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    New-Item -ItemType Directory -Path "$fullPath\assets" -Force | Out-Null
    New-Item -ItemType Directory -Path "$fullPath\assets\css" -Force | Out-Null
    New-Item -ItemType Directory -Path "$fullPath\assets\js" -Force | Out-Null
    New-Item -ItemType Directory -Path "$fullPath\assets\images" -Force | Out-Null
    
    # Create index.html with modern standards
    $indexHtml = @"
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="$projectName — A modern website">
  <meta name="theme-color" content="#3b82f6">
  
  <!-- Open Graph -->
  <meta property="og:title" content="$projectName">
  <meta property="og:description" content="A modern website built with Web Builder">
  <meta property="og:type" content="website">
  
  <title>$projectName</title>
  <link rel="stylesheet" href="assets/css/styles.css">
</head>
<body>
  <header class="site-header">
    <nav class="nav-container">
      <a href="/" class="logo">$projectName</a>
      <ul class="nav-links">
        <li><a href="#">Home</a></li>
        <li><a href="#">About</a></li>
        <li><a href="#">Contact</a></li>
      </ul>
    </nav>
  </header>

  <main class="main-content">
    <section class="hero">
      <h1>Welcome to $projectName</h1>
      <p>Start building something amazing.</p>
      <a href="#" class="cta-button">Get Started</a>
    </section>
  </main>

  <footer class="site-footer">
    <p>&copy; $(Get-Date -Format "yyyy") $projectName. All rights reserved.</p>
  </footer>

  <script src="assets/js/main.js" defer></script>
</body>
</html>
"@

    # Create styles.css with modern CSS
    $stylesCss = @"
/* ═══════════════════════════════════════════════════════════════════
   $projectName — Styles
   Generated by Evident Web Builder
   ═══════════════════════════════════════════════════════════════════ */

/* CSS Custom Properties (Design Tokens) */
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-dark: #2563eb;
  --color-text: #1a1a2e;
  --color-text-light: #64748b;
  --color-background: #ffffff;
  --color-surface: #f8fafc;
  --color-border: #e2e8f0;
  
  /* Typography */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-size-base: 1rem;
  --line-height: 1.6;
  
  /* Spacing */
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 2rem;
  --spacing-xl: 4rem;
  
  /* Layout */
  --max-width: 1200px;
  --radius: 8px;
  
  /* Transitions */
  --transition: 200ms ease;
}

/* Dark Mode */
@media (prefers-color-scheme: dark) {
  :root {
    --color-text: #e6edf3;
    --color-text-light: #8b949e;
    --color-background: #0d1117;
    --color-surface: #161b22;
    --color-border: #30363d;
  }
}

/* Reset */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Base */
html {
  font-family: var(--font-sans);
  font-size: var(--font-size-base);
  line-height: var(--line-height);
  scroll-behavior: smooth;
}

body {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-background);
  color: var(--color-text);
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  line-height: 1.2;
  font-weight: 700;
}

h1 { font-size: 2.5rem; }
h2 { font-size: 2rem; }
h3 { font-size: 1.5rem; }

p { margin-bottom: var(--spacing-md); }

a {
  color: var(--color-primary);
  text-decoration: none;
  transition: color var(--transition);
}

a:hover { color: var(--color-primary-dark); }

/* Header */
.site-header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: var(--spacing-md) var(--spacing-lg);
}

.nav-container {
  max-width: var(--max-width);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
}

.nav-links {
  display: flex;
  gap: var(--spacing-lg);
  list-style: none;
}

.nav-links a {
  color: var(--color-text-light);
  font-weight: 500;
}

.nav-links a:hover { color: var(--color-primary); }

/* Main Content */
.main-content {
  flex: 1;
}

/* Hero Section */
.hero {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-lg);
  max-width: 800px;
  margin: 0 auto;
}

.hero h1 {
  margin-bottom: var(--spacing-md);
}

.hero p {
  color: var(--color-text-light);
  font-size: 1.25rem;
  margin-bottom: var(--spacing-lg);
}

/* Buttons */
.cta-button {
  display: inline-block;
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius);
  font-weight: 600;
  transition: background var(--transition), transform var(--transition);
}

.cta-button:hover {
  background: var(--color-primary-dark);
  color: white;
  transform: translateY(-2px);
}

/* Footer */
.site-footer {
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  padding: var(--spacing-lg);
  text-align: center;
  color: var(--color-text-light);
}

/* Responsive */
@media (max-width: 768px) {
  h1 { font-size: 2rem; }
  
  .nav-links {
    gap: var(--spacing-md);
  }
  
  .hero {
    padding: var(--spacing-lg);
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
"@

    # Create main.js
    $mainJs = @"
/**
 * $projectName — Main JavaScript
 * Generated by Evident Web Builder
 */

'use strict';

// Wait for DOM
document.addEventListener('DOMContentLoaded', () => {
  console.log('$projectName loaded');
  
  // Add any interactive features here
});
"@

    # Create .gitignore
    $gitignore = @"
# Dependencies
node_modules/
.npm

# Build outputs
dist/
build/

# IDE
.idea/
.vscode/settings.json
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*

# Environment
.env
.env.local
"@

    # Create README.md
    $readme = @"
# $projectName

A modern website built with Evident Web Builder.

## Quick Start

1. Open in Web Builder
2. Edit visually or modify files directly
3. Deploy to GitHub Pages

## Structure

```
$projectName/
├── index.html          # Main page
├── assets/
│   ├── css/
│   │   └── styles.css  # Styles
│   ├── js/
│   │   └── main.js     # JavaScript
│   └── images/         # Images
└── README.md           # This file
```

## Deploy

\`\`\`bash
git add .
git commit -m "Update site"
git push origin main
\`\`\`

---

Built with [Evident Web Builder](https://github.com/DTMBX/Evident)
"@

    # Write files
    $indexHtml | Set-Content "$fullPath\index.html" -Encoding UTF8
    $stylesCss | Set-Content "$fullPath\assets\css\styles.css" -Encoding UTF8
    $mainJs | Set-Content "$fullPath\assets\js\main.js" -Encoding UTF8
    $gitignore | Set-Content "$fullPath\.gitignore" -Encoding UTF8
    $readme | Set-Content "$fullPath\README.md" -Encoding UTF8
    
    # Initialize Git
    Push-Location $fullPath
    git init | Out-Null
    git add . | Out-Null
    git commit -m "Initial commit from Web Builder" | Out-Null
    Pop-Location
    
    Write-Host ""
    Write-Host "  ✓ Project created: $fullPath" -ForegroundColor Green
    Write-Host ""
    
    Add-RecentProject $fullPath
    
    $open = Read-Host "  Open in Web Builder now? (y/n)"
    if ($open -eq 'y') {
        Start-LiveServer $fullPath
    }
}

function Start-CodeCheck {
    Write-Host ""
    Write-Host "  CODE STANDARDS CHECK:" -ForegroundColor Yellow
    Write-Host ""
    
    $projectPath = Read-Host "  Project path (or press Enter for current)"
    if (-not $projectPath) { $projectPath = Get-Location }
    
    if (-not (Test-Path $projectPath)) {
        Write-Host "  ✗ Path not found" -ForegroundColor Red
        return
    }
    
    Write-Host ""
    Write-Host "  Checking $projectPath..." -ForegroundColor Cyan
    Write-Host ""
    
    $issues = @()
    $warnings = @()
    $passed = @()
    
    # Check for index.html
    if (Test-Path "$projectPath\index.html") {
        $html = Get-Content "$projectPath\index.html" -Raw
        
        # DOCTYPE
        if ($html -match "<!DOCTYPE html>") {
            $passed += "HTML5 DOCTYPE present"
        } else {
            $issues += "Missing HTML5 DOCTYPE"
        }
        
        # Viewport meta
        if ($html -match 'name="viewport"') {
            $passed += "Viewport meta tag present"
        } else {
            $issues += "Missing viewport meta tag (not mobile-friendly)"
        }
        
        # Lang attribute
        if ($html -match '<html\s+lang=') {
            $passed += "Language attribute set"
        } else {
            $warnings += "Missing lang attribute on <html>"
        }
        
        # Meta description
        if ($html -match 'name="description"') {
            $passed += "Meta description present"
        } else {
            $warnings += "Missing meta description (affects SEO)"
        }
        
        # Alt text check
        $images = [regex]::Matches($html, '<img[^>]*>')
        $imagesWithoutAlt = $images | Where-Object { $_.Value -notmatch 'alt=' }
        if ($imagesWithoutAlt.Count -gt 0) {
            $issues += "Found $($imagesWithoutAlt.Count) image(s) without alt text"
        } else {
            $passed += "All images have alt text"
        }
        
        # External CSS
        if ($html -match 'rel="stylesheet"') {
            $passed += "External stylesheet linked"
        }
        
    } else {
        $issues += "No index.html found"
    }
    
    # Check for CSS
    $cssFiles = Get-ChildItem -Path $projectPath -Filter "*.css" -Recurse -ErrorAction SilentlyContinue
    if ($cssFiles.Count -gt 0) {
        $passed += "CSS files found ($($cssFiles.Count))"
    } else {
        $warnings += "No CSS files found"
    }
    
    # Check for .gitignore
    if (Test-Path "$projectPath\.gitignore") {
        $passed += ".gitignore present"
    } else {
        $warnings += "No .gitignore file"
    }
    
    # Check for README
    if (Test-Path "$projectPath\README.md") {
        $passed += "README.md present"
    } else {
        $warnings += "No README.md file"
    }
    
    # Display results
    Write-Host "  ─────────────────────────────────────────────────────" -ForegroundColor DarkGray
    
    if ($passed.Count -gt 0) {
        Write-Host ""
        Write-Host "  ✓ PASSED ($($passed.Count)):" -ForegroundColor Green
        foreach ($p in $passed) {
            Write-Host "    • $p" -ForegroundColor DarkGreen
        }
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host ""
        Write-Host "  ⚠ WARNINGS ($($warnings.Count)):" -ForegroundColor Yellow
        foreach ($w in $warnings) {
            Write-Host "    • $w" -ForegroundColor DarkYellow
        }
    }
    
    if ($issues.Count -gt 0) {
        Write-Host ""
        Write-Host "  ✗ ISSUES ($($issues.Count)):" -ForegroundColor Red
        foreach ($i in $issues) {
            Write-Host "    • $i" -ForegroundColor DarkRed
        }
    }
    
    Write-Host ""
    Write-Host "  ─────────────────────────────────────────────────────" -ForegroundColor DarkGray
    
    $total = $passed.Count + $warnings.Count + $issues.Count
    $score = [math]::Round(($passed.Count / $total) * 100)
    
    $color = if ($score -ge 80) { "Green" } elseif ($score -ge 60) { "Yellow" } else { "Red" }
    Write-Host "  SCORE: $score% ($($passed.Count)/$total checks passed)" -ForegroundColor $color
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if ($Help) {
    Show-Help
    exit 0
}

if ($Install) {
    Write-Banner
    Install-DesktopShortcut
    exit 0
}

Write-Banner
Test-Prerequisites | Out-Null

if ($Project) {
    if (Test-Path $Project) {
        Add-RecentProject $Project
        if ($Server) {
            Start-LiveServer $Project
        } else {
            Open-InBrowser $BuilderPath
        }
    } else {
        Write-Host "  ✗ Project path not found: $Project" -ForegroundColor Red
    }
} elseif ($Server) {
    Start-LiveServer
} else {
    Show-QuickMenu
}
