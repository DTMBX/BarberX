# App Icons & Splash Screens - Asset Checklist

## 📋 Pre-Generation Checklist

- [ ] Reviewed design specifications in [APP_ICONS_SPLASH_GUIDE.md](./APP_ICONS_SPLASH_GUIDE.md)
- [ ] Confirmed brand colors: `#5A3A31` (primary), `#F5F1EB` (text), `#8B6914` (accent)
- [ ] Have design feedback from stakeholders
- [ ] Browser for testing ready (Chrome/Safari/Firefox)

## 🎨 Generation Process

### Step 1: Generate Assets
- [ ] Open `generate-icons.html` in browser
- [ ] Click "🎨 Generate All Icons & Splash Screens" button
- [ ] Preview all icons to verify they look correct
- [ ] Preview splash screen to verify layout
- [ ] Click "📦 Download All Assets" button
- [ ] Wait for all files to download (45+ files)
- [ ] Locate INSTALLATION.md in downloads

### Step 2: Organize Downloads
- [ ] Create temporary folder for downloaded assets
- [ ] Verify all icons downloaded correctly
- [ ] Verify all splash screens downloaded
- [ ] Check that INSTALLATION.md is present

## 📦 Installation Checklist

### PWA Icons (Web App)
- [ ] Copy all `icon-*.png` files to `public/icons/`
- [ ] Copy `favicon-16x16.png` to `public/icons/`
- [ ] Copy `favicon-32x32.png` to `public/icons/`
- [ ] Copy all `shortcut-*.png` files to `public/icons/`
- [ ] Verify `manifest.json` references match filenames
- [ ] Verify `index.html` has correct favicon links

**Files to install (15 icons):**
```
public/icons/
├── favicon-16x16.png
├── favicon-32x32.png
├── icon-72x72.png
├── icon-96x96.png
├── icon-128x128.png
├── icon-144x144.png
├── icon-152x152.png
├── icon-180x180.png
├── icon-192x192.png
├── icon-384x384.png
├── icon-512x512.png
├── icon-1024x1024.png
├── shortcut-reader.png
├── shortcut-plan.png
├── shortcut-compare.png
└── shortcut-search.png
```

### Splash Screens (Web/PWA)
- [ ] Copy all `splash-*.png` files to `public/splash/`
- [ ] Update manifest.json if using splash_pages
- [ ] Test on different screen sizes

**Files to install (10 splash screens):**
```
public/splash/
├── splash-640x1136.png   (iPhone 5/SE)
├── splash-750x1334.png   (iPhone 6/7/8)
├── splash-1125x2436.png  (iPhone X/XS)
├── splash-1242x2208.png  (iPhone 6+/7+/8+)
├── splash-1242x2688.png  (iPhone XS Max)
├── splash-828x1792.png   (iPhone XR)
├── splash-1170x2532.png  (iPhone 12/13)
├── splash-1284x2778.png  (iPhone 12/13 Pro Max)
├── splash-1536x2048.png  (iPad)
└── splash-2048x2732.png  (iPad Pro)
```

### iOS Icons (Capacitor/Native)
- [ ] Create `ios/App/App/Assets.xcassets/AppIcon.appiconset/` directory
- [ ] Copy `ios-appicon-contents-template.json` as `Contents.json`
- [ ] Rename and copy icons according to Contents.json:
  - [ ] icon-20.png (20×20)
  - [ ] icon-20@2x.png (40×40)
  - [ ] icon-20@3x.png (60×60)
  - [ ] icon-29.png (29×29)
  - [ ] icon-29@2x.png (58×58)
  - [ ] icon-29@3x.png (87×87)
  - [ ] icon-40.png (40×40)
  - [ ] icon-40@2x.png (80×80)
  - [ ] icon-40@3x.png (120×120)
  - [ ] icon-60@2x.png (120×120)
  - [ ] icon-60@3x.png (180×180)
  - [ ] icon-76.png (76×76)
  - [ ] icon-76@2x.png (152×152)
  - [ ] icon-83.5@2x.png (167×167)
  - [ ] icon-1024.png (1024×1024)
- [ ] Open project in Xcode
- [ ] Verify AppIcon shows in asset catalog
- [ ] Build and test on simulator

### iOS Splash Screens (Capacitor/Native)
- [ ] Create `ios/App/App/Assets.xcassets/Splash.imageset/` directory
- [ ] Copy splash screens with device-specific names
- [ ] Create Contents.json for Splash imageset
- [ ] Verify splash shows on app launch
- [ ] Test on multiple device sizes

