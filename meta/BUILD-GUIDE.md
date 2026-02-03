# Evident Multi-Platform Build Guide

## Overview

Evident is a comprehensive legal tech platform with support for:

- **Windows Desktop** (.NET MAUI)
- **iOS Mobile** (.NET MAUI)
- **Android Mobile** (.NET MAUI)
- **Web Application** (Flask + Modern Frontend)
- **Mobile Web** (Responsive Web Design)

---

## Prerequisites

### For All Platforms

- **.NET 9.0 SDK** or later
- **Visual Studio 2022** (17.8+) or **Visual Studio Code**
- **Git** for version control

### For Mobile Development

- **Xcode 15+** (macOS only, for iOS)
- **Android SDK** (API 21+)
- **JDK 17** or later

### For Web Development

- **Python 3.9+**
- **Node.js 18+** and **npm**
- **Flask** and dependencies

---

## Project Structure

```
Evident.info/
├── src/
│   ├── Evident.Mobile/          # .NET MAUI cross-platform app
│   ├── Evident.Web/             # ASP.NET Core Web API
│   ├── Evident.Shared/          # Shared models and services
│   └── Evident.Infrastructure/  # Infrastructure layer
├── app.py                       # Flask backend
├── templates/                   # Web templates
├── static/                      # Web static assets
└── barber-cam/                  # BWC analysis tools (encrypted)
```

---

## Building the Mobile Apps (.NET MAUI)

### Windows Desktop App

```powershell
# Navigate to project
cd src\Evident.Mobile

# Restore dependencies
dotnet restore

# Build for Windows
dotnet build -f net10.0-windows10.0.19041.0 -c Release

# Run
dotnet run -f net10.0-windows10.0.19041.0
```

### Android App

```powershell
# Build for Android
dotnet build -f net10.0-android -c Release

# Deploy to connected device/emulator
dotnet build -f net10.0-android -c Release -t:Run

# Create APK
dotnet publish -f net10.0-android -c Release
```

**Output:** `bin\Release\net10.0-android\publish\*.apk`

### iOS App (macOS only)

```bash
# Build for iOS
dotnet build -f net10.0-ios -c Release

# Deploy to simulator
dotnet build -f net10.0-ios -c Release -t:Run

# Create IPA for App Store
dotnet publish -f net10.0-ios -c Release -p:ArchiveOnBuild=true
```

**Output:** `bin\Release\net10.0-ios\publish\*.ipa`

---

## Building the Web Application

### Flask Backend

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Production deployment
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### ASP.NET Core Web API

```powershell
cd src\Evident.Web

# Restore and build
dotnet restore
dotnet build -c Release

# Run
dotnet run

# Publish for deployment
dotnet publish -c Release -o publish
```

---

## Configuration

### Mobile App Configuration

Edit `src\Evident.Mobile\MauiProgram.cs`:

```csharp
#if DEBUG
    client.BaseAddress = new Uri("http://localhost:5000");
#else
    client.BaseAddress = new Uri("https://api.Evident.info");
#endif
```

### Web App Configuration

Create `.env` file (encrypted with git-crypt):

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host/db
OPENAI_API_KEY=your-openai-key
STRIPE_SECRET_KEY=your-stripe-key
```

---

## Platform-Specific Features

### Windows

- Native file system integration
- Windows Hello authentication
- Desktop notifications

### iOS

- Face ID/Touch ID authentication
- iOS Share Sheet integration
- Background upload support

### Android

- Biometric authentication
- Android Share integration
- Background services

### Web/Mobile Web

- Progressive Web App (PWA) support
- Offline mode with service workers
- Responsive design for all screen sizes

---

## Deployment

### Mobile Apps

#### iOS App Store

1. Configure signing in Xcode
2. Build archive: `dotnet publish -f net10.0-ios -c Release`
3. Upload to App Store Connect via Xcode or Transporter

#### Google Play Store

1. Generate signed APK/AAB
2. Configure app signing in Google Play Console
3. Upload via Google Play Console

#### Microsoft Store (Windows)

1. Create MSIX package
2. Submit via Partner Center

### Web Application

#### Netlify (Static Frontend)

```powershell
# Build static assets
npm run build

# Deploy
netlify deploy --prod
```

#### Railway/Render (Flask Backend)

```yaml
# render.yaml
services:
  - type: web
    name: Evident-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

---

## Testing

### Mobile Apps

```powershell
# Run unit tests
dotnet test

# Run UI tests (if configured)
dotnet test --filter Category=UI
```

### Web Application

```powershell
# Python tests
pytest

# JavaScript tests
npm test

# E2E tests
npx playwright test
```

---

## Troubleshooting

### Common Issues

**MAUI Build Errors:**

- Clean and rebuild: `dotnet clean && dotnet build`
- Clear NuGet cache: `dotnet nuget locals all --clear`

**Android Deployment Issues:**

- Check ADB connection: `adb devices`
- Restart ADB server: `adb kill-server && adb start-server`

**iOS Code Signing:**

- Verify provisioning profiles in Xcode
- Check bundle identifier matches

**Flask Import Errors:**

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

---

## Development Workflow

1. **Start Flask backend:** `python app.py`
2. **Run mobile app:** `dotnet run -f net10.0-android` (or desired platform)
3. **Make changes** to shared code in `Evident.Shared`
4. **Test on multiple platforms** before committing
5. **Commit and push** to git repository

---

## Resources

- [.NET MAUI Documentation](https://learn.microsoft.com/dotnet/maui/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Evident API Reference](docs/api/API-REFERENCE.md)
- [Contributing Guidelines](CONTRIBUTING.md)

---

## Support

For issues or questions:

- GitHub Issues: https://github.com/DTB396/Evident.info/issues
- Email: support@Evident.info
- Documentation: https://Evident.info/docs
