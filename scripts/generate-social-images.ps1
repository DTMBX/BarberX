# Social Media Image Generator for Evident
# Requires: ImageMagick installed
# Generates Open Graph and Twitter Card images

param(
    [string]$OutputDir = "assets\images",
    [switch]$UseTemplate
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== Evident Social Media Image Generator ===" -ForegroundColor Cyan

# Create output directory if it doesn't exist
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

Write-Host "`n📱 Generating Social Media Images..." -ForegroundColor Cyan

# Open Graph Image (1200x630)
Write-Host "`n1. Creating Open Graph Image (1200×630)..." -ForegroundColor Yellow

$ogSVG = @"
<svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
  <!-- Background Gradient -->
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1e40af;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#c41e3a;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1e40af;stop-opacity:1" />
    </linearGradient>
    <pattern id="stripes" width="40" height="40" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="20" height="40" fill="#c41e3a"/>
      <rect x="20" width="20" height="40" fill="#ffffff"/>
    </pattern>
  </defs>
  
  <!-- Background -->
  <rect width="1200" height="630" fill="url(#bgGradient)"/>
  
  <!-- Overlay -->
  <rect width="1200" height="630" fill="#000000" opacity="0.3"/>
  
  <!-- Barber Pole (Left) -->
  <rect x="50" y="150" width="80" height="330" rx="40" fill="url(#stripes)"/>
  <ellipse cx="90" cy="150" rx="50" ry="15" fill="#FFD700"/>
  <ellipse cx="90" cy="480" rx="50" ry="15" fill="#FFD700"/>
  
  <!-- Main Content Box -->
  <rect x="200" y="100" width="950" height="430" rx="20" fill="#ffffff" opacity="0.95"/>
  
  <!-- Title -->
  <text x="600" y="220" font-family="Arial, sans-serif" font-size="72" font-weight="bold" fill="#1e40af" text-anchor="middle">Evident</text>
  
  <!-- Subtitle -->
  <text x="600" y="300" font-family="Arial, sans-serif" font-size="36" fill="#c41e3a" text-anchor="middle">Legal Video Analysis</text>
  
  <!-- Tagline -->
  <text x="600" y="380" font-family="Arial, sans-serif" font-size="28" fill="#4b5563" text-anchor="middle">Professional Forensic Tools for Legal Professionals</text>
  
  <!-- Features -->
  <text x="280" y="460" font-family="Arial, sans-serif" font-size="22" fill="#1e40af" font-weight="600">✓ AI-Powered Analysis</text>
  <text x="580" y="460" font-family="Arial, sans-serif" font-size="22" fill="#1e40af" font-weight="600">✓ Evidence Management</text>
  <text x="900" y="460" font-family="Arial, sans-serif" font-size="22" fill="#1e40af" font-weight="600">✓ Secure Platform</text>
  
  <!-- URL -->
  <text x="600" y="510" font-family="Arial, sans-serif" font-size="24" fill="#6b7280" text-anchor="middle">Evident.info</text>
</svg>
"@

$ogSVGPath = Join-Path $OutputDir "og-image.svg"
$ogPNGPath = Join-Path $OutputDir "og-image.png"
$ogJPGPath = Join-Path $OutputDir "og-image.jpg"

$ogSVG | Out-File -FilePath $ogSVGPath -Encoding UTF8
Write-Host "  ✓ Created SVG template: og-image.svg" -ForegroundColor Green

& magick convert -background none -density 150 $ogSVGPath -quality 90 $ogJPGPath

if (Test-Path $ogJPGPath) {
    $fileSize = [math]::Round((Get-Item $ogJPGPath).Length / 1KB, 1)
    Write-Host "  ✓ og-image.jpg (1200×630, $fileSize KB)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to create og-image.jpg" -ForegroundColor Red
}

# Twitter Card Image (1200x675)
Write-Host "`n2. Creating Twitter Card Image (1200×675)..." -ForegroundColor Yellow

$twitterSVG = @"
<svg width="1200" height="675" xmlns="http://www.w3.org/2000/svg">
  <!-- Background Gradient -->
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#c41e3a;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#1e40af;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#c41e3a;stop-opacity:1" />
    </linearGradient>
    <pattern id="stripes" width="40" height="40" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="20" height="40" fill="#c41e3a"/>
      <rect x="20" width="20" height="40" fill="#ffffff"/>
    </pattern>
  </defs>
  
  <!-- Background -->
  <rect width="1200" height="675" fill="url(#bgGradient)"/>
  
  <!-- Overlay -->
  <rect width="1200" height="675" fill="#000000" opacity="0.4"/>
  
  <!-- Main Content Box -->
  <rect x="100" y="100" width="1000" height="475" rx="25" fill="#ffffff" opacity="0.95"/>
  
  <!-- Logo/Icon Area -->
  <circle cx="250" cy="300" r="100" fill="#1e40af"/>
  <text x="250" y="340" font-family="Arial, sans-serif" font-size="100" font-weight="bold" fill="#FFD700" text-anchor="middle">B</text>
  
  <!-- Title -->
  <text x="650" y="220" font-family="Arial, sans-serif" font-size="64" font-weight="bold" fill="#1e40af" text-anchor="middle">Evident</text>
  
  <!-- Subtitle -->
  <text x="650" y="300" font-family="Arial, sans-serif" font-size="32" fill="#c41e3a" text-anchor="middle">Legal Video Analysis Platform</text>
  
  <!-- Value Proposition -->
  <text x="650" y="380" font-family="Arial, sans-serif" font-size="26" fill="#4b5563" text-anchor="middle">Transform video evidence into courtroom clarity</text>
  
  <!-- Stats/Features -->
  <text x="450" y="470" font-family="Arial, sans-serif" font-size="22" fill="#1e40af" font-weight="600">⚡ AI-Powered</text>
  <text x="650" y="470" font-family="Arial, sans-serif" font-size="22" fill="#1e40af" font-weight="600">🔒 Secure</text>
  <text x="850" y="470" font-family="Arial, sans-serif" font-size="22" fill="#1e40af" font-weight="600">📊 Professional</text>
  
  <!-- CTA -->
  <rect x="500" y="510" width="300" height="50" rx="25" fill="#c41e3a"/>
  <text x="650" y="545" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#ffffff" text-anchor="middle">Get Started Free</text>
</svg>
"@

$twitterSVGPath = Join-Path $OutputDir "twitter-card.svg"
$twitterJPGPath = Join-Path $OutputDir "twitter-card.jpg"

$twitterSVG | Out-File -FilePath $twitterSVGPath -Encoding UTF8
Write-Host "  ✓ Created SVG template: twitter-card.svg" -ForegroundColor Green

& magick convert -background none -density 150 $twitterSVGPath -quality 90 $twitterJPGPath

if (Test-Path $twitterJPGPath) {
    $fileSize = [math]::Round((Get-Item $twitterJPGPath).Length / 1KB, 1)
    Write-Host "  ✓ twitter-card.jpg (1200×675, $fileSize KB)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to create twitter-card.jpg" -ForegroundColor Red
}

# Verify dimensions
Write-Host "`n🔍 Verifying Image Dimensions..." -ForegroundColor Cyan

if (Test-Path $ogJPGPath) {
    $ogInfo = & magick identify -format "%wx%h %b" $ogJPGPath
    Write-Host "  Open Graph: $ogInfo" -ForegroundColor Gray
}

if (Test-Path $twitterJPGPath) {
    $twitterInfo = & magick identify -format "%wx%h %b" $twitterJPGPath
    Write-Host "  Twitter Card: $twitterInfo" -ForegroundColor Gray
}

Write-Host "`n✅ Social media image generation complete!" -ForegroundColor Green

Write-Host "`n📋 Generated Files:" -ForegroundColor Cyan
Write-Host "  • og-image.jpg (1200×630) - Facebook, LinkedIn" -ForegroundColor Gray
Write-Host "  • twitter-card.jpg (1200×675) - Twitter" -ForegroundColor Gray
Write-Host "  • SVG templates for customization" -ForegroundColor Gray

Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review images in: $OutputDir" -ForegroundColor Gray
Write-Host "  2. Customize SVG templates if needed (edit .svg files)" -ForegroundColor Gray
Write-Host "  3. Re-run script to regenerate from edited SVGs" -ForegroundColor Gray
Write-Host "  4. Update structured-data.html paths if needed" -ForegroundColor Gray
Write-Host "  5. Test social sharing on Twitter/Facebook`n" -ForegroundColor Gray

Write-Host "🎨 Customization Tips:" -ForegroundColor Magenta
Write-Host "  • Edit .svg files in any text editor" -ForegroundColor Gray
Write-Host "  • Change colors, text, layout as needed" -ForegroundColor Gray
Write-Host "  • Run script again to convert to JPG" -ForegroundColor Gray
Write-Host "  • Use Figma/Canva for advanced designs`n" -ForegroundColor Gray
