@echo off
REM ==============================================================================
REM Geneva Bible Study - Capacitor Icon Setup Script (Windows)
REM ==============================================================================
REM This script automates the installation of iOS and Android app icons
REM for Capacitor native projects on Windows.
REM
REM Prerequisites:
REM - Icons generated from generate-icons.html
REM - Capacitor iOS and Android projects initialized
REM - ImageMagick installed (optional, for icon conversion)
REM
REM Usage:
REM   setup-capacitor-icons.bat [path-to-generated-icons]
REM ==============================================================================

setlocal enabledelayedexpansion

REM Colors for output (limited on Windows)
set "INFO=[INFO]"
set "SUCCESS=[OK]"
set "ERROR=[ERROR]"
set "WARNING=[WARN]"

REM Default paths
set "SCRIPT_DIR=%~dp0"
set "ICON_SOURCE_DIR=%~1"
if "!ICON_SOURCE_DIR!"=="" set "ICON_SOURCE_DIR=%SCRIPT_DIR%generated-icons"
set "IOS_DIR=%SCRIPT_DIR%ios\App\App\Assets.xcassets"
set "ANDROID_RES_DIR=%SCRIPT_DIR%android\app\src\main\res"

REM ==============================================================================
REM Main Execution
REM ==============================================================================

echo.
echo ===================================================
echo Geneva Bible Study - Capacitor Icon Setup
echo ===================================================
echo.

REM Check prerequisites
echo %INFO% Checking prerequisites...

if not exist "!ICON_SOURCE_DIR!" (
    echo %ERROR% Icon source directory not found: !ICON_SOURCE_DIR!
    echo %INFO% Please generate icons first using generate-icons.html
    echo %INFO% Or specify the path: setup-capacitor-icons.bat C:\path\to\icons
    exit /b 1
)
echo %SUCCESS% Icon source directory found

REM Check if Capacitor projects exist
set "HAS_IOS=0"
set "HAS_ANDROID=0"

if exist "%SCRIPT_DIR%ios" (
    echo %SUCCESS% iOS project found
    set "HAS_IOS=1"
) else (
    echo %WARNING% iOS project not found - iOS icons will be skipped
)

if exist "%SCRIPT_DIR%android" (
    echo %SUCCESS% Android project found
    set "HAS_ANDROID=1"
) else (
    echo %WARNING% Android project not found - Android icons will be skipped
)

if !HAS_IOS!==0 if !HAS_ANDROID!==0 (
    echo %ERROR% No Capacitor native projects found
    echo %INFO% Run 'npx cap add ios' and 'npx cap add android' first
    exit /b 1
)

REM ==============================================================================
REM iOS Icon Installation
REM ==============================================================================

if !HAS_IOS!==1 (
    echo.
    echo ===================================================
    echo Installing iOS Icons
    echo ===================================================
    echo.
    
    REM Create AppIcon.appiconset directory
    set "APPICON_DIR=%IOS_DIR%\AppIcon.appiconset"
    if not exist "!APPICON_DIR!" mkdir "!APPICON_DIR!"
    echo %SUCCESS% Created AppIcon.appiconset directory
    
    REM Create Contents.json
    (
        echo {
        echo   "images": [
        echo     {
        echo       "size": "20x20",
        echo       "idiom": "iphone",
        echo       "filename": "icon-20@2x.png",
        echo       "scale": "2x"
        echo     },
        echo     {
        echo       "size": "20x20",
        echo       "idiom": "iphone",
        echo       "filename": "icon-20@3x.png",
        echo       "scale": "3x"
        echo     },
        echo     {
        echo       "size": "29x29",
        echo       "idiom": "iphone",
        echo       "filename": "icon-29@2x.png",
        echo       "scale": "2x"
        echo     },
        echo     {
        echo       "size": "29x29",
        echo       "idiom": "iphone",
        echo       "filename": "icon-29@3x.png",
        echo       "scale": "3x"
        echo     },
        echo     {
        echo       "size": "40x40",
        echo       "idiom": "iphone",
        echo       "filename": "icon-40@2x.png",
        echo       "scale": "2x"
        echo     },
        echo     {
        echo       "size": "40x40",
        echo       "idiom": "iphone",
        echo       "filename": "icon-40@3x.png",
        echo       "scale": "3x"
        echo     },
        echo     {
        echo       "size": "60x60",
        echo       "idiom": "iphone",
        echo       "filename": "icon-60@2x.png",
        echo       "scale": "2x"
        echo     },
        echo     {
        echo       "size": "60x60",
        echo       "idiom": "iphone",
        echo       "filename": "icon-60@3x.png",
        echo       "scale": "3x"
        echo     },
        echo     {
        echo       "size": "20x20",
        echo       "idiom": "ipad",
        echo       "filename": "icon-20@1x.png",
        echo       "scale": "1x"
        echo     },
        echo     {
        echo       "size": "20x20",
        echo       "idiom": "ipad",
        echo       "filename": "icon-20@2x.png",
        echo       "scale": "2x"
        echo     },
        echo     {
        echo       "size": "29x29",
        echo       "idiom": "ipad",
        echo       "filename": "icon-29@1x.png",
        echo       "scale": "1x"
        echo     },
        echo     {
        echo       "size": "29x29",
        echo       "idiom": "ipad",
        echo       "filename": "icon-29@2x.png",
        echo       "scale": "2x"
        echo     },
        echo     {
        echo       "size": "40x40",
        echo       "idiom": "ipad",
        echo       "filename": "icon-40@1x.png",
        echo       "scale": "1x"
        echo     },
        echo     {
        echo       "size": "40x40",
        echo       "idiom": "ipad",
        echo       "filename": "icon-40@2x.png",
        echo       "scale": "2x"
        echo     },
        echo     {
        echo       "size": "76x76",
        echo       "idiom": "ipad",
        echo       "filename": "icon-76@1x.png",
        echo       "scale": "1x"
        echo     },
        echo     {
        echo       "size": "76x76",
        echo       "idiom": "ipad",
        echo       "filename": "icon-76@2x.png",
        echo       "scale": "2x"
        echo     },
        echo     {
        echo       "size": "83.5x83.5",
        echo       "idiom": "ipad",
        echo       "filename": "icon-83.5@2x.png",
        echo       "scale": "2x"
        echo     },
        echo     {
        echo       "size": "1024x1024",
        echo       "idiom": "ios-marketing",
        echo       "filename": "icon-1024@1x.png",
        echo       "scale": "1x"
        echo     }
        echo   ],
        echo   "info": {
        echo     "version": 1,
        echo     "author": "xcode"
        echo   }
        echo }
    ) > "!APPICON_DIR!\Contents.json"
    echo %SUCCESS% Created Contents.json
    
    echo %INFO% iOS icon files must be placed manually in: !APPICON_DIR!
    echo %INFO% Use ImageMagick or online tools to generate required sizes
    echo %SUCCESS% iOS icons setup complete
)

