# Capacitor iOS & Android Native App Icons Configuration

## 🎯 Overview

This guide provides complete configuration for iOS and Android native app icons in your Capacitor project for Geneva Bible Study.

## 📱 Icon Requirements

### iOS Requirements
- **App Icon Sizes:** 20pt to 1024pt at various scales (@1x, @2x, @3x)
- **Format:** PNG with no transparency
- **Color Space:** sRGB or P3
- **Location:** `ios/App/App/Assets.xcassets/AppIcon.appiconset/`

### Android Requirements
- **Densities:** mdpi (48px) to xxxhdpi (192px)
- **Format:** PNG with transparency support
- **Adaptive Icons:** Foreground + Background layers (API 26+)
- **Location:** `android/app/src/main/res/mipmap-*/`

## 🗂️ Directory Structure

```
ios/App/App/Assets.xcassets/
├── AppIcon.appiconset/
│   ├── Contents.json
│   ├── icon-20@1x.png          (20×20)
│   ├── icon-20@2x.png          (40×40)
│   ├── icon-20@3x.png          (60×60)
│   ├── icon-29@1x.png          (29×29)
│   ├── icon-29@2x.png          (58×58)
│   ├── icon-29@3x.png          (87×87)
│   ├── icon-40@1x.png          (40×40)
│   ├── icon-40@2x.png          (80×80)
│   ├── icon-40@3x.png          (120×120)
│   ├── icon-60@2x.png          (120×120)
│   ├── icon-60@3x.png          (180×180)
│   ├── icon-76@1x.png          (76×76)
│   ├── icon-76@2x.png          (152×152)
│   ├── icon-83.5@2x.png        (167×167)
│   └── icon-1024@1x.png        (1024×1024)
└── Splash.imageset/
    ├── Contents.json
    └── splash.png

android/app/src/main/res/
├── mipmap-mdpi/
│   ├── ic_launcher.png         (48×48)
│   ├── ic_launcher_round.png   (48×48)
│   └── ic_launcher_foreground.png (108×108)
├── mipmap-hdpi/
│   ├── ic_launcher.png         (72×72)
│   ├── ic_launcher_round.png   (72×72)
│   └── ic_launcher_foreground.png (162×162)
├── mipmap-xhdpi/
│   ├── ic_launcher.png         (96×96)
│   ├── ic_launcher_round.png   (96×96)
│   └── ic_launcher_foreground.png (216×216)
├── mipmap-xxhdpi/
│   ├── ic_launcher.png         (144×144)
│   ├── ic_launcher_round.png   (144×144)
│   └── ic_launcher_foreground.png (324×324)
├── mipmap-xxxhdpi/
│   ├── ic_launcher.png         (192×192)
│   ├── ic_launcher_round.png   (192×192)
│   └── ic_launcher_foreground.png (432×432)
├── mipmap-anydpi-v26/
│   ├── ic_launcher.xml
│   └── ic_launcher_round.xml
└── values/
    └── colors.xml
```

## 📐 Icon Size Reference

### iOS Icon Sizes (All Scales)

| Purpose | Size | Filenames |
|---------|------|-----------|
| **Notifications** | 20pt | icon-20@2x.png (40×40), icon-20@3x.png (60×60) |
| **Settings** | 29pt | icon-29@2x.png (58×58), icon-29@3x.png (87×87) |
| **Spotlight** | 40pt | icon-40@2x.png (80×80), icon-40@3x.png (120×120) |
| **App Icon (iPhone)** | 60pt | icon-60@2x.png (120×120), icon-60@3x.png (180×180) |
| **App Icon (iPad)** | 76pt | icon-76@1x.png (76×76), icon-76@2x.png (152×152) |
| **App Icon (iPad Pro)** | 83.5pt | icon-83.5@2x.png (167×167) |
| **App Store** | 1024pt | icon-1024@1x.png (1024×1024) |

### Android Icon Densities

| Density | Scale | Size | Filename |
|---------|-------|------|----------|
| **mdpi** | 1x | 48×48 | ic_launcher.png |
| **hdpi** | 1.5x | 72×72 | ic_launcher.png |
| **xhdpi** | 2x | 96×96 | ic_launcher.png |
| **xxhdpi** | 3x | 144×144 | ic_launcher.png |
| **xxxhdpi** | 4x | 192×192 | ic_launcher.png |

### Android Adaptive Icon Sizes

| Density | Foreground Size | Background |
|---------|----------------|------------|
| **mdpi** | 108×108 | Solid color or 108×108 PNG |
| **hdpi** | 162×162 | Solid color or 162×162 PNG |
| **xhdpi** | 216×216 | Solid color or 216×216 PNG |
| **xxhdpi** | 324×324 | Solid color or 324×324 PNG |
| **xxxhdpi** | 432×432 | Solid color or 432×432 PNG |

