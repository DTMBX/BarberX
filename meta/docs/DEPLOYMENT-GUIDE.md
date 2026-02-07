# Evident Multi-Platform Deployment Guide

## Overview

This guide covers deployment strategies for all Evident platforms:

- **Windows Desktop** - .NET MAUI app via Microsoft Store or direct download
- **Android** - .NET MAUI app via Google Play Store
- **iOS** - .NET MAUI app via Apple App Store
- **Web Application** - Flask app on cloud hosting
- **Web API** - ASP.NET Core on Azure/AWS

---

## Prerequisites

### All Platforms

- Git repository access
- CI/CD pipeline (GitHub Actions recommended)
- Code signing certificates
- API keys and secrets management

### Platform-Specific

- **Windows**: Microsoft Store developer account
- **Android**: Google Play Console account, signing keystore
- **iOS**: Apple Developer account, provisioning profiles
- **Web**: Cloud hosting account (Azure, AWS, Render, etc.)

---

## 1. Windows Desktop Deployment

### Build for Production

```powershell
cd src/Evident.Mobile
dotnet publish -f net10.0-windows -c Release -p:RuntimeIdentifierOverride=win10-x64
```

### Package as MSIX

```powershell
# Install Windows SDK
# Create MSIX package
dotnet publish -f net10.0-windows -c Release /p:GenerateAppxPackageOnBuild=true
```

### Microsoft Store Submission

1. Create app listing in Partner Center
2. Upload MSIX package
3. Complete store listing (screenshots, description)
4. Submit for certification
5. Monitor certification status

### Direct Download Alternative

```powershell
# Create installer with Inno Setup or WiX
# Sign with code signing certificate
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com Evident.exe
```

---

## 2. Android Deployment

### Build Release APK/AAB

```bash
cd src/Evident.Mobile
dotnet publish -f net10.0-android -c Release
```

### Sign APK

```bash
# Generate keystore (first time only)
keytool -genkey -v -keystore Evident.keystore -alias Evident -keyalg RSA -keysize 2048 -validity 10000

# Sign APK
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore Evident.keystore app-release-unsigned.apk Evident

# Align APK
zipalign -v 4 app-release-unsigned.apk Evident.apk
```

### Google Play Console

1. Create app in Play Console
2. Complete store listing
3. Upload AAB (Android App Bundle)
4. Configure release tracks (Internal → Alpha → Beta → Production)
5. Submit for review

### Configuration

```xml
<!-- AndroidManifest.xml -->
<manifest>
    <application android:usesCleartextTraffic="false">
        <!-- Production API endpoint -->
        <meta-data android:name="API_BASE_URL" android:value="https://api.Evident.info"/>
    </application>
</manifest>
```

---

## 3. iOS Deployment

### Build for iOS

```bash
cd src/Evident.Mobile
dotnet build -f net10.0-ios -c Release
```

### Archive and Export

```bash
# Archive (requires macOS)
dotnet publish -f net10.0-ios -c Release -p:ArchiveOnBuild=true

# Export IPA
# Use Xcode or Transporter app
```

### App Store Connect

1. Create app record in App Store Connect
2. Upload IPA via Transporter or Xcode
3. Complete app information
4. Add screenshots for all device sizes
5. Submit for review

### Provisioning

- Create App ID in Apple Developer Portal
- Generate Distribution Certificate
- Create Distribution Provisioning Profile
- Configure in project settings

---

## 4. Flask Web Application Deployment

### Production Server Setup

#### Option A: Render.com (Recommended)

```yaml
# render.yaml
services:
  - type: web
    name: Evident-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: DATABASE_URL
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: SECRET_KEY
        generateValue: true
```

#### Option B: Azure App Service

