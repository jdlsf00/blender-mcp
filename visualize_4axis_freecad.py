#!/usr/bin/env python3
"""
FreeCAD 4-Axis G-code Visualizer

Opens G-code in FreeCAD for visualization
Run with: FreeCAD --console visualize_4axis_freecad.py <gcode_file>
"""

import sys
import os

try:
    import FreeCAD
    import Part
except ImportError as e:
    print(f"❌ Error importing FreeCAD modules: {e}")
    print("\nThis script must be run with FreeCAD's Python interpreter:")
    print('  Method 1: FreeCAD --console this_script.py <gcode_file>')
    print('  Method 2: Open FreeCAD and run as Macro')
    sys.exit(1)


def parse_gcode_to_path(gcode_file):
    """Parse G-code and create FreeCAD Path"""
    print(f"\n📂 Loading: {gcode_file}")

    commands = []

    with open(gcode_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';') or line.startswith('('):
                continue

            if line.startswith('G') or line.startswith('M'):
                commands.append(line)

    print(f"✓ Loaded {len(commands)} G-code commands")
    return commands


def create_cylinder_stock(diameter, length, doc):
    """Create cylinder stock in FreeCAD"""
    print("⏳ Creating cylinder stock...")

    cylinder = doc.addObject("Part::Cylinder", "Stock")
    cylinder.Radius = diameter / 2.0
    cylinder.Height = length
    cylinder.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
    cylinder.Placement.Base = FreeCAD.Vector(0, 0, -diameter/2)

    # Make it semi-transparent
    cylinder.ViewObject.Transparency = 50
    cylinder.ViewObject.ShapeColor = (0.8, 0.6, 0.4)

    doc.recompute()
    return cylinder


def create_toolpath_visualization(commands, doc):
    """Create toolpath visualization in FreeCAD"""
    print("⏳ Creating toolpath visualization...")

    points = []
    current_pos = FreeCAD.Vector(0, 0, 0)

    for cmd in commands:
        if cmd.startswith('G0') or cmd.startswith('G1'):
            parts = cmd.split()
            x, y, z = current_pos.x, current_pos.y, current_pos.z

            for part in parts[1:]:
                if len(part) < 2:
                    continue
                axis = part[0].upper()
                try:
                    val = float(part[1:])
                    if axis == 'X':
                        x = val
                    elif axis == 'Y':
                        y = val
                    elif axis == 'Z':
                        z = val
                except ValueError:
                    pass

            current_pos = FreeCAD.Vector(x, y, z)
            points.append(current_pos)

    if len(points) < 2:
        print("⚠️  No toolpath points found")
        return None

    # Create wire from points
    import Part
    edges = []
    for i in range(len(points) - 1):
        edge = Part.makeLine(points[i], points[i+1])
        edges.append(edge)

    if edges:
        wire = Part.Wire(edges)
        toolpath = doc.addObject("Part::Feature", "Toolpath")
        toolpath.Shape = wire
        toolpath.ViewObject.LineColor = (1.0, 0.0, 0.0)
        toolpath.ViewObject.LineWidth = 3.0

        doc.recompute()
        print(f"✓ Created toolpath with {len(points)} points")
        return toolpath

    return None


def visualize_in_freecad(gcode_file, diameter=50, length=100):
    """Main FreeCAD visualization"""
    print("\n" + "="*60)
    print("  FreeCAD 4-Axis G-code Visualizer")
    print("="*60)

    # Create new document
    doc = FreeCAD.newDocument("FourAxis_Visualization")

    # Parse G-code
    commands = parse_gcode_to_path(gcode_file)

    # Create stock
    stock = create_cylinder_stock(diameter, length, doc)

    # Create toolpath
    toolpath = create_toolpath_visualization(commands, doc)

    # Fit view
    FreeCAD.Gui.SendMsgToActiveView("ViewFit")
    FreeCAD.Gui.activeDocument().activeView().viewIsometric()

    print("\n✅ Visualization complete!")
    print("\n📺 FreeCAD is now showing your 4-axis toolpath")
    print("   - Scroll: Zoom")
    print("   - Middle mouse: Rotate view")
    print("   - Shift+Middle mouse: Pan")

    return doc, stock, toolpath


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: visualize_4axis_freecad.py <gcode_file>")

        # Try default file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gcode_file = os.path.join(script_dir, "test_output", "true_4axis_surface.gcode")

        if not os.path.exists(gcode_file):
            print(f"\n❌ Default file not found: {gcode_file}")
            sys.exit(1)
    else:
        gcode_file = sys.argv[1]

    if not os.path.exists(gcode_file):
        print(f"❌ File not found: {gcode_file}")
        sys.exit(1)

    visualize_in_freecad(gcode_file)
