# Evident Matter Docket (DTMB) - Phase B: MAUI Native Client Development

**Date:** January 27, 2026  
**Status:** Starting Phase B - .NET MAUI Windows 11 Native Application

--

## 🎯 Phase B Overview

**Goal:** Build native Windows 11 desktop application using .NET MAUI  
**Duration:** 4-6 weeks  
**Current Status:** Environment setup in progress

--

## 📋 Architecture Design

### Technology Stack

**Frontend (MAUI):**

- .NET 8.0 SDK
- .NET MAUI (Multi-platform App UI)
- WinUI 3 (Windows 11 native UI)
- XAML for UI markup
- C# for business logic

**Backend (Unchanged):**

- Flask REST API (Python)
- PostgreSQL database
- Stripe payments
- OpenAI AI services

**Communication:**

- HTTP/HTTPS REST API
- JSON data interchange
- WebSocket for real-time updates (future)

### Application Architecture

```
┌─────────────────────────────────────────────────────┐
│           MAUI Windows 11 Client (C#)                │
│  ┌────────────────────────────────────────────┐     │
│  │  Presentation Layer (XAML + WinUI 3)       │     │
│  │  - Login/Auth screens                      │     │
│  │  - Dashboard                               │     │
│  │  - Evidence upload                         │     │
│  │  - AI analysis viewer                      │     │
│  │  - Document generation                     │     │
│  └────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────┐     │
│  │  Business Logic Layer (C# Services)        │     │
│  │  - API client (HttpClient)                 │     │
│  │  - Local caching (SQLite)                  │     │
│  │  - State management                        │     │
│  │  - Offline queue                           │     │
│  └────────────────────────────────────────────┘     │
└──────────────────┬──────────────────────────────────┘
                   │ HTTPS REST API
┌──────────────────▼──────────────────────────────────┐
│              Flask Backend (Python)                  │
│  - /api/auth/login                                   │
│  - /api/evidence/upload                              │
│  - /api/analysis/process                             │
│  - /api/documents/generate                           │
│  - /api/payments/checkout                            │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│         Data & Services Layer                        │
│  - PostgreSQL (cases, users, evidence)               │
│  - Stripe (payments)                                 │
│  - OpenAI (AI analysis)                              │
│  - AWS S3 (file storage)                             │
└─────────────────────────────────────────────────────┘
```

--

## 📁 Project Structure

```
Evident.MatterDocket.MAUI/
├── Evident.MatterDocket.csproj          # Main project file
├── MauiProgram.cs                       # App initialization
├── App.xaml / App.xaml.cs               # Application entry
│
├── Views/                               # UI Screens (XAML)
│   ├── LoginPage.xaml
│   ├── DashboardPage.xaml
│   ├── EvidenceUploadPage.xaml
│   ├── AnalysisPage.xaml
│   ├── DocumentsPage.xaml
│   └── SettingsPage.xaml
│
├── ViewModels/                          # MVVM ViewModels
│   ├── LoginViewModel.cs
│   ├── DashboardViewModel.cs
│   ├── EvidenceViewModel.cs
│   ├── AnalysisViewModel.cs
│   └── DocumentsViewModel.cs
│
├── Services/                            # Business logic
│   ├── ApiService.cs                    # REST API client
│   ├── AuthService.cs                   # Authentication
│   ├── CacheService.cs                  # Local caching
│   ├── FileService.cs                   # File operations
│   └── SyncService.cs                   # Offline sync
│
├── Models/                              # Data models
│   ├── User.cs
│   ├── Case.cs
│   ├── Evidence.cs
│   ├── Analysis.cs
│   └── Document.cs
│
├── Resources/                           # Assets
│   ├── Images/
│   ├── Fonts/
│   ├── Styles/
│   └── AppIcon/
│
└── Platforms/                           # Platform-specific
    ├── Windows/
    │   ├── Package.appxmanifest
    │   └── app.manifest
    ├── Android/ (future)
    ├── iOS/ (future)
    └── MacCatalyst/ (future)
```

--

## 🛠️ Development Phases

### Week 1: Environment Setup + Authentication

- [ ] Install Visual Studio 2022
- [ ] Install .NET 8 SDK
- [ ] Configure MAUI workload
- [ ] Create new MAUI project
- [ ] Implement login screen (XAML)
- [ ] Build API client service
- [ ] Test authentication flow

### Week 2: Core UI Implementation

- [ ] Design dashboard layout
- [ ] Implement navigation
- [ ] Create evidence upload UI
- [ ] Add file picker integration
- [ ] Build analysis viewer
- [ ] Implement data binding (MVVM)

### Week 3: Backend Integration

- [ ] Connect all API endpoints
- [ ] Implement local caching (SQLite)
- [ ] Add offline queue
- [ ] Build sync service
- [ ] Test end-to-end flows

### Week 4: Windows 11 Native Features

- [ ] Fluent Design System
- [ ] Acrylic effects
- [ ] Windows notifications
- [ ] System tray integration
- [ ] Jump lists
- [ ] File type associations

### Week 5: Payment & AI Features

- [ ] Stripe payment integration
- [ ] AI analysis display
- [ ] Document generation
- [ ] Real-time progress updates
- [ ] Download manager

### Week 6: Testing & Polish

- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance optimization
- [ ] UI/UX refinement
- [ ] Documentation

--

## 🔧 Key Features to Implement

### Authentication

- [x] Login with email/password
- [x] Token-based auth (JWT)
- [ ] Windows Hello integration (optional)
- [ ] Session persistence
- [ ] Auto-logout on inactivity

