<#
.SYNOPSIS
  Deactivate repo-local Python venv and restore prompt.
#>
param()

if (Get-Variable -Name VIRTUAL_ENV -Scope Global -ErrorAction SilentlyContinue) {
    try { deactivate } catch {}
}

if (Get-Variable -Name __RepoPromptOriginal -Scope Global -ErrorAction SilentlyContinue) {
    $orig = Get-Variable -Name __RepoPromptOriginal -Scope Global -ValueOnly
    Set-Item -Path Function:prompt -Value $orig
    Remove-Variable -Name __RepoPromptOriginal -Scope Global
}

Write-Host "Exited repo and restored prompt." -ForegroundColor Yellow
