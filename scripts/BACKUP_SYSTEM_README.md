# Automatic Daily Git Backup System

## 🎯 Purpose

Automatically creates dated backups of the Tillerstead.com repository at the end of each day **only if there are changes**. This protects against accidental data loss while keeping a clean history of daily work.

## 📁 How It Works

### Backup Location (Industry Standard)
- **Location:** `C:\web-dev\github-repos\tillerstead-backups\`
- **Outside repository:** Backups are stored in parent directory (not in working tree)
- **Benefits:** 
  - No gitignore needed
  - Faster git operations
  - Cleaner workspace
  - Industry best practice

### Backup Folder Naming
- Format: `YYYY-MM-DD`
- Example: `2026-01-21`
- Full path: `C:\web-dev\github-repos\tillerstead-backups\2026-01-21\`

### Automatic Triggers
Backups are created when:
- ✅ Uncommitted changes exist (modified, new, or deleted files)
- ✅ Unpushed commits exist (local commits not yet pushed to remote)
- ⏰ Runs daily at 11:59 PM (configurable)

### What Gets Backed Up
**Everything EXCEPT:**
- `.git/` (git database)
- `node_modules/` (npm packages)
- `_site/` (Jekyll build output)
- `.venv/` (Python virtual environment)
- `__pycache__/`, `*.pyc` (Python cache)
- `.pytest_cache/`, `test-results/`, `playwright-report/` (test artifacts)
- `.env`, `.env.local` (environment files)
- Log files, OS temp files

## 🚀 Quick Start

### Option 1: Setup Automatic Daily Backups (Recommended)

Run the setup script (will auto-elevate to Administrator):

```powershell
cd C:\web-dev\github-repos\Tillerstead.com
.\scripts\setup-daily-backup-task.ps1
```

The script will automatically request Administrator privileges if needed.

This creates a Windows Task Scheduler task that runs automatically at 11:59 PM every day.

### Option 2: Manual Backup

Run the backup script manually anytime:

```powershell
# Normal backup (only if changes detected)
.\scripts\auto-backup-daily.ps1

# Force backup even if no changes
.\scripts\auto-backup-daily.ps1 -Force
```

## 📋 Features

### Smart Change Detection
- Checks git status for uncommitted changes
- Checks for unpushed commits
- Skips backup if no changes (saves disk space)
- Force flag available for manual backups

### Automatic Cleanup
- Keeps last **7 daily backups**
- Automatically removes older backups
- Prevents disk space bloat

### Backup Metadata
Each backup includes `_BACKUP_INFO.json` with:
- Backup date and time
- Git branch name
- Git commit hash
- Git status (changed files)
- Backup reason (automatic or manual)

### Efficient Copying
- Uses Windows `robocopy` for fast, reliable copying
- Excludes unnecessary files
- Preserves directory structure
- Handles large repositories efficiently

## 🗂️ Example Backup Structure

```
github-repos/
├── Tillerstead.com/           # Your working repository
│   ├── _config.yml
│   ├── index.md
│   ├── _includes/
│   ├── _layouts/
│   ├── assets/
│   └── scripts/
│       ├── auto-backup-daily.ps1
│       └── setup-daily-backup-task.ps1
│
└── tillerstead-backups/       # Backup directory (outside repo)
    ├── 2026-01-14/            # 7 days ago
    ├── 2026-01-15/            # 6 days ago
    ├── 2026-01-16/            # 5 days ago
    ├── 2026-01-17/            # 4 days ago
    ├── 2026-01-18/            # 3 days ago
    ├── 2026-01-19/            # 2 days ago
    ├── 2026-01-20/            # Yesterday
    └── 2026-01-21/            # Today (latest)
        ├── _BACKUP_INFO.json  # Metadata
        ├── _config.yml
        ├── index.md
        ├── _includes/
 tillerstead-backups/── _layouts/
        ├── assets/
        └── ... (all repo files)
