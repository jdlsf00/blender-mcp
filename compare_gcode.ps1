# Compare Original vs New G-code - Quick Validation
# Shows side-by-side comparison of coordinates to verify scale fix

param(
    [string]$NewGCodePath = "F:\Documents\CODE\Blender-MCP\reference_projects\blender_helix_reference.gcode",
    [string]$OriginalGCodePath = "F:\Documents\CODE\Blender-MCP\helix_test_4axis.gcode"
)

$ErrorActionPreference = "Continue"

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   4-Axis G-code Comparison - Original vs Corrected        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check if files exist
$originalExists = Test-Path $OriginalGCodePath
$newExists = Test-Path $NewGCodePath

Write-Host "━━━ File Status ━━━" -ForegroundColor Cyan

if ($originalExists) {
    $origInfo = Get-Item $OriginalGCodePath
    Write-Host "✓ Original: " -ForegroundColor Green -NoNewline
    Write-Host "$($origInfo.Name) " -NoNewline
    Write-Host "($([math]::Round($origInfo.Length/1KB,1)) KB)" -ForegroundColor DarkGray
} else {
    Write-Host "✗ Original not found: $OriginalGCodePath" -ForegroundColor Red
}

if ($newExists) {
    $newInfo = Get-Item $NewGCodePath
    Write-Host "✓ New:      " -ForegroundColor Green -NoNewline
    Write-Host "$($newInfo.Name) " -NoNewline
    Write-Host "($([math]::Round($newInfo.Length/1KB,1)) KB)" -ForegroundColor DarkGray
} else {
    Write-Host "✗ New G-code not found: $NewGCodePath" -ForegroundColor Yellow
    Write-Host "`n💡 Generate G-code first:" -ForegroundColor Yellow
    Write-Host "   1. Open Blender with 4axis_helix_reference.blend" -ForegroundColor White
    Write-Host "   2. Configure Fabex CAM operation" -ForegroundColor White
    Write-Host "   3. Export G-code to: reference_projects\blender_helix_reference.gcode" -ForegroundColor White
    Write-Host "`nSee: QUICK_START_FABEX.md for detailed instructions`n" -ForegroundColor DarkGray
    exit 1
}

if (-not $originalExists) {
    Write-Host "`n⚠️  Original file not found, comparing new file only...`n" -ForegroundColor Yellow
}

# Function to extract sample coordinates
function Get-GCodeSample {
    param([string]$FilePath, [int]$LineCount = 50)

    $content = Get-Content $FilePath -TotalCount $LineCount
    $moves = $content | Where-Object { $_ -match '^G[01]' }

    return $moves
}

# Function to extract coordinate range
function Get-CoordinateRange {
    param([string]$FilePath, [string]$Axis)

    $content = Get-Content $FilePath -TotalCount 1000
    $pattern = "$Axis([-\d.]+)"

    $values = @()
    foreach ($line in $content) {
        if ($line -match $pattern) {
            $values += [double]$matches[1]
        }
    }

    if ($values.Count -eq 0) {
        return @{Min = "N/A"; Max = "N/A"; Range = "N/A" }
    }

    $min = ($values | Measure-Object -Minimum).Minimum
    $max = ($values | Measure-Object -Maximum).Maximum
    $range = $max - $min

    return @{
        Min   = [math]::Round($min, 3)
        Max   = [math]::Round($max, 3)
        Range = [math]::Round($range, 3)
    }
}

# Compare coordinates
Write-Host "`n━━━ Coordinate Comparison ━━━" -ForegroundColor Cyan

$axes = @('X', 'Y', 'Z', 'A')

foreach ($axis in $axes) {
    Write-Host "`n$axis-Axis:" -ForegroundColor White

    if ($originalExists) {
        $origRange = Get-CoordinateRange -FilePath $OriginalGCodePath -Axis $axis
        Write-Host "  Original: " -ForegroundColor Red -NoNewline
        Write-Host "Min: $($origRange.Min), Max: $($origRange.Max), Range: $($origRange.Range) mm" -ForegroundColor DarkGray

        # Detect scale errors
        if ($axis -ne 'A' -and $origRange.Range -ne "N/A" -and $origRange.Range -gt 10000) {
            Write-Host "    ❌ SCALE ERROR! " -ForegroundColor Red -NoNewline
            Write-Host "($($origRange.Range)mm = $([math]::Round($origRange.Range/1000,1)) METERS!)" -ForegroundColor Red
        }
    }

    if ($newExists) {
        $newRange = Get-CoordinateRange -FilePath $NewGCodePath -Axis $axis
        Write-Host "  New:      " -ForegroundColor Green -NoNewline
        Write-Host "Min: $($newRange.Min), Max: $($newRange.Max), Range: $($newRange.Range) mm" -ForegroundColor DarkGray

        # Validate expected ranges
        if ($axis -eq 'X' -and $newRange.Range -ne "N/A") {
            if ($newRange.Range -gt 50 -and $newRange.Range -lt 200) {
                Write-Host "    ✅ Scale looks correct!" -ForegroundColor Green
            } elseif ($newRange.Range -gt 1000) {
                Write-Host "    ❌ Still has scale error!" -ForegroundColor Red
            }
        }

        if ($axis -eq 'Y' -and $newRange.Range -ne "N/A") {
            if ($newRange.Range -gt 20 -and $newRange.Range -lt 100) {
                Write-Host "    ✅ Scale looks correct!" -ForegroundColor Green
            }
        }

        if ($axis -eq 'A' -and $newRange.Range -ne "N/A") {
            $rotations = [math]::Round($newRange.Range / 360, 1)
            Write-Host "    ℹ️  Total rotations: $rotations" -ForegroundColor Cyan
            if ($rotations -gt 30 -and $rotations -lt 100) {
                Write-Host "    ✅ Rotation count looks reasonable!" -ForegroundColor Green
            }
        }
    }
}

