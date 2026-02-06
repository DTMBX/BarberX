# Evident Phase 2 Deployment Guide

## 🎯 Current Status

✅ **Phase 1 Complete:** REST API fully implemented and tested  
🔧 **Phase 2 In Progress:** MAUI services 50% complete  
📋 **Next:** Deploy API to production and complete MAUI layer

--

## 🚀 Part 1: Deploy API to Production (Render.com)

### Step 1: Verify API Works Locally

```bash
cd C:\web-dev\github-repos\Evident.info

# Quick import test (already verified ✅)
python -c "from api import auth_api; print('OK')"

# Start Flask app
python app.py

# Should see:
# ✓ Registered API blueprint: /api/v1/auth
# ✓ Registered API blueprint: /api/v1/upload
# ✓ Registered API blueprint: /api/v1/analysis
# ... etc
# * Running on http://127.0.0.1:5000
```

### Step 2: Test with Postman

1. **Import Collection:**
   - Open Postman
   - Import `postman_collection.json`
   - Set base URL to `http://localhost:5000`

2. **Test Authentication:**
   - Run "Register User" request
   - Run "Login User" request (token auto-saved)
   - Run "Get Current User" request

3. **Test Upload:**
   - Run "Upload PDF" request
   - Check response for `file_id`

4. **Test Analysis:**
   - Run "Start Analysis" with `file_id`
   - Run "Get Analysis Status"

### Step 3: Commit and Push

```bash
cd C:\web-dev\github-repos\Evident.info

# Add all changes
git add .

# Commit with detailed message
git commit -m "feat: Add REST API v1 + MAUI client services

Phase 1 (REST API):
- 7 API blueprints (auth, upload, analysis, user, billing, evidence, admin)
- JWT authentication with 24-hour expiration
- 30+ endpoints documented
- CORS support for mobile/desktop
- Tier-based access control
- Comprehensive API documentation

Phase 2 (MAUI Services):
- 5 service classes (Auth, Upload, Analysis, User, Billing)
- 40+ API model DTOs
- Token management with auto-refresh
- Multipart file upload support
- Progress tracking infrastructure

Documentation:
- API-REFERENCE.md (complete endpoint docs)
- API-QUICK-START.md (5-minute tutorial)
- PHASE-1-API-COMPLETE.md (implementation summary)
- PHASE-2-MAUI-PROGRESS.md (MAUI guide)
- postman_collection.json (testing collection)
- SESSION-SUMMARY.md (comprehensive summary)
- QUICK-REFERENCE.md (developer quick ref)

Dependencies:
- Added PyJWT 2.10.1 for JWT tokens
"

# Push to GitHub
git push origin main
```

### Step 4: Deploy to Render.com

**Automatic Deployment:**

- Render.com detects push to `main` branch
- Builds using `requirements.txt`
- Runs using `gunicorn app:app`
- Uses `render.yaml` configuration

**Manual Trigger (if needed):**

