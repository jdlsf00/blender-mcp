#!/usr/bin/env python3
"""
FreeCAD 4-Axis Helical Toolpath Generator
Automates FreeCAD Path workbench to create rotary helical toolpaths

Usage:
    python freecad_4axis_generator.py --diameter 50 --length 100 --output helix.gcode
    python freecad_4axis_generator.py --config config.json
"""

import sys
import os
import argparse
import json
from pathlib import Path

def setup_freecad_path():
    """Add FreeCAD to Python path"""
    # Common FreeCAD installation paths
    freecad_paths = [
        r"C:\Program Files\FreeCAD 0.21\bin",
        r"C:\Program Files\FreeCAD 1.0\bin",
        r"C:\Program Files (x86)\FreeCAD\bin",
        "/usr/lib/freecad/lib",
        "/usr/local/lib/freecad/lib",
        "/Applications/FreeCAD.app/Contents/Resources/lib"
    ]

    for path in freecad_paths:
        if os.path.exists(path):
            sys.path.append(path)
            print(f"✓ Found FreeCAD at: {path}")
            return True

    print("✗ FreeCAD not found. Please install FreeCAD from https://www.freecadapp.org/")
    print("  Or set FREECAD_PATH environment variable")

    if 'FREECAD_PATH' in os.environ:
        custom_path = os.environ['FREECAD_PATH']
        sys.path.append(custom_path)
        print(f"✓ Using custom FreeCAD path: {custom_path}")
        return True

    return False

def create_4axis_toolpath(config):
    """
    Create 4-axis helical toolpath using FreeCAD

    Args:
        config (dict): Configuration with keys:
            - diameter: Cylinder diameter (mm)
            - length: Cylinder length (mm)
            - tool_diameter: End mill diameter (mm)
            - stepover: Axial step between passes (mm)
            - feed_rate: Cutting feed rate (mm/min)
            - spindle_rpm: Spindle speed (RPM)
            - rotary_axis: Rotation axis (X, Y, Z)
            - post_processor: Post processor name (grbl, linuxcnc, etc)
            - output: Output G-code file path
    """

    try:
        import FreeCAD
        import Part
        import Path
        from Path import Command
    except ImportError as e:
        print(f"✗ Error importing FreeCAD modules: {e}")
        print("  Make sure FreeCAD is properly installed")
        return False

    print("\n" + "="*60)
    print("FreeCAD 4-Axis Toolpath Generator")
    print("="*60)

    # Extract config
    diameter = config.get('diameter', 50)
    length = config.get('length', 100)
    tool_diameter = config.get('tool_diameter', 6)
    stepover = config.get('stepover', 5)
    feed_rate = config.get('feed_rate', 500)
    spindle_rpm = config.get('spindle_rpm', 12000)
    rotary_axis = config.get('rotary_axis', 'X').upper()
    post_processor = config.get('post_processor', 'grbl')
    output_file = config.get('output', 'freecad_4axis.gcode')

    print(f"\n📐 Configuration:")
    print(f"   Cylinder: ⌀{diameter}mm × {length}mm")
    print(f"   Tool: ⌀{tool_diameter}mm end mill")
    print(f"   Stepover: {stepover}mm")
    print(f"   Feed: {feed_rate} mm/min")
    print(f"   Spindle: {spindle_rpm} RPM")
    print(f"   Rotary Axis: {rotary_axis}")
    print(f"   Post: {post_processor}")
    print(f"   Output: {output_file}")

    # Create new document
    doc = FreeCAD.newDocument("4AxisHelix")
    print("\n✓ Created FreeCAD document")

    # Create cylinder geometry
    radius = diameter / 2.0

    if rotary_axis == 'X':
        # Cylinder along X-axis
        cylinder = Part.makeCylinder(radius, length,
                                     FreeCAD.Vector(0, 0, -radius),
                                     FreeCAD.Vector(1, 0, 0))
    elif rotary_axis == 'Y':
        # Cylinder along Y-axis
        cylinder = Part.makeCylinder(radius, length,
                                     FreeCAD.Vector(-radius, 0, 0),
                                     FreeCAD.Vector(0, 1, 0))
    else:  # Z
        # Cylinder along Z-axis
        cylinder = Part.makeCylinder(radius, length,
                                     FreeCAD.Vector(0, 0, 0),
                                     FreeCAD.Vector(0, 0, 1))

    shape_obj = doc.addObject("Part::Feature", "Cylinder")
    shape_obj.Shape = cylinder
    print(f"✓ Created cylinder along {rotary_axis}-axis")

    # Create Path Job
    job = Path.Job.Create("Job", [shape_obj], None)
    doc.addObject("Path::FeaturePython", "Job")
    print("✓ Created Path Job")

    # Setup stock (slightly oversized cylinder)
    stock_radius = radius + 5
    stock_length = length + 10
    job.Stock = Path.Stock.CreateFromBase(shape_obj, stock_radius, stock_length)
    print("✓ Configured stock")

    # Create tool
    tool = Path.Tool()
    tool.Diameter = tool_diameter
    tool.LengthOffset = 50
    tool.FlatRadius = 0
    tool.CornerRadius = 0
    tool.CuttingEdgeAngle = 180
    tool.CuttingEdgeHeight = 20
    tool.Name = f"D{tool_diameter}mm_EndMill"

    # Create tool controller
    tc = Path.ToolController.Create("TC: D{}mm".format(tool_diameter))
    tc.Tool = tool
    tc.HorizFeed = feed_rate
    tc.VertFeed = feed_rate / 2
    tc.HorizRapid = feed_rate * 2
    tc.VertRapid = feed_rate
    tc.SpindleSpeed = spindle_rpm
    tc.SpindleDir = "Forward"

    job.Tools.Group.append(tc)
    print(f"✓ Created tool controller: D{tool_diameter}mm")

    # Create 4-axis operation
    # Note: FreeCAD's 4-axis support depends on version
    # Using Surface operation with rotation

    try:
        op = Path.Operation.Create("Surface", job, shape_obj)
        op.ToolController = tc
        op.BoundBox = shape_obj.Shape.BoundBox

        # Configure for rotary
        if hasattr(op, 'RotationAxis'):
            op.RotationAxis = rotary_axis

        # Stepover
        op.StepOver = stepover

        # Pattern
        if hasattr(op, 'PatternType'):
            op.PatternType = "Spiral"  # or "ZigZag"

        job.Operations.Group.append(op)
        print("✓ Created 4-axis surface operation")

    except Exception as e:
        print(f"⚠ Advanced 4-axis op unavailable: {e}")
        print("  Using profile operation instead")

        # Fallback to profile with rotation
        op = Path.Operation.Create("Profile", job, shape_obj)
        op.ToolController = tc
        job.Operations.Group.append(op)

    # Generate toolpath
    print("\n⏳ Calculating toolpath...")
    job.Proxy.execute(job)
    doc.recompute()
    print("✓ Toolpath calculated")

    # Post-process to G-code
    print(f"\n⏳ Post-processing with '{post_processor}'...")

    # Get post processor
    postlist = Path.Post.Processor.get_post_processor_list()

    if post_processor not in postlist:
        print(f"⚠ Post processor '{post_processor}' not found")
        print(f"  Available: {', '.join(postlist[:5])}")
        post_processor = postlist[0] if postlist else 'grbl'
        print(f"  Using: {post_processor}")

    # Export G-code
    gcode = Path.Post.Processor.export(job, output_file, post_processor)
    print(f"✓ G-code exported: {output_file}")

    # Analyze output
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            lines = f.readlines()

        gcode_lines = [l for l in lines if l.strip() and not l.strip().startswith(';')]
        has_a_axis = any('A' in line.upper() for line in gcode_lines)

        print(f"\n📊 G-code Statistics:")
        print(f"   Total lines: {len(lines)}")
        print(f"   G-code commands: {len(gcode_lines)}")
        print(f"   A-axis commands: {'✓ Yes' if has_a_axis else '✗ No (check config)'}")

        # Sample lines
        print(f"\n📝 Sample G-code (first 10 moves):")
        move_count = 0
        for line in gcode_lines:
            if 'G0' in line or 'G1' in line:
                print(f"   {line.strip()}")
                move_count += 1
                if move_count >= 10:
                    break

    # Close document
    FreeCAD.closeDocument(doc.Name)
    print("\n✅ Complete!")
    print(f"   Output: {os.path.abspath(output_file)}")

    return True