## 🎨 Design Guidelines

### Brand Colors
```
Primary: #5A3A31 (Warm Brown)
Foreground: #F5F1EB (Cream/Parchment)
Accent: #8B6914 (Gold)
```

### Design Elements
- Open book with pages (subtle)
- Optional cross symbol (centered, minimal)
- "GENEVA" text at bottom (optional for larger sizes only)
- Gradient background for depth

### Best Practices
1. ✅ **Simple & Recognizable** - Clear at all sizes from 20px to 1024px
2. ✅ **No Small Text** - Avoid text on icons smaller than 76px
3. ✅ **High Contrast** - Ensure visibility on all backgrounds
4. ✅ **Safe Zone** - Keep critical elements within center 80%
5. ✅ **No Transparency (iOS)** - Use solid background colors
6. ✅ **Transparency OK (Android)** - Foreground layer should use transparency

## 📄 Configuration Files

### iOS Contents.json

Create `ios/App/App/Assets.xcassets/AppIcon.appiconset/Contents.json`:

```json
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
```

### Android Adaptive Icon XML

Create `android/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
```

Create `android/app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
```

### Android Colors

Create `android/app/src/main/res/values/colors.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="colorPrimary">#5A3A31</color>
    <color name="colorPrimaryDark">#4A2A21</color>
    <color name="colorAccent">#8B6914</color>
    <color name="ic_launcher_background">#5A3A31</color>
</resources>
```

### Android Manifest

Update `android/app/src/main/AndroidManifest.xml`:

```xml
<application
    android:allowBackup="true"
    android:icon="@mipmap/ic_launcher"
    android:roundIcon="@mipmap/ic_launcher_round"
    android:label="@string/app_name"
    android:supportsRtl="true"
    android:theme="@style/AppTheme">
```

## 🛠️ Installation Steps

### Step 1: Generate Icons

Use the included icon generator:

```bash
# Open the generator in browser
open generate-icons.html

# Or manually:
# - Open generate-icons.html in Chrome/Safari/Firefox
# - Click "Generate All Icons & Splash Screens"
# - Click "Download All Assets"
```

### Step 2: Install iOS Icons

```bash
# Create iOS icon directory
mkdir -p ios/App/App/Assets.xcassets/AppIcon.appiconset/

# Copy Contents.json
# (See iOS Contents.json section above)

# Copy icons (from generated assets)
# Rename according to Contents.json:
cp generated/icon-40x40.png ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-20@2x.png
cp generated/icon-60x60.png ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-20@3x.png
cp generated/icon-58x58.png ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-29@2x.png
cp generated/icon-87x87.png ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-29@3x.png
cp generated/icon-80x80.png ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-40@2x.png
cp generated/icon-120x120.png ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-40@3x.png
cp generated/icon-120x120.png ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-60@2x.png
cp generated/icon-180x180.png ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-60@3x.png
cp generated/icon-76x76.png ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-76@1x.png
cp generated/icon-152x152.png ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-76@2x.png
cp generated/icon-167x167.png ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-83.5@2x.png
cp generated/icon-1024x1024.png ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-1024@1x.png
```

### Step 3: Install Android Icons

```bash
# Create Android icon directories
mkdir -p android/app/src/main/res/mipmap-mdpi/
mkdir -p android/app/src/main/res/mipmap-hdpi/
mkdir -p android/app/src/main/res/mipmap-xhdpi/
mkdir -p android/app/src/main/res/mipmap-xxhdpi/
mkdir -p android/app/src/main/res/mipmap-xxxhdpi/
mkdir -p android/app/src/main/res/mipmap-anydpi-v26/
mkdir -p android/app/src/main/res/values/

# Copy launcher icons
cp generated/icon-48x48.png android/app/src/main/res/mipmap-mdpi/ic_launcher.png
cp generated/icon-72x72.png android/app/src/main/res/mipmap-hdpi/ic_launcher.png
cp generated/icon-96x96.png android/app/src/main/res/mipmap-xhdpi/ic_launcher.png
cp generated/icon-144x144.png android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png
cp generated/icon-192x192.png android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png

# Copy round icons (same files)
cp generated/icon-48x48.png android/app/src/main/res/mipmap-mdpi/ic_launcher_round.png
cp generated/icon-72x72.png android/app/src/main/res/mipmap-hdpi/ic_launcher_round.png
cp generated/icon-96x96.png android/app/src/main/res/mipmap-xhdpi/ic_launcher_round.png
cp generated/icon-144x144.png android/app/src/main/res/mipmap-xxhdpi/ic_launcher_round.png
cp generated/icon-192x192.png android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.png

# Copy adaptive icon foreground layers
cp generated/ic_launcher_foreground-108x108.png android/app/src/main/res/mipmap-mdpi/ic_launcher_foreground.png
cp generated/ic_launcher_foreground-162x162.png android/app/src/main/res/mipmap-hdpi/ic_launcher_foreground.png
cp generated/ic_launcher_foreground-216x216.png android/app/src/main/res/mipmap-xhdpi/ic_launcher_foreground.png
cp generated/ic_launcher_foreground-324x324.png android/app/src/main/res/mipmap-xxhdpi/ic_launcher_foreground.png
cp generated/ic_launcher_foreground-432x432.png android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_foreground.png

# Create XML files (see above)
# - ic_launcher.xml
# - ic_launcher_round.xml
# - colors.xml
```

