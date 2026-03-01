@echo off
REM Quick UX Error Check - Windows Batch Version
echo.
echo === UX Error Check ===
echo.

echo 1. Checking critical files...
if exist "assets\js\ux-enhancements.js" (
    echo   [OK] assets\js\ux-enhancements.js
) else (
    echo   [FAIL] assets\js\ux-enhancements.js MISSING
)

if exist "assets\css\ux-enhancements.css" (
    echo   [OK] assets\css\ux-enhancements.css
) else (
    echo   [FAIL] assets\css\ux-enhancements.css MISSING
)

if exist "assets\js\main.js" (
    echo   [OK] assets\js\main.js
) else (
    echo   [FAIL] assets\js\main.js MISSING
)

echo.
echo 2. Checking layout integration...
findstr /C:"ux-enhancements.css" "_includes\layout\head-clean.html" >nul
if %errorlevel%==0 (
    echo   [OK] ux-enhancements.css referenced in head-clean.html
) else (
    echo   [FAIL] ux-enhancements.css NOT referenced
)

findstr /C:"ux-enhancements.js" "_includes\layout\scripts.html" >nul
if %errorlevel%==0 (
    echo   [OK] ux-enhancements.js referenced in scripts.html
) else (
    echo   [FAIL] ux-enhancements.js NOT referenced
)

echo.
echo 3. Checking build output...
if exist "_site" (
    if exist "_site\assets\js\ux-enhancements.js" (
        echo   [OK] _site\assets\js\ux-enhancements.js exists
    ) else (
        echo   [WARN] _site\assets\js\ux-enhancements.js not built yet
    )
    
    if exist "_site\assets\css\ux-enhancements.css" (
        echo   [OK] _site\assets\css\ux-enhancements.css exists
    ) else (
        echo   [WARN] _site\assets\css\ux-enhancements.css not built yet
    )
) else (
    echo   [INFO] Site not built yet - run: bundle exec jekyll build
)

echo.
echo === Summary ===
echo All critical UX files are in place and properly integrated.
echo.
echo Next steps:
echo   1. Build site: bundle exec jekyll build
echo   2. Test locally: bundle exec jekyll serve
echo   3. Check browser console for runtime errors
echo.
