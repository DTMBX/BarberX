# Evident Technologies Development PowerShell Profile
# Save to: $PROFILE (run `notepad $PROFILE`)

# === COLOR DEFINITIONS ===
$Script:Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Highlight = "Magenta"
}

# === DIRECTORY SHORTCUTS ===
$Script:EvidentPaths = @{
    Root = "C:\web-dev\github-repos\Evident.info"
    MAUI = "C:\web-dev\github-repos\Evident.info\src\Evident.MatterDocket.MAUI"
    API = "C:\web-dev\github-repos\Evident.info\api"
    Tests = "C:\web-dev\github-repos\Evident.info\tests"
    Docs = "C:\web-dev\github-repos\Evident.info"
}

# Recent locations stack (max 10)
$Script:RecentLocations = @()
$Script:MaxRecentLocations = 10

# === NAVIGATION FUNCTIONS ===

function ev {
    <#
    .SYNOPSIS
    Go to Evident root directory
    #>
    Set-LocationWithHistory $Script:EvidentPaths.Root
    Write-Host "📁 Evident Root" -ForegroundColor $Script:Colors.Info
}

function em {
    <#
    .SYNOPSIS
    Go to MAUI project directory
    #>
    Set-LocationWithHistory $Script:EvidentPaths.MAUI
    Write-Host "📱 MAUI Project" -ForegroundColor $Script:Colors.Info
}

function ea {
    <#
    .SYNOPSIS
    Go to API directory
    #>
    Set-LocationWithHistory $Script:EvidentPaths.API
    Write-Host "🔌 API Directory" -ForegroundColor $Script:Colors.Info
}

function ed {
    <#
    .SYNOPSIS
    Go to Docs directory
    #>
    Set-LocationWithHistory $Script:EvidentPaths.Docs
    Write-Host "📚 Docs Directory" -ForegroundColor $Script:Colors.Info
}

function b- {
    <#
    .SYNOPSIS
    Go back to previous location
    #>
    if ($Script:RecentLocations.Count -gt 1) {
        $Script:RecentLocations = $Script:RecentLocations[1..($Script:RecentLocations.Count - 1)]
        $previous = $Script:RecentLocations[0]
        Set-Location $previous -ErrorAction SilentlyContinue
        Write-Host "⬅️  Back to: $previous" -ForegroundColor $Script:Colors.Info
    } else {
        Write-Host "❌ No previous location" -ForegroundColor $Script:Colors.Warning
    }
}

function brecent {
    <#
    .SYNOPSIS
    Show recent locations
    #>
    Write-Host "`n📍 Recent Locations:" -ForegroundColor $Script:Colors.Highlight
    for ($i = 0; $i -lt $Script:RecentLocations.Count; $i++) {
        Write-Host "  [$i] $($Script:RecentLocations[$i])" -ForegroundColor $Script:Colors.Info
    }
    Write-Host ""
}

function Set-LocationWithHistory {
    param([string]$Path)
    
    $currentLocation = Get-Location | Select-Object -ExpandProperty Path
    
    # Add current location to history (if different)
    if ($currentLocation -ne $Path) {
        $Script:RecentLocations = @($currentLocation) + $Script:RecentLocations
        
        # Keep only last N locations
        if ($Script:RecentLocations.Count > $Script:MaxRecentLocations) {
            $Script:RecentLocations = $Script:RecentLocations[0..($Script:MaxRecentLocations - 1)]
        }
    }
    
    Set-Location $Path
}

# === BUILD FUNCTIONS ===

function Build-MAUI {
    <#
    .SYNOPSIS
    Build MAUI project for Windows
    #>
    param(
        [ValidateSet("Debug", "Release")]
        [string]$Configuration = "Debug",
        [switch]$Clean
    )
    
    $originalLocation = Get-Location
    Set-Location $Script:EvidentPaths.MAUI
    
    try {
        if ($Clean) {
            Write-Host "🧹 Cleaning..." -ForegroundColor $Script:Colors.Warning
            dotnet clean
            Remove-Item -Recurse -Force bin, obj -ErrorAction SilentlyContinue
        }
        
        Write-Host "🔨 Building MAUI ($Configuration)..." -ForegroundColor $Script:Colors.Info
        dotnet build -f net10.0-windows10.0.19041.0 -c $Configuration
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Build succeeded!" -ForegroundColor $Script:Colors.Success
        } else {
            Write-Host "❌ Build failed!" -ForegroundColor $Script:Colors.Error
        }
    }
    finally {
        Set-Location $originalLocation
    }
}

function Run-MAUI {
    <#
    .SYNOPSIS
    Run MAUI app
    #>
    $originalLocation = Get-Location
    Set-Location $Script:EvidentPaths.MAUI
    
    try {
        Write-Host "🚀 Launching MAUI app..." -ForegroundColor $Script:Colors.Info
        dotnet run -f net10.0-windows10.0.19041.0
    }
    finally {
        Set-Location $originalLocation
    }
}

function Start-FlaskAPI {
    <#
    .SYNOPSIS
    Start Flask backend
    #>
    $originalLocation = Get-Location
    Set-Location $Script:EvidentPaths.Root
    
    try {
        Write-Host "🔌 Starting Flask API..." -ForegroundColor $Script:Colors.Info
        python app.py
    }
    finally {
        Set-Location $originalLocation
    }
}

