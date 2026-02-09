# Evident - Emergency Credential Scrubber
# Removes sensitive credentials from Git history

Write-Host "`n⚠️  CREDENTIAL SCRUBBER - EMERGENCY SECURITY FIX ⚠️" -ForegroundColor Red
Write-Host "=" * 70

Write-Host "`n📋 This script will:" -ForegroundColor Cyan
Write-Host "  1. Remove sensitive email (SENSITIVE_EMAIL) from ALL git history" -ForegroundColor White
Write-Host "  2. Remove sensitive password (SENSITIVE_PASSWORD) from ALL git history" -ForegroundColor White
Write-Host "  3. Force push to remote (rewrites history)" -ForegroundColor White

Write-Host "`n⚠️  WARNING:" -ForegroundColor Yellow
Write-Host "  • This REWRITES Git history (dangerous)" -ForegroundColor Red
Write-Host "  • All collaborators must re-clone the repo" -ForegroundColor Red
Write-Host "  • Cannot be undone easily" -ForegroundColor Red

$confirm = Read-Host "`nType 'SCRUB NOW' to proceed (or anything else to cancel)"

if ($confirm -ne "SCRUB NOW") {
    Write-Host "`n❌ Cancelled. No changes made." -ForegroundColor Yellow
    exit 0
}

Write-Host "`n🔧 Installing BFG Repo-Cleaner (faster than git-filter-branch)..." -ForegroundColor Cyan

# Check if BFG is installed
if (-not (Get-Command "bfg" -ErrorAction SilentlyContinue)) {
    Write-Host "  • BFG not found. Installing via scoop..." -ForegroundColor Yellow
    
    if (-not (Get-Command "scoop" -ErrorAction SilentlyContinue)) {
        Write-Host "  • Scoop not found. Using git-filter-branch instead..." -ForegroundColor Yellow
        $useBFG = $false
    } else {
        scoop install bfg
        $useBFG = $true
    }
} else {
    $useBFG = $true
}

# Create replacement file for BFG
$replacementFile = "credentials-to-scrub.txt"
@"
SENSITIVE_EMAIL==>REDACTED_EMAIL@example.com
SENSITIVE_PASSWORD==>REDACTED_PASSWORD
SENSITIVE_NAME==>Admin User
"@ | Set-Content $replacementFile

Write-Host "`n🧹 Scrubbing credentials from Git history..." -ForegroundColor Cyan

if ($useBFG) {
    # Use BFG (much faster)
    Write-Host "  • Using BFG Repo-Cleaner (fast method)" -ForegroundColor Green
    bfg --replace-text $replacementFile --no-blob-protection .
    git reflog expire --expire=now --all
    git gc --prune=now --aggressive
} else {
    # Fallback to git-filter-branch
    Write-Host "  • Using git-filter-branch (slow but works)" -ForegroundColor Yellow
    
    git filter-branch --force --index-filter `
        "git ls-files -z | xargs -0 sed -i 's/SENSITIVE_EMAIL/REDACTED@example.com/g; s/SENSITIVE_PASSWORD/REDACTED_PASSWORD/g; s/SENSITIVE_NAME/Admin User/g'" `
        --prune-empty --tag-name-filter cat -- --all
    
    # Clean up
    git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
    git reflog expire --expire=now --all
    git gc --prune=now --aggressive
}

# Remove replacement file
Remove-Item $replacementFile -ErrorAction SilentlyContinue

Write-Host "`n✅ Git history scrubbed locally!" -ForegroundColor Green

Write-Host "`n⚠️  CRITICAL NEXT STEPS:" -ForegroundColor Red
Write-Host "  1. Review changes: git log --all --oneline" -ForegroundColor White
Write-Host "  2. Force push to remote:" -ForegroundColor White
Write-Host "     git push origin --force --all" -ForegroundColor Yellow
Write-Host "     git push origin --force --tags" -ForegroundColor Yellow
Write-Host "  3. Notify all collaborators to re-clone the repo" -ForegroundColor White
Write-Host "  4. Update .env file with new ADMIN_PASSWORD" -ForegroundColor White
Write-Host "  5. Rotate ALL exposed credentials immediately" -ForegroundColor White

Write-Host "`n📧 Email Security Checklist:" -ForegroundColor Cyan
Write-Host "  □ Change password for SENSITIVE_EMAIL" -ForegroundColor White
Write-Host "  □ Enable 2FA on ProtonMail account" -ForegroundColor White
Write-Host "  □ Review ProtonMail access logs" -ForegroundColor White
Write-Host "  □ Check for unauthorized logins" -ForegroundColor White

Write-Host "`n🔐 System Security Checklist:" -ForegroundColor Cyan
Write-Host "  □ Update ADMIN_PASSWORD in production .env" -ForegroundColor White
Write-Host "  □ Rotate database passwords" -ForegroundColor White
Write-Host "  □ Rotate API keys (Stripe, OpenAI, etc.)" -ForegroundColor White
Write-Host "  □ Rotate Flask SECRET_KEY" -ForegroundColor White
Write-Host "  □ Force logout all active sessions" -ForegroundColor White

Write-Host "`n" -ForegroundColor Green
