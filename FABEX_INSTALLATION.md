# Fabex CNC Addon - Installation Complete

**Status**: ✅ Installed
**Version**: 1.0.68
**Location**: `C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\scripts\addons\fabex\`
**Date**: 2025-11-13

---

## Installation Summary

### ✅ Completed Steps:

1. Downloaded Fabex CNC v1.0.68 (39 MB)
2. Installed addon to Blender 4.5 addons directory
3. Installed Python dependency: `shapely`

### 🔧 Enable Addon in Blender:

**IMPORTANT**: The addon is installed but NOT enabled yet. You must enable it manually:

```
1. Open Blender
2. Edit → Preferences (or Ctrl+,)
3. Add-ons tab (left sidebar)
4. Search box: Type "Fabex" or "CNC"
5. Find "Fabex CNC" in results
6. Check the ✓ checkbox to enable
7. Close Preferences
```

### 📂 Addon Files Location:

```
C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\scripts\addons\fabex\
```

### 📥 Downloaded Zip (for backup):

```
C:\Users\jdlsf00\AppData\Local\Temp\blendercam_install\fabexcnc.zip
```

---

## Quick Start After Enabling

### 1. Open Your Project:

```
File → Open →
F:\Documents\CODE\Blender-MCP\reference_projects\4axis_helix_reference.blend
```

### 2. Access Fabex Panel:

- Press `N` key to show right sidebar
- Look for "Fabex CNC" tab (icon looks like a gear/machine)
- If not visible, addon is not enabled (go back to Preferences)

### 3. Verify Cylinder Object:

- Should see "TestCylinder_Helix" in scene
- Dimensions: 50mm × 100mm
- Oriented along X-axis (rotary axis)

### 4. Add CAM Operation:

In Fabex panel:

```
1. Click "+" to add new operation
2. Operation name: "Helix_Test"
3. Strategy: Select "4 axis" or "Rotary" option
4. Geometry: Click eyedropper, select TestCylinder_Helix
```

### 5. Configure Machine:

```
Fabex → Machine Settings:
• Post-processor: grbl (for GRBL controller)
• X: -400 to 400 mm
• Y: -400 to 400 mm
• Z: -150 to 50 mm
• A-axis: Enable, Type: Rotary
```

### 6. Configure Tool:

```
Tool Settings:
• Diameter: 6 mm
• Type: End mill
• Flutes: 4
• Feed rate: 500 mm/min
• Spindle speed: 12000 RPM
```

### 7. Calculate & Export:

```
1. Click "Calculate Path" (wait 30-60 sec)
2. Orange/green toolpath should appear
3. Click "Export G-code"
4. Save as: F:\Documents\CODE\Blender-MCP\reference_projects\blender_helix_reference.gcode
```

### 8. Validate G-code:

```powershell
cd F:\Documents\CODE\Blender-MCP
.\validate_gcode.ps1 -GCodePath "reference_projects\blender_helix_reference.gcode"
```

Expected results:

- ✅ G21 (millimeters) present
- ✅ Coordinates around ±50mm range
- ✅ A-axis commands (A0 to A18355)
- ✅ ~51 rotations calculated

---

## Troubleshooting

### Issue: "Fabex" not found in Add-ons search

**Solution**:

1. Check addon location exists:
   ```powershell
   Test-Path "C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\scripts\addons\fabex"
   ```
2. If FALSE, re-run installer:
   ```powershell
   .\install_blendercam.ps1
   ```

### Issue: Addon shows error when enabling

**Check console for errors**:

1. In Blender: Window → Toggle System Console
2. Try enabling addon again
3. Look for Python error messages
4. Most common: Missing `shapely` module

**Fix shapely issue**:

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.5\4.5\python\bin\python.exe" -m pip install shapely
```

### Issue: No Fabex panel visible after enabling

**Solutions**:

1. Press `N` key to toggle right sidebar
2. Look through tabs at top of sidebar
3. Restart Blender after enabling addon
4. Check if any error message appeared when enabling

### Issue: Can't find 4-axis or rotary option

**Fabex UI may vary by version**:

1. Look for "Rotary" in strategy dropdown
2. Or "4-axis" in operation type
3. Or separate checkbox: "Enable A-axis"
4. Check Fabex documentation if UI different

---

## Alternative: FreeCAD Path Workbench

If Fabex continues to have issues, FreeCAD is already installed:

```
F:\Documents\FreeCAD\
```

FreeCAD Path workbench has proven 4-axis rotary support and may be more stable. Would you like me to create the FreeCAD setup script as well?

---

## Reference Files

- **Project**: `4axis_helix_reference.blend` (430.8 KB)
- **Validation Checklist**: `VALIDATION_CHECKLIST.md`
- **G-code Validator**: `validate_gcode.ps1`
- **Machine Config**: `camotics_4axis_config.xml`

---

**Status**: Ready to enable addon and configure CAM operation!

**Next Step**: Open Blender → Enable Fabex → Follow Quick Start guide above
