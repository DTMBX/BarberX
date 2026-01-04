param(
  [Parameter(Mandatory=$true)]
  [string]$Root,

  [Parameter(Mandatory=$true)]
  [string]$OutFile,

  [string]$BaseUrl = "https://faithfrontier.org/cases",

  [string[]]$DefaultTags = @("Faith Frontier","Cases")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Ensure output directory exists
$outDir = Split-Path -Parent $OutFile
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

# Gather PDFs (skip hidden/system directories)
$caseDirs = Get-ChildItem -Path $Root -Directory -Force |
  Where-Object { $_.Name -notmatch '^\.' -and ($_.Attributes -band [IO.FileAttributes]::Hidden) -eq 0 }

$items = foreach ($dir in $caseDirs) {
  $caseId = $dir.Name

  Get-ChildItem -Path $dir.FullName -Recurse -File -Filter *.pdf -Force |
    Where-Object { ($_.Attributes -band [IO.FileAttributes]::Hidden) -eq 0 } |
    ForEach-Object {
      $fileName = $_.Name

      [PSCustomObject]@{
        caseId    = $caseId
        caseTitle = $caseId
        docId     = $fileName
        docTitle  = $fileName
        docType   = "pdf"
        date      = ""  # optional: fill later
        url       = ("{0}/{1}/{2}" -f $BaseUrl.TrimEnd("/"), $caseId, $fileName)
        tags      = $DefaultTags
        text      = ""  # later: OCR text
        snippet   = ""  # later: excerpt
      }
    }
}

# Stable ordering helps avoid noisy diffs
$items = $items | Sort-Object caseId, docId

# Write UTF-8 WITHOUT BOM (important for some tooling)
$json = $items | ConvertTo-Json -Depth 8
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($OutFile, $json, $utf8NoBom)

Write-Host "Wrote $OutFile with $($items.Count) PDFs"
