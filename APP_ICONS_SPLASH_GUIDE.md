# App Icons & Splash Screens Setup Guide

## 🎨 Overview

This guide covers the complete setup of app icons and splash screens for Geneva Bible Study across all platforms: iOS, Android, PWA, and Desktop.

## 📦 Quick Start

### Generate All Assets

1. **Open the Icon Generator:**
   ```bash
   # Open in your browser
   open generate-icons.html
   # or
   firefox generate-icons.html
   # or
   chrome generate-icons.html
   ```

2. **Generate Icons:**
   - Click "🎨 Generate All Icons & Splash Screens"
   - Wait for generation to complete
   - Click "📦 Download All Assets (ZIP)"

3. **Install Assets:**
   - Follow the INSTALLATION.md instructions in the downloaded files
   - Copy icons to appropriate directories (see below)

## 📱 Platform-Specific Requirements

### PWA (Progressive Web App)

**Location:** `public/icons/`

**Required Icons:**
- ✅ 72×72 - Android Chrome
- ✅ 96×96 - Android Chrome  
- ✅ 128×128 - Android Chrome
- ✅ 144×144 - Android Chrome, MS Tile
- ✅ 152×152 - iPad touch icon
- ✅ 180×180 - iPhone Retina
- ✅ 192×192 - Android Chrome
- ✅ 384×384 - Android Chrome
- ✅ 512×512 - Android Chrome, Splash

**Manifest Configuration:**
```json
{
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

**HTML Meta Tags:**
```html
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32x32.png" />
<link rel="icon" type="image/png" sizes="16x16" href="/icons/favicon-16x16.png" />
<link rel="apple-touch-icon" href="/icons/icon-180x180.png" />
```

### iOS (Capacitor Native App)

**App Icon Location:** `ios/App/App/Assets.xcassets/AppIcon.appiconset/`

**Required Sizes:**
- 20×20 (iPhone Notification) @2x, @3x
- 29×29 (iPhone Settings) @2x, @3x
- 40×40 (iPhone Spotlight) @2x, @3x
- 60×60 (iPhone App) @2x, @3x
- 76×76 (iPad App) @1x, @2x
- 83.5×83.5 (iPad Pro)
- 1024×1024 (App Store)

**Splash Screen Location:** `ios/App/App/Assets.xcassets/Splash.imageset/`

**Required Splash Screens:**
- 640×1136 - iPhone 5/SE
- 750×1334 - iPhone 6/7/8
- 1125×2436 - iPhone X/XS/11 Pro
- 1242×2208 - iPhone 6/7/8 Plus
- 1242×2688 - iPhone XS Max/11 Pro Max
- 828×1792 - iPhone XR/11
- 1170×2532 - iPhone 12/13 Pro
- 1284×2778 - iPhone 12/13 Pro Max
- 1536×2048 - iPad 9.7"/10.5"
- 2048×2732 - iPad Pro 12.9"

**Xcode Configuration:**
1. Open `ios/App/App.xcworkspace` in Xcode
2. Select App target → General → App Icons and Launch Images
3. Set App Icon Source to "AppIcon"
4. Set Launch Screen File to "Splash"

### Android (Capacitor Native App)

**Icon Location:** `android/app/src/main/res/`

**Required Mipmap Directories:**
```
mipmap-mdpi/     (48×48)   - icon-72x72.png resized
mipmap-hdpi/     (72×72)   - icon-72x72.png
mipmap-xhdpi/    (96×96)   - icon-96x96.png
mipmap-xxhdpi/   (144×144) - icon-144x144.png
mipmap-xxxhdpi/  (192×192) - icon-192x192.png
```

**Splash Screen Location:** `android/app/src/main/res/drawable/`

**Files Needed:**
- `splash.png` (main splash, use 1242×2688)
- `splash_portrait.png`
- `splash_landscape.png`

**Android Manifest Configuration:**
```xml
<application
    android:icon="@mipmap/ic_launcher"
    android:roundIcon="@mipmap/ic_launcher_round"
    android:label="@string/app_name"
    android:theme="@style/AppTheme.NoActionBarLaunch">
    
    <meta-data
        android:name="com.google.android.gms.ads.APPLICATION_ID"
        android:value="@string/app_id"/>
