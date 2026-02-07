# Evident Multi-Platform Framework Architecture

## Overview

Evident is built as a comprehensive multi-platform application supporting:

- **Windows** - .NET MAUI native app
- **Android** - .NET MAUI native app
- **iOS** - .NET MAUI native app
- **Web** - Flask web application
- **Mobile Web** - Responsive Flask web app
- **API Gateway** - ASP.NET Core Web API (optional)

---

## Architecture Layers

### 1. **Shared Layer** (`Evident.Shared`)

Cross-platform data models and service interfaces used by all platforms.

**Components**:

- `Models/AnalysisRequest.cs` - Shared data models
- `Services/IApiClient.cs` - API client interface
- `Services/ApiClient.cs` - HTTP-based API client implementation

**Purpose**: Ensure consistent data structures and API contracts across all
platforms.

### 2. **Mobile Layer** (`Evident.Mobile`)

.NET MAUI application targeting Windows, Android, iOS, and macOS.

**Architecture**: MVVM (Model-View-ViewModel)

**Components**:

- `Services/AuthService.cs` - Authentication with secure token storage
- `ViewModels/BaseViewModel.cs` - Base class with INotifyPropertyChanged
- `ViewModels/LoginViewModel.cs` - Login screen logic
- `ViewModels/AnalysisListViewModel.cs` - Analysis list management
- `Views/` - XAML pages (to be created)
- `MauiProgram.cs` - Dependency injection configuration

**Key Features**:

- Secure credential storage using `SecureStorage`
- Offline-first architecture (future)
- Platform-specific optimizations
- Native UI controls

### 3. **Web API Layer** (`Evident.Web`)

ASP.NET Core Web API serving as an API gateway to Flask backend.

**Architecture**: RESTful API with controller-based routing

**Components**:

- `Controllers/AnalysisController.cs` - BWC analysis endpoints
- `Services/IAnalysisService.cs` - Service interface
- `Services/FlaskProxyAnalysisService.cs` - Proxy to Flask backend
- `Program.cs` - API configuration (to be updated)

**Purpose**:

- Provide .NET-native API for mobile apps
- Handle authentication/authorization
- Proxy requests to Flask AI backend
- Add caching, rate limiting, monitoring

### 4. **Flask Backend** (Existing `app.py`)

Python-based AI processing engine and web application.

**Responsibilities**:

- AI/ML processing (Whisper, OCR, legal analysis)
- Database operations
- Web UI rendering
- Background job processing

---

## Data Flow

### Mobile App → Flask Backend (Direct)

```
Mobile App (MAUI)
    ↓ HTTP/HTTPS
Flask Backend (app.py)
    ↓
Database / AI Services
```

### Mobile App → ASP.NET Gateway → Flask Backend

```
Mobile App (MAUI)
    ↓ HTTP/HTTPS
ASP.NET Core API Gateway
    ↓ HTTP (internal)
Flask Backend (app.py)
    ↓
Database / AI Services
```

### Web Browser → Flask Backend

```
Web Browser
    ↓ HTTP/HTTPS
Flask Backend (app.py)
    ↓ Render HTML
Templates (Jinja2)
```

---

## API Endpoints

### Authentication

- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout
- `GET /auth/profile` - Get user profile

### BWC Analysis

- `POST /api/upload` - Upload video for analysis
- `GET /api/analysis/{id}/status` - Get analysis status
- `GET /api/analysis/{id}` - Get analysis results
- `GET /api/analyses` - List user analyses
- `DELETE /api/analysis/{id}` - Delete analysis
- `GET /api/analysis/{id}/report/{format}` - Download report

### PDF Processing

- `POST /api/upload/pdf` - Upload PDF
- `GET /api/pdfs` - List user PDFs
- `POST /api/pdf/{id}/analyze` - Analyze PDF
- `DELETE /api/pdf/{id}` - Delete PDF

### Legal Analysis

- `POST /api/legal/scan-violations` - Scan for violations
- `POST /api/legal/check-compliance` - Check compliance
- `POST /api/legal/combined-analysis` - Combined analysis

### Transcription & OCR

- `POST /api/evidence/transcribe` - Transcribe audio
- `POST /api/evidence/ocr` - Extract text via OCR

---

## Platform-Specific Features

### Windows (.NET MAUI)

- Native file picker
- Windows notifications
- Background tasks
- Live tiles (optional)

### Android (.NET MAUI)

- Camera integration
- Android notifications
- Background services
- Material Design 3

### iOS (.NET MAUI)

- Camera integration
- iOS notifications
- Background fetch
- Cupertino design

### Web (Flask)

- Progressive Web App (PWA)
- Service workers for offline
- Responsive design
- Touch-optimized UI

### Mobile Web (Flask)

- Touch gestures
- Mobile-optimized layouts
- Reduced data usage
- Fast loading

---

## Development Setup

### Prerequisites

- .NET 10 SDK
- Python 3.9+
- Visual Studio 2026 or VS Code
- Android SDK (for Android development)
- Xcode (for iOS development, macOS only)

### Mobile App Setup

```bash
cd src/Evident.Mobile
dotnet restore
dotnet build

# Run on Windows
dotnet run -f net10.0-windows

# Run on Android
dotnet build -f net10.0-android
dotnet run -f net10.0-android

# Run on iOS (macOS only)
dotnet build -f net10.0-ios
dotnet run -f net10.0-ios
```

### Web API Setup

```bash
cd src/Evident.Web
dotnet restore
dotnet run
# Runs on https://localhost:5001
```

### Flask Backend Setup

