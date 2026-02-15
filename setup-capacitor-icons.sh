#!/bin/bash

# ==============================================================================
# Geneva Bible Study - Capacitor Icon Setup Script
# ==============================================================================
# This script automates the installation of iOS and Android app icons
# for Capacitor native projects.
#
# Prerequisites:
# - Icons generated from generate-icons.html
# - Capacitor iOS and Android projects initialized
# - ImageMagick installed (optional, for icon conversion)
#
# Usage:
#   chmod +x setup-capacitor-icons.sh
#   ./setup-capacitor-icons.sh [path-to-generated-icons]
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ICON_SOURCE_DIR="${1:-$SCRIPT_DIR/generated-icons}"
IOS_DIR="$SCRIPT_DIR/ios/App/App/Assets.xcassets"
ANDROID_RES_DIR="$SCRIPT_DIR/android/app/src/main/res"

# ==============================================================================
# Helper Functions
# ==============================================================================

print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if icon source directory exists
    if [ ! -d "$ICON_SOURCE_DIR" ]; then
        print_error "Icon source directory not found: $ICON_SOURCE_DIR"
        print_info "Please generate icons first using generate-icons.html"
        print_info "Or specify the path: ./setup-capacitor-icons.sh /path/to/icons"
        exit 1
    fi
    print_success "Icon source directory found"
    
    # Check if Capacitor projects exist
    if [ ! -d "$SCRIPT_DIR/ios" ] && [ ! -d "$SCRIPT_DIR/android" ]; then
        print_warning "No Capacitor native projects found"
        print_info "Run 'npx cap add ios' and 'npx cap add android' first"
        exit 1
    fi
    
    if [ -d "$SCRIPT_DIR/ios" ]; then
        print_success "iOS project found"
    else
        print_warning "iOS project not found - iOS icons will be skipped"
    fi
    
    if [ -d "$SCRIPT_DIR/android" ]; then
        print_success "Android project found"
    else
        print_warning "Android project not found - Android icons will be skipped"
    fi
}

# ==============================================================================
# iOS Icon Installation
# ==============================================================================

install_ios_icons() {
    if [ ! -d "$SCRIPT_DIR/ios" ]; then
        print_warning "Skipping iOS icons - project not found"
        return
    fi
    
    print_header "Installing iOS Icons"
    
    # Create AppIcon.appiconset directory
    local APPICON_DIR="$IOS_DIR/AppIcon.appiconset"
    mkdir -p "$APPICON_DIR"
    print_success "Created AppIcon.appiconset directory"
    
    # Create Contents.json
    cat > "$APPICON_DIR/Contents.json" << 'EOF'
{
  "images": [
    {
      "size": "20x20",
      "idiom": "iphone",
      "filename": "icon-20@2x.png",
      "scale": "2x"
    },
    {
      "size": "20x20",
      "idiom": "iphone",
      "filename": "icon-20@3x.png",
      "scale": "3x"
    },
    {
      "size": "29x29",
      "idiom": "iphone",
      "filename": "icon-29@2x.png",
      "scale": "2x"
    },
    {
      "size": "29x29",
      "idiom": "iphone",
      "filename": "icon-29@3x.png",
      "scale": "3x"
    },
    {
      "size": "40x40",
      "idiom": "iphone",
      "filename": "icon-40@2x.png",
      "scale": "2x"
    },
    {
      "size": "40x40",
      "idiom": "iphone",
      "filename": "icon-40@3x.png",
      "scale": "3x"
    },
    {
      "size": "60x60",
      "idiom": "iphone",
      "filename": "icon-60@2x.png",
      "scale": "2x"
    },
    {
      "size": "60x60",
      "idiom": "iphone",
      "filename": "icon-60@3x.png",
      "scale": "3x"
    },
    {
      "size": "20x20",
      "idiom": "ipad",
      "filename": "icon-20@1x.png",
      "scale": "1x"
    },
    {
      "size": "20x20",
      "idiom": "ipad",
      "filename": "icon-20@2x.png",
      "scale": "2x"
    },
    {
      "size": "29x29",
      "idiom": "ipad",
      "filename": "icon-29@1x.png",
      "scale": "1x"
    },
    {
      "size": "29x29",
      "idiom": "ipad",
      "filename": "icon-29@2x.png",
      "scale": "2x"
    },
    {
      "size": "40x40",
      "idiom": "ipad",
      "filename": "icon-40@1x.png",
      "scale": "1x"
    },
    {
      "size": "40x40",
      "idiom": "ipad",
      "filename": "icon-40@2x.png",
      "scale": "2x"
    },
    {
      "size": "76x76",
      "idiom": "ipad",
      "filename": "icon-76@1x.png",
      "scale": "1x"
    },
    {
      "size": "76x76",
      "idiom": "ipad",
      "filename": "icon-76@2x.png",
      "scale": "2x"
    },
    {
      "size": "83.5x83.5",
      "idiom": "ipad",
      "filename": "icon-83.5@2x.png",
      "scale": "2x"
    },
    {
      "size": "1024x1024",
      "idiom": "ios-marketing",
      "filename": "icon-1024@1x.png",
      "scale": "1x"
    }
  ],
  "info": {
    "version": 1,
    "author": "xcode"
  }
}
EOF
    print_success "Created Contents.json"
    
    # Copy or generate iOS icons
    # Note: This uses the PWA icons from public/icons as source
    local PUBLIC_ICONS="$SCRIPT_DIR/public/icons"
    
    if [ -d "$PUBLIC_ICONS" ]; then
        print_info "Using icons from public/icons directory"
        
        # Check if ImageMagick is available for resizing
        if command -v convert &> /dev/null; then
            print_info "ImageMagick found - will resize icons as needed"
            
            # Generate all required iOS sizes
            declare -A ios_sizes=(
                ["icon-20@1x.png"]="20"
                ["icon-20@2x.png"]="40"
                ["icon-20@3x.png"]="60"
                ["icon-29@1x.png"]="29"
                ["icon-29@2x.png"]="58"
                ["icon-29@3x.png"]="87"
                ["icon-40@1x.png"]="40"
                ["icon-40@2x.png"]="80"
                ["icon-40@3x.png"]="120"
                ["icon-60@2x.png"]="120"
                ["icon-60@3x.png"]="180"
                ["icon-76@1x.png"]="76"
                ["icon-76@2x.png"]="152"
                ["icon-83.5@2x.png"]="167"
                ["icon-1024@1x.png"]="1024"
            )
            
            # Use the largest available icon as source
            local SOURCE_ICON="$PUBLIC_ICONS/icon-512x512.png"
            if [ ! -f "$SOURCE_ICON" ]; then
                SOURCE_ICON="$PUBLIC_ICONS/icon-192x192.png"
            fi
            
            for filename in "${!ios_sizes[@]}"; do
                local size="${ios_sizes[$filename]}"
                convert "$SOURCE_ICON" -resize "${size}x${size}" "$APPICON_DIR/$filename"
                print_success "Generated $filename (${size}×${size})"
            done
        else
            print_warning "ImageMagick not found - manual icon preparation required"
            print_info "Install ImageMagick: brew install imagemagick (macOS) or apt-get install imagemagick (Linux)"
            print_info "Or manually prepare icons at required sizes and place in $APPICON_DIR"
        fi
    else
        print_warning "public/icons directory not found"
        print_info "Please generate PWA icons first, then re-run this script"
    fi
    
    print_success "iOS icons installation complete"
}

