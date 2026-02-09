# Pre-App Store Submission Checklist

Complete this checklist before submitting to iOS App Store and Google Play Store.

---

## Phase 1: Local Testing (Before Device Testing)

- [ ] All Jest tests pass: `npm test`
- [ ] No TypeScript errors: `npm run type-check`
- [ ] ESLint passes: `npm run lint`
- [ ] Web app builds: `npm run build`
- [ ] No console errors in browser devtools
- [ ] API endpoints tested with Postman/curl
- [ ] WebSocket tested with WebSocket client
- [ ] Backend health check passes: `curl http://localhost:5000/health`
- [ ] Database migrations complete
- [ ] Test data seeded in database
- [ ] No hardcoded API URLs (use environment variables)
- [ ] No credentials in source code
- [ ] No sensitive data in logs

---

## Phase 2: Device Testing (iOS & Android)

### Pre-Device Checklist

- [ ] Mobile dependencies installed: `cd mobile && npm install && cd ..`
- [ ] Mobile tests pass: `npm run mobile:test`
- [ ] Type check passes: `npm run type-check`
- [ ] Code lint passes: `npm run lint`
- [ ] iOS builds without errors: `npm run mobile:build:ios`
- [ ] Android builds without errors: `npm run mobile:build:android`
- [ ] Backend running and accessible from device
- [ ] Device has valid test video files
- [ ] Network environment chosen (WiFi for initial testing)

### iOS Device Testing

**Setup (Mac only)**
- [ ] Xcode 14+ installed
- [ ] Apple ID added to Xcode (Preferences → Accounts)
- [ ] Provisioning profile created
- [ ] iPhone connected via USB
- [ ] "Trust" tapped on iPhone for computer
- [ ] iPhone has iOS 14+ installed

**Deployment**
- [ ] App deployed to device successfully: `react-native run-ios --device "Device Name"`
- [ ] App launches without crashing
- [ ] Permissions granted (Storage, Camera, Network)
- [ ] No crash on initial load

