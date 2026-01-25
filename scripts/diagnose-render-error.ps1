#!/usr/bin/env pwsh
# Render Deployment Diagnostics
# Helps identify why Render deployment is failing

Write-Host "`n?? Render Deployment Diagnostics" -ForegroundColor Cyan
Write-Host "=" * 60

Write-Host "`n?? To diagnose your Render error, follow these steps:" -ForegroundColor Yellow

Write-Host "`n[STEP 1] Check Render Logs" -ForegroundColor Cyan
Write-Host "1. Go to: https://dashboard.render.com" -ForegroundColor White
Write-Host "2. Click on 'barberx-legal-tech' service" -ForegroundColor White
Write-Host "3. Click 'Logs' tab (left sidebar)" -ForegroundColor White
Write-Host "4. Scroll to the bottom" -ForegroundColor White
Write-Host "5. Look for RED error messages" -ForegroundColor White

Write-Host "`n[STEP 2] Common Errors & Fixes" -ForegroundColor Cyan

Write-Host "`n? ERROR 1: ModuleNotFoundError" -ForegroundColor Red
Write-Host "   Example: 'ModuleNotFoundError: No module named batch_upload_handler'" -ForegroundColor Gray
Write-Host "   FIX: Missing dependency or import error" -ForegroundColor Yellow
Write-Host "   ? Check if all imports in app.py are correct" -ForegroundColor Green

Write-Host "`n? ERROR 2: Database Connection" -ForegroundColor Red
Write-Host "   Example: 'sqlalchemy.exc.OperationalError: could not connect'" -ForegroundColor Gray
Write-Host "   FIX: Database not created or DATABASE_URL not set" -ForegroundColor Yellow
Write-Host "   ? Create PostgreSQL database in Render" -ForegroundColor Green

Write-Host "`n? ERROR 3: Missing Environment Variables" -ForegroundColor Red
Write-Host "   Example: 'KeyError: SECRET_KEY'" -ForegroundColor Gray
Write-Host "   FIX: Environment variables not set" -ForegroundColor Yellow
Write-Host "   ? Add required env vars in Render dashboard" -ForegroundColor Green

Write-Host "`n? ERROR 4: Import Error from batch_upload_handler" -ForegroundColor Red
Write-Host "   Example: 'cannot import name batch_upload_bp'" -ForegroundColor Gray
Write-Host "   FIX: Circular import or module issue" -ForegroundColor Yellow
Write-Host "   ? Make batch_upload_handler imports optional" -ForegroundColor Green

Write-Host "`n[STEP 3] Required Environment Variables" -ForegroundColor Cyan
Write-Host "In Render Dashboard ? Environment tab, you MUST have:" -ForegroundColor White
Write-Host "  ? SECRET_KEY = (any random string)" -ForegroundColor Gray
Write-Host "  ? DATABASE_URL = (auto-set if PostgreSQL created)" -ForegroundColor Gray
Write-Host "  ? FLASK_ENV = production" -ForegroundColor Gray
Write-Host "  ? PYTHON_VERSION = 3.11.9" -ForegroundColor Gray

Write-Host "`n[STEP 4] Quick Fix - Make Imports Optional" -ForegroundColor Cyan
Write-Host "The most likely issue is the batch_upload_handler import." -ForegroundColor White
Write-Host "Run this fix:" -ForegroundColor Yellow
Write-Host "  python scripts\fix-render-imports.py" -ForegroundColor White

Write-Host "`n?? WHAT TO DO NOW:" -ForegroundColor Yellow
Write-Host "1. Check Render logs (copy last 30 lines)" -ForegroundColor White
Write-Host "2. Paste the error here" -ForegroundColor White
Write-Host "3. I'll give you exact fix!" -ForegroundColor White

Write-Host "`n?? OR - Let me create a quick fix for common issue:" -ForegroundColor Cyan
Write-Host "   The batch_upload_handler might be causing circular import" -ForegroundColor Gray
Write-Host "   I'll make it optional in app.py" -ForegroundColor Gray

Write-Host ""
