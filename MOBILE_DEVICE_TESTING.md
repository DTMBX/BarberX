# Mobile Device Testing Guide

Testing on real iOS and Android devices before app store submission ensures reliability and catches platform-specific issues early.

---

## 📋 Prerequisites

### iOS Requirements

- **Mac computer** (required for iOS development)
- **Xcode 14+** (latest version recommended)
- **Apple ID** with valid payment method (for provisioning profiles)
- **Physical iPhone 12+** (test device)
- **iOS 14+** (on test device)
- **USB cable** (to connect device to Mac)

### Android Requirements

- **Windows/Mac/Linux computer** (any OS works)
- **Android Studio 2023+** (Bumblebee or newer)
- **Android SDK 31+** (API level)
- **Physical Android phone 9+** (test device)
- **USB cable** (to connect device to computer)
- **Google account** (for Play Store testing)

---

## 🍎 iOS Device Testing (Mac Only)

### Step 1: Install Prerequisites

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Node.js + npm (if not already installed)
node --version
npm --version
```

### Step 2: Set Up Signing Certificate

```bash
# Open Xcode and create signing certificates
open /Applications/Xcode.app

# In Xcode: Xcode → Preferences → Accounts
# Add your Apple ID
# Click "Manage Certificates"
# Create "iOS Development" certificate
# Let Xcode auto-manage signing (easiest method)
```

### Step 3: Prepare Mobile App

```bash
# Navigate to mobile directory
cd mobile

# Install dependencies
npm install
npm install -g react-native-cli

# Check Pod dependencies (iOS)
cd ios
pod install
cd ..
```

### Step 4: Connect iPhone

1. **Connect iPhone via USB cable**
2. **Trust the computer** (tap "Trust" on iPhone)
3. **Verify connection:**

   ```bash
   # List connected devices
   xcrun xcode-select -p

   # Should output: /Applications/Xcode.app/Contents/Developer
   ```

### Step 5: Build and Deploy to iPhone

```bash
# Option A: Using CLI (fastest)
react-native run-ios --device "Your iPhone Name"

# Replace "Your iPhone Name" with actual device name shown in Xcode
# Example: react-native run-ios --device "Jane's iPhone"

# Option B: Using Xcode GUI
# Open ios/VideoUpload.xcworkspace (NOT .xcodeproj)
# Select your iPhone in "Destination" dropdown
# Click the Play button to build and run
```

### Step 6: Grant App Permissions on Device

When app launches on device for first time:

1. ✅ **Camera Access** — Tap "Allow" (needed for file picker)
2. ✅ **Files Access** — Tap "Allow" (needed for video upload)
3. ✅ **Network Access** — Tap "Allow" (needed for API calls)

### Step 7: Test on Device

#### Feature Checklist

- [ ] App launches without crashing
- [ ] File picker opens when tapping "Select Videos"
- [ ] Can select video files from camera roll
- [ ] Quality selector displays all 5 tiers
- [ ] Case selector shows cases from API
- [ ] Upload button triggers batch upload
- [ ] Real-time progress updates display
- [ ] Connection status shows (online/offline)
- [ ] Error messages display properly
- [ ] App doesn't crash on rotation
- [ ] Back button works correctly

#### Performance Checklist

- [ ] App starts within 5 seconds
- [ ] File selection is responsive
- [ ] Large file list (50 files) scrolls smoothly
- [ ] No memory warnings during upload
- [ ] WebSocket stays connected for 5+ minutes

#### Network Testing

- [ ] WiFi connection: Upload works
- [ ] Switch to cellular: App handles gracefully
- [ ] Disable network: Shows offline message
- [ ] Re-enable network: Reconnects automatically

### iOS Debugging

```bash
# View device console logs
# In Xcode: Window → Devices and Simulators
# Select your iPhone
# View "Console" tab for logs

# Or use command line:
# First get Device ID
instruments -s devices

# Then tail logs (replace UDID)
log stream --device-id <UDID> --predicate 'eventMessage contains "VideoUpload"'
```

### iOS TestFlight Preparation

Before app store submission, use TestFlight for wider testing:

```bash
# 1. Create an App ID in Apple Developer Portal
# https://developer.apple.com/account/resources/identifiers/list

# 2. Configure provisioning profiles
# https://developer.apple.com/account/resources/profiles/list

# 3. Archive app for distribution
# In Xcode: Product → Archive
# Click "Distribute App"
# Select "TestFlight Only"
# Follow upload prompts

# 4. Add testers in App Store Connect
# https://appstoreconnect.apple.com
# Go to your app → TestFlight → Internal Testers
# Add email addresses of testers