</application>
```

### Desktop (Windows Widget)

**Icon Location:** `public/icons/`

**Recommended:**
- Use icon-512x512.png for highest quality
- Convert to .ico format for native Windows apps
- Include in electron configuration if using Electron

## 🎨 Design Specifications

### App Icon Design

**Primary Colors:**
- Background: `#5A3A31` (warm brown)
- Foreground: `#F5F1EB` (cream/parchment)
- Accent: `#8B6914` (gold)

**Design Elements:**
- Open book representation
- Cross symbol (subtle, centered)
- "GENEVA" text at bottom
- Gradient background for depth

**Best Practices:**
- ✅ Simple, recognizable at small sizes
- ✅ No text smaller than 10% of icon size
- ✅ High contrast elements
- ✅ Avoid gradients for small sizes (<72px)
- ✅ Safe zone: Keep important elements in center 80%

### Splash Screen Design

**Layout:**
- Vertical gradient background
- Centered app icon (30% of screen height)
- "GENEVA BIBLE STUDY" title below icon
- "Explore Scripture Together" subtitle
- 2-3 second display duration

**Colors:**
- Gradient from `#6B4A3A` → `#5A3A31` → `#4A2A21`
- Text: `#F5F1EB` (cream)
- Subtitle: `rgba(245, 241, 235, 0.7)` (70% opacity)

## 🔧 Capacitor Configuration

**capacitor.config.ts:**
```typescript
plugins: {
  SplashScreen: {
    launchShowDuration: 2000,
    backgroundColor: '#5A3A31',
    showSpinner: false,
    androidSpinnerStyle: 'small',
    iosSpinnerStyle: 'small',
    androidSplashResourceName: 'splash',
    iosSplashResourceName: 'Splash'
  }
}
```

## 📋 Asset Checklist

### PWA Assets
- [ ] favicon-16x16.png
- [ ] favicon-32x32.png
- [ ] icon-72x72.png
- [ ] icon-96x96.png
- [ ] icon-128x128.png
- [ ] icon-144x144.png
- [ ] icon-152x152.png
- [ ] icon-180x180.png (Apple touch)
- [ ] icon-192x192.png
- [ ] icon-384x384.png
- [ ] icon-512x512.png

### iOS Assets
- [ ] AppIcon.appiconset (all sizes)
- [ ] Splash.imageset (all device sizes)
- [ ] Contents.json files

### Android Assets
- [ ] mipmap-mdpi/ic_launcher.png
- [ ] mipmap-hdpi/ic_launcher.png
- [ ] mipmap-xhdpi/ic_launcher.png
- [ ] mipmap-xxhdpi/ic_launcher.png
- [ ] mipmap-xxxhdpi/ic_launcher.png
- [ ] drawable/splash.png

### Shortcut Icons
- [ ] shortcut-reader.png (📖 blue)
- [ ] shortcut-plan.png (📅 green)
- [ ] shortcut-compare.png (🔍 amber)
- [ ] shortcut-search.png (🔎 teal)

## 🧪 Testing

### PWA Icons
1. Open app in Chrome DevTools
2. Application → Manifest
3. Verify all icon sizes load
4. Test "Add to Home Screen"
5. Check icon appearance on home screen

### iOS Testing
1. Build and run on iOS Simulator
2. Check app icon on home screen
3. Test splash screen on launch
4. Verify different device sizes
5. Test on physical device

### Android Testing
1. Build and run on Android Emulator
2. Check launcher icon (round and square)
3. Test splash screen
4. Verify adaptive icon behavior
5. Test on physical device (multiple vendors)

## 🚀 Deployment

### GitHub Pages (PWA)
Icons are automatically included in the build:
```bash
npm run build
```

Icons in `public/icons/` are copied to `dist/icons/`

### App Store (iOS)
1. Generate icons with generator tool
2. Copy to Xcode Assets.xcassets
3. Build archive in Xcode
4. Upload to App Store Connect
5. Icons automatically included

### Google Play (Android)
1. Generate icons with generator tool
2. Copy to appropriate res/ directories
3. Build signed APK/AAB
4. Upload to Google Play Console
5. Feature graphic (1024×500) needed separately

## 📐 Icon Sizes Reference

### iOS Sizes
| Size | Scale | Usage |
|------|-------|-------|
| 20pt | 2x, 3x | Notification |
| 29pt | 2x, 3x | Settings |
| 40pt | 2x, 3x | Spotlight |
| 60pt | 2x, 3x | App Icon |
| 76pt | 1x, 2x | iPad |
| 83.5pt | 2x | iPad Pro |
| 1024pt | 1x | App Store |

