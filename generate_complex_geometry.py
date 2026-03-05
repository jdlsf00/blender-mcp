#!/usr/bin/env python3
"""
Complex Geometric 4-Axis Toolpath Generator

Creates toolpaths for mathematically-defined complex shapes including:
- Chess pawn with smooth profile
- Vase with trigonometric curves
- Helical spiral column
- Fibonacci spiral profile
- Bezier curve turned object
"""

import sys
import os
import math

# Add parent directory to path to import the generator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from true_4axis_generator import (
    WorkpieceConfig, ToolConfig, MachineConfig, StrategyConfig,
    True4AxisGenerator, GCodeExporter
)


def generate_chess_pawn():
    """Generate a chess pawn with classic profile"""
    print("\n" + "="*60)
    print("  CHESS PAWN - Classical Profile")
    print("="*60)

    # Define pawn profile (position_mm, radius_mm)
    # Classic pawn shape: base -> stem -> ball -> crown
    contour_points = [
        (0, 12),      # Wide base
        (5, 10),      # Base taper
        (10, 8),      # Stem start
        (15, 6),      # Narrow stem
        (20, 5),      # Narrowest point
        (25, 6),      # Ball bottom
        (30, 9),      # Ball widest
        (35, 8),      # Ball top
        (40, 6),      # Neck
        (45, 7),      # Crown base
        (50, 8),      # Crown middle
        (55, 7),      # Crown taper
        (60, 6),      # Crown top
    ]

    workpiece = WorkpieceConfig(
        type="CONTOURED",
        diameter=24,  # Max diameter (ball section)
        length=60,
        rotary_axis='X',
        contour_points=contour_points
    )

    tool = ToolConfig(
        diameter=6,
        flutes=4,
        material='carbide'
    )

    machine = MachineConfig(
        feed_rate=800,
        plunge_rate=200,
        rapid_rate=3000,
        spindle_rpm=15000,
        safe_z=50
    )

    strategy = StrategyConfig(
        type="SURFACE",
        stepover=1.0,              # Fine 1mm stepover
        angular_resolution=3.0,    # 3° for smooth surface
        start_angle=0,
        end_angle=360              # Full rotation
    )

    # Generate
    generator = True4AxisGenerator(workpiece, tool, machine, strategy)
    toolpath = generator.generate_surface_toolpath()

    # Export
    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    output_file = os.path.join(output_dir, "chess_pawn.gcode")

    exporter = GCodeExporter(machine, strategy)
    exporter.export(toolpath, output_file, "Chess Pawn - Classical Profile")

    print(f"\n✓ Generated: {output_file}")
    print(f"  Points: {len(toolpath)}")
    print(f"  File size: {os.path.getsize(output_file) / 1024:.1f} KB")


def generate_trigonometric_vase():
    """Generate a vase with sine wave profile"""
    print("\n" + "="*60)
    print("  TRIGONOMETRIC VASE - Sine Wave Profile")
    print("="*60)

    # Create sine wave profile for elegant vase shape
    # r(z) = base_radius + amplitude * sin(frequency * z)

    length = 100
    base_radius = 15
    amplitude = 5
    frequency = 2 * math.pi / 50  # 2 complete waves over length
    num_points = 41

    contour_points = []
    for i in range(num_points):
        z = (i / (num_points - 1)) * length
        radius = base_radius + amplitude * math.sin(frequency * z)
        contour_points.append((z, radius))

    workpiece = WorkpieceConfig(
        type="CONTOURED",
        diameter=(base_radius + amplitude) * 2,
        length=length,
        rotary_axis='X',
        contour_points=contour_points
    )

    tool = ToolConfig(diameter=6, flutes=4, material='carbide')
    machine = MachineConfig(
        feed_rate=600,
        plunge_rate=150,
        rapid_rate=3000,
        spindle_rpm=12000,
        safe_z=50
    )

    strategy = StrategyConfig(
        type="SURFACE",
        stepover=1.5,
        angular_resolution=5.0,
        start_angle=0,
        end_angle=360
    )

    generator = True4AxisGenerator(workpiece, tool, machine, strategy)
    toolpath = generator.generate_surface_toolpath()

    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    output_file = os.path.join(output_dir, "trig_vase.gcode")

    exporter = GCodeExporter(machine, strategy)
    exporter.export(toolpath, output_file, "Trigonometric Vase - Sine Wave")

    print(f"\n✓ Generated: {output_file}")
    print(f"  Points: {len(toolpath)}")
    print(f"  File size: {os.path.getsize(output_file) / 1024:.1f} KB")