def load_config(config_file):
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description='FreeCAD 4-Axis Helical Toolpath Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick generation with defaults
  python freecad_4axis_generator.py

  # Custom cylinder dimensions
  python freecad_4axis_generator.py --diameter 50 --length 100

  # Full configuration
  python freecad_4axis_generator.py --diameter 50 --length 100 \\
      --tool 6 --stepover 5 --feed 500 --spindle 12000 \\
      --axis X --post grbl --output helix.gcode

  # From config file
  python freecad_4axis_generator.py --config freecad_config.json

Config file format (JSON):
{
  "diameter": 50,
  "length": 100,
  "tool_diameter": 6,
  "stepover": 5,
  "feed_rate": 500,
  "spindle_rpm": 12000,
  "rotary_axis": "X",
  "post_processor": "grbl",
  "output": "freecad_4axis.gcode"
}
        """
    )

    parser.add_argument('--config', '-c', type=str,
                       help='Load configuration from JSON file')
    parser.add_argument('--diameter', '-d', type=float, default=50,
                       help='Cylinder diameter (mm) [default: 50]')
    parser.add_argument('--length', '-l', type=float, default=100,
                       help='Cylinder length (mm) [default: 100]')
    parser.add_argument('--tool', '-t', type=float, default=6,
                       help='Tool diameter (mm) [default: 6]')
    parser.add_argument('--stepover', '-s', type=float, default=5,
                       help='Stepover distance (mm) [default: 5]')
    parser.add_argument('--feed', '-f', type=float, default=500,
                       help='Feed rate (mm/min) [default: 500]')
    parser.add_argument('--spindle', type=int, default=12000,
                       help='Spindle RPM [default: 12000]')
    parser.add_argument('--axis', '-a', type=str, default='X', choices=['X', 'Y', 'Z'],
                       help='Rotary axis [default: X]')
    parser.add_argument('--post', '-p', type=str, default='grbl',
                       help='Post processor [default: grbl]')
    parser.add_argument('--output', '-o', type=str, default='freecad_4axis.gcode',
                       help='Output G-code file [default: freecad_4axis.gcode]')

    args = parser.parse_args()

    # Load config
    if args.config:
        print(f"📄 Loading config from: {args.config}")
        config = load_config(args.config)
    else:
        config = {
            'diameter': args.diameter,
            'length': args.length,
            'tool_diameter': args.tool,
            'stepover': args.stepover,
            'feed_rate': args.feed,
            'spindle_rpm': args.spindle,
            'rotary_axis': args.axis,
            'post_processor': args.post,
            'output': args.output
        }

    # Setup FreeCAD
    if not setup_freecad_path():
        print("\n❌ Cannot proceed without FreeCAD")
        print("\nInstallation instructions:")
        print("  Windows: https://www.freecadapp.org/downloads.php")
        print("  Linux: sudo apt install freecad")
        print("  macOS: brew install freecad")
        return 1

    # Generate toolpath
    success = create_4axis_toolpath(config)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
