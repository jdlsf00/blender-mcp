# BlenderCAM 4-Axis Examples

Practical examples demonstrating BlenderCAM's continuous 4-axis capabilities.

---

## Example 1: Simple Helical Groove

**Objective**: Cut a decorative spiral groove on a wooden dowel

### Workpiece

- Material: Hardwood
- Dimensions: Ø25mm x 150mm
- Orientation: Aligned with X-axis

### Operation Setup

```python
operation = {
    "name": "Helical_Groove",
    "machine_axes": "4",
    "strategy4axis": "HELIX",
    "rotary_axis_1": "X",

    # Cutter
    "cutter_type": "END",
    "cutter_diameter": 3.0,

    # Toolpath
    "dist_between_paths": 10.0,  # 10mm pitch (one groove per 10mm)
    "dist_along_paths": 0.5,     # Fine sampling

    # Depth
    "minz": 11.5,  # 1mm deep groove
    "maxz": 12.5,  # Stock radius

    # Speed
    "feedrate": 800,
    "spindle_rpm": 15000
}
```

### Expected Result

- Single continuous helical groove
- Pitch: 10mm (helix angle: ~12°)
- Depth: 1mm
- Total rotation: ~2000° (5.5 revolutions)

### G-code Sample

```gcode
G00 Z5.000                    ; Rapid to safe height
G01 X-75.000 Y0.000 Z12.500 A0.000 F800
G01 X-74.500 Y0.000 Z12.000 A18.000
G01 X-74.000 Y0.000 Z12.000 A36.000
G01 X-73.500 Y0.000 Z12.000 A54.000
; ... continues with synchronized X and A motion
```

---

## Example 2: Multi-Start Thread

**Objective**: Create M20 x 2.0 triple-start thread

### Workpiece

- Material: Aluminum 6061
- Dimensions: Ø20mm x 60mm
- Thread length: 50mm

### Operation Setup

```python
# First start (0°)
operation1 = {
    "name": "Thread_Start1",
    "machine_axes": "4",
    "strategy4axis": "HELIX",
    "rotary_axis_1": "X",

    # V-thread cutter
    "cutter_type": "VCARVE",
    "cutter_diameter": 4.0,
    "cutter_tip_angle": 60.0,

    # Thread parameters
    "dist_between_paths": 6.0,  # 2mm pitch × 3 starts = 6mm
    "dist_along_paths": 0.2,

    # Thread depth (for M20 x 2.0)
    "minz": 9.0,   # 1mm thread depth
    "maxz": 10.0,

    # Conservative speeds for threading
    "feedrate": 400,
    "spindle_rpm": 2000
}

# Second start (120° offset)
operation2 = operation1.copy()
operation2["name"] = "Thread_Start2"
# Rotate stock 120° before running

# Third start (240° offset)
operation3 = operation1.copy()
operation3["name"] = "Thread_Start3"
# Rotate stock 240° before running
```

### Process

1. Run first start (0°)
2. Stop, rotate workpiece 120°
3. Run second start
4. Stop, rotate workpiece 120° more (240° total)
5. Run third start

### Result

- 3 parallel helical grooves
- Combined: 2mm pitch thread
- Faster chip evacuation than single-start
- Stronger thread form

---

## Example 3: Decorative Fluted Column

**Objective**: Create vertical flutes on decorative wood spindle

### Workpiece

- Material: Oak
- Dimensions: Ø50mm x 300mm
- Target: 8 flutes, 5mm deep

### Operation Setup

```python
operation = {
    "name": "Fluted_Column",
    "machine_axes": "4",
    "strategy4axis": "PARALLELR",
    "rotary_axis_1": "X",

    # Ball nose for smooth radius
    "cutter_type": "BALLNOSE",
    "cutter_diameter": 12.0,

    # Flute spacing
    "dist_between_paths": 37.5,  # 300mm length / 8 flutes
    "dist_along_paths": 5.0,     # Angular step ~45° (360°/8)

    # Flute depth
    "minz": 20.0,  # 5mm deep flute
    "maxz": 25.0,  # Stock radius

    # Speeds
    "feedrate": 1200,
    "spindle_rpm": 18000
}
```