### Android Icons (Capacitor/Native)
- [ ] Create all mipmap directories:
  - [ ] `android/app/src/main/res/mipmap-mdpi/`
  - [ ] `android/app/src/main/res/mipmap-hdpi/`
  - [ ] `android/app/src/main/res/mipmap-xhdpi/`
  - [ ] `android/app/src/main/res/mipmap-xxhdpi/`
  - [ ] `android/app/src/main/res/mipmap-xxxhdpi/`
- [ ] Copy and rename icons:
  - [ ] mipmap-mdpi/ic_launcher.png (48×48) - resize icon-72x72.png
  - [ ] mipmap-hdpi/ic_launcher.png (72×72) - use icon-72x72.png
  - [ ] mipmap-xhdpi/ic_launcher.png (96×96) - use icon-96x96.png
  - [ ] mipmap-xxhdpi/ic_launcher.png (144×144) - use icon-144x144.png
  - [ ] mipmap-xxxhdpi/ic_launcher.png (192×192) - use icon-192x192.png
- [ ] Copy round icon variants (same sizes)
- [ ] Update AndroidManifest.xml to reference ic_launcher
- [ ] Copy `android-colors-template.xml` to `res/values/colors.xml`
- [ ] Build and test on emulator

### Android Splash Screens (Capacitor/Native)
- [ ] Create `android/app/src/main/res/drawable/` directory
- [ ] Copy main splash screen:
  - [ ] drawable/splash.png (use splash-1242x2688.png)
- [ ] Update capacitor.config.ts with splash settings
- [ ] Test splash on app launch
- [ ] Verify orientation handling

### Adaptive Icons (Android API 26+)
- [ ] Create `mipmap-anydpi-v26/` directory
- [ ] Copy `android-adaptive-icon-template.xml` as `ic_launcher.xml`
- [ ] Create foreground and background layers
- [ ] Test adaptive icon masking
- [ ] Verify on Android 8.0+ devices

## ✅ Testing Checklist

### PWA Testing (All Platforms)
- [ ] **Chrome (Desktop)**
  - [ ] Open app in Chrome
  - [ ] Check DevTools → Application → Manifest
  - [ ] Verify all icons load without 404s
  - [ ] Test "Install App" button
  - [ ] Verify installed icon looks correct
  - [ ] Test app shortcuts (right-click icon)
- [ ] **Chrome (Android)**
  - [ ] Open app in Chrome on Android
  - [ ] Test "Add to Home Screen"
  - [ ] Verify icon on home screen
  - [ ] Test adaptive icon masking
  - [ ] Verify shortcuts work
- [ ] **Safari (iOS)**
  - [ ] Open app in Safari
  - [ ] Share → Add to Home Screen
  - [ ] Verify icon on home screen
  - [ ] Test app launch
  - [ ] Verify splash screen (if supported)
- [ ] **Safari (macOS)**
  - [ ] Open app in Safari
  - [ ] Install PWA
  - [ ] Verify dock icon
  - [ ] Test app shortcuts
- [ ] **Edge (Windows)**
  - [ ] Open app in Edge
  - [ ] Install app
  - [ ] Verify Start Menu tile
  - [ ] Test taskbar icon
  - [ ] Check Windows widget compatibility

### iOS Native Testing (Capacitor)
- [ ] **iPhone Simulator**
  - [ ] Build and run app
  - [ ] Verify app icon on home screen
  - [ ] Check icon in multiple sizes (Settings, Spotlight)
  - [ ] Test splash screen
  - [ ] Verify splash screen orientation
- [ ] **iPad Simulator**
  - [ ] Build and run app
  - [ ] Verify app icon
  - [ ] Test multitasking icon appearance
  - [ ] Test splash screen
- [ ] **Physical iPhone**
  - [ ] Deploy via TestFlight or development
  - [ ] Verify icon quality (no pixelation)
  - [ ] Test splash screen
  - [ ] Test on multiple models (if possible)
- [ ] **Physical iPad**
  - [ ] Deploy and test
  - [ ] Verify icon quality
  - [ ] Test splash screen

### Android Native Testing (Capacitor)
- [ ] **Android Emulator (Multiple Densities)**
  - [ ] Test on mdpi emulator
  - [ ] Test on hdpi emulator
  - [ ] Test on xhdpi emulator
  - [ ] Test on xxhdpi emulator
  - [ ] Test on xxxhdpi emulator
- [ ] **Android Emulator (Adaptive Icons)**
  - [ ] Test on Android 8.0 (API 26)
  - [ ] Test on Android 9.0 (API 28)
  - [ ] Test on Android 11+ (latest)
  - [ ] Verify round icon support
  - [ ] Test icon masking
