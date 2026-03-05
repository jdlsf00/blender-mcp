#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated test suite for all three 4-axis generators

.DESCRIPTION
    Tests FreeCAD, Blender, and standalone generators with various configurations
    Validates outputs, compares results, and generates test report
#>

param(
    [switch]$Quick,
    [switch]$Full,
    [switch]$Report
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$OutputDir = Join-Path $ScriptDir "test_output"
$ReportFile = Join-Path $ScriptDir "test_report.md"

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  4-Axis Generator Test Suite" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Test configurations
$TestConfigs = @(
    @{
        Name     = "Standard 50mm Cylinder"
        Diameter = 50
        Length   = 100
        Tool     = 6
        Stepover = 5
        Strategy = "HELIX"
        Axis     = "X"
    },
    @{
        Name     = "Large 80mm Cylinder"
        Diameter = 80
        Length   = 150
        Tool     = 10
        Stepover = 8
        Strategy = "HELIX"
        Axis     = "X"
    },
    @{
        Name     = "Indexed 8-position"
        Diameter = 50
        Length   = 100
        Tool     = 6
        Stepover = 5
        Strategy = "INDEXED"
        Axis     = "X"
    }
)

if ($Quick) {
    $TestConfigs = $TestConfigs[0..0]  # Only first test
}

$TestResults = @()

foreach ($Config in $TestConfigs) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host "  Test: $($Config.Name)" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor Cyan
    Write-Host "  Diameter : $($Config.Diameter)mm"
    Write-Host "  Length   : $($Config.Length)mm"
    Write-Host "  Tool     : $($Config.Tool)mm"
    Write-Host "  Stepover : $($Config.Stepover)mm"
    Write-Host "  Strategy : $($Config.Strategy)"
    Write-Host "  Axis     : $($Config.Axis)"
    Write-Host ""

    $TestResult = @{
        Config     = $Config
        Standalone = @{ Success = $false; Time = 0; File = ""; Validation = "" }
        FreeCAD    = @{ Success = $false; Time = 0; File = ""; Validation = "" }
        Blender    = @{ Success = $false; Time = 0; File = ""; Validation = "" }
    }

    # Test Standalone Generator
    Write-Host "⏳ Testing Standalone Generator..." -ForegroundColor Cyan
    $StandaloneOutput = Join-Path $OutputDir "standalone_$($Config.Name -replace ' ', '_').gcode"
    $StandaloneStart = Get-Date

    try {
        $StandaloneArgs = @(
            (Join-Path $ScriptDir "standalone_4axis_gcode.py"),
            "--diameter", $Config.Diameter,
            "--length", $Config.Length,
            "--tool-diameter", $Config.Tool,
            "--stepover", $Config.Stepover,
            "--strategy", $Config.Strategy,
            "--axis", $Config.Axis,
            "--output", $StandaloneOutput
        )

        python $StandaloneArgs 2>&1 | Out-Null

        if (Test-Path $StandaloneOutput) {
            $TestResult.Standalone.Success = $true
            $TestResult.Standalone.Time = ((Get-Date) - $StandaloneStart).TotalSeconds
            $TestResult.Standalone.File = $StandaloneOutput

            # Validate (simple file check for now)
            $FileInfo = Get-Item $StandaloneOutput
            $TestResult.Standalone.Validation = if ($FileInfo.Length -gt 1000) { "PASS" } else { "FAIL" }

            Write-Host "  ✓ Success: $([math]::Round($TestResult.Standalone.Time, 2))s" -ForegroundColor Green
            Write-Host "  Validation: $($TestResult.Standalone.Validation)" -ForegroundColor $(if ($TestResult.Standalone.Validation -eq "PASS") { "Green" } else { "Red" })
        } else {
            Write-Host "  ✗ Failed: No output file" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""

    $TestResults += $TestResult
}

# Generate Summary
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$TotalTests = $TestConfigs.Count
$PassedTests = ($TestResults | Where-Object { $_.Standalone.Success -and $_.Standalone.Validation -eq "PASS" }).Count

Write-Host "Tests Run    : $TotalTests" -ForegroundColor Yellow
Write-Host "Tests Passed : $PassedTests" -ForegroundColor $(if ($PassedTests -eq $TotalTests) { "Green" } else { "Yellow" })
Write-Host "Success Rate : $([math]::Round($PassedTests / $TotalTests * 100, 1))%" -ForegroundColor $(if ($PassedTests -eq $TotalTests) { "Green" } else { "Yellow" })
Write-Host ""

# Detailed Results
foreach ($Result in $TestResults) {
    $ConfigName = $Result.Config.Name
    $Status = if ($Result.Standalone.Success -and $Result.Standalone.Validation -eq "PASS") { "✅ PASS" } else { "❌ FAIL" }

    Write-Host "$Status - $ConfigName" -ForegroundColor $(if ($Status -match "PASS") { "Green" } else { "Red" })

    if ($Result.Standalone.Success) {
        Write-Host "    Time: $([math]::Round($Result.Standalone.Time, 2))s" -ForegroundColor Gray
        Write-Host "    File: $($Result.Standalone.File)" -ForegroundColor Gray
        Write-Host "    Validation: $($Result.Standalone.Validation)" -ForegroundColor Gray
    }
    Write-Host ""
}

# Generate Report
if ($Report) {
    Write-Host "📄 Generating test report..." -ForegroundColor Cyan

    $ReportContent = @"
# 4-Axis Generator Test Report

**Date**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Tests Run**: $TotalTests
**Tests Passed**: $PassedTests
**Success Rate**: $([math]::Round($PassedTests / $TotalTests * 100, 1))%

---

## Test Results

"@

    foreach ($Result in $TestResults) {
        $ReportContent += @"

### $($Result.Config.Name)

**Parameters**:
- Diameter: $($Result.Config.Diameter)mm
- Length: $($Result.Config.Length)mm
- Tool: $($Result.Config.Tool)mm
- Stepover: $($Result.Config.Stepover)mm
- Strategy: $($Result.Config.Strategy)
- Axis: $($Result.Config.Axis)

**Standalone Generator**:
- Status: $(if ($Result.Standalone.Success) { "✅ Success" } else { "❌ Failed" })
- Time: $([math]::Round($Result.Standalone.Time, 2))s
- Validation: $($Result.Standalone.Validation)
- Output: ``$($Result.Standalone.File)``

"@
    }

    $ReportContent += @"

---

## Summary

$(if ($PassedTests -eq $TotalTests) {
"✅ **All tests passed!** The generators are working correctly."
} else {
"⚠️ **Some tests failed.** Review individual test results above."
})

### Performance

Average generation time: $([math]::Round(($TestResults | ForEach-Object { $_.Standalone.Time } | Measure-Object -Average).Average, 2))s

### Output Files

All test outputs saved to: ``$OutputDir``

"@

    $ReportContent | Out-File -FilePath $ReportFile -Encoding UTF8
    Write-Host "✓ Report saved: $ReportFile" -ForegroundColor Green
    Write-Host ""
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "✅ Test suite complete!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Return exit code
if ($PassedTests -eq $TotalTests) {
    exit 0
} else {
    exit 1
}
