# 📱 Complete iPhone Testing Guide - Evident MAUI

**3 ways to test on iPhone | Fastest path: Start with Android (30 min)**

--

## 🚀 Path 1: Android APK (RECOMMENDED FIRST)

**Timeline:** 30 minutes | **Cost:** FREE | **Complexity:** ⭐

Test your app RIGHT NOW while waiting for iOS approval.

### Build Android APK

```powershell
# Use our custom PowerShell profile!
bm  # Navigate to MAUI project

# Build APK
dotnet build -f net10.0-android34.0 -c Release
```

**APK Location:**

```
bin\Release\net10.0-android34.0\com.Evident.matterdocket-Signed.apk
```

### Install on Any Android Phone

**Method 1: Email**

1. Email APK to yourself
2. Open email on Android phone
3. Download APK
4. Tap to install (allow "Unknown sources")

**Method 2: USB**

1. Connect Android via USB
2. Copy APK to `Downloads` folder
3. Open file manager → Downloads
4. Tap APK → Install

### Test Everything

✅ Login system  
✅ ChatGPT integration  
✅ Legal AI tools  
✅ Evidence upload  
✅ Camera integration  
✅ Subscription flows

**Result: Full working app on Android while iOS setup processes!**

--

## 📲 Path 2: TestFlight (Best for Teams)

**Timeline:** 2-4 weeks initial setup | **Cost:** $99/year | **Complexity:**
⭐⭐⭐⭐

Distribute to 10,000 testers (law firms, civic orgs).

### Week 1: Apple Developer Enrollment

#### Step 1: Join Apple Developer Program

1. Visit https://developer.apple.com/programs/
2. Click **Enroll**
3. Sign in with Apple ID
4. Choose entity type:
   - **Individual:** Personal use ($99/year)
   - **Organization:** Law firm/company ($99/year, requires D-U-N-S number)
5. Complete payment
6. **WAIT 1-2 days for approval**

#### Step 2: Create App ID (after approval)

1. Log in to https://developer.apple.com/account/
2. Navigate to **Certificates, Identifiers & Profiles**
3. Select **Identifiers** → Click **+**
4. Choose **App IDs** → Continue
5. Configure:
   - **Description:** Evident Matter Docket
   - **Bundle ID (Explicit):** `com.Evident.matterdocket`
   - **Capabilities:** Enable:
     - [x] Push Notifications (for case alerts)
     - [x] Associated Domains (for deep linking)
     - [x] Sign in with Apple (optional)
6. Click **Register**

--

### Week 2: Certificates & Provisioning (REQUIRES MAC)

#### Option A: You Have a Mac

```bash
# On your Mac, open Terminal

# 1. Install Xcode from App Store (free, ~10 GB)

# 2. Install .NET SDK
curl -sSL https://dot.net/v1/dotnet-install.sh | bash

# 3. Install MAUI workload
dotnet workload install maui

# 4. Clone Evident repo
git clone https://github.com/YOUR-USERNAME/Evident.info.git
cd Evident.info/src/Evident.MatterDocket.MAUI
```

#### Option B: No Mac? Use Cloud Mac

**MacStadium** (recommended): $79/month  
https://www.macstadium.com

**MacinCloud**: From $30/month  
https://www.macincloud.com

**Steps:**

1. Sign up for cloud Mac service
2. Remote desktop into Mac
3. Follow "Option A" steps above

--

### Week 2-3: Create Distribution Certificate

**On Mac:**

```bash
# Open Keychain Access app
# Menu: Keychain Access → Certificate Assistant → Request a Certificate from a Certificate Authority

# Fill in form:
# Email: your-apple-id@email.com
# Common Name: Evident iOS Distribution
# Request is: Saved to disk
# Click Continue

# This creates: CertificateSigningRequest.certSigningRequest
```

**Upload to Apple:**

1. Go to https://developer.apple.com/account/
2. **Certificates** → Click **+**
3. Select **iOS Distribution** → Continue
4. Upload `.certSigningRequest` file
5. Download certificate (`.cer` file)
6. **Double-click to install in Keychain**

--

### Week 3: Build iOS App

**On Mac:**

```bash
cd Evident.info/src/Evident.MatterDocket.MAUI

# Clean previous builds
dotnet clean

# Build iOS app (Release mode)
dotnet publish -f net10.0-ios -c Release
```

**Output:**

```
bin/Release/net10.0-ios/ios-arm64/publish/Evident.MatterDocket.MAUI.ipa
```

--

### Week 4: Upload to TestFlight

#### Create App in App Store Connect

