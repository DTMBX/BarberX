# 🚀 GO LIVE CHECKLIST - Tillerstead.com
# Run this step-by-step to deploy your site

Write-Host "`n🚀 TILLERSTEAD.COM - GO LIVE DEPLOYMENT" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: VERIFY LOCAL BUILD
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "`n📦 STEP 1: Verify Local Build" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────" -ForegroundColor Gray

Write-Host "Building Jekyll site locally..." -ForegroundColor Yellow
$buildOutput = bundle exec jekyll build 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Jekyll build successful!" -ForegroundColor Green
    
    # Check for _site directory
    if (Test-Path "_site/index.html") {
        $size = (Get-Item "_site/index.html").Length
        Write-Host "✅ Homepage exists ($([math]::Round($size/1KB, 1)) KB)" -ForegroundColor Green
    }
    
    # Check for _redirects
    if (Test-Path "_site/_redirects") {
        $redirectCount = (Get-Content "_site/_redirects" | Where-Object { $_ -match "^/" }).Count
        Write-Host "✅ Redirects file ready ($redirectCount rules)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Copying _redirects to _site..." -ForegroundColor Yellow
        Copy-Item "_redirects" "_site/_redirects" -Force
        Write-Host "✅ Redirects copied" -ForegroundColor Green
    }
} else {
    Write-Host "❌ Build failed! Fix errors before deploying." -ForegroundColor Red
    Write-Host $buildOutput -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Step 1 Complete - Site ready to deploy!" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to continue to Step 2"

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: GITHUB STATUS CHECK
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "`n📤 STEP 2: GitHub Status" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────" -ForegroundColor Gray

$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "⚠️  Uncommitted changes detected:" -ForegroundColor Yellow
    git status --short
    Write-Host "`nCommit these before going live? (recommended)" -ForegroundColor Yellow
    $commit = Read-Host "Commit now? (y/n)"
    
    if ($commit -eq 'y') {
        git add -A
        $message = Read-Host "Commit message (or press Enter for default)"
        if (-not $message) { $message = "Pre-deployment commit: Going live!" }
        git commit -m $message
        git push origin main
        Write-Host "✅ Changes committed and pushed!" -ForegroundColor Green
    }
} else {
    Write-Host "✅ All changes committed" -ForegroundColor Green
}

$currentBranch = git branch --show-current
$remoteUrl = git config --get remote.origin.url

Write-Host "✅ Current branch: $currentBranch" -ForegroundColor Green
Write-Host "✅ GitHub repo: $remoteUrl" -ForegroundColor Green

Write-Host "`n✅ Step 2 Complete - Code is on GitHub!" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to continue to Step 3"

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: NETLIFY DEPLOYMENT INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "`n🌐 STEP 3: Deploy to Netlify" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────" -ForegroundColor Gray

Write-Host "`n🔗 Opening Netlify in your browser..." -ForegroundColor Yellow
Start-Process "https://app.netlify.com"

Write-Host "`n📋 FOLLOW THESE STEPS IN NETLIFY:" -ForegroundColor Yellow -BackgroundColor DarkYellow
Write-Host ""
Write-Host "1️⃣  Click 'Add new site' → 'Import an existing project'" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  Choose 'GitHub' as your Git provider" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣  Authorize Netlify to access your GitHub (if not already)" -ForegroundColor White
Write-Host ""
Write-Host "4️⃣  Search for and select: 'Tillerstead.com'" -ForegroundColor White
Write-Host ""
Write-Host "5️⃣  Configure build settings (COPY EXACTLY):" -ForegroundColor White
Write-Host "    ┌─────────────────────────────────────────────┐" -ForegroundColor Gray
Write-Host "    │ Branch to deploy:  main                     │" -ForegroundColor Cyan
Write-Host "    │ Build command:     bundle exec jekyll build │" -ForegroundColor Cyan
Write-Host "    │ Publish directory: _site                    │" -ForegroundColor Cyan
Write-Host "    └─────────────────────────────────────────────┘" -ForegroundColor Gray
Write-Host ""
Write-Host "6️⃣  Click 'Show advanced' → 'New variable' and add:" -ForegroundColor White
Write-Host "    • RUBY_VERSION = 3.4.0" -ForegroundColor Cyan
Write-Host "    • JEKYLL_ENV = production" -ForegroundColor Cyan
Write-Host ""
Write-Host "7️⃣  Click 'Deploy site'" -ForegroundColor White
Write-Host ""
Write-Host "8️⃣  Wait 2-3 minutes for build to complete" -ForegroundColor White
Write-Host ""

Write-Host "Have you completed the Netlify setup above?" -ForegroundColor Yellow
$netlifyDone = Read-Host "Type 'yes' when deployed"

