<#
Runs the routine checks mentioned in the audit memo so the commands execute in a reliable order.
Usage example:
  powershell -ExecutionPolicy Bypass -File scripts/run-quality.ps1
#>

param ()

$ErrorActionPreference = 'Stop'

Write-Host '1/4 Passing SCSS lint…' -ForegroundColor Cyan
npm run lint:css

Write-Host '2/4 Running full lint suite…' -ForegroundColor Cyan
npm run lint

Write-Host '3/4 Executing automated tests…' -ForegroundColor Cyan
npm run test

Write-Host '4/4 Rebuilding site artifacts…' -ForegroundColor Cyan
npm run build

Write-Host 'Quality flow complete. Re-run contrast/compliance audits if needed.' -ForegroundColor Green