# ==============================================================================
# Android Icon Installation
# ==============================================================================

install_android_icons() {
    if [ ! -d "$SCRIPT_DIR/android" ]; then
        print_warning "Skipping Android icons - project not found"
        return
    fi
    
    print_header "Installing Android Icons"
    
    # Create mipmap directories
    local DENSITIES=("mdpi" "hdpi" "xhdpi" "xxhdpi" "xxxhdpi")
    for density in "${DENSITIES[@]}"; do
        mkdir -p "$ANDROID_RES_DIR/mipmap-$density"
        print_success "Created mipmap-$density directory"
    done
    
    mkdir -p "$ANDROID_RES_DIR/mipmap-anydpi-v26"
    mkdir -p "$ANDROID_RES_DIR/values"
    print_success "Created adaptive icon directories"
    
    # Copy or generate Android icons
    local PUBLIC_ICONS="$SCRIPT_DIR/public/icons"
    
    if [ -d "$PUBLIC_ICONS" ] && command -v convert &> /dev/null; then
        print_info "Generating Android launcher icons"
        
        local SOURCE_ICON="$PUBLIC_ICONS/icon-512x512.png"
        if [ ! -f "$SOURCE_ICON" ]; then
            SOURCE_ICON="$PUBLIC_ICONS/icon-192x192.png"
        fi
        
        # Generate launcher icons for each density
        declare -A android_sizes=(
            ["mdpi"]="48"
            ["hdpi"]="72"
            ["xhdpi"]="96"
            ["xxhdpi"]="144"
            ["xxxhdpi"]="192"
        )
        
        for density in "${!android_sizes[@]}"; do
            local size="${android_sizes[$density]}"
            local output_dir="$ANDROID_RES_DIR/mipmap-$density"
            
            convert "$SOURCE_ICON" -resize "${size}x${size}" "$output_dir/ic_launcher.png"
            print_success "Generated ic_launcher.png for $density (${size}×${size})"
            
            # Copy as round icon too
            cp "$output_dir/ic_launcher.png" "$output_dir/ic_launcher_round.png"
            print_success "Generated ic_launcher_round.png for $density"
        done
        
        # Generate adaptive icon foreground layers
        print_info "Generating adaptive icon foreground layers"
        declare -A adaptive_sizes=(
            ["mdpi"]="108"
            ["hdpi"]="162"
            ["xhdpi"]="216"
            ["xxhdpi"]="324"
            ["xxxhdpi"]="432"
        )
        
        for density in "${!adaptive_sizes[@]}"; do
            local size="${adaptive_sizes[$density]}"
            local output_dir="$ANDROID_RES_DIR/mipmap-$density"
            
            # Create foreground with padding for safe zone
            convert "$SOURCE_ICON" -resize "${size}x${size}" \
                    -gravity center -background transparent \
                    -extent "${size}x${size}" \
                    "$output_dir/ic_launcher_foreground.png"
            print_success "Generated ic_launcher_foreground.png for $density (${size}×${size})"
        done
    else
        if [ ! -d "$PUBLIC_ICONS" ]; then
            print_warning "public/icons directory not found"
        fi
        if ! command -v convert &> /dev/null; then
            print_warning "ImageMagick not found"
        fi
        print_info "Manual Android icon preparation required"
    fi
    
    # Create adaptive icon XML files
    cat > "$ANDROID_RES_DIR/mipmap-anydpi-v26/ic_launcher.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
EOF
    print_success "Created ic_launcher.xml"
    
    cat > "$ANDROID_RES_DIR/mipmap-anydpi-v26/ic_launcher_round.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
EOF
    print_success "Created ic_launcher_round.xml"
    
    # Create colors.xml
    cat > "$ANDROID_RES_DIR/values/colors.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="colorPrimary">#5A3A31</color>
    <color name="colorPrimaryDark">#4A2A21</color>
    <color name="colorAccent">#8B6914</color>
    <color name="ic_launcher_background">#5A3A31</color>
</resources>
EOF
    print_success "Created colors.xml"
    
    print_success "Android icons installation complete"
}

