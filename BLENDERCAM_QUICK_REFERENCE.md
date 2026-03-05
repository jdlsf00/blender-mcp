# 🎯 BlenderCAM MCP Quick Reference

**GitHub Copilot Integration** - Just say what you want!

---

## 💬 Natural Language Examples

### Basic Operations

```
"Create a pocket toolpath with 6mm flat endmill"
"Generate parallel finishing with 3mm ball nose"
"Drill these holes with 4mm drill bit"
"Cut out this profile with 3mm endmill"
```

### Advanced Operations

```
"Rough with 10mm, then finish with 6mm ball nose"
"Create spiral toolpath for smooth motion"
"Generate waterline passes for this 3D shape"
"Make a V-carve engraving with 60-degree bit"
```

### Export Commands

```
"Export G-code for Grbl controller"
"Generate Fanuc-compatible code"
"Save as ISO standard G-code"
"Create output for my Haas machine"
```

---

## 🔧 MCP Tools Reference

### 1. `setup_blendercam`

**Purpose**: Enable BlenderCAM addon
**When**: First time use, after Blender restart
**Parameters**: None required

```json
{
  "name": "setup_blendercam",
  "arguments": {}
}
```

### 2. `create_cam_operation`

**Purpose**: Configure CNC operation
**When**: Before calculating toolpath
**Key Parameters**:

| Parameter         | Type   | Default    | Description                |
| ----------------- | ------ | ---------- | -------------------------- |
| `object_name`     | string | required   | Target object              |
| `operation_name`  | string | required   | Operation identifier       |
| `operation_type`  | string | "PARALLEL" | See strategies below       |
| `cutter_type`     | string | "BALLNOSE" | See cutters below          |
| `cutter_diameter` | number | 6.0        | Tool diameter (mm)         |
| `feedrate`        | number | 1000       | Feed rate (mm/min)         |
| `spindle_rpm`     | number | 12000      | Spindle speed              |
| `stepdown`        | number | 1.0        | Z step per pass (mm)       |
| `stepover`        | number | 0.5        | XY stepover (0-1 or 0-100) |

```json
{
  "name": "create_cam_operation",
  "arguments": {
    "object_name": "Part",
    "operation_name": "Roughing",
    "operation_type": "POCKET",
    "cutter_type": "FLAT",
    "cutter_diameter": 6.0,
    "feedrate": 1200,
    "spindle_rpm": 12000,
    "stepdown": 1.5,
    "stepover": 50
  }
}
```

### 3. `calculate_cam_paths`

**Purpose**: Generate toolpath
**When**: After creating operation
**Parameters**:

```json
{
  "name": "calculate_cam_paths",
  "arguments": {
    "operation_name": "Roughing"
  }
}
```

### 4. `export_cam_gcode`

**Purpose**: Export G-code
**When**: After calculating toolpath
**Parameters**:

```json
{
  "name": "export_cam_gcode",
  "arguments": {
    "operation_name": "Roughing",
    "post_processor": "GRBL",
    "filename": "part_rough"
  }
}
```

### 5. `simulate_cam_operation`

**Purpose**: Visual verification
**When**: Before export (optional safety check)
**Parameters**:

```json
{
  "name": "simulate_cam_operation",
  "arguments": {
    "operation_name": "Roughing"
  }
}
```

---

## 📋 Operation Types (Strategies)

| Strategy      | Best For              | Description                |
| ------------- | --------------------- | -------------------------- |
| `PARALLEL`    | Finishing             | Zigzag along axis          |
| `CROSS`       | Cross-grain finishing | Perpendicular passes       |
| `BLOCK`       | Roughing              | Efficient material removal |
| `SPIRAL`      | Smooth motion         | Continuous spiral          |
| `WATERLINE`   | 3D shapes             | Follow Z contours          |
| `POCKET`      | Enclosed areas        | Pocket clearing            |
| `DRILL`       | Holes                 | Drilling operations        |
| `CUTOUT`      | Profiles              | Part separation            |
| `MEDIAL_AXIS` | Complex pockets       | Advanced strategy          |

---

## 🔨 Cutter Types

| Type       | Description    | Best For                     |
| ---------- | -------------- | ---------------------------- |
| `BALLNOSE` | Spherical tip  | 3D contouring, smooth finish |
| `FLAT`     | Flat endmill   | Pockets, facing, slots       |
| `VCARVE`   | V-shaped       | Engraving, chamfering        |
| `BULLNOSE` | Rounded corner | Rounded features             |
| `BALLCONE` | Combined shape | Hybrid operations            |

