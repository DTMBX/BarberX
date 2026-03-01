# Configure-Netlify.ps1
# PowerShell script to configure Netlify site via API
# Requires: Netlify Personal Access Token in .env file

[CmdletBinding()]
param(
    [switch]$ShowStatus,
    [switch]$EnableAllFeatures,
    [switch]$UpdateBuildSettings,
    [switch]$ConfigureDomain,
    [switch]$EnableForms,
    [switch]$EnableAnalytics,
    [switch]$SetEnvironmentVars,
    [switch]$All
)

# ═══════════════════════════════════════════════════════════════════════════════
# Load Environment Variables
# ═══════════════════════════════════════════════════════════════════════════════

$envFile = Join-Path $PSScriptRoot ".." ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "❌ ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "📝 Create .env from .env.example:" -ForegroundColor Yellow
    Write-Host "   1. Copy .env.example to .env" -ForegroundColor White
    Write-Host "   2. Add your NETLIFY_AUTH_TOKEN" -ForegroundColor White
    Write-Host "   3. Add your NETLIFY_SITE_ID" -ForegroundColor White
    Write-Host "`n🔑 Get token at: https://app.netlify.com/user/applications" -ForegroundColor Cyan
    exit 1
}

# Parse .env file
$env:NETLIFY_AUTH_TOKEN = $null
$env:NETLIFY_SITE_ID = $null
$env:NETLIFY_DOMAIN = $null

Get-Content $envFile | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        
        switch ($key) {
            'NETLIFY_AUTH_TOKEN' { $env:NETLIFY_AUTH_TOKEN = $value }
            'NETLIFY_SITE_ID' { $env:NETLIFY_SITE_ID = $value }
            'NETLIFY_DOMAIN' { $env:NETLIFY_DOMAIN = $value }
        }
    }
}

# Validate required vars
if (-not $env:NETLIFY_AUTH_TOKEN -or $env:NETLIFY_AUTH_TOKEN -eq 'your_netlify_auth_token_here') {
    Write-Host "❌ ERROR: NETLIFY_AUTH_TOKEN not set in .env" -ForegroundColor Red
    Write-Host "🔑 Get your token at: https://app.netlify.com/user/applications#personal-access-tokens" -ForegroundColor Cyan
    exit 1
}

if (-not $env:NETLIFY_SITE_ID -or $env:NETLIFY_SITE_ID -eq 'your_site_id_here') {
    Write-Host "⚠️  WARNING: NETLIFY_SITE_ID not set in .env" -ForegroundColor Yellow
    Write-Host "   Some operations will be limited" -ForegroundColor White
}

# ═══════════════════════════════════════════════════════════════════════════════
# Netlify API Functions
# ═══════════════════════════════════════════════════════════════════════════════

$baseUrl = "https://api.netlify.com/api/v1"
$headers = @{
    "Authorization" = "Bearer $env:NETLIFY_AUTH_TOKEN"
    "Content-Type" = "application/json"
}

