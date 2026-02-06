# 📁 Evident Repository Structure Explained

**Question:** "Do I have a separate repo folder for each app platform? How does
it work? Where is our code?"

**Answer:** You have **ONE repository** with **multiple project folders**, but
most are legacy/placeholder. Here's what you actually have:

--

## 🎯 What You're Actually Using (Active Projects)

### 1. **Flask Backend (Python)** - Main Production App

**Location:** `C:\web-dev\github-repos\Evident.info\` (root folder)

```
Evident.info/
├── app.py                    ← Main Flask application
├── api/                      ← REST API (Phase 1 - NEW)
│   ├── __init__.py
│   ├── auth.py              ← JWT authentication
│   ├── upload.py            ← File uploads
│   ├── analysis.py          ← AI analysis
│   ├── user.py
│   ├── stripe_endpoints.py
│   ├── evidence.py
│   └── admin.py
├── templates/               ← HTML templates for web UI
├── static/                  ← CSS, JS, images
├── models_auth.py           ← Database models
├── tier_gating.py           ← Feature gating
├── stripe_payment_service.py
└── requirements.txt         ← Python dependencies
```

**Purpose:** This is your **production Flask app** that runs at
https://Evident.info  
**Platforms:** Web browsers (all platforms)  
**Status:** ✅ Production-ready with new REST API

--

### 2. **.NET MAUI App (C#)** - Cross-Platform Native Apps

**Location:**
`C:\web-dev\github-repos\Evident.info\src\Evident.MatterDocket.MAUI\`

```
src/Evident.MatterDocket.MAUI/
├── Services/                ← Phase 2 - API client services
│   ├── ApiService.cs
│   ├── AuthService.cs
│   ├── UploadService.cs
│   ├── AnalysisService.cs
│   ├── UserService.cs
│   ├── BillingService.cs
│   ├── EvidenceService.cs
│   ├── TierService.cs
│   └── CaseService.cs
├── ViewModels/              ← Phase 2 - MVVM ViewModels
│   ├── BaseViewModel.cs
│   ├── LoginViewModel.cs
│   ├── DashboardViewModel.cs
│   └── UploadViewModel.cs
├── Views/                   ← Phase 3 - XAML UI Pages
│   ├── LoginPage.xaml
│   ├── DashboardPage.xaml
│   └── UploadPage.xaml
├── Models/
│   └── ApiModels.cs         ← 40+ API DTOs
├── Converters/
│   └── ValueConverters.cs   ← UI converters
├── Helpers/
│   └── Constants.cs         ← API URLs, tier limits
├── Platforms/               ← Platform-specific code
│   ├── Windows/             ← Windows-specific
│   ├── iOS/                 ← iOS-specific
│   └── Android/             ← Android-specific
├── MauiProgram.cs           ← Dependency injection
├── AppShell.xaml            ← Navigation
└── Evident.MatterDocket.MAUI.csproj
```

**Purpose:** This **ONE MAUI project** builds apps for **ALL platforms**  
**Platforms:**

- Windows desktop (.exe)
- iOS (iPhone/iPad)
- Android (phones/tablets)
- macOS (optional)

**Status:** ✅ Phase 1-3 complete, ready for testing

--

## 🔍 How .NET MAUI Works (The Magic!)

### **ONE Codebase → MULTIPLE Platforms**

```
Evident.MatterDocket.MAUI (Single Project)
           │
           ├─→ Build for Windows   → Evident.exe
           ├─→ Build for iOS       → Evident.app
           ├─→ Build for Android   → Evident.apk
           └─→ Build for macOS     → Evident.app (Mac)
```

**How it works:**

1. You write code **once** in `src/Evident.MatterDocket.MAUI/`
2. .NET MAUI compiles it for each platform
3. Platform-specific features go in `Platforms/` subfolders
4. Shared code (Services, ViewModels, Views) works everywhere

**Example:**

```bash
# Build Windows app
dotnet build -f net9.0-windows10.0.19041.0

# Build iOS app
dotnet build -f net9.0-ios