1. Go to https://appstoreconnect.apple.com
2. Click **My Apps** → **+** → **New App**
3. Fill in:
   - **Platforms:** iOS
   - **Name:** Evident Matter Docket
   - **Primary Language:** English (U.S.)
   - **Bundle ID:** com.Evident.matterdocket
   - **SKU:** Evident-001
4. Click **Create**

#### Upload Build

**Method 1: Transporter App (easiest)**

1. Download **Transporter** from Mac App Store (free)
2. Open Transporter
3. Sign in with Apple ID
4. Drag `.ipa` file into window
5. Click **Deliver**
6. Wait 5-15 minutes for processing

**Method 2: Command Line**

```bash
# Install xcrun tools (included with Xcode)

# Upload
xcrun altool -upload-app \
  -type ios \
  -file bin/Release/net10.0-ios/ios-arm64/publish/*.ipa \
  -username YOUR-APPLE-ID@email.com \
  -password YOUR-APP-SPECIFIC-PASSWORD
```

--

### Configure TestFlight

**In App Store Connect:**

1. Click **TestFlight** tab
2. Wait for build to appear (~10-15 min after upload)
3. Click build number
4. Add **Export Compliance:**
   - "Does your app use encryption?" → **Yes**
   - "Is it exempt?" → **Yes** (standard HTTPS only)
5. Click **Save**

**Add Internal Testers:**

1. **TestFlight** → **Internal Testing**
2. Click **+** next to Testers
3. Add email addresses (up to 100)
4. They receive invite **immediately**

**Add External Testers (requires review):**

1. **TestFlight** → **External Testing** → **+**
2. Create group (e.g., "Law Firms Beta")
3. Add testers (up to 10,000)
4. Submit for **App Review** (~24-48 hours)

--

### Install on Your iPhone

**Step 1: Download TestFlight**

1. On iPhone, open **App Store**
2. Search: **TestFlight**
3. Install (free app from Apple)

**Step 2: Accept Invite**

1. Check email for TestFlight invite
2. Tap **View in TestFlight**
3. Opens TestFlight app automatically
4. Tap **Accept** → **Install**

**Step 3: Trust Developer (if needed)**

1. If app won't open, go to: **Settings** → **General** → **VPN & Device
   Management**
2. Tap your developer profile
3. Tap **Trust**

**🎉 Evident is now on your iPhone!**

--

## 🔧 Path 3: Development Deployment (Fastest for Testing)

**Timeline:** 2-3 hours | **Cost:** FREE | **Complexity:** ⭐⭐⭐

Deploy directly to YOUR iPhone without App Store or TestFlight.

### Requirements

- Mac computer (or cloud Mac)
- iPhone connected via USB
- Free Apple ID (no paid account needed)

### Setup Automatic Signing

**Edit `Evident.MatterDocket.MAUI.csproj`:**

```xml
<PropertyGroup Condition="'$(TargetFramework)' == 'net10.0-ios'">
    <!-- Automatic signing (free Apple ID) ->
    <CodesignKey>Apple Development</CodesignKey>
    <CodesignProvision>Automatic</CodesignProvision>

    <!-- Unique bundle ID with your Apple ID ->
    <ApplicationId>com.YOUR-NAME.Evident</ApplicationId>

    <!-- Development settings ->
    <MtouchLink>SdkOnly</MtouchLink>
    <MtouchDebug>true</MtouchDebug>
</PropertyGroup>
```

### Deploy from Command Line

```bash
# Connect iPhone via USB

# Build and deploy
dotnet build -f net10.0-ios -c Debug \
  -p:RuntimeIdentifier=ios-arm64 \
  -p:_DeviceName=YOUR-IPHONE-NAME

# App installs and launches automatically
```

### Deploy from Visual Studio for Mac

1. Open `Evident.info.sln` in Visual Studio for Mac
2. Select your iPhone from device dropdown
3. Click **Run** (▶️)
4. First time: Enter Apple ID credentials
5. App deploys and launches

**Limitation:** Certificate expires in **7 days** (free account) or **1 year**
(paid account).

--

## ⚡ GitHub Actions: Automated iOS Builds

**Set up once, builds automatically on every commit!**

### Create Workflow File

**Create `.github/workflows/ios-build.yml`:**