### Step 4: Update Capacitor Config

Your `capacitor.config.ts` is already configured with icon settings. Verify:

```typescript
plugins: {
  SplashScreen: {
    launchShowDuration: 2000,
    backgroundColor: '#5A3A31',
    showSpinner: false,
    androidSplashResourceName: 'splash',
    iosSplashResourceName: 'Splash',
  }
}
```

### Step 5: Sync Capacitor

```bash
# Install Capacitor CLI if not installed
npm install -g @capacitor/cli

# Sync assets to native projects
npx cap sync ios
npx cap sync android

# Or sync both at once
npx cap sync
```

## ✅ Testing

### Test iOS Icons

```bash
# Open in Xcode
npx cap open ios

# In Xcode:
# 1. Check Assets.xcassets → AppIcon
# 2. Verify all icon sizes are present
# 3. Build and run on simulator
# 4. Check home screen icon appearance
```

### Test Android Icons

```bash
# Open in Android Studio
npx cap open android

# In Android Studio:
# 1. Check res/mipmap-* folders
# 2. Verify ic_launcher.xml adaptive icons
# 3. Build and run on emulator
# 4. Check launcher icon (try different shapes)
```

## 🐛 Troubleshooting

### iOS Issues

**Issue:** Icons not showing in Xcode
- **Fix:** Ensure Contents.json is valid JSON
- **Fix:** Verify filenames match exactly (case-sensitive)
- **Fix:** Check that icons are PNG format, not JPEG

**Issue:** App Store icon missing
- **Fix:** Must be exactly 1024×1024 pixels
- **Fix:** Must have no transparency
- **Fix:** Must be in sRGB color space

### Android Issues

**Issue:** Adaptive icons not working
- **Fix:** Ensure API level 26+ in AndroidManifest.xml
- **Fix:** Verify ic_launcher.xml syntax
- **Fix:** Check foreground images have transparency

**Issue:** Icons pixelated on device
- **Fix:** Generate icons at correct densities
- **Fix:** Don't scale from smaller sizes
- **Fix:** Use lossless PNG compression

## 📚 Resources

### Official Documentation
- [iOS Human Interface Guidelines - App Icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)
- [Android Adaptive Icons Guide](https://developer.android.com/develop/ui/views/launch/icon_design_adaptive)
- [Capacitor Icons & Splash Screens](https://capacitorjs.com/docs/guides/splash-screens-and-icons)

### Tools
- Icon Generator: `generate-icons.html` (included)
- [App Icon Generator](https://www.appicon.co/)
- [Android Asset Studio](https://romannurik.github.io/AndroidAssetStudio/)
- [iOS Icon Generator](https://appicon.co/)

## 🎉 Verification Checklist

### iOS
- [ ] All 18 icon sizes present in AppIcon.appiconset
- [ ] Contents.json valid and complete
- [ ] No Xcode warnings about missing icons
- [ ] App builds successfully
- [ ] Icon appears on simulator home screen
- [ ] Icon appears in Settings and Spotlight
- [ ] 1024×1024 App Store icon present

### Android
- [ ] Icons present in all density folders (mdpi-xxxhdpi)
- [ ] Round icon variants present
- [ ] Adaptive icon XML files created
- [ ] colors.xml with background color
- [ ] AndroidManifest.xml references ic_launcher
- [ ] App builds successfully
- [ ] Icon appears on emulator launcher
- [ ] Adaptive icon masks correctly

### Capacitor
- [ ] `npx cap sync` runs without errors
- [ ] capacitor.config.ts properly configured
- [ ] Icons visible in both iOS and Android native projects
- [ ] Splash screens configured (if applicable)

---

**Document Version:** 1.0.0  
**Last Updated:** December 2024  
**Platform:** Geneva Bible Study  
**Capacitor Version:** 6.x