function Test-Evident {
    <#
    .SYNOPSIS
    Run all tests
    #>
    $originalLocation = Get-Location
    Set-Location $Script:EvidentPaths.Root
    
    try {
        Write-Host "🧪 Running tests..." -ForegroundColor $Script:Colors.Info
        
        # Run Python tests
        if (Test-Path "tests") {
            Write-Host "  Python tests..." -ForegroundColor $Script:Colors.Info
            python -m pytest tests/ -v
        }
        
        # Run MAUI tests
        if (Test-Path "src\Evident.MatterDocket.MAUI.Tests") {
            Write-Host "  MAUI tests..." -ForegroundColor $Script:Colors.Info
            dotnet test src\Evident.MatterDocket.MAUI.Tests
        }
        
        Write-Host "✅ Tests complete!" -ForegroundColor $Script:Colors.Success
    }
    finally {
        Set-Location $originalLocation
    }
}

# === GIT SHORTCUTS ===

function gs {
    <#
    .SYNOPSIS
    Git status (short)
    #>
    git status -s
}

function gaa {
    <#
    .SYNOPSIS
    Git add all
    #>
    git add .
    Write-Host "✅ All changes staged" -ForegroundColor $Script:Colors.Success
}

function gc {
    <#
    .SYNOPSIS
    Git commit with message
    #>
    param([Parameter(Mandatory)][string]$Message)
    
    git commit -m $Message
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Committed: $Message" -ForegroundColor $Script:Colors.Success
    }
}

function gp {
    <#
    .SYNOPSIS
    Git push
    #>
    Write-Host "🚀 Pushing to origin..." -ForegroundColor $Script:Colors.Info
    git push origin main
}

function gpl {
    <#
    .SYNOPSIS
    Git pull
    #>
    Write-Host "⬇️  Pulling from origin..." -ForegroundColor $Script:Colors.Info
    git pull origin main
}

function gquick {
    <#
    .SYNOPSIS
    Quick commit and push
    #>
    param([Parameter(Mandatory)][string]$Message)
    
    gaa
    gc $Message
    gp
}

# === DATABASE SHORTCUTS ===

function Migrate-DB {
    <#
    .SYNOPSIS
    Run database migrations
    #>
    param([string]$MigrationScript = "migrate_add_chatgpt.py")
    
    $originalLocation = Get-Location
    Set-Location $Script:EvidentPaths.Root
    
    try {
        Write-Host "🗄️  Running migration: $MigrationScript" -ForegroundColor $Script:Colors.Info
        python $MigrationScript
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Migration complete!" -ForegroundColor $Script:Colors.Success
        }
    }
    finally {
        Set-Location $originalLocation
    }
}

function Reset-DB {
    <#
    .SYNOPSIS
    Reset database (WARNING: Deletes all data!)
    #>
    $confirm = Read-Host "⚠️  This will DELETE all data! Are you sure? (yes/no)"
    
    if ($confirm -eq "yes") {
        $originalLocation = Get-Location
        Set-Location $Script:EvidentPaths.Root
        
        try {
            Remove-Item instance\*.db -Force -ErrorAction SilentlyContinue
            Write-Host "🗑️  Database deleted" -ForegroundColor $Script:Colors.Warning
            
            Write-Host "🔄 Recreating tables..." -ForegroundColor $Script:Colors.Info
            python -c "from models_auth import db, app; app.app_context().push(); db.create_all(); print('✅ Tables created')"
        }
        finally {
            Set-Location $originalLocation
        }
    }
}

# === UTILITY FUNCTIONS ===

function Show-EvidentMenu {
    <#
    .SYNOPSIS
    Show Evident command menu
    #>
    Write-Host "`n╔══════════════════════════════════════════╗" -ForegroundColor $Script:Colors.Highlight
    Write-Host "║     Evident Development Commands         ║" -ForegroundColor $Script:Colors.Highlight
    Write-Host "╚══════════════════════════════════════════╝`n" -ForegroundColor $Script:Colors.Highlight
    
    Write-Host "📁 Navigation:" -ForegroundColor $Script:Colors.Info
    Write-Host "  br          - Go to root directory"
    Write-Host "  bm          - Go to MAUI project"
    Write-Host "  ba          - Go to API directory"
    Write-Host "  bd          - Go to docs directory"
    Write-Host "  b-          - Go back to previous location"
    Write-Host "  brecent     - Show recent locations`n"
    
    Write-Host "🔨 Build & Run:" -ForegroundColor $Script:Colors.Info
    Write-Host "  Build-MAUI        - Build MAUI project"
    Write-Host "  Run-MAUI          - Run MAUI app"
    Write-Host "  Start-FlaskAPI    - Start Flask backend"
    Write-Host "  Test-Evident      - Run all tests`n"
    
    Write-Host "📝 Git Shortcuts:" -ForegroundColor $Script:Colors.Info
    Write-Host "  gs               - Git status (short)"
    Write-Host "  gaa              - Git add all"
    Write-Host "  gc 'message'     - Git commit"
    Write-Host "  gp               - Git push"
    Write-Host "  gpl              - Git pull"
    Write-Host "  gquick 'message' - Add, commit, and push`n"
    
    Write-Host "🗄️  Database:" -ForegroundColor $Script:Colors.Info
    Write-Host "  Migrate-DB  - Run database migration"
    Write-Host "  Reset-DB    - Reset database (WARNING!)`n"
    
    Write-Host "💡 Tip: Type 'bmenu' anytime to see this menu`n" -ForegroundColor $Script:Colors.Warning
}

# Alias for menu
Set-Alias -Name bmenu -Value Show-EvidentMenu

# === WELCOME MESSAGE ===
Write-Host "`n🚀 Evident Development Environment Loaded!" -ForegroundColor $Script:Colors.Success
Write-Host "   Type 'bmenu' to see all commands`n" -ForegroundColor $Script:Colors.Info

# Auto-navigate to Evident on load (optional)
# Uncomment next line to auto-cd to project on PowerShell start:
# br
