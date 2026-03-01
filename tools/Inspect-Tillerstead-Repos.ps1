param(
    [string]$Root = "C:\barber-cam\public",
    [string]$ReportDir = "C:\barber-cam\public\reports"
)

New-Item -ItemType Directory -Force $ReportDir | Out-Null
$timestamp = Get-Date -Format yyyyMMdd_HHmmss
$report = Join-Path $ReportDir "tillerstead-repo-audit_$timestamp.txt"

"== TILLERSTEAD REPO AUDIT ==" | Out-File $report
"Root: $Root" | Out-File $report -Append
"Timestamp: $(Get-Date)" | Out-File $report -Append
"" | Out-File $report -Append

if (-not (Test-Path $Root)) {
    Write-Host "Root directory does not exist: $Root" -ForegroundColor Red
    exit 1
}

Get-ChildItem $Root -Directory -Filter "tillerstead*" | ForEach-Object {

    $path = $_.FullName
    $name = $_.Name

    "--------------------------------------------------" | Out-File $report -Append
    "Repo: $name" | Out-File $report -Append
    "Path: $path" | Out-File $report -Append

    if (-not (Test-Path (Join-Path $path ".git"))) {
        "❌ Not a git repository" | Out-File $report -Append
        return
    }

    Push-Location $path

    try {
        $branch = git branch --show-current 2>$null
        $head   = git rev-parse --short HEAD 2>$null
        $dirty  = if (git status --porcelain) { "DIRTY" } else { "CLEAN" }

        "Branch: $branch" | Out-File $report -Append
        "HEAD:   $head"   | Out-File $report -Append
        "Status: $dirty"  | Out-File $report -Append

        "" | Out-File $report -Append
        "Branches:" | Out-File $report -Append
        git branch -a | Out-File $report -Append

        "" | Out-File $report -Append
        "Build signals:" | Out-File $report -Append
        "  _config.yml : $(Test-Path _config.yml)" | Out-File $report -Append
        "  Gemfile     : $(Test-Path Gemfile)"     | Out-File $report -Append
        "  tools/      : $(Test-Path tools)"       | Out-File $report -Append
        "  dist/       : $(Test-Path dist)"        | Out-File $report -Append
        "  _site/      : $(Test-Path _site)"       | Out-File $report -Append

        if ($name -match "__backup|FINALKEEP") {
            "⚠️  Marked as BACKUP/ARCHIVE" | Out-File $report -Append
        } else {
            "✅ Candidate for canonical repo" | Out-File $report -Append
        }
    } catch {
        Write-Host "Error processing repo: $name" -ForegroundColor Yellow
        Write-Host $_.Exception.Message -ForegroundColor Red
    } finally {
        Pop-Location
    }

    "" | Out-File $report -Append
}

"== END OF AUDIT ==" | Out-File $report -Append

Write-Host "Audit complete:"
Write-Host $report
