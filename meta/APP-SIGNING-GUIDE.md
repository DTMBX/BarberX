# Evident Mobile App Signing Guide

Complete guide for configuring code signing for iOS and Android deployments.

---

## Android App Signing

### 1. Generate Keystore

```powershell
# Generate a new keystore (do this once)
keytool -genkey -v -keystore Evident-release.keystore -alias Evident -keyalg RSA -keysize 2048 -validity 10000

# You'll be prompted for:
# - Keystore password (save securely!)
# - Key password (save securely!)
# - Your name, organization, city, state, country
```

**Important:** Store the keystore file and passwords securely. You cannot
recover them if lost!

### 2. Configure Android Signing

Create `src/Evident.Mobile/Platforms/Android/signing.properties`:

```properties
keystore.file=Evident-release.keystore
keystore.password=YOUR_KEYSTORE_PASSWORD
key.alias=Evident
key.password=YOUR_KEY_PASSWORD
```

**⚠️ NEVER commit this file to git!** Add to `.gitignore`:

```gitignore
**/signing.properties
**/*.keystore
**/*.jks
```

### 3. Update Android Project File

Edit `src/Evident.Mobile/Evident.Mobile.csproj`:

```xml
<PropertyGroup Condition="'$(Configuration)' == 'Release' AND '$(TargetFramework)' == 'net10.0-android'">
  <AndroidKeyStore>True</AndroidKeyStore>
  <AndroidSigningKeyStore>Evident-release.keystore</AndroidSigningKeyStore>
  <AndroidSigningKeyAlias>Evident</AndroidSigningKeyAlias>
  <AndroidSigningKeyPass>$(AndroidSigningKeyPassword)</AndroidSigningKeyPass>
  <AndroidSigningStorePass>$(AndroidSigningStorePassword)</AndroidSigningStorePass>
</PropertyGroup>
```

### 4. Build Signed APK/AAB

```powershell
# Set environment variables (or use secure storage)
$env:AndroidSigningKeyPassword = "YOUR_KEY_PASSWORD"
$env:AndroidSigningStorePassword = "YOUR_KEYSTORE_PASSWORD"

# Build signed APK
dotnet publish src/Evident.Mobile/Evident.Mobile.csproj `
  -f net10.0-android `
  -c Release `
  -p:AndroidPackageFormat=apk

# Build signed AAB (for Google Play)
dotnet publish src/Evident.Mobile/Evident.Mobile.csproj `
  -f net10.0-android `
  -c Release `
  -p:AndroidPackageFormat=aab
```

### 5. Google Play Console Setup

