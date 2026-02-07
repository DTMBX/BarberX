<#
.SYNOPSIS
  Run repository checks: pytest, ruff (if available), and basic linters.
#>
try { Write-Host "Running pytest"; & pytest -q } catch { Write-Warning "pytest not found or failed" }

try { Write-Host "Running ruff"; & ruff check . } catch { Write-Host "ruff not installed; skipping" }

Write-Host "Completed Run-Checks (some tools optional)."
