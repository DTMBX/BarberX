<#
.SYNOPSIS
  Regenerates the RAG context pack for the Evident Discovery Suite.
  Phase 3 hardened: deterministic hashing, timestamp normalization,
  version tagging, integrity manifests, idempotent rebuild.

.PARAMETER SuiteRoot
  Path to the bwc suite folder. Defaults to the script's own directory.

.PARAMETER SkipExcerpts
  If set, skip copying excerpt files (useful in CI).

.EXAMPLE
  .\Update-RagContext.ps1
  .\Update-RagContext.ps1 -SuiteRoot C:\repos\Evident\bwc
#>
[CmdletBinding()]
param(
  [string]$SuiteRoot,
  [switch]$SkipExcerpts
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ── Constants ───────────────────────────────────────────────────────
$SCRIPT_VERSION = '2.0.0'
$INDEX_SCHEMA_VERSION = '2'

# ── Resolve SuiteRoot ───────────────────────────────────────────────
if (-not $SuiteRoot) {
  $SuiteRoot = $PSScriptRoot
  if (-not (Test-Path (Join-Path $SuiteRoot 'rag_context') -PathType Container)) {
    $SuiteRoot = Join-Path (Split-Path -Parent $PSScriptRoot) 'bwc'
  }
}

if (-not (Test-Path -LiteralPath $SuiteRoot -PathType Container)) {
  Write-Error "SuiteRoot not found: $SuiteRoot"
  exit 1
}

Write-Host "Update-RagContext v$SCRIPT_VERSION"
Write-Host "SuiteRoot : $SuiteRoot"

# ── Helpers ─────────────────────────────────────────────────────────
function Ensure-Dir([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
  }
}

function Write-Utf8([string]$Path, [string]$Content) {
  Ensure-Dir (Split-Path -Parent $Path)
  [System.IO.File]::WriteAllText($Path, $Content,
    [System.Text.UTF8Encoding]::new($false))
}

function Get-NormalizedUtcTimestamp([datetime]$dt) {
  $dt.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
}

function Get-FileHashLower([string]$FilePath) {
  (Get-FileHash -LiteralPath $FilePath -Algorithm SHA256).Hash.ToLowerInvariant()
}

# ── Paths ───────────────────────────────────────────────────────────
$ctxRoot    = Join-Path $SuiteRoot 'rag_context'
$excerpts   = Join-Path $ctxRoot   'excerpts'
$auditLog   = Join-Path $ctxRoot   'audit_log.jsonl'
Ensure-Dir $ctxRoot
Ensure-Dir $excerpts

$runTimestamp = Get-NormalizedUtcTimestamp (Get-Date)

# ── Audit logger (append-only) ──────────────────────────────────────
function Append-AuditEvent {
  param(
    [string]$EventType,
    [string]$Target,
    [string]$Detail = '',
    [string]$HashBefore = '',
    [string]$HashAfter = ''
  )
  $evt = [ordered]@{
    timestamp     = $runTimestamp
    scriptVersion = $SCRIPT_VERSION
    event         = $EventType
    target        = $Target
    detail        = $Detail
    hashBefore    = $HashBefore
    hashAfter     = $HashAfter
  }
  $line = ($evt | ConvertTo-Json -Compress -Depth 10)
  [System.IO.File]::AppendAllText($auditLog, "$line`n",
    [System.Text.UTF8Encoding]::new($false))
}

Append-AuditEvent -EventType 'INDEX_REBUILD_START' -Target $SuiteRoot

# ── 1) Rebuild repo_tree.txt ───────────────────────────────────────
Write-Host 'Rebuilding repo_tree.txt ...'
$treePath = Join-Path $ctxRoot 'repo_tree.txt'
$hashBefore = if (Test-Path $treePath) { Get-FileHashLower $treePath } else { '' }

$rootLen = (Get-Item -LiteralPath $SuiteRoot).FullName.Length
$treeLines = [System.Collections.Generic.List[string]]::new()
$treeLines.Add("# Repo tree for: $SuiteRoot")
$treeLines.Add("# Generated: $runTimestamp")
$treeLines.Add("# Script: Update-RagContext.ps1 v$SCRIPT_VERSION")
$treeLines.Add('')

Get-ChildItem -LiteralPath $SuiteRoot -Recurse -Force -EA SilentlyContinue |
  Where-Object {
    $_.FullName -notmatch '\\node_modules\\|\\\.\.git\\|\\\.\.next\\|\\dist\\|\\build\\|\\\.\.venv\\|\\__pycache__\\' -and
    $_.Name -notmatch '^_.*\.log$'
  } |
  Sort-Object FullName |
  ForEach-Object {
    $rel   = $_.FullName.Substring($rootLen).TrimStart('\')
    $depth = ($rel -split '\\').Count
    if ($depth -le 7) {
      $type = if ($_.PSIsContainer) { 'dir ' } else { 'file' }
      $treeLines.Add("$type  $rel")
    }
  }

Write-Utf8 $treePath ($treeLines -join "`n")
$hashAfter = Get-FileHashLower $treePath
Append-AuditEvent -EventType 'TREE_REBUILT' -Target 'rag_context\repo_tree.txt' `
  -HashBefore $hashBefore -HashAfter $hashAfter

# ── 2) Rebuild file_index.json ─────────────────────────────────────
Write-Host 'Rebuilding file_index.json ...'
$idxPath = Join-Path $ctxRoot 'file_index.json'
$hashBefore = if (Test-Path $idxPath) { Get-FileHashLower $idxPath } else { '' }

$files = Get-ChildItem -LiteralPath $SuiteRoot -Recurse -File -Force -EA SilentlyContinue |
  Where-Object {
    $_.FullName -notmatch '\\node_modules\\|\\\.\.git\\|\\\.\.next\\|\\dist\\|\\build\\|\\\.\.venv\\|\\__pycache__\\' -and
    $_.Name -notmatch '^_.*\.log$' -and
    # Exclude self-referential rag_context artifacts (signed by integrity_statement instead)
    $_.FullName -notmatch '\\rag_context\\(file_index\.json|repo_tree\.txt|verification_report\.txt|integrity_statement\.json|audit_log\.jsonl)$' -and
    $_.FullName -notmatch '\\rag_context\\excerpts\\'
  }

$indexEntries = foreach ($f in $files) {
  [ordered]@{
    path         = $f.FullName.Substring($rootLen).TrimStart('\')
    bytes        = $f.Length
    sha256       = Get-FileHashLower $f.FullName
    lastWriteUtc = Get-NormalizedUtcTimestamp $f.LastWriteTimeUtc
  }
}
$indexSorted = $indexEntries | Sort-Object { $_.path }

$indexWrapper = [ordered]@{
  schemaVersion = $INDEX_SCHEMA_VERSION
  generatedUtc  = $runTimestamp
  scriptVersion = $SCRIPT_VERSION
  suiteRoot     = $SuiteRoot
  fileCount     = $indexSorted.Count
  files         = @($indexSorted)
}

$json = $indexWrapper | ConvertTo-Json -Depth 50
Write-Utf8 $idxPath $json
$hashAfter = Get-FileHashLower $idxPath
Append-AuditEvent -EventType 'INDEX_REBUILT' -Target 'rag_context\file_index.json' `
  -Detail "entries=$($indexSorted.Count)" -HashBefore $hashBefore -HashAfter $hashAfter

# ── 3) Re-populate excerpts/ ───────────────────────────────────────
if (-not $SkipExcerpts) {
  Write-Host 'Copying excerpts ...'
  $excerptSources = @(
    '.env.example',
    'ops\docker\docker-compose.yml',
    'docs\LOCAL_DEV.md',
    'RAG_UPGRADE_PROMPT.md',
    'backend\pyproject.toml',
    'backend\alembic.ini',
    'backend\app\main.py',
    'frontend\package.json',
    'frontend\next.config.mjs',
    'frontend\tsconfig.json',
    '.gitignore',
    '.dockerignore',
    '.github\workflows\ci.yml',
    'docs\ARCHITECTURE.md',
    'docs\CHAIN_OF_CUSTODY.md'
  )

  $copiedCount = 0
  foreach ($rel in $excerptSources) {
    $src = Join-Path $SuiteRoot $rel
    $dst = Join-Path $excerpts  $rel
    if (Test-Path -LiteralPath $src -PathType Leaf) {
      Ensure-Dir (Split-Path -Parent $dst)
      $hBefore = if (Test-Path $dst) { Get-FileHashLower $dst } else { '' }
      Copy-Item -LiteralPath $src -Destination $dst -Force
      $hAfter = Get-FileHashLower $dst
      if ($hBefore -ne $hAfter) {
        Append-AuditEvent -EventType 'EXCERPT_COPIED' -Target $rel `
          -HashBefore $hBefore -HashAfter $hAfter
      }
      $copiedCount++
    }
  }
  Write-Host "  Copied $copiedCount excerpt(s)."
} else {
  Write-Host '  Skipping excerpts (--SkipExcerpts).'
}

# ── 4) Verification report ─────────────────────────────────────────
Write-Host 'Writing verification_report.txt ...'
$requiredArtifacts = @(
  'rag_context\repo_tree.txt',
  'rag_context\file_index.json',
  'RAG_UPGRADE_PROMPT.md',
  '.env.example',
  'docs\LOCAL_DEV.md',
  'ops\docker\docker-compose.yml'
)

$report = [System.Text.StringBuilder]::new()
[void]$report.AppendLine("=== RAG Context Verification Report ===")
[void]$report.AppendLine("Generated : $runTimestamp")
[void]$report.AppendLine("Script    : Update-RagContext.ps1 v$SCRIPT_VERSION")
[void]$report.AppendLine("SuiteRoot : $SuiteRoot")
[void]$report.AppendLine('')
$hdrLine = 'Path'.PadRight(45) + 'Exists'.PadRight(7) + 'Bytes'.PadRight(10) + 'LastWriteTimeUtc'.PadRight(24) + 'SHA-256'
$sepLine = '----'.PadRight(45) + '------'.PadRight(7) + '-----'.PadRight(10) + '----------------'.PadRight(24) + '-------'
[void]$report.AppendLine($hdrLine)
[void]$report.AppendLine($sepLine)

$allOk = $true
foreach ($rel in $requiredArtifacts) {
  $full = Join-Path $SuiteRoot $rel
  $ex   = Test-Path -LiteralPath $full -PathType Leaf
  if (-not $ex) { $allOk = $false }
  $it = if ($ex) { Get-Item -LiteralPath $full } else { $null }
  $h  = if ($ex) { Get-FileHashLower $full } else { '-' }
  $b  = if ($it) { "$($it.Length)" } else { '-' }
  $t  = if ($it) { Get-NormalizedUtcTimestamp $it.LastWriteTimeUtc } else { '-' }
  $row = $rel.PadRight(45) + "$ex".PadRight(7) + $b.PadRight(10) + $t.PadRight(24) + $h
  [void]$report.AppendLine($row)
}

$excFiles = Get-ChildItem -LiteralPath $excerpts -Recurse -File -EA SilentlyContinue
[void]$report.AppendLine('')
[void]$report.AppendLine("Excerpts count : $($excFiles.Count)")
foreach ($ef in $excFiles) {
  $eRel = $ef.FullName.Substring($excerpts.Length).TrimStart('\')
  $eHash = Get-FileHashLower $ef.FullName
  [void]$report.AppendLine("  $eRel  sha256=$eHash")
}

$idxContent = Get-Content -LiteralPath $idxPath -Raw | ConvertFrom-Json
$entryCount = if ($idxContent.files -is [array]) { $idxContent.files.Count } else { 0 }
[void]$report.AppendLine('')
[void]$report.AppendLine("file_index.json schema  : v$($idxContent.schemaVersion)")
[void]$report.AppendLine("file_index.json entries : $entryCount")

$auditLines = 0
if (Test-Path $auditLog) {
  $auditLines = (Get-Content $auditLog | Measure-Object -Line).Lines
}
[void]$report.AppendLine("audit_log.jsonl events  : $auditLines")

[void]$report.AppendLine('')
if ($allOk) {
  [void]$report.AppendLine('RESULT: PASS - all required artifacts present.')
} else {
  [void]$report.AppendLine('RESULT: FAIL - one or more artifacts missing.')
}

$reportText = $report.ToString()
$reportPath = Join-Path $ctxRoot 'verification_report.txt'
Write-Utf8 $reportPath $reportText

$reportHash = Get-FileHashLower $reportPath
$integrity = [ordered]@{
  statement        = 'RAG Context Pack Integrity Statement'
  generatedUtc     = $runTimestamp
  scriptVersion    = $SCRIPT_VERSION
  reportSha256     = $reportHash
  indexSha256      = Get-FileHashLower $idxPath
  treeSha256       = Get-FileHashLower $treePath
  auditLogSha256   = if (Test-Path $auditLog) { Get-FileHashLower $auditLog } else { 'not-present' }
  allArtifactsPass = $allOk
  fileCount        = $entryCount
  excerptCount     = $excFiles.Count
}
$integrityJson = $integrity | ConvertTo-Json -Depth 10
Write-Utf8 (Join-Path $ctxRoot 'integrity_statement.json') $integrityJson

Append-AuditEvent -EventType 'INDEX_REBUILD_COMPLETE' -Target $SuiteRoot `
  -Detail "pass=$allOk;files=$entryCount;excerpts=$($excFiles.Count)" `
  -HashAfter $reportHash

Write-Host ''
Write-Host $reportText
Write-Host ''

if ($allOk) {
  Write-Host 'EXIT 0 - all artifacts verified.'
  exit 0
} else {
  Write-Host 'EXIT 1 - missing artifacts detected.'
  exit 1
}
