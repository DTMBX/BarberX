#!/bin/bash

# Geneva Bible Study - Icon & Splash Screen Setup Script
# This script creates the directory structure and generates placeholder documentation

echo "📱 Geneva Bible Study - Icon & Splash Screen Setup"
echo "=================================================="
echo ""

# Create directory structure
echo "📁 Creating directory structure..."

mkdir -p public/icons
mkdir -p public/splash
mkdir -p android/app/src/main/res/mipmap-mdpi
mkdir -p android/app/src/main/res/mipmap-hdpi
mkdir -p android/app/src/main/res/mipmap-xhdpi
mkdir -p android/app/src/main/res/mipmap-xxhdpi
mkdir -p android/app/src/main/res/mipmap-xxxhdpi
mkdir -p android/app/src/main/res/drawable
mkdir -p ios/App/App/Assets.xcassets/AppIcon.appiconset
mkdir -p ios/App/App/Assets.xcassets/Splash.imageset

echo "✅ Directory structure created"
echo ""

# Check if ImageMagick is installed for icon generation
if command -v convert &> /dev/null; then
    echo "✅ ImageMagick detected - can generate icons automatically"
    echo ""
    echo "Would you like to generate icons now? (y/n)"
    read -r response
    
    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        echo "🎨 Generating app icons..."
        
        # This would be the icon generation logic
        # For now, we'll just document the steps
        echo "⚠️  Automated generation requires additional setup"
        echo "   Please use the web-based generator: generate-icons.html"
    fi
else
    echo "ℹ️  ImageMagick not found - use web-based generator"
    echo "   Open generate-icons.html in your browser to create icons"
fi

echo ""
echo "📋 Next Steps:"
echo "=============="
echo ""
echo "1. Generate Icons:"
echo "   - Open generate-icons.html in your browser"
echo "   - Click 'Generate All Icons & Splash Screens'"
echo "   - Download the generated assets"
echo ""
echo "2. Install Assets:"
echo "   - Copy icons to public/icons/"
echo "   - Copy splash screens to public/splash/"
echo "   - For native apps, copy to platform-specific directories"
echo ""
echo "3. Verify Installation:"
echo "   - Check manifest.json references"
echo "   - Test PWA installation"
echo "   - Build and test native apps"
echo ""
echo "📖 Full documentation: APP_ICONS_SPLASH_GUIDE.md"
echo ""
echo "✨ Setup complete!"
