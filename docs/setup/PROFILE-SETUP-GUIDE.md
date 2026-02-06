# PowerShell Profile Setup Instructions

## Quick Install (2 minutes)

### Step 1: Create/Edit Your PowerShell Profile

```powershell
# Check if profile exists
Test-Path $PROFILE

# If False, create it:
New-Item -Path $PROFILE -ItemType File -Force

# Open in notepad
notepad $PROFILE
```

### Step 2: Add Evident Profile

**Copy and paste** the entire contents of `Evident-Profile.ps1` into your profile file.

Or use this one-liner:

```powershell
# Append Evident profile to your existing profile
Get-Content "C:\web-dev\github-repos\Evident.info\Evident-Profile.ps1" | Add-Content $PROFILE
```

### Step 3: Reload Profile

```powershell
# Reload PowerShell profile
. $PROFILE

# You should see:
# 🚀 Evident Development Environment Loaded!
```

--

## Available Commands

### 📁 Navigation Shortcuts

| Command   | Description                  | Example   |
| --------- | ---------------------------- | --------- |
| `br`      | Go to Evident root           | `br`      |
| `bm`      | Go to MAUI project           | `bm`      |
| `ba`      | Go to API directory          | `ba`      |
| `bd`      | Go to Docs directory         | `bd`      |
| `b-`      | Go back to previous location | `b-`      |
| `brecent` | Show recent 10 locations     | `brecent` |

**Usage:**

```powershell
# Navigate to MAUI project
bm

# Do some work...

# Go back
b-

# See where you've been
brecent
```

### 🔨 Build & Run

| Command                             | Description            | Example                             |
| ----------------------------------- | ---------------------- | ----------------------------------- |
| `Build-MAUI`                        | Build MAUI for Windows | `Build-MAUI`                        |
| `Build-MAUI -Clean`                 | Clean and build        | `Build-MAUI -Clean`                 |
| `Build-MAUI -Configuration Release` | Release build          | `Build-MAUI -Configuration Release` |
| `Run-MAUI`                          | Launch MAUI app        | `Run-MAUI`                          |
| `Start-FlaskAPI`                    | Start Flask backend    | `Start-FlaskAPI`                    |
| `Test-Evident`                      | Run all tests          | `Test-Evident`                      |

**Usage:**

```powershell
# Clean build and run
Build-MAUI -Clean
Run-MAUI

# In separate terminal: Start API
Start-FlaskAPI
```

### 📝 Git Shortcuts

| Command        | Description        | Example                         |
| -------------- | ------------------ | ------------------------------- |
| `gs`           | Git status (short) | `gs`                            |
| `gaa`          | Git add all        | `gaa`                           |
| `gc "message"` | Git commit         | `gc "fix: ChatGPT integration"` |
| `gp`           | Git push           | `gp`                            |
| `gpl`          | Git pull           | `gpl`                           |
| `gquick "msg"` | Add, commit, push  | `gquick "feat: Add chat UI"`    |

**Usage:**

```powershell
# Quick save workflow
gquick "feat: Add ChatPage UI"

# Equivalent to:
git add .
git commit -m "feat: Add ChatPage UI"
git push origin main
```

### 🗄️ Database Commands

| Command                  | Description            | Example                               |
| ------------------------ | ---------------------- | ------------------------------------- |
| `Migrate-DB`             | Run default migration  | `Migrate-DB`                          |
| `Migrate-DB "script.py"` | Run specific migration | `Migrate-DB "migrate_add_chatgpt.py"` |
| `Reset-DB`               | Delete and recreate DB | `Reset-DB`                            |

**Usage:**

```powershell
# Run ChatGPT migration
Migrate-DB "migrate_add_chatgpt.py"

# Reset everything (careful!)
Reset-DB
# Prompts: "⚠️ This will DELETE all data! Are you sure? (yes/no)"
```

### 💡 Help

| Command            | Description                   |
| ------------------ | ----------------------------- |
| `bmenu`            | Show command menu             |
| `Show-EvidentMenu` | Show command menu (full name) |

--

## Workflow Examples

### Starting Development Session

```powershell
# Navigate to MAUI project
bm

# Check git status
gs

# Pull latest changes
gpl

# Clean build
Build-MAUI -Clean

# Run app
Run-MAUI
```

### Working on Chat Feature

```powershell
# Go to MAUI
bm

# Edit ChatPage.xaml
code Views\ChatPage.xaml

# Build to check for errors
Build-MAUI

# If good, commit
gquick "feat: Add chat message list UI"
```

### Testing Full Stack

```powershell
# Terminal 1: Start Flask API
br
Start-FlaskAPI

# Terminal 2: Run MAUI app
bm
Run-MAUI

# Terminal 3: Check database
br
python -c "from models_auth import db; print(db.engine.table_names())"
```

### Database Migration Workflow

```powershell
# Go to root
br

# Check current tables
python -c "from models_auth import db, app; app.app_context().push(); print(db.engine.table_names())"

# Run migration
Migrate-DB "migrate_add_chatgpt.py"

# Verify new tables
python -c "from api.chatgpt import Project; print('✅ ChatGPT tables loaded')"
```

--

## Customization

### Change Evident Paths

Edit the `$Script:EvidentPaths` section:

```powershell
$Script:EvidentPaths = @{
    Root = "D:\Projects\Evident"  # Your path here
    MAUI = "D:\Projects\Evident\src\Evident.MatterDocket.MAUI"
    API = "D:\Projects\Evident\api"
    Tests = "D:\Projects\Evident\tests"
    Docs = "D:\Projects\Evident"
}
```

### Add Custom Commands

Add your own functions:

```powershell
function Deploy-Production {
    Write-Host "🚀 Deploying to production..." -ForegroundColor Yellow

    # Your deployment commands
    git push production main

    Write-Host "✅ Deployed!" -ForegroundColor Green
}
```

### Auto-Navigate on Start

Uncomment the last line to auto-cd to Evident on PowerShell start:

```powershell
# Auto-navigate to Evident on load
br  # Uncomment this line
```

--

## Troubleshooting

### "Cannot be loaded because running scripts is disabled"

**Solution:**

```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Commands not found after install

**Solution:**

```powershell
# Reload profile
. $PROFILE

# Or restart PowerShell
```

### Profile changes not taking effect

**Solution:**

```powershell
# Make sure you saved the file
# Reload:
. $PROFILE
```

--

## Tips & Tricks

### Use Tab Completion

```powershell
# Type and press Tab
Build-<Tab>  # Cycles through Build-MAUI, etc.
```

### Combine Commands

```powershell
# Build and run in one line
Build-MAUI && Run-MAUI

# Go to MAUI and build
bm; Build-MAUI
```

### Check Recent Locations

```powershell
# See where you've been
brecent

# Output:
# 📍 Recent Locations:
#   [0] C:\web-dev\github-repos\Evident.info
#   [1] C:\web-dev\github-repos\Evident.info\src\Evident.MatterDocket.MAUI
#   [2] C:\web-dev\github-repos\Evident.info\api
```

### Color Customization

Change colors by editing `$Script:Colors`:

```powershell
$Script:Colors = @{
    Success = "DarkGreen"  # Change to your preference
    Warning = "DarkYellow"
    Error = "DarkRed"
    Info = "DarkCyan"
    Highlight = "DarkMagenta"
}
```

--

**Installation Time:** 2 minutes  
**Commands Added:** 20+  
**Productivity Boost:** 10x faster navigation! 🚀
