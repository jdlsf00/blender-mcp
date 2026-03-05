# 4-Axis G-code Generator - Quick Reference

**Status**: ✅ Production Ready | **Last Updated**: November 14, 2025

---

## 🚀 Quick Start (30 seconds)

```powershell
# Generate G-code for 50mm × 100mm cylinder
python standalone_4axis_gcode.py

# Custom parameters
python standalone_4axis_gcode.py --diameter 80 --length 150 --tool-diameter 10

# Different strategies
python standalone_4axis_gcode.py --strategy INDEXED --index-count 12
python standalone_4axis_gcode.py --strategy SPIRAL
```

---

## 📋 Common Commands

### Standard Cylinder (Most Common)

```powershell
python standalone_4axis_gcode.py `
    --diameter 50 `
    --length 100 `
    --tool-diameter 6 `
    --stepover 5 `
    --strategy HELIX `
    --output my_cylinder.gcode
```

### Large Workpiece

```powershell
python standalone_4axis_gcode.py `
    --diameter 80 `
    --length 150 `
    --tool-diameter 10 `
    --stepover 8 `
    --feed 600 `
    --spindle 10000
```

### Indexed 4-Axis (12 positions)

```powershell
python standalone_4axis_gcode.py `
    --strategy INDEXED `
    --index-count 12 `
    --diameter 50 `
    --length 100
```

### Y-Axis Rotary

```powershell
python standalone_4axis_gcode.py `
    --axis Y `
    --diameter 50 `
    --length 100
```

### LinuxCNC Post-Processor

```powershell
python standalone_4axis_gcode.py `
    --post LINUXCNC `
    --output output.ngc
```

---

## 🔧 Parameters Reference

| Parameter         | Default                | Description            | Example                   |
| ----------------- | ---------------------- | ---------------------- | ------------------------- |
| `--diameter`      | 50                     | Cylinder diameter (mm) | `--diameter 80`           |
| `--length`        | 100                    | Cylinder length (mm)   | `--length 150`            |
| `--tool-diameter` | 6                      | Tool diameter (mm)     | `--tool-diameter 10`      |
| `--stepover`      | 5                      | Stepover distance (mm) | `--stepover 3`            |
| `--strategy`      | HELIX                  | Toolpath strategy      | `--strategy INDEXED`      |
| `--axis`          | X                      | Rotary axis (X/Y/Z)    | `--axis Y`                |
| `--feed`          | 500                    | Feed rate (mm/min)     | `--feed 800`              |
| `--spindle`       | 12000                  | Spindle RPM            | `--spindle 10000`         |
| `--post`          | GRBL                   | Post-processor         | `--post LINUXCNC`         |
| `--output`        | standalone_4axis.gcode | Output file            | `--output my_part.gcode`  |
| `--config`        | -                      | Config JSON file       | `--config my_config.json` |
| `--stats`         | -                      | Show statistics        | `--stats`                 |

---

## 📊 Strategies

### HELIX (Continuous Spiral)

- **Use for**: Smooth surface finish, balanced tool wear
- **Best for**: Decorative patterns, smooth cylinders
- **Command**: `--strategy HELIX`
- **Output**: Continuous helical toolpath
- **Example**: Thread milling, decorative spirals

### INDEXED (Discrete Positions)

- **Use for**: Features at specific angles, faceted surfaces
- **Best for**: Flutes, lobes, indexed features
- **Command**: `--strategy INDEXED --index-count 12`
- **Output**: Cuts at 12 angular positions (30° apart)
- **Example**: 6-flute endmill, hexagonal features

### SPIRAL (Linear Angle Increase)

- **Use for**: Experimental, special effects
- **Best for**: Gradual transitions
- **Command**: `--strategy SPIRAL`
- **Output**: Linear angular progression
- **Example**: Tapered spirals

---

## ✅ Validation Workflow

```powershell
# 1. Generate G-code
python standalone_4axis_gcode.py --output test.gcode

# 2. Validate output
.\validate_gcode.ps1 -GCodePath test.gcode

# 3. Compare with reference (if available)
.\compare_gcode.ps1 -OriginalFile reference.gcode -NewFile test.gcode