- [ ] **Physical Android Device**
  - [ ] Deploy via APK or Play Store
  - [ ] Verify launcher icon
  - [ ] Test splash screen
  - [ ] Test on multiple manufacturers (Samsung, Pixel, etc.)

### Browser Compatibility
- [ ] Chrome (Desktop & Mobile)
- [ ] Safari (iOS & macOS)
- [ ] Firefox (Desktop & Mobile)
- [ ] Edge (Desktop & Mobile)
- [ ] Samsung Internet (Android)

### Icon Quality Checks
- [ ] No pixelation at any size
- [ ] Colors match brand guidelines
- [ ] Text is legible at small sizes (if applicable)
- [ ] Icon is recognizable at 16×16
- [ ] Icon looks professional at 512×512
- [ ] Safe zone respected (center 80%)
- [ ] No important elements cut off
- [ ] Consistent visual style across sizes

### Splash Screen Quality Checks
- [ ] Centered properly on all devices
- [ ] Colors match brand
- [ ] Text is legible
- [ ] Displays for appropriate duration (2-3s)
- [ ] Smooth transition to app
- [ ] No flashing or flickering
- [ ] Orientation handled correctly

## 📊 Lighthouse Audit

After installation, run Lighthouse to verify:

```bash
# Install Lighthouse CLI (if not installed)
npm install -g @lhci/cli

# Run Lighthouse audit
lhci autorun

# Or use Chrome DevTools → Lighthouse
```

**Check these metrics:**
- [ ] PWA installability score: 100%
- [ ] All icon sizes present
- [ ] Manifest correctly configured
- [ ] Apple touch icon present
- [ ] Favicon present
- [ ] No console errors for missing icons

## 🎯 Acceptance Criteria

All items must be checked before marking as complete:

### PWA
- [ ] All 11 icon sizes generated and installed
- [ ] Favicons (16×16, 32×32) present
- [ ] Apple touch icon (180×180) present
- [ ] Manifest.json correctly references all icons
- [ ] PWA installs successfully on all tested browsers
- [ ] Home screen icon looks professional
- [ ] App shortcuts have custom icons

### iOS Native
- [ ] All required icon sizes present (18 files)
- [ ] AppIcon.appiconset properly configured
- [ ] App Store icon (1024×1024) present
- [ ] Splash screens for all devices
- [ ] Xcode shows no icon warnings
- [ ] App builds and runs successfully
- [ ] Icons look sharp on Retina displays

### Android Native
- [ ] All density buckets covered (mdpi-xxxhdpi)
- [ ] Adaptive icon configured (API 26+)
- [ ] Round icon variant present
- [ ] Splash screen configured
- [ ] AndroidManifest.xml updated
- [ ] App builds and runs successfully
- [ ] Icons adapt to launcher theme

### Documentation
- [ ] INSTALLATION.md included in downloads
- [ ] Team knows how to regenerate icons if needed
- [ ] Asset sources documented
- [ ] Color values documented

## 🚀 Deployment Checklist

### GitHub Pages (PWA)
- [ ] Icons in `public/icons/` directory
- [ ] Splash screens in `public/splash/` directory
- [ ] Manifest.json updated
- [ ] Build passes: `npm run build`
- [ ] Test dist output locally
- [ ] Deploy to GitHub Pages
- [ ] Verify icons load on deployed site

### App Store (iOS)
- [ ] All icons in Xcode Assets.xcassets
- [ ] App Store icon (1024×1024) present
- [ ] Build succeeds in Xcode
- [ ] Archive created successfully
- [ ] Upload to App Store Connect
- [ ] Icons appear in App Store Connect
- [ ] App Store listing shows correct icon

### Google Play (Android)
- [ ] All density icons present in res/
- [ ] Adaptive icon configured
- [ ] Signed APK/AAB builds successfully
- [ ] Upload to Play Console
- [ ] Feature graphic uploaded (1024×500)
- [ ] Play Store listing shows correct icon
- [ ] Internal test track verified

## 📝 Post-Deployment Verification

- [ ] PWA installs with correct icon from production URL
- [ ] iOS app shows correct icon in TestFlight/App Store
- [ ] Android app shows correct icon in Play Store
- [ ] No user reports of icon issues
- [ ] Analytics show successful PWA installations
- [ ] App store reviews don't mention icon issues

## 🎉 Success!

Once all items are checked:
- [ ] Create GitHub release with icon assets
- [ ] Update project documentation
- [ ] Notify team of completion
- [ ] Archive source files for future updates
- [ ] Document any custom modifications made

---

**Checklist Version:** 1.0.0
**Last Updated:** December 2024
**Platform:** Geneva Bible Study
