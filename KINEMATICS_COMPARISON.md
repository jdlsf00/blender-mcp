# 4-Axis Kinematics: Old vs New Comparison

## The Problem with Original Implementation

### Original "Spiral Wrapping" Approach (INCORRECT)

```python
# OLD CODE - WRONG PHYSICS
def _calculate_position(linear, angle_deg, radius):
    angle_rad = math.radians(angle_deg)
    if rotary_axis == 'X':
        x = linear
        y = radius * math.cos(angle_rad)  # ❌ Tool moves in circle
        z = radius * math.sin(angle_rad)  # ❌ Tool moves in circle
    return (x, y, z)
```

**What this does**: Tool traces a helical path around a stationary cylinder
**Physical impossibility**: Tool would need to teleport or pass through workpiece

### Visualized in CAMotics:

- Tool appears to move in impossible circular paths
- No actual rotation of workpiece visible
- A-axis changes but XYZ doesn't reflect rotated workpiece position
- Cannot be executed on real CNC machine

---

## Correct 4-Axis Kinematics (NEW)

### True Rotary Machining Approach

```python
# NEW CODE - CORRECT PHYSICS
def calculate_tool_position(linear_pos, angle_deg, radial_offset=0.0):
    workpiece_radius = get_workpiece_radius_at_position(linear_pos)
    engagement_radius = workpiece_radius + tool_radius + radial_offset

    if rotary_axis == 'X':
        x = linear_pos           # ✅ Linear position along axis
        y = engagement_radius    # ✅ Fixed tool approach distance
        z = 0.0                  # ✅ Tool at centerline
        a = angle_deg            # ✅ Workpiece rotates
    return (x, y, z, a)
```

**What this does**: Tool stays at fixed distance from axis, workpiece rotates
**Physical reality**: Matches how real 4-axis CNCs work

### Visualized in CAMotics:

- Tool approaches from consistent direction (e.g., from +Y)
- Workpiece rotates under the tool (A-axis changes)
- Tool may move along X (length) and slightly in Y (for different diameters)
- Can be executed on real CNC machine

---

## Key Differences

| Aspect                  | OLD (Spiral)                  | NEW (True 4-Axis)                  |
| ----------------------- | ----------------------------- | ---------------------------------- |
| **Tool Motion**         | Circular path around cylinder | Linear/fixed radial position       |
| **Workpiece**           | Stationary                    | Rotates (A-axis)                   |
| **Y Position**          | Varies continuously in circle | Fixed or changes only for contours |
| **Z Position**          | Varies continuously in circle | At centerline (0) or fixed offset  |
| **Physically Possible** | ❌ No                         | ✅ Yes                             |
| **CAMotics Simulation** | Looks wrong                   | Looks correct                      |
| **Real Machine**        | Would crash                   | Would work                         |

---

## Test Files Comparison

### File Set 1: Original (Incorrect Kinematics)

- `test1_standard_helix.gcode` - 32.5 KB
- `test2_large_helix.gcode` - 29.9 KB
- `test3_indexed.gcode` - 10.6 KB

**Sample G-code (incorrect)**:

```gcode
G1 X0.1389 Y27.5746 Z4.8621 A10.0000
G1 X0.2778 Y26.3114 Z9.5766 A20.0000
G1 X0.4167 Y24.2487 Z14.0000 A30.0000
```

**Problem**: Y and Z trace circular path while A increments

- Y goes: 27.57 → 26.31 → 24.25 (following cos curve)
- Z goes: 4.86 → 9.58 → 14.00 (following sin curve)
- This is mathematically a spiral, physically impossible

### File Set 2: Corrected (Proper Kinematics)

- `true_4axis_surface.gcode` - 18.6 KB (half rotation)
- `true_4axis_contoured.gcode` - 102.6 KB (barrel shape)
- `true_4axis_wavy.gcode` - 123.8 KB (sinusoidal)

**Sample G-code (correct)**:

```gcode
G1 X0.0000 Y28.0000 Z0.0000 A0.0000
G1 X0.0000 Y28.0000 Z0.0000 A10.0000
G1 X0.0000 Y28.0000 Z0.0000 A20.0000
```

**Correct behavior**: Y and Z stay constant, only A changes

- Y stays: 28.00mm (tool engagement radius)
- Z stays: 0.00mm (centerline)
- X advances: Along cylinder length
- A rotates: Workpiece turns under tool

---

## Advanced Features in New Implementation

### 1. Contoured Surfaces (Variable Diameter)

```python
# Barrel shape: narrow → wide → narrow
contour_points = [
    (0, 15),      # 30mm diameter at start
    (25, 20),     # 40mm diameter
    (50, 25),     # 50mm diameter at center (widest)
    (75, 20),     # 40mm diameter
    (100, 15),    # 30mm diameter at end
]
```

**File**: `true_4axis_contoured.gcode`
**Tool behavior**: Y-axis adjusts to follow contour

- At narrow sections: Y = smaller radius + tool_radius
- At wide sections: Y = larger radius + tool_radius
- Demonstrates surface-following capability