REM ==============================================================================
REM Android Icon Installation
REM ==============================================================================

if !HAS_ANDROID!==1 (
    echo.
    echo ===================================================
    echo Installing Android Icons
    echo ===================================================
    echo.
    
    REM Create mipmap directories
    for %%d in (mdpi hdpi xhdpi xxhdpi xxxhdpi) do (
        if not exist "%ANDROID_RES_DIR%\mipmap-%%d" mkdir "%ANDROID_RES_DIR%\mipmap-%%d"
        echo %SUCCESS% Created mipmap-%%d directory
    )
    
    if not exist "%ANDROID_RES_DIR%\mipmap-anydpi-v26" mkdir "%ANDROID_RES_DIR%\mipmap-anydpi-v26"
    if not exist "%ANDROID_RES_DIR%\values" mkdir "%ANDROID_RES_DIR%\values"
    echo %SUCCESS% Created adaptive icon directories
    
    REM Create adaptive icon XML files
    (
        echo ^<?xml version="1.0" encoding="utf-8"?^>
        echo ^<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android"^>
        echo     ^<background android:drawable="@color/ic_launcher_background"/^>
        echo     ^<foreground android:drawable="@mipmap/ic_launcher_foreground"/^>
        echo ^</adaptive-icon^>
    ) > "%ANDROID_RES_DIR%\mipmap-anydpi-v26\ic_launcher.xml"
    echo %SUCCESS% Created ic_launcher.xml
    
    (
        echo ^<?xml version="1.0" encoding="utf-8"?^>
        echo ^<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android"^>
        echo     ^<background android:drawable="@color/ic_launcher_background"/^>
        echo     ^<foreground android:drawable="@mipmap/ic_launcher_foreground"/^>
        echo ^</adaptive-icon^>
    ) > "%ANDROID_RES_DIR%\mipmap-anydpi-v26\ic_launcher_round.xml"
    echo %SUCCESS% Created ic_launcher_round.xml
    
    REM Create colors.xml
    (
        echo ^<?xml version="1.0" encoding="utf-8"?^>
        echo ^<resources^>
        echo     ^<color name="colorPrimary"^>#5A3A31^</color^>
        echo     ^<color name="colorPrimaryDark"^>#4A2A21^</color^>
        echo     ^<color name="colorAccent"^>#8B6914^</color^>
        echo     ^<color name="ic_launcher_background"^>#5A3A31^</color^>
        echo ^</resources^>
    ) > "%ANDROID_RES_DIR%\values\colors.xml"
    echo %SUCCESS% Created colors.xml
    
    echo %INFO% Android icon files must be placed manually
    echo %INFO% Required sizes:
    echo %INFO%   - mipmap-mdpi: 48x48
    echo %INFO%   - mipmap-hdpi: 72x72
    echo %INFO%   - mipmap-xhdpi: 96x96
    echo %INFO%   - mipmap-xxhdpi: 144x144
    echo %INFO%   - mipmap-xxxhdpi: 192x192
    echo %SUCCESS% Android icons setup complete
)

REM ==============================================================================
REM Capacitor Sync
REM ==============================================================================

echo.
echo ===================================================
echo Syncing Capacitor Projects
echo ===================================================
echo.

where npx >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo %INFO% Running npx cap sync...
    call npx cap sync
    if !ERRORLEVEL! EQU 0 (
        echo %SUCCESS% Capacitor sync completed successfully
    ) else (
        echo %WARNING% Capacitor sync encountered issues
        echo %INFO% You may need to sync manually: npx cap sync
    )
) else (
    echo %WARNING% npx not found - skipping Capacitor sync
    echo %INFO% Run 'npx cap sync' manually after installation
)

REM ==============================================================================
REM Completion
REM ==============================================================================

echo.
echo ===================================================
echo Setup Complete!
echo ===================================================
echo.
echo %INFO% Next steps:
echo   1. Place icon files in the created directories
echo   2. Open iOS project: npx cap open ios
echo   3. Open Android project: npx cap open android
echo   4. Verify icons appear in Xcode and Android Studio
echo   5. Build and test on simulators/emulators
echo.
echo %INFO% For detailed configuration, see CAPACITOR_ICONS_CONFIG.md
echo.

pause
