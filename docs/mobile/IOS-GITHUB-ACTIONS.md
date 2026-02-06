# 🍎 iOS Build via GitHub Actions

**Status:** ✅ Workflow Created - Ready to Use  
**Location:** `.github/workflows/ios-build.yml`  
**Cost:** 🆓 FREE (GitHub provides Mac runners)

--

## 🚀 How It Works

### Automatic iOS Builds (No Mac Required!)

1. **Push code to GitHub** → Triggers workflow
2. **GitHub Mac runner** → Builds iOS app in cloud
3. **Download .ipa** → Install on iPhone

--

## 📋 Setup Instructions

### Step 1: Push Workflow to GitHub

```powershell
cd C:\web-dev\github-repos\Evident.info

# Add workflow file
git add .github/workflows/ios-build.yml

# Commit
git commit -m "Add iOS build workflow"

# Push to main branch
git push origin main
```

--

### Step 2: Watch Build Execute

1. **Go to GitHub repository**
2. **Click "Actions" tab**
3. **Watch build progress** (takes 5-10 minutes)
4. **Build output shows:**
   ```
   ✅ Restore dependencies
   ✅ Install MAUI workload
   ✅ Build iOS app
   ✅ Create .ipa file
   ✅ Upload artifact
   ```

--

### Step 3: Download IPA

1. **After build completes:**
   - Actions → Latest workflow run
   - Scroll to "Artifacts" section
   - Click "evident-ios-development" to download

2. **Extract ZIP:**
   - Contains: `Evident.MatterDocket.MAUI.ipa`

--

### Step 4: Install on iPhone

#### Option A: Development (Free Apple Account)

**Requirements:**

- Mac with Xcode
- iPhone connected via USB
- Free Apple Developer account

**Steps:**

1. Open Xcode
2. Window → Devices and Simulators
3. Select your iPhone
4. Drag .ipa file to device
5. App installs (expires in 7 days)

--

#### Option B: TestFlight (Paid $99/year)

**Requirements:**

- Apple Developer Program membership
- App Store Connect access

**Steps:**

1. Upload .ipa to App Store Connect
2. Submit for TestFlight review (1-2 days)
3. Add testers via email
4. Testers install via TestFlight app
5. Beta expires in 90 days

--

## 🔧 Workflow Details

### What It Builds

```yaml
Platform: iOS (iPhone/iPad)
Target Framework: net10.0-ios
Configuration: Debug (development)
Architecture: arm64 (real devices)
Output: .ipa file
```

### When It Runs

- ✅ Push to `main` branch
- ✅ Push to `develop` branch
- ✅ Pull requests to `main`
- ✅ Manual trigger (workflow_dispatch button)

--

## 🎯 Manual Trigger

Don't want to push code? Run manually:

1. **GitHub → Actions tab**
2. **Select "iOS Build" workflow**
3. **Click "Run workflow" button**
4. **Select branch** (main/develop)
5. **Click "Run workflow"**

--

## 🐛 Troubleshooting

### Build Fails: Code Signing

**Error:** `No signing certificate found`

**Solution:**

- This workflow builds **unsigned development** builds
- To sign for distribution, need:
  - Apple Developer certificates
  - Provisioning profiles
  - GitHub Secrets with credentials

**For now:** Use unsigned .ipa with Xcode installation

--

### Build Fails: MAUI Workload

**Error:** `Workload 'maui' not found`

**Solution:**

- Workflow automatically installs MAUI
- If fails, GitHub runner issue (retry)

--

### Can't Install IPA on iPhone

**Error:** `Unable to install app`

**Reasons:**

1. **App not signed** → Use Xcode to install
2. **Wrong architecture** → Built for arm64 (real devices), not simulator
3. **iOS version too old** → Requires iOS 15.0+

--

## 📊 Build Time Estimates

| Task             | Duration         |
| ---------------- | ---------------- |
| Checkout code    | 5-10 seconds     |
| Setup .NET       | 10-15 seconds    |
| Install MAUI     | 1-2 minutes      |
| Restore packages | 1-2 minutes      |
| Build iOS app    | 3-5 minutes      |
| Upload artifact  | 10-20 seconds    |
| **Total**        | **5-10 minutes** |

--

## 💰 Cost Analysis

### GitHub Actions Free Tier

- **2,000 minutes/month** for private repos
- **Unlimited** for public repos
- Mac runners: **10x multiplier**
- Effective: **200 minutes/month** of Mac time

### Example Usage

- 1 iOS build = ~10 minutes
- 10 builds/month = 100 Mac minutes
- **Under free tier** ✅

### If You Exceed

- $0.08/minute for Mac runners
- 100 extra minutes = $8.00

--

## 🔐 Advanced: Code Signing Setup

For **App Store distribution**, add these GitHub Secrets:

```yaml
APPLE_CERTIFICATE_BASE64      # P12 certificate
APPLE_CERTIFICATE_PASSWORD    # P12 password
APPLE_PROVISIONING_PROFILE    # .mobileprovision
APPLE_TEAM_ID                 # Apple Developer Team ID
```

Then update workflow:

```yaml
- name: Import Code Signing Certificate
  uses: apple-actions/import-codesign-certs@v2
  with:
    p12-file-base64: ${{ secrets.APPLE_CERTIFICATE_BASE64 }}
    p12-password: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
```

--

## 🎉 You're Set!

### What You Have Now

1. ✅ **Android APK** - Ready to test on Android phones
2. ✅ **iOS Workflow** - Automated builds via GitHub Actions
3. ✅ **Full Documentation** - Complete guides

### Next Actions

1. **Test Android APK** on your phone today
2. **Push workflow to GitHub** (when ready for iOS)
3. **Set up Apple Developer** account (for TestFlight)

--

## 📚 Related Guides

- `ANDROID-APK-READY.md` - Android installation guide
- `IOS-TESTING-COMPLETE-GUIDE.md` - Detailed iOS deployment
- `GET-ON-IPHONE-NOW.md` - All iOS options explained
- `BUILD-SUCCESS.md` - Integration complete summary

--

**Questions?** Check the docs or view workflow logs in GitHub Actions.