```bash
# Create App Service
az webapp create --resource-group Evident --plan EvidentPlan --name Evident-api --runtime "PYTHON:3.9"

# Deploy
az webapp deployment source config-zip --resource-group Evident --name Evident-api --src deploy.zip

# Configure environment variables
az webapp config appsettings set --resource-group Evident --name Evident-api --settings \
    FLASK_ENV=production \
    DATABASE_URL=$DATABASE_URL \
    OPENAI_API_KEY=$OPENAI_API_KEY
```

#### Option C: Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
# Build and deploy
docker build -t Evident-api .
docker run -p 5000:5000 --env-file .env Evident-api
```

### Database Migration

```bash
# PostgreSQL production setup
flask db upgrade

# Or use Alembic
alembic upgrade head
```

### Environment Variables

```bash
# .env.production
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://user:pass@host:5432/Evident
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_live_...
REDIS_URL=redis://host:6379
SENTRY_DSN=https://...
```

---

## 5. ASP.NET Core Web API Deployment

### Build for Production

```bash
cd src/Evident.Web
dotnet publish -c Release -o ./publish
```

### Azure App Service

```bash
# Create App Service
az webapp create --resource-group Evident --plan EvidentPlan --name Evident-webapi --runtime "DOTNET:9.0"

# Deploy
az webapp deployment source config-zip --resource-group Evident --name Evident-webapi --src publish.zip

