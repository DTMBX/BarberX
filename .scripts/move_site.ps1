# Move non-conflicting files from site/ to repo root
$items = Get-ChildItem -Force site
foreach ($i in $items) {
    $name = $i.Name
    if ($name -in @('_config.yml','_layouts','_includes','.jekyll-cache')) {
        Write-Host "skip exclude: $name"
        continue
    }
    if (-not (Test-Path $name)) {
        Write-Host "mv: $name"
        git mv $i.FullName $name
    } else {
        Write-Host "skip exists: $name"
    }
}