# 4. Simulate in CAMotics
# Open CAMotics → Load test.gcode → Run simulation
```

---

## 📁 Using Config Files

### Create config file: `my_project.json`

```json
{
  "geometry": {
    "diameter": 50,
    "length": 100,
    "rotary_axis": "X"
  },
  "tool": {
    "diameter": 6,
    "flutes": 2,
    "material": "carbide"
  },
  "machining": {
    "stepover": 5,
    "feed_rate": 500,
    "plunge_rate": 250,
    "spindle_rpm": 12000
  },
  "strategy": {
    "type": "HELIX",
    "angular_resolution": 10
  },
  "output": {
    "post_processor": "GRBL",
    "filename": "my_part.gcode"
  }
}
```

### Use config:

```powershell
python standalone_4axis_gcode.py --config my_project.json
```

---

## 🎯 Expected Output

### For 50mm × 100mm Cylinder (Default):

- **Points**: ~777
- **File Size**: ~32 KB
- **Passes**: 21
- **Total Rotation**: 7560°
- **X Range**: 0-100mm
- **Y/Z Range**: ±28mm
- **Time**: <1 second

### Validation Checklist:

- ✅ G21 (millimeters) present
- ✅ X range = cylinder length
- ✅ Y/Z range = (diameter/2) + (tool/2)
- ✅ A-axis commands present
- ✅ M3 (spindle on) present
- ✅ Feed rate (G1 F) present

---

## 🐛 Troubleshooting

### "No output file generated"

```powershell
# Check Python installation
python --version

# Check script exists
ls standalone_4axis_gcode.py

# Try with absolute path
python "F:\Documents\CODE\Blender-MCP\standalone_4axis_gcode.py"
```

### "Invalid parameter" error

```powershell
# Use correct strategy names (case-sensitive)
--strategy HELIX      # ✅ Correct
--strategy helix      # ❌ Wrong
--strategy Helix      # ❌ Wrong

# Check parameter names (use hyphens)
--tool-diameter 6     # ✅ Correct
--tool_diameter 6     # ❌ Wrong
--tooldiameter 6      # ❌ Wrong
```

### Coordinates too large/small

```powershell
# Verify diameter/length in millimeters
--diameter 50         # ✅ 50mm (correct)
--diameter 0.05       # ❌ 0.05mm (too small)
--diameter 50000      # ❌ 50 meters (too large)
```

---

## 📚 Additional Resources

- **Full Documentation**: `README_4AXIS_SUITE.md`
- **Test Results**: `TEST_RESULTS.md`
- **FabEX Bug Info**: `FABEX_4AXIS_BUG_WORKAROUND.md`
- **Machine Presets**: `LOADING_MACHINE_PRESETS.md`
- **Validation Scripts**: `validate_gcode.ps1`, `compare_gcode.ps1`

---

## 🔄 Comparison: Three Generators

| Feature           | Standalone | FreeCAD        | Blender       |
| ----------------- | ---------- | -------------- | ------------- |
| **Speed**         | <1s ⚡     | ~15s           | ~7s           |
| **Dependencies**  | None       | FreeCAD        | Blender       |
| **GUI**           | CLI only   | FreeCAD GUI    | Blender GUI   |
| **Visualization** | No         | Yes            | Yes           |
| **Portability**   | High       | Medium         | Medium        |
| **Best For**      | Automation | Production CAM | Visual design |

---

## 🎬 Example Workflows

### Quick Test

```powershell
# Generate and validate in one command
python standalone_4axis_gcode.py --stats; .\validate_gcode.ps1 -GCodePath standalone_4axis.gcode
```

### Batch Processing

```powershell
# Generate multiple configurations
@(50, 60, 70, 80) | ForEach-Object {
    python standalone_4axis_gcode.py --diameter $_ --output "cylinder_${_}mm.gcode"
}
```

### Production Workflow

```powershell
# 1. Generate with config
python standalone_4axis_gcode.py --config production.json

# 2. Validate
.\validate_gcode.ps1 -GCodePath production_part.gcode

# 3. Simulate in CAMotics
# (Manual step - load in CAMotics)

# 4. Transfer to CNC
Copy-Item production_part.gcode -Destination "\\CNC-MACHINE\gcode\"
```

---

## 💡 Pro Tips

1. **Start with defaults** - They work well for most cases
2. **Use --stats flag** - Shows helpful information during generation
3. **Always validate** - Run validate_gcode.ps1 before machining
4. **Test in simulator** - Use CAMotics or NC Viewer first
5. **Save configs** - Create JSON files for repeatable jobs
6. **Check A-axis range** - Ensure your machine can handle total rotation
7. **Verify units** - Always check G21 (mm) vs G20 (inches)
8. **Safe Z height** - Default 50mm works for most setups

---

## 📞 Support

- **Issues**: Check TEST_RESULTS.md for known issues
- **Questions**: Refer to README_4AXIS_SUITE.md
- **Bugs**: Document unexpected behavior with examples

---

_Last tested: November 14, 2025 | All systems operational ✅_