# Configure app settings
az webapp config appsettings set --resource-group Evident --name Evident-webapi --settings \
    ASPNETCORE_ENVIRONMENT=Production \
    FlaskBackend__Url=https://api.Evident.info \
    Jwt__Key=$JWT_SECRET
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY ["src/Evident.Web/Evident.Web.csproj", "Evident.Web/"]
RUN dotnet restore "Evident.Web/Evident.Web.csproj"
COPY . .
WORKDIR "/src/Evident.Web"
RUN dotnet build "Evident.Web.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "Evident.Web.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "Evident.Web.dll"]
```

### Configuration

```json
// appsettings.Production.json
{
  "Logging": {
    "LogLevel": {
      "Default": "Warning"
    }
  },
  "FlaskBackend": {
    "Url": "https://api.Evident.info"
  },
  "Jwt": {
    "Key": "env:JWT_SECRET",
    "Issuer": "Evident",
    "Audience": "Evident"
  }
}
```

---

## 6. CI/CD Pipelines

### GitHub Actions - Mobile Apps

```yaml
# .github/workflows/mobile-build.yml
name: Build Mobile Apps

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build-android:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '10.0.x'

      - name: Restore dependencies
        run: dotnet restore src/Evident.Mobile/Evident.Mobile.csproj

      - name: Build Android
        run:
          dotnet build src/Evident.Mobile/Evident.Mobile.csproj -f
          net10.0-android -c Release

      - name: Sign APK
        if: github.ref == 'refs/heads/main'
        run: |
          # Sign with keystore from secrets
          echo "${{ secrets.ANDROID_KEYSTORE }}" | base64 -d > Evident.keystore
          jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
            -keystore Evident.keystore \
            -storepass ${{ secrets.KEYSTORE_PASSWORD }} \
            bin/Release/net10.0-android/com.Evident.mobile.apk Evident

      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: android-apk
          path: bin/Release/net10.0-android/*.apk

  build-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '10.0.x'

      - name: Install provisioning profile
        run: |
          mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
          echo "${{ secrets.IOS_PROVISIONING_PROFILE }}" | base64 -d > \
            ~/Library/MobileDevice/Provisioning\ Profiles/Evident.mobileprovision

      - name: Build iOS
        run:
          dotnet build src/Evident.Mobile/Evident.Mobile.csproj -f net10.0-ios
          -c Release

      - name: Archive
        if: github.ref == 'refs/heads/main'
        run:
          dotnet publish src/Evident.Mobile/Evident.Mobile.csproj -f net10.0-ios
          -c Release -p:ArchiveOnBuild=true

      - name: Upload IPA
        uses: actions/upload-artifact@v3
        with:
          name: ios-ipa
          path: bin/Release/net10.0-ios/*.ipa
```

### GitHub Actions - Flask Backend

```yaml
# .github/workflows/flask-deploy.yml
name: Deploy Flask Backend

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest

      - name: Deploy to Render
        if: success()
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

### GitHub Actions - ASP.NET Core API

```yaml
# .github/workflows/webapi-deploy.yml
name: Deploy Web API

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '9.0.x'

      - name: Restore dependencies
        run: dotnet restore src/Evident.Web/Evident.Web.csproj

      - name: Build
        run: dotnet build src/Evident.Web/Evident.Web.csproj -c Release

      - name: Test
        run: dotnet test

      - name: Publish
        run:
          dotnet publish src/Evident.Web/Evident.Web.csproj -c Release -o
          ./publish

      - name: Deploy to Azure
        uses: azure/webapps-deploy@v2
        with:
          app-name: Evident-webapi
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
          package: ./publish
```

---

## 7. Secrets Management

### GitHub Secrets

Required secrets for CI/CD:

**Mobile Apps**:

- `ANDROID_KEYSTORE` - Base64 encoded keystore
- `KEYSTORE_PASSWORD` - Keystore password
- `IOS_PROVISIONING_PROFILE` - Base64 encoded profile
- `IOS_CERTIFICATE` - Base64 encoded certificate

**Backend**:

- `RENDER_DEPLOY_HOOK` - Render.com deploy webhook
- `AZURE_WEBAPP_PUBLISH_PROFILE` - Azure publish profile
- `DATABASE_URL` - Production database URL
- `OPENAI_API_KEY` - OpenAI API key
- `STRIPE_SECRET_KEY` - Stripe secret key
- `JWT_SECRET` - JWT signing key

### Environment-Specific Configuration

```bash
# Development
API_BASE_URL=http://localhost:5000

# Staging
API_BASE_URL=https://staging-api.Evident.info

# Production
API_BASE_URL=https://api.Evident.info
```

---

## 8. Monitoring & Analytics

### Application Insights (Azure)

```csharp
// Program.cs
builder.Services.AddApplicationInsightsTelemetry();
```

### Sentry Error Tracking

```python
# app.py
import sentry_sdk
sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'))
```

### PostHog Analytics

```python
# app.py
from posthog import Posthog
posthog = Posthog(os.getenv('POSTHOG_API_KEY'))
```

---

## 9. Performance Optimization

### Mobile Apps

- Enable AOT compilation for iOS
- Use R8/ProGuard for Android
- Implement image caching
- Lazy load views

### Web API

- Enable response caching
- Use CDN for static assets
- Implement Redis caching
- Enable gzip compression

### Flask Backend

- Use Gunicorn with multiple workers
- Enable Redis caching
- Implement database connection pooling
- Use Celery for background tasks

---

## 10. Rollback Strategy

### Mobile Apps

- Keep previous version available in stores
- Implement feature flags
- Monitor crash reports closely

### Backend Services

- Use blue-green deployment
- Keep previous Docker images
- Database migration rollback scripts
- Monitor error rates

---

## Quick Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Version numbers updated
- [ ] Changelog updated
- [ ] Secrets configured
- [ ] Database migrations ready

### Mobile Apps

- [ ] Build signed release
- [ ] Test on physical devices
- [ ] Update store listings
- [ ] Prepare screenshots
- [ ] Submit for review

### Backend

- [ ] Environment variables set
- [ ] Database backed up
- [ ] Run migrations
- [ ] Deploy to staging first
- [ ] Smoke test critical paths
- [ ] Deploy to production
- [ ] Monitor logs and metrics

### Post-Deployment

- [ ] Verify all platforms working
- [ ] Check error rates
- [ ] Monitor performance
- [ ] Update documentation
- [ ] Notify team

---

## Support

For deployment issues:

- Check logs in respective platforms
- Review CI/CD pipeline outputs
- Consult platform-specific documentation
- Contact platform support if needed
