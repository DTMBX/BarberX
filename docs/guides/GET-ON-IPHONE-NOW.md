# 📱 Get Evident on Your iPhone - Practical Guide

**Reality:** iOS apps require a Mac to build. Here are your **real options** with timelines.

--

## 🚀 FASTEST: Test on Android RIGHT NOW (30 min)

**Why:** Build Android APK on Windows, test full app today while iOS setup processes.

### Steps

```powershell
# 1. Navigate to MAUI
bm

# 2. Build Android APK (takes 5-10 min)
dotnet build -f net10.0-android34.0 -c Release

# 3. APK location:
# bin\Release\net10.0-android34.0\com.Evident.matterdocket-Signed.apk
```

### Install on Android Phone

**Method A: Email**

1. Email the APK to yourself
2. Open email on Android phone
3. Download APK
4. Tap to install (allow "Unknown sources")
5. **Done!** ✅

**Method B: USB**

1. Connect Android phone via USB
2. Copy APK to `Downloads` folder
3. On phone: Files → Downloads → Tap APK
4. Install
5. **Done!** ✅

**Same app, same features, available TODAY.**

--

## ⚡ Option 2: Cloud Mac (2-3 hours, $30-79)

**Why:** Build iOS without owning a Mac.

### A. MacinCloud (Cheaper)

**Cost:** $30/month (pay-as-you-go)  
**Setup:** https://www.macincloud.com

1. **Sign up** for MacinCloud account
2. **Choose plan:** "Pay As You Go" ($1/hour)
3. **Access Mac** via remote desktop
4. **Install tools** on cloud Mac:

   ```bash
   # Install Xcode from App Store (free, ~10 GB)
   # Install .NET SDK
   curl -sSL https://dot.net/v1/dotnet-install.sh | bash

   # Install MAUI workload
   dotnet workload install maui
   ```

5. **Clone repo** to cloud Mac:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Evident.info.git
   cd Evident.info/src/Evident.MatterDocket.MAUI
   ```
6. **Build iOS app**:
   ```bash
   dotnet build -f net10.0-ios -c Debug
   ```
7. **Connect iPhone** to cloud Mac via USB tethering (complicated) or use development certificate

**Drawback:** Complex iPhone connection over remote desktop.

### B. MacStadium (Better)

**Cost:** $79/month  
**Setup:** https://www.macstadium.com

Same steps as MacinCloud but:

- ✅ Dedicated Mac instance
- ✅ Better performance
- ✅ Easier iPhone deployment

--

## 🎯 Option 3: GitHub Actions (FREE, 1 day setup)

**Why:** Free Mac runners, automated builds, no Mac needed.

### Setup GitHub Actions Workflow

**Create:** `.github/workflows/ios-build.yml`

```yaml
name: Build iOS App

on:
  workflow_dispatch: # Manual trigger

jobs:
  build-ios:
    runs-on: macos-14 # FREE GitHub-hosted Mac

    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "10.0.x"

      - name: Install MAUI
        run: dotnet workload install maui

      - name: Build iOS
        run: |
          cd src/Evident.MatterDocket.MAUI
          dotnet build -f net10.0-ios -c Release

      - name: Upload IPA
        uses: actions/upload-artifact@v4
        with:
          name: Evident-iOS
          path: |
            src/Evident.MatterDocket.MAUI/bin/Release/net10.0-ios/**/*.app
            src/Evident.MatterDocket.MAUI/bin/Release/net10.0-ios/**/*.ipa
```

### Trigger Build

1. Go to GitHub repo → **Actions** tab
2. Select "Build iOS App" workflow
3. Click **Run workflow**
4. Wait 10-15 minutes
5. Download `.ipa` file from artifacts

### Install on iPhone

**Requires:** Free Apple Developer account

1. **Install Xcode** on any Mac (friend's, library, etc.)
2. **Connect iPhone** via USB
3. **Open Xcode** → Window → Devices and Simulators
4. **Drag .ipa** onto your iPhone in device list
5. **Trust developer** on iPhone: Settings → General → VPN & Device Management
6. **Done!** ✅

**Limitation:** Certificate expires in **7 days** (free account) - need to reinstall weekly.

--

## 🏆 Option 4: Official TestFlight (2-4 weeks, $99/year)

**Why:** Proper iOS distribution, 90-day certificates, up to 10,000 beta testers.

### Timeline

| Week       | Task                                  | Duration          |
| ---------- | ------------------------------------- | ----------------- |
| **Week 1** | Enroll in Apple Developer Program     | 1-2 days approval |
| **Week 2** | Create App ID, certificates, profiles | 2-3 hours         |
| **Week 3** | Build iOS app, upload to TestFlight   | 1-2 hours         |
| **Week 4** | Beta testing, feedback, iterate       | Ongoing           |

### Steps

#### Week 1: Enroll in Apple Developer Program

1. **Visit:** https://developer.apple.com/programs/
2. **Sign in** with Apple ID
3. **Choose:** Individual ($99/year) or Organization ($99/year + D-U-N-S)
4. **Pay:** $99 USD
5. **Wait:** 1-2 days for approval

#### Week 2: Create App ID & Certificates

**On developer.apple.com:**

1. **Certificates, Identifiers & Profiles**
2. **Identifiers** → **+** → App IDs
   - Description: Evident Matter Docket
   - Bundle ID: `com.Evident.matterdocket`
   - Capabilities: (none needed for basic app)
3. **Certificates** → **+** → iOS App Development
   - Upload certificate request (generate on Mac via Keychain Access)
4. **Profiles** → **+** → iOS App Development
   - Select App ID and certificate

#### Week 3: Build & Upload

**On Mac (yours, cloud, or borrowed):**

```bash
# Clone repo
git clone https://github.com/YOUR-USERNAME/Evident.info.git
cd Evident.info/src/Evident.MatterDocket.MAUI

