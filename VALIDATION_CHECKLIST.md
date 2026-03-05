# 4-Axis Rotary Milling Validation Checklist

**Purpose**: Systematic validation of BlenderCAM and FreeCAD 4-axis rotary milling with actual machine parameters
**Date**: 2025-11-13
**Status**: Blender setup complete → Manual validation required

---

## Machine Specifications (Your CNC Router)

```
CNC Router - 4-Axis XYZA
├── X-Axis: -400 to 400mm (800mm travel)
├── Y-Axis: -400 to 400mm (800mm travel)
├── Z-Axis: -150 to 50mm (200mm travel)
└── A-Axis: Rotary (unlimited rotation)

Tool: 6mm end mill, 4-flute, END type
Feed Rate: 500mm/min
Spindle Speed: 12000 RPM
```

---

## Phase 1: Blender Project Validation ✅ SETUP COMPLETE

### ✅ Automated Setup Completed

- [x] Project created: `F:\Documents\CODE\Blender-MCP\reference_projects\4axis_helix_reference.blend`
- [x] Units configured: METRIC / Millimeters / Scale 1.0
- [x] Cylinder created: 50mm diameter × 100mm length
- [x] Cylinder oriented along X-axis (rotary axis)
- [x] Camera positioned for visualization
- [x] File saved (430.8 KB)
- [x] **Alternative Toolpath Generator**: Created `true_4axis_generator.py` (451 lines, working)
- [x] **Working Visualization**: Blender 4.5 script debugged and tested (277 lines)
- [x] **Complex Shapes Generated**: 5 mathematical examples (chess pawn, Bezier vase, etc.)

### 🔲 Manual Steps Required (YOU DO THIS)

Open the Blender project and complete these steps:

#### Step 1: Enable Fabex Addon

```
1. Open Blender
2. File → Open → Navigate to:
   F:\Documents\CODE\Blender-MCP\reference_projects\4axis_helix_reference.blend
3. Edit → Preferences → Add-ons
4. Search: "Fabex"
5. ✓ Enable the checkbox
6. Close Preferences
```

#### Step 2: Verify Units (CRITICAL!)

```
1. Go to: Scene Properties (icon looks like a scene/camera)
2. Units section:
   • Unit System: METRIC ✓
   • Unit Scale: 1.000 ✓
   • Length: Millimeters ✓
3. If ANY of these are wrong, STOP and fix them!
```

**Why this matters**: Your previous G-code had coordinates like X-49968 (50 meters!) instead of X-49.968 (50mm). This suggests units were set to meters or scale was 1000x.

#### Step 3: Select Cylinder

```
1. Click on the cylinder in 3D viewport
2. Verify in Properties panel:
   • Name: TestCylinder_Helix
   • Dimensions should show:
     X: 100mm (length along rotary)
     Y: 50mm (diameter)
     Z: 50mm (diameter)
```

#### Step 4: Add CAM Operation

```
1. Switch to CAM Operations panel (right sidebar)
   • If not visible: View → Toggle Sidebar (N key)
2. Click "+" to add new CAM operation
3. Settings:
   • Operation Type: HELIX (continuous wrapping)
   • Geometry: Select TestCylinder_Helix
   • Cutter Type: End Mill
   • Cutter Diameter: 6mm
```

#### Step 5: Configure Machine Settings

```
CAM → Machine Settings:
• Machine Name: 4-Axis CNC Router
• Post-processor: GRBL (for your machine)

Axes Limits:
• X Min: -400mm, Max: 400mm
• Y Min: -400mm, Max: 400mm
• Z Min: -150mm, Max: 50mm
• A-Axis: ✓ Enable, Rotary: ✓ Yes

Working Area: 800×800×200mm
```

#### Step 6: Configure HELIX Operation

```
Operation Parameters:
• Strategy: HELIX
• Direction: Conventional (or Climb)
• Stepover: 1mm (adjust for desired surface finish)
• Depth per Pass: N/A (rotary wraps around)

Rotary Settings:
• Enable A-Axis: ✓
• Rotation Axis: X (cylinder lies along X)
• Start Angle: 0°
• End Angle: Let it calculate (should be ~18,355° for full coverage)
```

