# CAMotics Quick Start Guide - 4-Axis HELIX Simulation

**Purpose**: Simulate BlenderCAM HELIX G-code with material removal and collision detection
**Machine**: 4-axis CNC router (XYZA)
**Test Part**: 50mm × 100mm cylinder
**Last Updated**: 2025-11-13

---

## 🚀 Step 1: Launch CAMotics

### Windows

```powershell
# Option A: From Start Menu
# Search "CAMotics" and click

# Option B: From Command Line
Start-Process "C:\Program Files\CAMotics\camotics.exe"

# Option C: Direct path (adjust if different)
& "C:\Program Files\CAMotics\camotics.exe"
```

---

## 🔧 Step 2: Configure 4-Axis Machine

### Method 1: Import Configuration File

1. **File → Open Project**
2. Navigate to: `F:\Documents\CODE\Blender-MCP\camotics_4axis_config.xml`
3. Click **Open**

### Method 2: Manual Configuration

1. **Edit → Machine → New**
2. Enter machine parameters:
   - **Name**: `4-Axis CNC Router (XYZA)`
   - **X-Axis**: Min `-400`, Max `400` mm
   - **Y-Axis**: Min `-400`, Max `400` mm
   - **Z-Axis**: Min `-150`, Max `50` mm
   - **A-Axis**: Min `-99999`, Max `99999` mm, **Rotary** ✓
3. **Save** machine profile

---

## 📦 Step 3: Set Up Workpiece

### Cylinder Workpiece (for HELIX test)

1. **Workpiece → New → Cylinder**
2. Enter dimensions:
   - **Diameter**: `50` mm
   - **Length**: `100` mm
   - **Material**: `Wood` (or select from dropdown)
3. **Position**:
   - **X**: `0`
   - **Y**: `0`
   - **Z**: `0`
   - **A**: `0`
4. Click **OK**

### Visual Verification

- Workpiece should appear as a gray cylinder in the 3D viewport
- Use mouse to rotate view: **Right-click + Drag**
- Zoom: **Mouse Wheel**

---

## 📂 Step 4: Load G-code

### Locate HELIX G-code File

```powershell
# Find generated G-code files
Get-ChildItem "F:\Documents\CODE\Blender-MCP" -Filter "*helix*" -Recurse |
    Where-Object { $_.Extension -in '.gcode','.tap','.ngc' } |
    Select-Object Name, FullName, @{Name="Size";Expression={[math]::Round($_.Length/1KB,1)}}
```

### Import in CAMotics

1. **File → Open G-code**
2. Navigate to G-code file (example paths):
   - `helix_4axis_test_GRBL.gcode`
   - `helix_rotation_data.csv` (if you need to reference data)
3. Select file and click **Open**

### Expected Result

- G-code should load without errors
- Status bar shows: `Loaded X lines`
- Toolpath appears as colored lines in viewport

---

## 🛠️ Step 5: Configure Tool

### Set Tool Properties

1. **Tools → Tool 1 → Edit**
2. Enter tool parameters:
   - **Type**: `End Mill`
   - **Diameter**: `6.0` mm
   - **Length**: `50` mm
   - **Flutes**: `2`
   - **Material**: `HSS` or `Carbide`
3. Click **OK**

### Tool Visualization

- Tool should appear in viewport during simulation
- Default color: Yellow/Orange

---

## ▶️ Step 6: Run Simulation

### Start Simulation

1. **Simulation → Run** (or press **F5**)
2. Watch the simulation progress:
   - Tool moves along toolpath
   - Material is removed in real-time
   - A-axis rotates the workpiece

### Simulation Controls

| Control       | Action        |
| ------------- | ------------- |
| **Space Bar** | Pause/Resume  |
| **F5**        | Run           |
| **F6**        | Step Forward  |
| **Shift+F6**  | Step Backward |
| **F7**        | Slow Motion   |
| **F8**        | Reset         |

### Adjust Simulation Speed

1. **View → Playback Speed**
2. Options: `0.1x`, `0.5x`, `1x`, `2x`, `5x`, `10x`
3. Recommended for first run: `2x` (2× speed)

---

## 🔍 Step 7: Inspect Results

### 4-Axis Rotation Verification

**Expected**:

- A-axis should rotate from `0°` to `~18,355°` (51 revolutions)
- Rotation should be smooth and continuous

**Check**:

1. **View → Show Axes** (enable axis display)
2. Watch the workpiece rotate during simulation
3. **Window → G-code** (view executed commands)
4. Search for `A` commands: Look for `A18355.233` near the end

### Material Removal Inspection

**Zoom and Rotate**:

- Right-click + drag to rotate view
- Mouse wheel to zoom
- **View → Perspective** vs **View → Orthographic**

**Visual Checks**:

- ✅ Material removed in helical pattern
- ✅ Tool follows surface of cylinder
- ✅ No gouges or unexpected cuts
- ✅ Final part matches expected geometry

### Collision Detection

**Check for Collisions**:

