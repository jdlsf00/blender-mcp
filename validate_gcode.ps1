# G-Code Validation Script
# Analyzes generated G-code to verify scale, units, and A-axis commands
# Usage: .\validate_gcode.ps1 -GCodePath "path\to\file.gcode"

param(
    [Parameter(Mandatory = $false)]
    [string]$GCodePath = "F:\Documents\CODE\Blender-MCP\reference_projects\blender_helix_reference.gcode",
    [switch]$Silent
)

if (-not $Silent) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  G-CODE VALIDATION REPORT" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

# Check if file exists
if (-not (Test-Path $GCodePath)) {
    if (-not $Silent) {
        Write-Host "❌ ERROR: File not found!" -ForegroundColor Red
        Write-Host "   Path: $GCodePath" -ForegroundColor Yellow
        Write-Host "`n💡 Generate the file first by following VALIDATION_CHECKLIST.md" -ForegroundColor Cyan
    }
    return "FAIL"
}

$file = Get-Item $GCodePath
if (-not $Silent) {
    Write-Host "📄 File Information:" -ForegroundColor Green
    Write-Host "   Path: $($file.FullName)"
    Write-Host "   Size: $([math]::Round($file.Length/1KB, 1)) KB"
    Write-Host "   Modified: $($file.LastWriteTime)"
}

# Read file content
$content = Get-Content $GCodePath
$lineCount = $content.Count
if (-not $Silent) {
    Write-Host "   Lines: $lineCount"
    Write-Host "`n🔍 Validation Checks:" -ForegroundColor Yellow
}

# Check 1: Units (G21 = millimeters)
if (-not $Silent) { Write-Host "`n1. UNITS CHECK:" }
$hasG21 = $content | Select-String -Pattern "G21" -Quiet
$hasG20 = $content | Select-String -Pattern "G20" -Quiet

if (-not $Silent) {
    if ($hasG21) {
        Write-Host "   ✅ G21 found - Using MILLIMETERS" -ForegroundColor Green
    } elseif ($hasG20) {
        Write-Host "   ⚠️  G20 found - Using INCHES (check if intentional)" -ForegroundColor Yellow
    } else {
        Write-Host "   ❌ No G20/G21 found - Units unclear!" -ForegroundColor Red
    }
}

# Check 2: Coordinate Scale
Write-Host "`n2. COORDINATE SCALE CHECK:"
$xCoords = @()
$yCoords = @()
$zCoords = @()

# Sample first 1000 lines for coordinate analysis
$sampleLines = $content | Select-Object -First 1000 | Where-Object { $_ -match "^G[01]" }

foreach ($line in $sampleLines) {
    if ($line -match "X(-?\d+\.?\d*)") { $xCoords += [float]$matches[1] }
    if ($line -match "Y(-?\d+\.?\d*)") { $yCoords += [float]$matches[1] }
    if ($line -match "Z(-?\d+\.?\d*)") { $zCoords += [float]$matches[1] }
}

if ($xCoords.Count -gt 0) {
    $xMin = [math]::Round(($xCoords | Measure-Object -Minimum).Minimum, 2)
    $xMax = [math]::Round(($xCoords | Measure-Object -Maximum).Maximum, 2)
    $xRange = [math]::Abs($xMax - $xMin)

    Write-Host "   X-Axis: $xMin to $xMax mm (range: $([math]::Round($xRange, 1))mm)"

    # Expected cylinder length = 100mm, so X should be around ±50mm
    if ($xRange -gt 10 -and $xRange -lt 200) {
        Write-Host "   ✅ X range looks correct for 100mm cylinder" -ForegroundColor Green
    } elseif ($xRange -gt 10000) {
        Write-Host "   ❌ X range is HUGE! Scale error (50,000mm = 50 meters!)" -ForegroundColor Red
        Write-Host "      Problem: Blender units likely set to METERS instead of MILLIMETERS" -ForegroundColor Yellow
    } elseif ($xRange -lt 1) {
        Write-Host "   ❌ X range is TINY! Scale error (0.05mm instead of 50mm)" -ForegroundColor Red
        Write-Host "      Problem: Unit scale factor might be 0.001 instead of 1.0" -ForegroundColor Yellow
    }
}

if ($yCoords.Count -gt 0) {
    $yMin = [math]::Round(($yCoords | Measure-Object -Minimum).Minimum, 2)
    $yMax = [math]::Round(($yCoords | Measure-Object -Maximum).Maximum, 2)
    $yRange = [math]::Abs($yMax - $yMin)

    Write-Host "   Y-Axis: $yMin to $yMax mm (range: $([math]::Round($yRange, 1))mm)"

    # Expected cylinder diameter = 50mm, so Y should be around ±25mm
    if ($yRange -gt 10 -and $yRange -lt 100) {
        Write-Host "   ✅ Y range looks correct for 50mm diameter" -ForegroundColor Green
    } elseif ($yRange -gt 10000) {
        Write-Host "   ❌ Y range is HUGE! Scale error detected" -ForegroundColor Red
    }
}

