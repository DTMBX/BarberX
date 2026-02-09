@echo off
cd /d C:\web-dev\github-repos\Evident
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║         CLEANING UP 43 STALE BRANCHES FROM GITHUB                  ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

set deleted=0
set skipped=0

for /f "tokens=*" %%B in (
    'echo fix/cname copilot/fix-deploy-issues copilot/consolidate-branches-and-deploy fix/ci-stylelint-script merge/chore-ruff-f401-cleanup-allow-unrelated fix/pages-ci-robustness copilot/identify-open-source-components chore/ruff-f401-cleanup update-gemfile-lock fix/unfreeze-bundle-ci fix/pages-ci-robustness-clean fix/jekyll-ruby release/pages-ready fix/security-scan-workflow fix/stylelint-placeholders local-main-backup pr-53 feature/ci-node20-clean fix/ci-node20-workflows fix/ci-node20-all fix/ci-node20 chore/remediate-assets-links backup-before-purge backup/chore-add-tokens-core-and-ci-20260206-000000 backup/chore-add-tokens-core-and-ci-20260206-000002 backup/chore-add-tokens-core-and-ci-20260206-131414 chore/add-root-requirements chore/add-tokens-core-and-ci chore/add-tokens-core-and-ci-merged-assets chore/add-tokens-core-and-ci-reconciled chore/format-tests feature/workflows-fixes chore/repo-layout chore/site-ci-readme chore/site-dev-hooks ci/auto-workflow-automation copilot-worktree-2026-02-06T20-42-56 DTMBX-patch-2 feature/css-media-lint feature/pages-jekyll-fix') do (
    echo Deleting: %%B
    gh api -X DELETE repos/evident-technologies/Evident/git/refs/heads/%%B >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [DELETED]
        set /a deleted=!deleted!+1
    ) else (
        echo   [SKIPPED - already deleted]
        set /a skipped=!skipped!+1
    )
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Summary:
echo   Deleted: %deleted%
echo   Skipped: %skipped%
echo.
echo Pruning local references...
git fetch origin --prune >nul 2>&1
echo.
echo Remaining branches:
git branch -r
echo.
echo ✓ Cleanup complete!
echo.
pause
