@echo off
REM Geneva Bible Study - Icon & Splash Screen Setup Script (Windows)
REM This script creates the directory structure for icons and splash screens

echo 📱 Geneva Bible Study - Icon ^& Splash Screen Setup
echo ==================================================
echo.

REM Create directory structure
echo 📁 Creating directory structure...
echo.

mkdir public\icons 2>nul
mkdir public\splash 2>nul
mkdir android\app\src\main\res\mipmap-mdpi 2>nul
mkdir android\app\src\main\res\mipmap-hdpi 2>nul
mkdir android\app\src\main\res\mipmap-xhdpi 2>nul
mkdir android\app\src\main\res\mipmap-xxhdpi 2>nul
mkdir android\app\src\main\res\mipmap-xxxhdpi 2>nul
mkdir android\app\src\main\res\drawable 2>nul
mkdir ios\App\App\Assets.xcassets\AppIcon.appiconset 2>nul
mkdir ios\App\App\Assets.xcassets\Splash.imageset 2>nul

echo ✅ Directory structure created
echo.

echo 📋 Next Steps:
echo ==============
echo.
echo 1. Generate Icons:
echo    - Open generate-icons.html in your browser
echo    - Click 'Generate All Icons ^& Splash Screens'
echo    - Download the generated assets
echo.
echo 2. Install Assets:
echo    - Copy icons to public\icons\
echo    - Copy splash screens to public\splash\
echo    - For native apps, copy to platform-specific directories
echo.
echo 3. Verify Installation:
echo    - Check manifest.json references
echo    - Test PWA installation
echo    - Build and test native apps
echo.
echo 📖 Full documentation: APP_ICONS_SPLASH_GUIDE.md
echo.
echo ✨ Setup complete!
echo.
pause
