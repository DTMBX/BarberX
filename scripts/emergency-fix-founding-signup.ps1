#!/usr/bin/env pwsh
# EMERGENCY FIX: Founding member signup database error

Write-Host "========================================" -ForegroundColor Red
Write-Host "EMERGENCY FIX: Founding Member Signup" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

Set-Location C:\web-dev\github-repos\Evident.info

Write-Host "Staging fix..." -ForegroundColor Yellow
git add app.py

Write-Host "Committing..." -ForegroundColor Yellow
git commit -m "EMERGENCY FIX: Founding member signup database error

PRODUCTION ERROR FIXED:
- Changed founding_member_signup() from raw SQL (get_db) to CSV flat file
- get_db() doesn't exist in Flask-SQLAlchemy setup
- CSV approach is simpler, production-ready for email capture
- Avoids database schema changes on production deploy

ERROR WAS:
AttributeError at line 2675: get_db() not defined
Raw SQL cursor.execute() incompatible with Flask-SQLAlchemy

FIX:
- Use founding_member_signups.csv for email capture
- Check for duplicates before adding
- Count spots remaining (100 max)
- Same API response structure
- Production: Integrate with Stripe customer creation later

TESTED: CSV file creation, duplicate detection, spots counting
SAFE: No database migrations required
SIMPLE: Easy to review signups (open CSV)

This unblocks Day 1 deployment."

Write-Host "Pushing..." -ForegroundColor Yellow
git push origin main

Write-Host "" -ForegroundColor Green
Write-Host "✅ EMERGENCY FIX DEPLOYED" -ForegroundColor Green
Write-Host "Render.com will auto-deploy in ~2 minutes" -ForegroundColor White
Write-Host "" -ForegroundColor White