```

## 📊 Backup Info Example

`_backup-2026-01-21/_BACKUP_INFO.json`:
```json
{
  "backup_date": "2026-01-21 23:59:01",
  "source_repo": "C:\\web-dev\\github-repos\\Tillerstead.com",
  "git_branch": "main",
  "git_commit": "a1b2c3d4e5f6...",
  "git_status": "M  _includes/navigation/nav.html\nA  assets/css/new-feature.css",
  "backup_reason": "Automatic backup - changes detected",
  "created_by": "auto-backup-daily.ps1"
}
```

## 🛠️ Configuration

### Change Backup Time

Edit the setup script:
```powershell
.\scripts\setup-daily-backup-task.ps1 -BackupTime "22:00"  # 10 PM
```

### Change Retention Period

Edit `auto-backup-daily.ps1` line ~180:
```powershell
# Change from 7 to desired number of days
Select-Object -Skip 7    # Change this number
```

### Customize Exclusions

Edit `auto-backup-daily.ps1` line ~80:
```powershell
$excludePatterns = @(
    '.git',
    'node_modules',
    # Add more patterns here...
)
```

## 🔍 Verify Task Scheduler

1. Press `Win + R`
2. Type `taskschd.msc`
3. Look for: **Tillerstead Daily Git Backup**
4. Right-click → Properties to see configuration

## ⚡ Manual Task Scheduler Setup

If you prefer to set it up manually:

1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task
   - Name: `Tillerstead Daily Git Backup`
   - Trigger: Daily at 11:59 PM
   - Action: Start a program
   - Program: `PowerShell.exe`
   - Arguments: `-NoProfile -ExecutionPolicy Bypass -File "C:\web-dev\github-repos\Tillerstead.com\scripts\auto-backup-daily.ps1"`
   - Start in: `C:\web-dev\github-repos\Tillerstead.com`

## 🧪 Testing

Test the backup system:

```powershell
# Test with current changes
.\scripts\auto-backup-daily.ps1

# Test with force flag
.\scripts\auto-backup-daily.ps1 -Force

# Verify backup was created
dir _backup-* | Sort-Object Name -Descending | Select-Object -First 1
```

## 📝 Output Example

```
ℹ️  Repository: C:\web-dev\github-repos\Tillerstead.com
ℹ️  Backup folder: _backup-2026-01-21
ℹ️  Uncommitted changes detected:
  M  _includes/navigation/nav.html
  A  assets/css/new-feature.css
ℹ️  Creating backup...
ℹ️  Copying files (this may take a moment)...
✅ Backup created successfully!
ℹ️  Location: C:\web-dev\github-repos\Tillerstead.com\_backup-2026-01-21
ℹ️  Size: 45.32 MB
ℹ️  Files: 1,247
ℹ️  Checking for old backups...
⚠️  Removing old backups (keeping last 7 days):
  Removing: 2026-01-14
✅ Cleaned up 1 old backup(s)

✅ === Backup Complete ===
Backup folder: _backup-2026-01-21
Total size: 45.32 MB
Created: 2026-01-21 23:59:01
```

## 🚨 Troubleshooting

### Backup Not Running Automatically
1. Check Task Scheduler: `taskschd.msc`
2. Verify task exists and is enabled
3. Check "Last Run Result" (should be 0x0 for success)
4. View task history in Task Scheduler

### No Backup Created
- **Expected:** No changes detected since last backup
- Run with `-Force` to create backup anyway

### Backup Failed
- Check disk space (backups ~40-50 MB each)
- Verify PowerShell execution policy: `Get-ExecutionPolicy`
- Check permissions on repository folder

### Old Backups Not Deleted
- Manually remove: `Remove-Item ..\tillerstead-backups\YYYY-MM-DD -Recurse -Force`
- Check script line ~180 for retention setting

## 🔒 Security Notes

- Backups are **local only** (not synced to git)
- Stored **outside repository** (industry best practice)
- `.env` files are excluded from backups
- Backups contain full repository state (unencrypted)
- Located at: `C:\web-dev\github-repos\tillerstead-backups\`

## 📦 Git Integration

Backups are stored **outside the repository**, so no gitignore configuration needed!

Location: `..\tillerstead-backups\` (parent directory of repository)

This prevents any possibility of accidentally committing large backup folders to git.

## 🎯 Use Cases

### Restore from Backup
```powershell
# Copy specific file from backup
Copy-Item ..\tillerstead-backups\2026-01-20\path\to\file.html .

# Restore entire folder
Copy-Item ..\tillerstead-backups\2026-01-20\_includes\_includes -Recurse -Force

# Compare current vs backup
code --diff ..\tillerstead-backups\2026-01-20\file.html file.html
```

### Find When File Changed
```powershell
# Search all backups for a file
Get-ChildItem ..\tillerstead-backups\*\path\to\file.html

# Compare across backups
fc ..\tillerstead-backups\2026-01-19\file.html ..\tillerstead-backups\2026-01-20\file.html
```

### Recover Deleted File
```powershell
# Find in latest backup
Get-ChildItem ..\tillerstead-backups -Recurse -Filter "deleted-file.html" | 
    Sort-Object DirectoryName -Descending | 
    Select-Object -First 1
```

## 📞 Support

If you encounter issues:
1. Check logs in Task Scheduler History
2. Run script manually to see errors
3. Verify PowerShell version: `$PSVersionTable`
4. Contact: Tillerstead LLC

---

**Created:** January 21, 2026  
**Version:** 1.0  
**Tillerstead.com** - Automated Repository Protection
