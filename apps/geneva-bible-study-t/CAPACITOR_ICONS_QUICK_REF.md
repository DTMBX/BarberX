# Capacitor Native App Icons - Quick Reference

## 🚀 Quick Setup (3 Steps)

### Step 1: Generate Icons
```bash
# Open the icon generator in your browser
open generate-icons.html
# Click "Generate All Icons & Splash Screens"
# Click "Download All Assets"
```

### Step 2: Run Setup Script
```bash
# macOS/Linux
chmod +x setup-capacitor-icons.sh
./setup-capacitor-icons.sh

# Windows
setup-capacitor-icons.bat
```

### Step 3: Sync & Build
```bash
npx cap sync
npx cap open ios     # Verify in Xcode
npx cap open android # Verify in Android Studio
```

---

## 📱 Required Icon Sizes at a Glance

### iOS (18 icons)
```
20×20 @2x, @3x    → Notifications
29×29 @2x, @3x    → Settings
40×40 @2x, @3x    → Spotlight
60×60 @2x, @3x    → iPhone App
76×76 @1x, @2x    → iPad App
83.5×83.5 @2x     → iPad Pro
1024×1024 @1x     → App Store ⭐
```

### Android (5 densities × 3 variants = 15+ files)
```
mdpi:    48×48    (1x)
hdpi:    72×72    (1.5x)
xhdpi:   96×96    (2x)
xxhdpi:  144×144  (3x)
xxxhdpi: 192×192  (4x)

For each density:
- ic_launcher.png
- ic_launcher_round.png
- ic_launcher_foreground.png (adaptive)
```

---

## 📂 File Structure Reference

### iOS
```
ios/App/App/Assets.xcassets/
└── AppIcon.appiconset/
    ├── Contents.json ← Configuration file
    ├── icon-20@2x.png (40×40)
    ├── icon-20@3x.png (60×60)
    ├── icon-29@2x.png (58×58)
    ├── icon-29@3x.png (87×87)
    ├── icon-40@2x.png (80×80)
    ├── icon-40@3x.png (120×120)
    ├── icon-60@2x.png (120×120)
    ├── icon-60@3x.png (180×180)
    ├── icon-76@1x.png (76×76)
    ├── icon-76@2x.png (152×152)
    ├── icon-83.5@2x.png (167×167)
    └── icon-1024@1x.png (1024×1024) ⭐
```

### Android
```
android/app/src/main/res/
├── mipmap-mdpi/
│   ├── ic_launcher.png (48×48)
│   ├── ic_launcher_round.png
│   └── ic_launcher_foreground.png (108×108)
├── mipmap-hdpi/ (same files, 72×72, 162×162)
├── mipmap-xhdpi/ (96×96, 216×216)
├── mipmap-xxhdpi/ (144×144, 324×324)
├── mipmap-xxxhdpi/ (192×192, 432×432)
├── mipmap-anydpi-v26/
│   ├── ic_launcher.xml ← Adaptive icon config
│   └── ic_launcher_round.xml
└── values/
    └── colors.xml ← Background color
```

---

## 🎨 Design Specs

### Colors (Geneva Bible Study)
```css
Primary:   #5A3A31  (Warm Brown)
Text:      #F5F1EB  (Cream/Parchment)
Accent:    #8B6914  (Gold)
```

### Design Rules
- ✅ **Safe Zone:** Keep critical elements in center 80%
- ✅ **Simplicity:** Recognizable at 20px
- ✅ **No Transparency (iOS):** Use solid backgrounds
- ✅ **Transparency OK (Android):** Foreground layer
- ✅ **No Small Text:** Avoid text on icons < 76px

---

## ⚡ Common Commands

```bash
# Add native platforms (if not done)
npx cap add ios
npx cap add android

# Sync after icon changes
npx cap sync

# Open in native IDEs
npx cap open ios
npx cap open android

# Build web assets first
npm run build

# Full rebuild
npm run build && npx cap sync && npx cap copy
```

---

## ✅ Verification Checklist

### Before Building
- [ ] All iOS icon sizes present (18 files)
- [ ] iOS Contents.json valid
- [ ] All Android densities present (5 folders)
- [ ] Android adaptive icon XMLs created
- [ ] colors.xml with background color

### In Xcode (iOS)
- [ ] Open project: `npx cap open ios`
- [ ] Check Assets.xcassets → AppIcon
- [ ] No yellow warnings about missing sizes
- [ ] Build succeeds
- [ ] Icon appears on simulator home screen

