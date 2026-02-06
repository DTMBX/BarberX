$patterns = @('assets/*','site/*','docs/*','_includes/*','_layouts/*','_config.yml','Gemfile','.github/workflows/*')
$u = git diff --name-only --diff-filter=U
if (-not $u) { Write-Host "No unmerged files"; exit 0 }
$u | ForEach-Object {
    $f = $_.Trim()
    foreach ($p in $patterns) {
        if ($f -like $p) {
            Write-Host "Accepting ours for: $f"
            git checkout --ours -- "$f"
            git add "$f"
            break
        }
    }
}
# Stage any remaining resolved files
git add -A