def generate_fibonacci_spiral():
    """Generate profile based on Fibonacci spiral (golden ratio)"""
    print("\n" + "="*60)
    print("  FIBONACCI SPIRAL - Golden Ratio Profile")
    print("="*60)

    # Use golden ratio to create aesthetically pleasing taper
    # Each section is phi times the previous
    phi = (1 + math.sqrt(5)) / 2  # Golden ratio ≈ 1.618

    length = 80
    base_radius = 20
    num_sections = 8

    contour_points = []
    for i in range(num_sections + 1):
        z = (i / num_sections) * length
        # Radius decreases by golden ratio
        radius = base_radius / (phi ** (i * 0.5))
        contour_points.append((z, max(radius, 3)))  # Minimum 3mm radius

    workpiece = WorkpieceConfig(
        type="CONTOURED",
        diameter=base_radius * 2,
        length=length,
        rotary_axis='X',
        contour_points=contour_points
    )

    tool = ToolConfig(diameter=4, flutes=4, material='carbide')
    machine = MachineConfig(
        feed_rate=700,
        plunge_rate=180,
        rapid_rate=3000,
        spindle_rpm=14000,
        safe_z=50
    )

    strategy = StrategyConfig(
        type="SURFACE",
        stepover=1.2,
        angular_resolution=4.0,
        start_angle=0,
        end_angle=360
    )

    generator = True4AxisGenerator(workpiece, tool, machine, strategy)
    toolpath = generator.generate_surface_toolpath()

    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    output_file = os.path.join(output_dir, "fibonacci_spiral.gcode")

    exporter = GCodeExporter(machine, strategy)
    exporter.export(toolpath, output_file, "Fibonacci Spiral - Golden Ratio")

    print(f"\n✓ Generated: {output_file}")
    print(f"  Points: {len(toolpath)}")
    print(f"  File size: {os.path.getsize(output_file) / 1024:.1f} KB")


def bezier_curve(t, p0, p1, p2, p3):
    """Cubic Bezier curve calculation"""
    return (
        (1-t)**3 * p0 +
        3 * (1-t)**2 * t * p1 +
        3 * (1-t) * t**2 * p2 +
        t**3 * p3
    )


def generate_bezier_vase():
    """Generate vase with Bezier curve profile"""
    print("\n" + "="*60)
    print("  BEZIER VASE - Smooth Cubic Curve")
    print("="*60)

    # Define Bezier control points for elegant vase profile
    # (z_position, radius)
    length = 90

    # Control points: base, lower bulge, upper narrow, lip
    z_controls = [0, 20, 70, 90]
    r_controls = [10, 15, 8, 12]  # Base, bulge, narrow, lip

    # Sample Bezier curve
    num_points = 31
    contour_points = []

    for i in range(num_points):
        t = i / (num_points - 1)
        z = bezier_curve(t, z_controls[0], z_controls[1], z_controls[2], z_controls[3])
        r = bezier_curve(t, r_controls[0], r_controls[1], r_controls[2], r_controls[3])
        contour_points.append((z, r))

    workpiece = WorkpieceConfig(
        type="CONTOURED",
        diameter=max(r_controls) * 2,
        length=length,
        rotary_axis='X',
        contour_points=contour_points
    )

    tool = ToolConfig(diameter=6, flutes=4, material='carbide')
    machine = MachineConfig(
        feed_rate=650,
        plunge_rate=160,
        rapid_rate=3000,
        spindle_rpm=13000,
        safe_z=50
    )

    strategy = StrategyConfig(
        type="SURFACE",
        stepover=1.0,
        angular_resolution=4.0,
        start_angle=0,
        end_angle=360
    )

    generator = True4AxisGenerator(workpiece, tool, machine, strategy)
    toolpath = generator.generate_surface_toolpath()

    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    output_file = os.path.join(output_dir, "bezier_vase.gcode")

    exporter = GCodeExporter(machine, strategy)
    exporter.export(toolpath, output_file, "Bezier Vase - Cubic Curve Profile")

    print(f"\n✓ Generated: {output_file}")
    print(f"  Points: {len(toolpath)}")
    print(f"  File size: {os.path.getsize(output_file) / 1024:.1f} KB")