**Feature Testing (iOS)**
- [ ] login works (if auth required)
- [ ] File picker opens and displays videos
- [ ] Can select single file
- [ ] Can select multiple files (test 5, 10, 50)
- [ ] Quality selector shows all 5 options
- [ ] Case selector loads cases from API
- [ ] Can search/filter cases
- [ ] Upload button initiates batch upload (202 Accepted)
- [ ] Progress bar displays and updates
- [ ] Transcription status displays
- [ ] Download transcript button works
- [ ] Downloaded file opens correctly
- [ ] Download video button works
- [ ] Error messages display (network error, validation)
- [ ] Back button works correctly
- [ ] No memory leaks (app doesn't slow down)

**Edge Cases (iOS)**
- [ ] Backgrounding app pauses upload gracefully
- [ ] Returning to app resumes progress
- [ ] Screen rotation preserves UI state
- [ ] Landscape orientation works
- [ ] Network switch (WiFi → Cellular) handled
- [ ] Network disable/enable handled
- [ ] Long upload (30+ min) doesn't crash
- [ ] Large file list (50 items) scrolls smoothly
- [ ] App doesn't crash under low memory (Android warns before iOS crashes)

**Performance (iOS)**
- [ ] App launches in <5 seconds
- [ ] File picker opens in <2 seconds
- [ ] Selecting 50 files takes <3 seconds
- [ ] Upload starts in <1 second
- [ ] Progress updates in <500ms
- [ ] No jank during animations

**Security (iOS)**
- [ ] Token stored securely (check with Instruments)
- [ ] No API keys in console logs
- [ ] No sensitive data in error messages
- [ ] HTTPS enforced (if deployed)

**Test Results (iOS)**
- [ ] Critical issues: _____ (should be 0)
- [ ] Major issues: _____ (should be 0)
- [ ] Minor issues: _____ (acceptable if documented)
- [ ] Tester: _______
- [ ] Date: _______
- [ ] Device: _______ (model, OS version)
- [ ] Status: ✅ Ready / ⚠️ Needs Fixes

### Android Device Testing

**Setup (Windows/Mac/Linux)**
- [ ] Android Studio installed
- [ ] Android SDK 31+ installed
- [ ] Android phone connected via USB
- [ ] USB Debugging enabled on phone
- [ ] Debugger authorization granted on phone
- [ ] Connection verified: `adb devices` shows device

**Deployment**
- [ ] App deployed successfully: `react-native run-android`
- [ ] App launches without crashing
- [ ] Permissions granted (Storage, Camera, Network)
- [ ] No crash on initial load

**Feature Testing (Android)**
- [ ] Login works
- [ ] File picker opens and displays videos
- [ ] Can select single file
- [ ] Can select multiple files (test 5, 10, 50)
- [ ] Quality selector shows all 5 options
- [ ] Case selector loads cases from API
- [ ] Can search/filter cases
- [ ] Upload button initiates batch upload
- [ ] Progress bar displays and updates
- [ ] Transcription status displays
- [ ] Download transcript button works
- [ ] Downloaded file opens correctly
- [ ] Download video button works
- [ ] Error messages display
- [ ] Back button works correctly
- [ ] No memory leaks (use Android Profiler)

**Edge Cases (Android)**
- [ ] Backgrounding app pauses upload gracefully
- [ ] Returning to app resumes progress
- [ ] Screen rotation preserves UI state
- [ ] Landscape orientation works
- [ ] Network switch handled
- [ ] Network disable/enable handled
- [ ] Long upload (30+ min) doesn't crash
- [ ] Large file list (50 items) scrolls smoothly
- [ ] App doesn't crash under low memory

**Performance (Android)**
- [ ] App launches in <5 seconds
- [ ] File picker opens in <2 seconds
- [ ] Selecting 50 files takes <3 seconds
- [ ] Upload starts in <1 second
- [ ] Progress updates in <500ms
- [ ] 60fps animations (no jank)

**Security (Android)**
- [ ] Token stored securely (use Android Studio debugger)
- [ ] No API keys in logcat
- [ ] No sensitive data in error messages
- [ ] HTTPS enforced

**Test Results (Android)**
- [ ] Critical issues: _____ (should be 0)
- [ ] Major issues: _____ (should be 0)
- [ ] Minor issues: _____ (acceptable if documented)
- [ ] Tester: _______
- [ ] Date: _______
- [ ] Device: _______ (model, OS version, API level)
- [ ] Status: ✅ Ready / ⚠️ Needs Fixes

### Device Testing Issues Log

For each issue found:

```
Issue #1
--------
Description: App crashes when uploading 50 files
Device: iPhone 14 Pro, iOS 17.2
Reproducible: 100% (happens every time)
Severity: Critical (blocks submission)
Steps to reproduce:
  1. Select 50 video files
  2. Tap "Upload"
  3. Observe crash
Expected: Upload starts, progress displays
Root cause: [To be determined after debugging]
Resolution: [To be filled after fix]
Status: Open / In Progress / Fixed
```

---

## Phase 3: Build for Distribution

### iOS Distribution Build

- [ ] Increment version number in `package.json`
- [ ] Increment build number in Xcode
- [ ] Verify provisioning profile valid (expires > 30 days)
- [ ] Create App ID in Apple Developer Portal (if new app)
- [ ] Create App Store listing in App Store Connect
- [ ] Add app description, screenshots, keywords
- [ ] Build archive: `npm run mobile:build:ios`
- [ ] Validate app with Xcode
- [ ] Upload to App Store Connect via Xcode
- [ ] Screenshots uploaded (6 required, landscape/portrait)
- [ ] Privacy policy link added
- [ ] Support email added
- [ ] App review notes completed
- [ ] Submission ready

### Android Release Build

- [ ] Increment version number in `package.json`
- [ ] Increment version code in `android/app/build.gradle`
- [ ] Create release keystore (if first time): `keytool -genkey -v ...`
- [ ] Store keystore password securely (document location)
- [ ] Create signing key in Android Studio
- [ ] Build release APK: `cd android && ./gradlew assembleRelease && cd ..`
- [ ] Test release APK on device
- [ ] Create app listing in Google Play Console (if new app)
- [ ] Add app description, screenshots, keywords
- [ ] Upload APK to Play Store (Internal Testing first)
- [ ] Screenshots uploaded (landscape/portrait)
- [ ] Privacy policy link added
- [ ] Support email added
- [ ] Content rating completed
- [ ] Submission ready

---

## Phase 4: Pre-Submission Verification

### iOS Pre-Submission

- [ ] Run Apple's guidelines review checklist
- [ ] Enable bitcode (if required)
- [ ] Remove debug code and logging
- [ ] Test on minimum supported iOS version (14)
- [ ] Test on maximum supported iOS version (current)
- [ ] No deprecated APIs used
- [ ] IDFA not used (or properly declared)
- [ ] All privacy requirements met
- [ ] No hardcoded API endpoints
- [ ] Production API URL configured
- [ ] Certificate/provisioning expires > 30 days after submission
- [ ] Binary doesn't contain non-public APIs
- [ ] All strings localized (if international app)
- [ ] Support URL valid (test in browser)
- [ ] Privacy policy valid (test in browser)

### Android Pre-Submission

- [ ] Google Play compliance checklist completed
- [ ] Target API level 31+ (Google Play requirement)
- [ ] No deprecated dependencies
- [ ] Remove debug keystore (use release keystore only)
- [ ] No hardcoded credentials
- [ ] Production API URL configured
- [ ] All permissions justified in privacy policy
- [ ] All requested permissions actually used
- [ ] No malicious code (run security analysis)
- [ ] Support URL valid
- [ ] Privacy policy valid
- [ ] Compliance forms completed

---

## Phase 5: Final Submission

### iOS App Store Submission

- [ ] Version number matches internal tracking
- [ ] Build passes validation
- [ ] Metadata complete and accurate
- [ ] Screenshots represent actual UI (no mockups)
- [ ] No external app URLs in description
- [ ] Review notes provided (if needed for testing)
- [ ] Submit for review in App Store Connect
- [ ] Expected review time: 24-48 hours
- [ ] Record submission date/time

### Android Play Store Submission

- [ ] Version number matches internal tracking
- [ ] Release notes written
- [ ] Metadata complete and accurate
- [ ] Screenshots represent actual UI
- [ ] App rating set (ESRB, etc.)
- [ ] Target countries selected
- [ ] Content rating form submitted
- [ ] Submit for review in Play Console
- [ ] Expected review time: 2-4 hours
- [ ] Record submission date/time

---

## Phase 6: Post-Submission Monitoring

### While in Review

- [ ] Check review status daily
- [ ] Monitor notification email
- [ ] Have answers ready for potential questions
- [ ] Be ready to respond quickly if feedback received

### After Approval

- [ ] Verify app appears in app stores
- [ ] Test download and install from store
- [ ] Verify app runs from store version
- [ ] Monitor user reviews/ratings
- [ ] Monitor crash reports
- [ ] Have patch version ready for critical bugs

### First Week Monitoring

- [ ] Daily check for crashes (Firebase, Sentry)
- [ ] Monitor user reviews
- [ ] Respond to user feedback
- [ ] Track app analytics
- [ ] Monitor server logs for errors
- [ ] Plan for patches if needed

---

## 📊 Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Developer | | | ✅ / ❌ |
| QA Lead | | | ✅ / ❌ |
| Product Manager | | | ✅ / ❌ |
| Security Lead | | | ✅ / ❌ |

**Overall Submission Status:** ✅ Ready / ⚠️ Conditional / ❌ Not Ready

**Conditional Issues:**
- [ ] (if applicable)
- [ ] (if applicable)

**Sign-Off Notes:**

---

## 🎯 Key Dates

| Event | Actual | Target |
|-------|--------|--------|
| Device Testing Complete | | Week of Feb 17 |
| Build for Distribution | | Feb 20 |
| Submit to iOS | | Feb 23 |
| Submit to Android | | Feb 23 |
| iOS Review Complete | | Feb 25 |
| Android Review Complete | | Feb 25 |
| Live in Both Stores | | Feb 26 |

---

## 📞 Support Contacts

- **Apple Support**: https://developer.apple.com/contact/
- **Google Play Support**: https://support.google.com/googleplay/
- **Apple Critical Issues**: https://appleseed.apple.com
- **Internal Contact**: [team lead name]

---

## 📚 References

- [iOS App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Google Play Policies](https://play.google.com/about/developer-content-policy/)
- [App Privacy](https://privacy.apple.com/)
- [Google Play Console Help](https://support.google.com/googleplay/android-developer)

---

**Keep this checklist updated throughout submission process.**
