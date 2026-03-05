# G-code Simulation & Verification Options

## Overview

Comprehensive guide to G-code simulation tools for verifying BlenderCAM-generated toolpaths before hardware execution. This document covers installed tools, browser-based options, and CAMotics installation.

**Last Updated**: 2025-11-13
**Status**: Ready for implementation

---

## ✅ Installed Tools (Available Now)

### 1. Candle - GRBL Sender & Visualizer ⭐ RECOMMENDED

**Status**: Already installed at `F:\Documents\Candle\`

**Features**:

- 3D toolpath visualization
- G-code line-by-line preview
- Real-time simulation playback
- Built-in GRBL sender for hardware control
- 4-axis (XYZA) support
- Free and open-source

**Best For**:

- GRBL-formatted G-code (our primary format)
- Quick local verification
- Integrated sending to CNC hardware
- Real-time jog controls

**Usage**:

```powershell
# Launch Candle
Start-Process "F:\Documents\Candle\Candle.exe"

# Open G-code file
# File → Open → Select helix_4axis_test_GRBL.gcode
# View → 3D View to see toolpath
# Check A-axis rotation in visualization
```

**Limitations**:

- Basic collision detection only
- No material removal simulation
- GRBL-focused (works best with GRBL post-processor)

---

### 2. LightBurn - Laser-Specific Simulator

**Status**: Already installed at `F:\Documents\Lightburn\`

**Features**:

- Laser-optimized preview
- Power/speed visualization
- Material cut/engrave simulation
- Camera alignment support
- Job time estimation

**Best For**:

- MOPA fiber laser test patterns
- Diode laser test patterns
- Laser engraving projects
- Power/speed matrix testing

**Usage**:

```powershell
# Launch LightBurn
Start-Process "F:\Documents\Lightburn\LightBurn.exe"

