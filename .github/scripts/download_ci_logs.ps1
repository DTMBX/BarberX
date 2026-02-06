# Download CI logs for PR head commit and save under .github/actions-logs
$ErrorActionPreference = 'Stop'
$owner = 'DTMBX'
$repo = 'Evident'
$pr = 50
$outdir = '.github/actions-logs'
if (-not (Test-Path $outdir)) { New-Item -ItemType Directory -Path $outdir | Out-Null }

$sha = gh pr view $pr --repo "$owner/$repo" --json headRefOid -q '.headRefOid' 2>$null
if (-not $sha) { Write-Output '[error] Unable to determine PR head SHA'; exit 1 }
Write-Output "PR #$pr head SHA: $sha"

$apiJson = gh api repos/$owner/$repo/actions/runs?per_page=200 2>$null
if (-not $apiJson) { Write-Output '[error] Unable to list workflow runs'; exit 1 }
$api = $apiJson | ConvertFrom-Json
$runs = @()
if ($api.workflow_runs) { foreach ($r in $api.workflow_runs) { if ($r.head_sha -eq $sha) { $runs += $r } } }
if ($runs.Count -eq 0) { Write-Output 'No workflow runs found for this commit.'; exit 0 }

Write-Output "Found $($runs.Count) workflow run(s) for the PR commit. Listing summary..."
$failCount = 0
foreach ($run in $runs) {
    $id = $run.id
    $name = $run.name
    $status = $run.status
    $conclusion = $run.conclusion
    $url = $run.html_url
    Write-Output "- Run: $name (id:$id) status:$status conclusion:$conclusion url:$url"
    if ($conclusion -ne 'success' -and $conclusion -ne 'skipped') {
        $failCount++
        $dir = Join-Path $outdir "run-$id"
        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
        Write-Output "  -> Downloading logs for run id $id to $dir"
        # `gh run download` on some GH CLI versions doesn't support a --log flag; use `gh run view --log` and save to file
        $logFile = Join-Path $dir "run-$id-log.txt"
        Write-Output "    Saving combined run logs to $logFile"
        try {
            gh run view $id --repo $owner/$repo --log 2>&1 | Out-File -FilePath $logFile -Encoding utf8
        } catch {
            Write-Output ("    Error: failed to download logs for run {0}: {1}" -f $id, $_.Exception.Message)
            # continue to next run
        }
        Write-Output "  -> Listing downloaded files:"
        Get-ChildItem -Recurse -File $dir | ForEach-Object { Write-Output "    $($_.FullName)" }
    }
}
Write-Output "Download complete. $failCount failing/unstable run(s) downloaded to $outdir."