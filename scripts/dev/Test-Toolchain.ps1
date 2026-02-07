<#
.SYNOPSIS
  Quick checks for required tools: python, pip, ffmpeg, git, and required env vars.
#>
Write-Host "Testing toolchain..."

function Check-Cmd($cmd, $args = '--version') {
    try {
        & $cmd $args 2>$null | Out-Null
        return $true
    } catch { return $false }
}

$checks = @{
    'python' = $false
    'pip' = $false
    'git' = $false
    'ffmpeg' = $false
}

foreach ($k in $checks.Keys) {
    $ok = Check-Cmd -cmd $k
    $checks[$k] = $ok
    Write-Host "$k : $ok"
}

# Check env vars (names only, do not print values)
$requiredEnv = @('COURTLISTENER_API_KEY')
$missing = @()
foreach ($envName in $requiredEnv) {
    if (-not $env:$envName) { $missing += $envName }
}

if ($missing.Count -gt 0) {
    Write-Warning "Missing required environment variables: $($missing -join ', ')"
} else {
    Write-Host "Required environment variables present (names checked)."
}

Write-Host "Toolchain check complete."