# Import test pattern
# File → Import → Select MOPA_Test_Grid.blend or DXF export
# Preview in Preview window
# Check power levels and speeds
```

**Limitations**:

- Laser-focused (not for CNC milling)
- Limited 4-axis support
- Requires LightBurn-compatible file formats

---

### 3. FreeCAD Path Workbench

**Status**: Already installed at `F:\Documents\FreeCAD\`

**Features**:

- Full CAM workflow (CAD → CAM → Simulation)
- Post-processor library
- 3D toolpath simulation
- Collision detection
- 4-axis support via custom configurations

**Best For**:

- Complex part validation
- Engineering analysis
- Alternative CAM workflow comparison
- Educational/learning purposes

**Usage**:

```python
# Open FreeCAD
# Switch to Path workbench
# File → Import → Select STL test part
# Path → Inspect G-code
# View → Taskbar → Simulate for playback
```

**Limitations**:

- Steeper learning curve
- Requires manual setup for 4-axis
- Slower than dedicated simulators

---

## 🌐 Browser-Based Options (No Installation)

### 1. NC Viewer ⭐ FASTEST OPTION

**URL**: https://ncviewer.com

**Features**:

- Instant drag-and-drop G-code loading
- 3D toolpath visualization
- Line-by-line code view
- Zoom/pan/rotate controls
- Multi-format support (G-code, TAP, NGC)
- **4-axis rotation visualization** (A-axis support confirmed)

**Best For**:

- Quick verification (30 seconds)
- No installation needed
- Cross-platform (any browser)
- Sharing with team members

**Usage**:

1. Open https://ncviewer.com
2. Click "Plot" button
3. Drag & drop `helix_4axis_test_GRBL.gcode`
4. Inspect toolpath in 3D viewer
5. Check A-axis commands in code panel

**Pros**:

- ✅ Zero setup time
- ✅ Works on any device
- ✅ Clean interface
- ✅ 4-axis visualization

**Cons**:

- ❌ No collision detection
- ❌ No material removal simulation
- ❌ Internet connection required

---

### 2. OpenBuilds CAM & Control

**URL**: https://cam.openbuilds.com

**Features**:

- CAM generation + simulation
- Real-time toolpath preview
- Machine control integration
- GRBL-optimized
- Cloud-based project storage

**Best For**:

- All-in-one CAM workflow
- GRBL CNC machines
- OpenBuilds hardware users

**Usage**:

1. Create free account at cam.openbuilds.com
2. Upload DXF/SVG or generate toolpath
3. Use "Simulate" tab for preview
4. Export G-code

**Pros**:

- ✅ CAM + simulation in one tool
- ✅ No installation

**Cons**:

- ❌ Requires account signup
- ❌ Limited 4-axis support
- ❌ Focused on 2.5D operations

---

### 3. io-cnc G-Code Simulator

**URL**: https://io-cnc.com

**Features**:

- Simple drag-and-drop interface
- Basic 3D visualization
- Lightweight and fast

**Best For**:

- Ultra-quick checks
- Simple 3-axis verification

**Limitations**:

- ❌ Limited 4-axis support
- ❌ Basic features only

---

## 🔧 CAMotics - Advanced Material Removal Simulation ✅ INSTALLED

### Overview

**Status**: ✅ Installed and ready for use

CAMotics is a free, open-source G-code simulator that performs **realistic material removal simulation**, showing exactly what will be cut from the workpiece.

**Official Website**: https://camotics.org
**GitHub**: https://github.com/CauldronDevelopmentLLC/CAMotics

**📖 Quick Start Guide**: See `camotics_quick_start.md` for step-by-step HELIX simulation
**⚙️ Machine Configuration**: See `camotics_4axis_config.xml` for 4-axis CNC profile

### Key Features

- ✅ **3D material removal simulation** (see actual cuts in virtual material)
- ✅ **Collision detection** (tool vs. workpiece, tool vs. fixture)
- ✅ **STL workpiece import** (simulate on custom stock models)
- ✅ **4-axis support** (XYZA rotary configuration)
- ✅ **Multi-tool support** (verify tool changes)
- ✅ **Free and open-source** (no licensing costs)
- ✅ **Cross-platform** (Windows, Linux, macOS)

### Installation Instructions

#### Windows Installation (Recommended)

```powershell
# Download installer from camotics.org
Start-Process "https://camotics.org/download.html"

# Or use winget (if available)
winget install CAMotics.CAMotics

# Or use Chocolatey
choco install camotics
```

**Manual Installation**:

1. Download Windows installer from https://camotics.org/download.html
2. Run `CAMotics-x.x.x-Windows.exe`
3. Follow installation wizard
4. Default install location: `C:\Program Files\CAMotics\`

#### Verify Installation

```powershell
# Check if CAMotics is installed
Get-Command camotics -ErrorAction SilentlyContinue

# Or check install directory
Test-Path "C:\Program Files\CAMotics\camotics.exe"
```

### Configuration for 4-Axis CNC

**Machine Configuration** (`machine.xml`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<camotics>
  <machine>
    <name>4-Axis CNC Router</name>
    <axes>
      <axis name="X" min="-400" max="400" />
      <axis name="Y" min="-400" max="400" />
      <axis name="Z" min="-150" max="50" />
      <axis name="A" min="-9999" max="9999" rotary="true" />
    </axes>
    <tool-change>
      <x>0</x>
      <y>0</y>
      <z>50</z>
    </tool-change>
  </machine>
</camotics>
```

### Usage Workflow

#### 1. Basic Simulation

```powershell
# Launch CAMotics
camotics.exe

# Or from PowerShell
Start-Process "C:\Program Files\CAMotics\camotics.exe"
```

**GUI Steps**:

1. File → Open → Select `helix_4axis_test_GRBL.gcode`
2. View → Workpiece → Set dimensions (50mm × 50mm × 100mm cylinder)
3. Tools → Configure → Set tool diameter (6mm)
4. Simulation → Run → Watch material removal
5. View → Rotate to inspect A-axis cuts