def generate_helical_column():
    """Generate classical helical column (like Greek/Roman architecture)"""
    print("\n" + "="*60)
    print("  HELICAL COLUMN - Architectural Twist")
    print("="*60)

    # Column with slight entasis (taper) and helical groove
    length = 120
    base_radius = 18
    top_radius = 15
    num_points = 25

    # Linear taper with slight curve (entasis)
    contour_points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        z = t * length

        # Slight parabolic curve for classical entasis
        entasis_factor = 1 - 0.1 * (4 * t * (1 - t))  # Parabola peaks at middle
        radius = base_radius - (base_radius - top_radius) * t * entasis_factor

        contour_points.append((z, radius))

    workpiece = WorkpieceConfig(
        type="CONTOURED",
        diameter=base_radius * 2,
        length=length,
        rotary_axis='X',
        contour_points=contour_points
    )

    tool = ToolConfig(diameter=6, flutes=4, material='carbide')
    machine = MachineConfig(
        feed_rate=750,
        plunge_rate=200,
        rapid_rate=3000,
        spindle_rpm=12000,
        safe_z=50
    )

    # Create helical groove with multiple passes
    strategy = StrategyConfig(
        type="SURFACE",
        stepover=2.0,
        angular_resolution=5.0,
        start_angle=0,
        end_angle=720  # 2 full rotations for helical effect
    )

    generator = True4AxisGenerator(workpiece, tool, machine, strategy)
    toolpath = generator.generate_surface_toolpath()

    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    output_file = os.path.join(output_dir, "helical_column.gcode")

    exporter = GCodeExporter(machine, strategy)
    exporter.export(toolpath, output_file, "Helical Column - Architectural")

    print(f"\n✓ Generated: {output_file}")
    print(f"  Points: {len(toolpath)}")
    print(f"  File size: {os.path.getsize(output_file) / 1024:.1f} KB")


def main():
    """Generate all complex geometric shapes"""
    print("\n" + "="*60)
    print("  COMPLEX GEOMETRIC 4-AXIS TOOLPATH GENERATOR")
    print("  Mathematical Shapes and Curves")
    print("="*60)

    # Create output directory if needed
    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    os.makedirs(output_dir, exist_ok=True)

    # Generate all shapes
    generate_chess_pawn()
    generate_trigonometric_vase()
    generate_fibonacci_spiral()
    generate_bezier_vase()
    generate_helical_column()

    print("\n" + "="*60)
    print("  ✓ ALL GEOMETRIC SHAPES GENERATED")
    print("="*60)
    print("\nGenerated files in test_output/:")
    print("  • chess_pawn.gcode      - Classical chess piece")
    print("  • trig_vase.gcode       - Sine wave vase")
    print("  • fibonacci_spiral.gcode - Golden ratio taper")
    print("  • bezier_vase.gcode     - Cubic Bezier curve")
    print("  • helical_column.gcode  - Architectural column")
    print("\nVisualize with:")
    print("  python visualize_4axis_blender.py test_output/<filename>.gcode")


if __name__ == "__main__":
    main()
