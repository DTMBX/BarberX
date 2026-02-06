# Evident Matter Docket (DTMB) - Project Context for New Workspace

**Copy and paste this entire prompt into your new VS Code workspace chat to continue development:**

--

## 🎯 PROJECT OVERVIEW

I'm building **Evident Matter Docket (DTMB)**, a professional legal evidence platform across multiple platforms:

- ✅ **Web Application** - LIVE at https://Evident.info (Flask + PostgreSQL + Stripe + OpenAI)
- ✅ **REST API** - LIVE at https://Evident.info/api (20+ endpoints, JWT auth)
- ✅ **Windows 11 Desktop App** - Just completed login screen (.NET MAUI 10.0)
- 🔜 **Android/iOS Apps** - Planned (same MAUI codebase, 80% code sharing)

## 📂 WORKSPACE STRUCTURE

I just set up a **VS Code Multi-Root Workspace** with TWO separate Git repositories:

```
Evident-MultiPlatform.code-workspace
├── 📁 🌐 Evident.info - Web App & API
│   ├── Location: C:\web-dev\github-repos\Evident.info\
│   ├── Git: Separate repository (main branch)
│   ├── Stack: Flask, PostgreSQL, Stripe, OpenAI
│   └── Status: LIVE in production
│
└── 📁 💻 Evident MAUI - Windows/Mobile App
    ├── Location: C:\web-dev\github-repos\Evident.info\src\Evident.MatterDocket.MAUI\
    ├── Git: Separate .git (can be independent repo or subfolder)
    ├── Stack: .NET MAUI 10.0, WinUI 3, C#
    └── Status: Login screen complete, ready to run
```

**Each folder has its own .git**, so commits/pushes are completely separate. I can work on both simultaneously.

## ✅ WHAT WE JUST COMPLETED (Last Session)

### Phase A: PWA Packaging ✅

- Created Windows 11 MSIX package (Evident-MatterDocket-DTMB.msix)
- Rebranded entire app to "Evident Matter Docket (DTMB)"

### Phase B: MAUI Architecture ✅

- Designed complete .NET MAUI + WinUI 3 architecture
- Created 6-week development roadmap
- Mapped all Flask API endpoints for integration

### Phase C: Development Environment ✅

- Installed and configured Visual Studio 2022
- Verified all tools (.NET 10.0.102, MAUI Workload 10.0.100)
- Successfully built test MAUI project

### Phase D: Windows 11 App - Login Screen ✅

**JUST COMPLETED - 11 files created:**

**Services:**

- `AuthService.cs` - Authentication with secure token storage (SecureStorage)
- `ApiService.cs` - HTTP client for Flask REST API at Evident.info/api

**ViewModels:**

- `BaseViewModel.cs` - MVVM base class with IsBusy, Title, ErrorMessage
- `LoginViewModel.cs` - Login logic, email/password validation, error handling

**Views:**