# Sample G-code comparison
Write-Host "`n━━━ Sample G-code Lines ━━━" -ForegroundColor Cyan

if ($originalExists) {
    Write-Host "`nOriginal (WRONG - 1000x scale error):" -ForegroundColor Red
    $origSample = Get-GCodeSample -FilePath $OriginalGCodePath
    $origSample | Select-Object -First 5 | ForEach-Object {
        Write-Host "  $_" -ForegroundColor DarkGray
    }
}

if ($newExists) {
    Write-Host "`nNew (Should be CORRECT):" -ForegroundColor Green
    $newSample = Get-GCodeSample -FilePath $NewGCodePath
    $newSample | Select-Object -First 5 | ForEach-Object {
        Write-Host "  $_" -ForegroundColor DarkGray
    }
}

# Units check
Write-Host "`n━━━ Units Check ━━━" -ForegroundColor Cyan

if ($originalExists) {
    $origContent = Get-Content $OriginalGCodePath -TotalCount 50
    $origUnits = if ($origContent -match 'G21') { "G21 (Millimeters) ✓" }
    elseif ($origContent -match 'G20') { "G20 (Inches)" }
    else { "Not specified ✗" }
    Write-Host "  Original: $origUnits" -ForegroundColor DarkGray
}

if ($newExists) {
    $newContent = Get-Content $NewGCodePath -TotalCount 50
    $newUnits = if ($newContent -match 'G21') { "G21 (Millimeters) ✓" }
    elseif ($newContent -match 'G20') { "G20 (Inches)" }
    else { "Not specified ✗" }

    if ($newContent -match 'G21') {
        Write-Host "  New:      $newUnits" -ForegroundColor Green
    } else {
        Write-Host "  New:      $newUnits" -ForegroundColor Yellow
    }
}

# Final verdict
Write-Host "`n━━━ Verdict ━━━" -ForegroundColor Cyan

if ($newExists) {
    $newXRange = Get-CoordinateRange -FilePath $NewGCodePath -Axis 'X'
    $newYRange = Get-CoordinateRange -FilePath $NewGCodePath -Axis 'Y'
    $newARange = Get-CoordinateRange -FilePath $NewGCodePath -Axis 'A'

    $scaleOK = ($newXRange.Range -ne "N/A" -and $newXRange.Range -lt 1000)
    $unitsOK = (Get-Content $NewGCodePath -TotalCount 50) -match 'G21'
    $axisOK = ($newARange.Range -ne "N/A")

    if ($scaleOK -and $unitsOK -and $axisOK) {
        Write-Host "`n✅ SUCCESS! G-code looks CORRECT!" -ForegroundColor Green
        Write-Host "   • Scale fixed (coordinates in millimeters)" -ForegroundColor Green
        Write-Host "   • G21 present (millimeter mode)" -ForegroundColor Green
        Write-Host "   • A-axis commands present (rotary motion)" -ForegroundColor Green
        Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
        Write-Host "   1. Run full validation: .\validate_gcode.ps1" -ForegroundColor White
        Write-Host "   2. Simulate in CAMotics or NC Viewer" -ForegroundColor White
        Write-Host "   3. Air cut on machine (Z +50mm offset)" -ForegroundColor White
    } elseif (-not $scaleOK) {
        Write-Host "`n❌ SCALE ERROR STILL PRESENT!" -ForegroundColor Red
        Write-Host "   X Range: $($newXRange.Range)mm (should be ~100-150mm)" -ForegroundColor Red
        Write-Host "`n🔧 Troubleshooting:" -ForegroundColor Yellow
        Write-Host "   1. Check Blender: Scene Properties → Units" -ForegroundColor White
        Write-Host "      • Unit System: Metric" -ForegroundColor White
        Write-Host "      • Length: Millimeters" -ForegroundColor White
        Write-Host "      • Unit Scale: 1.0 (CRITICAL!)" -ForegroundColor White
        Write-Host "   2. Re-calculate toolpath in Fabex" -ForegroundColor White
        Write-Host "   3. Re-export G-code" -ForegroundColor White
    } elseif (-not $axisOK) {
        Write-Host "`n⚠️  A-AXIS MISSING!" -ForegroundColor Yellow
        Write-Host "   No A-axis commands found in G-code" -ForegroundColor Yellow
        Write-Host "`n🔧 Possible causes:" -ForegroundColor Yellow
        Write-Host "   1. 4-axis strategy not selected" -ForegroundColor White
        Write-Host "   2. A-axis not enabled in Machine settings" -ForegroundColor White
        Write-Host "   3. Fabex using indexed mode (not continuous)" -ForegroundColor White
        Write-Host "   4. May need alternative approach (FreeCAD, custom script)" -ForegroundColor White
    } else {
        Write-Host "`n⚠️  Partial success" -ForegroundColor Yellow
        Write-Host "   Some issues detected, review details above" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n⏸️  Generate G-code first to compare" -ForegroundColor Yellow
}

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan
