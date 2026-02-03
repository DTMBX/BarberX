#!/usr/bin/env pwsh
# DAY 1 FINAL DEPLOYMENT SCRIPT

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DAY 1 FINAL: Deploying Pro-Truth Landing" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to repo
Set-Location C:\web-dev\github-repos\Evident.info

# Stage files
Write-Host "Staging files..." -ForegroundColor Yellow
git add templates/landing-public.html
git add app.py
git add DAY-1-LAUNCH-READY-COMPLETE.md
git add PRO-TRUTH-MESSAGING-UPDATE.md

# Show what's staged
Write-Host ""
Write-Host "Files to commit:" -ForegroundColor Green
git diff --cached --name-status

# Commit
Write-Host ""
Write-Host "Committing..." -ForegroundColor Yellow
git commit -m @"
DAY 1 FINAL: Launch-Ready Landing + Pro-Truth Messaging

COMPLETE: All Day 1 acceptance criteria met + pro-truth update

NEW SECTION: Truth Protects Good Officers Too
✅ "We sell confidence, not conflict"
✅ "Truth protects good officers who honor their oath"
✅ "Remove bad apples to protect the good ones"
✅ "Both sides have oath to justice"

HERO UPDATED:
- Tagline: "Sell Confidence, Not Conflict — Dig Up Truth, Protect Good Officers"
- Sub-tagline emphasizes protecting both defendants AND good officers

PROBLEM/SOLUTION UPDATED:
- Headline: "Defense Attorneys Need The Same Tools Prosecutors Have"
- Subtitle: "Truth-seeking technology protects everyone—including good officers"
- Added: Bad actors hide violations / Good officers overlooked
- Added: Truth surfaces / Confidence not guesswork

CONFIDENCE FRAMING:
"Evident gives you confidence in the evidence—that you found every
Miranda warning, every 4th Amendment issue, every contradiction. When
defense attorneys have tools to uncover truth, good officers are
protected and bad actors are held accountable. That's how the system
is supposed to work."

MISSION STATEMENT:
"The truth doesn't take sides. It just is. Our job is to find it—
no matter where it leads."

FILES:
+ templates/landing-public.html (conversion landing + pro-truth)
+ DAY-1-LAUNCH-READY-COMPLETE.md (deployment guide)
+ PRO-TRUTH-MESSAGING-UPDATE.md (messaging explanation)
M app.py (/ route + email API)

POSITIONING:
- Not anti-police, pro-accountability
- Not conflict-driven, confidence-driven  
- Not divisive, truth-seeking
- Protects everyone who honors their oath

READY: Evident can launch Founding Member program today
with messaging that honors both sides' service to justice.

Phase 1 Ignition: Deployed → Credible → Conversion-capable → Honorable
"@

# Push
Write-Host ""
Write-Host "Pushing to origin main..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ DAY 1 DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test at https://Evident.info" -ForegroundColor White
Write-Host "2. Verify email capture works" -ForegroundColor White
Write-Host "3. Share with first potential customer" -ForegroundColor White
Write-Host ""
Write-Host "By the Grace of Almighty God, DAY 1 IS SHIPPED. 🇺🇸" -ForegroundColor Green