# ==============================================================================
# Capacitor Sync
# ==============================================================================

sync_capacitor() {
    print_header "Syncing Capacitor Projects"
    
    if ! command -v npx &> /dev/null; then
        print_warning "npx not found - skipping Capacitor sync"
        print_info "Run 'npx cap sync' manually after installation"
        return
    fi
    
    print_info "Running npx cap sync..."
    if npx cap sync; then
        print_success "Capacitor sync completed successfully"
    else
        print_warning "Capacitor sync encountered issues"
        print_info "You may need to sync manually: npx cap sync"
    fi
}

# ==============================================================================
# Verification
# ==============================================================================

verify_installation() {
    print_header "Verifying Installation"
    
    local errors=0
    
    # Verify iOS
    if [ -d "$SCRIPT_DIR/ios" ]; then
        if [ -f "$IOS_DIR/AppIcon.appiconset/Contents.json" ]; then
            print_success "iOS Contents.json exists"
        else
            print_error "iOS Contents.json missing"
            ((errors++))
        fi
        
        if [ -f "$IOS_DIR/AppIcon.appiconset/icon-1024@1x.png" ]; then
            print_success "iOS App Store icon exists"
        else
            print_warning "iOS App Store icon missing"
        fi
    fi
    
    # Verify Android
    if [ -d "$SCRIPT_DIR/android" ]; then
        if [ -f "$ANDROID_RES_DIR/mipmap-xxxhdpi/ic_launcher.png" ]; then
            print_success "Android launcher icons exist"
        else
            print_error "Android launcher icons missing"
            ((errors++))
        fi
        
        if [ -f "$ANDROID_RES_DIR/mipmap-anydpi-v26/ic_launcher.xml" ]; then
            print_success "Android adaptive icon XML exists"
        else
            print_error "Android adaptive icon XML missing"
            ((errors++))
        fi
        
        if [ -f "$ANDROID_RES_DIR/values/colors.xml" ]; then
            print_success "Android colors.xml exists"
        else
            print_error "Android colors.xml missing"
            ((errors++))
        fi
    fi
    
    if [ $errors -eq 0 ]; then
        print_success "All verification checks passed!"
    else
        print_warning "$errors verification check(s) failed"
    fi
}

# ==============================================================================
# Main Execution
# ==============================================================================

main() {
    print_header "Geneva Bible Study - Capacitor Icon Setup"
    
    check_prerequisites
    install_ios_icons
    install_android_icons
    sync_capacitor
    verify_installation
    
    print_header "Setup Complete!"
    print_info "Next steps:"
    echo "  1. Open iOS project: npx cap open ios"
    echo "  2. Open Android project: npx cap open android"
    echo "  3. Verify icons appear in Xcode and Android Studio"
    echo "  4. Build and test on simulators/emulators"
    echo ""
    print_info "For detailed configuration, see CAPACITOR_ICONS_CONFIG.md"
}

# Run main function
main "$@"
