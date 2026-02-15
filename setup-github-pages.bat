@echo off
REM GitHub Pages Deployment Setup Script for Windows
REM This script helps configure the repository for GitHub Pages deployment

echo ================================
echo GitHub Pages Deployment Setup
echo ================================
echo.

REM Check if git is available
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: git is not installed
    pause
    exit /b 1
)

REM Check if we're in a git repository
git rev-parse --is-inside-work-tree >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Not in a git repository
    pause
    exit /b 1
)

echo Detecting repository information...
echo.

REM Get remote URL
for /f "tokens=*" %%i in ('git config --get remote.origin.url') do set REMOTE_URL=%%i

if "%REMOTE_URL%"=="" (
    echo Warning: No remote origin found
    set /p REMOTE_URL="Enter your GitHub repository URL: "
)

echo Remote URL: %REMOTE_URL%
echo.

REM Extract username and repo (simplified for Windows)
set /p USERNAME="Enter your GitHub username: "
set /p REPO="Enter your repository name: "

echo.
echo Configuration to apply:
echo   - Base path: /%REPO%/
echo   - Homepage: https://%USERNAME%.github.io/%REPO%/
echo   - Repository URL: https://github.com/%USERNAME%/%REPO%.git
echo.

set /p CONFIRM="Is this correct? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Setup cancelled
    pause
    exit /b 0
)

echo.
echo Updating configuration files...

REM Update vite.config.ts
if exist vite.config.ts (
    echo   - Updating vite.config.ts...
    powershell -Command "(Get-Content vite.config.ts) -replace 'base: process.env.GITHUB_ACTIONS \? ''/spark-template/'' : ''/''', 'base: process.env.GITHUB_ACTIONS ? ''/%REPO%/'' : ''/''' | Set-Content vite.config.ts"
    echo     vite.config.ts updated
) else (
    echo     Warning: vite.config.ts not found
)

REM Update package.json
if exist package.json (
    echo   - Updating package.json...
    powershell -Command "(Get-Content package.json) -replace 'YOUR_USERNAME', '%USERNAME%' -replace 'YOUR_REPO', '%REPO%' | Set-Content package.json"
    echo     package.json updated
) else (
    echo     Warning: package.json not found
)

REM Update README.md
if exist README.md (
    echo   - Updating README.md...
    powershell -Command "(Get-Content README.md) -replace 'YOUR_USERNAME', '%USERNAME%' -replace 'YOUR_REPO', '%REPO%' | Set-Content README.md"
    echo     README.md updated
)

echo.
echo Configuration complete!
echo.
echo Next steps:
echo.
echo 1. Enable GitHub Pages in your repository:
echo    - Go to: https://github.com/%USERNAME%/%REPO%/settings/pages
echo    - Under 'Build and deployment', select 'GitHub Actions'
echo.
echo 2. Commit and push changes:
echo    git add .
echo    git commit -m "Configure for GitHub Pages deployment"
echo    git push origin main
echo.
echo 3. Monitor deployment:
echo    - Go to: https://github.com/%USERNAME%/%REPO%/actions
echo    - Watch the 'Deploy to GitHub Pages' workflow
echo.
echo 4. Access your site:
echo    - https://%USERNAME%.github.io/%REPO%/
echo.
echo Happy deploying!
echo.
pause
