<#
.SYNOPSIS
  Activate repo-local Python venv and show a repo-aware prompt.

USAGE
  Run this when you cd into the repo, or add the small user profile snippet in docs/dev-shell.md
#>
param(
  [string]$RepoRoot = $(Split-Path -Path $PSScriptRoot -Parent -Parent)
)

Write-Host "Entering repo: $RepoRoot"

$profileFile = Join-Path $RepoRoot '.repo-profile.json'
if (-Not (Test-Path $profileFile)) {
    Write-Warning "No .repo-profile.json found in repo root. Skipping venv activation."
    return
}

try {
    $profile = Get-Content $profileFile | ConvertFrom-Json
} catch {
    Write-Warning "Failed to read .repo-profile.json: $_"
    return
}

$venvRelative = $profile.venv_path
if (-not $venvRelative) { Write-Warning "No venv_path in .repo-profile.json"; return }

$venvPath = Resolve-Path -Path (Join-Path $RepoRoot $venvRelative) -ErrorAction SilentlyContinue
if (-not $venvPath) {
    Write-Warning "Virtual environment not found at $venvRelative. Use .\scripts\dev\Test-Toolchain.ps1 to diagnose."
    return
}

# Activate venv
& "$($venvPath.Path)\Scripts\Activate.ps1"

# Prompt customization (non-destructive: store previous prompt)
if (-not (Get-Variable -Name __RepoPromptOriginal -Scope Global -ErrorAction SilentlyContinue)) {
    Set-Variable -Name __RepoPromptOriginal -Value (Get-Command prompt).ScriptBlock -Scope Global
}

function global:prompt {
    $branch = ''
    try { $branch = (git rev-parse --abbrev-ref HEAD 2>$null).Trim() } catch {}
    $venvName = Split-Path $venvPath -Leaf
    $label = if ($profile.prompt_label) { $profile.prompt_label } else { 'Evident' }
    "$label[$branch][$venvName] PS> "
}

Write-Host "Activated venv at: $($venvPath.Path)" -ForegroundColor Green
