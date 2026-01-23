# PowerShell Netlify Deployment Script for BarberX.info
# Quick deployment for Windows

Write-Host "🚀 BarberX.info - Netlify Deployment" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Netlify CLI is installed
$netlifyInstalled = Get-Command netlify -ErrorAction SilentlyContinue
if (-not $netlifyInstalled) {
    Write-Host "❌ Netlify CLI not found. Installing..." -ForegroundColor Red
    npm install -g netlify-cli
    Write-Host "✅ Netlify CLI installed" -ForegroundColor Green
} else {
    Write-Host "✅ Netlify CLI already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "📋 Pre-deployment checklist:" -ForegroundColor Yellow

# Check if bundle is installed
$bundleInstalled = Get-Command bundle -ErrorAction SilentlyContinue
if (-not $bundleInstalled) {
    Write-Host "  ❌ Ruby/Bundler not found. Please install Ruby first." -ForegroundColor Red
    Write-Host "     Download from: https://rubyinstaller.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "  1. Installing Ruby dependencies..."
bundle install | Out-Null
Write-Host "  ✅ Bundle install complete" -ForegroundColor Green

Write-Host "  2. Testing local Jekyll build..."
$buildResult = bundle exec jekyll build 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Jekyll build successful" -ForegroundColor Green
} else {
    Write-Host "  ❌ Jekyll build failed. Fix errors before deploying:" -ForegroundColor Red
    Write-Host $buildResult -ForegroundColor Red
    exit 1
}

Write-Host "  3. Checking Git status..."
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "  ⚠️  You have uncommitted changes" -ForegroundColor Yellow
    $commit = Read-Host "     Commit them before deploying? (y/n)"
    if ($commit -eq "y") {
        git add .
        $commitMsg = Read-Host "     Enter commit message"
        git commit -m "$commitMsg"
        git push origin main
        Write-Host "  ✅ Changes committed and pushed" -ForegroundColor Green
    }
} else {
    Write-Host "  ✅ Git working directory clean" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Ready to deploy!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose deployment option:" -ForegroundColor Yellow
Write-Host "  1. Deploy to PRODUCTION (--prod)"
Write-Host "  2. Deploy PREVIEW (draft)"
Write-Host "  3. Initialize new site"
Write-Host "  4. Login to Netlify"
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "Deploying to PRODUCTION..." -ForegroundColor Green
        netlify deploy --prod
    }
    "2" {
        Write-Host "Creating PREVIEW deployment..." -ForegroundColor Yellow
        netlify deploy
    }
    "3" {
        Write-Host "Initializing new Netlify site..." -ForegroundColor Cyan
        netlify init
    }
    "4" {
        Write-Host "Opening Netlify login..." -ForegroundColor Cyan
        netlify login
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Opening your site..." -ForegroundColor Cyan
netlify open:site
