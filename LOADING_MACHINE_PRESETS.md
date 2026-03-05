# Loading Machine Presets in Fabex

## Issue

Machine presets are installed to file system but not visible in Fabex UI.

**Root cause**: Fabex may not have a machine preset dropdown in GUI. Presets are loaded by running them as Python scripts.

---

## ✅ How to Load Machine Presets

### Method 1: Text Editor (Recommended)

1. **Open Blender** with your project
2. **Switch to Scripting workspace**:

   - Click "Scripting" tab at top of Blender window
   - OR: Top menu → Window → Toggle Scripts Editor

3. **Open preset file**:

   - In Text Editor panel (large area with "+ New" button)
   - Click "Open" button (folder icon)
   - Navigate to: `C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\extensions\blender_org\fabex\presets\cam_machines\`
   - Select: `CNC_Router_4Axis_GRBL.py`
   - Click "Open Text"

4. **Execute preset script**:

   - With preset file open in Text Editor
   - Press: **Alt + P** (or click ▶ play button at top of Text Editor)
   - You'll see: "Machine settings applied to scene" (if successful)

5. **Verify application**:
   - Switch back to "Layout" workspace
   - FabEX CNC panel → Machine Settings should now show:
     - Post Processor: grbl
     - Working Area: 800 × 800 × 200 mm
     - Rotary Axis: X
     - Spindle: 12000 RPM
     - Feed: 500 mm/min

---

### Method 2: Drag and Drop (Alternative)

1. Open Windows File Explorer
2. Navigate to: `C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\extensions\blender_org\fabex\presets\cam_machines\`
3. Drag `CNC_Router_4Axis_GRBL.py` directly into Blender window
4. File opens in Text Editor automatically
5. Press **Alt + P** to execute

---

### Method 3: Via Blender Python Console

1. Switch to "Scripting" workspace
2. In Python Console (bottom panel):
   ```python
   import bpy
   preset_path = r"C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\extensions\blender_org\fabex\presets\cam_machines\CNC_Router_4Axis_GRBL.py"
   exec(compile(open(preset_path).read(), preset_path, 'exec'))
   print("Preset loaded")
   ```
3. Press **Enter** to execute

---

## 📦 Available Presets

You have 3 presets installed:

### 1. CNC_Router_4Axis_GRBL.py ✅ READY

Complete configuration for your CNC router:

- **Controller**: GRBL
- **Work Area**: 800 × 800 × 200 mm
- **Rotary Axis**: X
- **Spindle**: 12000 RPM max
- **Feed Rates**: 500 mm/min (cutting), 250 mm/min (plunge)
- **Post Processor**: grbl

**Use this for**: Your current 4-axis helix project

---

### 2. MOPA_Fiber_Laser_TEMPLATE.py ⚠️ NEEDS CONFIG

Template requiring your laser specifications:

**Edit before using**:

```python
# TODO: Replace with your actual MOPA laser specs
WORK_AREA_X_MM = 300  # Your laser's X working area
WORK_AREA_Y_MM = 300  # Your laser's Y working area
WORK_AREA_Z_MM = 100  # Your laser's Z working area
MARKING_SPEED = 100   # Your marking speed (mm/min)
TRAVEL_SPEED = 1000   # Your rapid travel speed (mm/min)
POST_PROCESSOR = 'iso'  # May need custom post-processor
```

**To edit**:

1. Open preset in Text Editor (Method 1 above)
2. Modify values with your actual machine specs
3. Text menu → Save As → Save modified version
4. Execute with Alt+P

---

### 3. Diode_Laser_TEMPLATE.py ⚠️ NEEDS CONFIG

Template requiring your diode laser specifications:

**Edit before using**:

```python
# TODO: Replace with your actual diode laser specs
WORK_AREA_X_MM = 400
WORK_AREA_Y_MM = 400
WORK_AREA_Z_MM = 50
ENGRAVING_SPEED = 200  # mm/min
CUTTING_SPEED = 100    # mm/min
TRAVEL_SPEED = 3000    # mm/min
POST_PROCESSOR = 'grbl'  # Typical for diode lasers
```

**Note**: Diode lasers use spindle S parameter for power:

- M3 S1000 = constant power (use for cutting)
- M4 S1000 = dynamic power (use for engraving)
- M5 = laser off

---

## 🔄 Switching Between Machines

To switch machines mid-project:

1. Open different preset file in Text Editor
2. Press Alt+P to execute
3. Fabex machine settings update immediately
4. Existing operations keep their settings unless you recalculate

---

## 💾 Creating Custom Presets

To create your own machine preset:

1. **Copy existing preset**:

   ```powershell
   Copy-Item "F:\Documents\CODE\Blender-MCP\machine_presets\CNC_Router_4Axis_GRBL.py" "F:\Documents\CODE\Blender-MCP\machine_presets\My_Custom_Machine.py"
   ```

2. **Edit in text editor** (VS Code, Notepad++):

   - Change machine name
   - Modify working area dimensions
   - Update feed rates, spindle speeds
   - Change post-processor

3. **Install**:

   ```powershell
   cd F:\Documents\CODE\Blender-MCP
   .\install_machine_presets.ps1
   ```

4. **Load in Blender** via Text Editor → Alt+P

---

## 📋 Quick Reference

| Task                       | Steps                                                         |
| -------------------------- | ------------------------------------------------------------- |
| **Load CNC Router preset** | Scripting workspace → Open → CNC_Router_4Axis_GRBL.py → Alt+P |
| **Verify preset applied**  | Check Machine Settings in FabEX CNC panel                     |
| **Edit laser templates**   | Open in Text Editor → Modify values → Save → Alt+P            |
| **Switch machines**        | Open different preset → Alt+P                                 |
| **Create custom preset**   | Copy existing → Edit → Install → Load                         |

---

## 🎯 For Your Current Project

**To use your CNC Router preset right now**:

1. Blender already open with `4axis_helix_reference.blend`? ✅
2. Click **"Scripting"** tab at top
3. Text Editor → **"Open"** (folder icon)
4. Navigate to preset directory (path above)
5. Open: **CNC_Router_4Axis_GRBL.py**
6. Press: **Alt + P**
7. Switch back to **"Layout"** workspace
8. Check FabEX CNC → Machine Settings to verify

**Then proceed with workaround** from `FABEX_4AXIS_BUG_WORKAROUND.md` to generate G-code.

---

## ❓ Troubleshooting

**Preset doesn't execute / no output**:

- Check Python Console for errors (Scripting workspace, bottom panel)
- Verify preset file syntax (should see `machine = scene.cam_machine`)
- Check file was saved (Text menu → Revert to see if changes lost)

**Machine settings don't change**:

- Verify you're in correct scene (check top header, Scene dropdown)
- Check Fabex operation exists (settings apply to scene, not individual operations)
- Try closing/reopening Blender to refresh

**Can't find preset directory**:

- Copy path from above and paste directly into File Explorer address bar
- OR use PowerShell:
  ```powershell
  explorer "C:\Users\jdlsf00\AppData\Roaming\Blender Foundation\Blender\4.5\extensions\blender_org\fabex\presets\cam_machines\"
  ```

---

Ready to load your CNC Router preset? Let me know if you need help with any step!