### 2. Sinusoidal Surfaces (Wavy)

```python
# 2 complete sine waves over 100mm length
radius = base_radius + amplitude * sin(frequency * position)
```

**File**: `true_4axis_wavy.gcode`
**Tool behavior**: Y-axis follows smooth wave

- Tool tracks sinusoidal variation in diameter
- Demonstrates complex surface machining
- Shows precision of kinematic calculations

---

## How to Verify in CAMotics

### Load Original File (Wrong):

1. Open CAMotics
2. Load `test_output/test1_standard_helix.gcode`
3. **Observe**:
   - Tool traces impossible spiral path
   - Tool appears to move through space in ways no physical tool could
   - A-axis changes seem disconnected from tool motion

### Load Corrected File (Right):

1. Open CAMotics
2. Load `test_output/true_4axis_surface.gcode`
3. **Observe**:
   - Tool approaches from consistent direction (top, +Y)
   - Tool stays at fixed distance from axis
   - Workpiece appears to rotate under tool
   - Physically realistic motion

### Load Complex Surface (Advanced):

1. Open CAMotics
2. Load `test_output/true_4axis_contoured.gcode`
3. **Observe**:
   - Tool tracks varying diameter
   - Y-axis adjusts smoothly as diameter changes
   - Creates barrel-shaped workpiece
   - Still physically realistic

---

## Mathematical Explanation

### Why the Old Way Was Wrong

In the old implementation:

```
For angle θ at position x:
  Y = R × cos(θ)
  Z = R × sin(θ)
  A = θ
```

This assumes **the tool moves in a circular path** while simultaneously **commanding A-axis rotation**. The CNC controller would:

1. Try to move tool to Y,Z coordinates (circular path)
2. Try to rotate workpiece to angle A

**Result**: Tool collision with workpiece at most angles, or impossible positioning

### Why the New Way Is Correct

In the new implementation:

```
For angle θ at position x:
  Y = R_engagement (constant or varying with contour)
  Z = 0 (centerline)
  A = θ (workpiece rotation)
```

This assumes **the tool stays in a fixed position** while **workpiece rotates**. The CNC controller:

1. Positions tool at fixed Y,Z (approach position)
2. Rotates workpiece to angle A
3. Tool engages rotating workpiece surface

**Result**: Physically correct machining operation

---

## Real-World 4-Axis Machining Explained

### How It Actually Works

1. **Workpiece Setup**:

   - Cylinder mounted between centers or in chuck
   - Rotates around one axis (A-axis)

2. **Tool Position**:

   - Approaches from fixed direction (usually from above or side)
   - Maintains constant distance from rotation axis
   - May move along rotation axis (X, Y, or Z depending on setup)

3. **Machining Action**:

   - Workpiece rotates slowly (A-axis)
   - Tool may advance along length simultaneously
   - Creates helical, spiral, or indexed patterns

4. **For Contoured Surfaces**:
   - Tool-to-axis distance varies with local diameter
   - Controller adjusts Y (or X/Z) based on workpiece profile
   - A-axis rotation synchronized with linear motion

---

## Configuration Parameters

### Original Generator (standalone_4axis_gcode.py)

```bash
python standalone_4axis_gcode.py \
  --diameter 50 \          # Cylinder diameter
  --length 100 \           # Cylinder length
  --strategy HELIX         # Creates spiral pattern (wrong kinematics)
```

### New Generator (true_4axis_generator.py)

```bash
python true_4axis_generator.py \
  --diameter 50 \          # Cylinder diameter
  --length 100 \           # Cylinder length
  --strategy SURFACE \     # Surface machining (correct kinematics)
  --start-angle 0 \        # Start at 0°
  --end-angle 180          # Machine half rotation (or 360 for full)
```

### Complex Surfaces (generate_complex_surfaces.py)

```bash
python generate_complex_surfaces.py
```

Generates both:

- Barrel-shaped contour (5 control points)
- Sinusoidal wave (21 control points, 2 complete waves)

---

## Summary

### The Fix

**Before**: Tool moved in impossible circular paths while commanding rotation
**After**: Tool maintains realistic position while workpiece rotates

### Benefits of New Implementation

1. ✅ **Physically Correct**: Can run on real CNC machines
2. ✅ **CAMotics Accurate**: Simulations look realistic
3. ✅ **Contour Support**: Handles variable diameter workpieces
4. ✅ **Surface Following**: Tool adjusts to complex shapes
5. ✅ **Educational**: Shows true 4-axis kinematics principles

### Files to Test

**Simple cylinder** (half rotation):

- `test_output/true_4axis_surface.gcode`

**Complex surfaces**:

- `test_output/true_4axis_contoured.gcode` (barrel)
- `test_output/true_4axis_wavy.gcode` (sinusoidal)

### Recommendation

**Use `true_4axis_generator.py` for all future 4-axis work**. The original `standalone_4axis_gcode.py` produces mathematically interesting but physically impossible toolpaths.

---

_For questions about 4-axis kinematics, refer to CNC machining textbooks on rotary axis programming (G-code A/B/C axes)._
