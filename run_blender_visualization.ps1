#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run Blender 4-axis visualization script

.DESCRIPTION
    Launches Blender in background mode with the visualization script,
    then opens the saved .blend file in the GUI for viewing.

.PARAMETER GCodeFile
    Path to the G-code file to visualize (default: true_4axis_surface.gcode)

.EXAMPLE
    .\run_blender_visualization.ps1
    .\run_blender_visualization.ps1 -GCodeFile "test_output\true_4axis_wavy.gcode"
#>

param(
    [string]$GCodeFile = "test_output\true_4axis_surface.gcode"
)

$BlenderPath = "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
$ScriptPath = "$PSScriptRoot\visualize_4axis_blender.py"
$OutputBlend = "$PSScriptRoot\4axis_visualization.blend"

# Convert to absolute path if needed
if (-not [System.IO.Path]::IsPathRooted($GCodeFile)) {
    $GCodeFile = Join-Path $PSScriptRoot $GCodeFile
}

Write-Host "🎬 Starting Blender 4-axis visualization..." -ForegroundColor Cyan
Write-Host "📂 G-code file: $GCodeFile" -ForegroundColor Gray
Write-Host "💾 Output file: $OutputBlend" -ForegroundColor Gray
Write-Host ""

# Step 1: Run Blender in background to create the scene
Write-Host "⚙️  Step 1/2: Running visualization script in background..." -ForegroundColor Yellow
& $BlenderPath --background --python $ScriptPath -- $GCodeFile $OutputBlend

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error running Blender script (exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Visualization scene created successfully!" -ForegroundColor Green
Write-Host ""

# Step 2: Open the .blend file in Blender GUI
Write-Host "⚙️  Step 2/2: Opening Blender GUI..." -ForegroundColor Yellow
& $BlenderPath $OutputBlend

Write-Host ""
Write-Host "✅ Done! Blender should now be open with your 4-axis visualization." -ForegroundColor Green
Write-Host ""
Write-Host "📺 Controls:" -ForegroundColor Cyan
Write-Host "   - Spacebar: Play/pause animation" -ForegroundColor Gray
Write-Host "   - Mouse: Rotate view" -ForegroundColor Gray
Write-Host "   - Scroll: Zoom" -ForegroundColor Gray
Write-Host "   - Alt+A: Play animation" -ForegroundColor Gray