1. Go to [Render.com Dashboard](https://dashboard.render.com)
2. Select "Evident" service
3. Click "Manual Deploy" → "Deploy latest commit"

**Monitor Deployment:**

- Check build logs for errors
- Verify "✓ Registered API blueprint" messages
- Wait for "Service is live" status

### Step 5: Verify Production API

```bash
# Test production API
curl https://Evident.info/api/v1/auth/login

# Should return method not allowed (needs POST)
# Indicates endpoint is live

# Test with registration
curl -X POST https://Evident.info/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'

# Should return JWT token + user object
```

### Step 6: Update Postman Collection

1. Duplicate environment
2. Create "Production" environment
3. Set base URL: `https://Evident.info`
4. Run test suite against production

--

## 🔧 Part 2: Complete MAUI Services

### Remaining Services to Create

#### 1. EvidenceService.cs

```csharp
// Location: src/Evident.MatterDocket.MAUI/Services/EvidenceService.cs

public interface IEvidenceService
{
    Task<ApiResponse<List<EvidenceItem>>> GetEvidenceListAsync(int caseId);
    Task<ApiResponse<EvidenceDetails>> GetEvidenceAsync(int evidenceId);
    Task<ApiResponse<TranscriptionResult>> TranscribeVideoAsync(int evidenceId);
    Task<ApiResponse<OcrResult>> ExtractTextFromPdfAsync(int evidenceId);
    Task<ApiResponse<bool>> DeleteEvidenceAsync(int evidenceId);
}
```

#### 2. TierService.cs

```csharp
// Location: src/Evident.MatterDocket.MAUI/Services/TierService.cs

public interface ITierService
{
    Task<ApiResponse<UserTier>> GetCurrentTierAsync();
    bool CanUploadPdf(long fileSize);
    bool CanUploadVideo(long fileSize);
    bool CanUseAiAnalysis();
    string GetUpgradeMessage(string feature);
}
```

#### 3. CaseService.cs

```csharp
// Location: src/Evident.MatterDocket.MAUI/Services/CaseService.cs

public interface ICaseService
{
    Task<ApiResponse<List<CaseListItem>>> GetCasesAsync();
    Task<ApiResponse<CaseDetails>> GetCaseAsync(int caseId);
    Task<ApiResponse<CaseDetails>> CreateCaseAsync(CreateCaseRequest request);
    Task<ApiResponse<CaseDetails>> UpdateCaseAsync(int caseId, UpdateCaseRequest request);
    Task<ApiResponse<bool>> DeleteCaseAsync(int caseId);
}
```

### Register Services in MauiProgram.cs

```csharp
// Location: src/Evident.MatterDocket.MAUI/MauiProgram.cs

public static MauiApp CreateMauiApp()
{
    var builder = MauiApp.CreateBuilder();
    builder
        .UseMauiApp<App>()
        .ConfigureFonts(fonts =>
        {
            fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
            fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
        });

    // Register services
    builder.Services.AddSingleton<IApiService, ApiService>();
    builder.Services.AddSingleton<IAuthService, AuthService>();
    builder.Services.AddSingleton<IUploadService, UploadService>();
    builder.Services.AddSingleton<IAnalysisService, AnalysisService>();
    builder.Services.AddSingleton<IUserService, UserService>();
    builder.Services.AddSingleton<IBillingService, BillingService>();
    // TODO: Add remaining services
    // builder.Services.AddSingleton<IEvidenceService, EvidenceService>();
    // builder.Services.AddSingleton<ITierService, TierService>();
    // builder.Services.AddSingleton<ICaseService, CaseService>();

    return builder.Build();
}
```

--

## 📱 Part 3: Build ViewModels (MVVM Pattern)

### Base ViewModel

```csharp
// Location: src/Evident.MatterDocket.MAUI/ViewModels/BaseViewModel.cs

public class BaseViewModel : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler PropertyChanged;

    protected void OnPropertyChanged([CallerMemberName] string name = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }

    protected bool SetProperty<T>(ref T field, T value, [CallerMemberName] string name = null)
    {
        if (EqualityComparer<T>.Default.Equals(field, value)) return false;
        field = value;
        OnPropertyChanged(name);
        return true;
    }
}
```

### LoginViewModel

```csharp
// Location: src/Evident.MatterDocket.MAUI/ViewModels/LoginViewModel.cs

public class LoginViewModel : BaseViewModel
{
    private readonly IAuthService _authService;

    public string Email { get; set; }
    public string Password { get; set; }
    public bool IsLoading { get; set; }
    public string ErrorMessage { get; set; }

    public ICommand LoginCommand { get; }
    public ICommand RegisterCommand { get; }

    public LoginViewModel(IAuthService authService)
    {
        _authService = authService;
        LoginCommand = new Command(async () => await LoginAsync());
        RegisterCommand = new Command(async () => await RegisterAsync());
    }

    private async Task LoginAsync()
    {
        IsLoading = true;
        ErrorMessage = null;

        var result = await _authService.LoginAsync(Email, Password);

        if (result.Success)
        {
            // Navigate to dashboard
            await Shell.Current.GoToAsync("//Dashboard");
        }
        else
        {
            ErrorMessage = result.ErrorMessage;
        }

        IsLoading = false;
    }
}
```

--

## 🖼️ Part 4: Create UI Pages (XAML)

### LoginPage.xaml

```xml
<!-- Location: src/Evident.MatterDocket.MAUI/Views/LoginPage.xaml ->

<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:vm="clr-namespace:Evident.MatterDocket.MAUI.ViewModels"
             x:Class="Evident.MatterDocket.MAUI.Views.LoginPage"
             Title="Evident Login">

    <ContentPage.BindingContext>
        <vm:LoginViewModel />
    </ContentPage.BindingContext>

    <StackLayout Padding="20" VerticalOptions="Center">
        <Label Text="Evident Matter Docket"
               FontSize="32"
               HorizontalOptions="Center"
               Margin="0,0,0,40" />

        <Entry Placeholder="Email"
               Text="{Binding Email}"
               Keyboard="Email"
               Margin="0,10" />

        <Entry Placeholder="Password"
               Text="{Binding Password}"
               IsPassword="True"
               Margin="0,10" />

        <Button Text="Login"
                Command="{Binding LoginCommand}"
                IsEnabled="{Binding IsLoading, Converter={StaticResource InverseBoolConverter}}"
                Margin="0,20,0,10" />

        <Button Text="Register"
                Command="{Binding RegisterCommand}"
                BackgroundColor="Transparent"
                TextColor="{StaticResource Primary}"
                Margin="0,10" />

        <Label Text="{Binding ErrorMessage}"
               TextColor="Red"
               IsVisible="{Binding ErrorMessage, Converter={StaticResource StringNotNullOrEmptyConverter}}"
               Margin="0,20" />

        <ActivityIndicator IsRunning="{Binding IsLoading}"
                          IsVisible="{Binding IsLoading}" />
    </StackLayout>
</ContentPage>
```

--

## ✅ Deployment Checklist

### Pre-Deployment

- [x] API modules created and tested locally
- [x] JWT authentication implemented
- [x] CORS configured for production
- [x] API documentation complete
- [x] Postman collection created
- [x] MAUI services implemented (5/8 complete)
- [ ] All services registered in DI
- [ ] ViewModels created
- [ ] UI pages built
- [ ] End-to-end testing

### Production Deployment

- [ ] Environment variables set on Render.com:
  - [ ] `SECRET_KEY` (generate new for production)
  - [ ] `DATABASE_URL` (PostgreSQL connection)
  - [ ] `STRIPE_SECRET_KEY` (live key)
  - [ ] `STRIPE_WEBHOOK_SECRET` (live webhook)
  - [ ] `CORS_ORIGINS` (production domains)
  - [ ] `OPENAI_API_KEY` (for AI features)

- [ ] Code committed and pushed to GitHub
- [ ] Render.com deployment triggered
- [ ] Build logs checked for errors
- [ ] Production API tested with Postman
- [ ] Database migrations run successfully
- [ ] Stripe webhooks configured
- [ ] SSL certificate active (HTTPS)

### Post-Deployment

- [ ] Test registration flow in production
- [ ] Test login and token refresh
- [ ] Test file upload (PDF and video)
- [ ] Test AI analysis workflow
- [ ] Test Stripe checkout session
- [ ] Monitor error logs for 24 hours
- [ ] Update documentation with production URLs

--

## 🐛 Troubleshooting

### API Import Errors

```bash
# If "ModuleNotFoundError: No module named 'api'"
cd C:\web-dev\github-repos\Evident.info
python -c "import sys; print(sys.path); from api import auth_api"

# Ensure api/ folder has __init__.py
ls api/__init__.py
```

### JWT Token Issues

```python
# Generate new secret key for production
python -c "import secrets; print(secrets.token_hex(32))"

# Set in Render.com environment variables
# Never commit SECRET_KEY to git!
```

### CORS Errors from MAUI App

```python
# Update CORS_ORIGINS in Render.com
CORS_ORIGINS=https://Evident.info,https://www.Evident.info,http://localhost:5000
```

### Database Connection Errors

```bash
# Check DATABASE_URL format
postgresql://user:password@host:5432/database

# Test connection
python -c "from app import db; db.create_all(); print('OK')"
```

--

## 📊 Success Metrics

After deployment, verify:

1. **API Health:** All endpoints return 200 or appropriate status
2. **Authentication:** Login returns valid JWT token
3. **File Upload:** PDF/video uploads succeed
4. **Analysis:** AI analysis completes without errors
5. **Billing:** Stripe checkout creates session
6. **Performance:** Response time < 2 seconds
7. **Uptime:** 99.9% availability (monitor with Render.com)

--

## 🚀 Next Phase

After successful deployment:

1. **Complete MAUI Services:**
   - EvidenceService
   - TierService
   - CaseService

2. **Build ViewModels:**
   - LoginViewModel ✅
   - DashboardViewModel
   - UploadViewModel
   - CaseDetailViewModel

3. **Create UI Pages:**
   - LoginPage ✅
   - DashboardPage
   - UploadPage
   - CaseDetailPage
   - SettingsPage

4. **Test on Platforms:**
   - Windows desktop (primary target)
   - iOS simulator
   - Android emulator

5. **Package and Distribute:**
   - Windows: MSIX installer
   - iOS: TestFlight beta
   - Android: Google Play Internal Testing

--

**Ready to deploy?** Run the commands in Part 1 to push to production! 🚀