1. Go to [Google Play Console](https://play.google.com/console)
2. Create a new app or select existing
3. Navigate to **Release > Setup > App signing**
4. Upload your signing key or let Google manage it
5. Configure app details, screenshots, and privacy policy
6. Submit for review

---

## iOS App Signing

### 1. Apple Developer Account

1. Enroll in [Apple Developer Program](https://developer.apple.com/programs/)
   ($99/year)
2. Create App ID in
   [Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources/)
   - Bundle ID: `com.Evident.mobile` (must match your app)
   - Enable capabilities: Push Notifications, In-App Purchase, etc.

### 2. Create Certificates

#### Development Certificate

```bash
# On macOS, open Keychain Access
# Go to: Keychain Access > Certificate Assistant > Request a Certificate from a Certificate Authority
# Save the CSR file

# Upload CSR to Apple Developer Portal
# Download the certificate and double-click to install in Keychain
```

#### Distribution Certificate

```bash
# Same process as development, but select "App Store and Ad Hoc" distribution
# Download and install the distribution certificate
```

### 3. Create Provisioning Profiles

1. Go to Apple Developer Portal > Profiles
2. Create **Development Profile**:
   - Type: iOS App Development
   - App ID: Select your Evident app ID
   - Certificates: Select your development certificate
   - Devices: Select test devices
3. Create **Distribution Profile**:
   - Type: App Store
   - App ID: Select your Evident app ID
   - Certificates: Select your distribution certificate

### 4. Configure Xcode Signing

Open `src/Evident.Mobile/Platforms/iOS/Info.plist` and verify:

```xml
<key>CFBundleIdentifier</key>
<string>com.Evident.mobile</string>
<key>CFBundleName</key>
<string>Evident</string>
<key>CFBundleVersion</key>
<string>1.0</string>
```

### 5. Build and Archive

```bash
# On macOS
cd src/Evident.Mobile

# Build for iOS
dotnet build -f net10.0-ios -c Release

# Create archive for App Store
dotnet publish -f net10.0-ios -c Release -p:ArchiveOnBuild=true -p:RuntimeIdentifier=ios-arm64

# The IPA will be in: bin/Release/net10.0-ios/ios-arm64/publish/
```

### 6. Upload to App Store Connect

```bash
# Install Transporter app from Mac App Store
# Or use command line:
xcrun altool --upload-app -f Evident.ipa -u YOUR_APPLE_ID -p YOUR_APP_SPECIFIC_PASSWORD

# Or use Xcode:
# Open Xcode > Window > Organizer > Archives
# Select your archive > Distribute App > App Store Connect
```

### 7. App Store Connect Configuration

1. Go to [App Store Connect](https://appstoreconnect.apple.com/)
2. Create new app or select existing
3. Fill in app information:
   - Name: Evident Legal Tech
   - Subtitle: Professional Legal Analysis
   - Category: Business / Productivity
   - Privacy Policy URL: https://Evident.info/privacy
4. Add screenshots (required sizes):
   - 6.7" iPhone: 1290 x 2796
   - 6.5" iPhone: 1242 x 2688
   - 5.5" iPhone: 1242 x 2208
   - iPad Pro: 2048 x 2732
5. Submit for review

---

## Windows App Signing

### 1. Create Certificate

```powershell
# For testing (self-signed)
New-SelfSignedCertificate -Type Custom -Subject "CN=Evident" -KeyUsage DigitalSignature -FriendlyName "Evident Certificate" -CertStoreLocation "Cert:\CurrentUser\My"

# For production, purchase a code signing certificate from:
# - DigiCert
# - Sectigo
# - GlobalSign
```

### 2. Create MSIX Package

Edit `src/Evident.Mobile/Platforms/Windows/Package.appxmanifest`:

```xml
<Identity Name="Evident.Mobile"
          Publisher="CN=Your Company Name"
          Version="1.0.0.0" />
```

### 3. Build and Sign

```powershell
# Build MSIX
dotnet publish src/Evident.Mobile/Evident.Mobile.csproj `
  -f net10.0-windows10.0.19041.0 `
  -c Release `
  -p:GenerateAppxPackageOnBuild=true `
  -p:AppxPackageSigningEnabled=true

# Sign manually if needed
signtool sign /f YourCertificate.pfx /p PASSWORD /fd SHA256 Evident.msix
```

### 4. Microsoft Store Submission

1. Go to [Partner Center](https://partner.microsoft.com/dashboard)
2. Create new app submission
3. Upload MSIX package
4. Configure store listing
5. Submit for certification

---

## CI/CD Integration

### GitHub Actions Secrets

Add these secrets to your GitHub repository:

#### Android

- `ANDROID_KEYSTORE_BASE64` - Base64 encoded keystore file
- `ANDROID_KEYSTORE_PASSWORD` - Keystore password
- `ANDROID_KEY_ALIAS` - Key alias
- `ANDROID_KEY_PASSWORD` - Key password

#### iOS

- `IOS_CERTIFICATE_BASE64` - Base64 encoded certificate
- `IOS_CERTIFICATE_PASSWORD` - Certificate password
- `IOS_PROVISIONING_PROFILE_BASE64` - Base64 encoded provisioning profile
- `APPLE_ID` - Your Apple ID
- `APPLE_APP_SPECIFIC_PASSWORD` - App-specific password

### Encode Files for GitHub Secrets

```powershell
# Windows PowerShell
$bytes = [System.IO.File]::ReadAllBytes("Evident-release.keystore")
$base64 = [System.Convert]::ToBase64String($bytes)
$base64 | Out-File keystore-base64.txt

# macOS/Linux
base64 -i certificate.p12 -o certificate-base64.txt
```

---

## Security Best Practices

### ✅ DO:

- Store signing keys in secure password manager (1Password, LastPass)
- Use different keys for development and production
- Enable two-factor authentication on all developer accounts
- Rotate certificates before expiration
- Use GitHub Secrets for CI/CD
- Backup keystore files securely (encrypted cloud storage)

### ❌ DON'T:

- Commit signing keys to git
- Share signing keys via email or chat
- Use weak passwords for keystores
- Store passwords in plain text
- Reuse passwords across services

---

## Troubleshooting

### Android: "Keystore was tampered with"

```powershell
# Verify keystore integrity
keytool -list -v -keystore Evident-release.keystore
```

### iOS: "No valid signing identity"

```bash
# List available certificates
security find-identity -v -p codesigning

# Import certificate
security import certificate.p12 -k ~/Library/Keychains/login.keychain
```

### Windows: "Publisher name does not match"

- Ensure Publisher in Package.appxmanifest matches certificate subject

---

## Resources

- [Android App Signing](https://developer.android.com/studio/publish/app-signing)
- [iOS Code Signing](https://developer.apple.com/support/code-signing/)
- [Windows App Packaging](https://docs.microsoft.com/windows/msix/)
- [.NET MAUI Publishing](https://learn.microsoft.com/dotnet/maui/deployment/)

---

## Support

For signing issues:

- Email: dev@Evident.info
- GitHub Issues: https://github.com/DTB396/Evident.info/issues
