#!/usr/bin/env python3
"""
Generate complex contoured 4-axis toolpath

Creates a toolpath for a workpiece with variable diameter along its length,
demonstrating proper 4-axis kinematics with surface following.
"""

import sys
sys.path.append('.')

from true_4axis_generator import (
    WorkpieceConfig, ToolConfig, MachineConfig, StrategyConfig,
    True4AxisGenerator, GCodeExporter
)


def create_contoured_cylinder():
    """
    Create a contoured cylinder with varying diameter

    Profile: narrow at ends, wider in middle (barrel shape)
    """
    # Define contour points (position_mm, radius_mm)
    contour_points = [
        (0, 15),      # Start: 30mm diameter
        (25, 20),     # Quarter: 40mm diameter
        (50, 25),     # Middle: 50mm diameter (widest)
        (75, 20),     # Three-quarter: 40mm diameter
        (100, 15),    # End: 30mm diameter
    ]

    workpiece = WorkpieceConfig(
        type="CONTOURED",
        diameter=50.0,  # Max diameter
        length=100.0,
        rotary_axis="X",
        contour_points=contour_points
    )

    tool = ToolConfig(diameter=6.0)
    machine = MachineConfig(feed_rate=500.0, spindle_rpm=12000)
    strategy = StrategyConfig(
        type="SURFACE",
        stepover=3.0,  # Smaller stepover for smooth finish on contour
        angular_resolution=5.0,  # Finer resolution
        start_angle=0.0,
        end_angle=360.0  # Full wrap
    )

    print("\n" + "="*70)
    print("  Contoured Cylinder Toolpath Generator")
    print("="*70)
    print("\n📐 Profile:")
    print("   Position (mm) | Radius (mm) | Diameter (mm)")
    print("   " + "-"*50)
    for pos, rad in contour_points:
        print(f"   {pos:6.1f}        | {rad:6.1f}      | {rad*2:6.1f}")
    print("\n   Shape: Barrel (narrow at ends, wide in middle)")

    generator = True4AxisGenerator(workpiece, tool, machine, strategy)

    print(f"\n⏳ Generating contoured toolpath...")
    path = generator.generate_toolpath()
    print(f"✓ Generated {len(path)} points")

    # Export
    output_file = "test_output/true_4axis_contoured.gcode"
    exporter = GCodeExporter(machine, strategy)

    print(f"\n⏳ Exporting to {output_file}...")
    if exporter.export(path, output_file, "GRBL"):
        import os
        size = os.path.getsize(output_file)
        with open(output_file) as f:
            lines = len(f.readlines())

        print(f"✓ Exported: {output_file}")
        print(f"  Size: {size:,} bytes")
        print(f"  Lines: {lines}")
        print("\n✅ Complete!")
        print("\n💡 Load in CAMotics to see tool following the barrel contour")
        return 0
    else:
        print("\n❌ Export failed!")
        return 1


def create_wavy_cylinder():
    """
    Create a cylinder with sinusoidal variation (wavy surface)
    """
    import math

    # Create sinusoidal contour
    contour_points = []
    for i in range(21):  # 20 segments
        pos = i * 5.0  # 0 to 100mm in 5mm steps
        # Sine wave: radius varies between 20-25mm
        base_radius = 22.5
        amplitude = 2.5
        frequency = 2.0  # 2 complete waves
        radius = base_radius + amplitude * math.sin(frequency * 2 * math.pi * pos / 100.0)
        contour_points.append((pos, radius))

    workpiece = WorkpieceConfig(
        type="CONTOURED",
        diameter=50.0,
        length=100.0,
        rotary_axis="X",
        contour_points=contour_points
    )

    tool = ToolConfig(diameter=6.0)
    machine = MachineConfig(feed_rate=500.0, spindle_rpm=12000)
    strategy = StrategyConfig(
        type="SURFACE",
        stepover=2.5,
        angular_resolution=5.0,
        start_angle=0.0,
        end_angle=360.0
    )

    print("\n" + "="*70)
    print("  Wavy Cylinder Toolpath Generator")
    print("="*70)
    print("\n📐 Profile: Sinusoidal variation")
    print(f"   Base radius: 22.5mm (45mm diameter)")
    print(f"   Amplitude: ±2.5mm")
    print(f"   Frequency: 2 complete waves over 100mm length")
    print(f"   Diameter range: 40-50mm")

    generator = True4AxisGenerator(workpiece, tool, machine, strategy)

    print(f"\n⏳ Generating wavy toolpath...")
    path = generator.generate_toolpath()
    print(f"✓ Generated {len(path)} points")

    # Export
    output_file = "test_output/true_4axis_wavy.gcode"
    exporter = GCodeExporter(machine, strategy)

    print(f"\n⏳ Exporting to {output_file}...")
    if exporter.export(path, output_file, "GRBL"):
        import os
        size = os.path.getsize(output_file)
        with open(output_file) as f:
            lines = len(f.readlines())

        print(f"✓ Exported: {output_file}")
        print(f"  Size: {size:,} bytes")
        print(f"  Lines: {lines}")
        print("\n✅ Complete!")
        print("\n💡 Load in CAMotics to see tool following the wavy surface")
        return 0
    else:
        print("\n❌ Export failed!")
        return 1


if __name__ == "__main__":
    print("\n🔧 Complex Surface 4-Axis Toolpath Examples\n")

    print("="*70)
    print("Example 1: Barrel-shaped contour")
    print("="*70)
    result1 = create_contoured_cylinder()

    print("\n\n")
    print("="*70)
    print("Example 2: Sinusoidal (wavy) surface")
    print("="*70)
    result2 = create_wavy_cylinder()

    print("\n\n" + "="*70)
    if result1 == 0 and result2 == 0:
        print("✅ All complex surfaces generated successfully!")
        print("\n📂 Files created:")
        print("   - test_output/true_4axis_contoured.gcode (barrel shape)")
        print("   - test_output/true_4axis_wavy.gcode (sinusoidal)")
        print("\n🎬 Next steps:")
        print("   1. Open CAMotics")
        print("   2. Load each .gcode file")
        print("   3. Observe tool following variable diameter surfaces")
        print("   4. Notice how Y-axis position changes with contour")
        exit(0)
    else:
        print("❌ Some files failed to generate")
        exit(1)
