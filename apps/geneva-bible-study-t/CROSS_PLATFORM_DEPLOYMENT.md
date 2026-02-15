# Cross-Platform Deployment & Distribution Guide

Complete guide for deploying Geneva Bible Study across all platforms: Web, iOS, Android, Windows, macOS, and Linux.

## 📋 Table of Contents

1. [Web Deployment](#web-deployment)
2. [Mobile Deployment (iOS & Android)](#mobile-deployment)
3. [Desktop Applications](#desktop-applications)
4. [Distribution Channels](#distribution-channels)
5. [Continuous Deployment](#continuous-deployment)

---

## 🌐 Web Deployment

### Option 1: GitHub Pages (Current - Automated)

**Status**: ✅ Configured and Ready

**Deployment Process**:
```bash
# Automatic deployment on push to main
git add .
git commit -m "Your changes"
git push origin main

# GitHub Actions automatically:
# 1. Builds the application
# 2. Runs Lighthouse tests
# 3. Deploys to GitHub Pages
# 4. Available at: https://YOUR_USERNAME.github.io/YOUR_REPO/
```

**Configuration Files**:
- `.github/workflows/deploy.yml` - Deployment workflow
- `.github/workflows/lighthouse-ci.yml` - Performance testing
- `vite.config.ts` - Build configuration
- `package.json` - Scripts and dependencies

**Setup Steps**:
1. Update `vite.config.ts` with your repo name
2. Update `package.json` repository URLs
3. Enable GitHub Pages in repository settings
4. Push to main branch

**Documentation**: See [GITHUB_PAGES_DEPLOYMENT.md](./GITHUB_PAGES_DEPLOYMENT.md)

---

### Option 2: Custom Domain

**Steps**:
1. **Update Vite Config**:
```typescript
// vite.config.ts
export default defineConfig({
  base: '/', // Change from '/spark-template/'
  // ... rest of config
});
```

2. **Add CNAME File**:
```bash
echo "yourdomain.com" > public/CNAME
```

3. **Configure DNS**:
```
Type: CNAME
Name: www
Value: YOUR_USERNAME.github.io

Type: A (for root domain)
Name: @
Value: 185.199.108.153
Value: 185.199.109.153
Value: 185.199.110.153
Value: 185.199.111.153
```

4. **Enable HTTPS** in GitHub Pages settings

---

### Option 3: Vercel (Zero-Config Deployment)

**Steps**:
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Deploy to production
vercel --prod
```

**Features**:
- ✅ Automatic HTTPS
- ✅ Edge network (fast worldwide)
- ✅ Preview deployments for PRs
- ✅ Custom domains
- ✅ Analytics

**Configuration**: Create `vercel.json`:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

---

### Option 4: Netlify

**Steps**:
1. Connect GitHub repository
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Deploy

**Features**:
- ✅ Continuous deployment
- ✅ Form handling
- ✅ Serverless functions
- ✅ Split testing
- ✅ Custom headers

**Configuration**: Create `netlify.toml`:
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

### Option 5: Cloudflare Pages

**Steps**:
1. Connect GitHub repository
2. Framework preset: Vite
3. Build command: `npm run build`
4. Build output: `dist`

**Features**:
- ✅ Free unlimited bandwidth
- ✅ Global CDN
- ✅ Web analytics
- ✅ Edge computing

---

### Option 6: Firebase Hosting

**Steps**:
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize
firebase init hosting

# Deploy
firebase deploy
```

**Configuration**: `firebase.json`:
```json
{
  "hosting": {
    "public": "dist",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

---

## 📱 Mobile Deployment

### Progressive Web App (PWA) - Current Method

**iOS Installation**:
1. Open app in Safari
2. Tap Share button
3. Select "Add to Home Screen"
4. App installs as standalone app

**Android Installation**:
1. Open app in Chrome
2. Tap "Install" banner
3. Or: Menu → "Install app"
4. App installs with icon

**Features**:
- ✅ No app store approval needed
- ✅ Instant updates
- ✅ Cross-platform
- ✅ Smaller download size
- ⚠️ Limited OS integration

---

### Native App Wrappers (Future Enhancement)

#### Capacitor - Recommended Approach

**Installation**:
```bash
# Install Capacitor
npm install @capacitor/core @capacitor/cli
npm install @capacitor/ios @capacitor/android

# Initialize
npx cap init "Geneva Bible Study" "com.genevabible.study"

# Build web assets
npm run build

# Add platforms
npx cap add ios
npx cap add android
```

**iOS Build**:
```bash
# Open in Xcode
npx cap open ios

# In Xcode:
# 1. Configure signing & capabilities
# 2. Select target device
# 3. Product → Archive
# 4. Distribute to App Store
```

**Android Build**:
```bash
# Open in Android Studio
npx cap open android

# In Android Studio:
# 1. Build → Generate Signed Bundle / APK
# 2. Create/select keystore
# 3. Build AAB for Play Store
# 4. Or build APK for direct distribution
```

**Configuration**: `capacitor.config.json`:
```json
{
  "appId": "com.genevabible.study",
  "appName": "Geneva Bible Study",
  "webDir": "dist",
  "bundledWebRuntime": false,
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 2000
    },
    "LocalNotifications": {
      "smallIcon": "ic_stat_icon_config_sample",
      "iconColor": "#5A3A31"
    }
  }
}
```

**Benefits**:
- ✅ Access native APIs
- ✅ App store distribution
- ✅ Better performance
- ✅ Offline capabilities
- ✅ Native plugins available

---

### iOS App Store Distribution

**Requirements**:
- Apple Developer account ($99/year)
- macOS with Xcode
- App Store Connect account

**Submission Process**:
1. **Prepare App**:
   - Screenshots (6.5", 5.5" required)
   - App icon (1024x1024px)
   - App description
   - Keywords
   - Privacy policy URL

2. **Build and Archive**:
   - Open project in Xcode
   - Select "Any iOS Device"
   - Product → Archive
   - Validate archive
   - Upload to App Store Connect

3. **App Store Connect**:
   - Create new app
   - Fill in metadata
   - Upload screenshots
   - Set pricing (free)
   - Submit for review

4. **Review Process**:
   - Wait 1-3 days
   - Respond to any rejections
   - Once approved, app is live

**Resources**:
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [App Store Connect Guide](https://developer.apple.com/app-store-connect/)

---

### Android Play Store Distribution

**Requirements**:
- Google Play Developer account ($25 one-time)
- Android app bundle (AAB) or APK

**Submission Process**:
1. **Prepare App**:
   - Screenshots (phone, tablet, TV)
   - Feature graphic (1024x500px)
   - App icon (512x512px)
   - Description (short & full)
   - Privacy policy URL

2. **Build Release**:
   ```bash
   # Generate keystore
   keytool -genkey -v -keystore my-release-key.keystore \
     -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000

   # Build signed AAB
   cd android
   ./gradlew bundleRelease
   ```

3. **Create Play Console Listing**:
   - Sign in to Play Console
   - Create application
   - Fill in store listing
   - Upload AAB
   - Set content rating
   - Set pricing & distribution

4. **Testing Tracks**:
   - Internal testing (up to 100 testers)
   - Closed testing (beta)
   - Open testing (public beta)
   - Production

5. **Submit for Review**:
   - Review takes 1-7 days
   - App goes live after approval

**Resources**:
- [Play Console Help](https://support.google.com/googleplay/android-developer/)
- [Launch Checklist](https://developer.android.com/distribute/best-practices/launch/)

---

## 🖥️ Desktop Applications

### Windows

#### Option 1: PWA (Easy - No Build Required)
**Installation**:
- Open in Edge/Chrome
- Click install icon
- App installs to Start Menu

**Features**:
- ✅ Native window
- ✅ Taskbar integration
- ✅ Auto-updates

---

#### Option 2: Electron App (Advanced - Native Features)

**Setup**:
```bash
# Install Electron
npm install electron electron-builder --save-dev

# Create electron/main.js
# (See WINDOWS_WIDGET_GUIDE.md for code)

# Add to package.json
{
  "main": "electron/main.js",
  "scripts": {
    "electron:dev": "electron .",
    "electron:build": "electron-builder"
  }
}
```

**Build Windows Installer**:
```bash
npm run electron:build
```

**Outputs**:
- `dist/Geneva Bible Study Setup.exe` - Installer
- `dist/Geneva Bible Study.exe` - Portable

**Distribution**:
1. **Direct Download**: Host on website
2. **Microsoft Store**: Submit via Partner Center
3. **Chocolatey**: Create package for `choco install`
4. **Winget**: Submit to Windows Package Manager

---

### macOS

#### Option 1: PWA (Easy)
- Open in Safari/Chrome
- File → Install Geneva Bible Study

#### Option 2: Electron App (Advanced)

**Build macOS App**:
```bash
# Requires macOS to build
electron-builder --mac
```

**Outputs**:
- `dist/Geneva Bible Study.dmg` - Installer
- `dist/Geneva Bible Study.app` - Application

**Distribution**:
1. **Direct Download**: Host DMG file
2. **Mac App Store**: Requires Apple Developer account
3. **Homebrew**: Create Cask formula

**Code Signing** (for distribution):
```bash
# Sign the app
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  "Geneva Bible Study.app"

# Notarize (required for macOS 10.15+)
xcrun altool --notarize-app \
  --primary-bundle-id "com.genevabible.study" \
  --username "your@email.com" \
  --password "app-specific-password" \
  --file "Geneva Bible Study.dmg"
```

---

### Linux

#### Option 1: PWA (Easy)
- Open in Chrome/Firefox
- Menu → Install

#### Option 2: Electron App (Advanced)

**Build Linux Packages**:
```bash
# Build all formats
electron-builder --linux

# Specific formats
electron-builder --linux deb       # Debian/Ubuntu
electron-builder --linux rpm       # Fedora/RHEL
electron-builder --linux AppImage  # Universal
electron-builder --linux snap      # Snap Store
electron-builder --linux flatpak   # Flathub
```

**Distribution**:
1. **AppImage**: Universal, works everywhere
2. **Snap Store**: `snapcraft` packaging
3. **Flathub**: Flatpak packaging
4. **Distribution Repos**: DEB/RPM packages
5. **AUR** (Arch): PKGBUILD file

---

## 📦 Distribution Channels Summary

### Web Platforms
| Platform | Cost | Setup Time | Best For |
|----------|------|------------|----------|
| GitHub Pages | Free | 5 min | Open source, documentation |
| Vercel | Free | 10 min | Fast global delivery |
| Netlify | Free | 10 min | Advanced features |
| Cloudflare Pages | Free | 15 min | Unlimited bandwidth |
| Firebase | Free | 20 min | Google ecosystem |
| Custom Domain | $10-15/yr | 30 min | Professional branding |

### Mobile Platforms
| Platform | Cost | Setup Time | Approval Time | Best For |
|----------|------|------------|---------------|----------|
| PWA (Web) | Free | 0 min | Instant | Quick launch, testing |
| iOS App Store | $99/yr | 2-3 days | 1-3 days | Native iOS features |
| Google Play | $25 once | 1-2 days | 1-7 days | Native Android features |
| Direct APK | Free | 1 day | Instant | Beta testing, regions |

### Desktop Platforms
| Platform | Cost | Setup Time | Best For |
|----------|------|------------|----------|
| PWA | Free | 0 min | Simple, auto-updating |
| Electron (Direct) | Free | 2-3 days | Full control |
| Microsoft Store | $19 once | 3-5 days | Discoverability |
| Mac App Store | $99/yr | 3-5 days | macOS users |
| Snap Store | Free | 1-2 days | Linux users |
| Flathub | Free | 2-3 days | Linux users |

---

## 🔄 Continuous Deployment

### GitHub Actions - Current Setup

**Automated Workflows**:

1. **Deploy to GitHub Pages** (`.github/workflows/deploy.yml`):
   - Triggers: Push to main, manual dispatch
   - Steps: Build → Test → Deploy
   - Status: ✅ Active

2. **Lighthouse CI** (`.github/workflows/lighthouse-ci.yml`):
   - Triggers: PR, push to main, weekly
   - Steps: Build → Run Lighthouse → Comment on PR
   - Status: ✅ Active

**Configuration**:
```yaml
# Example workflow structure
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

---

### Multi-Platform CD Pipeline (Future)

**Comprehensive Pipeline**:
```yaml
# .github/workflows/release.yml
name: Multi-Platform Release

on:
  push:
    tags:
      - 'v*'

jobs:
  web:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Vercel
      - name: Deploy to Netlify
      - name: Update CDN

  ios:
    runs-on: macos-latest
    steps:
      - name: Build iOS app
      - name: Upload to TestFlight
      - name: Submit to App Store

  android:
    runs-on: ubuntu-latest
    steps:
      - name: Build Android app
      - name: Upload to Play Console
      - name: Create GitHub release

  windows:
    runs-on: windows-latest
    steps:
      - name: Build Windows installer
      - name: Sign executable
      - name: Upload to GitHub releases

  macos:
    runs-on: macos-latest
    steps:
      - name: Build macOS app
      - name: Code sign and notarize
      - name: Upload to GitHub releases

  linux:
    runs-on: ubuntu-latest
    steps:
      - name: Build AppImage
      - name: Build Snap
      - name: Build Flatpak
      - name: Upload to repositories
```

---

## 📊 Monitoring & Analytics

### Performance Monitoring
- **Lighthouse CI**: Automated performance testing
- **GitHub Actions**: Build and deployment status
- **Uptime Monitoring**: Services like UptimeRobot

### Usage Analytics (Optional, Privacy-First)
- **Self-hosted**: Plausible, Umami
- **Privacy-focused**: Simple Analytics
- **Traditional**: Google Analytics (opt-in)

### Error Tracking
- **Sentry**: Real-time error tracking
- **LogRocket**: Session replay
- **Browser Console**: Built-in error logging

---

## 🔐 Security & Compliance

### Pre-Deployment Checklist
- [ ] HTTPS enabled
- [ ] Content Security Policy configured
- [ ] Dependencies updated (no vulnerabilities)
- [ ] API keys removed from client code
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] GDPR compliance (if EU users)
- [ ] Accessibility tested (WCAG AA)

### App Store Compliance
- [ ] Privacy policy URL
- [ ] Data collection disclosure
- [ ] Age rating appropriate
- [ ] Content guidelines followed
- [ ] Export compliance (US)

---

## 📚 Additional Resources

### Documentation
- [CROSS_PLATFORM_STABILITY.md](./CROSS_PLATFORM_STABILITY.md)
- [MOBILE_IMPLEMENTATION.md](./MOBILE_IMPLEMENTATION.md)
- [WINDOWS_WIDGET_GUIDE.md](./WINDOWS_WIDGET_GUIDE.md)
- [GITHUB_PAGES_DEPLOYMENT.md](./GITHUB_PAGES_DEPLOYMENT.md)
- [LIGHTHOUSE_CI.md](./LIGHTHOUSE_CI.md)

### External Guides
- [Capacitor Documentation](https://capacitorjs.com/docs)
- [Electron Documentation](https://www.electronjs.org/docs)
- [PWA Builder](https://www.pwabuilder.com/)
- [Web.dev](https://web.dev/)

---

## 🎯 Recommended Deployment Strategy

### Phase 1: Web (Current) ✅
1. Deploy to GitHub Pages
2. Set up custom domain (optional)
3. Enable PWA features
4. Monitor with Lighthouse CI

### Phase 2: Mobile Enhancement
1. Improve PWA installation flow
2. Test on real iOS/Android devices
3. Optimize for mobile performance
4. Add offline functionality

### Phase 3: Native Mobile (Optional)
1. Implement Capacitor
2. Build iOS/Android apps
3. Submit to beta testing (TestFlight, Play Console)
4. Release to app stores

### Phase 4: Desktop Apps (Optional)
1. Create Electron wrapper
2. Build for Windows/macOS/Linux
3. Distribute via GitHub releases
4. Submit to app stores

---

**Your app is ready for global deployment!** 🚀🌍

For questions or issues, see [CONTRIBUTING.md](./CONTRIBUTING.md) or open a GitHub issue.