---

## 🏭 Post-Processors

### Hobby/DIY

- `GRBL` - Most hobby CNC (3018, 3040, etc.)
- `MACH3` - Mach3 software
- `SMOOTHIE` - Smoothie boards

### Industrial

- `FANUC` - Fanuc controllers
- `HAAS` - Haas machines
- `HEIDENHAIN` - TNC controllers
- `ISO` - International standard

### Open-Source

- `LINUXCNC` - LinuxCNC/EMC2
- `SHOPBOT` - ShopBot routers

### Others

- `FADAL` - Fadal VMCs
- `CENTROID` - Centroid controls
- `MAZAK` - Mazak machines
- Plus 30+ more!

---

## 🎓 Common Workflows

### Workflow 1: Simple Pocket

```
1. "Create pocket toolpath with 6mm flat endmill"
   → create_cam_operation(operation_type="POCKET", cutter_type="FLAT", cutter_diameter=6.0)
   → calculate_cam_paths()

2. "Export for Grbl"
   → export_cam_gcode(post_processor="GRBL")
```

### Workflow 2: Rough + Finish

```
1. "Rough with 10mm flat mill"
   → create_cam_operation(name="Rough", cutter_diameter=10.0, operation_type="BLOCK")
   → calculate_cam_paths(operation_name="Rough")

2. "Finish with 6mm ball nose"
   → create_cam_operation(name="Finish", cutter_diameter=6.0, cutter_type="BALLNOSE", operation_type="PARALLEL")
   → calculate_cam_paths(operation_name="Finish")

3. "Export both"
   → export_cam_gcode(operation_name="Rough", filename="rough")
   → export_cam_gcode(operation_name="Finish", filename="finish")
```

### Workflow 3: 3D Contour

```
1. "Create waterline passes for 3D shape with 3mm ball"
   → create_cam_operation(operation_type="WATERLINE", cutter_type="BALLNOSE", cutter_diameter=3.0)
   → calculate_cam_paths()

2. "Export as ISO standard"
   → export_cam_gcode(post_processor="ISO")
```

---

## ⚙️ Parameter Guidelines

### Feedrate Selection

| Material | Soft (Wood) | Medium (Plastic) | Hard (Aluminum) |
| -------- | ----------- | ---------------- | --------------- |
| 6mm flat | 1500-2000   | 1000-1500        | 500-800         |
| 3mm ball | 1000-1500   | 800-1200         | 400-600         |

### Stepdown Rules

- **Roughing**: 50-80% of tool diameter
- **Finishing**: 20-40% of tool diameter
- **Drilling**: 1-2x tool diameter per peck

### Stepover Recommendations

- **Roughing**: 40-60% (0.4-0.6)
- **Finishing**: 5-15% (0.05-0.15)
- **3D Contour**: 10-20% (0.1-0.2)

### Spindle Speed

- **Wood**: 12000-18000 RPM
- **Plastic**: 10000-15000 RPM
- **Aluminum**: 8000-12000 RPM
- **Steel**: 3000-6000 RPM

---

## 🐛 Troubleshooting

### "Object not found"

→ Ensure object name matches exactly
→ Import STL first: `import_stl(filepath="...", name="Part")`

### "Operation not found"

→ Create operation first: `create_cam_operation(...)`
→ Check operation_name matches

### "Toolpath not calculated"

→ Run `calculate_cam_paths()` before export
→ Check for errors in calculation step

### "BlenderCAM not available"

→ Run `setup_blendercam()` first
→ Verify addon path: `F:\Documents\Blender\blendercam-master\scripts\addons`

### "G-code export failed"

→ Verify post-processor name is valid
→ Check file path permissions

---

## 📊 Performance Tips

### For Large Operations

1. Use `BLOCK` strategy for roughing (faster)
2. Reduce stepover for faster calculation
3. Increase stepdown within safe limits
4. Consider splitting into multiple operations

### For Quality

1. Use `PARALLEL` or `WATERLINE` for finishing
2. Reduce stepover (10-15%)
3. Use appropriate cutter type (BALLNOSE for 3D)
4. Simulate before cutting

---

## 🎯 Quick Start Checklist

- [ ] Run `setup_blendercam()` once
- [ ] Create or import 3D object
- [ ] Create CAM operation with desired parameters
- [ ] Calculate toolpath
- [ ] (Optional) Simulate for verification
- [ ] Export G-code with correct post-processor
- [ ] Verify output file created
- [ ] Load into CNC controller

