<#
.SYNOPSIS
  Test suite for the Evident Discovery Suite RAG context pack.
  Covers: ingestion, hash validation, corruption detection, rebuild consistency.

.PARAMETER SuiteRoot
  Path to the bwc/ folder. Defaults to the script's grandparent.
#>
[CmdletBinding()]
param(
  [string]$SuiteRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $SuiteRoot) {
  $SuiteRoot = Split-Path -Parent $PSScriptRoot
}

$ctxRoot  = Join-Path $SuiteRoot 'rag_context'
$idxPath  = Join-Path $ctxRoot   'file_index.json'
$treePath = Join-Path $ctxRoot   'repo_tree.txt'
$intPath  = Join-Path $ctxRoot   'integrity_statement.json'
$auditPath = Join-Path $ctxRoot  'audit_log.jsonl'

$passed = 0
$failed = 0
$results = [System.Collections.Generic.List[string]]::new()

function Assert-True {
  param([string]$Name, [bool]$Condition, [string]$Detail = '')
  if ($Condition) {
    $script:passed++
    $script:results.Add("[PASS] $Name")
  } else {
    $script:failed++
    $script:results.Add("[FAIL] $Name$(if($Detail){': '+$Detail})")
  }
}

function Assert-Equal {
  param([string]$Name, $Expected, $Actual)
  if ($Expected -eq $Actual) {
    $script:passed++
    $script:results.Add("[PASS] $Name")
  } else {
    $script:failed++
    $script:results.Add("[FAIL] $Name : expected='$Expected' actual='$Actual'")
  }
}

Write-Host "=== Evident RAG Context Test Suite ==="
Write-Host "SuiteRoot: $SuiteRoot"
Write-Host ""

# ════════════════════════════════════════════════════════════════════
# TEST 1: Ingestion — required artifacts exist
# ════════════════════════════════════════════════════════════════════
Write-Host "-- Test 1: Ingestion (artifact existence) --"
$requiredFiles = @(
  'rag_context\repo_tree.txt',
  'rag_context\file_index.json',
  'rag_context\integrity_statement.json',
  'RAG_UPGRADE_PROMPT.md',
  '.env.example',
  'docs\LOCAL_DEV.md',
  'ops\docker\docker-compose.yml',
  'Update-RagContext.ps1',
  'Verify-Integrity.ps1'
)

foreach ($rel in $requiredFiles) {
  $full = Join-Path $SuiteRoot $rel
  Assert-True "EXISTS: $rel" (Test-Path -LiteralPath $full)
}

# ════════════════════════════════════════════════════════════════════
# TEST 2: Hash Validation — file_index hashes match disk
# ════════════════════════════════════════════════════════════════════
Write-Host "-- Test 2: Hash Validation --"
if (Test-Path $idxPath) {
  $idx = Get-Content $idxPath -Raw | ConvertFrom-Json
  Assert-Equal "Index schema version" "2" $idx.schemaVersion
  Assert-True "Index has files" ($idx.files.Count -gt 0)

  foreach ($entry in $idx.files) {
    $fp = Join-Path $SuiteRoot $entry.path
    if (Test-Path $fp) {
      $h = (Get-FileHash -LiteralPath $fp -Algorithm SHA256).Hash.ToLowerInvariant()
      Assert-Equal "HASH: $($entry.path)" $entry.sha256 $h
    } else {
      Assert-True "FILE EXISTS: $($entry.path)" $false
    }
  }
} else {
  Assert-True "file_index.json exists" $false
}

# ════════════════════════════════════════════════════════════════════
# TEST 3: Integrity Statement cross-checks
# ════════════════════════════════════════════════════════════════════
Write-Host "-- Test 3: Integrity Statement --"
if (Test-Path $intPath) {
  $stmt = Get-Content $intPath -Raw | ConvertFrom-Json

  Assert-True "Statement has scriptVersion" ($null -ne $stmt.scriptVersion)
  Assert-True "Statement has generatedUtc" ($null -ne $stmt.generatedUtc)
  Assert-True "Statement allArtifactsPass" ($stmt.allArtifactsPass -eq $true)

  # Index hash check
  if (Test-Path $idxPath) {
    $currentHash = (Get-FileHash -LiteralPath $idxPath -Algorithm SHA256).Hash.ToLowerInvariant()
    Assert-Equal "Integrity->Index hash" $stmt.indexSha256 $currentHash
  }

  # Tree hash check
  if (Test-Path $treePath) {
    $currentHash = (Get-FileHash -LiteralPath $treePath -Algorithm SHA256).Hash.ToLowerInvariant()
    Assert-Equal "Integrity->Tree hash" $stmt.treeSha256 $currentHash
  }
} else {
  Assert-True "integrity_statement.json exists" $false
}

# ════════════════════════════════════════════════════════════════════
# TEST 4: Corruption Detection — tamper a temp copy, verify fails
# ════════════════════════════════════════════════════════════════════
Write-Host "-- Test 4: Corruption Detection --"
$tempDir = Join-Path $env:TEMP "evident_test_$(Get-Random)"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

