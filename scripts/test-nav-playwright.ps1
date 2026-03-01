#!/usr/bin/env pwsh
# Playwright Navigation Test Runner
# Tests all navigation links on desktop and mobile

param(
    [string]$Environment = "prod",  # "local" or "prod"
    [string]$Browser = "all",       # "chrome", "firefox", "safari", "mobile", or "all"
    [switch]$Headed,                # Run with browser UI visible
    [switch]$Debug                  # Run in debug mode
)

$ErrorActionPreference = "Continue"
Set-Location "C:\web-dev\github-repos\Tillerstead.com"

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🎭 PLAYWRIGHT NAVIGATION TESTS                       ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Set environment
if ($Environment -eq "local") {
    $env:BASE_URL = "http://localhost:4000"
    Write-Host "🌐 Testing: LOCAL (http://localhost:4000)" -ForegroundColor Yellow
    Write-Host "⚠️  Make sure Jekyll is running: bundle exec jekyll serve" -ForegroundColor Yellow
} else {
    $env:BASE_URL = "https://tillerstead.com"
    Write-Host "🌐 Testing: PRODUCTION (https://tillerstead.com)" -ForegroundColor Green
}

Write-Host ""

# Determine which browsers to test
$projects = @()

switch ($Browser) {
    "chrome" {
        $projects = @("chromium-desktop")
        Write-Host "🌐 Browsers: Chrome Desktop" -ForegroundColor Cyan
    }
    "firefox" {
        $projects = @("firefox-desktop")
        Write-Host "🌐 Browsers: Firefox Desktop" -ForegroundColor Cyan
    }
    "safari" {
        $projects = @("webkit-desktop")
        Write-Host "🌐 Browsers: Safari Desktop" -ForegroundColor Cyan
    }
    "mobile" {
        $projects = @("mobile-chrome-iphone-16-pro-max", "mobile-safari-iphone-14", "mobile-chrome-pixel-7")
        Write-Host "🌐 Browsers: All Mobile Devices" -ForegroundColor Cyan
    }
    "all" {
        # Run all tests
        Write-Host "🌐 Browsers: ALL (Desktop + Mobile)" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "📋 Test Suite: Navigation Links" -ForegroundColor Cyan
Write-Host "  • Desktop nav links" -ForegroundColor Gray
Write-Host "  • Mobile nav drawer" -ForegroundColor Gray
Write-Host "  • Dropdown menus" -ForegroundColor Gray
Write-Host "  • Accordion menus" -ForegroundColor Gray
Write-Host "  • Accessibility" -ForegroundColor Gray
Write-Host "  • Responsive breakpoints" -ForegroundColor Gray
Write-Host ""

# Build command
$cmd = "npx playwright test tests/navigation.spec.js"

if ($projects.Count -gt 0) {
    $projectArgs = ($projects | ForEach-Object { "--project=$_" }) -join " "
    $cmd += " $projectArgs"
}

if ($Headed) {
    $cmd += " --headed"
    Write-Host "👀 Mode: Headed (browser visible)" -ForegroundColor Yellow
} else {
    Write-Host "🚀 Mode: Headless (no browser UI)" -ForegroundColor Gray
}

if ($Debug) {
    $cmd += " --debug"
    Write-Host "🐛 Mode: Debug (step through)" -ForegroundColor Magenta
}

Write-Host ""
Write-Host "▶️  Running tests..." -ForegroundColor Green
Write-Host ""

# Run tests
Invoke-Expression $cmd

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "✅ ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 View HTML Report:" -ForegroundColor Cyan
    Write-Host "  npx playwright show-report" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ SOME TESTS FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "📊 View Failure Report:" -ForegroundColor Yellow
    Write-Host "  npx playwright show-report" -ForegroundColor White
    Write-Host ""
    Write-Host "🔍 Debug Failed Tests:" -ForegroundColor Yellow
    Write-Host "  .\scripts\test-nav-playwright.ps1 -Debug" -ForegroundColor White
    Write-Host ""
}

Write-Host "📁 Test Results:" -ForegroundColor Cyan
Write-Host "  • HTML Report: playwright-report/html/index.html" -ForegroundColor Gray
Write-Host "  • JSON Results: playwright-report/results.json" -ForegroundColor Gray
Write-Host "  • Screenshots: test-results/" -ForegroundColor Gray
Write-Host "  • Videos: test-results/" -ForegroundColor Gray
Write-Host ""

exit $exitCode
