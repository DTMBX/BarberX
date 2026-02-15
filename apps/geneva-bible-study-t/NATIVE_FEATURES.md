# Native Features Setup

## Required Capacitor Plugins

Install these plugins for full app functionality:

```bash
npm install @capacitor/splash-screen
npm install @capacitor/status-bar
npm install @capacitor/haptics
npm install @capacitor/local-notifications
npm install @capacitor/push-notifications
npm install @capacitor/share
npm install @capacitor/filesystem
npm install @capacitor/app
npm install @capacitor/network
npm install @capacitor/background-task
```

## Feature Mappings

### Audio Bible Playback
- Uses Web Audio API (works natively)
- Add background audio capability in iOS Info.plist:
```xml
<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
</array>
```

### Notifications (Verse of the Day)
- Plugin: `@capacitor/local-notifications`
- Requires permission prompts on both platforms
- iOS: Add to Info.plist
- Android: Automatic permission handling

### Voice Annotations
- Plugin: `@capacitor/filesystem` for storage
- Requires microphone permissions
- iOS Info.plist:
```xml
<key>NSMicrophoneUsageDescription</key>
<string>Record voice annotations for Bible verses</string>
```

### Social Sharing
- Plugin: `@capacitor/share`
- Native share sheets on both platforms

### Dark Mode
- Uses system preferences automatically
- No additional setup required

### Offline Storage
- Current useKV system works with Capacitor
- Consider adding `@capacitor/preferences` for native storage

## Platform-Specific Permissions

### iOS Info.plist Additions

```xml
<key>NSUserNotificationAlertStyle</key>
<string>alert</string>
<key>NSMicrophoneUsageDescription</key>
<string>Record voice annotations for your Bible study</string>
<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
    <string>fetch</string>
</array>
```

### Android Manifest Additions

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
```

## App Icons & Splash Screens

Generate assets using:
```bash
npm install @capacitor/assets --save-dev
npx capacitor-assets generate
```

Place source files in:
- `resources/icon.png` (1024x1024)
- `resources/splash.png` (2732x2732)

## Distribution Checklist

### iOS
- [ ] Configure Bundle Identifier
- [ ] Set up signing certificates
- [ ] Add privacy descriptions
- [ ] Test on physical device
- [ ] Archive and upload to App Store Connect
- [ ] Submit for review

### Android
- [ ] Update applicationId
- [ ] Generate signing key
- [ ] Configure ProGuard (optional)
- [ ] Test on physical device
- [ ] Generate signed AAB
- [ ] Upload to Play Console
- [ ] Submit for review