function Get-NetlifySites {
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/sites" -Headers $headers -Method Get
        return $response
    } catch {
        Write-Host "❌ Failed to fetch sites: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

function Get-NetlifySite {
    param([string]$SiteId)
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/sites/$SiteId" -Headers $headers -Method Get
        return $response
    } catch {
        Write-Host "❌ Failed to fetch site: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

function Update-NetlifySite {
    param(
        [string]$SiteId,
        [hashtable]$Settings
    )
    
    try {
        $body = $Settings | ConvertTo-Json -Depth 10
        $response = Invoke-RestMethod -Uri "$baseUrl/sites/$SiteId" -Headers $headers -Method Patch -Body $body
        return $response
    } catch {
        Write-Host "❌ Failed to update site: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

function Set-NetlifyEnvironmentVariables {
    param(
        [string]$SiteId,
        [hashtable]$Variables
    )
    
    try {
        $body = $Variables | ConvertTo-Json -Depth 10
        $response = Invoke-RestMethod -Uri "$baseUrl/accounts/{account_id}/env/$SiteId" -Headers $headers -Method Put -Body $body
        return $response
    } catch {
        Write-Host "❌ Failed to set environment variables: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   Note: This requires account-level permissions" -ForegroundColor Yellow
        return $null
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# Command Handlers
# ═══════════════════════════════════════════════════════════════════════════════

function Show-NetlifyStatus {
    Write-Host "`n🔍 Fetching Netlify Sites..." -ForegroundColor Cyan
    
    $sites = Get-NetlifySites
    if (-not $sites) { return }
    
    Write-Host "`n📊 Your Netlify Sites:" -ForegroundColor Green
    $sites | ForEach-Object {
        Write-Host "`n  Site: $($_.name)" -ForegroundColor White
        Write-Host "  ID: $($_.id)" -ForegroundColor Gray
        Write-Host "  URL: $($_.url)" -ForegroundColor Cyan
        Write-Host "  Custom Domain: $($_.custom_domain ?? 'None')" -ForegroundColor Yellow
        Write-Host "  Build Command: $($_.build_settings.cmd ?? 'None')" -ForegroundColor White
        Write-Host "  Publish Dir: $($_.build_settings.dir ?? 'None')" -ForegroundColor White
        Write-Host "  Status: $($_.state)" -ForegroundColor $(if ($_.state -eq 'current') { 'Green' } else { 'Red' })
    }
    
    if ($env:NETLIFY_SITE_ID) {
        Write-Host "`n📍 Your configured site ID: $env:NETLIFY_SITE_ID" -ForegroundColor Magenta
    }
}

function Update-NetlifyBuildSettings {
    if (-not $env:NETLIFY_SITE_ID) {
        Write-Host "❌ NETLIFY_SITE_ID required for this operation" -ForegroundColor Red
        return
    }
    
    Write-Host "`n🔧 Updating build settings..." -ForegroundColor Cyan
    
    $settings = @{
        build_settings = @{
            cmd = "bundle exec jekyll build"
            dir = "_site"
            env = @{
                RUBY_VERSION = "3.4.0"
                JEKYLL_ENV = "production"
                NODE_VERSION = "20"
            }
        }
        processing_settings = @{
            css = @{
                bundle = $true
                minify = $true
            }
            js = @{
                bundle = $true
                minify = $true
            }
            html = @{
                pretty_urls = $true
            }
            images = @{
                compress = $true
            }
        }
    }
    
    $result = Update-NetlifySite -SiteId $env:NETLIFY_SITE_ID -Settings $settings
    if ($result) {
        Write-Host "✅ Build settings updated successfully!" -ForegroundColor Green
    }
}

function Enable-NetlifyForms {
    if (-not $env:NETLIFY_SITE_ID) {
        Write-Host "❌ NETLIFY_SITE_ID required for this operation" -ForegroundColor Red
        return
    }
    
    Write-Host "`n📧 Enabling Netlify Forms..." -ForegroundColor Cyan
    
    $settings = @{
        processing_settings = @{
            forms = @{
                enabled = $true
            }
        }
    }
    
    $result = Update-NetlifySite -SiteId $env:NETLIFY_SITE_ID -Settings $settings
    if ($result) {
        Write-Host "✅ Forms enabled!" -ForegroundColor Green
        Write-Host "   Add 'data-netlify=`"true`"' to your HTML forms" -ForegroundColor Yellow
    }
}

function Set-NetlifyDomain {
    if (-not $env:NETLIFY_SITE_ID) {
        Write-Host "❌ NETLIFY_SITE_ID required for this operation" -ForegroundColor Red
        return
    }
    
    if (-not $env:NETLIFY_DOMAIN) {
        Write-Host "❌ NETLIFY_DOMAIN not set in .env" -ForegroundColor Red
        return
    }
    
    Write-Host "`n🌐 Configuring domain: $env:NETLIFY_DOMAIN..." -ForegroundColor Cyan
    
    try {
        $body = @{
            domain = $env:NETLIFY_DOMAIN
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$baseUrl/sites/$env:NETLIFY_SITE_ID/domains" `
            -Headers $headers -Method Post -Body $body
        
        Write-Host "✅ Domain added successfully!" -ForegroundColor Green
        Write-Host "📝 Next steps:" -ForegroundColor Yellow
        Write-Host "   1. Configure DNS to point to Netlify" -ForegroundColor White
        Write-Host "   2. Wait for DNS propagation (24-48 hours)" -ForegroundColor White
        Write-Host "   3. Provision SSL certificate in Netlify dashboard" -ForegroundColor White
    } catch {
        if ($_.Exception.Message -match "already exists") {
            Write-Host "✅ Domain already configured" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to add domain: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

function Enable-AllNetlifyFeatures {
    Write-Host "`n🚀 Enabling all Netlify features..." -ForegroundColor Green -BackgroundColor DarkGreen
    
    Update-NetlifyBuildSettings
    Enable-NetlifyForms
    
    if (-not $env:NETLIFY_SITE_ID) {
        Write-Host "`n⚠️  Skipping domain configuration (NETLIFY_SITE_ID not set)" -ForegroundColor Yellow
        return
    }
    
    Write-Host "`n🔧 Enabling additional features..." -ForegroundColor Cyan
    
    $settings = @{
        force_ssl = $true
        processing_settings = @{
            skip_processing = $false
            html = @{
                pretty_urls = $true
            }
            css = @{
                bundle = $true
                minify = $true
            }
            js = @{
                bundle = $true
                minify = $true
            }
            images = @{
                compress = $true
            }
        }
    }
    
    $result = Update-NetlifySite -SiteId $env:NETLIFY_SITE_ID -Settings $settings
    if ($result) {
        Write-Host "`n✅ All features enabled!" -ForegroundColor Green
        Write-Host "`n📋 Enabled:" -ForegroundColor Cyan
        Write-Host "  ✓ Force HTTPS" -ForegroundColor Green
        Write-Host "  ✓ Asset optimization (CSS, JS, Images)" -ForegroundColor Green
        Write-Host "  ✓ Pretty URLs" -ForegroundColor Green
        Write-Host "  ✓ Forms processing" -ForegroundColor Green
        Write-Host "  ✓ Build settings (Jekyll + Ruby 3.4)" -ForegroundColor Green
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main Execution
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "`n🌐 Netlify Configuration Tool" -ForegroundColor Cyan
Write-Host "════════════════════════════════" -ForegroundColor Cyan

if ($All -or $EnableAllFeatures) {
    Enable-AllNetlifyFeatures
} elseif ($ShowStatus) {
    Show-NetlifyStatus
} elseif ($UpdateBuildSettings) {
    Update-NetlifyBuildSettings
} elseif ($ConfigureDomain) {
    Set-NetlifyDomain
} elseif ($EnableForms) {
    Enable-NetlifyForms
} elseif ($SetEnvironmentVars) {
    Write-Host "⚠️  Environment variable management requires manual setup" -ForegroundColor Yellow
    Write-Host "   Go to: Site settings → Environment variables" -ForegroundColor White
} else {
    # Show help
    Write-Host "`nUsage:" -ForegroundColor Yellow
    Write-Host "  .\Configure-Netlify.ps1 -ShowStatus" -ForegroundColor White
    Write-Host "  .\Configure-Netlify.ps1 -EnableAllFeatures" -ForegroundColor White
    Write-Host "  .\Configure-Netlify.ps1 -UpdateBuildSettings" -ForegroundColor White
    Write-Host "  .\Configure-Netlify.ps1 -ConfigureDomain" -ForegroundColor White
    Write-Host "  .\Configure-Netlify.ps1 -EnableForms" -ForegroundColor White
    Write-Host "`nOptions:" -ForegroundColor Yellow
    Write-Host "  -ShowStatus           : Show all your Netlify sites" -ForegroundColor White
    Write-Host "  -EnableAllFeatures    : Enable all optimizations (RECOMMENDED)" -ForegroundColor Green
    Write-Host "  -UpdateBuildSettings  : Set Jekyll build command" -ForegroundColor White
    Write-Host "  -ConfigureDomain      : Add custom domain" -ForegroundColor White
    Write-Host "  -EnableForms          : Enable form submissions" -ForegroundColor White
    Write-Host "`n📖 First time? Run: .\Configure-Netlify.ps1 -ShowStatus" -ForegroundColor Cyan
}

Write-Host ""
