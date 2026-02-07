# 📱 Deploy Evident MAUI to iPhone (TestFlight)

**Goal:** Get the app on your iPhone for testing in ~30 minutes

--

## Prerequisites

### 1. **Apple Developer Account** (Required)

- **Free Account:** Can run on YOUR device only (7-day certificate)
- **Paid Account ($99/year):** Can use TestFlight, distribute to testers
- Sign up: https://developer.apple.com/programs/

### 2. **Mac Computer** (Required for iOS builds)

- .NET MAUI iOS builds require macOS
- Xcode 15+ installed
- Paired with Visual Studio

### 3. **iPhone**

- iOS 15.0 or later
- Connected to Mac via USB or Wi-Fi

--

## Quick Path: Development Build (FREE - No Mac Required!)

If you just want to test on YOUR iPhone quickly:

### Option 1: Use Visual Studio on Windows (Paired to Mac)

**Not ideal but possible:**

1. Rent a cloud Mac (MacStadium, MacinCloud)
2. Pair Visual Studio Windows to cloud Mac
3. Build and deploy remotely

**Cost:** ~$30/month for cloud Mac

### Option 2: Use GitHub Actions (Easiest!)

**Deploy via CI/CD - No local Mac needed:**

1. **Fork repository to GitHub**
2. **Add Apple secrets to GitHub**
3. **Push code - auto-builds iOS**
4. **Download .ipa from artifacts**
5. **Install via TestFlight or Xcode**

**I'll show you this method below** ✅

--

## Recommended Path: TestFlight (Best for Testing)

### Step 1: Set Up Apple Developer Account (10 min)

1. **Go to:** https://developer.apple.com/account
2. **Sign in** with your Apple ID
3. **Enroll** in Apple Developer Program ($99/year)
4. **Wait** for approval (usually 24-48 hours)

### Step 2: Create App Store Connect Record (5 min)

1. **Go to:** https://appstoreconnect.apple.com
2. **Click:** My Apps → + → New App
3. **Fill in:**
   - Platform: iOS
   - Name: Evident Matter Docket
   - Primary Language: English
   - Bundle ID: com.Evident.matterdocket (create new)
   - SKU: Evident-MAUI-001

4. **Save**

### Step 3: Create Certificates & Provisioning (10 min)

**On Mac:**

```bash
# Install Xcode command line tools
xcode-select -install

# Generate certificate signing request
# Keychain Access → Certificate Assistant → Request Certificate from CA
# Email: your-email@example.com
# Common Name: Evident iOS Distribution
# Save to disk: Evident.certSigningRequest
```

**On Apple Developer Portal:**

1. **Go to:** https://developer.apple.com/account/resources/certificates
2. **Click:** + → iOS Distribution (App Store and Ad Hoc)
3. **Upload:** Evident.certSigningRequest
4. **Download** certificate, double-click to install in Keychain

**Create App ID:**

1. **Go to:** Identifiers → +
2. **Select:** App IDs → App
3. **Description:** Evident Matter Docket
4. **Bundle ID:** com.Evident.matterdocket (Explicit)
5. **Capabilities:** Enable Push Notifications, Sign in with Apple (if needed)
6. **Register**

**Create Provisioning Profile:**

1. **Go to:** Profiles → +
2. **Select:** App Store Connect
3. **App ID:** com.Evident.matterdocket
4. **Certificate:** Select your distribution certificate
5. **Download** and double-click to install

### Step 4: Configure MAUI Project (5 min)

Edit `src/Evident.MatterDocket.MAUI/Evident.MatterDocket.MAUI.csproj`:

```xml
<PropertyGroup Condition="$(TargetFramework.Contains('-ios'))">
    <!-- App Bundle ID ->
    <ApplicationId>com.Evident.matterdocket</ApplicationId>

    <!-- Display Name ->
    <ApplicationTitle>Evident</ApplicationTitle>
    <ApplicationDisplayVersion>1.0</ApplicationDisplayVersion>
    <ApplicationVersion>1</ApplicationVersion>

    <!-- Provisioning ->
    <CodesignKey>iPhone Distribution</CodesignKey>
    <CodesignProvision>Evident Matter Docket Distribution</CodesignProvision>
    <CodesignEntitlements>Platforms/iOS/Entitlements.plist</CodesignEntitlements>

    <!-- Architecture ->
    <RuntimeIdentifiers>ios-arm64</RuntimeIdentifiers>

    <!-- iOS Version ->
    <SupportedOSPlatformVersion>15.0</SupportedOSPlatformVersion>
</PropertyGroup>
```

Create `src/Evident.MatterDocket.MAUI/Platforms/iOS/Entitlements.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>aps-environment</key>
    <string>production</string>
</dict>
</plist>
```

### Step 5: Build iOS App (On Mac)

```bash
cd /path/to/Evident.info/src/Evident.MatterDocket.MAUI

# Restore packages
dotnet restore

# Build for iOS
dotnet build -f net10.0-ios -c Release

# Publish .ipa
dotnet publish -f net10.0-ios -c Release -p:ArchiveOnBuild=true
```

**Output:**
`bin/Release/net10.0-ios/ios-arm64/publish/Evident.MatterDocket.MAUI.ipa`

### Step 6: Upload to TestFlight (5 min)

**Option A: Xcode (Easiest)**

```bash
# Open in Xcode
open bin/Release/net10.0-ios/Evident.MatterDocket.MAUI.xcarchive

# Window → Organizer → Archives
# Select archive → Distribute App → App Store Connect
# Upload
```

**Option B: Command Line (Faster)**

