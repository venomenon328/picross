param([Parameter(Mandatory)][string]$Python, [Parameter(Mandatory)][string]$Build, [Parameter(Mandatory)][string]$Output)
$ErrorActionPreference = 'Stop'
$principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    & $Python -m tools.production_workspace.smoke_installer --build $Build --output $Output
    if ($LASTEXITCODE -ne 0) { throw 'Non-elevated installer smoke failed' }
    exit
}
# Provision only on the disposable Actions host; never create a user on a local desktop.
if ($env:GITHUB_ACTIONS -ne 'true') { throw 'Use an ordinary non-elevated Windows test user' }
$name = 'pwtest' + [Guid]::NewGuid().ToString('N').Substring(0,10)
$password = ConvertTo-SecureString ([Guid]::NewGuid().ToString('N') + 'aA!7') -AsPlainText -Force
$credential = [pscredential]::new("$env:COMPUTERNAME\$name", $password)
if (Test-Path -LiteralPath $Output) { throw 'Use a new dedicated test output directory' }
New-Item -ItemType Directory -Path $Output | Out-Null
$script = Join-Path $Output 'bootstrap.ps1'
$result = Join-Path $Output 'exit.txt'
$case = Join-Path $Output 'lifecycle'
$source = (Get-Location).Path
try {
    New-LocalUser -Name $name -Password $password -Description 'Ephemeral P4 MSI synthetic test user' | Out-Null
    # Grant only this account access to this new dedicated test directory.
    & icacls.exe $Output /grant "${name}:(OI)(CI)M" /q | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Test output access failed' }
    @"
`$ErrorActionPreference='Stop'
Set-Location -LiteralPath '$($source.Replace("'", "''"))'
& '$($Python.Replace("'", "''"))' -m tools.production_workspace.smoke_installer --build '$($Build.Replace("'", "''"))' --output '$($case.Replace("'", "''"))'
`$code=`$LASTEXITCODE
Set-Content -LiteralPath '$($result.Replace("'", "''"))' -Value `$code
exit `$code
"@ | Set-Content -LiteralPath $script -Encoding utf8
    $process = Start-Process powershell.exe -Credential $credential -LoadUserProfile -WindowStyle Hidden -Wait -PassThru -ArgumentList @('-NoProfile', '-File', $script)
    if ($process.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $result) -or (Get-Content -Raw -LiteralPath $result).Trim() -ne '0') {
        throw 'Actual nonadministrator installer lifecycle failed'
    }
    Get-Content -Raw -LiteralPath (Join-Path $case 'result.json')
} finally {
    Remove-LocalUser -Name $name -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $script,$result -Force -ErrorAction SilentlyContinue
}
