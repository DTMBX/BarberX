# Device Testing Quick Start

## ⚡ TL;DR - Get Testing in 10 Minutes

### iOS (Mac Only)

```bash
# 1. Connect iPhone via USB
# 2. Trust the computer on your iPhone
# 3. Get device name
instruments -s devices

# 4. Deploy app
cd mobile && npm install && cd ..
react-native run-ios --device "Your iPhone Name"

# 5. Grant permissions when prompted

# 6. Test features
# - Upload files
# - Select quality
# - Monitor progress
# - Download results
```

### Android (Windows/Mac/Linux)

```bash
# 1. Enable USB Debugging on phone:
#    Settings → Developer Options → USB Debugging

# 2. Connect via USB

# 3. Verify connection
adb devices

# 4. Deploy app
cd mobile && npm install && cd ..
react-native run-android

# 5. Grant permissions when prompted

# 6. Test features
```

---

## 🔍 Pre-Testing Setup

```bash
# Make sure everything is ready
npm run mobile:test              # Tests pass ✓
npm run type-check              # No TypeScript errors ✓
npm run lint                     # Code lint passes ✓
curl http://localhost:5000/health  # Backend running ✓
```

---

## ✅ What to Test on Device

### Must Work
- [ ] App launches
- [ ] Login works
- [ ] Select files (tap button)
- [ ] Pick quality (tap preset)
- [ ] Pick case (from dropdown)
- [ ] Upload starts (tap Upload button)
- [ ] Progress updates in real-time
- [ ] Results display when done
- [ ] Download transcript works
- [ ] App doesn't crash

### Nice to Test
- [ ] Orientation change (rotate phone)
- [ ] Background/foreground (press home, return)
- [ ] Slow network (toggle WiFi)
- [ ] Offline mode (turn off network)
- [ ] Large batch (50 files)

---

## 🐛 Debug If Something Breaks

### iOS
```bash
# View logs in Xcode
# Window → Devices and Simulators → Your iPhone → Console

# Or command line logs:
log stream --device-id <UDID> | grep -i error
```

### Android
```bash
# View logs
adb logcat | grep "VideoUpload\|RN"

# Filter to errors only
adb logcat *:E
```

---

## 📝 Report Issues

When testing, note down:
- **What happened** - "App crashed when selecting 50 files"
- **Expected** - "Should select 50 files without crashing"
- **Device** - "iPhone 14 Pro, iOS 17.2"
- **Network** - "WiFi"
- **Steps to reproduce** - "Open app, tap Select, pick 50 videos, tap Upload"

---

## ✨ Success = Ready for App Store

When these are all true:
- ✅ No crashes
- ✅ All features work
- ✅ Performance is good (app starts in <5 seconds)
- ✅ Can upload without errors
- ✅ Can download results

**Then you're ready to submit to App Store / Play Store!**

---

## 🆘 Common Problems

| Problem | Fix |
|---------|-----|
| "Device not found" | Reconnect USB, restart `adb devices` |
| "Permission denied" | Tap "Trust" on iPhone, or `adb revoke` on Android |
| "WebSocket connection failed" | Check backend is running: `curl localhost:5000` |
| "API 404 Not Found" | Verify `REACT_APP_API_URL` matches your backend IP |
| "Out of memory" | Close other apps, restart phone |
| "Build failed" | Run `npm install` again in mobile folder |

---

See [MOBILE_DEVICE_TESTING.md](MOBILE_DEVICE_TESTING.md) for complete guide with all details.
