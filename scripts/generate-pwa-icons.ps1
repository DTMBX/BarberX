# PWA Icon Generator for Evident
# Requires: ImageMagick installed
# Usage: .\generate-pwa-icons.ps1 -SourceImage "path\to\logo.png"

param(
    [string]$SourceImage = "assets\images\logo-source.png",
    [string]$OutputDir = "assets\images",
    [switch]$CreatePlaceholder
)

$ErrorActionPreference = "Stop"

# Icon sizes for PWA
$iconSizes = @(72, 96, 128, 144, 152, 192, 384, 512)
$appleSizes = @(180, 167, 152)
$faviconSizes = @(32, 16)

Write-Host "`n=== Evident PWA Icon Generator ===" -ForegroundColor Cyan
Write-Host "Source: $SourceImage" -ForegroundColor Gray
Write-Host "Output: $OutputDir`n" -ForegroundColor Gray

# Create output directory if it doesn't exist
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "✓ Created output directory: $OutputDir" -ForegroundColor Green
}

# If source doesn't exist, create a placeholder SVG
if (!(Test-Path $SourceImage) -or $CreatePlaceholder) {
    Write-Host "⚠ Source image not found. Creating placeholder logo..." -ForegroundColor Yellow
    
    $placeholderSVG = @"
<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
  <!-- Barber Pole Background -->
  <defs>
    <linearGradient id="poleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#c41e3a;stop-opacity:1" />
      <stop offset="33%" style="stop-color:#ffffff;stop-opacity:1" />
      <stop offset="66%" style="stop-color:#1e40af;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#c41e3a;stop-opacity:1" />
    </linearGradient>
    <pattern id="stripes" width="40" height="40" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="20" height="40" fill="#c41e3a"/>
      <rect x="20" width="20" height="40" fill="#ffffff"/>
    </pattern>
  </defs>
  
  <!-- Background Circle -->
  <circle cx="256" cy="256" r="240" fill="#1e40af"/>
  
  <!-- Barber Pole -->
  <rect x="200" y="100" width="112" height="312" rx="56" fill="url(#stripes)"/>
  
  <!-- Gold Top Cap -->
  <ellipse cx="256" cy="100" rx="70" ry="20" fill="#FFD700"/>
  <rect x="186" y="100" width="140" height="20" fill="#FFD700"/>
  
  <!-- Gold Bottom Cap -->
  <ellipse cx="256" cy="412" rx="70" ry="20" fill="#FFD700"/>
  <rect x="186" y="392" width="140" height="20" fill="#FFD700"/>
  
  <!-- Letter B -->
  <text x="256" y="480" font-family="Arial, sans-serif" font-size="120" font-weight="bold" fill="#FFD700" text-anchor="middle">B</text>
</svg>
"@
    
    $svgPath = "assets\images\logo-source.svg"
    $placeholderSVG | Out-File -FilePath $svgPath -Encoding UTF8
    Write-Host "✓ Created placeholder SVG: $svgPath" -ForegroundColor Green
    
    # Convert SVG to PNG using ImageMagick
    $pngPath = "assets\images\logo-source.png"
    & magick convert -background none -density 300 $svgPath -resize 1024x1024 $pngPath
    
    if (Test-Path $pngPath) {
        $SourceImage = $pngPath
        Write-Host "✓ Converted to PNG: $pngPath" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to convert SVG to PNG" -ForegroundColor Red
        exit 1
    }
}

