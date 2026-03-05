#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Unified 4-Axis Toolpath Generator - Run all three methods in parallel

.DESCRIPTION
    Orchestrates FreeCAD, Blender, and standalone generators
    Runs them in parallel with consistent parameters
    Compares outputs and generates validation reports

.PARAMETER Diameter
    Cylinder diameter in mm (default: 50)

.PARAMETER Length
    Cylinder length in mm (default: 100)

.PARAMETER Tool
    Tool diameter in mm (default: 6)

.PARAMETER Stepover
    Stepover distance in mm (default: 5)

.PARAMETER Strategy
    Toolpath strategy: HELIX, INDEXED, or SPIRAL (default: HELIX)

.PARAMETER Axis
    Rotary axis: X, Y, or Z (default: X)

.PARAMETER RunAll
    Run all three generators (default)

.PARAMETER RunFreeCAD
    Run only FreeCAD generator

.PARAMETER RunBlender
    Run only Blender generator

.PARAMETER RunStandalone
    Run only standalone generator

.PARAMETER Compare
    Compare outputs after generation

.EXAMPLE
    .\run_all_4axis.ps1

.EXAMPLE
    .\run_all_4axis.ps1 -Diameter 50 -Length 100 -Strategy HELIX

.EXAMPLE
    .\run_all_4axis.ps1 -RunStandalone -Compare
#>

param(
    [float]$Diameter = 50.0,
    [float]$Length = 100.0,
    [float]$Tool = 6.0,
    [float]$Stepover = 5.0,
    [ValidateSet('HELIX', 'INDEXED', 'SPIRAL')]
    [string]$Strategy = 'HELIX',
    [ValidateSet('X', 'Y', 'Z')]
    [string]$Axis = 'X',
    [int]$Feed = 500,
    [int]$Spindle = 12000,
    [switch]$RunAll,
    [switch]$RunFreeCAD,
    [switch]$RunBlender,
    [switch]$RunStandalone,
    [switch]$Compare,
    [switch]$Parallel
)