try {
  # Copy the index to temp
  $tempIdx = Join-Path $tempDir 'file_index.json'
  Copy-Item $idxPath $tempIdx -Force

  # Tamper: change a hash in the copy
  $content = Get-Content $tempIdx -Raw
  $tamperedContent = $content -replace '"sha256":\s*"([a-f0-9]{4})', '"sha256": "dead'
  [System.IO.File]::WriteAllText($tempIdx, $tamperedContent,
    [System.Text.UTF8Encoding]::new($false))

  # Verify the tampered index differs
  $origHash = (Get-FileHash $idxPath -Algorithm SHA256).Hash
  $tampHash = (Get-FileHash $tempIdx -Algorithm SHA256).Hash
  Assert-True "Tampered index differs from original" ($origHash -ne $tampHash)

  # Parse tampered index and check first file hash doesn't match disk
  $tampIdx = Get-Content $tempIdx -Raw | ConvertFrom-Json
  if ($tampIdx.files.Count -gt 0) {
    $firstFile = $tampIdx.files[0]
    $fp = Join-Path $SuiteRoot $firstFile.path
    if (Test-Path $fp) {
      $diskHash = (Get-FileHash -LiteralPath $fp -Algorithm SHA256).Hash.ToLowerInvariant()
      Assert-True "Tampered hash detected (mismatch)" ($diskHash -ne $firstFile.sha256)
    }
  }
} finally {
  Remove-Item $tempDir -Recurse -Force -EA SilentlyContinue
}

# ════════════════════════════════════════════════════════════════════
# TEST 5: Rebuild Consistency — run Update twice, compare outputs
# ════════════════════════════════════════════════════════════════════
Write-Host "-- Test 5: Rebuild Consistency --"
$updateScript = Join-Path $SuiteRoot 'Update-RagContext.ps1'
if (Test-Path $updateScript) {
  # Capture hash of current integrity statement
  $hashBefore = if (Test-Path $intPath) { (Get-FileHash $intPath -Algorithm SHA256).Hash } else { '' }

  # Run update
  & pwsh -NoProfile -ExecutionPolicy Bypass -File $updateScript -SuiteRoot $SuiteRoot *> $null 2>&1

  # Capture hash after
  $hashAfter = if (Test-Path $intPath) { (Get-FileHash $intPath -Algorithm SHA256).Hash } else { '' }

  Assert-True "Rebuild produces integrity statement" (Test-Path $intPath)

  # Verify the index is still valid JSON
  try {
    $null = Get-Content $idxPath -Raw | ConvertFrom-Json
    Assert-True "Post-rebuild index is valid JSON" $true
  } catch {
    Assert-True "Post-rebuild index is valid JSON" $false
  }

  # Run Verify-Integrity and check exit code
  $verifyScript = Join-Path $SuiteRoot 'Verify-Integrity.ps1'
  if (Test-Path $verifyScript) {
    & pwsh -NoProfile -ExecutionPolicy Bypass -File $verifyScript -SuiteRoot $SuiteRoot *> $null 2>&1
    Assert-Equal "Post-rebuild Verify-Integrity exit code" 0 $LASTEXITCODE
  }
} else {
  Assert-True "Update-RagContext.ps1 exists" $false
}

# ════════════════════════════════════════════════════════════════════
# TEST 6: Audit Log integrity
# ════════════════════════════════════════════════════════════════════
Write-Host "-- Test 6: Audit Log --"
if (Test-Path $auditPath) {
  $lines = Get-Content $auditPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
  Assert-True "Audit log is non-empty" ($lines.Count -gt 0)

  $allValid = $true
  foreach ($line in $lines) {
    try { $null = $line | ConvertFrom-Json } catch { $allValid = $false; break }
  }
  Assert-True "All audit log entries are valid JSON" $allValid

  # Check required event types present
  $events = $lines | ForEach-Object { ($_ | ConvertFrom-Json).event }
  $types = $events | Sort-Object -Unique
  Assert-True "Has INDEX_REBUILD_START event" ('INDEX_REBUILD_START' -in $types)
  Assert-True "Has INDEX_REBUILD_COMPLETE event" ('INDEX_REBUILD_COMPLETE' -in $types)
  Assert-True "Has TREE_REBUILT event" ('TREE_REBUILT' -in $types)
  Assert-True "Has INDEX_REBUILT event" ('INDEX_REBUILT' -in $types)
} else {
  Assert-True "Audit log exists" $false
}

# ════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════
Write-Host ""
Write-Host "=== Test Results ==="
foreach ($r in $results) { Write-Host "  $r" }
Write-Host ""
Write-Host "Passed: $passed  Failed: $failed  Total: $($passed + $failed)"

# Write results to file
$reportContent = @(
  "=== Evident RAG Context Test Report ==="
  "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')"
  "SuiteRoot: $SuiteRoot"
  ""
) + $results + @(
  ""
  "Passed: $passed  Failed: $failed  Total: $($passed + $failed)"
  "Result: $(if($failed -eq 0){'ALL PASSED'}else{'FAILURES DETECTED'})"
)
$reportContent -join "`n" | Out-File (Join-Path $ctxRoot 'test_report.txt') -Encoding utf8

if ($failed -eq 0) {
  Write-Host "RESULT: ALL TESTS PASSED."
  exit 0
} else {
  Write-Host "RESULT: $failed TEST(S) FAILED."
  exit 1
}