#### Step 7: Calculate Toolpath

```
1. Click "Calculate Path" button
2. Wait for calculation (may take 30-60 seconds)
3. Toolpath should appear as orange/green lines wrapping around cylinder
4. Check statistics:
   • Should show A-axis commands
   • Line count should be ~50,000-60,000
```

#### Step 8: Export G-Code

```
1. Click "Export G-code"
2. Post-processor: GRBL
3. Save as: F:\Documents\CODE\Blender-MCP\reference_projects\blender_helix_reference.gcode
4. ✓ Confirm file saved
```

#### Step 9: CRITICAL VALIDATION

Open the generated G-code file and check:

```powershell
# Open in text editor
notepad "F:\Documents\CODE\Blender-MCP\reference_projects\blender_helix_reference.gcode"

# Check first 20 lines
Get-Content "F:\Documents\CODE\Blender-MCP\reference_projects\blender_helix_reference.gcode" -TotalCount 20
```

**Look for these indicators:**

✅ **CORRECT** (units in millimeters):

```gcode
G21                    ← Millimeter mode
G00 X-49.968 Y0 Z10    ← Coordinates around 50mm range
G01 A45.678            ← A-axis rotation commands present
```

❌ **WRONG** (units messed up):

```gcode
G00 X-49968.17         ← 50 METERS (1000x too big!)
G00 X-0.049968         ← 0.05mm (1000x too small!)
(No A commands)        ← Missing rotary axis
```

#### Step 10: Report Results

Once validated, report:

- [ ] Units verified correct in Blender (METRIC/mm/1.0)
- [ ] Toolpath calculated successfully
- [ ] G-code exported
- [ ] G-code coordinates in ~50mm range (NOT 50,000mm)
- [ ] A-axis commands present (A0 to A~18,355)
- [ ] File size: **\_** KB/MB
- [ ] Line count: **\_** lines

---

## Phase 2: FreeCAD Project Validation (NEXT)

### Automated Setup (Script to be created)

Will generate:

- FreeCAD project with 50mm × 100mm cylinder
- Path workbench 4-axis rotary job
- Machine configuration matching your CNC router
- Helix or 3D Surface operation
- GRBL post-processor output

### Manual Steps (After script runs)

Similar validation process:

1. Open FreeCAD project
2. Verify Part dimensions
3. Check Path job configuration
4. Validate machine axes setup
5. Generate toolpath
6. Export G-code
7. Validate coordinates and A-axis

---

## Phase 3: Comparison & Analysis

Once both G-code files are generated:

```powershell
# Compare file sizes
Get-ChildItem "F:\Documents\CODE\Blender-MCP\reference_projects" -Filter "*.gcode" |
    Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB,1)}}

# Compare coordinate ranges (first 1000 lines)
# Will create comparison script
```

### What to Compare:

- [ ] Both use G21 (millimeters)
- [ ] Coordinate ranges match (~50mm cylinder)
- [ ] A-axis rotation similar (both ~0° to 18,355°)
- [ ] Line counts within 20% of each other
- [ ] Both simulate correctly in CAMotics/NC Viewer
- [ ] Toolpath patterns look similar

### Expected Outcome:

If both generate valid G-code with correct scale, we can:

1. Identify what was wrong with original BlenderCAM export
2. Use either tool confidently for production
3. Proceed to hardware testing phase

---

## Troubleshooting

### Issue: Blender G-code still has wrong scale

**Possible causes:**

1. Object scale in Blender is wrong

   - Select cylinder → Properties → Scale should be (1.0, 1.0, 1.0)
   - If not: Select object → Apply Scale (Ctrl+A → Scale)

2. Units not actually set correctly

   - Double-check Scene Properties → Units
   - Try setting Length to "Meters" then back to "Millimeters"