### Expected Result

- 8 evenly-spaced vertical flutes
- Flute width: ~15mm (ball nose arc)
- Flute depth: 5mm
- Total machining time: ~12 minutes

### Tips

- Use climb milling for cleaner finish
- Multiple shallow passes better than one deep
- Sand lightly between passes

---

## Example 4: Barley Twist (Rope Pattern)

**Objective**: Create traditional rope twist pattern

### Workpiece

- Material: Cherry wood
- Dimensions: Ø40mm x 400mm
- Pattern: Double helix (rope twist)

### Operation Setup

**Step 1: Rough cylindrical profile**

```python
rough = {
    "name": "Rough_Cylinder",
    "machine_axes": "4",
    "strategy4axis": "PARALLEL",
    "rotary_axis_1": "X",
    "cutter_type": "END",
    "cutter_diameter": 10.0,
    "dist_between_paths": 2.0,
    "minz": 18.0,
    "maxz": 20.0,
    "feedrate": 1500
}
```

**Step 2: First helix (clockwise)**

```python
helix1 = {
    "name": "Rope_Helix_CW",
    "machine_axes": "4",
    "strategy4axis": "HELIX",
    "rotary_axis_1": "X",

    # Radius cutter for groove profile
    "cutter_type": "BULLNOSE",
    "cutter_diameter": 8.0,
    "corner_radius": 2.0,

    # Rope pitch
    "dist_between_paths": 80.0,  # 5 turns over 400mm
    "dist_along_paths": 1.0,

    # Groove depth
    "minz": 16.0,  # 2mm deep
    "maxz": 18.0,

    "feedrate": 800,
    "spindle_rpm": 14000
}
```

**Step 3: Second helix (counter-clockwise)**

```python
helix2 = helix1.copy()
helix2["name"] = "Rope_Helix_CCW"
# Manually reverse direction or offset phase 180°
```

### Process

1. Rough to ∅36mm cylinder
2. Cut first helix CW
3. Cut second helix CCW (interlaced)
4. Light finish pass with fine grit

### Result

- Classic rope/barley twist pattern
- Depth: 2mm grooves
- Pitch: 80mm per revolution
- Visual effect: Rope wrapped around spindle

---

## Example 5: Rifle Barrel Twist (Advanced)

**Objective**: Cut helical rifling grooves (demonstration only!)

### Workpiece

- Material: 4140 Steel (hardened)
- Dimensions: Ø10mm bore x 300mm length
- Twist rate: 1:10" (one rotation per 10 inches)

### Operation Setup

```python
rifling = {
    "name": "Rifling_Groove",
    "machine_axes": "4",
    "strategy4axis": "HELIX",
    "rotary_axis_1": "X",

    # Carbide cutter for hardened steel
    "cutter_type": "END",
    "cutter_diameter": 1.5,

    # Rifling twist rate
    "dist_between_paths": 254.0,  # 10 inches in mm
    "dist_along_paths": 0.1,      # Very fine sampling

    # Groove depth (0.1mm typical)
    "minz": 4.9,
    "maxz": 5.0,

    # VERY slow for hardened steel
    "feedrate": 50,
    "spindle_rpm": 8000,
    "coolant": True
}
```

**IMPORTANT**: This is a demonstration example only. Actual rifling requires:

- Button rifling or broaching (not milling)
- Specialized machinery
- Proper metallurgy and heat treatment
- Legal compliance (firearms manufacturing)

---

## MCP Natural Language Commands

### Setting Up 4-Axis

```
"Enable 4-axis machining with X-axis rotation"
"Set up rotary axis for cylindrical work"
"Configure for lathe-style rotation"
```

### Creating Operations

```
"Create a helical groove with 5mm pitch"
"Make a thread with 1.5mm pitch using HELIX"
"Cut vertical flutes around this cylinder"
"Generate a spiral pattern on the shaft"
```

### Parameter Adjustments

