# Tillerstead Repository Encoding Fixer & Validator
# Fixes encoding issues and validates file consistency across the repo

param(
    [switch]$Validate,
    [switch]$Fix,
    [switch]$Report,
    [string]$Path = "C:\Users\Devon Tyler\tillerstead"
)

$ErrorActionPreference = "Continue"
$issues = [System.Collections.Generic.List[object]]::new()
$fixed = @()

function Test-FileEncoding {
    param([string]$FilePath)
    
    try {
        $bytes = [System.IO.File]::ReadAllBytes($FilePath)
        
        # Check for BOM
        if ($bytes.Count -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            return @{ Encoding = "UTF-8-BOM"; HasBOM = $true }
        }
        if ($bytes.Count -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) {
            return @{ Encoding = "UTF-16LE"; HasBOM = $true }
        }
        if ($bytes.Count -ge 2 -and $bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF) {
            return @{ Encoding = "UTF-16BE"; HasBOM = $true }
        }
        
        return @{ Encoding = "UTF-8"; HasBOM = $false }
    }
    catch {
        return @{ Encoding = "Unknown"; Error = $_.Exception.Message }
    }
}

function Fix-FileEncoding {
    param([string]$FilePath)
    
    try {
        # Read as UTF-8 without BOM
        $content = [System.IO.File]::ReadAllText($FilePath, [System.Text.Encoding]::UTF8)
        
        # Remove any BOM if present
        if ($content.StartsWith([char]0xFEFF)) {
            $content = $content.Substring(1)
        }
        
        # Write back as UTF-8 without BOM
        [System.IO.File]::WriteAllText($FilePath, $content, [System.Text.Encoding]::UTF8)
        return $true
    }
    catch {
        Write-Host "ERROR fixing $FilePath : $_" -ForegroundColor Red
        return $false
    }
}

function Validate-HTMLFiles {
    param([string]$RootPath)
    
    Write-Host "🔍 Validating HTML files..." -ForegroundColor Cyan
    $htmlFiles = Get-ChildItem -Path $RootPath -Recurse -Include "*.html" -ErrorAction SilentlyContinue
    
    foreach ($file in $htmlFiles) {
        $encoding = Test-FileEncoding -FilePath $file.FullName
        
        # Check for common issues
        $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
        
        $issues_local = @()
        
        # Missing DOCTYPE
        if (-not $content.Contains("<!DOCTYPE")) {
            $issues_local += "Missing DOCTYPE declaration"
        }
        
        # Check for proper meta charset
        if ($file.Name -ne "404.html" -and $file.Name -ne "success.html") {
            if (-not $content.Contains('<meta charset="utf-8"') -and -not $content.Contains('<meta charset="UTF-8"')) {
                $issues_local += "Missing or incorrect meta charset"
            }
        }
        
        # Check for broken entities
        if ($content -match '&[a-zA-Z]+;' | Select-String -Pattern '&(?!(?:lt|gt|amp|quot|apos|#\d+|#x[0-9a-fA-F]+);)') {
            $issues_local += "Potential broken HTML entities detected"
        }
        
        if ($issues_local.Count -gt 0) {
            $issues += @{
                File = $file.FullName
                Encoding = $encoding.Encoding
                HasBOM = $encoding.HasBOM
                Issues = $issues_local
            }
        }
    }
    
    return $issues
}

function Validate-YAMLFiles {
    param([string]$RootPath)
    
    Write-Host "🔍 Validating YAML files..." -ForegroundColor Cyan
    $yamlFiles = Get-ChildItem -Path $RootPath -Recurse -Include "*.yml", "*.yaml" -ErrorAction SilentlyContinue
    
    foreach ($file in $yamlFiles) {
        $encoding = Test-FileEncoding -FilePath $file.FullName
        $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
        
        $issues_local = @()
        
        # Check for tabs (YAML should use spaces)
        if ($content -match "`t") {
            $issues_local += "Contains tab characters (YAML requires spaces)"
        }
        
        # Check for inconsistent indentation
        $lines = $content -split "`n"
        $indents = @()
        foreach ($line in $lines) {
            if ($line -match '^( +)\S') {
                $indents += $matches[1].Length
            }
        }
        
        $uniqueIndents = $indents | Sort-Object -Unique
        if ($uniqueIndents.Count -gt 3) {
            $issues_local += "Inconsistent indentation levels detected"
        }
        
        if ($issues_local.Count -gt 0) {
            $issues += @{
                File = $file.FullName
                Encoding = $encoding.Encoding
                HasBOM = $encoding.HasBOM
                Issues = $issues_local
            }
        }
    }
    
    return $issues
}

# Main execution
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║  Tillerstead Repository Encoding Fixer & Validator v1.0    ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
Write-Host ""

if ($Validate -or (-not $Fix -and -not $Report)) {
    Write-Host "🚀 Running validation..." -ForegroundColor Green
    
    $html_issues = Validate-HTMLFiles -RootPath $Path
    $yaml_issues = Validate-YAMLFiles -RootPath $Path
    
    $all_issues = @($html_issues) + @($yaml_issues)
    
    if ($all_issues.Count -eq 0) {
        Write-Host "✅ All files validated successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Found $($all_issues.Count) files with issues:" -ForegroundColor Yellow
        foreach ($issue in $all_issues) {
            Write-Host "  📄 $($issue.File)" -ForegroundColor Red
            Write-Host "     Encoding: $($issue.Encoding) $(if ($issue.HasBOM) { '(with BOM)' } else { '(no BOM)' })" -ForegroundColor Gray
            foreach ($msg in $issue.Issues) {
                Write-Host "     ⚠️  $msg" -ForegroundColor Yellow
            }
        }
    }
}

if ($Fix) {
    Write-Host "🔧 Fixing encoding issues..." -ForegroundColor Green
    
    $allFiles = Get-ChildItem -Path $Path -Recurse -Include "*.html", "*.md", "*.yml", "*.yaml", "*.json" -ErrorAction SilentlyContinue
    
    $fixed_count = 0
    foreach ($file in $allFiles) {
        if (Fix-FileEncoding -FilePath $file.FullName) {
            $fixed_count++
        }
    }
    
    Write-Host "✅ Fixed encoding for $fixed_count files" -ForegroundColor Green
}

if ($Report) {
    Write-Host "📊 Generating detailed report..." -ForegroundColor Green
    
    $reportPath = Join-Path $Path "reports\encoding-audit-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    
    $reportData = @{
        Timestamp = Get-Date -Format "o"
        Repository = $Path
        Statistics = @{
            TotalHTMLFiles = (Get-ChildItem -Path $Path -Recurse -Include "*.html" | Measure-Object).Count
            TotalYAMLFiles = (Get-ChildItem -Path $Path -Recurse -Include "*.yml", "*.yaml" | Measure-Object).Count
            TotalJSONFiles = (Get-ChildItem -Path $Path -Recurse -Include "*.json" | Measure-Object).Count
        }
        Issues = $all_issues
    }
    
    New-Item -ItemType Directory -Force -Path (Split-Path $reportPath) | Out-Null
    $reportData | ConvertTo-Json -Depth 10 | Set-Content -Path $reportPath -Encoding UTF8
    
    Write-Host "✅ Report saved to: $reportPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done! Use -Fix to correct encoding issues, -Validate to check, or -Report for detailed audit." -ForegroundColor Cyan
