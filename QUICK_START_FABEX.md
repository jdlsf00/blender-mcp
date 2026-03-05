# 🚀 Quick Start: Fabex 4-Axis Helix Configuration

**Project**: 4axis_helix_reference.blend
**Goal**: Generate corrected 4-axis helical G-code with proper scale (50mm, not 50m!)
**Machine**: CNC Router 4-Axis XYZA (800×800×200mm)

---

## 📋 Step-by-Step Configuration Guide

### Step 1: Open Project in Blender

```powershell
# Option A: Open from command line
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" "F:\Documents\CODE\Blender-MCP\reference_projects\4axis_helix_reference.blend"

# Option B: Double-click the file in File Explorer
# Navigate to: F:\Documents\CODE\Blender-MCP\reference_projects\
```

---

### Step 2: Verify Scene Setup

**What you should see:**

- Object: `TestCylinder_Helix`
- Dimensions: 50mm diameter × 100mm length
- Orientation: Along X-axis (rotary axis)

**Check Units (CRITICAL!):**

1. Go to: **Scene Properties** (icon looks like a scene/landscape on right panel)
2. Scroll to **Units** section
3. Verify:
   - Unit System: **Metric** ✓
   - Unit Scale: **1.0** ✓
   - Length: **Millimeters** ✓

**⚠️ If units are wrong, the G-code will have scale errors!**

---

### Step 3: Access Fabex Panel

1. Press `N` key to show right sidebar (if hidden)
2. Look at the top tabs: **Tool | Item | Fabex CNC**
3. Click **Fabex CNC** tab

**If "Fabex CNC" tab is missing:**

- Fabex addon not enabled
- Go to: Edit → Preferences → Get Extensions
- Search: "Fabex"
- Enable the checkbox

---

### Step 4: Add CAM Operation

In the **Fabex CNC** panel:

1. **Operations** section at top
2. Click **[+ Add New]** button
3. A new operation appears (default name: "Operation")

**Rename it:**

- Operation Name: `Helix_Test_50mm`

---

### Step 5: Configure Operation Strategy

**Strategy dropdown:**

- Look for: **4 Axis**, **Rotary**, or **Helix** option
- Select the appropriate strategy

**⚠️ Important Notes:**

- Fabex v1.0.68 has **experimental** 4-axis support
- 4-axis may be listed as "manual indexing" mode
- If true continuous 4-axis not available, we may need alternative approach

**Expected options** (depending on Fabex version):

- ✅ **4 Axis** - Continuous rotary + XYZ
- ✅ **Rotary 4 Axis** - Wrapped surface machining
- ⚠️ **Parallel** + Manual A-axis - Indexed milling (workaround)

**For now**: Select the most appropriate rotary/4-axis option available

---

### Step 6: Select Geometry

**Geometry Source:**

- Select: **Object**

**Object to Process:**

- Click the eyedropper icon 🎨
- Click on the cylinder in 3D view
- Or use dropdown and select: `TestCylinder_Helix`

**Verify:**

- Object name appears in the field
- Cylinder highlights in viewport

---

### Step 7: Configure Machine Settings

**Machine Section** (may need to expand):

**Post-Processor:**

- Select: **grbl** (for GRBL CNC controller)
- Alternative: **iso** (standard G-code)

**Work Area (in millimeters):**

```
X min: -400    X max: 400
Y min: -400    Y max: 400
Z min: -150    Z max: 50
```

**A-Axis (Rotary):**

- Enable A-axis: **✓ Checked**
- Type: **Rotary** or **Unlimited**
- A min: -99999 (unlimited rotation)
- A max: 99999

**Important:** If A-axis options aren't visible, the strategy may not support true 4-axis

---

### Step 8: Configure Cutter (Tool)

**Cutter Section:**

**Cutter Type:**

- Select: **End Mill** (flat end)

**Cutter Diameter:**

- Value: **6** mm (or 0.006 m depending on unit display)
- This is the 6mm end mill from your tool

**Cutter Settings:**

- Flutes: **4**
- Tip Angle: Not applicable for end mill

**Feed Rate:**

- Value: **500** mm/min
- This is the safe feed rate for your machine

**Spindle Speed:**

- Value: **12000** RPM
- Match your router's optimal speed

