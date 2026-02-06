# Evident Matter Docket (DTMB) - Phase C: Development Environment Setup

**Date:** January 27, 2026  
**Status:** Starting Phase C - Installing Development Tools

--

## 🎯 Phase C Overview

**Goal:** Set up complete development environment for .NET MAUI Windows 11 development  
**Duration:** 1-2 hours  
**Prerequisites:** Windows 11, Administrator access

--

## 📦 Required Software

### 1. Visual Studio 2022 Community Edition

**Purpose:** Primary IDE for .NET MAUI development  
**Download:** https://visualstudio.microsoft.com/vs/community/  
**License:** Free for individual developers  
**Size:** ~8-15 GB (with workloads)

**Required Workloads:**

- ✅ .NET Multi-platform App UI development
- ✅ .NET desktop development
- ✅ Universal Windows Platform development

**Optional (Recommended):**

- Azure development (for cloud integration)
- Mobile development with .NET (for cross-platform)

--

### 2. .NET 8.0 SDK

**Purpose:** Latest .NET runtime and SDK  
**Download:** https://dotnet.microsoft.com/download/dotnet/8.0  
**Version:** 8.0.x (latest)  
**Size:** ~200 MB

**Verification:**

```powershell
dotnet -version
# Expected: 8.0.xxx
```

--

### 3. Windows SDK

**Purpose:** Windows 11 app packaging and deployment  
**Download:** Included with Visual Studio  
**Version:** 10.0.22621.0 or later (Windows 11)

**Components Needed:**

- Windows App SDK
- MSIX Packaging Tools
- Code signing tools (SignTool.exe)

--

### 4. Git for Windows

**Purpose:** Version control  
**Download:** https://git-scm.com/download/win  
**Version:** Latest  
**Size:** ~50 MB

**Configuration:**

```powershell
git config -global user.name "Your Name"
git config -global user.email "your.email@example.com"
```

--

### 5. Additional Tools (Optional)

#### Windows Terminal

**Purpose:** Modern terminal for PowerShell/CMD  
**Download:** Microsoft Store (free)  
**Why:** Better developer experience

#### PowerShell 7

**Purpose:** Latest PowerShell version  
**Download:** https://github.com/PowerShell/PowerShell/releases  
**Size:** ~100 MB

#### Windows Subsystem for Linux (WSL2)

**Purpose:** Run Linux/Python development (Flask backend)  
**Install:**

```powershell
wsl -install
```

--

## 🛠️ Installation Steps

### Step 1: Install Visual Studio 2022

1. **Download Installer**

   ```powershell
   # Download Visual Studio 2022 Community
   Start-Process "https://visualstudio.microsoft.com/vs/community/"
   ```

2. **Run Installer**
   - Launch `vs_community.exe`
   - Sign in with Microsoft account (optional)

3. **Select Workloads**
   - [x] .NET Multi-platform App UI development
   - [x] .NET desktop development
   - [x] Universal Windows Platform development

4. **Individual Components (Additional)**
   - Windows 11 SDK (10.0.22621.0)
   - .NET 8.0 Runtime
   - MSIX Packaging Tools

5. **Installation Location**
   - Default: `C:\Program Files\Microsoft Visual Studio\2022\Community`
   - Requires ~15-20 GB free space

6. **Install**
   - Click "Install"
   - Wait 30-60 minutes (depending on internet speed)

--

### Step 2: Install .NET 8 SDK

1. **Download SDK**

   ```powershell
   # Open download page
   Start-Process "https://dotnet.microsoft.com/download/dotnet/8.0"
   ```

2. **Run Installer**
   - Select: "SDK x64" (Windows)
   - Install to default location

3. **Verify Installation**

   ```powershell
   dotnet -version
   # Should show: 8.0.xxx

   dotnet -list-sdks
   # Should include: 8.0.xxx [C:\Program Files\dotnet\sdk]
   ```

--

### Step 3: Configure MAUI Workload

1. **Install MAUI Workload**

   ```powershell
   dotnet workload install maui
   ```

2. **Verify MAUI Installation**

   ```powershell
   dotnet workload list
   # Should show: maui
   ```

3. **Install Additional Workloads (Optional)**

   ```powershell
   # For Android support
   dotnet workload install android

   # For iOS support (requires Mac for builds)
   dotnet workload install ios
   ```

--

### Step 4: Install Git (if not already installed)

1. **Check if Git exists**

   ```powershell
   git -version
   ```

2. **Install if missing**
   - Download from https://git-scm.com/download/win
   - Use default settings
   - Select "Use Git from Windows Command Prompt"

3. **Configure Git**
   ```powershell
   git config -global user.name "Developer"
   git config -global user.email "dev@Evident.info"
   ```

--

### Step 5: Install Windows Terminal (Optional but Recommended)

1. **Install from Microsoft Store**

   ```powershell
   # Open Microsoft Store
   start ms-windows-store://pdp/?ProductId=9N0DX20HK701
   ```

2. **Set as Default Terminal**
   - Settings → Default terminal application → Windows Terminal

--

## 🔧 Environment Configuration

### Visual Studio Configuration

1. **Theme**
   - Tools → Options → Environment → General → Color theme
   - Recommended: Dark (matches Evident branding)

2. **Editor Settings**
   - Tools → Options → Text Editor → All Languages
   - Tab size: 4 spaces
   - Insert spaces (not tabs)

3. **MAUI Hot Reload**
   - Tools → Options → XAML Hot Reload
   - Enable XAML Hot Reload

4. **Performance Optimization**
   - Tools → Options → Performance
   - Disable unnecessary features for faster startup

--

### Code Signing Setup (For Package Distribution)

#### Option 1: Self-Signed Certificate (Development)

