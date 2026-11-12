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
$script = Join-Path $PSScriptRoot 'smoke-bootstrap.ps1'
$result = Join-Path $Output 'exit.txt'
$case = Join-Path $Output 'lifecycle'
$source = (Get-Location).Path
$stdout = Join-Path $Output 'stdout.log'
$stderr = Join-Path $Output 'stderr.log'
try {
    New-LocalUser -Name $name -Password $password -Description 'Ephemeral P4 MSI synthetic test user' | Out-Null
    # Grant only this account access to this new dedicated test directory.
    & icacls.exe $Output /grant "${name}:(OI)(CI)M" /q | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Test output access failed' }
    # Start-Process joins ArgumentList: quote each file/directory explicitly.
    $arguments = @('-NoProfile', '-File', "`"$script`"", '-Python', "`"$Python`"", '-Build', "`"$Build`"", '-Output', "`"$Output`"", '-Source', "`"$source`"")
    $process = Start-Process powershell.exe -Credential $credential -LoadUserProfile -WindowStyle Hidden -Wait -PassThru -ArgumentList $arguments -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    Get-Content -Raw -LiteralPath $stdout,$stderr -Encoding utf8
    if ($process.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $result) -or (Get-Content -Raw -LiteralPath $result).Trim() -ne '0') {
        throw "Actual nonadministrator installer lifecycle failed (process exit $($process.ExitCode)); see child output above"
    }
    Get-Content -Raw -LiteralPath (Join-Path $case 'result.json')
} finally {
    Remove-LocalUser -Name $name -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $result -Force -ErrorAction SilentlyContinue
}
