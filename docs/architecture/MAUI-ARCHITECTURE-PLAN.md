# Evident Matter Docket (DTMB) - MAUI Architecture Plan

**Date:** January 27, 2026  
**Project:** Windows 11 Native Desktop Application  
**Technology:** .NET MAUI + WinUI 3 + Flask Backend

--

## 🏗️ Architecture Overview

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────┐
│         PRESENTATION LAYER (MAUI/WinUI 3)        │
│  ┌───────────────────────────────────────────┐  │
│  │  Views (XAML)                              │  │
│  │  - LoginPage.xaml                          │  │
│  │  - DashboardPage.xaml                      │  │
│  │  - EvidenceUploadPage.xaml                 │  │
│  │  - AnalysisPage.xaml                       │  │
│  │  - DocumentsPage.xaml                      │  │
│  │  - SettingsPage.xaml                       │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │  ViewModels (MVVM Pattern)                 │  │
│  │  - LoginViewModel.cs                       │  │
│  │  - DashboardViewModel.cs                   │  │
│  │  - EvidenceViewModel.cs                    │  │
│  │  - AnalysisViewModel.cs                    │  │
│  │  - DocumentsViewModel.cs                   │  │
│  └───────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────┘
                     │ Data Binding & Commands
┌────────────────────▼────────────────────────────┐
│           BUSINESS LOGIC LAYER (Services)        │
│  ┌───────────────────────────────────────────┐  │
│  │  ApiService.cs                             │  │
│  │  - Login/Logout                            │  │
│  │  - Evidence Upload                         │  │
│  │  - Analysis Requests                       │  │
│  │  - Document Generation                     │  │
│  │  - Payment Processing                      │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │  CacheService.cs                           │  │
│  │  - Local SQLite database                   │  │
│  │  - Offline data storage                    │  │
│  │  - Sync queue management                   │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │  AuthService.cs                            │  │
│  │  - Token management                        │  │
│  │  - Secure storage                          │  │
│  │  - Session handling                        │  │
│  └───────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────┘
                     │ HTTPS REST API
┌────────────────────▼────────────────────────────┐
│           DATA LAYER (Flask Backend)             │
│  - PostgreSQL Database                           │
│  - Stripe Payments                               │
│  - OpenAI Services                               │
│  - File Storage (S3)                             │
└─────────────────────────────────────────────────┘
```

--

## 📁 Project Structure (Detailed)

```
Evident.MatterDocket.MAUI/
│
├── 📄 Evident.MatterDocket.MAUI.csproj    # Project file
├── 📄 MauiProgram.cs                      # App entry point
├── 📄 App.xaml / App.xaml.cs              # Application class
├── 📄 AppShell.xaml / AppShell.xaml.cs    # Navigation shell
│
├── 📁 Views/                               # XAML UI Pages
│   ├── 📄 LoginPage.xaml / .cs
│   ├── 📄 DashboardPage.xaml / .cs
│   ├── 📄 EvidenceUploadPage.xaml / .cs
│   ├── 📄 AnalysisPage.xaml / .cs
│   ├── 📄 AnalysisDetailPage.xaml / .cs
│   ├── 📄 DocumentsPage.xaml / .cs
│   ├── 📄 DocumentGeneratePage.xaml / .cs
│   ├── 📄 SettingsPage.xaml / .cs
│   └── 📄 PaymentPage.xaml / .cs
│
├── 📁 ViewModels/                          # MVVM ViewModels
│   ├── 📄 BaseViewModel.cs                 # Base class for all VMs
│   ├── 📄 LoginViewModel.cs
│   ├── 📄 DashboardViewModel.cs
│   ├── 📄 EvidenceViewModel.cs
│   ├── 📄 AnalysisViewModel.cs
│   ├── 📄 DocumentsViewModel.cs
│   ├── 📄 SettingsViewModel.cs
│   └── 📄 PaymentViewModel.cs
│
├── 📁 Services/                            # Business Logic
│   ├── 📄 ApiService.cs                    # HTTP client for Flask API
│   ├── 📄 AuthService.cs                   # Authentication
│   ├── 📄 CacheService.cs                  # Local database
│   ├── 📄 SyncService.cs                   # Offline sync
│   ├── 📄 FileService.cs                   # File operations
│   ├── 📄 NavigationService.cs             # Page navigation
│   └── 📄 DialogService.cs                 # Alerts/dialogs
│
├── 📁 Models/                              # Data Models
│   ├── 📄 User.cs
│   ├── 📄 Case.cs
│   ├── 📄 Evidence.cs
│   ├── 📄 EvidenceFile.cs
│   ├── 📄 Analysis.cs
│   ├── 📄 AnalysisResult.cs
│   ├── 📄 Document.cs
│   ├── 📄 DocumentTemplate.cs
│   ├── 📄 Subscription.cs
│   └── 📄 ApiResponse.cs
│
├── 📁 Helpers/                             # Utility Classes
│   ├── 📄 Constants.cs                     # App constants
│   ├── 📄 Converters.cs                    # XAML value converters
│   ├── 📄 Validators.cs                    # Input validation
│   └── 📄 Extensions.cs                    # Extension methods
│
├── 📁 Resources/                           # Assets
│   ├── 📁 Images/                          # Icons, logos
│   ├── 📁 Fonts/                           # Custom fonts
│   ├── 📁 Styles/                          # XAML styles
│   │   ├── 📄 Colors.xaml
│   │   ├── 📄 Styles.xaml
│   │   └── 📄 Templates.xaml
│   └── 📁 Raw/                             # Raw assets
│
├── 📁 Platforms/                           # Platform-specific code
│   ├── 📁 Windows/
│   │   ├── 📄 Package.appxmanifest
│   │   ├── 📄 app.manifest
│   │   └── 📄 app.ico
│   ├── 📁 Android/                         # Future
│   ├── 📁 iOS/                             # Future
│   └── 📁 MacCatalyst/                     # Future
│
└── 📁 Data/                                # Local database
    ├── 📄 LocalDatabase.cs                 # SQLite context
    └── 📄 CachedModels.cs                  # Offline models
