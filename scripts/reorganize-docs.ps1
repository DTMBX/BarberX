# Documentation Reorganization Script
# Safely reorganize tillerstead-stone documentation per DOCUMENTATION_AUDIT.md
# Reference: .ai/SYSTEM.md governance standards

param(
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"
$root = "C:\Users\Devon Tyler\tillerstead-stone"
$reportsDir = Join-Path $root "reports"
$docsDir = Join-Path $root "docs"

Write-Host "=== Tillerstead Documentation Reorganization ===" -ForegroundColor Cyan
Write-Host "Root: $root" -ForegroundColor Gray
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN MODE - No files will be modified" -ForegroundColor Yellow
    Write-Host ""
}

# Create new directory structure
$newDirs = @(
    "docs\guides",
    "docs\design",
    "docs\operations"
)

Write-Host "Creating directory structure..." -ForegroundColor Green
foreach ($dir in $newDirs) {
    $fullPath = Join-Path $root $dir
    if (-not (Test-Path $fullPath)) {
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        }
        Write-Host "  ✓ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  • Exists: $dir" -ForegroundColor Gray
    }
}
Write-Host ""

# FILES TO MOVE
$filesToMove = @{
    # Active reference guides
    "CSS-ARCHITECTURE.md" = "docs\guides\CSS-ARCHITECTURE.md"
    "WCAG-CONTRAST-SYSTEM.md" = "docs\guides\ACCESSIBILITY.md"
    "ICON_SYSTEM.md" = "docs\guides\ICON-SYSTEM.md"
    "SCRIPTS_GUIDE.md" = "docs\SCRIPTS.md"
    "RELEASE-CHECKLIST.md" = "docs\RELEASE-CHECKLIST.md"
    "QUICK_REFERENCE.md" = "docs\QUICK-REFERENCE.md"
    "QUICK_REFERENCE_CARD.md" = "docs\QUICK-START.md"
    
    # Design system
    "TILE-PATTERN-REFERENCE.md" = "docs\design\TILE-PATTERNS.md"
    "FOOTER-PATTERN-REFERENCE.md" = "docs\design\FOOTER-PATTERNS.md"
    "ICON_PLACEMENT_GUIDE.md" = "docs\design\ICON-PLACEMENT.md"
    "ICON_DESIGN_SUMMARY.md" = "docs\design\ICONS.md"
    
    # Operations
    "REVIEWS-MANAGEMENT.md" = "docs\operations\REVIEWS.md"
    "email-drip-campaign-templates.md" = "docs\operations\EMAIL-CAMPAIGNS.md"
    "tillerstead-work-assets.md" = "docs\operations\ASSETS.md"
}

Write-Host "Moving active documentation files..." -ForegroundColor Green
$moveCount = 0
foreach ($file in $filesToMove.Keys) {
    $source = Join-Path $reportsDir $file
    $dest = Join-Path $root $filesToMove[$file]
    
    if (Test-Path $source) {
        if (-not $DryRun) {
            Move-Item -Path $source -Destination $dest -Force
        }
        Write-Host "  ✓ Moved: $file → $($filesToMove[$file])" -ForegroundColor Green
        $moveCount++
    } else {
        Write-Host "  ⚠ Not found: $file" -ForegroundColor Yellow
    }
}
Write-Host "  Total moved: $moveCount files" -ForegroundColor Cyan
Write-Host ""

# FILES TO DELETE - Obsolete deployment logs
$deleteDeployment = @(
    "CICD_WORKFLOW_FIXES.md",
    "DEPLOYMENT_COMPLETE.md",
    "DEPLOYMENT_EXECUTION_LOG.md",
    "DEPLOYMENT_FIX_SUMMARY.md",
    "FINAL_PRODUCTION_VERIFICATION.md",
    "GITHUB_ACTIONS_COMPLETE.md",
    "GITHUB_ACTIONS_DEBUG_SUMMARY.md",
    "GITHUB_ACTIONS_DEPLOYMENT_COMPLETE.md",
    "GITHUB_ACTIONS_FIX_PLAN.md",
    "GITHUB_ACTIONS_FIX_REPORT.md",
    "GITHUB_ACTIONS_QUICK_FIX.md",
    "GITHUB_PAGES_DEPLOYMENT_FIX.md",
    "NODE24_UPGRADE_REPORT.md",
    "POST_DEPLOYMENT_VERIFICATION.md",
    "TILLERSTEAD_DEPLOYMENT_SAFETY.md",
    "TILLERSTEAD_DEPLOYMENT_STATUS.md",
    "PRODUCTION_REMEDIATION_REPORT.md",
    "COMPREHENSIVE_VERIFICATION_COMPLETE.md"
)

# FILES TO DELETE - Debug/fix logs
$deleteDebug = @(
    "nav-debug.md",
    "NAV_DIAGNOSTIC_REPORT.md",
    "MOBILE_NAV_VERIFICATION.md",
    "DIAGNOSTIC_SUMMARY.md",
    "ROOT-CAUSE-ANALYSIS.md",
    "REPO_STRUCTURE_ISSUE.md",
    "TILLERSTEAD_404_COMPREHENSIVE_FIX.md",
    "TILLERSTEAD_404_ROOT_CAUSE_ANALYSIS.md",
    "FOOTER_CROSSHATCH_FIX.md",
    "FOOTER_CROSSHATCH_QUICK_FIX.md",
    "CONTRAST-FIX-SUMMARY.md",
    "PORTFOLIO_IMAGE_FIX_PLAN.md"
)

