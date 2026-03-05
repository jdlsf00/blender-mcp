# 4-Axis CNC Simulators - CAMotics Alternatives

## Problem with CAMotics

❌ **CAMotics only supports 3-axis (XYZ) visualization**

- No A-axis (rotary) support
- Cannot show true 4-axis kinematics
- Requires "unwrapping" which defeats the purpose

---

## ✅ Recommended 4-Axis Simulators

### 1. **NC Viewer** (Best - Free Web-Based)

**URL**: https://ncviewer.com/

**Features**:

- ✅ Free web-based (no installation)
- ✅ Supports A, B, C rotary axes
- ✅ Real-time 3D visualization
- ✅ Works with GRBL, LinuxCNC, Fanuc G-code
- ✅ Shows actual rotation animation
- ✅ Can export STL of result

**How to Use**:

1. Go to https://ncviewer.com/
2. Click "Choose File" or drag & drop your .gcode file
3. Select the "Plot" tab
4. Enable "Show Tool" and "Show Machine"
5. Click Play to see animation

**Files to Try**:

- `test_output/true_4axis_surface.gcode`
- `test_output/true_4axis_contoured.gcode`
- `test_output/true_4axis_wavy.gcode`

---

### 2. **G-Code Ripper** (Free, Windows)

**URL**: https://github.com/vlachoudis/bCNC

**Features**:

- ✅ Free and open source
- ✅ Supports 4-axis (A-axis)
- ✅ Real-time visualization
- ✅ Works with GRBL
- ✅ Python-based

**Installation**:

```powershell
pip install bCNC
bcnc
```

---

### 3. **CNCSimulator Pro** (Commercial - Free Trial)

**URL**: https://cncsimulator.info/

**Features**:

- ✅ Full 4-axis support (A, B, C axes)
- ✅ Realistic machine simulation
- ✅ Collision detection
- ✅ Multiple controller support
- ✅ Training mode

**Price**: ~$200 (Free trial available)

---

### 4. **Vericut** (Professional - Expensive)

**URL**: https://www.cgtech.com/

**Features**:

- ✅ Industry-standard 4/5-axis simulator
- ✅ Full rotary axis support
- ✅ Machine collision detection
- ✅ Optimized toolpath verification
- ✅ Used by aerospace/automotive

**Price**: Enterprise pricing (very expensive)
**Note**: Overkill for hobby use

---

### 5. **CutViewer** (Mid-Range Commercial)

**URL**: https://cutviewer.com/

**Features**:

- ✅ 4-axis rotary support
- ✅ Real machine kinematics
- ✅ G-code verification
- ✅ Measuring tools

**Price**: ~$300-500

---

### 6. **LinuxCNC + Axis GUI** (Free, Linux/Virtual)

**URL**: http://linuxcnc.org/

**Features**:

- ✅ Free and open source
- ✅ Full 4-axis support
- ✅ Real CNC controller simulation
- ✅ Can actually run real machines

**Setup**:

- Run in VirtualBox or WSL2
- Best for testing G-code before real machining

---

## 🎯 **RECOMMENDED: Use NC Viewer**

### Why NC Viewer is Best for Your Case:

1. **No Installation** - Web-based, works immediately
2. **Free** - No cost, no trial limits
3. **True 4-Axis** - Shows A-axis rotation correctly
4. **Easy to Use** - Drag and drop interface
5. **Cross-Platform** - Works on any OS with browser

### Quick Start with NC Viewer:

```powershell
# Open NC Viewer
start https://ncviewer.com/

# Your files are ready at:
# F:\Documents\CODE\Blender-MCP\test_output\
# - true_4axis_surface.gcode (simple)
# - true_4axis_contoured.gcode (barrel)
# - true_4axis_wavy.gcode (sinusoidal)
```

---

## Testing Your Files

### In NC Viewer:

1. Go to https://ncviewer.com/
2. Upload `true_4axis_surface.gcode`
3. You should see:
   - Tool at Y=28mm (fixed position)
   - Cylinder rotating 0° to 180°
   - Tool advancing along X-axis
   - Proper 4-axis kinematics

### What to Look For:

✅ Tool maintains constant distance from rotation axis
✅ Workpiece appears to rotate under tool
✅ No impossible motions or collisions
✅ Smooth surface following (contoured files)

---

## Alternative: Python-Based Viewer

If you want a local solution, I can create a Python viewer using:

- **Matplotlib** for 3D visualization
- **VPython** for interactive simulation
- **PyQt + OpenGL** for real-time rendering

Would you like me to create a custom 4-axis viewer?

---

## Comparison Table

| Simulator        | Cost | Installation | 4-Axis Support  | Ease of Use | Recommended    |
| ---------------- | ---- | ------------ | --------------- | ----------- | -------------- |
| **NC Viewer**    | Free | None (web)   | ✅ Full         | ⭐⭐⭐⭐⭐  | ✅ **YES**     |
| CAMotics         | Free | Local        | ❌ 3-axis only  | ⭐⭐⭐⭐    | ❌ No          |
| G-Code Ripper    | Free | pip install  | ✅ A-axis       | ⭐⭐⭐      | ✅ Good        |
| CNCSimulator Pro | $200 | Local        | ✅ Full         | ⭐⭐⭐⭐    | 💰 If budget   |
| Vericut          | $$$$ | Enterprise   | ✅ Professional | ⭐⭐⭐      | 💰 Pro only    |
| LinuxCNC         | Free | VM/Linux     | ✅ Full         | ⭐⭐        | 🐧 Linux users |

---

## Next Steps

### Immediate Action:

1. **Open NC Viewer**: https://ncviewer.com/
2. **Upload**: `test_output/true_4axis_surface.gcode`
3. **Verify**: Correct 4-axis kinematics visible

### If NC Viewer Works:

- Test all three files (surface, contoured, wavy)
- Take screenshots for documentation
- Proceed to hardware testing

### If You Need Local Solution:

Let me know and I'll create:

- Python-based 4-axis visualizer
- Uses matplotlib or VPython
- Shows tool path with rotation animation
- Can save as video or images

---

## Installation Commands

### If you want G-Code Ripper (bCNC):

```powershell
# Install bCNC
pip install bCNC

# Run
python -m bCNC
```

### If you want to try LinuxCNC (WSL2):

```powershell
# Enable WSL2
wsl --install

# Install LinuxCNC
wsl
sudo apt update
sudo apt install linuxcnc
```

---

## Summary

**Best Option**: Use **NC Viewer** (https://ncviewer.com/)

- No installation
- True 4-axis support
- Free
- Works immediately

**Your files are ready in**: `F:\Documents\CODE\Blender-MCP\test_output\`

Upload them to NC Viewer and you'll see the proper 4-axis kinematics! 🎯