```yaml
name: Build iOS App

on:
  push:
    branches: [main, develop]
  workflow_dispatch: # Manual trigger

jobs:
  build-ios:
    runs-on: macos-14 # GitHub-hosted Mac

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "10.0.x"

      - name: Install MAUI workload
        run: dotnet workload install maui

      - name: Restore dependencies
        run: dotnet restore src/Evident.MatterDocket.MAUI

      - name: Build iOS
        run: |
          cd src/Evident.MatterDocket.MAUI
          dotnet build -f net10.0-ios -c Release

      - name: Publish iOS
        run: |
          cd src/Evident.MatterDocket.MAUI
          dotnet publish -f net10.0-ios -c Release

      - name: Upload IPA
        uses: actions/upload-artifact@v4
        with:
          name: Evident-iOS
          path: src/Evident.MatterDocket.MAUI/bin/Release/net10.0-ios/**/*.ipa
          retention-days: 30

      # Optional: Auto-upload to TestFlight
      - name: Upload to TestFlight
        if: github.ref == 'refs/heads/main'
        env:
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APP_PASSWORD: ${{ secrets.APPLE_APP_PASSWORD }}
        run: |
          xcrun altool -upload-app \
            -type ios \
            -file src/Evident.MatterDocket.MAUI/bin/Release/net10.0-ios/**/*.ipa \
            -username "$APPLE_ID" \
            -password "$APP_PASSWORD"
```

### Add GitHub Secrets

1. Go to GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add secrets:
   - `APPLE_ID`: Your Apple ID email
   - `APPLE_APP_PASSWORD`: Generate at https://appleid.apple.com (App-Specific
     Password)

**Now:** Every push to `main` automatically builds iOS app and uploads to
TestFlight!

--

## 🐛 Troubleshooting

### "Unable to find a valid signing identity"

**Fix:**

```bash
# List available signing identities
security find-identity -v -p codesigning

# If none, download certificate from developer.apple.com
# Double-click .cer file to install
```

--

### "Provisioning profile has expired"

**Fix:**

1. Go to https://developer.apple.com/account/
2. **Profiles** → Delete old profile
3. Create new profile
4. Download and double-click to install

--

### Build succeeds but app crashes on iPhone

**Fix:**

```bash
# View crash logs
# On Mac: Xcode → Window → Devices and Simulators
# Select iPhone → View Device Logs

# Common causes:
# 1. Missing permissions in Info.plist
# 2. Network security (ATS) blocking HTTP
# 3. Missing frameworks
```

--

### App shows white screen on launch

**Fix:** Add to `Platforms/iOS/Info.plist`:

```xml
<key>UILaunchScreen</key>
<dict>
    <key>UIImageName</key>
    <string>splash</string>
    <key>UIColorName</key>
    <string>SplashColor</string>
</dict>
```

--

## Path Comparison

| Path               | Time         | Cost     | Testers   | Renewal | Best For               |
| ------------------ | ------------ | -------- | --------- | ------- | ---------------------- |
| **Android APK**    | 30 min       | FREE     | Unlimited | Never   | Immediate testing      |
| **TestFlight**     | 2-4 weeks    | $99/year | 10,000    | Yearly  | Law firm distribution  |
| **Development**    | 2-3 hours    | FREE     | 1 (you)   | 7 days  | Quick personal testing |
| **GitHub Actions** | 1 hour setup | FREE     | Auto      | Never   | CI/CD automation       |

--

## 📅 Recommended Timeline

### This Week

- ✅ **Day 1:** Build Android APK, test on Android phone
- ⏳ **Day 2:** Enroll in Apple Developer Program
- ⏳ **Day 3-4:** Wait for approval

### Next Week

- ⏳ **Day 7:** Create App ID, certificates
- ⏳ **Day 8:** Set up cloud Mac (if needed)
- ⏳ **Day 9:** Build iOS app
- ⏳ **Day 10:** Upload to TestFlight

### Week 3-4

- ⏳ **Day 14:** Invite beta testers (law firms)
- ⏳ **Day 21:** Gather feedback, iterate
- ⏳ **Day 28:** Prepare for App Store submission

--

## 🎯 Next Steps

**RIGHT NOW:**

```powershell
# Build Android APK (works today!)
bm
dotnet build -f net10.0-android34.0 -c Release
```

**THIS WEEK:**

1. Enroll in Apple Developer Program
2. Test app on Android while waiting
3. Set up cloud Mac access (if no Mac)

**NEXT WEEK:**

1. Create certificates and profiles
2. Build iOS app
3. Upload to TestFlight

--

**Support:** See `PROFILE-SETUP-GUIDE.md` for PowerShell shortcuts!  
**Legal Tools:** See `LEGAL-AI-TOOLS.md` for AI features!

🚀 **Start with Android today, iOS will follow!**