**Plunge Rate:**

- Value: **250** mm/min (typically 50% of feed rate)

---

### Step 9: Configure Operation Parameters

**Distance Settings:**

**Step Over (spacing between passes):**

- Value: **3** mm (50% of tool diameter = efficient)
- Smaller = finer finish, longer time

**Step Down (depth per pass):**

- Value: **3** mm for roughing
- For finishing: **1** mm

**Clearance Height:**

- Value: **10** mm above workpiece
- Safe height for rapid moves

**Stock to Leave:**

- Value: **0** mm (cutting to final dimensions)
- For roughing pass: **0.5** mm

---

### Step 10: Advanced Settings (Optional)

**Movement Type:**

- Climb milling (recommended for CNC routers)

**Optimize:**

- ✓ Enable optimization (reduces travel time)

**Use Layers:**

- If doing multiple depth passes, enable layers

**Helical Entry** (if available):

- Experimental feature
- Can enable for smoother entry

---

### Step 11: Calculate Toolpath

1. Click **[Calculate Path]** button
2. Wait for calculation (may take 30-60 seconds)
3. Watch Blender's status bar (bottom left) for progress

**What you should see:**

- Toolpath appears in 3D viewport as colored lines
- Orange/green paths showing tool movement
- Spiral/helical pattern around cylinder

**Expected toolpath stats:**

- Points: ~50,000-60,000
- A-axis rotation: 0° to ~18,355° (51 full rotations)
- XYZ movement: Helical wrap around cylinder

**If calculation fails:**

- Check Console: Window → Toggle System Console
- Look for error messages
- Common issues: Geometry not selected, invalid parameters

---

### Step 12: Preview & Verify

**Visual inspection:**

- Rotate view (middle mouse drag) to see toolpath from all angles
- Verify helical pattern covers entire cylinder
- Check for gaps or overlaps

**Check endpoints:**

- Path should start at safe height
- End at safe height
- A-axis should complete full surface coverage

---

### Step 13: Export G-code

1. Click **[Export G-code]** button
2. Save dialog appears
3. Navigate to: `F:\Documents\CODE\Blender-MCP\reference_projects\`
4. Filename: `blender_helix_reference.gcode`
5. Click **Save**

**File should be:**

- Size: ~2-5 MB (depending on resolution)
- Lines: ~50,000-60,000
- Contains: G21 (mm), G00/G01 (moves), A commands (rotary)

---

### Step 14: Validate G-code (CRITICAL!)

**Run the validation script:**

```powershell
cd F:\Documents\CODE\Blender-MCP
.\validate_gcode.ps1 -GCodePath "reference_projects\blender_helix_reference.gcode"
```

**Expected CORRECT output:**

```
✅ G21 (millimeters) found
✅ X range: 10-200 mm (correct for 100mm cylinder)
✅ Y range: 10-100 mm (correct for 50mm diameter)
✅ Z range: -150 to 50 mm (within work envelope)
✅ A-axis commands: ~58,000 instances
✅ A-axis range: 0° to 18,355° (~51 rotations)
✅ Tool commands: T1, M3 (spindle), F500 (feed)
```

**WRONG output (like original file):**

```
❌ X range: HUGE (50,000mm = 50 meters!)
❌ No A-axis commands
❌ Scale error detected
```

**If validation fails:**

- G-code has same scale error as before
- Check Blender units (Step 2)
- Check Fabex internal units
- May need to troubleshoot further

---

### Step 15: Compare with Original

**Compare files:**

```powershell
# Show file sizes
Get-Item "F:\Documents\CODE\Blender-MCP\reference_projects\*.gcode" |
  Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB,2)}}

# Compare coordinate ranges (first 50 lines)
Write-Host "`n=== ORIGINAL (WRONG) ===" -ForegroundColor Red
Get-Content "F:\Documents\CODE\Blender-MCP\helix_test_4axis.gcode" -TotalCount 50 |
  Select-String "G0|G1" | Select-Object -First 5

Write-Host "`n=== NEW (CORRECTED) ===" -ForegroundColor Green
Get-Content "F:\Documents\CODE\Blender-MCP\reference_projects\blender_helix_reference.gcode" -TotalCount 50 |
  Select-String "G0|G1" | Select-Object -First 5