### Evidence Management

- [ ] File upload (PDF, images, video, audio)
- [ ] Drag-and-drop support
- [ ] Progress indicators
- [ ] Batch upload
- [ ] Local file caching
- [ ] Offline queue for uploads

### AI Analysis

- [ ] Display analysis results
- [ ] Real-time progress updates
- [ ] Export analysis reports
- [ ] View transcripts
- [ ] Highlight key findings

### Document Generation

- [ ] Select document templates
- [ ] Fill evidence-based fields
- [ ] Preview generated docs
- [ ] Download as PDF/DOCX
- [ ] Save to local files

### Payments

- [ ] View subscription status
- [ ] Upgrade/downgrade tiers
- [ ] Payment method management
- [ ] Invoice history

### Windows 11 Integration

- [ ] Native window chrome
- [ ] Dark/Light theme sync
- [ ] System notifications
- [ ] Taskbar badge notifications
- [ ] Context menu integration

--

## 📦 Dependencies

### NuGet Packages Required

```xml
<ItemGroup>
  <!-- HTTP Client ->
  <PackageReference Include="Microsoft.Extensions.Http" Version="8.0.0" />

  <!-- JSON Serialization ->
  <PackageReference Include="System.Text.Json" Version="8.0.0" />

  <!-- Local Database ->
  <PackageReference Include="sqlite-net-pcl" Version="1.9.172" />

  <!-- MVVM Toolkit ->
  <PackageReference Include="CommunityToolkit.Mvvm" Version="8.2.2" />

  <!-- WinUI 3 ->
  <PackageReference Include="Microsoft.WindowsAppSDK" Version="1.5.240311000" />

  <!-- Stripe (if client-side needed) ->
  <PackageReference Include="Stripe.net" Version="44.0.0" />
</ItemGroup>
```

--

## 🔌 API Client Implementation

### ApiService.cs (Example)

```csharp
public class ApiService
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl = "https://Evident.info/api";

    public ApiService()
    {
        _httpClient = new HttpClient();
        _httpClient.DefaultRequestHeaders.Add("Accept", "application/json");
    }

    // Authentication
    public async Task<AuthResponse> LoginAsync(string email, string password)
    {
        var payload = new { email, password };
        var response = await _httpClient.PostAsJsonAsync($"{_baseUrl}/auth/login", payload);
        return await response.Content.ReadFromJsonAsync<AuthResponse>();
    }

    // Evidence Upload
    public async Task<UploadResponse> UploadEvidenceAsync(string filePath, string caseId)
    {
        using var form = new MultipartFormDataContent();
        var fileBytes = await File.ReadAllBytesAsync(filePath);
        form.Add(new ByteArrayContent(fileBytes), "file", Path.GetFileName(filePath));
        form.Add(new StringContent(caseId), "case_id");

        var response = await _httpClient.PostAsync($"{_baseUrl}/evidence/upload", form);
        return await response.Content.ReadFromJsonAsync<UploadResponse>();
    }

    // Get Analysis
    public async Task<AnalysisResult> GetAnalysisAsync(string analysisId)
    {
        var response = await _httpClient.GetAsync($"{_baseUrl}/analysis/{analysisId}");
        return await response.Content.ReadFromJsonAsync<AnalysisResult>();
    }
}
```

--

## 🎨 UI Design Guidelines

### Windows 11 Fluent Design

- Use Acrylic material for backgrounds
- Rounded corners (CornerRadius="8")
- Fluent shadows and elevation
- Smooth animations (200-300ms)
- Responsive layouts

### Color Scheme

- **Primary:** #d4a574 (Evident gold)
- **Background:** #0f0f0f (dark)
- **Surface:** #1a1a1a
- **Text:** #ffffff (primary), #b0b0b0 (secondary)
- **Accent:** #d4a574

### Typography

- **Headers:** Segoe UI Variable Display
- **Body:** Segoe UI Variable Text
- **Monospace:** Cascadia Mono (for code/logs)

--

## 🧪 Testing Strategy

### Unit Tests

- ViewModel logic
- API client methods
- Data model validation
- Service layer functions

### Integration Tests

- Login flow
- Evidence upload
- Analysis retrieval
- Payment processing

### UI Tests (WinAppDriver)

- Navigation flows
- Form validation
- File upload
- Data display

--

## 📊 Success Criteria

### Performance

- [ ] App launches in <1 second
- [ ] API calls complete in <500ms (p95)
- [ ] File upload shows progress
- [ ] Smooth 60fps animations
- [ ] Memory usage <200MB idle

### Functionality

- [ ] All Flask API endpoints accessible
- [ ] Offline mode for viewing cached data
- [ ] Background sync works
- [ ] Payments process correctly
- [ ] AI analysis displays properly

### User Experience

- [ ] Intuitive navigation
- [ ] Clear error messages
- [ ] Loading states
- [ ] Keyboard shortcuts
- [ ] Accessible (WCAG 2.1 AA)

--

## 🚀 Next Actions

### Immediate (Phase C)

1. Install Visual Studio 2022 Community
2. Install .NET 8 SDK
3. Enable MAUI workload
4. Create new MAUI project
5. Configure development environment

### After Setup (Week 1)

6. Implement login screen
7. Build API service
8. Test authentication
9. Design dashboard layout
10. Create navigation structure

--

_Status: Phase B Planning Complete - Ready for Phase C_  
_Last Updated: January 27, 2026_
