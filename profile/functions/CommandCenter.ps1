function Get-CommandDatabasePath {
    $profileRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
    return Join-Path $profileRoot "command-database.json"
}

function Get-CommandDatabase {
    $databasePath = Get-CommandDatabasePath

    if (-not (Test-Path $databasePath)) {
        Write-Host "Command database not found at $databasePath" -ForegroundColor Yellow
        return @()
    }

    return Get-Content -Path $databasePath -Raw | ConvertFrom-Json
}

function Get-CommandDefinition {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $database = Get-CommandDatabase
    return $database | Where-Object { $_.name -eq $Name }
}

function Resolve-CommandSet {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [string[]]$Visited = @()
    )

    if ($Visited -contains $Name) {
        Write-Host "Detected a circular command reference: $Name" -ForegroundColor Red
        return @()
    }

    $definition = Get-CommandDefinition -Name $Name
    if (-not $definition) {
        Write-Host "Command set '$Name' not found in the database." -ForegroundColor Yellow
        return @()
    }

    $nextVisited = $Visited + $Name
    $commands = @()

    if ($definition.includes) {
        foreach ($include in $definition.includes) {
            $commands += Resolve-CommandSet -Name $include -Visited $nextVisited
        }
    }

    if ($definition.commands) {
        $commands += $definition.commands
    }

    return $commands
}

function Invoke-MassExecute {
    [CmdletBinding(DefaultParameterSetName = "Commands")]
    param(
        [Parameter(Mandatory = $true, ParameterSetName = "Commands")]
        [string[]]$Commands,
        [Parameter(Mandatory = $true, ParameterSetName = "CommandSets")]
        [string[]]$CommandSetNames
    )

    $resolvedCommands = @()

    if ($PSCmdlet.ParameterSetName -eq "CommandSets") {
        foreach ($name in $CommandSetNames) {
            $resolvedCommands += Resolve-CommandSet -Name $name
        }
    } else {
        $resolvedCommands = $Commands
    }

    if (-not $resolvedCommands -or $resolvedCommands.Count -eq 0) {
        Write-Host "No commands to execute." -ForegroundColor Yellow
        return
    }

    foreach ($command in $resolvedCommands) {
        Write-Host "Executing: $command" -ForegroundColor Cyan
        Invoke-Expression $command
    }

    Write-Host "All commands executed successfully!" -ForegroundColor Green
}

function Invoke-CommandSet {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    Invoke-MassExecute -CommandSetNames @($Name)
}

function Format-CommandEntryLabel {
    param(
        [Parameter(Mandatory = $true)]
        $Entry,
        [Parameter(Mandatory = $true)]
        [int]$Number
    )

    $tagLabel = if ($Entry.tags) { " [" + ($Entry.tags -join ", ") + "]" } else { "" }
    return "$Number. $($Entry.name) - $($Entry.description)$tagLabel"
}

function Invoke-CommandCenter {
    $database = Get-CommandDatabase

    if (-not $database -or $database.Count -eq 0) {
        Write-Host "No command sets are available." -ForegroundColor Yellow
        return
    }

    Write-Host "Select batch operations (comma-separated for multiple):" -ForegroundColor Cyan
    for ($index = 0; $index -lt $database.Count; $index++) {
        $entry = $database[$index]
        $number = $index + 1
        Write-Host (Format-CommandEntryLabel -Entry $entry -Number $number)
    }
    Write-Host "0. Exit"

    $choice = Read-Host "Enter your choice"
    if (-not $choice) {
        Write-Host "No selection made." -ForegroundColor Yellow
        return
    }

    if ($choice -eq "0") {
        Write-Host "Exiting..." -ForegroundColor Yellow
        return
    }

    $selections = $choice -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    $commandSetNames = @()

    foreach ($selection in $selections) {
        $indexValue = 0
        if ([int]::TryParse($selection, [ref]$indexValue)) {
            $resolvedIndex = $indexValue - 1
            if ($resolvedIndex -ge 0 -and $resolvedIndex -lt $database.Count) {
                $commandSetNames += $database[$resolvedIndex].name
            } else {
                Write-Host "Selection '$selection' is out of range." -ForegroundColor Red
            }
        } else {
            $commandSetNames += $selection
        }
    }

    if (-not $commandSetNames -or $commandSetNames.Count -eq 0) {
        Write-Host "No valid selections to run." -ForegroundColor Yellow
        return
    }

    Invoke-MassExecute -CommandSetNames $commandSetNames
}

function command-center {
    Invoke-CommandCenter
}