```

**What to look for:**

- Original: X-49968 (50 meters!) ❌
- New: X-49.968 (50mm) ✅

---

## 🔧 Troubleshooting

### Issue: "4-Axis" or "Rotary" strategy not available

**Cause**: Fabex v1.0.68 has experimental 4-axis support

**Workarounds:**

**Option A: Manual Indexing**

1. Use **Parallel** strategy
2. Manually rotate object
3. Generate multiple operations at different A-angles
4. Combine G-code files manually

**Option B: Use FreeCAD Instead**

- FreeCAD Path workbench has proven 4-axis
- We can create equivalent project in FreeCAD
- Would you like me to create FreeCAD setup?

**Option C: Custom G-code Generation**

- Python script to generate helical toolpath
- Full control over A-axis movement
- Requires programming but guaranteed to work

---

### Issue: A-axis not showing in Fabex

**Solutions:**

1. Check strategy supports rotary
2. Enable A-axis in Machine settings
3. Set A-axis type to "Rotary" not "Linear"
4. Update Fabex if older version

---

### Issue: Scale still wrong in G-code

**Causes:**

- Blender units set to Meters (should be Millimeters)
- Unit scale not 1.0 (should be exactly 1.0)
- Fabex internal unit conversion issue

**Fix:**

1. Scene Properties → Units
2. Unit System: Metric
3. Length: Millimeters
4. Unit Scale: 1.0
5. Re-calculate toolpath
6. Re-export G-code

---

### Issue: Toolpath calculation fails

**Check:**

1. Object selected correctly
2. Object has mesh data (not empty)
3. Cutter diameter < workpiece size
4. Console for specific errors

---

### Issue: Toolpath looks wrong/gaps

**Adjust:**

- Step Over: Reduce to 2mm (finer passes)
- Step Down: Reduce to 2mm (shallower cuts)
- Strategy: Try different 4-axis mode
- Optimize: Toggle on/off

---

## 📊 Expected Results

**If everything works correctly:**

**File output:**

- `blender_helix_reference.gcode` (~2-5 MB)
- ~50,000-60,000 lines
- Proper scale (coordinates in millimeters)
- A-axis commands for rotary motion
- G21 (millimeter mode)
- GRBL-compatible format

**Coordinates:**

- X: -50 to +50 mm (cylinder ends)
- Y: -25 to +25 mm (cylinder radius)
- Z: -150 to +50 mm (work envelope)
- A: 0° to 18,355° (51 rotations)

**Movement:**

- Rapid moves (G00) at clearance height
- Linear moves (G01) at feed rate
- Coordinated XYZA for helical pattern

---

## 🎯 Next Steps After Successful Export

1. ✅ **Validate G-code** with script (catch any issues)
2. ✅ **Simulate** in CAMotics or NC Viewer (visual verification)
3. ✅ **Air cut** on machine (no material, verify movements)
4. ✅ **Test cut** on soft material (foam/wood)
5. ✅ **Production cut** on final material

**DO NOT skip simulation and air cutting!**

---

## 📁 Reference Files

**Your project files:**

- Project: `4axis_helix_reference.blend` (pre-configured)
- Output: `blender_helix_reference.gcode` (to be generated)
- Original: `helix_test_4axis.gcode` (has scale error)
- Machine config: `camotics_4axis_config.xml`

**Scripts & guides:**

- Validation: `validate_gcode.ps1`
- Checklist: `VALIDATION_CHECKLIST.md`
- Optimization: `BLENDER_OPTIMIZATION_GUIDE.md`

---

## ⚠️ Important Safety Reminders

Before running on actual machine:

1. **Verify coordinates** - No values > 400mm (machine limits)
2. **Check Z-height** - Ensure tool won't crash into fixture
3. **Verify A-axis** - Rotation direction correct for your machine
4. **Air cut first** - Run with Z +50mm offset (no material)
5. **Emergency stop ready** - Know where E-stop button is
6. **Workpiece secured** - Cylinder properly clamped for rotation

---

## 🚀 You're Ready!

**Open Blender and follow Steps 1-15 above.**

When you encounter any issues or questions, stop and let me know:

- Screenshot of the Fabex panel
- Error messages from Console
- Description of what's not working

Good luck! 🎉
