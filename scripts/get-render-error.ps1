#!/usr/bin/env pwsh
# Quick Render Error Checker
# Gets you the exact error message

Write-Host "`n?? Render Error Diagnosis Helper" -ForegroundColor Cyan
Write-Host "=" * 70

Write-Host "`n?? TO GET THE EXACT ERROR:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to: https://dashboard.render.com" -ForegroundColor White
Write-Host "2. Login with your Render account" -ForegroundColor White
Write-Host "3. Click on your service: 'Evident-legal-tech'" -ForegroundColor White
Write-Host "4. Click 'Logs' in the left sidebar" -ForegroundColor White
Write-Host "5. Scroll to the VERY BOTTOM" -ForegroundColor White
Write-Host "6. Look for RED ERROR MESSAGES" -ForegroundColor Red
Write-Host "7. Copy the last 30-50 lines" -ForegroundColor White
Write-Host "8. Paste them here" -ForegroundColor White

Write-Host "`n? COMMON RENDER ERRORS:" -ForegroundColor Cyan
Write-Host ""

Write-Host "ERROR 1: Database Not Created" -ForegroundColor Yellow
Write-Host "  Message: 'could not connect to database' or 'DATABASE_URL not set'" -ForegroundColor Gray
Write-Host "  Fix: You need to create PostgreSQL database in Render" -ForegroundColor Green
Write-Host ""

Write-Host "ERROR 2: Missing Environment Variables" -ForegroundColor Yellow  
Write-Host "  Message: 'KeyError: SECRET_KEY' or similar" -ForegroundColor Gray
Write-Host "  Fix: Add SECRET_KEY in Render Environment tab" -ForegroundColor Green
Write-Host ""

Write-Host "ERROR 3: Import/Module Error" -ForegroundColor Yellow
Write-Host "  Message: 'ModuleNotFoundError' or 'ImportError'" -ForegroundColor Gray
Write-Host "  Fix: Missing dependency or circular import" -ForegroundColor Green
Write-Host ""

Write-Host "ERROR 4: Build Failed" -ForegroundColor Yellow
Write-Host "  Message: 'Build failed' in Events tab" -ForegroundColor Gray
Write-Host "  Fix: Check build logs for missing dependencies" -ForegroundColor Green
Write-Host ""

Write-Host "=" * 70
Write-Host "`n??  QUICK CHECK:" -ForegroundColor Cyan
Write-Host "Open this URL and see what happens:" -ForegroundColor White
Write-Host "https://Evident-legal-tech.onrender.com" -ForegroundColor Blue
Write-Host ""
Write-Host "What do you see?" -ForegroundColor Yellow
Write-Host "  A) 'Internal Server Error' - App is running but crashing" -ForegroundColor Gray
Write-Host "  B) 'Service Unavailable' - App not deployed yet or sleeping" -ForegroundColor Gray
Write-Host "  C) Nothing/Timeout - App failed to start" -ForegroundColor Gray
Write-Host "  D) Working website - Success!" -ForegroundColor Green
Write-Host ""

Write-Host "?? PASTE YOUR RENDER LOGS HERE AND I'LL FIX IT IMMEDIATELY!" -ForegroundColor Green
Write-Host ""