1. **View → Show Collisions** (enable)
2. If collisions detected:
   - Red highlights indicate tool/workpiece interference
   - Review G-code line numbers
   - Check tool diameter vs. part geometry

**Expected for HELIX test**: ✅ **No collisions**

---

## 📊 Step 8: Generate Report

### Simulation Statistics

1. **Tools → Simulation Info**
2. Review metrics:
   - **Total Lines Executed**: ~58,822 (for HELIX GRBL)
   - **Simulation Time**: X minutes
   - **Material Removed**: X mm³
   - **Tool Travel Distance**: X mm

### Export Results

#### Screenshot

1. Position view to show final part
2. **File → Export → Screenshot**
3. Save as: `helix_simulation_result.png`

#### Simulated Part (STL)

1. **File → Export → Workpiece STL**
2. Save as: `helix_simulated_part.stl`
3. Compare with original test part using FreeCAD or Blender

---

## ✅ Validation Checklist

Before proceeding to hardware:

- [ ] G-code loads without errors
- [ ] Workpiece dimensions correct (50mm × 100mm cylinder)
- [ ] Tool diameter correct (6mm)
- [ ] Simulation runs to completion (no crashes)
- [ ] **A-axis rotation**: 0° → 18,355° (51 revolutions) ✓
- [ ] **No collisions detected** ✓
- [ ] Material removal looks correct (helical pattern)
- [ ] Tool stays within work envelope
- [ ] No unexpected rapids or movements
- [ ] Final part geometry matches expected shape

---

## 🚨 Troubleshooting

### Issue: "Cannot find G-code file"

**Solution**:

```powershell
# Generate G-code if missing
cd "F:\Documents\CODE\Blender-MCP"
python test_4axis_helix.py --strategy HELIX --post GRBL
```

### Issue: "Invalid A-axis value"

**Possible Causes**:

- Machine not configured for rotary axis
- A-axis not set to "Rotary" mode

**Solution**:

1. **Edit → Machine → Edit Current**
2. Find A-axis configuration
3. Enable **Rotary** checkbox
4. Set Min/Max to large values: `-99999` / `99999`

### Issue: Simulation crashes or freezes

**Possible Causes**:

- GPU driver issue
- Insufficient memory
- Too high simulation resolution

**Solution**:

1. **Edit → Preferences → Simulation → Resolution**: Set to `Medium` or `Low`
2. Close other applications to free memory
3. Update GPU drivers

### Issue: Toolpath not visible

**Solution**:

1. **View → Show Toolpath** (enable)
2. **View → Reset Camera**
3. Zoom out: Mouse wheel scroll

### Issue: Workpiece too small/large

**Solution**:

1. **Workpiece → Edit Current**
2. Verify dimensions:
   - Diameter: `50` mm
   - Length: `100` mm
3. **Workpiece → Reset View**

---

## 🎯 Next Steps After Validation

### If Simulation Passes ✅

1. **Export simulation report**:

   - Screenshot of final part
   - Simulation statistics
   - Add to `HARDWARE_TESTING_WORKFLOW.md`

2. **Prepare for air cutting test**:

   - Load G-code into CNC controller
   - Set Z-offset +50mm (tool above workpiece)
   - Run at 100% speed
   - Visually verify A-axis rotation (51 revolutions)

3. **Proceed to hardware testing**:
   - Use scrap material first (pine wood or HDPE)
   - Follow safety protocols in `HARDWARE_TESTING_WORKFLOW.md`
   - Collect data in material test CSVs

### If Issues Found ❌

1. **Document the problem**:

   - Screenshot of collision/error
   - G-code line number
   - Description of issue

2. **Investigate cause**:

   - Tool diameter too large?
   - Stepover too aggressive?
   - A-axis rotation incorrect?

3. **Adjust BlenderCAM parameters**:
   - Modify `test_4axis_helix.py`
   - Regenerate G-code
   - Re-simulate in CAMotics

---

## 📚 Additional Resources

### CAMotics Documentation

- **Official Manual**: https://camotics.org/manual.html
- **GitHub**: https://github.com/CauldronDevelopmentLLC/CAMotics
- **FAQ**: https://camotics.org/faq.html

### Video Tutorials

- Search YouTube: "CAMotics 4-axis tutorial"
- Search YouTube: "CAMotics rotary axis setup"

### Community Support

- **CAMotics Forum**: https://groups.google.com/g/camotics-users
- **BlenderCAM Issues**: https://github.com/vilemduha/blendercam/issues

---

## 🔗 Related Documentation

- `GCODE_SIMULATION_OPTIONS.md` - Complete simulation tool comparison
- `HARDWARE_TESTING_WORKFLOW.md` - Full hardware testing procedures
- `BLENDERCAM_4AXIS_VALIDATION.md` - Software validation report
- `camotics_4axis_config.xml` - Machine configuration file

---

**Status**: Ready for HELIX G-code simulation ✅
**Estimated Time**: 15-30 minutes (first run)
**Safety Note**: Always simulate before running on hardware
