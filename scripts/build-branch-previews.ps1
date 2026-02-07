param(
    [string]$RemoteMain = 'origin/main'
)

Write-Host "Fetching from origin..."
git fetch origin --prune

$merged = git branch -r --merged $RemoteMain | ForEach-Object { $_ -replace '^\s+' , '' } | Where-Object { ($_ -notmatch '->') -and ($_ -notmatch 'origin/HEAD') -and ($_ -ne 'origin/main') }
if (-not $merged) {
    Write-Host 'No merged remote branches found.'
    exit 0
}

if (-not (Test-Path builds)) { New-Item -ItemType Directory -Path builds | Out-Null }

foreach ($b in $merged) {
    $ref = $b -replace '^\s+' , ''
    $remoteName = $ref -replace '^origin/' , ''
    $safe = $remoteName -replace '/' , '--'
    Write-Host "\n=== Processing $ref -> $safe ==="

    # create/update a preview branch pointing at the remote ref
    git branch -f "preview/$safe" $ref
    git checkout "preview/$safe"

    if (-not (Test-Path node_modules)) {
        Write-Host 'Installing dependencies (npm ci)...'
        npm ci
    } else {
        Write-Host 'Re-using existing node_modules'
    }

    # Merge latest main into preview branch so local improvements (like flag-video) are included
    Write-Host "Merging main into preview/$safe"
    git merge --no-edit main
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'Merge resulted in conflicts or failed; aborting merge and continuing build of branch state.'
        git merge --abort 2>$null
    }

    Write-Host 'Running npm run build'
    npm run build

    $dest = Join-Path 'builds' $safe
    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    New-Item -ItemType Directory -Path $dest | Out-Null
    Copy-Item -Path "_site\*" -Destination $dest -Recurse -Force
    Write-Host "Copied _site to $dest"
}

# Write index
$indexPath = Join-Path 'builds' 'index.html'
$html = @'
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Branch Previews</title>
</head>
<body>
  <h1>Branch Previews</h1>
  <ul>
'@

Get-ChildItem -Directory builds | ForEach-Object { if ($_.Name -ne 'node_modules') { $html += "    <li><a href='$($_.Name)/'>$($_.Name)</a></li>`n" } }
$html += "  </ul>`n</body>`n</html>`n"

Set-Content -Path $indexPath -Value $html -Encoding UTF8
Write-Host "Wrote $indexPath"

git checkout main | Out-Null
Write-Host 'Restored main branch'
