# Move non-conflicting files from site/assets into assets/
$src = Join-Path (Get-Location) 'site\assets'
$destRoot = Join-Path (Get-Location) 'assets'
if (-not (Test-Path $src)) { Write-Host "Source not found: $src"; exit 0 }
$files = Get-ChildItem -Path $src -Recurse -File
foreach ($f in $files) {
    $rel = $f.FullName.Substring($src.Length).TrimStart('\')
    $target = Join-Path $destRoot $rel
    $targetDir = Split-Path $target -Parent
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }
    if (-not (Test-Path $target)) {
        Write-Host "mv: $rel"
        git mv $f.FullName $target
    } else {
        Write-Host "skip exists: $rel"
    }
}
