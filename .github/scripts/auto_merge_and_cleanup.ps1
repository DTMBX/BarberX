# Auto merge watcher: waits for PR checks to succeed, merges PR, then deletes remote branches except `main`
$ErrorActionPreference = 'Stop'
$owner = 'DTMBX'
$repo = 'Evident'
$pr = 50

function Get-HeadSha {
    $out = gh pr view $pr --repo "$owner/$repo" --json headRefOid -q '.headRefOid' 2>$null
    return $out.Trim()
}

function All-Checks-Success($sha) {
    if (-not $sha) { return $false }
    $respJson = gh api repos/$owner/$repo/commits/$sha/check-runs 2>$null
    if (-not $respJson) { return $false }
    $resp = $respJson | ConvertFrom-Json
    if (-not $resp.check_runs) { return $false }
    foreach ($c in $resp.check_runs) {
        if ($c.status -ne 'completed') { return $false }
        if ($c.conclusion -ne 'success' -and $c.conclusion -ne 'skipped') { return $false }
    }
    return $true
}

$sha = Get-HeadSha
if (-not $sha) { Write-Output "[watcher] Unable to get PR head SHA; aborting."; exit 1 }
Write-Output "[watcher] Monitoring checks for commit $sha..."
while ($true) {
    try {
        if (All-Checks-Success $sha) { break }
        Write-Output "[watcher] Checks not ready yet; sleeping 60s..."
    } catch {
        Write-Output "[watcher] Error querying checks: $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 60
}
Write-Output "[watcher] All checks succeeded or skipped. Merging PR #$pr..."
$merge = gh pr merge $pr --repo "$owner/$repo" --merge --delete-branch --yes 2>&1
Write-Output "[watcher] Merge output:`n$merge"

Write-Output "[watcher] Listing remote branches..."
$branches = git ls-remote --heads origin | ForEach-Object { ($_ -split "\t")[1].Replace('refs/heads/','') } | Where-Object { $_ -ne 'main' }
foreach ($b in $branches) {
    Write-Output "[watcher] Deleting remote branch: $b"
    $out = git push origin --delete $b 2>&1
    Write-Output $out
}
Write-Output "[watcher] Branch cleanup complete."
Write-Output "Done"