### Android Densities
| Density | Scale | Size |
|---------|-------|------|
| mdpi | 1x | 48×48 |
| hdpi | 1.5x | 72×72 |
| xhdpi | 2x | 96×96 |
| xxhdpi | 3x | 144×144 |
| xxxhdpi | 4x | 192×192 |

## 🎯 Best Practices

### Icon Design
1. **Simplicity** - Clear at 16×16, detailed at 512×512
2. **Consistency** - Same visual language across sizes
3. **Contrast** - Ensure visibility on all backgrounds
4. **Testing** - View at actual size on real devices
5. **Accessibility** - Avoid relying only on color

### Splash Screens
1. **Speed** - Show for 2-3 seconds maximum
2. **Branding** - Match app icon design
3. **Orientation** - Provide portrait and landscape
4. **Loading** - No loading indicators on splash
5. **Simplicity** - Minimal text and elements

### Performance
1. **Optimize PNGs** - Use tools like pngquant
2. **Correct Formats** - PNG for transparency
3. **File Sizes** - Keep under 100KB per icon
4. **Caching** - Icons cached by OS/browser
5. **Variants** - Provide all required sizes

## 🔗 Resources

### Tools
- **Icon Generator** - `generate-icons.html` (included)
- **Image Optimization** - [TinyPNG](https://tinypng.com)
- **iOS Asset Catalog** - Xcode built-in
- **Android Asset Studio** - [Android Studio](https://developer.android.com/studio)

### Documentation
- [PWA Icons Guide](https://web.dev/app-manifest/)
- [iOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/ios/icons-and-images/app-icon/)
- [Android Icon Guidelines](https://developer.android.com/guide/practices/ui_guidelines/icon_design_launcher)
- [Capacitor Icons & Splash](https://capacitorjs.com/docs/guides/splash-screens-and-icons)

### Validation
- [PWA Manifest Validator](https://manifest-validator.appspot.com/)
- Chrome DevTools → Application → Manifest
- Lighthouse audit (checks icon sizes)

## 📝 Notes

### Adaptive Icons (Android)
Android 8.0+ supports adaptive icons with foreground and background layers. For best results:
- Provide 108dp icons (foreground + background)
- Safe zone is inner 72dp circle
- Background can be color or image
- Foreground should have transparency

### Maskable Icons (PWA)
PWA icons can be masked to different shapes:
```json
"purpose": "any maskable"
```
- Keep important content in center 40% circle
- Provide bleed area for masking
- Test with different mask shapes

### Dark Mode Icons
Consider providing separate icons for dark mode:
```html
<link rel="icon" media="(prefers-color-scheme: light)" href="/icons/icon-light.png">
<link rel="icon" media="(prefers-color-scheme: dark)" href="/icons/icon-dark.png">
```

## 🆘 Troubleshooting

### Icons Not Appearing
1. Clear browser cache
2. Check file paths in manifest.json
3. Verify MIME types (image/png)
4. Check file permissions
5. Validate manifest JSON syntax

### Splash Screen Issues
1. Check capacitor.config.ts settings
2. Verify file names match config
3. Rebuild native projects
4. Clean build folders
5. Check device orientation settings

### Size Mismatches
1. Use exact pixel dimensions
2. Don't resize existing icons
3. Regenerate from source
4. Check aspect ratios
5. Verify DPI settings

## ✅ Verification

After installation, verify:

```bash
# Check PWA icons exist
ls public/icons/*.png

# Verify manifest references
cat public/manifest.json | grep "icons"

# Check iOS assets (if using Capacitor)
ls ios/App/App/Assets.xcassets/AppIcon.appiconset/

# Check Android assets (if using Capacitor)
ls android/app/src/main/res/mipmap-*/
```

## 🎉 Success Criteria

Your app icons are properly configured when:

✅ PWA can be installed with correct icon
✅ iOS home screen shows app icon (all sizes)
✅ Android launcher shows app icon (all densities)
✅ Splash screens appear on native app launch
✅ Favicons appear in browser tabs
✅ PWA shortcuts have custom icons
✅ All Lighthouse icon audits pass
✅ Icons look crisp on all devices

---

**Generated:** December 2024
**Version:** 1.0.0
**Platform:** Geneva Bible Study
**Maintainer:** Development Team
