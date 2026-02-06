# Evident MAUI - Quick Start Guide

## 🚀 Running the App (Development)

### Windows Desktop

```powershell
cd "C:\web-dev\github-repos\Evident.info\src\Evident.MatterDocket.MAUI"
dotnet run -f net10.0-windows10.0.19041.0
```

### Build Only

```powershell
dotnet build -f net10.0-windows10.0.19041.0 -c Debug
```

### Clean Build

```powershell
dotnet clean
dotnet build -f net10.0-windows10.0.19041.0 -c Debug
```

--

## 📱 Testing Workflow

### 1. Start Flask API (Required)

The MAUI app needs the backend API running:

```powershell
# In separate terminal
cd "C:\web-dev\github-repos\Evident.info"
python app.py
```

API will run at: `http://localhost:5000`

### 2. Run MAUI App

```powershell
cd "C:\web-dev\github-repos\Evident.info\src\Evident.MatterDocket.MAUI"
dotnet run -f net10.0-windows10.0.19041.0
```

### 3. Test User Flows

**Flow 1: New User Registration**

1. Launch app → Login page appears
2. Click "Register" button
3. Enter email + password
4. Should navigate to Dashboard (currently empty - API not running)

**Flow 2: Existing User Login**

1. Enter credentials
2. Click "Login"
3. Should navigate to Dashboard
4. Verify user name and tier badge display

**Flow 3: File Upload**

1. From Dashboard, click "Upload Evidence"
2. Select file type (PDF or Video)
3. Click "Choose File" → File picker opens
4. Select a file
5. Click "Upload" → Progress bar appears
6. Should see success message

**Flow 4: Navigation**

1. Test shell navigation (hamburger menu if present)
2. Test back navigation
3. Verify routes work: Login, Dashboard, Upload

--

## 🔧 Development Tips

### Hot Reload

MAUI supports hot reload for XAML changes:

1. Run app with `dotnet run`
2. Edit XAML file
3. Save → UI updates automatically
4. C# changes require rebuild

### Debug Mode

Add breakpoints in Visual Studio Code:

1. Open C# file
2. Click left margin to add breakpoint
3. Press F5 to start debugging
4. App pauses at breakpoints

### Check Logs

```powershell
# View detailed build output
dotnet build -v detailed

# View minimal output
dotnet build -v minimal
```

--

## 🌐 API Endpoints (for testing)

### Authentication

- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `GET /api/v1/auth/me` - Get current user

### Upload

- `POST /api/v1/upload/pdf` - Upload PDF document
- `POST /api/v1/upload/video` - Upload video file
- `GET /api/v1/upload/status/{file_id}` - Check upload status

### User

- `GET /api/v1/user/profile` - Get user profile
- `GET /api/v1/user/usage` - Get usage statistics
- `PUT /api/v1/user/profile` - Update profile

### Analysis

- `POST /api/v1/analysis/start` - Start AI analysis
- `GET /api/v1/analysis/{id}` - Get analysis result
- `GET /api/v1/analysis/list` - List all analyses

--

## 🐛 Common Issues & Fixes

### Issue: "API connection failed"

**Solution:** Make sure Flask app is running on `http://localhost:5000`

### Issue: "File not found" on upload

**Solution:** Check file permissions and path

### Issue: "JWT token expired"

**Solution:** App auto-refreshes tokens. If persists, logout and login again

### Issue: "Tier limit exceeded"

**Solution:** Check user tier and file size. FREE tier = 10MB PDF only

### Issue: Build fails with "CS" errors

**Solution:** Clean build:

```powershell
dotnet clean
rm -r bin, obj
dotnet restore
dotnet build
```

--

## 📦 Publishing for Production

### Windows Desktop (MSIX Package)

```powershell
dotnet publish -f net10.0-windows10.0.19041.0 -c Release -p:RuntimeIdentifierOverride=win10-x64 -p:WindowsPackageType=MSIX
```

Output: `bin\Release\net10.0-windows10.0.19041.0\win10-x64\publish\`

### Android APK

```bash
dotnet publish -f net10.0-android -c Release
```

Output: `bin\Release\net10.0-android\publish\`

### iOS App (requires Mac)

```bash
dotnet publish -f net10.0-ios -c Release
```

--

## 🔑 Environment Variables

### Development (DEBUG mode)

```
API_BASE_URL = http://localhost:5000/api/v1
```

### Production (RELEASE mode)

```
API_BASE_URL = https://Evident.info/api/v1
```

Configured in: `src/Evident.MatterDocket.MAUI/Helpers/Constants.cs`

--

## 📊 Performance Optimization

### Reduce App Size

```powershell
# Enable trimming and AOT
dotnet publish -c Release -p:PublishTrimmed=true -p:EnableCompressionInSingleFile=true
```

### Improve Startup Time

- Use Singleton services for heavy initialization
- Lazy-load ViewModels
- Defer non-critical service initialization

### Reduce Memory Usage

- Dispose streams after upload
- Clear large collections when not needed
- Use weak references for cached data

--

## 🧪 Testing Commands

### Unit Tests (when added)

```powershell
dotnet test
```

### Code Coverage

```powershell
dotnet test --collect:"XPlat Code Coverage"
```

### Lint/Format

```powershell
dotnet format
```

--

## 📚 Additional Resources

### Official Docs

- [.NET MAUI Documentation](https://learn.microsoft.com/en-us/dotnet/maui/)
- [CommunityToolkit.Mvvm](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/)
- [XAML Controls](https://learn.microsoft.com/en-us/dotnet/maui/user-interface/controls/)

### Project Documentation

- `API-REFERENCE.md` - Complete API documentation
- `MAUI-BUILD-COMPLETE.md` - Build optimization summary
- `PHASE-3-UI-PROGRESS.md` - UI implementation details

### Support

- GitHub Issues:
  [Create an issue](https://github.com/YOUR_ORG/Evident.info/issues)
- Email: support@Evident.info

--

**Last Updated:** January 27, 2026  
**Build Status:** ✅ PASSING (0 errors)  
**Version:** 1.0.0