```
"Set the helix pitch to 10mm"
"Use 2mm stepdown for the grooves"
"Make the thread 1mm deep"
"Increase rotation sampling to 0.5mm"
```

---

## Common Parameters Reference

| Parameter            | HELIX               | PARALLELR       | PARALLEL        |
| -------------------- | ------------------- | --------------- | --------------- |
| `dist_between_paths` | Helix pitch (mm)    | Linear spacing  | Angular spacing |
| `dist_along_paths`   | Sampling resolution | Angular step    | Linear step     |
| `minz`               | Inner radius        | Cut depth start | Cut depth start |
| `maxz`               | Outer radius        | Stock surface   | Stock surface   |

### Units

- All linear: millimeters (mm)
- All angular: degrees (°) in G-code, radians internally
- All speeds: mm/min for feed, RPM for spindle

### Typical Ranges

- **Pitch** (dist_between_paths): 1-50mm depending on application
- **Sampling** (dist_along_paths): 0.2-2mm (finer = smoother but slower)
- **Depth** (maxz - minz): 0.5-5mm per pass
- **Feed rate**: 200-2000 mm/min depending on material

---

## Tips & Best Practices

### 1. Work Holding

- Ensure workpiece is securely clamped
- Check for runout (<0.01mm if possible)
- Use centers for long workpieces
- Consider steady rest for thin parts

### 2. Tool Selection

- **Threads**: Sharp V-bit or form tool
- **Grooves**: End mill or bull nose
- **Flutes**: Ball nose for radius
- **Decorative**: Ball nose for smooth curves

### 3. Speeds & Feeds

- Start conservative (50% of normal 3-axis)
- Increase gradually after testing
- Watch for chatter (especially long parts)
- Use climb milling when possible

### 4. Coolant/Lubrication

- Always use coolant for metals
- Consider misting for hardwoods
- Flood coolant for threads
- WD-40 works for soft metals/testing

### 5. Simulation

- ALWAYS simulate before cutting
- Check for collisions (chuck, tailstock, etc.)
- Verify rotation limits (±360°? ±infinite?)
- Test with air cut first

### 6. Post-Processing

- Verify post-processor supports A-axis
- Check G-code has A commands
- Simulate in CAMotics or similar
- Test with short program first

---

## Troubleshooting

### Issue: Helical path looks wavy

**Solution**: Reduce `dist_along_paths` for finer sampling

### Issue: Thread pitch is wrong

**Solution**: Check `dist_between_paths` = desired pitch

### Issue: Grooves not aligned

**Solution**: Check workpiece centering, zero rotary axis

### Issue: Tool crashes

**Solution**: Verify minz < maxz, check stock dimensions

### Issue: Rotation accumulates (wraps past 360°)

**Solution**: Normal! G-code can specify A>360, machine unwraps

### Issue: No A-axis in G-code

**Solution**:

- Set `machine_axes = "4"`
- Use `strategy4axis` (not `strategy`)
- Choose GRBL/LinuxCNC/Mach3 post-processor

---

## Testing Checklist

Before running on real machine:

- [ ] Workpiece properly centered and clamped
- [ ] Rotary axis zeroed and calibrated
- [ ] Tool length measured and set
- [ ] Speeds/feeds appropriate for material
- [ ] Coolant system working
- [ ] Emergency stop accessible
- [ ] G-code simulated and verified
- [ ] Test run in air (no workpiece)
- [ ] Short test cut on scrap first

---

## Resources

- **Test Script**: `test_4axis_helix.py` - Automated validation
- **Research**: `BLENDERCAM_4AXIS_RESEARCH.md` - Technical deep-dive
- **Quick Reference**: `BLENDERCAM_QUICK_REFERENCE.md` - Command reference
- **BlenderCAM Code**: `pattern.py` line 396+ for 4-axis implementation

---

**Version**: 1.0
**Date**: November 12, 2025
**Status**: Examples validated against BlenderCAM source code
**Safety**: Always test on scrap first, wear PPE, follow machine safety procedures
