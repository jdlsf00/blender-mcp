# 🚀 Blender & Fabex CNC - Optimization & Enhancement Guide

**Date**: November 13, 2025
**Blender Version**: 4.5.3 LTS
**Fabex Version**: 1.0.68

---

## ✅ Current Installation Status

### Fabex CNC (Primary CAM Tool)

- **Status**: ✅ Installed & Enabled (manually)
- **Version**: 1.0.68
- **Location**: `extensions\blender_org\fabex\`
- **Core Dependencies**:
  - ✅ `opencamlib` - Advanced toolpath generation (included in wheels)
  - ✅ `shapely` - Geometric operations (installed separately)

---

## 🎯 Optional Performance Enhancements for Fabex

### 1. Numba + LLVM Lite (⚠️ OPTIONAL - Performance Boost)

**What it does**: Dramatically speeds up toolpath calculations using JIT (Just-In-Time) compilation

**Status in Fabex v1.0.68**:

- Commented out in manifest (not automatically installed)
- Warning message: "Numba library is not installed"
- Fabex works WITHOUT it, but calculations are slower

**Performance Impact**:

- Complex 3D toolpaths: 2-5x faster
- Large operations (100k+ lines): 5-10x faster
- Simulation rendering: 3-4x faster

**Installation** (if you want the speed boost):

```powershell
# Install for Blender's Python
$blenderPython = "C:\Program Files\Blender Foundation\Blender 4.5\4.5\python\bin\python.exe"

# Install numba (will auto-install llvmlite dependency)
& $blenderPython -m pip install numba

# Verify installation
& $blenderPython -c "import numba; print(f'Numba {numba.__version__} installed')"
```

**Recommendation**:

- ✅ **Install if**: You're doing complex 3D milling, adaptive toolpaths, or large operations
- ⏸️ **Skip if**: You're only doing simple 2D profiles or small test cuts

---

## 📦 Recommended Complementary Blender Extensions

### For CAM Preparation & Modeling

#### 1. **Mesh Repair Tools** (FREE - Highly Recommended)

**Why**: Clean up mesh issues before CAM operations

- Fixes non-manifold edges (causes CAM errors)
- Removes duplicate vertices
- Fills holes
- Makes meshes "watertight" for better toolpaths

**Install**:

```
Edit → Preferences → Get Extensions → Search "Mesh Repair Tools" → Install
```

**Use case**: Run before exporting/CAM to ensure clean geometry

---

#### 2. **MeasureIt-ARCH** (FREE - Recommended)

**Why**: Precision measurements for CAM work

- Real-time dimensions overlay
- Verify part sizes match machine envelope
- Check clearances and tool access
- Export dimension reports

**Install**:

```
Edit → Preferences → Get Extensions → Search "MeasureIt-ARCH" → Install
```

**Use case**: Verify dimensions before generating toolpaths

---

#### 3. **Extra Objects** (Built-in - Enable)

**Why**: Additional primitive shapes useful for CAM

- Extra mesh primitives (gears, pipes, etc.)
- Extra curve objects (spirals, helixes)
- Useful for testing toolpaths

**Enable**:

```
Edit → Preferences → Add-ons → Search "Extra Objects" → Enable:
  - Add Mesh: Extra Objects
  - Add Curve: Extra Objects
```

---

#### 4. **Node Wrangler** (Built-in - Enable)

**Why**: If using materials/textures for heightfield-based carving

- Quick material preview
- Texture coordinate mapping
- Useful for bas-relief operations

**Enable**:

```
Edit → Preferences → Add-ons → Search "Node Wrangler" → Enable
```

---

#### 5. **Import Images as Planes** (Built-in - Enable)

**Why**: Import reference images for tracing/CAM

- Import image as mesh with proper scale
- Useful for converting images to toolpaths
- Good for V-carving from photos

**Enable**:

```
Edit → Preferences → Add-ons → Search "Import Images" → Enable
```

---

### For Workflow & Productivity

#### 6. **Bool Tool** (Built-in - Enable)

**Why**: Faster boolean operations for CAM geometry

- Union, Difference, Intersect with shortcuts
- Clean up boolean results
- Essential for combining parts

**Enable**:

```
Edit → Preferences → Add-ons → Search "Bool Tool" → Enable
```

---

#### 7. **3D Print Toolbox** (Built-in - Enable)

**Why**: Mesh analysis similar to CAM requirements

- Check for mesh errors
- Calculate volume/weight
- Check overhangs (useful for accessibility)
- Make solid (fixes non-manifold)

**Enable**:

```
Edit → Preferences → Add-ons → Search "3D Print" → Enable
```

---

## 🔧 Fabex Code Improvements You Can Make

### 1. Custom Post-Processor Enhancement

**What**: Optimize G-code output for your specific machines

**Location**: `extensions\blender_org\fabex\post_processors\`

**Your machines**:

- MOPA fiber laser
- Diode laser
- CNC router (4-axis XYZA)

**Recommendation**: Create custom post-processors

```python
# Example: F:\Documents\CODE\Blender-MCP\custom_post_processors\grbl_4axis_optimized.py