# 5. Testers receive invite email
# They click link and install via TestFlight app
```

---

## 🤖 Android Device Testing

### Step 1: Install Prerequisites

```bash
# Windows users: Download Android Studio
# https://developer.android.com/studio

# Mac users:
brew install android-studio

# Or download from: https://developer.android.com/studio
```

### Step 2: Configure Android Environment

```bash
# After installing Android Studio, download SDKs:
# Open Android Studio → Tools → SDK Manager
# Install:
# - Android SDK Platform 31+ (for targetSdkVersion)
# - Android SDK Build-Tools 33+
# - Google Play Services
# - Android Emulator (for emulator testing)

# Set ANDROID_HOME environment variable
# Windows (PowerShell):
[Environment]::SetEnvironmentVariable("ANDROID_HOME", "C:\Users\<YourUsername>\AppData\Local\Android\Sdk", "User")
$env:ANDROID_HOME = "C:\Users\<YourUsername>\AppData\Local\Android\Sdk"

# Mac:
echo 'export ANDROID_HOME=$HOME/Library/Android/Sdk' >> ~/.zshrc
echo 'export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/tools' >> ~/.zshrc
source ~/.zshrc

# Linux:
echo 'export ANDROID_HOME=$HOME/Android/Sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/tools' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Prepare Mobile App

```bash
# Navigate to mobile directory
cd mobile

# Install dependencies
npm install

# Install Android dependencies
npm install -g react-native-cli
```

### Step 4: Enable USB Debugging on Android Device

1. **Open Settings** on Android phone
2. **Go to "About Phone"**
3. **Tap "Build Number"** 7 times rapidly
   - You'll see "Developer mode enabled" message
4. **Go back to Settings**
5. **Tap "Developer Options"** (now visible)
6. **Enable "USB Debugging"**
7. **Enable "USB File Transfer Mode"**
8. **Plug phone into computer via USB**
9. **Tap "Allow" on phone** when prompted to authorize USB debugging

### Step 5: Verify Android Connection

```bash
# List connected Android devices
adb devices

# Should show:
# List of attached devices
# <device_id>    device

# If shows "unauthorized", revoke USB debugging:
adb devices -l  # List all devices
adb kill-server
adb devices      # Reconnect and authorize on phone again
```

### Step 6: Build and Deploy to Android Device

```bash
# Navigate to mobile directory
cd mobile

# Option A: Using CLI (fastest)
react-native run-android --device <device_id>

# Example: react-native run-android --device emulator-5554

# Option B: Build APK manually
cd android
./gradlew assembleDebug
cd ..
# APK will be at: android/app/build/outputs/apk/debug/app-debug.apk

# Then install APK on device:
adb install android/app/build/outputs/apk/debug/app-debug.apk

# Option C: Using Android Studio GUI
# Open android/ folder as Android Studio project
# Select device in "Run Device" dropdown
# Click Play button
```

### Step 7: Grant App Permissions on Device

When app launches for first time:

1. ✅ **Storage Access** — Tap "Allow" (needed for file picker)
2. ✅ **Camera Access** — Tap "Allow" (if app uses camera)
3. ✅ **Network Access** — Auto-granted (required for API)

### Step 8: Test on Device

#### Feature Checklist

- [ ] App launches without crashing
- [ ] File picker opens when tapping "Select Videos"
- [ ] Can select multiple video files
- [ ] Quality selector works
- [ ] Case selector fetches and displays cases
- [ ] Upload button initiates batch upload
- [ ] Real-time progress displays
- [ ] Connection status updates
- [ ] Back button navigates correctly
- [ ] App doesn't freeze during operations
- [ ] Transcription preview displays

#### Performance Checklist

- [ ] App starts within 5 seconds
- [ ] Can select 50 files without crashing
- [ ] File list scrolls smoothly with 50 items
- [ ] Upload doesn't cause crashes (test 10+ file batch)
- [ ] WebSocket stays connected 5+ minutes
- [ ] Memory usage stays under 200MB

#### Network Testing

- [ ] WiFi: Upload works end-to-end
- [ ] Cellular data: Upload works (may be slower)
- [ ] Switch networks mid-upload: Handles gracefully
- [ ] Disable network: Shows offline message
- [ ] Re-enable network: Reconnects within 10 seconds

### Android Debugging

```bash
# View device logs in real-time
adb logcat | grep "VideoUpload\|RN"

# Or filter by app package:
adb logcat -s ReactNativeJS

# Clear logs
adb logcat -c

# Save logs to file
adb logcat > logs.txt

# Capture only errors
adb logcat *:E | grep -v "less"
```

### Android Keystore Setup (for Play Store)

