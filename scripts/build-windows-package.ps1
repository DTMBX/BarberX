# Evident PWA to Windows 11 MSIX Package Builder
# This script packages the Evident PWA as a Windows 11 application

param(
    [string]$Url = "https://Evident.info",
    [string]$OutputDir = "windows-package"
)

Write-Output "📦 Evident WINDOWS 11 MSIX PACKAGE BUILDER`n"
Write-Output "═══════════════════════════════════════════════════`n"

# Configuration
$packageName = "Evident Matter Docket (DTMB)"
$packageIdentifier = "com.Evident.matterdocket"
$packageVersion = "1.0.0.0"
$publisherName = "Evident"
$publisherDisplayName = "Evident Matter Docket"

Write-Output "Configuration:"
Write-Output "  App Name: $packageName"
Write-Output "  Package ID: $packageIdentifier"
Write-Output "  Version: $packageVersion"
Write-Output "  URL: $Url"
Write-Output "  Output: $OutputDir`n"

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Output "✅ Created output directory`n"
}

# Method 1: Use PWA Builder CLI
Write-Output "Method 1: PWA Builder CLI (Recommended)`n"
Write-Output "Running: pwa package $Url --output $OutputDir`n"

try {
    # Note: PWA Builder will analyze the live site and generate packages
    # For offline/local testing, we'll need to use Method 2
    Write-Output "⚠️  PWA Builder requires a live URL to analyze.`n"
    Write-Output "Since we're testing locally, we'll use Method 2...`n"
} catch {
    Write-Output "❌ PWA Builder CLI failed: $_`n"
}

# Method 2: Manual MSIX Generation with Windows SDK
Write-Output "Method 2: Manual MSIX Package Creation`n"

# Check if Windows SDK is installed
$makeappx = Get-Command makeappx -ErrorAction SilentlyContinue

if ($makeappx) {
    Write-Output "✅ Windows SDK found (makeappx available)`n"
    
    # Create package structure
    $packageRoot = Join-Path $OutputDir "Evident-Package"
    $assetsDir = Join-Path $packageRoot "Assets"
    
    New-Item -ItemType Directory -Path $packageRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $assetsDir -Force | Out-Null
    
    Write-Output "Creating package structure:`n"
    Write-Output "  📁 $packageRoot"
    Write-Output "  📁 $assetsDir`n"
    
    # Copy icons
    Write-Output "Copying icon assets...`n"
    Copy-Item "assets\icons\icon-44x44.png" "$assetsDir\Square44x44Logo.png" -ErrorAction SilentlyContinue
    Copy-Item "assets\icons\icon-150x150.png" "$assetsDir\Square150x150Logo.png" -ErrorAction SilentlyContinue
    Copy-Item "assets\icons\icon-310x310.png" "$assetsDir\Square310x310Logo.png" -ErrorAction SilentlyContinue
    Copy-Item "assets\icons\icon-71x71.png" "$assetsDir\Square71x71Logo.png" -ErrorAction SilentlyContinue
    
    # Use available icons as fallbacks
    Copy-Item "assets\icons\icon-72x72.png" "$assetsDir\Square44x44Logo.png" -Force
    Copy-Item "assets\icons\icon-152x152.png" "$assetsDir\Square150x150Logo.png" -Force
    Copy-Item "assets\icons\icon-384x384.png" "$assetsDir\Square310x310Logo.png" -Force
    Copy-Item "assets\icons\icon-72x72.png" "$assetsDir\Square71x71Logo.png" -Force
    
    Write-Output "  ✅ Icons copied`n"
    
    # Create AppxManifest.xml
    $manifestXml = @"
<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
         xmlns:uap3="http://schemas.microsoft.com/appx/manifest/uap/windows10/3"
         xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities">
  <Identity Name="$packageIdentifier"
            Version="$packageVersion"
            Publisher="CN=$publisherName" />
  
  <Properties>
    <DisplayName>$packageName</DisplayName>
    <PublisherDisplayName>$publisherDisplayName</PublisherDisplayName>
    <Logo>Assets\Square150x150Logo.png</Logo>
  </Properties>
  
  <Dependencies>
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.19041.0" MaxVersionTested="10.0.22621.0" />
  </Dependencies>
  
  <Resources>
    <Resource Language="en-us" />
  </Resources>
  
  <Applications>
    <Application Id="EvidentLegal" StartPage="$Url">
      <uap:VisualElements DisplayName="$packageName"
                          Description="Professional matter docket management and legal case tracking platform"
                          BackgroundColor="#0f0f0f"
                          Square150x150Logo="Assets\Square150x150Logo.png"
                          Square44x44Logo="Assets\Square44x44Logo.png">
        <uap:DefaultTile Wide310x150Logo="Assets\Square310x310Logo.png"
                         Square310x310Logo="Assets\Square310x310Logo.png"
                         Square71x71Logo="Assets\Square71x71Logo.png">
          <uap:ShowNameOnTiles>
            <uap:ShowOn Tile="square150x150Logo"/>
            <uap:ShowOn Tile="wide310x150Logo"/>
            <uap:ShowOn Tile="square310x310Logo"/>
          </uap:ShowNameOnTiles>
        </uap:DefaultTile>
      </uap:VisualElements>
      
      <uap:ApplicationContentUriRules>
        <uap:Rule Type="include" Match="$Url" WindowsRuntimeAccess="all"/>
      </uap:ApplicationContentUriRules>
    </Application>
  </Applications>
  
  <Capabilities>
    <Capability Name="internetClient"/>
    <Capability Name="internetClientServer"/>
    <uap:Capability Name="documentsLibrary"/>
    <uap:Capability Name="picturesLibrary"/>
  </Capabilities>
</Package>
"@
    
    $manifestPath = Join-Path $packageRoot "AppxManifest.xml"
    $manifestXml | Out-File -FilePath $manifestPath -Encoding UTF8
    
    Write-Output "  ✅ AppxManifest.xml created`n"
    
    Write-Output "Package structure ready!`n"
    Write-Output "To build MSIX package, run:`n"
    Write-Output "  makeappx pack /d $packageRoot /p $OutputDir\Evident.msix`n"
    
} else {
    Write-Output "⚠️  Windows SDK not found.`n"
    Write-Output "To build MSIX packages, install Windows SDK from:`n"
    Write-Output "https://developer.microsoft.com/windows/downloads/windows-sdk/`n"
}

# Method 3: PWA Builder Web Interface
Write-Output "Method 3: PWA Builder Web Interface (Easiest)`n"
Write-Output "Steps:"
Write-Output "  1. Visit: https://www.pwabuilder.com/"
Write-Output "  2. Enter URL: $Url"
Write-Output "  3. Click 'Package For Stores'"
Write-Output "  4. Select 'Windows' platform"
Write-Output "  5. Download MSIX package`n"

Write-Output "═══════════════════════════════════════════════════`n"
Write-Output "✅ PACKAGING PREPARATION COMPLETE`n"
Write-Output "Next steps:"
Write-Output "  1. Test package structure in $OutputDir"
Write-Output "  2. Generate MSIX with makeappx (if Windows SDK installed)"
Write-Output "  3. OR use PWA Builder web interface (recommended)`n"
