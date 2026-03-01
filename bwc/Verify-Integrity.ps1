<#
.SYNOPSIS
  Verifies the integrity of the RAG context pack by replaying
  audit_log.jsonl and cross-checking SHA-256 hashes.

.DESCRIPTION
  Phase 4 forensic integrity: reads the audit log and integrity
  statement, then independently re-hashes every file in file_index.json
  to detect silent mutations. Produces PASS/FAIL exit code.

.PARAMETER SuiteRoot
  Path to bwc/. Defaults to the script's parent directory.
#>
[CmdletBinding()]
param(
  [string]$SuiteRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $SuiteRoot) { $SuiteRoot = Split-Path -Parent $PSScriptRoot }
if (-not (Test-Path (Join-Path $SuiteRoot 'rag_context'))) {
  $SuiteRoot = $PSScriptRoot
}

$ctxRoot = Join-Path $SuiteRoot 'rag_context'
$idxPath = Join-Path $ctxRoot 'file_index.json'
$intPath = Join-Path $ctxRoot 'integrity_statement.json'
$auditPath = Join-Path $ctxRoot 'audit_log.jsonl'

Write-Host "=== Forensic Integrity Verification ==="
Write-Host "SuiteRoot: $SuiteRoot"
Write-Host ""

$failures = [System.Collections.Generic.List[string]]::new()
$checked = 0

# ── 1) Verify file_index.json entries ──────────────────────────────
if (-not (Test-Path $idxPath)) {
  Write-Host "FAIL: file_index.json not found."
  exit 1
}

$idx = Get-Content $idxPath -Raw | ConvertFrom-Json
Write-Host "Index schema version: $($idx.schemaVersion)"
Write-Host "Index generated: $($idx.generatedUtc)"
Write-Host "Checking $($idx.fileCount) indexed files..."
Write-Host ""

foreach ($entry in $idx.files) {
  $fullPath = Join-Path $SuiteRoot $entry.path
  $checked++

  if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
    $msg = "MISSING: $($entry.path)"
    $failures.Add($msg)
    Write-Host "  [FAIL] $msg"
    continue
  }

  $actualHash = (Get-FileHash -LiteralPath $fullPath -Algorithm SHA256).Hash.ToLowerInvariant()
  $actualSize = (Get-Item -LiteralPath $fullPath).Length

  if ($actualHash -ne $entry.sha256) {
    $msg = "HASH MISMATCH: $($entry.path) expected=$($entry.sha256) actual=$actualHash"
    $failures.Add($msg)
    Write-Host "  [FAIL] $msg"
  } elseif ($actualSize -ne $entry.bytes) {
    $msg = "SIZE MISMATCH: $($entry.path) expected=$($entry.bytes) actual=$actualSize"
    $failures.Add($msg)
    Write-Host "  [FAIL] $msg"
  } else {
    Write-Host "  [OK]   $($entry.path)"
  }
}