# Based on grbl.py but with:
# - Optimized A-axis wrapping (prevent unnecessary rotations)
# - Arc compensation for rotary (G2/G3 adjustments)
# - Custom feed rate ramping for direction changes
# - Tool change macros for your specific setup
```

**Create script to install custom post-processors**:

```powershell
# Copy custom post-processors to Fabex
$customPP = "F:\Documents\CODE\Blender-MCP\custom_post_processors"
$fabexPP = "C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\extensions\blender_org\fabex\post_processors"

Copy-Item "$customPP\*.py" -Destination $fabexPP -Force
Write-Host "✅ Custom post-processors installed"
```

---

### 2. Machine Presets

**What**: Save your machine configurations for quick setup

**Location**: `extensions\blender_org\fabex\presets\cam_machines\`

**Create presets for**:

1. CNC Router 4-axis (800×800×200mm, GRBL)
2. MOPA Fiber Laser (marking parameters)
3. Diode Laser (engraving parameters)

**How**:

1. Configure machine in Fabex UI
2. Click "+" next to Machine dropdown
3. Save as preset: "CNC_Router_4Axis_XYZA.py"
4. Reusable across projects

---

### 3. Tool Library Enhancement

**Location**: `extensions\blender_org\fabex\presets\cam_cutters\`

**Add your actual tools**:

```python
# 6mm_EndMill_4Flute.py
bpy.context.scene.cam_operations[0].cutter_type = 'ENDMILL'
bpy.context.scene.cam_operations[0].cutter_diameter = 0.006  # 6mm in meters
bpy.context.scene.cam_operations[0].cutter_flutes = 4
bpy.context.scene.cam_operations[0].feedrate = 500  # mm/min
bpy.context.scene.cam_operations[0].spindle_rpm = 12000
```

**Benefit**: One-click tool selection, no manual entry

---

### 4. Operation Templates

**Location**: `extensions\blender_org\fabex\presets\cam_operations\`

**Create operation presets**:

- `4Axis_Helix_Roughing.py` - Your current use case
- `Profile_Cutout_6mm.py` - 2D profile cutting
- `Pocket_Adaptive_3mm.py` - Adaptive clearing
- `VCarve_60deg_Text.py` - V-carving operations

**Usage**:

```
Fabex panel → Operations → Presets → Your_Operation
```

---

## 🔬 Advanced: OpenCAMLib Optimization

**What**: OpenCAMLib is the core toolpath engine (already included)

**Current version**: 2023.1.11 (included in wheels)

**Latest version check**:

```powershell
# Check for updates
Invoke-WebRequest -Uri "https://pypi.org/pypi/opencamlib/json" |
  ConvertFrom-Json |
  Select-Object -ExpandProperty info |
  Select-Object version
```

**If newer version available**:

```powershell
# Update OpenCAMLib
$blenderPython = "C:\Program Files\Blender Foundation\Blender 4.5\4.5\python\bin\python.exe"
& $blenderPython -m pip install --upgrade opencamlib
```

---

## 🎨 Workflow-Specific Recommendations

### For 4-Axis Rotary Work (Your Current Task)

**Must-have**:

1. ✅ Fabex CNC (already enabled)
2. ✅ Mesh Repair Tools (check geometry before CAM)
3. ✅ MeasureIt-ARCH (verify cylinder dimensions)
4. ⏸️ Numba (optional - speeds up complex helical calculations)

**Nice-to-have**:

- Extra Objects (for creating test cylinders)
- Bool Tool (for combining fixtures)

---

### For Laser Engraving (MOPA/Diode)

**Must-have**:

1. ✅ Fabex CNC (2D operations)
2. ✅ Import Images as Planes (convert images to paths)
3. ✅ Extra Curve Objects (create decorative patterns)

**Fabex strategies to use**:

- Engrave (for raster images)
- Cutout (for vector outlines)
- Curve (for line art)

---

### For 3D Milling

**Must-have**:

1. ✅ Fabex CNC
2. ✅ Numba (significantly faster for 3D)
3. ✅ Mesh Repair Tools (critical for 3D)
4. ✅ 3D Print Toolbox (mesh analysis)

**Fabex strategies to use**:

- Parallel (3D roughing)
- Waterline (finish pass)
- Adaptive (efficient clearing)

---

## 📝 Installation Script: All Recommended Addons

```powershell
# Enable Built-in Blender Addons
$addonsToEnable = @(
    "mesh_extra_objects",
    "curve_extra_objects",
    "node_wrangler",
    "io_import_images_as_planes",
    "object_boolean_tools",
    "object_print3d_utils"
)

