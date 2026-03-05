# 🎯 Fabex 4-Axis Configuration - CORRECTED WORKFLOW

**Date**: November 14, 2025
**Issue**: 4-axis options not visible in strategy dropdown
**Solution**: Must configure Machine Axes FIRST, then 4-axis strategies appear

---

## ✅ CORRECT Fabex Workflow (Step-by-Step)

### Step 1: Set Render Engine (REQUIRED!)

**This is a Fabex requirement - not optional**

1. Top header bar → **Render Engine dropdown** (default shows "Eevee")
2. Change to: **"FabEX CNC/CAM"** ✓

**Why**: Fabex uses a custom render engine for visualization. This must be set before operations work.

---

### Step 2: Select Your Object FIRST

**Before adding operations - critical!**

1. Click on **TestCylinder_Helix** in 3D viewport
2. Or select from Outliner (top-right panel)
3. Object should highlight in viewport

**Why**: Fabex validates object selection when adding operations. Adding operation without selection = error.

---

### Step 3: Open Fabex Panel

1. Press `N` key (toggle sidebar)
2. Click **"FabEX CNC"** tab
3. Panel may appear empty initially - this is normal

---

### Step 4: Add Operation

1. In Fabex panel, look for **"Operations"** section
2. Click **[+ Add]** button
3. New operation appears: "Operation"
4. CNC tab now populates with options ✓

---

### Step 5: Configure Machine Axes (CRITICAL FOR 4-AXIS!)

**This is the KEY step you were missing!**

Look for **"Machine Axes"** or **"Number of Axes"** dropdown:

1. Find property: **"Machine Axes"** or **"Number of Axes"**
2. Default is: **"3 axis"**
3. Change to: **"4 axis - EXPERIMENTAL"** ✓

**⚡ As soon as you change this, 4-axis options unlock!**

---

### Step 6: Configure 4-Axis Strategy

**Now the 4-axis strategies appear!**

After setting Machine Axes = 4, look for **"4 Axis Strategy"** dropdown:

**Available 4-Axis Strategies:**

- ✅ **HELIX** - "Helix around 1st rotary axis" ← USE THIS!
- **PARALLELR** - "Parallel around 1st rotary axis" (wraps around)
- **PARALLEL** - "Parallel along 1st rotary axis" (along length)
- **CROSS** - "Cross paths"
- **INDEXED** - "Indexed 3-axis" (manual indexing, not continuous)

**For your project**: Select **"HELIX"** ✓

---

### Step 7: Configure Rotary Axis

**Tell Fabex which axis is the rotary (A-axis)**

Look for **"Rotary Axis"** or **"Rotary Axis 1"** dropdown:

**Options:**

- **X** ← Your cylinder is oriented along X-axis, SELECT THIS!
- Y
- Z

**Important**: Must match your cylinder orientation. TestCylinder_Helix is along X, so select X.

---

### Step 8: Configure Standard Operation Settings

**Geometry:**

- Source: Object
- Object: TestCylinder_Helix (already selected)

**Cutter:**

- Type: End Mill
- Diameter: 6 mm
- Flutes: 4

**Feeds & Speeds:**

- Feed Rate: 500 mm/min
- Spindle Speed: 12000 RPM
- Plunge Rate: 250 mm/min

**Distance Settings:**

- Step Over: 3 mm
- Step Down: 3 mm
- Clearance: 10 mm

---

### Step 9: Machine Configuration (Create Preset)

**Post-Processor:**

- Select: **grbl**

**Machine envelope** (will set up presets for this):

- X: -400 to 400 mm
- Y: -400 to 400 mm
- Z: -150 to 50 mm
- A: Rotary (unlimited)

---

## 🏭 Creating Machine Presets

Fabex stores presets in Python files. Let me create presets for your machines:

### Preset 1: CNC Router 4-Axis

**File**: `F:\Documents\CODE\Blender-MCP\machine_presets\CNC_Router_4Axis_GRBL.py`

```python
# Machine: CNC Router 4-Axis XYZA
# Controller: GRBL
# Envelope: 800×800×200mm + rotary A-axis

import bpy

scene = bpy.context.scene

# Post-processor
scene.cam_machine.post_processor = 'grbl'

# Work area (in Blender units - meters)
scene.cam_machine.working_area.x = 0.800  # 800mm
scene.cam_machine.working_area.y = 0.800  # 800mm
scene.cam_machine.working_area.z = 0.200  # 200mm

# Position limits
scene.cam_machine.use_position_definitions = True
scene.cam_machine.starting_position.x = 0.0
scene.cam_machine.starting_position.y = 0.0
scene.cam_machine.starting_position.z = 0.050  # 50mm above table

# Rotary axis
scene.cam_machine.rotary_axis_1 = 'X'  # A-axis wraps around X

# Spindle
scene.cam_machine.spindle_default_rpm = 12000
scene.cam_machine.feed_default = 0.500  # 500mm/min in m/min

# Plunge
scene.cam_machine.plunge_default = 0.250  # 250mm/min

print("✅ CNC Router 4-Axis GRBL preset loaded")
```

---

### Preset 2: MOPA Fiber Laser