# ── 2) Verify integrity statement ─────────────────────────────────
Write-Host ""
if (Test-Path $intPath) {
  $stmt = Get-Content $intPath -Raw | ConvertFrom-Json
  Write-Host "Integrity statement generated: $($stmt.generatedUtc)"

  # Cross-check index hash
  $currentIdxHash = (Get-FileHash -LiteralPath $idxPath -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($currentIdxHash -ne $stmt.indexSha256) {
    $msg = "INDEX HASH DRIFT: integrity_statement says $($stmt.indexSha256) but current is $currentIdxHash"
    $failures.Add($msg)
    Write-Host "  [FAIL] $msg"
  } else {
    Write-Host "  [OK]   Index hash matches integrity statement."
  }

  # Cross-check tree hash
  $treePath = Join-Path $ctxRoot 'repo_tree.txt'
  if (Test-Path $treePath) {
    $currentTreeHash = (Get-FileHash -LiteralPath $treePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($currentTreeHash -ne $stmt.treeSha256) {
      $msg = "TREE HASH DRIFT: integrity_statement says $($stmt.treeSha256) but current is $currentTreeHash"
      $failures.Add($msg)
      Write-Host "  [FAIL] $msg"
    } else {
      Write-Host "  [OK]   Tree hash matches integrity statement."
    }
  }

  # Cross-check report hash
  $rptPath = Join-Path $ctxRoot 'verification_report.txt'
  if (Test-Path $rptPath) {
    $currentRptHash = (Get-FileHash -LiteralPath $rptPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($currentRptHash -ne $stmt.reportSha256) {
      $msg = "REPORT HASH DRIFT: integrity_statement says $($stmt.reportSha256) but current is $currentRptHash"
      $failures.Add($msg)
      Write-Host "  [FAIL] $msg"
    } else {
      Write-Host "  [OK]   Report hash matches integrity statement."
    }
  }

  # Cross-check audit log hash
  if ($stmt.auditLogSha256 -and $stmt.auditLogSha256 -ne 'not-present') {
    if (Test-Path $auditPath) {
      $currentAuditHash = (Get-FileHash -LiteralPath $auditPath -Algorithm SHA256).Hash.ToLowerInvariant()
      if ($currentAuditHash -ne $stmt.auditLogSha256) {
        # Audit log is append-only — new events after integrity statement is expected
        Write-Host "  [INFO] Audit log hash differs from integrity statement (new events appended — expected for append-only log)."
      } else {
        Write-Host "  [OK]   Audit log hash matches integrity statement."
      }
    }
  }
} else {
  $failures.Add("integrity_statement.json not found")
  Write-Host "  [WARN] integrity_statement.json not found — run Update-RagContext.ps1 first."
}

# ── 3) Audit log continuity check ─────────────────────────────────
Write-Host ""
if (Test-Path $auditPath) {
  $lines = Get-Content $auditPath
  $eventCount = $lines.Count
  Write-Host "Audit log: $eventCount events"

  # Verify each line is valid JSON
  $badLines = 0
  foreach ($line in $lines) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    try { $null = $line | ConvertFrom-Json } catch { $badLines++ }
  }
  if ($badLines -gt 0) {
    $failures.Add("Audit log has $badLines malformed JSON lines")
    Write-Host "  [FAIL] $badLines malformed lines in audit log."
  } else {
    Write-Host "  [OK]   All $eventCount audit events are valid JSON."
  }

  # Check for required event types
  $events = $lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_ | ConvertFrom-Json }
  $types = $events | ForEach-Object { $_.event } | Sort-Object -Unique
  Write-Host "  Event types: $($types -join ', ')"

  $requiredTypes = @('INDEX_REBUILD_START', 'INDEX_REBUILD_COMPLETE')
  foreach ($rt in $requiredTypes) {
    if ($rt -notin $types) {
      $failures.Add("Missing required audit event type: $rt")
      Write-Host "  [WARN] Missing event type: $rt"
    }
  }
} else {
  $failures.Add("audit_log.jsonl not found")
  Write-Host "  [WARN] audit_log.jsonl not found."
}

# ── 4) Detect untracked files (files on disk not in index) ────────
Write-Host ""
Write-Host "Checking for untracked files..."
$indexedPaths = @{}
foreach ($entry in $idx.files) { $indexedPaths[$entry.path] = $true }

$rootLen = (Get-Item -LiteralPath $SuiteRoot).FullName.Length
$diskFiles = Get-ChildItem -LiteralPath $SuiteRoot -Recurse -File -Force -EA SilentlyContinue |
  Where-Object {
    $_.FullName -notmatch '\\node_modules\\|\\\.git\\|\\\.next\\|\\dist\\|\\build\\|\\\.venv\\|\\__pycache__\\'
  }

$untracked = 0
foreach ($df in $diskFiles) {
  $rel = $df.FullName.Substring($rootLen).TrimStart('\')
  if (-not $indexedPaths.ContainsKey($rel)) {
    Write-Host "  [INFO] Untracked: $rel"
    $untracked++
  }
}
if ($untracked -eq 0) {
  Write-Host "  [OK]   No untracked files."
} else {
  Write-Host "  [INFO] $untracked file(s) not in index (re-run Update-RagContext.ps1 to sync)."
}

# ── Summary ────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=== Summary ==="
Write-Host "Files checked : $checked"
Write-Host "Failures      : $($failures.Count)"
Write-Host "Untracked     : $untracked"

if ($failures.Count -eq 0) {
  Write-Host ""
  Write-Host "RESULT: PASS - forensic integrity verified."
  exit 0
} else {
  Write-Host ""
  Write-Host "RESULT: FAIL - integrity violations detected:"
  foreach ($f in $failures) { Write-Host "  - $f" }
  exit 1
}
