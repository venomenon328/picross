param(
    [Parameter(Mandatory = $true)][string]$Exe,
    [Parameter(Mandatory = $true)][string]$Profile,
    [ValidateSet('Start', 'Status', 'BlockSave', 'UnblockSave', 'HidePrimary')]
    [string]$Action = 'Start'
)

$ErrorActionPreference = 'Stop'
$tempRoot = [System.IO.Path]::GetFullPath($env:TEMP).TrimEnd('\')
$profileRoot = [System.IO.Path]::GetFullPath($Profile).TrimEnd('\')
if (-not $profileRoot.StartsWith($tempRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Das Testprofil muss ein eigener Unterordner von TEMP sein.'
}
$marker = Join-Path $profileRoot '.picross-p14-owner-profile'
$saveRoot = Join-Path $profileRoot 'appdata\Godot\app_userdata\picross · P1\p1\saves'
$primary = Join-Path $saveRoot 'f03.json'
$backup = Join-Path $saveRoot 'f03.bak'
$temporary = Join-Path $saveRoot 'f03.tmp'

if ($Action -eq 'Start') {
    $resolvedExe = (Resolve-Path -LiteralPath $Exe).Path
    if (-not [System.IO.Path]::GetFileName($resolvedExe).Equals('picross-p1.exe', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'Erwartet wird picross-p1.exe aus dem geprüften ZIP.'
    }
    if ((Test-Path -LiteralPath $profileRoot) -and -not (Test-Path -LiteralPath $marker -PathType Leaf)) {
        throw 'Der bestehende TEMP-Ordner gehört nicht zu dieser Probe; einen neuen Profilpfad wählen.'
    }
    [void](New-Item -ItemType Directory -Path $profileRoot -Force)
    [void](New-Item -ItemType Directory -Path (Join-Path $profileRoot 'appdata') -Force)
    [void](New-Item -ItemType Directory -Path (Join-Path $profileRoot 'localappdata') -Force)
    if (-not (Test-Path -LiteralPath $marker)) {
        [System.IO.File]::WriteAllText($marker, 'P1.4 isolated owner probe profile')
    }
    $priorAppData = $env:APPDATA
    $priorLocalAppData = $env:LOCALAPPDATA
    try {
        $env:APPDATA = Join-Path $profileRoot 'appdata'
        $env:LOCALAPPDATA = Join-Path $profileRoot 'localappdata'
        Write-Host "Isoliertes Testprofil: $profileRoot"
        $process = Start-Process -FilePath $resolvedExe -WorkingDirectory (Split-Path -Parent $resolvedExe) -PassThru -Wait
        Write-Host "Programm beendet mit Exitcode $($process.ExitCode)"
    } finally {
        $env:APPDATA = $priorAppData
        $env:LOCALAPPDATA = $priorLocalAppData
    }
    exit $process.ExitCode
}

if (-not (Test-Path -LiteralPath $marker -PathType Leaf)) {
    throw 'Testprofil-Marker fehlt. Zuerst Start mit diesem TEMP-Profil ausführen.'
}
if ($Action -eq 'Status') {
    Write-Host "Testprofil: $profileRoot"
    foreach ($path in @($primary, $backup, $temporary)) {
        $kind = if (Test-Path -LiteralPath $path -PathType Container) { 'Verzeichnis' } elseif (Test-Path -LiteralPath $path -PathType Leaf) { 'Datei' } else { 'fehlt' }
        Write-Host "$([System.IO.Path]::GetFileName($path)): $kind"
    }
    exit 0
}
if (-not (Test-Path -LiteralPath $saveRoot -PathType Container)) {
    throw 'Noch kein F-03-Speicherordner im isolierten Testprofil.'
}

switch ($Action) {
    'BlockSave' {
        if (Test-Path -LiteralPath $temporary) { throw 'f03.tmp existiert bereits; keine Änderung ausgeführt.' }
        [void](New-Item -ItemType Directory -Path $temporary)
        Write-Host 'Nächster F-03-Speicherversuch wird durch den Testordner f03.tmp blockiert.'
    }
    'UnblockSave' {
        if (-not (Test-Path -LiteralPath $temporary -PathType Container)) { throw 'Kein Testordner f03.tmp vorhanden.' }
        if (@(Get-ChildItem -LiteralPath $temporary -Force).Count -ne 0) { throw 'Testordner ist nicht leer; keine Änderung ausgeführt.' }
        Remove-Item -LiteralPath $temporary
        Write-Host 'Testblockade entfernt; den in der App gesperrten Übergang erneut versuchen.'
    }
    'HidePrimary' {
        if (-not (Test-Path -LiteralPath $primary -PathType Leaf) -or -not (Test-Path -LiteralPath $backup -PathType Leaf)) {
            throw 'F-03 benötigt ein Primary und Backup im isolierten Testprofil. In der App zuerst zwei wirksame Aktionen speichern.'
        }
        $held = Join-Path $saveRoot 'f03.owner-held'
        if (Test-Path -LiteralPath $held) { throw 'f03.owner-held existiert bereits; keine Änderung ausgeführt.' }
        Move-Item -LiteralPath $primary -Destination $held
        Write-Host 'Nur das isolierte F-03-Primary wurde beiseitegelegt. Die App sollte jetzt Backup-Recovery anzeigen.'
    }
}