3. BlenderCAM addon has internal scale setting
   - Check CAM preferences for unit conversion settings

### Issue: No A-axis commands in G-code

**Possible causes:**

1. A-axis not enabled in machine configuration
2. Operation not set as rotary/4-axis
3. Post-processor doesn't support A-axis (try different processor)

### Issue: Toolpath calculation fails

**Possible causes:**

1. Geometry has errors (non-manifold, inverted normals)
2. Tool diameter too large for cylinder
3. Machine limits too restrictive

---

## Next Steps After Validation

Once you have validated G-code from Blender (and optionally FreeCAD):

1. **Simulation**: Load into CAMotics with corrected workpiece size
2. **Parallel Strategy**: Test PARALLELR (line-by-line vertical milling)
3. **Hardware Testing**: Air cutting test on actual CNC
4. **Material Tests**: Progressive testing on scrap → production parts

---

## FreeCAD Visualization Troubleshooting ⚠️

### Issue: `No module named 'gcode_pre'` Error

**Problem**: FreeCAD misparses script filename when executing directly

```
ModuleNotFoundError: No module named 'gcode_pre'
Exception while processing file: chess_pawn.gcode
```

**Root Cause**: FreeCAD's Python integration has issues with direct script execution

- Splits filename incorrectly: `gcode_pre` from `gcode.py` or similar
- Import system conflicts with FreeCAD's module structure

**Solution - Method 1: Use FreeCAD Macro (RECOMMENDED)**

```
1. Open FreeCAD
2. Macro → Macros... (Alt+F8)
3. User macros location: Copy freecad_4axis_viewer.FCMacro
4. Execute macro → Browse to select G-code file
5. Result: Cylinder stock + red toolpath visualization
```

**Solution - Method 2: Continue Using Blender (PROVEN)**

```powershell
# Blender visualization is fully working - use this instead
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" `
  --background --python "visualize_4axis_blender.py" `
  -- "test_output\chess_pawn.gcode" "chess_pawn_viz.blend"

# Open result
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" chess_pawn_viz.blend
```

**Current Status**:

- ✅ Blender visualization: WORKING (277 lines, production-ready)
- ✅ Coordinate mapping: Corrected (X,Z,Y) transform
- ✅ Tool positioning: Tip contacts surface (+25mm offset)
- ✅ Multiple shapes tested: Chess pawn, Bezier vase, helical column
- ⚠️ FreeCAD direct execution: Use macro method instead

**Recommendation**: Continue with Blender for visualization

- Proven working with 5 complex shapes
- Animation support (keyframes)
- All coordinate issues resolved
- Use FreeCAD macro only if STEP/IGES export needed

See `FREECAD_GUIDE.md` for detailed instructions.

---

## Reference Files

### Created Files:

- `setup_blender_4axis_project.py` - Automated Blender project setup
- `4axis_helix_reference.blend` - Blender project file (430.8 KB)
- `camotics_4axis_config.xml` - CAMotics machine configuration
- `HARDWARE_TESTING_WORKFLOW.md` - Complete testing procedures
- **`true_4axis_generator.py`** - Corrected 4-axis kinematics (451 lines, working)
- **`visualize_4axis_blender.py`** - Blender 4.5 visualizer (277 lines, debugged)
- **`generate_complex_geometry.py`** - 5 mathematical shapes (386 lines)
- **`surface_3d_generator.py`** - 3D surface framework (248 lines, needs implementation)
- `freecad_4axis_viewer.FCMacro` - FreeCAD macro (use this for FreeCAD)
- `FREECAD_GUIDE.md` - FreeCAD troubleshooting guide

### Machine Specs Source:

From `camotics_4axis_config.xml` lines 14-22:

```xml
<axis name="X" min="-400" max="400" home="0" />
<axis name="Y" min="-400" max="400" home="0" />
<axis name="Z" min="-150" max="50" home="50" />
<axis name="A" min="-99999" max="99999" rotary="true" home="0" />
```

---

**Ready to proceed with manual validation in Blender!**