# FILES TO DELETE - Duplicate/superseded
$deleteDuplicate = @(
    ".AI_GOVERNANCE.md",
    "AI-GOVERNANCE-IMPLEMENTATION.md",
    "AI-INSTRUCTION-ORGANIZATION.md",
    "AI_PROJECT_INSTRUCTIONS.md",
    "GOVERNANCE_COMPLIANCE_AUDIT.md",
    "GOVERNANCE_COMPLIANCE_CHECKLIST.md",
    "FULL_COMPLIANCE_CERTIFICATION.md"
)

# FILES TO DELETE - Completed refactors
$deleteRefactor = @(
    "REFACTOR_MARATHON.md",
    "REFACTOR-COMPLETION-REPORT.md",
    "CSS-MODERNIZATION.md",
    "GIT-COMMIT-CSS-MODERNIZATION.md",
    "GIT-COMMIT-GUIDE-VOICE-REFACTOR.md",
    "VOICE-CONVERSION-STANDARD.md",
    "REMEDIATION_COMPLETE.md",
    "OPTIMIZATION-COMPLETE.md",
    "QUALITY_ASSURANCE_SUMMARY.md",
    "HOMEPAGE_OPTIMIZATION_REPORT.md",
    "ts-include-scss-audit.md"
)

# FILES TO DELETE - Design experiments
$deleteDesign = @(
    "90S-DESIGN-GUIDE.md",
    "CARTOON-DESIGN-GUIDE.md",
    "HYBRID-DESIGN-IMPLEMENTATION.md",
    "OPTIMIZATION-FUN-PLAN.md",
    "CONVERSION-OPTIMIZATION-PLAN.md"
)

# FILES TO DELETE - Status/index
$deleteStatus = @(
    "STATUS.md",
    "WEB_DEV_STATUS.md",
    "WEB_DEV_AUDIT.md",
    "GITHUB_ACTIONS_INDEX.md",
    "TILLERSTEAD_EXECUTIVE_SUMMARY.md"
)

# FILES TO DELETE - Copilot iterations
$deleteCopilot = @(
    "COPILOT.md",
    "COPILOT_STONE_PROD_FIX.md",
    "PLAN.md",
    "IMPLEMENTATION_GUIDE.md"
)

# FILES TO DELETE - Evaluate workflow (likely redundant)
$deleteWorkflow = @(
    "WORKFLOW.md"
)

# Combine all delete lists
$allDeletes = $deleteDeployment + $deleteDebug + $deleteDuplicate + $deleteRefactor + $deleteDesign + $deleteStatus + $deleteCopilot + $deleteWorkflow

Write-Host "Deleting obsolete files..." -ForegroundColor Green
$deleteCount = 0
foreach ($file in $allDeletes) {
    $filePath = Join-Path $reportsDir $file
    if (Test-Path $filePath) {
        if (-not $DryRun) {
            Remove-Item -Path $filePath -Force
        }
        Write-Host "  ✓ Deleted: $file" -ForegroundColor DarkGray
        $deleteCount++
    }
}
Write-Host "  Total deleted: $deleteCount files" -ForegroundColor Cyan
Write-Host ""

# VERIFY KEPT FILES
$keepFiles = @(
    "HOMEPAGE_COMPLIANCE_AUDIT.md",
    "HOMEPAGE_DESIGN_FIXES.md",
    "FOOTER_AND_PATTERNS_AUDIT.md",
    "IMAGE_AUDIT_REPORT.md"
)

Write-Host "Verifying kept audit files in reports/..." -ForegroundColor Green
$keepCount = 0
foreach ($file in $keepFiles) {
    $filePath = Join-Path $reportsDir $file
    if (Test-Path $filePath) {
        Write-Host "  ✓ Kept: $file" -ForegroundColor Green
        $keepCount++
    } else {
        Write-Host "  ⚠ Missing: $file" -ForegroundColor Yellow
    }
}
Write-Host "  Total kept in reports/: $keepCount files" -ForegroundColor Cyan
Write-Host ""

# SUMMARY
Write-Host "=== Reorganization Summary ===" -ForegroundColor Cyan
Write-Host "  Files moved to docs/: $moveCount" -ForegroundColor Green
Write-Host "  Files deleted: $deleteCount" -ForegroundColor DarkGray
Write-Host "  Files kept in reports/: $keepCount" -ForegroundColor Green
Write-Host "  Total files processed: $($moveCount + $deleteCount + $keepCount)" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN COMPLETE - Run without -DryRun to execute" -ForegroundColor Yellow
} else {
    Write-Host "REORGANIZATION COMPLETE ✓" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Review changes: git status" -ForegroundColor Gray
    Write-Host "  2. Test build: npm run build" -ForegroundColor Gray
    Write-Host "  3. Commit: git add -A && git commit -m 'docs: reorganize documentation structure'" -ForegroundColor Gray
}