if ($netlifyDone -eq 'yes') {
    Write-Host "`n✅ Step 3 Complete - Site deployed to Netlify!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Complete Netlify setup before continuing" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Read-Host "Press Enter to continue to Step 4"

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: CONFIGURE CUSTOM DOMAIN
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "`n🌍 STEP 4: Add Custom Domain (tillerstead.com)" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────" -ForegroundColor Gray

Write-Host "`n📋 IN NETLIFY DASHBOARD:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Go to: Site settings → Domain management" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  Click 'Add custom domain'" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣  Enter: tillerstead.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "4️⃣  Click 'Verify' then 'Add domain'" -ForegroundColor White
Write-Host ""
Write-Host "5️⃣  Choose DNS setup:" -ForegroundColor White
Write-Host "    • RECOMMENDED: Use Netlify DNS (easiest)" -ForegroundColor Green
Write-Host "    • MANUAL: Use external DNS (requires manual setup)" -ForegroundColor Yellow
Write-Host ""

$dnsChoice = Read-Host "Using Netlify DNS or External DNS? (netlify/external)"

if ($dnsChoice -eq 'netlify') {
    Write-Host "`n📋 NETLIFY DNS SETUP:" -ForegroundColor Yellow
    Write-Host "1. Follow Netlify wizard to get nameservers" -ForegroundColor White
    Write-Host "2. Go to your domain registrar (GoDaddy, Namecheap, etc.)" -ForegroundColor White
    Write-Host "3. Update nameservers to Netlify's nameservers" -ForegroundColor White
    Write-Host "4. Wait 24-48 hours for DNS propagation" -ForegroundColor White
} else {
    Write-Host "`n📋 EXTERNAL DNS SETUP:" -ForegroundColor Yellow
    Write-Host "In your DNS provider, add these records:" -ForegroundColor White
    Write-Host "  A       @       75.2.60.5" -ForegroundColor Cyan
    Write-Host "  CNAME   www     [your-site].netlify.app" -ForegroundColor Cyan
}

Write-Host ""
Read-Host "Press Enter to continue to Step 5"

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5: ENABLE HTTPS
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "`n🔒 STEP 5: Enable HTTPS" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────" -ForegroundColor Gray

Write-Host "`n📋 IN NETLIFY DASHBOARD:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Go to: Site settings → Domain management → HTTPS" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  Wait for domain to verify (may take a few minutes)" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣  Click 'Verify DNS configuration'" -ForegroundColor White
Write-Host ""
Write-Host "4️⃣  Click 'Provision certificate' (free Let's Encrypt)" -ForegroundColor White
Write-Host ""
Write-Host "5️⃣  Wait 1-2 minutes for certificate" -ForegroundColor White
Write-Host ""
Write-Host "6️⃣  Enable 'Force HTTPS' toggle" -ForegroundColor White
Write-Host ""

Write-Host "✅ Step 5 Complete - HTTPS enabled!" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to continue to Step 6"

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6: VERIFY DEPLOYMENT
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "`n✅ STEP 6: Verify Your Live Site" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────" -ForegroundColor Gray

Write-Host "`n🔗 Opening your site..." -ForegroundColor Yellow

# Try to open the site
Start-Process "https://tillerstead.com"

Write-Host "`n📋 CHECK THESE:" -ForegroundColor Yellow
Write-Host "  □ Homepage loads correctly" -ForegroundColor White
Write-Host "  □ No 404 errors" -ForegroundColor White
Write-Host "  □ HTTPS (green lock) in browser" -ForegroundColor White
Write-Host "  □ Test a redirect: https://tillerstead.com/contact.html" -ForegroundColor White
Write-Host "  □ Images load properly" -ForegroundColor White
Write-Host "  □ Navigation works" -ForegroundColor White
Write-Host "  □ Forms display correctly" -ForegroundColor White
Write-Host "  □ Mobile responsive (resize browser)" -ForegroundColor White
Write-Host ""

$allGood = Read-Host "Does everything look good? (yes/no)"

if ($allGood -eq 'yes') {
    Write-Host "`n🎉 CONGRATULATIONS! YOU'RE LIVE!" -ForegroundColor Green -BackgroundColor DarkGreen
    Write-Host ""
    Write-Host "✅ Site deployed: https://tillerstead.com" -ForegroundColor Green
    Write-Host "✅ HTTPS enabled" -ForegroundColor Green
    Write-Host "✅ Custom domain active" -ForegroundColor Green
    Write-Host "✅ 404 prevention active" -ForegroundColor Green
    Write-Host "✅ Auto-deploy on git push" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "  • Test all pages and links" -ForegroundColor White
    Write-Host "  • Run Lighthouse audit" -ForegroundColor White
    Write-Host "  • Submit sitemap to Google Search Console" -ForegroundColor White
    Write-Host "  • Set up Netlify form notifications" -ForegroundColor White
    Write-Host "  • Monitor analytics" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 FUTURE DEPLOYMENTS:" -ForegroundColor Yellow
    Write-Host "   Just push to GitHub - Netlify auto-deploys!" -ForegroundColor White
    Write-Host "   git add ." -ForegroundColor Gray
    Write-Host "   git commit -m 'Your changes'" -ForegroundColor Gray
    Write-Host "   git push origin main" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "`n⚠️  Issues detected. Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  • Check Netlify deploy logs for errors" -ForegroundColor White
    Write-Host "  • Verify DNS propagation: https://www.whatsmydns.net" -ForegroundColor White
    Write-Host "  • Clear browser cache and try again" -ForegroundColor White
    Write-Host "  • Check Netlify status: https://www.netlifystatus.com" -ForegroundColor White
}

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "🚀 DEPLOYMENT SCRIPT COMPLETE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