```bash
# Generate release keystore (do this once)
keytool -genkey -v -keystore my-release-key.jks \
  -alias my-app-key \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# This prompts for:
# - Keystore password (remember this!)
# - Key password (same as keystore password)
# - Full name, organization, city, etc.

# Place keystore in android/app directory:
mv my-release-key.jks android/app/

# Create android/app/build.gradle.properties:
MYAPP_RELEASE_STORE_FILE=my-release-key.jks
MYAPP_RELEASE_STORE_PASSWORD=<password>
MYAPP_RELEASE_KEY_ALIAS=my-app-key
MYAPP_RELEASE_KEY_PASSWORD=<password>

# Now build release APK:
cd android
./gradlew assembleRelease
cd ..

# APK location: android/app/build/outputs/apk/release/app-release.apk
```

---

## 🧪 Comprehensive Testing Checklist

### Before First Device Test

- [ ] API endpoint is running (health check: `curl http://localhost:5000/health`)
- [ ] WebSocket is accessible (check CORS configuration)
- [ ] Database is seeded with test data
- [ ] Test video files are available (small files for testing)
- [ ] Environment variables are set (.env file)

### Unit Testing

```bash
# Run Jest tests before device testing
cd mobile
npm test

# With coverage:
npm test -- --coverage
```

### On Device: Core Functionality

- [ ] Authentication (login screen, token storage)
- [ ] File selection (all video formats work)
- [ ] Upload (single file, batch files)
- [ ] Progress tracking (real-time updates)
- [ ] Transcription retrieval (results display)
- [ ] Error handling (invalid files, network errors)
- [ ] Offline support (graceful degradation)

### On Device: Edge Cases