### In Android Studio
- [ ] Open project: `npx cap open android`
- [ ] Check res/mipmap-* folders
- [ ] Verify ic_launcher.xml exists
- [ ] Build succeeds (Build → Make Project)
- [ ] Icon appears on emulator launcher
- [ ] Test adaptive icon (try different launcher shapes)

---

## 🐛 Quick Troubleshooting

### iOS Icons Not Showing
```bash
# 1. Verify Contents.json syntax
cat ios/App/App/Assets.xcassets/AppIcon.appiconset/Contents.json | python -m json.tool

# 2. Check file names match exactly (case-sensitive!)
ls -la ios/App/App/Assets.xcassets/AppIcon.appiconset/

# 3. Re-sync Capacitor
npx cap sync ios
```

### Android Icons Not Showing
```bash
# 1. Verify all densities present
ls android/app/src/main/res/mipmap-*/ic_launcher.png

# 2. Check XML syntax
cat android/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml

# 3. Clean and rebuild in Android Studio
# Build → Clean Project
# Build → Rebuild Project
```

### Icon Quality Issues
- **Pixelated:** Generate icons at correct sizes, don't scale up
- **Wrong colors:** Check source icon colors match brand
- **Clipped edges:** Ensure safe zone respected (center 80%)

---

## 📝 Manual Icon Creation (Alternative)

If you prefer manual control:

### Using ImageMagick (Command Line)
```bash
# Install ImageMagick
brew install imagemagick  # macOS
apt-get install imagemagick  # Linux

# Create iOS icons from 1024×1024 source
convert icon-1024.png -resize 40x40 icon-20@2x.png
convert icon-1024.png -resize 60x60 icon-20@3x.png
# ... repeat for all sizes

# Create Android icons
convert icon-1024.png -resize 48x48 mipmap-mdpi/ic_launcher.png
convert icon-1024.png -resize 72x72 mipmap-hdpi/ic_launcher.png
# ... repeat for all densities
```

### Using Online Tools
- [App Icon Generator](https://www.appicon.co/) - Upload 1024×1024, get all sizes
- [Icon Kitchen](https://icon.kitchen/) - Android adaptive icons
- [Make App Icon](https://makeappicon.com/) - iOS & Android bundle

---

## 📚 Full Documentation

For complete details, see:
- **[CAPACITOR_ICONS_CONFIG.md](./CAPACITOR_ICONS_CONFIG.md)** - Complete configuration guide
- **[APP_ICONS_SPLASH_GUIDE.md](./APP_ICONS_SPLASH_GUIDE.md)** - Design guidelines
- **[ICONS_CHECKLIST.md](./ICONS_CHECKLIST.md)** - Detailed checklist

---

## 🎯 Icon Size Calculator

| iOS Size | @1x | @2x | @3x |
|----------|-----|-----|-----|
| 20pt | 20px | 40px | 60px |
| 29pt | 29px | 58px | 87px |
| 40pt | 40px | 80px | 120px |
| 60pt | - | 120px | 180px |
| 76pt | 76px | 152px | - |
| 83.5pt | - | 167px | - |

| Android Density | Scale | 48dp Base |
|----------------|-------|-----------|
| mdpi | 1× | 48px |
| hdpi | 1.5× | 72px |
| xhdpi | 2× | 96px |
| xxhdpi | 3× | 144px |
| xxxhdpi | 4× | 192px |

---

## 💡 Pro Tips

1. **Start with 1024×1024** - Create your icon at the largest size first
2. **Test on Real Devices** - Simulators don't always match real device appearance
3. **Check All Backgrounds** - Test icon on light/dark launcher backgrounds
4. **App Store Screenshots** - Need 1024×1024 for App Store listing too
5. **Adaptive Icons** - Android 8+ supports animated adaptive icons (advanced)
6. **PWA First** - Test icon as PWA before native builds

---

## 🔗 Resources

**Official Docs:**
- [iOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/app-icons)
- [Android Adaptive Icons](https://developer.android.com/develop/ui/views/launch/icon_design_adaptive)
- [Capacitor Documentation](https://capacitorjs.com/docs/guides/splash-screens-and-icons)

**Design Tools:**
- Figma, Sketch, Adobe XD - Icon design
- [Pixelmator](https://www.pixelmator.com/) - Icon editing (Mac)
- [GIMP](https://www.gimp.org/) - Free alternative

**Testing:**
- [App Store Connect](https://appstoreconnect.apple.com/) - iOS submission
- [Google Play Console](https://play.google.com/console) - Android submission

---

**Last Updated:** December 2024  
**Version:** 1.0.0  
**Project:** Geneva Bible Study