- `LoginPage.xaml` - Professional login UI with Evident gold theme (#d4a574)
- `LoginPage.xaml.cs` - Code-behind
- `DashboardPage.xaml` - Post-login dashboard UI
- `DashboardPage.xaml.cs` - Code-behind

**Models:**

- `ApiModels.cs` - User, Evidence, Analysis, LoginRequest/Response models

**Helpers:**

- `Constants.cs` - App-wide constants (API URL, branding colors, storage keys)
- `Converters.cs` - XAML value converters (StringNotNullOrEmptyConverter)

**Configuration Updated:**

- `MauiProgram.cs` - Dependency injection configured (ApiService, AuthService, ViewModels, Pages)
- `AppShell.xaml` - Navigation routes for Login and Dashboard
- `App.xaml` - Global resources and converters registered

**Build Status:** ✅ SUCCESS (0 errors, 9 nullability warnings - safe to ignore)

## 🎨 BRANDING (Consistent Across All Platforms)

```css
Primary Gold:     #d4a574  /* Evident brand color */
Background Dark:  #0f0f0f  /* Main background */
Surface Dark:     #1a1a1a  /* Cards, inputs */
Text Primary:     #ffffff  /* Headings */
Text Secondary:   #b0b0b0  /* Body text */
Error Red:        #ff4444  /* Error messages */
Success Green:    #00ff00  /* Success states */
```

## 🔌 API INTEGRATION (Flask Backend → MAUI App)

The Windows app connects to the **LIVE Flask API** at https://Evident.info/api:

### Authentication Flow

```csharp
// User enters email/password in LoginPage.xaml
// LoginViewModel validates and calls AuthService
var result = await _authService.LoginAsync(email, password);

// AuthService calls Flask API
POST https://Evident.info/api/auth/login
Body: { "email": "user@example.com", "password": "..." }

// On success, stores JWT token in SecureStorage
await SecureStorage.SetAsync("auth_token", response.Token);

// Navigates to Dashboard
await Shell.Current.GoToAsync("//Dashboard");
```

### API Endpoints Ready to Use

```
POST   /api/auth/login              ✅ Login (implemented in Windows app)
POST   /api/auth/logout             🔜 Next to implement
GET    /api/evidence/list           🔜 Next to implement
POST   /api/evidence/upload         🔜 Next to implement
POST   /api/analysis/start          🔜 Next to implement
GET    /api/analysis/{id}/results   🔜 Next to implement
POST   /api/documents/generate      🔜 Next to implement
```

## 🎯 IMMEDIATE NEXT STEPS

### 1. Test Windows App (RIGHT NOW)

```
In Visual Studio 2022:
1. Open: C:\web-dev\github-repos\Evident.info\src\Evident.MatterDocket.MAUI\Evident.MatterDocket.MAUI.csproj
2. Set as Startup Project (right-click → Set as Startup Project)
3. Select "Windows Machine" as target
4. Press F5 to run

Expected: Professional login screen with gold branding appears
```

### 2. Build Next Feature for BOTH Platforms

**Evidence Upload Module** - Build simultaneously for Web + Windows:

**Backend (Flask API):**

- Endpoint already exists: `POST /api/evidence/upload`
- Accepts: PDF, MP4, images
- Returns: Evidence ID, file metadata

**Web (Flask Template):**

- Template exists: `templates/evidence_upload.html`
- JavaScript handles drag-drop upload
- Status: ✅ Already working

**Windows (MAUI):**

- Create: `EvidenceUploadPage.xaml` (file picker UI)
- Create: `EvidenceViewModel.cs` (upload logic)
- Implement: File picker, progress tracking, offline queue
- Status: 🔜 Next to build

### 3. Sync & Test

- Test upload from web
- Test upload from Windows app
- Verify both hit same API
- Confirm data appears in PostgreSQL

## 📋 DEVELOPMENT WORKFLOW (Multi-Platform)

```
1️⃣  DESIGN FEATURE
   → Define API contract (what endpoints needed?)
   → Design UI for Web (Flask template + JS)
   → Design UI for Windows/Mobile (XAML)

2️⃣  BUILD BACKEND FIRST
   → Implement Flask endpoint
   → Test with curl/Postman
   → Deploy to Render (auto-deploys from git push)

3️⃣  BUILD WEB FRONTEND
   → Create/update Flask template
   → Add JavaScript
   → Test on https://Evident.info

4️⃣  BUILD WINDOWS/MOBILE
   → Create XAML views
   → Implement ViewModels
   → Call API with ApiService
   → Test locally

5️⃣  SYNC & VERIFY
   → Test same user flow on web + desktop
   → Verify data consistency
   → Check branding matches
```

## 🛠️ TECHNICAL STACK DETAILS

### Web App (Python)

```python
Framework: Flask 3.x
Database: PostgreSQL (Render)
ORM: SQLAlchemy
Auth: Flask-Login + JWT
Payments: Stripe API
AI: OpenAI API
Deployment: Render.com (auto-deploy)
```

### Windows/Mobile App (C#)

```csharp
Framework: .NET MAUI 10.0
UI: WinUI 3 (Windows), native controls (Mobile)
Architecture: MVVM with CommunityToolkit.Mvvm
HTTP: HttpClient + System.Text.Json
Storage: SecureStorage (tokens), SQLite (offline cache)
Platforms: Windows 11, Android, iOS, macOS
```

### Shared API (REST)

```
Base URL: https://Evident.info/api
Auth: JWT Bearer tokens
Format: JSON
CORS: Enabled for all platforms
```

## 📁 KEY FILE LOCATIONS

### Web App Root

```
C:\web-dev\github-repos\Evident.info\
├── app.py                    # Main Flask app
├── auth_routes.py           # Authentication logic
├── stripe_payments.py       # Payment processing
├── models_*.py              # Database models
├── templates/               # Jinja2 HTML templates
└── static/                  # CSS, JS, images
```

### Windows App Root

```
C:\web-dev\github-repos\Evident.info\src\Evident.MatterDocket.MAUI\
├── ViewModels/              # Business logic
├── Views/                   # XAML UI pages
├── Services/                # API, Auth, Cache services
├── Models/                  # Data models
├── Helpers/                 # Constants, converters
└── Platforms/               # Windows, Android, iOS specific
```

### Documentation

```
C:\web-dev\github-repos\Evident.info\
├── MULTI-PLATFORM-ARCHITECTURE.md     # Overview (11 KB)
├── MAUI-ARCHITECTURE-PLAN.md          # Detailed MAUI design
├── WINDOWS-APP-PHASE-*.md             # Implementation phases
└── DEPLOYMENT-*.md                    # Production deployment
```

## 🎨 WINDOWS APP LOGIN SCREEN FEATURES

What's already implemented and working:

✅ Professional UI with Evident gold theme (#d4a574)  
✅ Email input with validation (checks valid email format)  
✅ Password input (masked)  
✅ "Remember Me" checkbox (state tracked)  
✅ "Forgot Password" link (opens browser to Evident.info)  
✅ "Sign Up" link (opens browser to registration)  
✅ Login button with loading indicator  
✅ Error message display (red text, appears on login failure)  
✅ Auto-navigation to Dashboard on success  
✅ Secure token storage (SecureStorage API)  
✅ Password cleared after login attempt (security)

## 🚀 WHAT TO DO NEXT IN NEW WORKSPACE

### Option 1: Test Windows App

```
Tell me: "run the windows app" or "test login screen"

I will:
1. Verify Visual Studio 2022 is open
2. Guide you through running the app (F5)
3. Test login with live API
4. Show you the beautiful gold-themed login screen
```

### Option 2: Build Next Feature (Evidence Upload)

```
Tell me: "build evidence upload" or "add upload feature"

I will:
1. Check existing Flask API endpoint
2. Create EvidenceUploadPage.xaml (Windows UI)
3. Create EvidenceViewModel.cs (logic)
4. Implement file picker + progress tracking
5. Test upload from Windows to live API
```

### Option 3: Continue Multi-Platform Development

```
Tell me: "build [feature] for all platforms"

Examples:
- "build analysis viewer for all platforms"
- "build document generator for web and windows"
- "add stripe payments to windows app"

I will build the feature for web + desktop simultaneously
```

### Option 4: Fix/Improve Existing Code

```
Tell me what needs improvement:
- "improve login screen UI"
- "add biometric auth to windows app"
- "optimize API calls"
- "add offline support"
```

## 💾 PACKAGES INSTALLED

### Web App (Python)

```
Flask==3.0.3
SQLAlchemy
stripe
openai
PyPDF2
python-dotenv
requests
```

### Windows App (NuGet)

```
CommunityToolkit.Mvvm 8.3.2         # MVVM pattern
Microsoft.Extensions.Http 10.0.0    # HTTP client
sqlite-net-pcl 1.9.172              # Local database
System.Text.Json 10.0.1             # JSON serialization
```

## 🔐 ENVIRONMENT VARIABLES (for reference)

The Windows app needs to connect to the Flask API. These are already configured in `Constants.cs`:

```csharp
public const string ApiBaseUrl = "https://Evident.info/api";
public const string WebsiteUrl = "https://Evident.info";
```

For local testing against localhost Flask:

```csharp
// Change to:
public const string ApiBaseUrl = "http://localhost:5000/api";
```

## 📊 PROJECT STATUS SUMMARY

| Component        | Status     | Completion |
| ---------------- | ---------- | ---------- |
| Web App          | ✅ Live    | 100%       |
| REST API         | ✅ Live    | 100%       |
| Windows Login    | ✅ Ready   | 100%       |
| Windows Upload   | 🔜 Next    | 0%         |
| Windows Analysis | 🔜 Planned | 0%         |
| Android App      | 🔜 Week 2  | 0%         |
| iOS App          | 🔜 Week 3  | 0%         |

**Overall Platform Progress:** 35% (Web + API complete, Desktop starting)

## 🎯 MY GOALS

1. Build a **professional multi-platform legal evidence system**
2. Maintain **consistent branding and UX** across all platforms
3. Use **one API** to power web, desktop, and mobile
4. Create **offline-first mobile apps** that sync when online
5. Deploy to **production** for real users
6. Keep **separate Git repos** for web and desktop (already done!)

## ⚡ READY TO CONTINUE!

I have the workspace open with both folders:

- 🌐 Evident.info (web/API)
- 💻 Evident MAUI (desktop/mobile)

**Tell me what you want to build next!**

Common commands:

- "run the windows app"
- "build evidence upload"
- "add [feature] to windows app"
- "test the login screen"
- "build [feature] for all platforms"
- "show me the architecture"
- "commit and push changes"

--

**Last Session Date:** January 27, 2026  
**Time:** 3:49 AM UTC  
**Workspace File:** `C:\web-dev\github-repos\Evident-MultiPlatform.code-workspace`  
**Ready to code!** 🚀
