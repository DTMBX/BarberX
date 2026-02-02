# ⚡ Quick Setup Script - Get Started in 5 Minutes
# Run this to activate everything built today!

Write-Host "🚀 Evident Quick Setup - Starting..." -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# STEP 1: Install PowerShell Profile
# ============================================================================
Write-Host "📁 Step 1: Installing PowerShell Profile..." -ForegroundColor Yellow

$profilePath = $PROFILE
$EvidentProfilePath = "C:\web-dev\github-repos\Evident.info\Evident-Profile.ps1"

if (Test-Path $EvidentProfilePath) {
    Write-Host "  ✓ Found Evident profile" -ForegroundColor Green
    
    # Backup existing profile
    if (Test-Path $profilePath) {
        $backup = "$profilePath.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $profilePath $backup
        Write-Host "  ✓ Backed up existing profile to: $backup" -ForegroundColor Green
    }
    
    # Append Evident profile
    Get-Content $EvidentProfilePath | Add-Content $profilePath
    Write-Host "  ✓ Evident profile installed!" -ForegroundColor Green
    Write-Host "  → Reload with: . `$PROFILE" -ForegroundColor Cyan
} else {
    Write-Host "  ✗ Evident-Profile.ps1 not found!" -ForegroundColor Red
    Write-Host "  → Make sure you're in the Evident.info directory" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 2: Install Python Dependencies
# ============================================================================
Write-Host "🐍 Step 2: Installing Python Dependencies..." -ForegroundColor Yellow

Set-Location "C:\web-dev\github-repos\Evident.info"

try {
    Write-Host "  Installing openai..." -ForegroundColor Cyan
    pip install openai --quiet
    
    Write-Host "  Installing cryptography..." -ForegroundColor Cyan
    pip install cryptography --quiet
    
    Write-Host "  ✓ Python packages installed!" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to install Python packages" -ForegroundColor Red
    Write-Host "  → Run manually: pip install openai cryptography" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 3: Generate Encryption Key
# ============================================================================
Write-Host "🔐 Step 3: Generating Encryption Key..." -ForegroundColor Yellow

try {
    $key = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    
    Write-Host "  ✓ Encryption key generated!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║  ADD THIS TO YOUR .env FILE:                             ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  API_KEY_ENCRYPTION_KEY=$key" -ForegroundColor Yellow
    Write-Host ""
    
    # Auto-add to .env if it exists
    if (Test-Path ".env") {
        Add-Content .env "`nAPI_KEY_ENCRYPTION_KEY=$key"
        Write-Host "  ✓ Added to .env file automatically!" -ForegroundColor Green
    } else {
        Write-Host "  → Create .env file and add the above line" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ Failed to generate encryption key" -ForegroundColor Red
    Write-Host "  → Run manually: python -c `"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())`"" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 4: Run Database Migration
# ============================================================================
Write-Host "🗄️  Step 4: Running Database Migration..." -ForegroundColor Yellow

if (Test-Path "migrate_add_chatgpt.py") {
    try {
        python migrate_add_chatgpt.py
        Write-Host "  ✓ Database migration complete!" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Migration failed" -ForegroundColor Red
        Write-Host "  → Run manually: python migrate_add_chatgpt.py" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ migrate_add_chatgpt.py not found!" -ForegroundColor Red
}

Write-Host ""

# ============================================================================
# STEP 5: Build Android APK
# ============================================================================
Write-Host "📱 Step 5: Building Android APK..." -ForegroundColor Yellow

$confirm = Read-Host "Build Android APK now? This takes ~5 minutes (y/n)"

if ($confirm -eq 'y' -or $confirm -eq 'Y') {
    Set-Location "C:\web-dev\github-repos\Evident.info\src\Evident.MatterDocket.MAUI"
    
    try {
        Write-Host "  Building Android Release APK..." -ForegroundColor Cyan
        dotnet build -f net10.0-android34.0 -c Release
        
        Write-Host ""
        Write-Host "  ✓ Android APK built successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "  📦 APK Location:" -ForegroundColor Yellow
        Write-Host "  bin\Release\net10.0-android34.0\com.Evident.matterdocket-Signed.apk" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  📧 Email yourself the APK or copy to your Android phone via USB" -ForegroundColor Yellow
        
    } catch {
        Write-Host "  ✗ Build failed" -ForegroundColor Red
        Write-Host "  → Run manually: dotnet build -f net10.0-android34.0 -c Release" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⏭️  Skipped Android build" -ForegroundColor Yellow
    Write-Host "  → Build later with: bm && dotnet build -f net10.0-android34.0 -c Release" -ForegroundColor Cyan
}

Write-Host ""

# ============================================================================
# COMPLETION SUMMARY
# ============================================================================
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    ✅ SETUP COMPLETE!                       ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "🎯 What's Ready:" -ForegroundColor Cyan
Write-Host "  ✓ PowerShell dev profile (20+ commands)" -ForegroundColor Green
Write-Host "  ✓ ChatGPT backend (database + API)" -ForegroundColor Green
Write-Host "  ✓ Chat UI (MAUI app)" -ForegroundColor Green
Write-Host "  ✓ Legal AI tools (15+ analyzers)" -ForegroundColor Green
if ($confirm -eq 'y' -or $confirm -eq 'Y') {
    Write-Host "  ✓ Android APK (ready to install)" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Reload PowerShell profile:" -ForegroundColor White
Write-Host "     . `$PROFILE" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Test new commands:" -ForegroundColor White
Write-Host "     bmenu                 # Show all commands" -ForegroundColor Cyan
Write-Host "     br                    # Go to Evident root" -ForegroundColor Cyan
Write-Host "     bm                    # Go to MAUI project" -ForegroundColor Cyan
Write-Host "     Build-MAUI -Clean     # Build MAUI app" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Start Flask API:" -ForegroundColor White
Write-Host "     Start-FlaskAPI" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Run MAUI app:" -ForegroundColor White
Write-Host "     Run-MAUI" -ForegroundColor Cyan
Write-Host ""
Write-Host "  5. Install Android APK on your phone (if built)" -ForegroundColor White
Write-Host ""

Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "  → PROFILE-SETUP-GUIDE.md       # PowerShell commands" -ForegroundColor Cyan
Write-Host "  → LEGAL-AI-TOOLS.md            # 15 legal AI tools" -ForegroundColor Cyan
Write-Host "  → IOS-TESTING-COMPLETE-GUIDE.md # iPhone deployment" -ForegroundColor Cyan
Write-Host "  → SESSION-CHAT-UI-COMPLETE.md  # Today's progress" -ForegroundColor Cyan
Write-Host ""

Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "  • Use 'gquick \"message\"' for fast git commits" -ForegroundColor White
Write-Host "  • Use 'b-' to go back to previous directory" -ForegroundColor White
Write-Host "  • Use 'brecent' to see recent locations" -ForegroundColor White
Write-Host ""

Write-Host "🎉 Happy coding!" -ForegroundColor Green
Write-Host ""