```powershell
# Create self-signed certificate
$cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject "CN=Evident Matter Docket Development" `
    -CertStoreLocation "Cert:\CurrentUser\My"

# Export certificate
$certPath = "C:\Dev\Evident-Dev-Cert.cer"
Export-Certificate -Cert $cert -FilePath $certPath

# Import to Trusted Root (requires admin)
Import-Certificate -FilePath $certPath `
    -CertStoreLocation "Cert:\LocalMachine\Root"
```

#### Option 2: Commercial Certificate (Production)

- Purchase from DigiCert, GlobalSign, or Sectigo
- Cost: ~$400-800/year
- Provides trusted signing for distribution

--

## 📁 Project Setup

### Create New MAUI Project

```powershell
# Navigate to projects directory
cd C:\Dev\Projects

# Create new MAUI app
dotnet new maui -n Evident.MatterDocket.MAUI -f net8.0

# Open in Visual Studio
cd Evident.MatterDocket.MAUI
start Evident.MatterDocket.MAUI.csproj
```

### Project Structure Setup

```powershell
# Create directory structure
cd Evident.MatterDocket.MAUI

New-Item -ItemType Directory -Path "Views"
New-Item -ItemType Directory -Path "ViewModels"
New-Item -ItemType Directory -Path "Services"
New-Item -ItemType Directory -Path "Models"
New-Item -ItemType Directory -Path "Resources\Images"
New-Item -ItemType Directory -Path "Resources\Styles"
```

### Add Required NuGet Packages

```powershell
# MVVM Community Toolkit
dotnet add package CommunityToolkit.Mvvm

# HTTP Extensions
dotnet add package Microsoft.Extensions.Http

# SQLite for local caching
dotnet add package sqlite-net-pcl

# Windows App SDK (if not included)
dotnet add package Microsoft.WindowsAppSDK
```

--

## ✅ Verification Checklist

### Visual Studio

- [ ] Visual Studio 2022 installed
- [ ] .NET Multi-platform App UI workload installed
- [ ] Can create new MAUI project
- [ ] XAML designer loads

### .NET SDK

- [ ] .NET 8.0 SDK installed
- [ ] `dotnet -version` shows 8.0.x
- [ ] MAUI workload installed
- [ ] Can build MAUI project

### Windows Development

- [ ] Windows SDK installed
- [ ] MSIX packaging tools available
- [ ] Code signing certificate ready (dev or commercial)

### Tools

- [ ] Git installed and configured
- [ ] Windows Terminal installed (optional)
- [ ] PowerShell 7 installed (optional)

--

## 🧪 Test Development Environment

### Create & Run Sample MAUI App

```powershell
# Create test project
cd C:\Temp
dotnet new maui -n TestApp -f net8.0
cd TestApp

# Build project
dotnet build

# Run on Windows
dotnet run
```

**Expected Result:**

- App should compile without errors
- Windows window should open
- Should see "Hello, World!" button
- Clicking button should increment counter

--

## 🐛 Troubleshooting

### Issue: MAUI workload not found

**Solution:**

```powershell
dotnet workload restore
dotnet workload install maui
```

### Issue: Windows SDK version mismatch

**Solution:**

```powershell
# Update Windows SDK
dotnet workload update
```

### Issue: Visual Studio build errors

**Solution:**

1. Clean solution: Build → Clean Solution
2. Rebuild: Build → Rebuild Solution
3. Restart Visual Studio

### Issue: XAML Hot Reload not working

**Solution:**

1. Tools → Options → XAML Hot Reload
2. Enable all options
3. Restart Visual Studio

--

## 📊 System Requirements

### Minimum

- **OS:** Windows 11 version 22000 or higher
- **RAM:** 8 GB
- **Storage:** 20 GB free space
- **CPU:** 64-bit processor, 1.8 GHz or faster

### Recommended

- **OS:** Windows 11 22H2 or later
- **RAM:** 16 GB or more
- **Storage:** 50 GB free space (SSD preferred)
- **CPU:** Multi-core processor, 2.5 GHz or faster
- **GPU:** DirectX 12 compatible (for UI acceleration)

--

## 🚀 Next Steps After Setup

1. **Verify Everything Works**
   - Create test MAUI project
   - Build and run
   - Test XAML designer

2. **Clone Evident Repository**

   ```powershell
   git clone https://github.com/DTB396/Evident.info.git
   ```

3. **Start Phase B Development**
   - Implement login screen
   - Build API client
   - Create dashboard

--

## 📝 Installation Script

### Automated Setup Script

```powershell
# Evident-DevEnv-Setup.ps1
# Automated development environment setup

Write-Host "Evident Matter Docket - Dev Environment Setup" -ForegroundColor Cyan

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run as Administrator"
    exit
}

# Install Chocolatey (package manager)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install Git
choco install git -y

# Install .NET 8 SDK
choco install dotnet-sdk -y

# Install Visual Studio 2022 Community (manual step required)
Write-Host "`nPlease install Visual Studio 2022 Community manually:"
Write-Host "https://visualstudio.microsoft.com/vs/community/" -ForegroundColor Yellow
Write-Host "`nSelect workloads: .NET MAUI, .NET Desktop, UWP" -ForegroundColor Yellow

# Install Windows Terminal
choco install microsoft-windows-terminal -y

Write-Host "`n✅ Basic tools installed!" -ForegroundColor Green
Write-Host "Next steps:"
Write-Host "1. Install Visual Studio 2022 (see link above)"
Write-Host "2. Run: dotnet workload install maui"
Write-Host "3. Verify: dotnet -version"
```

--

_Status: Phase C Ready for Execution_  
_Estimated Time: 1-2 hours_  
_Last Updated: January 27, 2026_