# Default to running all if no specific generator selected
if (-not $RunFreeCAD -and -not $RunBlender -and -not $RunStandalone) {
    $RunAll = $true
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$OutputDir = Join-Path $ScriptDir "output"

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Unified 4-Axis Toolpath Generator" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Geometry    : ⌀$($Diameter)mm × $($Length)mm"
Write-Host "  Tool        : ⌀$($Tool)mm"
Write-Host "  Strategy    : $Strategy"
Write-Host "  Stepover    : $($Stepover)mm"
Write-Host "  Rotary Axis : $Axis"
Write-Host "  Feed        : $Feed mm/min"
Write-Host "  Spindle     : $Spindle RPM"
Write-Host ""

# Track results
$Results = @{
    FreeCAD    = @{ Success = $false; OutputFile = ""; Duration = 0; Error = "" }
    Blender    = @{ Success = $false; OutputFile = ""; Duration = 0; Error = "" }
    Standalone = @{ Success = $false; OutputFile = ""; Duration = 0; Error = "" }
}

# ============================================================================
# GENERATOR FUNCTIONS
# ============================================================================

function Invoke-FreeCadGenerator {
    Write-Host "━━━ FreeCAD Generator ━━━" -ForegroundColor Green

    $OutputFile = Join-Path $OutputDir "freecad_4axis.gcode"
    $FreeCadScript = Join-Path $ScriptDir "freecad_4axis_generator.py"

    if (-not (Test-Path $FreeCadScript)) {
        Write-Host "✗ Script not found: $FreeCadScript" -ForegroundColor Red
        $Results.FreeCAD.Error = "Script not found"
        return
    }

    $StartTime = Get-Date

    try {
        Write-Host "⏳ Running FreeCAD generator..." -ForegroundColor Cyan

        $Args = @(
            $FreeCadScript,
            "--diameter", $Diameter,
            "--length", $Length,
            "--tool", $Tool,
            "--stepover", $Stepover,
            "--feed", $Feed,
            "--spindle", $Spindle,
            "--axis", $Axis,
            "--output", $OutputFile
        )

        python $Args 2>&1 | ForEach-Object { Write-Host "  $_" }

        if (Test-Path $OutputFile) {
            $Duration = ((Get-Date) - $StartTime).TotalSeconds
            $Results.FreeCAD.Success = $true
            $Results.FreeCAD.OutputFile = $OutputFile
            $Results.FreeCAD.Duration = $Duration
            Write-Host "✓ FreeCAD complete: $OutputFile" -ForegroundColor Green
            Write-Host "  Duration: $([math]::Round($Duration, 2))s" -ForegroundColor Gray
        } else {
            $Results.FreeCAD.Error = "Output file not created"
            Write-Host "✗ FreeCAD failed: No output" -ForegroundColor Red
        }
    } catch {
        $Results.FreeCAD.Error = $_.Exception.Message
        Write-Host "✗ FreeCAD error: $($_.Exception.Message)" -ForegroundColor Red
    }

    Write-Host ""
}

function Invoke-BlenderGenerator {
    Write-Host "━━━ Blender Generator ━━━" -ForegroundColor Green

    $OutputFile = Join-Path $OutputDir "blender_4axis.gcode"
    $BlenderScript = Join-Path $ScriptDir "blendercam_4axis.py"

    if (-not (Test-Path $BlenderScript)) {
        Write-Host "✗ Script not found: $BlenderScript" -ForegroundColor Red
        $Results.Blender.Error = "Script not found"
        return
    }

    # Find Blender executable
    $BlenderPaths = @(
        "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
    )

    $BlenderExe = $BlenderPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

    if (-not $BlenderExe) {
        Write-Host "✗ Blender not found. Install from https://www.blender.org/" -ForegroundColor Red
        $Results.Blender.Error = "Blender not installed"
        return
    }

    $StartTime = Get-Date

    try {
        Write-Host "⏳ Running Blender generator..." -ForegroundColor Cyan
        Write-Host "  Using: $BlenderExe" -ForegroundColor Gray

        $Args = @(
            "--background",
            "--python", $BlenderScript,
            "--",
            "--diameter", $Diameter,
            "--length", $Length,
            "--tool", $Tool,
            "--stepover", $Stepover,
            "--feed", $Feed,
            "--spindle", $Spindle,
            "--strategy", $Strategy,
            "--axis", $Axis,
            "--output", $OutputFile
        )

        & $BlenderExe $Args 2>&1 | Where-Object { $_ -match "✓|✗|⏳|Calculated|Exported" } | ForEach-Object { Write-Host "  $_" }

        if (Test-Path $OutputFile) {
            $Duration = ((Get-Date) - $StartTime).TotalSeconds
            $Results.Blender.Success = $true
            $Results.Blender.OutputFile = $OutputFile
            $Results.Blender.Duration = $Duration
            Write-Host "✓ Blender complete: $OutputFile" -ForegroundColor Green
            Write-Host "  Duration: $([math]::Round($Duration, 2))s" -ForegroundColor Gray
        } else {
            $Results.Blender.Error = "Output file not created"
            Write-Host "✗ Blender failed: No output" -ForegroundColor Red
        }
    } catch {
        $Results.Blender.Error = $_.Exception.Message
        Write-Host "✗ Blender error: $($_.Exception.Message)" -ForegroundColor Red
    }

    Write-Host ""
}

function Invoke-StandaloneGenerator {
    Write-Host "━━━ Standalone Generator ━━━" -ForegroundColor Green

    $OutputFile = Join-Path $OutputDir "standalone_4axis.gcode"
    $StandaloneScript = Join-Path $ScriptDir "standalone_4axis_gcode.py"

    if (-not (Test-Path $StandaloneScript)) {
        Write-Host "✗ Script not found: $StandaloneScript" -ForegroundColor Red
        $Results.Standalone.Error = "Script not found"
        return
    }

    $StartTime = Get-Date

    try {
        Write-Host "⏳ Running standalone generator..." -ForegroundColor Cyan

        $Args = @(
            $StandaloneScript,
            "--diameter", $Diameter,
            "--length", $Length,
            "--tool-diameter", $Tool,
            "--stepover", $Stepover,
            "--feed", $Feed,
            "--spindle", $Spindle,
            "--strategy", $Strategy,
            "--axis", $Axis,
            "--output", $OutputFile,
            "--stats"
        )

        python $Args 2>&1 | ForEach-Object { Write-Host "  $_" }

        if (Test-Path $OutputFile) {
            $Duration = ((Get-Date) - $StartTime).TotalSeconds
            $Results.Standalone.Success = $true
            $Results.Standalone.OutputFile = $OutputFile
            $Results.Standalone.Duration = $Duration
            Write-Host "✓ Standalone complete: $OutputFile" -ForegroundColor Green
            Write-Host "  Duration: $([math]::Round($Duration, 2))s" -ForegroundColor Gray
        } else {
            $Results.Standalone.Error = "Output file not created"
            Write-Host "✗ Standalone failed: No output" -ForegroundColor Red
        }
    } catch {
        $Results.Standalone.Error = $_.Exception.Message
        Write-Host "✗ Standalone error: $($_.Exception.Message)" -ForegroundColor Red
    }

    Write-Host ""
}

# ============================================================================
# EXECUTION
# ============================================================================

if ($Parallel -and $RunAll) {
    Write-Host "Running generators in parallel..." -ForegroundColor Yellow
    Write-Host ""

    $Jobs = @()

    if ($RunAll -or $RunFreeCAD) {
        $Jobs += Start-Job -Name "FreeCAD" -ScriptBlock ${function:Invoke-FreeCadGenerator}
    }

    if ($RunAll -or $RunBlender) {
        $Jobs += Start-Job -Name "Blender" -ScriptBlock ${function:Invoke-BlenderGenerator}
    }

    if ($RunAll -or $RunStandalone) {
        $Jobs += Start-Job -Name "Standalone" -ScriptBlock ${function:Invoke-StandaloneGenerator}
    }

    # Wait for all jobs
    $Jobs | Wait-Job | Receive-Job
    $Jobs | Remove-Job
} else {
    # Run sequentially
    if ($RunAll -or $RunStandalone) {
        Invoke-StandaloneGenerator
    }

    if ($RunAll -or $RunFreeCAD) {
        Invoke-FreeCadGenerator
    }

    if ($RunAll -or $RunBlender) {
        Invoke-BlenderGenerator
    }
}

# ============================================================================
# RESULTS SUMMARY
# ============================================================================

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Results Summary" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$SuccessCount = 0
$TotalTime = 0

foreach ($Generator in $Results.Keys) {
    $Result = $Results[$Generator]

    if ($Result.Success) {
        $SuccessCount++
        $TotalTime += $Result.Duration
        Write-Host "✓ $Generator" -ForegroundColor Green
        Write-Host "    File: $($Result.OutputFile)" -ForegroundColor Gray
        Write-Host "    Time: $([math]::Round($Result.Duration, 2))s" -ForegroundColor Gray

        if (Test-Path $Result.OutputFile) {
            $FileSize = (Get-Item $Result.OutputFile).Length
            $LineCount = (Get-Content $Result.OutputFile).Count
            Write-Host "    Size: $($FileSize) bytes, $LineCount lines" -ForegroundColor Gray
        }
    } else {
        Write-Host "✗ $Generator" -ForegroundColor Red
        if ($Result.Error) {
            Write-Host "    Error: $($Result.Error)" -ForegroundColor Red
        }
    }
    Write-Host ""
}

Write-Host "Success: $SuccessCount / $($Results.Count)" -ForegroundColor $(if ($SuccessCount -eq $Results.Count) { "Green" } else { "Yellow" })
Write-Host "Total Time: $([math]::Round($TotalTime, 2))s" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# COMPARISON
# ============================================================================

if ($Compare -and $SuccessCount -ge 2) {
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  Output Comparison" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""

    $ValidatorScript = Join-Path $ScriptDir "validate_gcode.ps1"

    if (Test-Path $ValidatorScript) {
        foreach ($Generator in $Results.Keys) {
            if ($Results[$Generator].Success) {
                $File = $Results[$Generator].OutputFile
                Write-Host "━━━ $Generator ━━━" -ForegroundColor Yellow
                & $ValidatorScript -GCodePath $File -Silent | Select-Object -First 15
                Write-Host ""
            }
        }
    }

    # Side-by-side comparison
    Write-Host "━━━ Side-by-Side Comparison ━━━" -ForegroundColor Yellow

    $SuccessfulFiles = $Results.Values | Where-Object { $_.Success } | ForEach-Object { $_.OutputFile }

    if ($SuccessfulFiles.Count -ge 2) {
        $CompareScript = Join-Path $ScriptDir "compare_gcode.ps1"

        if (Test-Path $CompareScript) {
            & $CompareScript -OriginalFile $SuccessfulFiles[0] -NewFile $SuccessfulFiles[1]
        }
    }
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "✅ All generators complete!" -ForegroundColor Green
Write-Host "   Output directory: $OutputDir" -ForegroundColor Gray
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
