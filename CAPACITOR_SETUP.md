# Capacitor Native App Setup Guide

## Prerequisites

### For iOS Development
- macOS computer
- Xcode 14+ installed
- Apple Developer Account ($99/year)
- CocoaPods installed: `sudo gem install cocoapods`

### For Android Development
- Android Studio installed
- Java JDK 17+
- Android SDK installed via Android Studio

## Step 1: Install Capacitor

```bash
npm install @capacitor/core @capacitor/cli
npm install @capacitor/ios @capacitor/android
```

## Step 2: Initialize Capacitor

```bash
npx cap init
```

When prompted:
- App name: **Geneva Bible Study**
- App ID: **com.genevabible.study** (or your custom domain)
- Web asset directory: **dist**

## Step 3: Build Your Web App

```bash
npm run build
```

## Step 4: Add Platforms

```bash
npx cap add ios
npx cap add android
```

## Step 5: Configure for Production

### iOS Setup

1. Open the iOS project:
```bash
npx cap open ios
```

2. In Xcode:
   - Select your project in the navigator
   - Update Bundle Identifier to match your App ID
   - Select your Development Team
   - Configure signing certificates
   - Set deployment target to iOS 13.0+

3. Update Info.plist for required permissions:
   - Microphone access (for voice annotations)
   - Notifications
   - Background audio

### Android Setup

1. Open the Android project:
```bash
npx cap open android
```

2. In Android Studio:
   - Update `applicationId` in `app/build.gradle`
   - Set `versionCode` and `versionName`
   - Configure signing keys for release builds
   - Set minimum SDK to 22 (Android 5.1)

## Step 6: Sync and Build

After any web app changes:

```bash
npm run build
npx cap sync
```

## Step 7: Build for Distribution

### iOS App Store

1. In Xcode, select **Product > Archive**
2. Once archived, click **Distribute App**
3. Choose **App Store Connect**
4. Follow the upload wizard
5. Submit for review in App Store Connect

### Android Play Store

1. In Android Studio: **Build > Generate Signed Bundle/APK**
2. Choose **Android App Bundle**
3. Create or select your signing key
4. Build release bundle
5. Upload to Google Play Console

## Important Configuration Files

See `capacitor.config.ts` for app configuration.
See `NATIVE_FEATURES.md` for feature-specific setup.

## Testing

```bash
# Test on iOS simulator
npx cap run ios

# Test on Android emulator
npx cap run android
```

## Troubleshooting

- **Build fails**: Ensure all prerequisites are installed
- **Signing issues**: Verify certificates in Xcode/Android Studio
- **API issues**: Check CORS configuration for native apps
- **Plugin errors**: Run `npx cap sync` after installing plugins
