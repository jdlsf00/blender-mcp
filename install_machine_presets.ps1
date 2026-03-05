# Install Custom Machine Presets to Fabex
# Copies machine configuration files to Fabex presets directory

param(
    [switch]$ListOnly,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$sourceDir = "F:\Documents\CODE\Blender-MCP\machine_presets"
$fabexPresetsDir = "C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\extensions\blender_org\fabex\presets\cam_machines"

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Fabex Machine Presets Installer                         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check source directory
if (-not (Test-Path $sourceDir)) {
    Write-Host "❌ Source directory not found: $sourceDir" -ForegroundColor Red
    exit 1
}

# Check Fabex presets directory
if (-not (Test-Path $fabexPresetsDir)) {
    Write-Host "❌ Fabex presets directory not found!" -ForegroundColor Red
    Write-Host "   Expected: $fabexPresetsDir" -ForegroundColor Yellow
    Write-Host "   Make sure Fabex addon is installed" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Source: $sourceDir" -ForegroundColor Green
Write-Host "✅ Target: $fabexPresetsDir" -ForegroundColor Green

# Get available presets
$presets = Get-ChildItem -Path $sourceDir -Filter "*.py"

if ($presets.Count -eq 0) {
    Write-Host "`n⚠️  No preset files found in source directory" -ForegroundColor Yellow
    exit 0
}

Write-Host "`n━━━ Available Machine Presets ━━━" -ForegroundColor Cyan
foreach ($preset in $presets) {
    $status = ""
    $targetFile = Join-Path $fabexPresetsDir $preset.Name

    if (Test-Path $targetFile) {
        $status = "[Already installed]"
        $color = "DarkGray"
    } else {
        $status = "[New]"
        $color = "Green"
    }

    Write-Host "  • $($preset.Name) " -NoNewline
    Write-Host $status -ForegroundColor $color

    # Show description from file
    $firstLine = Get-Content $preset.FullName -TotalCount 5 | Where-Object { $_ -match '^Machine Preset:' }
    if ($firstLine) {
        $description = $firstLine -replace '.*Machine Preset:\s*', '' -replace '"""', ''
        Write-Host "    $description" -ForegroundColor DarkGray
    }
}

if ($ListOnly) {
    Write-Host "`n💡 To install presets, run: .\install_machine_presets.ps1`n" -ForegroundColor Cyan
    exit 0
}

# Install presets
Write-Host "`n━━━ Installation ━━━" -ForegroundColor Cyan

$installed = 0
$skipped = 0

foreach ($preset in $presets) {
    $targetFile = Join-Path $fabexPresetsDir $preset.Name
    $exists = Test-Path $targetFile

    if ($exists -and -not $Force) {
        Write-Host "  ⏸️  Skipping: $($preset.Name) (already exists)" -ForegroundColor Yellow
        $skipped++
        continue
    }

    try {
        Copy-Item -Path $preset.FullName -Destination $targetFile -Force

        if ($exists) {
            Write-Host "  ✅ Updated: $($preset.Name)" -ForegroundColor Green
        } else {
            Write-Host "  ✅ Installed: $($preset.Name)" -ForegroundColor Green
        }
        $installed++
    } catch {
        Write-Host "  ❌ Failed: $($preset.Name)" -ForegroundColor Red
        Write-Host "     Error: $_" -ForegroundColor Red
    }
}

# Summary
Write-Host "`n━━━ Summary ━━━" -ForegroundColor Cyan
Write-Host "  Installed: $installed" -ForegroundColor Green
Write-Host "  Skipped: $skipped" -ForegroundColor Yellow

if ($skipped -gt 0 -and -not $Force) {
    Write-Host "`n💡 To overwrite existing presets, use: -Force" -ForegroundColor Cyan
}

# Usage instructions
Write-Host "`n━━━ How to Use Presets in Blender ━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Method 1: Via Fabex UI (if available)" -ForegroundColor White
Write-Host "  1. Open Blender with Fabex enabled"
Write-Host "  2. In Fabex panel, look for Machine presets dropdown"
Write-Host "  3. Select your machine preset"
Write-Host ""
Write-Host "Method 2: Via Text Editor (recommended)" -ForegroundColor White
Write-Host "  1. Open Blender → Scripting workspace"
Write-Host "  2. Text Editor → Open → Navigate to preset file"
Write-Host "  3. Or: Text → Open → $fabexPresetsDir"
Write-Host "  4. Select your preset file (e.g., CNC_Router_4Axis_GRBL.py)"
Write-Host "  5. Press Alt+P to run script"
Write-Host "  6. Machine settings applied to current scene"
Write-Host ""
Write-Host "Method 3: Drag and drop" -ForegroundColor White
Write-Host "  1. Open Windows Explorer: $fabexPresetsDir"
Write-Host "  2. Drag preset file into Blender Text Editor"
Write-Host "  3. Press Alt+P to run"
Write-Host ""

# List installed presets
Write-Host "━━━ Installed Presets ━━━" -ForegroundColor Cyan
$allPresets = Get-ChildItem -Path $fabexPresetsDir -Filter "*.py"
foreach ($preset in $allPresets) {
    $isCustom = $presets.Name -contains $preset.Name
    if ($isCustom) {
        Write-Host "  ✓ $($preset.Name)" -ForegroundColor Green -NoNewline
        Write-Host " (custom)" -ForegroundColor Cyan
    }
}

Write-Host "`n✅ Installation complete!`n" -ForegroundColor Green
