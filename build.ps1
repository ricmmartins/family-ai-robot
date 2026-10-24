$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not (Get-Command idf.py -ErrorAction SilentlyContinue)) {
    throw 'Open the ESP-IDF 6.0.1 PowerShell terminal first. See the guide.'
}
$version = (& idf.py --version | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $version -notmatch '\bv6\.0\.1(?:$|[\s-])') {
    throw "This package targets ESP-IDF v6.0.1. Found: $version"
}
$source = Join-Path $PSScriptRoot 'work\xiaozhi'
if (-not (Test-Path (Join-Path $source '.family-robot.json'))) {
    throw 'Run python .\prepare_source.py first.'
}
Push-Location $source
try {
    $env:CMAKE_NINJA_FORCE_RESPONSE_FILE = '1'
    & python .\scripts\build.py xiao-family-robot --language en-US --wake-word disabled
    if ($LASTEXITCODE -ne 0) { throw 'Firmware build failed. Do not proceed to flashing.' }
    if (-not (Test-Path '.\build\merged-binary.bin')) {
        throw 'Build did not produce merged-binary.bin.'
    }
    & python (Join-Path $PSScriptRoot 'package_firmware.py')
    if ($LASTEXITCODE -ne 0) { throw 'Firmware packaging failed.' }
    Write-Host 'Build complete. Use flash.ps1 with the real COM port.'
} finally {
    Pop-Location
}