if ($zCoords.Count -gt 0) {
    $zMin = [math]::Round(($zCoords | Measure-Object -Minimum).Minimum, 2)
    $zMax = [math]::Round(($zCoords | Measure-Object -Maximum).Maximum, 2)

    Write-Host "   Z-Axis: $zMin to $zMax mm"

    if ($zMax -gt 1000) {
        Write-Host "   ❌ Z values are HUGE! Scale error detected" -ForegroundColor Red
    } else {
        Write-Host "   ✅ Z range looks reasonable" -ForegroundColor Green
    }
}

# Check 3: A-Axis (Rotary) Commands
Write-Host "`n3. A-AXIS (ROTARY) CHECK:"
$aCommands = $content | Select-String -Pattern " A(-?\d+\.?\d*)"

if ($aCommands.Count -gt 0) {
    Write-Host "   ✅ A-axis commands found: $($aCommands.Count) instances" -ForegroundColor Green

    # Extract A values
    $aValues = @()
    foreach ($cmd in ($aCommands | Select-Object -First 100)) {
        if ($cmd -match "A(-?\d+\.?\d*)") {
            $aValues += [float]$matches[1]
        }
    }

    if ($aValues.Count -gt 0) {
        $aMin = [math]::Round(($aValues | Measure-Object -Minimum).Minimum, 2)
        $aMax = [math]::Round(($aValues | Measure-Object -Maximum).Maximum, 2)
        $aRotations = [math]::Round($aMax / 360, 1)

        Write-Host "   A-Axis: $aMin° to $aMax° ($aRotations rotations)"

        # Expected: ~51 rotations for helix = ~18,355°
        if ($aMax -gt 15000 -and $aMax -lt 20000) {
            Write-Host "   ✅ Rotation range correct (~51 rotations expected)" -ForegroundColor Green
        } elseif ($aMax -lt 360) {
            Write-Host "   ⚠️  Only $aRotations rotation(s) - check strategy settings" -ForegroundColor Yellow
        }
    }

    # Show sample A commands
    Write-Host "`n   Sample A-axis commands:"
    $aCommands | Select-Object -First 5 | ForEach-Object {
        Write-Host "      $($_.Line)" -ForegroundColor Gray
    }
} else {
    Write-Host "   ❌ NO A-AXIS COMMANDS FOUND!" -ForegroundColor Red
    Write-Host "      Problem: Either not 4-axis or A-axis not enabled" -ForegroundColor Yellow
}

# Check 4: Tool Commands
Write-Host "`n4. TOOL COMMANDS CHECK:"
$toolChange = $content | Select-String -Pattern "T\d+" | Select-Object -First 1
$spindleOn = $content | Select-String -Pattern "M3|M4" | Select-Object -First 1
$feedRate = $content | Select-String -Pattern "F\d+" | Select-Object -First 1

if ($toolChange) {
    Write-Host "   ✅ Tool change: $($toolChange.Line.Trim())" -ForegroundColor Green
}
if ($spindleOn) {
    Write-Host "   ✅ Spindle command: $($spindleOn.Line.Trim())" -ForegroundColor Green
}
if ($feedRate) {
    Write-Host "   ✅ Feed rate: $($feedRate.Line.Trim())" -ForegroundColor Green
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$issuesFound = 0

if (-not $hasG21 -and -not $hasG20) {
    Write-Host "❌ Units not specified" -ForegroundColor Red
    $issuesFound++
}

if ($xRange -gt 10000 -or $yRange -gt 10000 -or $zMax -gt 1000) {
    Write-Host "❌ CRITICAL: Scale error detected (coordinates 1000x too large)" -ForegroundColor Red
    Write-Host "   ACTION REQUIRED: Check Blender Scene Properties → Units" -ForegroundColor Yellow
    Write-Host "   Must be: METRIC, Millimeters, Scale 1.0" -ForegroundColor Yellow
    $issuesFound++
}

if ($aCommands.Count -eq 0) {
    Write-Host "❌ CRITICAL: No A-axis commands (not 4-axis G-code)" -ForegroundColor Red
    Write-Host "   ACTION REQUIRED: Enable A-axis in machine config" -ForegroundColor Yellow
    $issuesFound++
}

if ($issuesFound -eq 0) {
    Write-Host "✅ All checks passed! G-code appears valid." -ForegroundColor Green
    Write-Host "   Ready for simulation in CAMotics or NC Viewer" -ForegroundColor Cyan
} else {
    Write-Host "`n⚠️  $issuesFound issue(s) found - review above" -ForegroundColor Yellow
    Write-Host "   Refer to VALIDATION_CHECKLIST.md for troubleshooting" -ForegroundColor Cyan
}

Write-Host "`n========================================`n" -ForegroundColor Cyan