# Verify source image exists
if (!(Test-Path $SourceImage)) {
    Write-Host "✗ Error: Source image not found: $SourceImage" -ForegroundColor Red
    Write-Host "  Please provide a high-resolution logo (1024x1024 recommended)" -ForegroundColor Yellow
    Write-Host "  Usage: .\generate-pwa-icons.ps1 -SourceImage 'path\to\your\logo.png'" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n📱 Generating PWA Icons..." -ForegroundColor Cyan

# Generate PWA icons
foreach ($size in $iconSizes) {
    $outputFile = Join-Path $OutputDir "icon-$size.png"
    
    try {
        & magick convert $SourceImage -resize "${size}x${size}" -background none -gravity center -extent "${size}x${size}" $outputFile
        
        if (Test-Path $outputFile) {
            $fileSize = [math]::Round((Get-Item $outputFile).Length / 1KB, 1)
            Write-Host "  ✓ icon-$size.png ($fileSize KB)" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Failed to create icon-$size.png" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ✗ Error creating icon-$size.png: $_" -ForegroundColor Red
    }
}

Write-Host "`n🍎 Generating Apple Touch Icons..." -ForegroundColor Cyan

# Generate Apple touch icons
foreach ($size in $appleSizes) {
    $outputFile = Join-Path $OutputDir "apple-touch-icon-$size.png"
    
    try {
        & magick convert $SourceImage -resize "${size}x${size}" -background none -gravity center -extent "${size}x${size}" $outputFile
        
        if (Test-Path $outputFile) {
            $fileSize = [math]::Round((Get-Item $outputFile).Length / 1KB, 1)
            Write-Host "  ✓ apple-touch-icon-$size.png ($fileSize KB)" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ✗ Error creating apple-touch-icon-$size.png: $_" -ForegroundColor Red
    }
}

# Create default apple-touch-icon.png (180x180)
$defaultAppleIcon = Join-Path $OutputDir "apple-touch-icon.png"
Copy-Item -Path (Join-Path $OutputDir "apple-touch-icon-180.png") -Destination $defaultAppleIcon -Force
Write-Host "  ✓ apple-touch-icon.png (default)" -ForegroundColor Green

Write-Host "`n🌐 Generating Favicons..." -ForegroundColor Cyan

# Generate favicons
foreach ($size in $faviconSizes) {
    $outputFile = Join-Path $OutputDir "favicon-$size.png"
    
    try {
        & magick convert $SourceImage -resize "${size}x${size}" -background none -gravity center -extent "${size}x${size}" $outputFile
        
        if (Test-Path $outputFile) {
            $fileSize = [math]::Round((Get-Item $outputFile).Length / 1KB, 1)
            Write-Host "  ✓ favicon-$size.png ($fileSize KB)" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ✗ Error creating favicon-$size.png: $_" -ForegroundColor Red
    }
}

# Generate favicon.ico (multi-resolution)
$icoFile = "favicon.ico"
try {
    & magick convert (Join-Path $OutputDir "favicon-16.png") (Join-Path $OutputDir "favicon-32.png") $icoFile
    
    if (Test-Path $icoFile) {
        $fileSize = [math]::Round((Get-Item $icoFile).Length / 1KB, 1)
        Write-Host "  ✓ favicon.ico ($fileSize KB)" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Error creating favicon.ico: $_" -ForegroundColor Red
}

Write-Host "`n✅ Icon generation complete!" -ForegroundColor Green
Write-Host "`nGenerated files:" -ForegroundColor Cyan
Write-Host "  • PWA Icons: 8 sizes (72px - 512px)" -ForegroundColor Gray
Write-Host "  • Apple Touch Icons: 4 files (152px, 167px, 180px + default)" -ForegroundColor Gray
Write-Host "  • Favicons: 3 files (16px, 32px, favicon.ico)" -ForegroundColor Gray

Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Verify icons in: $OutputDir" -ForegroundColor Gray
Write-Host "  2. Update manifest.json paths if needed" -ForegroundColor Gray
Write-Host "  3. Test PWA install on mobile device" -ForegroundColor Gray
Write-Host "  4. Run: .\generate-social-images.ps1`n" -ForegroundColor Gray

Get-ChildItem "$outputDir\icon-*.png" | ForEach-Object {
    $sizeKB = "{0:N0} KB" -f ($_.Length / 1KB)
    Write-Output "  ✅ $($_.Name) ($sizeKB)"
}

Write-Output "`n🎉 Ready for PWA packaging!`n"