# Build release
dotnet publish -f net10.0-ios -c Release

# Output: bin/Release/net10.0-ios/ios-arm64/publish/Evident.MatterDocket.MAUI.ipa
```

**Upload to TestFlight:**

1. Download **Transporter** app (Mac App Store)
2. Open Transporter
3. Sign in with Apple ID
4. Drag `.ipa` file
5. Click **Deliver**
6. Wait 5-15 minutes for processing

#### Week 4: Install on iPhone

1. **Download TestFlight** app (App Store on iPhone)
2. **Accept invite** (sent to your email)
3. **Install** Evident from TestFlight
4. **Done!** ✅

**Benefits:**

- ✅ 90-day certificates
- ✅ Distribute to 10,000 testers
- ✅ Professional distribution
- ✅ Automatic updates

--

## 🎯 RECOMMENDED PATH

### This Week

```
Day 1 (TODAY): Build Android APK → Test on Android phone
Day 2-3: Enroll in Apple Developer Program ($99)
Day 4-5: Set up GitHub Actions workflow (free Mac builds)
```

### Next Week

```
Week 2: Apple approval arrives → Create App ID & certificates
Week 3: Build iOS with GitHub Actions → Upload to TestFlight
Week 4: Test on iPhone → Distribute to beta testers
```

### Why This Works

- ✅ **Test TODAY** on Android (same app)
- ✅ **iOS setup** processes in background
- ✅ **Official distribution** via TestFlight in 2-3 weeks
- ✅ **Free CI/CD** with GitHub Actions

--

## 📋 Comparison

| Method             | Time        | Cost      | iPhone Install | Certificate Expiry            |
| ------------------ | ----------- | --------- | -------------- | ----------------------------- |
| **Android APK**    | 30 min      | FREE      | N/A (Android)  | Never                         |
| **Cloud Mac**      | 2-3 hours   | $30-79/mo | Complex        | 7 days (free) / 1 year (paid) |
| **GitHub Actions** | 1 day setup | FREE      | Via Xcode      | 7 days (free) / 1 year (paid) |
| **TestFlight**     | 2-4 weeks   | $99/year  | TestFlight app | 90 days (auto-renews)         |

--

## 💡 What to Do RIGHT NOW

### Step 1: Build Android APK (30 min)

```powershell
bm
dotnet build -f net10.0-android34.0 -c Release
# Email yourself: bin\Release\net10.0-android34.0\*.apk
```

### Step 2: Enroll in Apple Developer (5 min)

- Visit: https://developer.apple.com/programs/
- Click "Enroll"
- Pay $99
- Wait 1-2 days

### Step 3: Set up GitHub Actions (30 min)

- Copy workflow from above
- Push to GitHub
- Manual trigger build
- Download .ipa

### Step 4: Test Android Today

- Install APK on Android phone
- Test all features
- Gather feedback

### Step 5: iOS in 2 Weeks

- Apple approval arrives
- Upload to TestFlight
- Install on iPhone
- Ship! 🚀

--

## ❓ FAQ

**Q: Can I build iOS on Windows?**  
A: No. iOS builds require macOS and Xcode. No exceptions.

**Q: What's the absolute fastest way to my iPhone?**  
A: Use a friend's Mac + free Apple Developer account (2-3 hours total). Or GitHub Actions + Xcode install (1 day).

**Q: Is Android version identical to iOS?**  
A: Yes! Same codebase, same features. Test on Android while iOS setup processes.

**Q: Do I need to pay $99 AND use cloud Mac?**  
A: No. $99 Apple Developer unlocks TestFlight. Cloud Mac is only if you don't own a Mac.

**Q: Can GitHub build iOS for free?**  
A: Yes! GitHub Actions includes free Mac runners. Perfect for testing builds.

--

## 🚀 Start Now

```powershell
# Build Android APK RIGHT NOW
bm
dotnet build -f net10.0-android34.0 -c Release

# While that builds, enroll in Apple Developer Program:
# https://developer.apple.com/programs/
```

**Test on Android today. iOS in 2-3 weeks. Perfect! ✅**