```bash
# Install Apple's altool
xcode-select -install

# Upload to App Store Connect
xcrun altool -upload-app \
  -type ios \
  -file bin/Release/net10.0-ios/ios-arm64/publish/Evident.MatterDocket.MAUI.ipa \
  -username your-apple-id@example.com \
  -password your-app-specific-password
```

**Get app-specific password:**

1. Go to https://appleid.apple.com/account/manage
2. Sign in
3. App-Specific Passwords → Generate Password
4. Copy and use above

### Step 7: Configure TestFlight (3 min)

1. **Go to:** https://appstoreconnect.apple.com
2. **Select:** Your app → TestFlight
3. **Wait** for processing (10-30 minutes)
4. **Add testers:**
   - Internal Testing: Add your email
   - External Testing: Add other emails (requires Apple review)

5. **Send invites**

### Step 8: Install on iPhone (2 min)

1. **Check email** on iPhone (TestFlight invite)
2. **Install TestFlight app** from App Store (if not already)
3. **Open invite link**
4. **Install Evident**
5. **Launch!** 🎉

--

## Automated Deployment: GitHub Actions (Best Method!)

**No Mac needed! Build in the cloud!**

### Create `.github/workflows/ios-build.yml`

```yaml
name: Build iOS

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-ios:
    runs-on: macos-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup .NET
        uses: actions/setup-dotnet@v3
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
          dotnet publish -f net10.0-ios -c Release \
            -p:ArchiveOnBuild=true \
            -p:CodesignKey="${{ secrets.IOS_SIGNING_KEY }}" \
            -p:CodesignProvision="${{ secrets.IOS_PROVISION }}"

      - name: Upload IPA
        uses: actions/upload-artifact@v3
        with:
          name: Evident-iOS
          path: src/Evident.MatterDocket.MAUI/bin/Release/net10.0-ios/ios-arm64/publish/*.ipa
```

**Add secrets to GitHub:**

1. Go to repo → Settings → Secrets → Actions
2. Add:
   - `IOS_SIGNING_KEY` = Your distribution certificate
   - `IOS_PROVISION` = Your provisioning profile name

**Push to trigger build:**

```bash
git add .github/workflows/ios-build.yml
git commit -m "Add iOS build workflow"
git push origin main
```

**Download .ipa:**

1. Go to Actions tab
2. Select latest workflow run
3. Download `Evident-iOS` artifact
4. Upload to TestFlight manually

--

## Quick Development Install (FREE - Same Day!)

**For immediate testing on YOUR device only:**

### Method 1: Xcode Direct Install (Mac Required)

```bash
# On Mac, connect iPhone via USB

# Build and run
cd src/Evident.MatterDocket.MAUI
dotnet build -f net10.0-ios -c Debug --target=ios

# Deploy to connected iPhone
dotnet publish -f net10.0-ios -c Debug -p:BuildIpa=true
```

### Method 2: Visual Studio for Mac (Easiest!)

1. **Open** project in Visual Studio for Mac
2. **Select** iOS device from dropdown
3. **Click** Run ▶️
4. **Enter** Apple ID when prompted
5. **Trust** developer on iPhone (Settings → General → Device Management)
6. **App installs** automatically

--

## Troubleshooting

### "No valid iOS code signing keys found"

**Solution:**

```bash
# Check certificates in Keychain
security find-identity -p codesigning -v

# Should show: iPhone Distribution: Your Name (XXXXXXXXXX)
# If not, re-download certificate from developer.apple.com
```

### "Provisioning profile doesn't match bundle ID"

**Solution:**

- Make sure `ApplicationId` in .csproj matches Bundle ID in provisioning profile
- Re-download provisioning profile
- Clean and rebuild: `dotnet clean && dotnet build`

### "iPhone is not trusted"

**Solution:** On iPhone: Settings → General → Device Management → Trust "Your
Name"

### "This app cannot be installed because its integrity could not be verified"

**Solution:**

- Use proper distribution certificate (not development)
- Or use TestFlight (bypasses this issue)

--

## Alternative: Android First (Easier!)

**While waiting for iOS approval, test on Android:**

```bash
# Build Android APK (works on Windows)
cd src\Evident.MatterDocket.MAUI
dotnet build -f net10.0-android -c Debug

# Output: bin\Debug\net10.0-android\com.Evident.matterdocket-Signed.apk

# Transfer to phone and install
# Or use USB debugging:
adb install bin\Debug\net10.0-android\com.Evident.matterdocket-Signed.apk
```

--

## Comparison: Deployment Methods

| Method             | Time     | Cost     | Devices   | Mac Required |
| ------------------ | -------- | -------- | --------- | ------------ |
| **TestFlight**     | 48 hours | $99/year | Unlimited | Yes          |
| **Direct Install** | 5 min    | FREE     | 1 (yours) | Yes          |
| **GitHub Actions** | 30 min   | FREE     | Unlimited | No           |
| **Android APK**    | 5 min    | FREE     | Unlimited | No           |

--

## Recommended Workflow

**Week 1:**

- Build Android APK → Test on Android phone
- Submit to Apple Developer Program
- Build Windows .exe → Test on desktop

**Week 2:**

- Apple approval arrives
- Set up TestFlight
- Build iOS .ipa
- Test on iPhone

**Week 3:**

- Polish based on feedback
- Add more testers
- Prepare for App Store submission

--

## Next Steps After Install

Once installed on iPhone:

1. **Launch** Evident app
2. **Login** with test account
3. **Go to Settings** → Add OpenAI API Key
4. **Create** first project
5. **Start chatting** with GPT! 🎉

--

**Estimated Time:**

- First time: 2-3 hours (includes approval wait)
- After setup: 10 minutes per build

**Best Method for Now:**

1. Start with Android (immediate testing)
2. Set up TestFlight in parallel
3. Use GitHub Actions for automated builds

📱 **Ready to deploy!**
