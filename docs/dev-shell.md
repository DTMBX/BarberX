## Repo-local dev shell (non-invasive)

This document explains how to enable a repo-local PowerShell helper that activates the repo `.venv` and shows a repo-aware prompt when you enter the repository directory.

Files added:

- `scripts/dev/Enter-Repo.ps1` — activate venv & set prompt
- `scripts/dev/Exit-Repo.ps1` — deactivate & restore prompt
- `scripts/dev/Test-Toolchain.ps1` — quick checks for python/ffmpeg/git
- `.repo-profile.json` — repo marker describing venv path and label
- `.env.example` — example env var names (no secrets)

Non-invasive install (recommended)

1. Create a small PowerShell profile on your machine (one-time):
   - Open `C:\Users\<you>\Documents\PowerShell\Microsoft.PowerShell_profile.ps1` (create if missing).
   - Add this snippet (it only activates within repos containing `.repo-profile.json`):

```powershell
# Repo-aware activation snippet — paste into your user profile
function Invoke-Repo-Profile {
    $cwd = Get-Location
    $root = $cwd.Path
    while ($root -ne [System.IO.Path]::GetPathRoot($root)) {
        if (Test-Path (Join-Path $root '.repo-profile.json')) {
            & (Join-Path $root 'scripts\dev\Enter-Repo.ps1')
            return
        }
        $root = Split-Path $root -Parent
    }
}

# Optionally call this function from your prompt or run it manually after cd
```

2. Enter the repo folder and run the script `scripts\dev\Enter-Repo.ps1` (or rely on your profile snippet).

Disable

Remove the snippet from your personal profile file to stop automatic activation.

Security & behavior

- This is non-invasive and does not edit global system profiles by itself.
- It only reads `.repo-profile.json` from repo root and activates the referenced `.venv`.