```bash
cd c:\web-dev\github-repos\Evident.info
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
# Runs on http://localhost:5000
```

---

## Dependency Injection

### Mobile App (`MauiProgram.cs`)

```csharp
// HttpClient with base URL
builder.Services.AddHttpClient<IApiClient, ApiClient>(client =>
{
    client.BaseAddress = new Uri("http://localhost:5000");
});

// Services
builder.Services.AddSingleton<AuthService>();

// ViewModels
builder.Services.AddTransient<LoginViewModel>();
builder.Services.AddTransient<AnalysisListViewModel>();

// Views
builder.Services.AddTransient<LoginPage>();
builder.Services.AddTransient<AnalysisListPage>();
```

### Web API (`Program.cs`)

```csharp
// HttpClient for Flask backend
builder.Services.AddHttpClient<IAnalysisService, FlaskProxyAnalysisService>(client =>
{
    client.BaseAddress = new Uri("http://localhost:5000");
});

// Controllers
builder.Services.AddControllers();

// Authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => { /* config */ });
```

---

## Security

### Mobile App

- Credentials stored in `SecureStorage` (encrypted)
- HTTPS-only communication in production
- Certificate pinning (recommended)
- Token refresh mechanism

### Web API

- JWT-based authentication
- CORS configuration
- Rate limiting per tier
- Request validation

### Flask Backend

- Session-based authentication
- CSRF protection
- SQL injection prevention (parameterized queries)
- File upload validation

---

## Deployment

### Mobile Apps

#### Windows

```bash
dotnet publish -f net10.0-windows -c Release
# Output: bin/Release/net10.0-windows/publish/
# Package as MSIX for Microsoft Store
```

#### Android

```bash
dotnet publish -f net10.0-android -c Release
# Output: bin/Release/net10.0-android/publish/
# Sign APK/AAB for Google Play Store
```

#### iOS

```bash
dotnet publish -f net10.0-ios -c Release
# Output: bin/Release/net10.0-ios/publish/
# Archive and upload to App Store Connect
```

### Web API

```bash
cd src/Evident.Web
dotnet publish -c Release -o ./publish
# Deploy to Azure App Service, AWS, or Docker
```

### Flask Backend

```bash
# Production with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or with Docker
docker build -t Evident-api .
docker run -p 5000:5000 Evident-api
```

---

## CI/CD Workflows

### GitHub Actions (Mobile)

```yaml
name: Build Mobile Apps
on: [push, pull_request]
jobs:
  build-android:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '10.0.x'
      - run: dotnet build -f net10.0-android

  build-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '10.0.x'
      - run: dotnet build -f net10.0-ios
```

### GitHub Actions (Web)

```yaml
name: Deploy Flask App
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest
      - run: # Deploy to production
```

---

## Testing Strategy

### Mobile App

- Unit tests for ViewModels
- Integration tests for API client
- UI tests with Appium

### Web API

- Unit tests for controllers
- Integration tests for services
- API contract tests

### Flask Backend

- Unit tests for routes
- Integration tests for AI pipelines
- End-to-end tests

---

## Performance Optimization

### Mobile App

- Image caching
- Lazy loading
- Background processing
- Offline data sync

### Web API

- Response caching
- Database connection pooling
- Async/await throughout
- CDN for static assets

### Flask Backend

- Redis caching
- Celery for background jobs
- Database indexing
- GPU acceleration for AI

---

## Monitoring & Analytics

### Mobile App

- Crash reporting (AppCenter)
- Analytics (PostHog)
- Performance monitoring

### Web API

- Application Insights
- Sentry error tracking
- Prometheus metrics

### Flask Backend

- Sentry error tracking
- PostHog analytics
- Custom logging

---

## Next Steps

1. ✅ Create shared data models
2. ✅ Implement API client
3. ✅ Build mobile ViewModels
4. ✅ Create ASP.NET controllers
5. ⏳ Create XAML views for mobile
6. ⏳ Update ASP.NET Program.cs
7. ⏳ Add authentication middleware
8. ⏳ Implement offline sync
9. ⏳ Create CI/CD pipelines
10. ⏳ Deploy to production

---

## File Structure

```
Evident.info/
├── src/
│   ├── Evident.Shared/          # Shared models & services
│   │   ├── Models/
│   │   │   └── AnalysisRequest.cs
│   │   └── Services/
│   │       ├── IApiClient.cs
│   │       └── ApiClient.cs
│   │
│   ├── Evident.Mobile/          # .NET MAUI app
│   │   ├── Services/
│   │   │   └── AuthService.cs
│   │   ├── ViewModels/
│   │   │   ├── BaseViewModel.cs
│   │   │   ├── LoginViewModel.cs
│   │   │   └── AnalysisListViewModel.cs
│   │   ├── Views/               # XAML pages
│   │   ├── Platforms/           # Platform-specific code
│   │   └── MauiProgram.cs
│   │
│   ├── Evident.Web/             # ASP.NET Core API
│   │   ├── Controllers/
│   │   │   └── AnalysisController.cs
│   │   ├── Services/
│   │   │   ├── IAnalysisService.cs
│   │   │   └── FlaskProxyAnalysisService.cs
│   │   └── Program.cs
│   │
│   └── Evident.Infrastructure/  # Shared infrastructure
│
├── app.py                       # Flask backend
├── templates/                   # Flask templates
├── static/                      # Web assets
└── requirements.txt             # Python dependencies
```

---

## Support

For issues or questions:

- Mobile: Check `Evident.Mobile/README.md`
- Web API: Check `Evident.Web/README.md`
- Flask: Check `DEPENDENCIES-SETUP.md`