```

--

## 🔌 API Integration Map

### Flask Backend Endpoints Used

```csharp
// Base URL
private const string API_BASE = "https://Evident.info/api";

// Authentication
POST   /api/auth/login              → LoginAsync(email, password)
POST   /api/auth/logout             → LogoutAsync()
GET    /api/auth/verify             → VerifyTokenAsync()
POST   /api/auth/refresh            → RefreshTokenAsync()

// User Management
GET    /api/user/profile            → GetProfileAsync()
PUT    /api/user/profile            → UpdateProfileAsync(user)
GET    /api/user/subscription       → GetSubscriptionAsync()
GET    /api/user/usage               → GetUsageStatsAsync()

// Evidence Management
GET    /api/evidence/list           → GetEvidenceListAsync()
POST   /api/evidence/upload         → UploadEvidenceAsync(file)
POST   /api/evidence/batch-upload   → BatchUploadAsync(files)
GET    /api/evidence/{id}           → GetEvidenceAsync(id)
DELETE /api/evidence/{id}           → DeleteEvidenceAsync(id)

// Analysis
POST   /api/analysis/start          → StartAnalysisAsync(evidenceId)
GET    /api/analysis/{id}/status    → GetAnalysisStatusAsync(id)
GET    /api/analysis/{id}/results   → GetAnalysisResultsAsync(id)
GET    /api/analysis/{id}/transcript → GetTranscriptAsync(id)

// Documents
GET    /api/documents/templates     → GetTemplatesAsync()
GET    /api/documents/templates/{id} → GetTemplateAsync(id)
POST   /api/documents/generate      → GenerateDocumentAsync(data)
GET    /api/documents/{id}/download → DownloadDocumentAsync(id)

// Payments
POST   /payments/create-checkout-session → CreateCheckoutAsync(tier)
GET    /api/user/invoices           → GetInvoicesAsync()
```

--

## 🗄️ Local Database Schema (SQLite)

```sql
- Cached user data
CREATE TABLE Users (
    Id INTEGER PRIMARY KEY,
    Email TEXT NOT NULL,
    Name TEXT,
    Tier TEXT,
    SubscriptionExpiry INTEGER,
    LastSync INTEGER
);

