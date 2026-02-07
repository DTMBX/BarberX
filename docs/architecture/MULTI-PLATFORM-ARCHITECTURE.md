# Evident Matter Docket (DTMB) - Multi-Platform Architecture

**Date:** January 27, 2026  
**Status:** Multi-Platform Development Active

--

## 🌐 Platform Ecosystem Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Evident MATTER DOCKET                         │
│              Professional Legal Evidence Platform                │
└─────────────────────────────────────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
         ┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
         │  WEB APP    │ │ REST API │ │ WINDOWS 11 │
         │  (Flask)    │ │ (Flask)  │ │   (MAUI)   │
         │   LIVE ✅   │ │  LIVE ✅ │ │  READY ✅  │
         └─────────────┘ └──────────┘ └────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
         ┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
         │   ANDROID   │ │   iOS    │ │   macOS    │
         │   (MAUI)    │ │  (MAUI)  │ │  (MAUI)    │
         │  PLANNED 🔜 │ │ PLANNED 🔜│ │ PLANNED 🔜│
         └─────────────┘ └──────────┘ └────────────┘
```

--

## 📁 Repository Structure (Multi-Platform)

```
Evident.info/
│
├── 🌐 WEB APPLICATION (Root)
│   ├── app.py                          # Flask main application
│   ├── templates/                      # Jinja2 templates
│   ├── static/                         # CSS, JS, images
│   ├── auth_routes.py                  # Authentication
│   ├── stripe_payments.py              # Payment processing
│   ├── models_*.py                     # Database models
│   └── requirements.txt                # Python dependencies
│
├── 📱 WINDOWS/MOBILE APP (src/)
│   └── Evident.MatterDocket.MAUI/
│       ├── ViewModels/                 # MVVM ViewModels
│       │   ├── BaseViewModel.cs
│       │   └── LoginViewModel.cs
│       ├── Views/                      # XAML UI Pages
│       │   ├── LoginPage.xaml
│       │   └── DashboardPage.xaml
│       ├── Services/                   # Business logic
│       │   ├── ApiService.cs          # HTTP client
│       │   └── AuthService.cs         # Authentication
│       ├── Models/                     # Data models
│       │   └── ApiModels.cs
│       ├── Helpers/                    # Utilities
│       │   ├── Constants.cs
│       │   └── Converters.cs
│       └── Platforms/                  # Platform-specific code
│           ├── Windows/
│           ├── Android/
│           ├── iOS/
│           └── MacCatalyst/
│
├── 📚 DOCUMENTATION
│   ├── MAUI-ARCHITECTURE-PLAN.md       # Windows/Mobile architecture
│   ├── WINDOWS-APP-PHASE-A-COMPLETE.md # PWA packaging
│   ├── WINDOWS-APP-PHASE-B-PLAN.md     # MAUI design
│   ├── WINDOWS-APP-PHASE-C-SETUP.md    # Dev environment
│   ├── WINDOWS-APP-PHASE-D-IMPLEMENTATION.md # Timeline
│   └── ... (50+ other docs)
│
└── 🔧 CONFIGURATION
    ├── render.yaml                     # Render.com deployment
    ├── netlify.toml                    # Netlify config
    ├── Procfile                        # Process definitions
    └── requirements.txt                # Python deps
```

--

## 🔗 API Contract (Shared Across Platforms)

### Authentication Endpoints

```
POST   /api/auth/login              # Used by: Web, Windows, Mobile
POST   /api/auth/logout             # Used by: Web, Windows, Mobile
POST   /api/auth/register           # Used by: Web, Windows, Mobile
GET    /api/auth/verify             # Used by: Windows, Mobile
POST   /api/auth/refresh            # Used by: Windows, Mobile
```

### Evidence Management

```
GET    /api/evidence/list           # All platforms
POST   /api/evidence/upload         # All platforms
POST   /api/evidence/batch-upload   # Desktop/Web only
GET    /api/evidence/{id}           # All platforms
DELETE /api/evidence/{id}           # All platforms
```

### Analysis

```
POST   /api/analysis/start          # All platforms
GET    /api/analysis/{id}/status    # All platforms
GET    /api/analysis/{id}/results   # All platforms
GET    /api/analysis/{id}/transcript # All platforms
```

### Documents

```
GET    /api/documents/templates     # All platforms
POST   /api/documents/generate      # All platforms
GET    /api/documents/{id}/download # All platforms
```

### Payments (Stripe)

```
POST   /payments/create-checkout-session  # All platforms
GET    /api/user/subscription             # All platforms
GET    /api/user/invoices                 # All platforms
```

--

## 🎨 Shared Branding & Design System

### Colors (Consistent Across All Platforms)

```
Primary Gold:     #d4a574  (Evident brand color)
Background Dark:  #0f0f0f  (Main background)
Surface Dark:     #1a1a1a  (Cards, inputs)
Text Primary:     #ffffff  (Headings)
Text Secondary:   #b0b0b0  (Body text, labels)
Error Red:        #ff4444  (Errors, warnings)
Success Green:    #00ff00  (Success states)
```

### Typography

```
Headings:   Bold, 24-32px
Subheads:   Semibold, 18-20px
Body:       Regular, 14-16px
Captions:   Regular, 12-13px

Font Family:
- Web: System fonts (-apple-system, BlinkMacSystemFont, Segoe UI)
- Windows/MAUI: OpenSans, Segoe UI
- Mobile: Platform defaults (San Francisco, Roboto)
```

### Component Patterns

```
Buttons:
- Height: 48-50px
- Border Radius: 8px
- Primary: Gold background, dark text
- Secondary: Dark background, gold border