---

## 🚀 Pro Tips

1. **Start conservative**: Use lower feedrates and test first
2. **Simulate first**: Always verify toolpath before cutting
3. **Multi-stage**: Rough, then finish for best results
4. **Tool changes**: Create separate operations for different tools
5. **Naming**: Use clear operation names ("Rough_10mm", "Finish_3mm")
6. **Post-processors**: Match your actual CNC controller exactly
7. **Units**: All parameters in mm (converted internally to meters)
8. **Stepover**: Can use percentage (50) or decimal (0.5)

---

## 🔄 4-Axis / Rotary Operations

### Understanding 4-Axis in BlenderCAM

BlenderCAM supports **TRUE continuous 4-axis** machining! The workpiece rotates around an axis (typically X) while the cutter moves linearly, enabling cylindrical and rotary operations.

### 4-Axis Strategies

#### 🌀 HELIX (Continuous Spiral)

**Best for**: Threads, helical grooves, decorative spirals

```
"Create a helical groove on this cylinder with 2mm pitch"
"Make threads with 1.5mm pitch on the shaft"
```

**How it works**: True simultaneous rotation + linear motion. The cutter spirals around the cylinder like a barber pole.

**Parameters**:

- `dist_between_paths`: Helix pitch (mm) - distance per revolution
- `dist_along_paths`: Sampling resolution along the path
- `minz`: Inner radius (depth of cut)
- `maxz`: Outer radius (stock surface)

**Sample G-code**:

```gcode
G01 X10.000 Y0.000 Z22.500 A45.000 F1000
G01 X10.500 Y0.000 Z22.500 A90.000 F1000
G01 X11.000 Y0.000 Z22.500 A135.000 F1000
```

Notice the A-axis (rotation) continuously increases while X moves!

#### ⚡ PARALLELR (Parallel with Rotation)

**Best for**: Fluting, longitudinal grooves, decorative patterns

```
"Create parallel flutes along the cylinder"
"Make vertical grooves on this shaft"
```

**How it works**: Makes a pass along the length, rotates, makes another pass. Multiple "slices" around the circumference.

#### 📡 PARALLEL (Rotary Scanning)

**Best for**: Turning operations, cylindrical profiling

```
"Profile this cylinder shape on the lathe"
```

**How it works**: Scans linearly at fixed rotation angle, then increments rotation for next pass.

#### ✖️ CROSS (Crosshatch Pattern)

**Best for**: Surface finishing, decorative crosshatch

```
"Create a crosshatch finish on this cylinder"
```

### Setting Up 4-Axis Operations

```
"Create a 4-axis HELIX operation on this cylinder"
"Set up rotary axis machining with 2mm pitch"
"Make a helical thread with X-axis rotation"
```

**Key Parameters**:

- `machine_axes`: "4"
- `strategy4axis`: "HELIX", "PARALLELR", "PARALLEL", or "CROSS"
- `rotary_axis_1`: "X", "Y", or "Z" (axis of rotation)
- `dist_between_paths`: Spacing/pitch (mm)
- `minz`/`maxz`: Radial depth range

### Real-World Examples

**Threaded Bolt**: HELIX with 1.5mm pitch, Ø3mm V-bit
**Decorative Spindle**: PARALLELR with 10mm spacing, Ø6mm ball nose
**Helical Groove**: HELIX with 5mm pitch, Ø4mm end mill

### Troubleshooting 4-Axis

**No A-axis in G-code?**

- Check post-processor supports rotary (GRBL, LinuxCNC, Mach3)
- Verify `machine_axes = '4'`
- Use `strategy4axis` (not `strategy`)

**Toolpath looks wrong?**

- Cylinder must align with rotary_axis_1
- Check minz < maxz (radius values)
- Verify dist_between_paths is reasonable

---

**Need Help?**

- 📖 Full documentation: `BLENDERCAM_INTEGRATION_PLAN.md`
- 🧪 Test examples: `test_blendercam_integration.py`
- 🎉 Success story: `BLENDERCAM_SUCCESS.md`
- 🔬 4-Axis research: `BLENDERCAM_4AXIS_RESEARCH.md`
- 🧪 4-Axis test: `test_4axis_helix.py`
- 🔧 BlenderCAM GitHub: https://github.com/vilemduha/blendercam

**Version**: 1.1
**Last Updated**: November 12, 2025
**Status**: ✅ Production Ready (with 4-axis support confirmed!)