- Cached cases
CREATE TABLE Cases (
    Id INTEGER PRIMARY KEY,
    CaseNumber TEXT,
    Title TEXT,
    Status TEXT,
    CreatedAt INTEGER,
    UpdatedAt INTEGER,
    IsSynced INTEGER DEFAULT 0
);

- Cached evidence files
CREATE TABLE Evidence (
    Id INTEGER PRIMARY KEY,
    CaseId INTEGER,
    FileName TEXT,
    FilePath TEXT,
    FileType TEXT,
    FileSize INTEGER,
    UploadStatus TEXT, - 'pending', 'uploading', 'completed', 'failed'
    CreatedAt INTEGER,
    FOREIGN KEY (CaseId) REFERENCES Cases(Id)
);

- Analysis results cache
CREATE TABLE AnalysisResults (
    Id INTEGER PRIMARY KEY,
    EvidenceId INTEGER,
    Status TEXT,
    Progress INTEGER,
    ResultJson TEXT, - JSON blob
    CompletedAt INTEGER,
    FOREIGN KEY (EvidenceId) REFERENCES Evidence(Id)
);

- Sync queue
CREATE TABLE SyncQueue (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    EntityType TEXT, - 'evidence', 'analysis', 'document'
    EntityId INTEGER,
    Action TEXT, - 'upload', 'delete', 'update'
    Payload TEXT, - JSON blob
    Retries INTEGER DEFAULT 0,
    CreatedAt INTEGER
);
```

--

## 🎨 MVVM Pattern Implementation

### Example: Login Flow

```csharp
// 1. View (LoginPage.xaml)
<ContentPage>
    <StackLayout>
        <Entry Text="{Binding Email}" Placeholder="Email" />
        <Entry Text="{Binding Password}" IsPassword="True" />
        <Button Text="Login" Command="{Binding LoginCommand}" />
        <ActivityIndicator IsRunning="{Binding IsBusy}" />
    </StackLayout>
</ContentPage>

// 2. ViewModel (LoginViewModel.cs)
public class LoginViewModel : BaseViewModel
{
    private readonly IAuthService _authService;
    private readonly INavigationService _navigationService;

    public string Email { get; set; }
    public string Password { get; set; }

    public ICommand LoginCommand { get; }

    public LoginViewModel(IAuthService authService, INavigationService nav)
    {
        _authService = authService;
        _navigationService = nav;
        LoginCommand = new AsyncRelayCommand(LoginAsync);
    }

    private async Task LoginAsync()
    {
        IsBusy = true;
        try
        {
            var result = await _authService.LoginAsync(Email, Password);
            if (result.Success)
            {
                await _navigationService.NavigateToAsync("Dashboard");
            }
            else
            {
                await App.Current.MainPage.DisplayAlert("Error", result.Message, "OK");
            }
        }
        finally
        {
            IsBusy = false;
        }
    }
}

// 3. Service (AuthService.cs)
public class AuthService : IAuthService
{
    private readonly IApiService _apiService;

    public async Task<LoginResult> LoginAsync(string email, string password)
    {
        var response = await _apiService.PostAsync<LoginResponse>(
            "/api/auth/login",
            new { email, password }
        );

        if (response.Success)
        {
            // Store token securely
            await SecureStorage.SetAsync("auth_token", response.Token);
            return new LoginResult { Success = true };
        }

        return new LoginResult { Success = false, Message = response.Error };
    }
}
```

--

## 🔐 Security Implementation

### Token Storage

```csharp
// Secure token storage using MAUI SecureStorage
await SecureStorage.SetAsync("auth_token", token);
var token = await SecureStorage.GetAsync("auth_token");
```

### API Request Headers

```csharp
private async Task<HttpRequestMessage> CreateAuthenticatedRequest(string endpoint)
{
    var token = await SecureStorage.GetAsync("auth_token");
    var request = new HttpRequestMessage(HttpMethod.Get, endpoint);
    request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
    return request;
}
```

### Certificate Pinning (Production)

```csharp
public class SecureHttpClientHandler : HttpClientHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken ct)
    {
        // Validate certificate for Evident.info
        // Prevent man-in-the-middle attacks
        return await base.SendAsync(request, ct);
    }
}
```

--

## 📱 Offline-First Strategy

### Sync Queue Pattern

```csharp
public class SyncService
{
    // 1. User uploads evidence (offline)
    public async Task QueueEvidenceUpload(string filePath)
    {
        var queueItem = new SyncQueueItem
        {
            EntityType = "evidence",
            Action = "upload",
            Payload = JsonSerializer.Serialize(new { filePath }),
            CreatedAt = DateTime.UtcNow
        };

        await _database.AddToSyncQueue(queueItem);

        // Try immediate sync if online
        if (Connectivity.Current.NetworkAccess == NetworkAccess.Internet)
        {
            await ProcessSyncQueue();
        }
    }

