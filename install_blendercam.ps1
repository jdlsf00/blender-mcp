# BlenderCAM (Fabex) Installation Script
# Downloads and installs the BlenderCAM addon for Blender 4.5
# Source: https://github.com/vilemduha/blendercam

param(
    [string]$BlenderPath = "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe",
    [string]$DownloadDir = "$env:TEMP\blendercam_install"
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  BLENDERCAM (FABEX) INSTALLER" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Blender exists
if (-not (Test-Path $BlenderPath)) {
    Write-Host "❌ Blender not found at: $BlenderPath" -ForegroundColor Red
    Write-Host "`nPlease specify correct path:" -ForegroundColor Yellow
    Write-Host '  .\install_blendercam.ps1 -BlenderPath "C:\Path\To\blender.exe"'
    exit 1
}

Write-Host "✅ Blender found: $BlenderPath" -ForegroundColor Green

# Create download directory
New-Item -ItemType Directory -Force -Path $DownloadDir | Out-Null
Write-Host "✅ Download directory: $DownloadDir" -ForegroundColor Green

# Download latest BlenderCAM release
Write-Host "`n📥 Downloading BlenderCAM (Fabex) addon..." -ForegroundColor Yellow

$githubRepo = "vilemduha/blendercam"
$releaseUrl = "https://api.github.com/repos/$githubRepo/releases/latest"

try {
    # Get latest release info
    Write-Host "   Checking latest release from GitHub..." -ForegroundColor Gray
    $release = Invoke-RestMethod -Uri $releaseUrl -Headers @{"User-Agent" = "PowerShell" }

    # Find the .zip asset
    $zipAsset = $release.assets | Where-Object { $_.name -like "*.zip" -or $_.name -like "*blendercam*" } | Select-Object -First 1

    if (-not $zipAsset) {
        Write-Host "   ⚠️  No .zip asset found in latest release" -ForegroundColor Yellow
        Write-Host "   Trying direct download from main branch..." -ForegroundColor Yellow

        # Fallback: Download from main branch
        $downloadUrl = "https://github.com/$githubRepo/archive/refs/heads/main.zip"
        $zipFile = Join-Path $DownloadDir "blendercam-main.zip"
    } else {
        $downloadUrl = $zipAsset.browser_download_url
        $zipFile = Join-Path $DownloadDir $zipAsset.name
        Write-Host "   Found release: $($release.tag_name)" -ForegroundColor Green
        Write-Host "   Asset: $($zipAsset.name)" -ForegroundColor Gray
    }

    Write-Host "   Downloading from: $downloadUrl" -ForegroundColor Gray
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing

    Write-Host "✅ Downloaded: $zipFile" -ForegroundColor Green
    Write-Host "   Size: $([math]::Round((Get-Item $zipFile).Length/1MB, 1)) MB" -ForegroundColor Gray

} catch {
    Write-Host "❌ Download failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n💡 Manual installation:" -ForegroundColor Yellow
    Write-Host "   1. Visit: https://github.com/vilemduha/blendercam/releases" -ForegroundColor Cyan
    Write-Host "   2. Download latest blendercam.zip" -ForegroundColor Cyan
    Write-Host "   3. In Blender: Edit → Preferences → Add-ons → Install from File" -ForegroundColor Cyan
    Write-Host "   4. Select the .zip file (DON'T extract it!)" -ForegroundColor Cyan
    Write-Host "   5. Enable 'Fabex CNC' addon" -ForegroundColor Cyan
    exit 1
}

# Install addon in Blender
Write-Host "`n🔧 Installing addon in Blender..." -ForegroundColor Yellow

$installScript = @"
import bpy
import sys
import os

zip_file = r'$zipFile'

print('Installing BlenderCAM addon from:', zip_file)

try:
    # Install addon
    bpy.ops.preferences.addon_install(filepath=zip_file)
    print('✅ Addon installed successfully')

    # Try to enable it (module name might vary)
    addon_names = ['cam', 'blendercam', 'fabex']
    enabled = False

    for addon_name in addon_names:
        try:
            bpy.ops.preferences.addon_enable(module=addon_name)
            print(f'✅ Addon enabled: {addon_name}')
            enabled = True
            break
        except:
            continue

    if not enabled:
        print('⚠️  Addon installed but not auto-enabled')
        print('   Please enable manually in Preferences → Add-ons')

    # Save preferences
    bpy.ops.wm.save_userpref()
    print('✅ Preferences saved')

    sys.exit(0)

except Exception as e:
    print(f'❌ Installation failed: {str(e)}')
    sys.exit(1)
"@

$scriptFile = Join-Path $DownloadDir "install_addon.py"
$installScript | Out-File -FilePath $scriptFile -Encoding UTF8

# Run Blender with install script
try {
    & $BlenderPath --background --python $scriptFile

    Write-Host "`n✅ BlenderCAM addon installed!" -ForegroundColor Green

} catch {
    Write-Host "❌ Installation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Cleanup
Write-Host "`n🧹 Cleaning up..." -ForegroundColor Gray
# Keep the zip file for manual installation if needed
Write-Host "   Downloaded file kept at: $zipFile" -ForegroundColor Gray

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  INSTALLATION COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Open Blender" -ForegroundColor Cyan
Write-Host "   2. Edit → Preferences → Add-ons" -ForegroundColor Cyan
Write-Host "   3. Search for 'Fabex' or 'CAM'" -ForegroundColor Cyan
Write-Host "   4. Verify checkbox is enabled ✓" -ForegroundColor Cyan
Write-Host "   5. Open your project: 4axis_helix_reference.blend" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 If addon not visible:" -ForegroundColor Yellow
Write-Host "   Manual install using the downloaded zip:" -ForegroundColor Cyan
Write-Host "   $zipFile" -ForegroundColor Gray
Write-Host ""
