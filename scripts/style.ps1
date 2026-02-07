Param()
$ErrorActionPreference = 'Stop'

Write-Host '== Python (ruff) =='
try {
    if (Test-Path "backend/requirements-dev.txt") {
        Write-Host 'Installing backend dev requirements (ruff)'
        python -m pip install -r backend/requirements-dev.txt
    } else {
        python -m pip install ruff
    }
    python -m ruff format .
    python -m ruff check .
} catch {
    Write-Host 'ruff not available or failed; install with: python -m pip install -r backend/requirements-dev.txt' -ForegroundColor Yellow
}

if (Test-Path "package.json") {
    Write-Host '== Node (prettier) =='
    try {
        npm run format
    } catch {
        Write-Host 'npm/Prettier not available or failed; run npm ci then npm run format' -ForegroundColor Yellow
    }
}

Write-Host '== Markdown lint (if installed) =='
try {
    npx markdownlint "**/*.md" || true
} catch {
    Write-Host 'markdownlint not available; skip' -ForegroundColor Yellow
}

Write-Host '== Done =='