#### 2. Advanced Simulation with STL Workpiece

```powershell
# Generate STL workpiece from Blender test part
blender --background test_parts/TestCylinder_001.blend --python export_stl.py

# Import in CAMotics
# File → Import Workpiece → Select TestCylinder_001.stl
# File → Open G-code → Select helix_4axis_test_GRBL.gcode
# Simulation → Run
```

#### 3. Collision Detection

1. Enable collision detection: View → Show Collisions
2. Run simulation
3. Red highlights indicate tool collisions
4. Review G-code lines causing collisions

### CAMotics vs. Other Tools

| Feature                   | CAMotics                   | Candle             | NC Viewer            | LightBurn      |
| ------------------------- | -------------------------- | ------------------ | -------------------- | -------------- |
| **Material Removal Sim**  | ✅ Yes                     | ❌ No              | ❌ No                | ⚠️ 2D          |
| **Collision Detection**   | ✅ Yes                     | ⚠️ Basic           | ❌ No                | ❌ No          |
| **4-Axis Support**        | ✅ Yes                     | ✅ Yes             | ✅ Yes               | ⚠️ Limited     |
| **STL Workpiece Import**  | ✅ Yes                     | ❌ No              | ❌ No                | ❌ No          |
| **Installation Required** | ✅ Yes                     | ✅ Yes             | ❌ No                | ✅ Yes         |
| **Learning Curve**        | Medium                     | Low                | Low                  | Medium         |
| **Best Use Case**         | Safety-critical validation | Quick local checks | Instant verification | Laser projects |

---

## 🎯 Recommended Workflow

### Phase 1: Quick Verification (2 minutes)

```powershell
# Option A: NC Viewer (browser)
Start-Process "https://ncviewer.com"
# Drag & drop helix_4axis_test_GRBL.gcode

# Option B: Candle (local)
Start-Process "F:\Documents\Candle\Candle.exe"
# File → Open → helix_4axis_test_GRBL.gcode
```

**Check**:

- ✅ Toolpath loads without errors
- ✅ A-axis rotation visible (0° → 18,355°)
- ✅ 51 revolutions completed
- ✅ No obvious path errors

---

### Phase 2: Material Removal Simulation (5-10 minutes) - OPTIONAL

**Install CAMotics** (if collision detection needed):

```powershell
# Download and install
Start-Process "https://camotics.org/download.html"

# Configure 4-axis machine profile
# Import G-code
# Run simulation
```

**Check**:

- ✅ No tool collisions with workpiece
- ✅ Material removal matches expected part
- ✅ A-axis rotation smooth and continuous
- ✅ Tool doesn't exceed work envelope

---

### Phase 3: Laser Pattern Simulation (5 minutes)

**For MOPA/Diode Patterns**:

```powershell
# Launch LightBurn
Start-Process "F:\Documents\Lightburn\LightBurn.exe"

# Import test pattern
# File → Import → MOPA_Test_Grid.blend (or DXF export)
```

**Check**:

- ✅ Power levels correct (20W-80W for MOPA)
- ✅ Speed settings correct (50-200mm/s)
- ✅ Grid alignment proper
- ✅ Job time estimate reasonable

---

### Phase 4: Air Cutting Test (10 minutes) - SAFETY CRITICAL

**Before ANY material cutting**:

1. Load verified G-code into machine controller
2. Set Z-axis offset +50mm (tool above workpiece)
3. Run program at 100% speed
4. Visually verify:
   - ✅ No unexpected rapids
   - ✅ A-axis rotates smoothly (51 revolutions)
   - ✅ No machine alarms
   - ✅ Tool doesn't hit fixtures

**Only proceed to material cutting after air test passes.**

---

## 📊 Simulation Decision Matrix

### When to Use Each Tool