    // 2. Background sync when online
    public async Task ProcessSyncQueue()
    {
        var pendingItems = await _database.GetPendingSyncItems();

        foreach (var item in pendingItems)
        {
            try
            {
                switch (item.EntityType)
                {
                    case "evidence":
                        await SyncEvidence(item);
                        break;
                    // ... other types
                }

                await _database.RemoveFromSyncQueue(item.Id);
            }
            catch (Exception ex)
            {
                item.Retries++;
                await _database.UpdateSyncQueueItem(item);
            }
        }
    }
}
```

--

## 🎯 Navigation Flow

```
LoginPage
    │
    ├─► (Success) → DashboardPage
    │                   │
    │                   ├─► EvidenceUploadPage
    │                   │       │
    │                   │       └─► AnalysisPage
    │                   │               │
    │                   │               └─► AnalysisDetailPage
    │                   │
    │                   ├─► DocumentsPage
    │                   │       │
    │                   │       └─► DocumentGeneratePage
    │                   │
    │                   ├─► SettingsPage
    │                   │       │
    │                   │       ├─► ProfilePage
    │                   │       └─► SubscriptionPage
    │                   │               │
    │                   │               └─► PaymentPage
    │                   │
    │                   └─► (Logout) → LoginPage
    │
    └─► (Failed) → Error Dialog → Retry
```

--

## 🎨 Windows 11 Design System

### Colors (From Evident Branding)

```xml
<Color x:Key="PrimaryGold">#d4a574</Color>
<Color x:Key="BackgroundDark">#0f0f0f</Color>
<Color x:Key="SurfaceDark">#1a1a1a</Color>
<Color x:Key="TextPrimary">#ffffff</Color>
<Color x:Key="TextSecondary">#b0b0b0</Color>
```

### Fluent Design Principles

- **Acrylic backgrounds** for depth
- **Reveal highlights** on hover
- **Connected animations** between pages
- **Shadow elevation** for hierarchy

--

## 📊 Performance Targets

| Metric                | Target           | How to Achieve                        |
| --------------------- | ---------------- | ------------------------------------- |
| **App Launch**        | <1 second        | Lazy loading, minimize startup work   |
| **API Calls**         | <500ms p95       | Caching, connection pooling           |
| **File Upload**       | Progress visible | Chunked upload, background service    |
| **UI Responsiveness** | 60fps            | Async operations, virtual scrolling   |
| **Memory Usage**      | <200MB idle      | Dispose resources, image optimization |

--

## 🚀 Development Phases (Aligned with Phase D)

### Week 1: Authentication & Foundation

- Create project structure
- Implement login screen
- Build ApiService base
- Set up navigation

### Week 2: Evidence Upload

- File picker integration
- Upload progress UI
- Local caching
- Offline queue

### Week 3: Analysis Integration

- Analysis status display
- Real-time updates
- Transcript viewer
- Report export

### Week 4: Document Generation

- Template selector
- Parameter forms
- Preview & download

### Week 5: Payments

- Subscription display
- Upgrade flow
- Invoice management

### Week 6: Polish & Testing

- Windows 11 features
- Accessibility
- Performance optimization

--

_Architecture Plan Complete_  
_Ready for Implementation_  
_Last Updated: January 27, 2026_