$script = "import bpy; "
foreach ($addon in $addonsToEnable) {
    $script += "bpy.ops.preferences.addon_enable(module='$addon'); "
}
$script += "bpy.ops.wm.save_userpref(); print('✅ Built-in addons enabled')"

& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" `
  --background `
  --python-expr $script
```

---

## 🧪 Performance Testing

After installing numba (optional), test the performance:

```python
# Save as test_numba_performance.py
import bpy
import time

# Create test geometry
bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64)
obj = bpy.context.active_object

# Add CAM operation (requires Fabex enabled)
bpy.ops.scene.cam_operation_add()
op = bpy.context.scene.cam_operations[0]
op.geometry_source = 'OBJECT'
op.object_name = obj.name
op.strategy = 'PARALLEL'
op.parallel_step_back = 0.001

# Time toolpath calculation
start = time.time()
bpy.ops.object.calculate_cam_path()
duration = time.time() - start

print(f"Toolpath calculation time: {duration:.2f} seconds")
print(f"Points generated: {len(bpy.context.scene.cam_paths)}")
```

**Expected results**:

- Without numba: 15-30 seconds
- With numba: 3-8 seconds

---

## 🔍 Verify Current Setup

Run this to check what you have:

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --background --python-expr @"
import bpy
import sys

print('\n=== INSTALLED EXTENSIONS ===')
for addon in bpy.context.preferences.addons:
    print(f'  ✓ {addon.module}')

print('\n=== PYTHON PACKAGES ===')
packages = ['shapely', 'opencamlib', 'numba', 'llvmlite']
for pkg in packages:
    try:
        mod = __import__(pkg)
        version = getattr(mod, '__version__', 'unknown')
        print(f'  ✓ {pkg}: {version}')
    except ImportError:
        print(f'  ✗ {pkg}: not installed')

bpy.ops.wm.quit_blender()
"@
```

---

## 🎯 Recommended Installation Order

### Minimal Setup (Start Here):

1. ✅ Fabex CNC (already done)
2. Enable: Mesh Repair Tools
3. Enable: Bool Tool

### Standard Setup (Recommended):

4. Enable: Extra Objects (Mesh + Curve)
5. Enable: MeasureIt-ARCH
6. Enable: 3D Print Toolbox

### Performance Setup (If doing complex work):

7. Install: Numba (with llvmlite)

### Advanced Setup (Power users):

8. Create custom post-processors
9. Build tool library presets
10. Create machine presets

---

## 📚 Resources

**Fabex Documentation**: https://blendercam.com/
**GitHub**: https://github.com/vilemduha/blendercam
**Matrix Chat**: #BlenderCAM:matrix.org

**Numba Documentation**: https://numba.pydata.org/
**OpenCAMLib**: https://github.com/aewallin/opencamlib

---

## 🚨 Important Notes

### About 4-Axis in Fabex v1.0.68:

From the GitHub README:

> ⚠️ 4 Axis Milling ⚠️
> Currently only possible via **manual indexing**
> Status: ⏳ Experimental

**What this means**:

- True continuous 4-axis (simultaneous XYZA) is experimental
- "Manual indexing" = Rotate part, mill, rotate again (indexed operations)
- Your helix strategy may require workarounds

**Alternatives if Fabex 4-axis has issues**:

1. FreeCAD Path workbench (better 4-axis support)
2. PyCAM (dedicated 4-axis tool)
3. Commercial: Fusion 360 CAM (free for hobbyists)

---

## ✅ Summary: What to Install Now

**Immediate (for your 4-axis helix project)**:

```powershell
# Enable built-in addons
Edit → Preferences → Add-ons → Enable:
  - Mesh: Extra Objects
  - 3D Print Toolbox

# Optional performance boost
$blenderPython = "C:\Program Files\Blender Foundation\Blender 4.5\4.5\python\bin\python.exe"
& $blenderPython -m pip install numba
```

**Later (when expanding CAM use)**:

- MeasureIt-ARCH (for precision work)
- Mesh Repair Tools (for imported models)
- Custom post-processors (for machine-specific optimization)

---

**Next Steps**:

1. Open `4axis_helix_reference.blend`
2. Configure Fabex CAM operation (see VALIDATION_CHECKLIST.md)
3. Generate G-code
4. Validate with `validate_gcode.ps1`

🚀 **You're ready to generate CAM toolpaths!**