| Scenario                             | Recommended Tool       | Reason                            |
| ------------------------------------ | ---------------------- | --------------------------------- |
| **Quick 30-second check**            | NC Viewer (browser)    | Zero setup, instant results       |
| **Local verification (no internet)** | Candle                 | Already installed, GRBL-optimized |
| **Collision detection needed**       | CAMotics               | Material removal simulation       |
| **Laser test patterns**              | LightBurn              | Laser-specific features           |
| **Engineering analysis**             | FreeCAD Path           | Full CAM workflow                 |
| **Before first hardware run**        | Candle + Air cutting   | Multi-layer verification          |
| **Before expensive material**        | CAMotics + Air cutting | Maximum safety validation         |
| **Team collaboration/remote review** | NC Viewer (share link) | Browser-based, no install needed  |

---

## 🚀 Next Steps

### Immediate Actions

1. **Test NC Viewer** (5 minutes):

   - Open https://ncviewer.com
   - Load `helix_4axis_test_GRBL.gcode`
   - Verify 4-axis visualization

2. **Test Candle** (10 minutes):

   - Launch `F:\Documents\Candle\Candle.exe`
   - Open `helix_4axis_test_GRBL.gcode`
   - Inspect 3D toolpath

3. **Optional: Install CAMotics** (30 minutes):

   - Download from camotics.org
   - Install and configure 4-axis machine
   - Run material removal simulation

4. **Test Laser Patterns in LightBurn** (15 minutes):
   - Open LightBurn
   - Import MOPA_Test_Grid and Diode_Gradation_Test
   - Verify power/speed parameters

### Before Hardware Testing

- [ ] G-code verified in at least one simulator
- [ ] 4-axis rotation confirmed (51 revolutions)
- [ ] No obvious path errors
- [ ] Tool parameters correct
- [ ] Air cutting test planned
- [ ] Safety checklist reviewed

---

## 📚 Additional Resources

### Official Documentation

- **Candle**: https://github.com/Denvi/Candle
- **CAMotics**: https://camotics.org/manual.html
- **NC Viewer**: https://ncviewer.com/help
- **LightBurn**: https://lightburnsoftware.github.io/NewDocs/

### Video Tutorials

- NC Viewer Quick Start: Search "NC Viewer tutorial" on YouTube
- CAMotics 4-Axis Setup: Search "CAMotics rotary axis" on YouTube
- Candle GRBL Sender: Search "Candle CNC tutorial" on YouTube

### Community Support

- **BlenderCAM (Fabex)**: https://github.com/vilemduha/blendercam/issues
- **GRBL Forums**: https://github.com/gnea/grbl/discussions
- **CNCZone**: https://www.cnczone.com/forums/

---

## ✅ Validation Checklist

Before proceeding to hardware testing:

- [ ] G-code opens without errors in simulator
- [ ] Toolpath visualization looks correct
- [ ] 4-axis rotation range: 0° → 18,355° (~51 revolutions)
- [ ] No collisions detected (if using CAMotics)
- [ ] Tool stays within work envelope
- [ ] Rapids are safe speeds
- [ ] Feed rates are reasonable
- [ ] Spindle/laser power settings correct
- [ ] Air cutting test passed
- [ ] Safety equipment ready (glasses, guards, E-stop)

---

## 🔗 Related Documents

- `BLENDERCAM_4AXIS_VALIDATION.md` - Software validation report
- `HARDWARE_TESTING_WORKFLOW.md` - Complete hardware testing guide
- `HARDWARE_TESTING_SUMMARY.md` - Quick reference
- `ADVANCED_WORKFLOW_INTEGRATION.md` - JupyterLab/Airflow/LangChain roadmap
- `COMPLETE_PROJECT_ROADMAP.md` - Full project timeline

---

**Document Status**: Complete ✅
**Next Action**: Choose simulation tool and verify HELIX G-code
**Safety Note**: Always run air cutting test before material cutting
