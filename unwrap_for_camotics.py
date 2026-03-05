#!/usr/bin/env python3
"""
4-Axis to 3-Axis Unwrapper for CAMotics Visualization

Since CAMotics doesn't support A-axis, this script "unwraps" the rotary motion
into XYZ coordinates that CAMotics can visualize while maintaining the correct
4-axis machining concept.

The visualization shows what the tool path looks like in 3D space.
"""

import math
import argparse


def parse_gcode_line(line):
    """Parse G-code line and extract XYZA coordinates"""
    line = line.strip()
    if not line or line.startswith(';') or line.startswith('('):
        return None

    coords = {}
    parts = line.split()

    for part in parts:
        if len(part) < 2:
            continue
        axis = part[0].upper()
        if axis in 'XYZA':
            try:
                coords[axis] = float(part[1:])
            except ValueError:
                pass

    return coords if coords else None


def unwrap_4axis_to_3axis(input_file, output_file, workpiece_diameter=50.0):
    """
    Convert 4-axis G-code to 3-axis G-code for CAMotics visualization

    This transforms the A-axis rotation into actual XYZ tool positions
    as if the tool was moving around a stationary cylinder (for visualization only)
    """

    workpiece_radius = workpiece_diameter / 2.0

    print(f"\n🔄 Unwrapping 4-axis G-code for CAMotics visualization")
    print(f"   Input: {input_file}")
    print(f"   Output: {output_file}")
    print(f"   Workpiece: ⌀{workpiece_diameter}mm")

    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        # Write header
        f_out.write("; Unwrapped 4-Axis Toolpath for CAMotics Visualization\n")
        f_out.write("; Original: True 4-axis rotary machining\n")
        f_out.write("; Visualization: 3-axis XYZ motion showing tool path\n")
        f_out.write(";\n")

        last_coords = {'X': 0, 'Y': 0, 'Z': 0, 'A': 0}
        point_count = 0

        for line in f_in:
            stripped = line.strip()

            # Pass through comments and setup codes
            if (stripped.startswith(';') or stripped.startswith('(') or
                stripped.startswith('G21') or stripped.startswith('G90') or
                stripped.startswith('G17') or stripped.startswith('M') or
                stripped.startswith('G1 F') or not stripped):
                f_out.write(line)
                continue

            # Parse coordinates
            coords = parse_gcode_line(stripped)
            if not coords:
                f_out.write(line)
                continue

            # Update last known coordinates
            for axis in 'XYZA':
                if axis in coords:
                    last_coords[axis] = coords[axis]

            # Extract current position
            x_linear = last_coords['X']
            y_tool = last_coords['Y']
            z_tool = last_coords['Z']
            a_angle = last_coords['A']

            # Convert to 3-axis coordinates for visualization
            # The tool's Y,Z position represents offset from workpiece surface
            # We need to calculate where the tool actually is in space

            angle_rad = math.radians(a_angle)

            # Tool is at radius y_tool from axis, at angle a_angle
            # For X-axis rotary (cylinder along X):
            y_viz = y_tool * math.cos(angle_rad) + z_tool * math.sin(angle_rad)
            z_viz = -y_tool * math.sin(angle_rad) + z_tool * math.cos(angle_rad)
            x_viz = x_linear

            # Determine command type
            cmd = 'G1'
            if stripped.startswith('G0'):
                cmd = 'G0'
            elif stripped.startswith('G1'):
                cmd = 'G1'

            # Write unwrapped coordinates
            f_out.write(f"{cmd} X{x_viz:.4f} Y{y_viz:.4f} Z{z_viz:.4f}\n")
            point_count += 1

        print(f"✓ Unwrapped {point_count} points")

    return True


def main():
    parser = argparse.ArgumentParser(description="Unwrap 4-axis G-code for CAMotics")
    parser.add_argument("--input", required=True, help="Input 4-axis G-code file")
    parser.add_argument("--output", required=True, help="Output 3-axis G-code file")
    parser.add_argument("--diameter", type=float, default=50.0, help="Workpiece diameter (mm)")

    args = parser.parse_args()

    if unwrap_4axis_to_3axis(args.input, args.output, args.diameter):
        print("\n✅ Complete! Load in CAMotics to visualize.")
        return 0
    else:
        print("\n❌ Failed!")
        return 1


if __name__ == "__main__":
    exit(main())
