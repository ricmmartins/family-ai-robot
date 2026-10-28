param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^COM[1-9][0-9]*$')]
    [string]$Port
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$folder = Join-Path $PSScriptRoot 'firmware-built'
$binary = Join-Path $folder 'robot.bin'
$manifestPath = Join-Path $folder 'manifest.json'
if (-not (Test-Path $binary) -or -not (Test-Path $manifestPath)) {
    throw 'Missing built firmware. Extract robo-de-mesa-completo.zip from release Assets. Source code ZIP does not include robot.bin. See the illustrated guide; rebuilding is optional.'
}
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
$hash = (Get-FileHash $binary -Algorithm SHA256).Hash.ToLowerInvariant()
if ($manifest.board -ne 'xiao-family-robot' -or $hash -ne $manifest.sha256) {
    throw 'Firmware identity or SHA256 check failed. Do not flash.'
}
Write-Host 'Disconnect the servo supply and LiPo. Flashing writes firmware and may overwrite settings.'
Write-Host "Target port: $Port"
$localPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$python = if (Test-Path -LiteralPath $localPython) { $localPython } else { 'python' }
& $python -m esptool --chip esp32s3 --port $Port --baud 115200 write-flash --flash-size 8MB 0x0 $binary
if ($LASTEXITCODE -ne 0) { throw 'Flashing failed. Check COM port, data cable and BOOT mode.' }
Write-Host 'Flash transfer complete. This does NOT prove the hardware works. Continue with the guide.'
