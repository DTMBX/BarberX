function Monitor-DiskSpace {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DriveLetter,
        [int]$WarningThresholdPercent = 80
    )

    $drive = Get-PSDrive -Name $DriveLetter -ErrorAction SilentlyContinue
    if (-not $drive) {
        Write-Host "Drive '$DriveLetter' not found." -ForegroundColor Yellow
        return
    }

    $usedPercent = [math]::Round(($drive.Used / ($drive.Used + $drive.Free)) * 100, 2)
    if ($usedPercent -ge $WarningThresholdPercent) {
        Write-Host "Warning: Drive $DriveLetter is ${usedPercent}% full." -ForegroundColor Red
    } else {
        Write-Host "Drive $DriveLetter usage: ${usedPercent}%" -ForegroundColor Green
    }
}

function Show-SystemUptime {
    $bootTime = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
    $uptime = (Get-Date) - $bootTime
    Write-Host ("Uptime: {0:dd\:hh\:mm\:ss}" -f $uptime) -ForegroundColor Green
}

function Clean-TempFiles {
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "High")]
    param(
        [string]$Path = $env:TEMP
    )

    if (-not (Test-Path $Path)) {
        Write-Host "Temp path '$Path' not found." -ForegroundColor Yellow
        return
    }

    if ($PSCmdlet.ShouldProcess($Path, "Remove temp files")) {
        Remove-Item -Path (Join-Path $Path "*") -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Temp files cleaned from $Path." -ForegroundColor Green
    }
}

function Backup-Repo {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoName,
        [string]$SourceRoot = "$env:USERPROFILE\github-repos",
        [string]$DestinationRoot = "$env:USERPROFILE\backups"
    )

    $sourcePath = Join-Path $SourceRoot $RepoName
    $destinationPath = Join-Path $DestinationRoot $RepoName

    if (-not (Test-Path $sourcePath)) {
        Write-Host "Source repo '$sourcePath' not found." -ForegroundColor Yellow
        return
    }

    New-Item -ItemType Directory -Path $destinationPath -Force | Out-Null
    Copy-Item -Path $sourcePath -Destination $destinationPath -Recurse -Force
    Write-Host "$RepoName backed up to $destinationPath" -ForegroundColor Green
}

function Send-ErrorNotification {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ErrorMessage,
        [string]$To = "youremail@example.com",
        [string]$From = "system@yourdomain.com",
        [string]$Subject = "System Error"
    )

    $body = "An error occurred: $ErrorMessage"
    Send-MailMessage -To $To -From $From -Subject $Subject -Body $body
}