Input Fields:
- Height: 48px
- Border: 1px solid gold
- Border Radius: 8px
- Dark background

Cards:
- Border: 1px solid gold
- Border Radius: 12px
- Dark background
- Gold accent on hover
```

--

## 🔄 Data Synchronization Strategy

### Offline-First Architecture (MAUI Apps)

```
┌──────────────────────────────────────────────────┐
│  Local SQLite Database (Windows/Mobile)          │
│  - Cached user data                              │
│  - Offline evidence queue                        │
│  - Pending uploads                               │
└──────────────┬───────────────────────────────────┘
               │ Sync on network available
               ▼
┌──────────────────────────────────────────────────┐
│  Flask REST API (Evident.info)                   │
│  - PostgreSQL (source of truth)                  │
│  - S3 file storage                               │
│  - Stripe payments                               │
└──────────────┬───────────────────────────────────┘
               │ Real-time updates
               ▼
┌──────────────────────────────────────────────────┐
│  Web Application (Flask templates)               │
│  - Server-side rendering                         │
│  - Direct database access                        │
└──────────────────────────────────────────────────┘
```

### Sync Queue Pattern (MAUI)

```csharp
// Upload evidence while offline
await SyncService.QueueEvidenceUpload(filePath);

// Automatically sync when online
if (NetworkConnectivity.Current.NetworkAccess == NetworkAccess.Internet)
{
    await SyncService.ProcessPendingUploads();
}
```

--

## 🚀 Development Workflow (Multi-Platform)

### Step 1: Design Feature

- Define API contract
- Design UI for all platforms
- Document data models

### Step 2: Backend First

- Implement Flask API endpoint
- Add database migrations
- Write API tests
- Deploy to Render

### Step 3: Web Implementation

- Create Flask templates
- Add JavaScript interactions
- Test on Evident.info

### Step 4: Windows/Mobile Implementation

- Create XAML views
- Implement ViewModels
- Wire up API calls
- Test on Windows/Android/iOS

### Step 5: Sync & Test

- Verify API compatibility
- Test offline scenarios
- Ensure branding consistency
- Cross-platform QA

--

## 📊 Feature Parity Matrix

| Feature                 | Web | API | Windows | Android | iOS |
| ----------------------- | --- | --- | ------- | ------- | --- |
| **Authentication**      | ✅  | ✅  | ✅      | 🔜      | 🔜  |
| **Evidence Upload**     | ✅  | ✅  | 🔜      | 🔜      | 🔜  |
| **Batch Upload**        | ✅  | ✅  | 🔜      | ❌      | ❌  |
| **AI Analysis**         | ✅  | ✅  | 🔜      | 🔜      | 🔜  |
| **Document Generation** | ✅  | ✅  | 🔜      | 🔜      | 🔜  |
| **Stripe Payments**     | ✅  | ✅  | 🔜      | 🔜      | 🔜  |
| **Offline Mode**        | ❌  | N/A | 🔜      | 🔜      | 🔜  |
| **Push Notifications**  | ❌  | ✅  | 🔜      | 🔜      | 🔜  |
| **Biometric Auth**      | ❌  | N/A | 🔜      | 🔜      | 🔜  |

Legend: ✅ Complete | 🔜 Planned | ❌ Not Applicable

--

## 🎯 Next Steps (Multi-Platform Development)

### Immediate (Tonight)

1. ✅ Add MAUI folder to workspace
2. 🔜 Run Windows app login screen
3. 🔜 Test login with live API
4. 🔜 Build evidence upload for both platforms

### Week 1 Goals

- [ ] Complete authentication across all platforms
- [ ] Implement evidence upload (Web + Windows)
- [ ] Sync API models between platforms
- [ ] Create shared design component library

### Month 1 Goals

- [ ] Feature parity: Web + Windows
- [ ] Android app MVP
- [ ] iOS app MVP
- [ ] Cross-platform testing complete

--

## 💡 Cross-Platform Development Best Practices

### 1. API-First Development

Always build the API endpoint first, then consume it from all platforms.

### 2. Shared Models

Keep data models synchronized across platforms. Consider code generation from
OpenAPI spec.

### 3. Consistent Branding

Use the same color codes, typography, and spacing across all platforms.

### 4. Offline-First Mobile

Design mobile apps to work offline, sync when online.

### 5. Platform-Specific Features

Embrace platform-specific capabilities (Windows file system, iOS camera, etc.)

### 6. Unified Testing

Test the same user flows across all platforms to ensure consistency.

--

## 📈 Platform Statistics

### Web Application

- **Status:** ✅ Live at Evident.info
- **Users:** Active production system
- **Features:** 100% complete
- **Tech Stack:** Flask, PostgreSQL, Stripe, OpenAI

### REST API

- **Status:** ✅ Live at Evident.info/api
- **Endpoints:** 20+ endpoints
- **Auth:** JWT Bearer tokens
- **Tech Stack:** Flask, PostgreSQL

### Windows 11 App

- **Status:** ✅ Login screen ready
- **Framework:** .NET MAUI 10.0
- **Features:** 10% complete (auth only)
- **Next:** Evidence upload, analysis viewer

### Android/iOS Apps

- **Status:** 🔜 Planned (same MAUI codebase)
- **Timeline:** Week 2-3
- **Advantage:** 80% code sharing with Windows app

--

_Multi-Platform Development Strategy Complete_  
_Ready for Unified Development Workflow_  
_Last Updated: January 27, 2026_