- [ ] App backgrounding (pause upload, resume)
- [ ] Screen rotation (data persists)
- [ ] Device orientation (landscape/portrait)
- [ ] Low storage (graceful error)
- [ ] Low memory (app doesn't crash)
- [ ] Network switching (WiFi ↔ Cellular)
- [ ] Long uploads (test 30+ minute video)

### Performance Benchmarks

| Action                 | Target | Actual |
| ---------------------- | ------ | ------ |
| App launch             | <5s    | \_\_\_ |
| File picker open       | <2s    | \_\_\_ |
| Select 50 files        | <3s    | \_\_\_ |
| Start upload           | <1s    | \_\_\_ |
| Progress update        | <500ms | \_\_\_ |
| Zoom scroll (50 items) | >60fps | \_\_\_ |

### Security Checks

- [ ] Token stored securely (not in logs)
- [ ] Sensitive data not displayed
- [ ] API calls use HTTPS
- [ ] No hardcoded credentials
- [ ] File paths don't leak sensitive data
- [ ] WebSocket connection encrypted (if over internet)

---

## 🔧 Troubleshooting Common Issues

### iOS Issues

**"Could not find connected device"**

```bash
# Reconnect device and try again
# Restart Xcode
# Kill Xcode processes: killall Xcode
# Unpair and repair device
```

**"Provisioning profile expired"**

```bash
# In Xcode: Preferences → Accounts
# Select Apple ID
# Click Manage Certificates
# Delete expired certs
# Let Xcode auto-generate new ones
```

**"Build fails with 'App not installed'"**

```bash
# Device storage full
# Uninstall old app: xcode-select --reset
# Try again

# Or manually uninstall:
# On iPhone: Settings → General → iPhone Storage
# Find app, swipe left, Delete App
```

**"WebSocket connection fails"**

```bash
# Check API is accessible from device:
# On device browser, visit: http://<your-computer-ip>:5000/health

# Enable CORS in Flask:
# Add to app.py:
# from flask_cors import CORS
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# Or check firewall: Allow port 5000
```

### Android Issues

**"No device connected"**

```bash
# Check USB cable (try different port)
adb kill-server
adb devices

# If still not showing:
# Settings → Apps → Show system → Android Device Manager
# Force stop and restart it
```

**"Permission denied / Device unauthorized"**

```bash
# On phone, tap "Allow" in authorization prompt
# Or revoke and reconnect:
adb devices -l
adb kill-server
# Reconnect cable and authorize again
```

**"Gradle build fails"**

```bash
# Clear Gradle cache
cd android
./gradlew clean
./gradlew assembleDebug
cd ..

# Or completely reset:
rm -rf android/.gradle
./gradlew clean
react-native run-android
```

**"WebSocket connection fails"**

```bash
# Get computer IP address:
# Windows: ipconfig | findstr IPv4
# Mac: ifconfig | grep inet

# Update API_URL in mobile app to use IP instead of localhost:
# Example: http://192.168.1.100:5000

# Make sure port 5000 is not blocked by firewall
# Windows Firewall: Allow python.exe inbound on port 5000
```

**"Out of memory / App crashes"**

```bash
# Increase heap size:
# In android/app/build.gradle, find dexOptions:
dexOptions {
    javaMaxHeapSize "4g"
}

# Or reduce memory usage in app:
# Compress images before upload
# Limit file list size to 20 items
```

---

## 📊 Device Test Report Template

Create a file `device-testing-report.md`:

```markdown
# Device Testing Report

**Date:** 2026-02-09
**Tester Name:** ****\_\_\_****
**Device:** iPhone 14 Pro / Samsung Galaxy S23
**OS Version:** iOS 17.2 / Android 13
**Network:** WiFi / Cellular

## Functional Tests

### File Upload

- [ ] Single file upload succeeds
- [ ] Batch upload (10 files) succeeds
- [ ] File validation works (rejects non-video)
- [ ] Progress bar updates in real-time

### Quality Selection

- [ ] All 5 quality tiers selectable
- [ ] Selected quality persists
- [ ] Quality affects upload speed (visible?)

### Case Assignment

- [ ] Case dropdown loads cases
- [ ] Case search works
- [ ] Selected case saves

### Transcription

- [ ] Transcription progress displays
- [ ] Completed transcript displays
- [ ] Download transcript button works
- [ ] Text is readable (not corrupted)

### Error Handling

- [ ] Network error shows message
- [ ] Invalid file shows message
- [ ] Server error shows message
- [ ] Can retry failed upload

## Performance

| Metric          | Expected | Actual | Status |
| --------------- | -------- | ------ | ------ |
| App Launch      | <5s      | \_\_\_ | ✓/✗    |
| File Selection  | <2s      | \_\_\_ | ✓/✗    |
| Upload Start    | <1s      | \_\_\_ | ✓/✗    |
| Progress Update | <500ms   | \_\_\_ | ✓/✗    |

## Issues Found

### Critical (blocks submission)

- [ ] Crash: ****\_\_\_****
- [ ] Feature broken: ****\_\_\_****

### Major (need to fix)

- [ ] Slow performance: ****\_\_\_****
- [ ] UI issue: ****\_\_\_****

### Minor (nice to fix)

- [ ] Typo: ****\_\_\_****
- [ ] Layout: ****\_\_\_****

## Recommendations

- ***
- ***

**Overall Status:** ✓ Ready for App Store / ✗ Needs Fixes
```

---

## 📈 Metrics to Track

After testing on real devices, collect:

```json
{
  "ios": {
    "devices_tested": 2,
    "test_duration_hours": 8,
    "crash_count": 0,
    "critical_issues": 0,
    "major_issues": 2,
    "minor_issues": 5,
    "ready_for_appstore": true
  },
  "android": {
    "devices_tested": 2,
    "test_duration_hours": 8,
    "crash_count": 0,
    "critical_issues": 0,
    "major_issues": 1,
    "minor_issues": 3,
    "ready_for_playstore": true
  }
}
```

---

## 📱 Next Steps After Device Testing

### If All Tests Pass ✅

1. **Create TestFlight build** (iOS)
2. **Create closed beta** (Android)
3. **Get App Store approvals**
4. **Submit to App Store** (waiting 24-48 hours for review)
5. **Submit to Play Store** (usually approved within 2-4 hours)

### If Issues Found ✗

1. **Document all issues** with screenshots
2. **Prioritize by severity** (critical first)
3. **Fix in code**
4. **Re-test fixed features** on device
5. **Repeat until all critical issues resolved**

---

## 🎯 Success Criteria

Device testing is complete when:

- ✅ No crashes on either platform
- ✅ All critical features work (upload, transcription, download)
- ✅ All 8+ edge cases handled gracefully
- ✅ Performance meets benchmarks (app starts <5s)
- ✅ Network errors show user-friendly messages
- ✅ App works on min supported OS (iOS 14, Android 9)
- ✅ WebSocket stays connected during long upload
- ✅ No hardcoded IP addresses or credentials in logs
- ✅ All permissions requested properly
- ✅ Ready for app store review

---

## 📞 Support

**iOS Specific Issues:**

- Ask on StackOverflow with tag `[swift]`
- Check Apple Developer Forums
- Review Xcode logs: `~/Library/Logs/Xcode/`

**Android Specific Issues:**

- Ask on StackOverflow with tag `[android]`
- Check Google Android Developer docs
- Review Android Studio logcat

**React Native Issues:**

- Check React Native docs: https://reactnative.dev
- Review debugging guide: https://reactnative.dev/docs/debugging

**WebSocket Issues:**

- Test Socket.IO connection: https://socket.io/docs/
- Verify CORS settings in Flask backend
- Check firewall rules on both computers
