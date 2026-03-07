@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM                    EVIDENT WEB BUILDER — Quick Launcher
REM ═══════════════════════════════════════════════════════════════════════════
REM  Double-click this file to launch Web Builder
REM ═══════════════════════════════════════════════════════════════════════════

title Evident Web Builder

cd /d "%~dp0"

echo.
echo   Starting Evident Web Builder...
echo.

REM Check for PowerShell
where powershell >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    powershell -ExecutionPolicy Bypass -File "%~dp0WebBuilder.ps1"
) else (
    REM Fallback: Open directly in browser
    start "" "%~dp0index.html"
)
