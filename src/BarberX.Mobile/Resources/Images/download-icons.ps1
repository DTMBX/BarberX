# Download Material Design Icons for Evident Mobile App
# This script downloads free Material Design icons from Google Fonts

$icons = @{
    "home" = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/home/default/48px.svg"
    "folder" = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/folder/default/48px.svg"
    "chart" = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/analytics/default/48px.svg"
    "upload" = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/upload/default/48px.svg"
    "person" = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/person/default/48px.svg"
    "book" = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/book/default/48px.svg"
    "document" = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/description/default/48px.svg"
    "settings" = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/settings/default/48px.svg"
    "help" = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/help/default/48px.svg"
    "logout" = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/logout/default/48px.svg"
    "video" = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/videocam/default/48px.svg"
    "chevron_right" = "https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/chevron_right/default/48px.svg"
}

Write-Host "Downloading Material Design icons..." -ForegroundColor Cyan

foreach ($icon in $icons.GetEnumerator()) {
    $filename = "$($icon.Key).svg"
    $filepath = Join-Path $PSScriptRoot $filename
    
    try {
        Write-Host "Downloading $filename..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $icon.Value -OutFile $filepath
        Write-Host "✅ $filename downloaded" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to download $filename : $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Icon download complete!" -ForegroundColor Green
Write-Host "Note: You still need to add:" -ForegroundColor Yellow
Write-Host "  - Evident_logo.png (your custom logo)" -ForegroundColor White
Write-Host "  - case_placeholder.png" -ForegroundColor White
Write-Host "  - default_avatar.png" -ForegroundColor White
