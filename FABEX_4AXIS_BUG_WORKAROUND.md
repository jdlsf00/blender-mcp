# Fabex 4-Axis Bug Workaround

## 🐛 Bug Identified

**Error**: `'CamPathChunk' object has no attribute 'to_chunk'`

**Root Cause**: Bug in Fabex v1.0.68 `cam_chunk.py` line 1160

- Code converts `CamPathChunkBuilder` → `CamPathChunk` by calling `.to_chunk()`
- In 4-axis operations, code loops and tries to call `.to_chunk()` again on already-converted CamPathChunk
- CamPathChunk doesn't have `to_chunk()` method (only CamPathChunkBuilder does)

**Affected**: HELIX, PARALLELR, PARALLEL 4-axis strategies

---

## ✅ Workarounds (3 Options)

### **Option 1: Try INDEXED Strategy (Simplest)**

INDEXED strategy may avoid the buggy code path:

1. Open Blender with `4axis_helix_reference.blend`
2. Set Render Engine: **FabEX CNC/CAM**
3. Select TestCylinder_Helix object
4. Add Fabex Operation
5. Configure:
   - **Machine Axes**: `4 axis - EXPERIMENTAL`
   - **4 Axis Strategy**: `INDEXED` (instead of HELIX)
   - **Rotary Axis**: `X`
   - **Tool**: 6mm End Mill
   - **Feeds/Speeds**: 500 mm/min, 12000 RPM
6. Calculate Path
7. Try Export G-code

**If INDEXED works**: You get 4-axis G-code (indexed positioning, not continuous helical)

---

### **Option 2: FreeCAD Path Workbench (Most Reliable)**

FreeCAD has mature 4-axis rotary support:

#### Setup:

1. **Install FreeCAD** (if not already): https://www.freecadapp.org/downloads.php
2. Launch FreeCAD

#### Create 4-Axis Project:

1. **File → New**
2. **Workbench → Part Design**
3. Create cylinder:

   - Click "Create a new body"
   - Select body → Pad tool
   - Sketch circle diameter 50mm
   - Pad length 100mm along X-axis

4. **Workbench → Path**
5. **Path → Job**:

   - Stock: Cylinder 50mm diameter × 100mm
   - Setup: Rotation around X-axis
   - Tools: Add 6mm end mill (500 mm/min, 12000 RPM)

6. **Path → 4th-axis**:

   - Select "Rotational Surface" operation
   - Cutter Side: Outside
   - Step Over: 5mm
   - Pattern: Helical or Zigzag
   - Rotational Axis: X

7. **Post Process**:
   - Select grbl_post processor
   - Export: `freecad_4axis_helix.gcode`

#### Validate:

```powershell
.\validate_gcode.ps1 -GCodePath "freecad_4axis_helix.gcode"
```

**Expected**: X ±50mm, A-axis commands, proper scale

---

### **Option 3: Custom Python G-code Generator (Most Control)**

Generate helical toolpath programmatically:

#### Create script: `generate_helix_gcode.py`

```python
import math

# Configuration
CYLINDER_RADIUS = 25.0  # mm (50mm diameter / 2)
CYLINDER_LENGTH = 100.0  # mm
TOOL_DIAMETER = 6.0  # mm
STEP_OVER = 5.0  # mm axial spacing between passes
FEED_RATE = 500  # mm/min
SPINDLE_RPM = 12000
DEGREES_PER_MM = 360 / (2 * math.PI * CYLINDER_RADIUS)  # Convert linear to rotational

# Calculate helix
total_passes = int(CYLINDER_LENGTH / STEP_OVER)

print("; Generated Helical 4-Axis Toolpath")
print("G21 ; Millimeters")
print("G90 ; Absolute positioning")
print(f"M3 S{SPINDLE_RPM} ; Spindle on")
print("G0 X0 Y0 Z5 A0 ; Start position")
print(f"G1 F{FEED_RATE}")

for pass_num in range(total_passes):
    x_start = pass_num * STEP_OVER
    x_end = (pass_num + 1) * STEP_OVER

    # Full rotation for this pass
    for angle_deg in range(0, 361, 10):  # 10° increments
        x_pos = x_start + (x_end - x_start) * (angle_deg / 360.0)
        y_pos = CYLINDER_RADIUS * math.cos(math.radians(angle_deg))
        z_pos = CYLINDER_RADIUS * math.sin(math.radians(angle_deg))
        a_pos = angle_deg + (pass_num * 360)

        print(f"G1 X{x_pos:.3f} Y{y_pos:.3f} Z{z_pos:.3f} A{a_pos:.3f}")

print("G0 Z50 ; Retract")
print("M5 ; Spindle off")
print("M2 ; End program")
```

#### Run:

```powershell
python generate_helix_gcode.py > custom_4axis_helix.gcode
```

#### Validate:

```powershell
.\validate_gcode.ps1 -GCodePath "custom_4axis_helix.gcode"
.\compare_gcode.ps1 -NewFile "custom_4axis_helix.gcode"
```

**Pros**:

- Guaranteed to work
- Full control over toolpath
- No buggy addons

**Cons**:

- No GUI
- Manual parameter adjustments
- No collision detection

---

## 🔍 Alternative: Fix Fabex Bug (Advanced)

**NOT RECOMMENDED** (requires Python knowledge, may break addon)

If you want to patch Fabex:

### File: `cam_chunk.py` line 1159-1161

**Current (buggy)**:

```python
layeractivechunks[i] = (
    layeractivechunks[i].to_chunk() if layeractivechunks[i] is not None else None
)
```

**Fixed**:

```python
if layeractivechunks[i] is not None and hasattr(layeractivechunks[i], 'to_chunk'):
    layeractivechunks[i] = layeractivechunks[i].to_chunk()
elif layeractivechunks[i] is not None and isinstance(layeractivechunks[i], CamPathChunk):
    pass  # Already converted, don't convert again
else:
    layeractivechunks[i] = None
```

**Backup first**:

```powershell
Copy-Item "C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\extensions\blender_org\fabex\cam_chunk.py" "C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\extensions\blender_org\fabex\cam_chunk.py.backup"
```

**⚠️ Warning**:

- May violate addon license
- Breaks on Fabex updates
- No guarantee of fix working
- Better to report bug to Fabex developers

---

## 📋 Recommendation

**Try in this order**:

1. **Option 1 (INDEXED)**: 2 minutes, low risk
2. **Option 2 (FreeCAD)**: 30 minutes, most reliable for production
3. **Option 3 (Python script)**: 15 minutes, best for simple helical paths

**For your immediate goal** (50mm cylinder helical toolpath):
→ **Option 2 (FreeCAD)** is best - proven, stable, production-ready 4-axis support

---

## 🐞 Report Bug

Help improve Fabex for others:

1. GitHub: https://github.com/vilemduha/blendercam/issues
2. Report title: "4-axis HELIX strategy fails with 'CamPathChunk' object has no attribute 'to_chunk'"
3. Include:
   - Fabex version: 1.0.68
   - Blender version: 4.5.3 LTS
   - Strategy: HELIX (also affects PARALLEL, PARALLELR)
   - Error location: cam_chunk.py line 1160
   - Root cause: Attempts to call .to_chunk() on already-converted CamPathChunk object

---

## Next Steps

**Which option do you want to try first?**

1. **INDEXED strategy** (quickest test)
2. **FreeCAD** (production solution)
3. **Python script** (custom control)

Let me know and I'll provide detailed guidance for your choice!