**File**: `F:\Documents\CODE\Blender-MCP\machine_presets\MOPA_Fiber_Laser.py`

```python
# Machine: MOPA Fiber Laser
# Type: Marking/engraving
# Envelope: TBD (provide your specs)

import bpy

scene = bpy.context.scene

# Post-processor (may need custom for laser)
scene.cam_machine.post_processor = 'iso'  # or custom laser post-processor

# Work area (adjust to your laser specs)
scene.cam_machine.working_area.x = 0.300  # 300mm (example)
scene.cam_machine.working_area.y = 0.300  # 300mm
scene.cam_machine.working_area.z = 0.100  # Focus height range

# Laser-specific settings
scene.cam_machine.spindle_default_rpm = 0  # Not applicable for laser
scene.cam_machine.feed_default = 0.100  # 100mm/min marking speed

print("✅ MOPA Fiber Laser preset loaded")
```

---

### Preset 3: Diode Laser

**File**: `F:\Documents\CODE\Blender-MCP\machine_presets\Diode_Laser.py`

```python
# Machine: Diode Laser
# Type: Engraving/cutting
# Envelope: TBD (provide your specs)

import bpy

scene = bpy.context.scene

# Post-processor
scene.cam_machine.post_processor = 'grbl'  # Many diode lasers use GRBL

# Work area (adjust to your laser specs)
scene.cam_machine.working_area.x = 0.400  # 400mm (example)
scene.cam_machine.working_area.y = 0.400  # 400mm
scene.cam_machine.working_area.z = 0.050  # Focus height

# Laser settings
scene.cam_machine.spindle_default_rpm = 0  # Laser power controlled via M3 S value
scene.cam_machine.feed_default = 0.200  # 200mm/min engraving speed

print("✅ Diode Laser preset loaded")
```

---

## 📁 Installing Machine Presets

### Method 1: Copy to Fabex Presets Directory

```powershell
# Create machine preset files
$presetsDir = "C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\extensions\blender_org\fabex\presets\cam_machines"

# Copy your custom presets
Copy-Item "F:\Documents\CODE\Blender-MCP\machine_presets\*.py" -Destination $presetsDir -Force

Write-Host "✅ Machine presets installed to Fabex"
```

### Method 2: Load via Script in Blender

1. Open Text Editor in Blender (top menu → Scripting workspace)
2. Open preset file
3. Run script (Alt+P)
4. Machine settings applied to current scene

---

## 🔍 Troubleshooting Your Specific Issues

### Issue 1: "CNC tab is empty until I change render engine"

**Status**: ✅ CORRECT BEHAVIOR

- Fabex requires "FabEX CNC/CAM" render engine
- Always set this first before working with operations

### Issue 2: "Error if no object selected"

**Status**: ✅ CORRECT BEHAVIOR

- Fabex validates geometry on operation add
- Workflow: Select object → Add operation → Configure

### Issue 3: "No 4-axis/rotary option in strategy dropdown"

**Status**: ❌ USER ERROR (now fixed!)

- **Root cause**: Machine Axes was set to "3 axis"
- **Solution**: Set Machine Axes = "4 axis - EXPERIMENTAL"
- **Result**: 4 Axis Strategy dropdown appears with HELIX option

### Issue 4: "Have we done any editing to original code?"

**Status**: ❌ NO CODE EDITS

- We have NOT modified Fabex source code
- All files in `extensions\blender_org\fabex\` are original from v1.0.68
- We only created external helper scripts (validate_gcode.ps1, etc.)

### Issue 5: "Is it working?"

**Status**: ✅ SHOULD WORK NOW

- With correct workflow (Machine Axes = 4), 4-axis features unlock
- HELIX strategy is available and should work for your cylinder
- Follow updated steps above

### Issue 6: "Need to add machine profiles"

**Status**: ✅ SOLUTION PROVIDED

- Created 3 machine preset templates above
- Need your actual specs for MOPA and Diode lasers
- Can install to Fabex presets directory or load via script

---

## 📋 Updated Workflow Summary

**Correct order:**

1. ✅ Set Render Engine: "FabEX CNC/CAM"
2. ✅ Select Object: TestCylinder_Helix
3. ✅ Add Operation
4. ✅ **Set Machine Axes: "4 axis - EXPERIMENTAL"** ← KEY STEP!
5. ✅ Select 4 Axis Strategy: "HELIX"
6. ✅ Set Rotary Axis: "X"
7. ✅ Configure cutter, feeds, speeds
8. ✅ Calculate Path
9. ✅ Export G-code

---

## 🎯 Next Steps

1. **In Blender (currently open):**

   - Change Machine Axes to "4 axis - EXPERIMENTAL"
   - Select "HELIX" from 4 Axis Strategy dropdown
   - Set Rotary Axis to "X"
   - Configure remaining settings
   - Calculate path

2. **Provide machine specs for presets:**

   - MOPA Fiber Laser work envelope (X, Y, Z ranges)
   - Diode Laser work envelope
   - Any special post-processor requirements

3. **After G-code generation:**
   - Run: `.\compare_gcode.ps1`
   - Validate scale is correct

---

**Ready to continue? Try the corrected workflow and let me know if HELIX strategy now appears!** 🚀
