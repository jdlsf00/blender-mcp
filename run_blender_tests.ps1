param(
    [string]$BlenderExecutable
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if ($BlenderExecutable) {
    $env:BLENDER_EXECUTABLE = $BlenderExecutable
}

pytest -c pytest.blender.ini -q