# Build Android app
dotnet build -f net9.0-android
```

--

## 📂 Other Folders (Legacy/Unused)

These folders exist but are **NOT being used** in our current implementation:

### **src/Evident.Web/**

- **Purpose:** Was intended for Blazor web client
- **Status:** ❌ Not used (we use Flask templates instead)
- **Can delete:** Yes (or keep for future Blazor rewrite)

### **src/Evident.Mobile/**

- **Purpose:** Was a placeholder for mobile
- **Status:** ❌ Not used (MAUI handles mobile now)
- **Can delete:** Yes

### **src/Evident.Shared/**

- **Purpose:** Was for shared .NET code
- **Status:** ❌ Not used (MAUI Services are the shared code)
- **Can delete:** Yes

### **src/Evident.Infrastructure/**

- **Purpose:** Was for database/infrastructure layer
- **Status:** ❌ Not used (Flask handles this)
- **Can delete:** Yes

### **src/Evident.FlaskBridge/**

- **Purpose:** Was for .NET-to-Flask communication
- **Status:** ❌ Not used (MAUI calls Flask REST API directly)
- **Can delete:** Yes

--

## 🎯 Current Architecture (What We Built)

```
┌─────────────────────────────────────────────────────┐
│                  ONE REPOSITORY                      │
│            github.com/your-username/Evident.info     │
└──────────────┬──────────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼──────────┐   ┌──────▼────────────────────┐
│ Flask Backend│   │  .NET MAUI Client App     │
│ (Python)     │   │  (C#)                     │
│              │   │                           │
│ Location:    │   │ Location:                 │
│ / (root)     │   │ src/Evident.MatterDocket  │
│              │   │     .MAUI/                │
│              │   │                           │
│ Runs at:     │   │ Builds to:                │
│ Evident.info │   │ • Windows .exe            │
│              │   │ • iOS .app                │
│ Serves:      │   │ • Android .apk            │
│ • Web UI     │   │                           │
│ • REST API   │   │ Connects to:              │
│              │   │ Flask REST API            │
└──────────────┘   └───────────────────────────┘
```

--

## 🔗 How They Work Together

### **Flask Backend:**

- Runs on server (Render.com)
- URL: https://Evident.info
- Provides:
  - Web UI (HTML templates for browsers)
  - REST API at `/api/v1/*` (for MAUI apps)
  - Database access
  - AI processing
  - Stripe integration

### **MAUI Client Apps:**

- Run on user devices (Windows PC, iPhone, Android phone)
- **Call Flask REST API** for all data:
  - `POST /api/v1/auth/login` - Login
  - `POST /api/v1/upload/pdf` - Upload files
  - `GET /api/v1/user/profile` - Get user data
  - etc.

--

## 📍 Where to Find Your Code

### **Want to edit the Flask backend?**

```bash
cd C:\web-dev\github-repos\Evident.info
# Edit: app.py, api/*.py, templates/*.html, etc.
```

### **Want to edit the MAUI apps?**

```bash
cd C:\web-dev\github-repos\Evident.info\src\Evident.MatterDocket.MAUI
# Edit: Services/*.cs, ViewModels/*.cs, Views/*.xaml
```

### **Want to edit API endpoints?**

```bash
cd C:\web-dev\github-repos\Evident.info\api
# Edit: auth.py, upload.py, analysis.py, etc.
```

--

## 🚀 Deployment Paths

### **Flask Backend:**

```bash
# Deployed to Render.com
git push origin main
# → Render auto-deploys
# → Live at https://Evident.info
```

### **Windows App:**

```bash
cd src/Evident.MatterDocket.MAUI
dotnet publish -f net9.0-windows10.0.19041.0 -c Release
# → Creates Evident.exe
# → Package as MSIX for Microsoft Store
```

### **iOS App:**

```bash
cd src/Evident.MatterDocket.MAUI
dotnet publish -f net9.0-ios -c Release
# → Creates Evident.app
# → Upload to App Store Connect
```

### **Android App:**

```bash
cd src/Evident.MatterDocket.MAUI
dotnet publish -f net9.0-android -c Release
# → Creates Evident.apk
# → Upload to Google Play Console
```

--

## 📊 Summary

| Platform            | Location                         | Technology    | Status              |
| ------------------- | -------------------------------- | ------------- | ------------------- |
| **Web Browser**     | `/` (root)                       | Flask + HTML  | ✅ Production       |
| **REST API**        | `/api/`                          | Flask + PyJWT | ✅ Phase 1 Complete |
| **Windows Desktop** | `src/Evident.MatterDocket.MAUI/` | .NET MAUI     | ✅ Ready to test    |
| **iOS**             | `src/Evident.MatterDocket.MAUI/` | .NET MAUI     | ✅ Ready to test    |
| **Android**         | `src/Evident.MatterDocket.MAUI/` | .NET MAUI     | ✅ Ready to test    |

--

## 💡 Key Takeaways

1. **ONE Git Repository** - Everything in `Evident.info/`

2. **TWO Active Projects:**
   - Flask backend (root folder)
   - MAUI client (src/Evident.MatterDocket.MAUI/)

3. **MAUI = Cross-Platform Magic:**
   - Write code once in `Evident.MatterDocket.MAUI/`
   - Build for Windows, iOS, Android from same codebase
   - Platform-specific code goes in `Platforms/` subfolders

4. **Other `src/` folders are unused** - Created earlier but not part of current
   architecture

5. **All apps connect to same Flask backend** via REST API

--

## 🎯 Quick Navigation

**Edit Backend API:**

```bash
C:\web-dev\github-repos\Evident.info\api\
```

**Edit MAUI Services:**

```bash
C:\web-dev\github-repos\Evident.info\src\Evident.MatterDocket.MAUI\Services\
```

**Edit MAUI UI:**

```bash
C:\web-dev\github-repos\Evident.info\src\Evident.MatterDocket.MAUI\Views\
```

**Edit Flask Web Templates:**

```bash
C:\web-dev\github-repos\Evident.info\templates\
```

--

**Simple Answer:** You have **ONE repository** with **ONE Flask backend** and
**ONE MAUI project** that builds apps for all platforms. The magic of .NET MAUI
is that you write the code once and it compiles to Windows .exe, iOS .app, and
Android .apk from the same source! 🎉
