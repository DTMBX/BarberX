@echo off
setlocal EnableExtensions

REM --- Location of the script (same folder as this .cmd) ---
set "HERE=%~dp0"
set "SCRIPT=%HERE%Approve-Pad.ahk"

if not exist "%SCRIPT%" (
  echo [Approve Pad] Missing file: Approve-Pad.ahk
  echo Put Approve-Pad.ahk in the same folder as this launcher.
  echo.
  pause
  exit /b 1
)

REM --- If AutoHotkey v2 is installed and associated, this will run it ---
start "" "%SCRIPT%"
if errorlevel 1 goto :fallback

exit /b 0

:fallback
echo.
echo [Approve Pad] AutoHotkey v2 was not found or .ahk is not associated.
echo.
echo Install AutoHotkey v2 (official) then run Approve Pad again.
echo.
echo https://www.autohotkey.com/
echo.
pause
exit /b 2
