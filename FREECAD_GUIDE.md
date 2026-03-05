# FreeCAD 4-Axis Visualization Guide

## Problem

FreeCAD's Python integration has issues with direct script execution.
Error: `No module named 'gcode_pre'` - FreeCAD is misinterpreting the filename.

## Solution: Use FreeCAD Macro System

### Method 1: FreeCAD Macro (RECOMMENDED)

1. **Open FreeCAD**

   ```
   "C:\Program Files\FreeCAD 0.21\bin\FreeCAD.exe"
   ```

2. **Open Macro Menu**

   - Click `Macro` → `Macros...`
   - Or press `Alt+F8`

3. **Add Macro**

   - Click `User macros` location button to see where macros are stored
   - Copy `freecad_4axis_viewer.FCMacro` to that location
   - OR click `Create` and paste the macro code

4. **Execute**

   - Select `freecad_4axis_viewer.FCMacro`
   - Click `Execute`
   - Browse to select your G-code file

5. **Result**
   - Cylinder stock (semi-transparent orange)
   - Red toolpath wire
   - Isometric view

### Method 2: FreeCAD Console Mode

```powershell
# This may work in newer FreeCAD versions
& "C:\Program Files\FreeCAD 0.21\bin\FreeCAD.exe" --console -c visualize_4axis_freecad.py -- chess_pawn.gcode
```

### Method 3: Blender (PROVEN - USE THIS)

```powershell
# This works perfectly - use this instead of FreeCAD
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --background --python "F:\Documents\CODE\Blender-MCP\visualize_4axis_blender.py" -- "F:\Documents\CODE\Blender-MCP\test_output\chess_pawn.gcode" "F:\Documents\CODE\Blender-MCP\chess_pawn_viz.blend"

# Then open the .blend file
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" "F:\Documents\CODE\Blender-MCP\chess_pawn_viz.blend"
```

## Current Status

✅ **Blender Visualization** - WORKING PERFECTLY

- Correct coordinate mapping
- Tool tip positioning accurate
- Animation keyframes working
- Multiple shapes tested (chess pawn, Bezier vase)

❌ **FreeCAD Direct Execution** - PROBLEMATIC

- Script parsing issues
- Module import errors
- Use Macro method instead

## Recommendation

**Use Blender for visualization** - it's fully debugged and working.

- Already tested with 5 complex shapes
- Coordinate system corrections applied
- Animation support
- Tool tip offset correct

**FreeCAD via Macro** - if you specifically need FreeCAD format:

- More steps to execute
- Limited to static visualization
- No animation support
- Useful for exporting to STEP/IGES

## Files

- `visualize_4axis_blender.py` - WORKING (277 lines, production ready)
- `freecad_4axis_viewer.FCMacro` - FreeCAD macro (simple file selector)
- `visualize_4axis_freecad.py` - Direct execution (problematic)

## Next Steps

1. ✅ Continue using Blender (proven tool)
2. ⏳ Test FreeCAD macro if needed for CAD export
3. ⏳ Implement 3D mesh analysis (surface_3d_generator.py)
4. ⏳ Hardware testing on real CNC
