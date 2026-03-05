#!/usr/bin/env python3
"""
Standalone 4-Axis G-code Generator
Pure Python implementation - no dependencies on Blender or FreeCAD

Usage:
    python standalone_4axis_gcode.py --diameter 50 --length 100
    python standalone_4axis_gcode.py --config config.json
"""

import math
import argparse
import json
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ToolConfig:
    """Tool configuration"""
    diameter: float = 6.0  # mm
    flutes: int = 2
    material: str = "carbide"


@dataclass
class MachineConfig:
    """Machine parameters"""
    feed_rate: float = 500.0  # mm/min
    plunge_rate: float = 250.0  # mm/min
    rapid_rate: float = 1000.0  # mm/min
    spindle_rpm: int = 12000
    spindle_direction: str = "CW"


@dataclass
class GeometryConfig:
    """Workpiece geometry"""
    diameter: float = 50.0  # mm
    length: float = 100.0  # mm
    rotary_axis: str = "X"  # X, Y, or Z


@dataclass
class StrategyConfig:
    """Toolpath strategy"""
    type: str = "HELIX"  # HELIX, INDEXED, SPIRAL
    stepover: float = 5.0  # mm
    angular_resolution: float = 10.0  # degrees per step
    index_count: int = 8  # for INDEXED strategy
    safe_z: float = 50.0  # mm


class FourAxisGenerator:
    """4-axis helical toolpath generator"""

    def __init__(self, geometry: GeometryConfig, tool: ToolConfig,
                 machine: MachineConfig, strategy: StrategyConfig):
        self.geometry = geometry
        self.tool = tool
        self.machine = machine
        self.strategy = strategy

        # Calculate derived parameters
        self.radius = geometry.diameter / 2.0
        self.tool_radius = tool.diameter / 2.0
        self.cutting_radius = self.radius + self.tool_radius

        # Circumference and conversions
        self.circumference = 2 * math.pi * self.cutting_radius
        self.degrees_per_mm = 360.0 / self.circumference

    def generate_toolpath(self) -> List[Tuple[float, float, float, float]]:
        """
        Generate toolpath based on strategy
        Returns list of (x, y, z, a) tuples in mm and degrees
        """
        if self.strategy.type == "HELIX":
            return self._generate_helix()
        elif self.strategy.type == "INDEXED":
            return self._generate_indexed()
        elif self.strategy.type == "SPIRAL":
            return self._generate_spiral()
        else:
            raise ValueError(f"Unknown strategy: {self.strategy.type}")

    def _generate_helix(self) -> List[Tuple[float, float, float, float]]:
        """Generate continuous helical toolpath"""
        path = []

        # Calculate number of passes
        num_passes = int(self.geometry.length / self.strategy.stepover) + 1

        print(f"Helical toolpath:")
        print(f"  Radius: {self.cutting_radius:.3f}mm")
        print(f"  Length: {self.geometry.length:.3f}mm")
        print(f"  Stepover: {self.strategy.stepover:.3f}mm")
        print(f"  Passes: {num_passes}")
        print(f"  Total rotation: {num_passes * 360}°")

        for pass_num in range(num_passes):
            # Start position for this pass
            linear_start = pass_num * self.strategy.stepover

            # Full 360° rotation for this pass
            angle_range = range(0, 361, int(self.strategy.angular_resolution))

            for angle_deg in angle_range:
                # Progress through this pass (0 to 1)
                progress = angle_deg / 360.0

                # Linear position interpolated across the pass
                linear_pos = linear_start + (self.strategy.stepover * progress)

                # Clamp to geometry length
                linear_pos = min(linear_pos, self.geometry.length)

                # A-axis accumulates rotation
                a_angle = (pass_num * 360) + angle_deg

                # Calculate X, Y, Z based on rotary axis orientation
                x, y, z = self._calculate_position(
                    linear_pos, angle_deg, self.cutting_radius
                )

                path.append((x, y, z, a_angle))

        return path

    def _generate_indexed(self) -> List[Tuple[float, float, float, float]]:
        """Generate indexed toolpath (rotate, cut, rotate, cut)"""
        path = []

        index_count = self.strategy.index_count
        angle_step = 360.0 / index_count

        print(f"Indexed toolpath:")
        print(f"  Index positions: {index_count}")
        print(f"  Angle step: {angle_step:.2f}°")
        print(f"  Cuts per index: {int(self.geometry.length / self.strategy.stepover) + 1}")

        # For each indexed position
        for index in range(index_count):
            a_angle = index * angle_step

            # Machine along the axis at this rotation
            num_cuts = int(self.geometry.length / self.strategy.stepover) + 1

            for cut in range(num_cuts):
                linear_pos = cut * self.strategy.stepover
                linear_pos = min(linear_pos, self.geometry.length)

                # Calculate position (tool at surface)
                x, y, z = self._calculate_position(
                    linear_pos, a_angle, self.cutting_radius
                )

                path.append((x, y, z, a_angle))

        return path

    def _generate_spiral(self) -> List[Tuple[float, float, float, float]]:
        """Generate spiral toolpath (continuous angle increase)"""
        path = []

        # Total length to cover
        total_length = self.geometry.length

        # Calculate total rotation needed
        # Each revolution covers stepover distance
        revolutions = total_length / self.strategy.stepover
        total_rotation = revolutions * 360

        print(f"Spiral toolpath:")
        print(f"  Length: {total_length:.3f}mm")
        print(f"  Revolutions: {revolutions:.2f}")
        print(f"  Total rotation: {total_rotation:.1f}°")

        # Generate points with constant angular step
        num_points = int(total_rotation / self.strategy.angular_resolution)

        for i in range(num_points + 1):
            # Linear interpolation
            progress = i / num_points
            linear_pos = progress * total_length
            a_angle = progress * total_rotation

            # Calculate position
            x, y, z = self._calculate_position(
                linear_pos, a_angle, self.cutting_radius
            )

            path.append((x, y, z, a_angle))

        return path

    def _calculate_position(self, linear: float, angle_deg: float,
                           radius: float) -> Tuple[float, float, float]:
        """
        Calculate X, Y, Z position based on rotary axis orientation

        Args:
            linear: Position along rotary axis (mm)
            angle_deg: Rotation angle (degrees)
            radius: Radial distance from axis (mm)

        Returns:
            (x, y, z) tuple in mm
        """
        angle_rad = math.radians(angle_deg)

        if self.geometry.rotary_axis == 'X':
            # Cylinder along X-axis, rotate in YZ plane
            x = linear
            y = radius * math.cos(angle_rad)
            z = radius * math.sin(angle_rad)

        elif self.geometry.rotary_axis == 'Y':
            # Cylinder along Y-axis, rotate in XZ plane
            x = radius * math.cos(angle_rad)
            y = linear
            z = radius * math.sin(angle_rad)

        else:  # Z
            # Cylinder along Z-axis, rotate in XY plane
            x = radius * math.cos(angle_rad)
            y = radius * math.sin(angle_rad)
            z = linear

        return (x, y, z)


class GCodeExporter:
    """Export toolpath to G-code"""

    def __init__(self, machine: MachineConfig, strategy: StrategyConfig):
        self.machine = machine
        self.strategy = strategy

    def export(self, path: List[Tuple[float, float, float, float]],
               output_file: str, post_processor: str = "GRBL") -> bool:
        """
        Export toolpath to G-code file

        Args:
            path: List of (x, y, z, a) tuples
            output_file: Output file path
            post_processor: G-code dialect (GRBL, LINUXCNC, FANUC, MACH3)

        Returns:
            True if successful
        """
        try:
            with open(output_file, 'w') as f:
                self._write_header(f, post_processor)
                self._write_start_code(f, post_processor)
                self._write_toolpath(f, path, post_processor)
                self._write_end_code(f, post_processor)

            return True

        except Exception as e:
            print(f"✗ Export failed: {e}")
            return False

    def _write_header(self, f, post_processor: str):
        """Write file header comments"""
        f.write("; ============================================\n")
        f.write("; Standalone 4-Axis G-code Generator\n")
        f.write("; ============================================\n")
        f.write(f"; Post Processor: {post_processor}\n")
        f.write(f"; Feed Rate: {self.machine.feed_rate:.1f} mm/min\n")
        f.write(f"; Plunge Rate: {self.machine.plunge_rate:.1f} mm/min\n")
        f.write(f"; Spindle: {self.machine.spindle_rpm} RPM {self.machine.spindle_direction}\n")
        f.write(f"; Safe Z: {self.strategy.safe_z:.1f} mm\n")
        f.write(";\n")

    def _write_start_code(self, f, post_processor: str):
        """Write initialization G-code"""
        f.write("; Start code\n")
        f.write("G21 ; Millimeters\n")
        f.write("G90 ; Absolute positioning\n")
        f.write("G17 ; XY plane\n")

        if post_processor == "GRBL":
            f.write("G54 ; Work coordinate system\n")

        # Spindle on
        spindle_dir = "M3" if self.machine.spindle_direction == "CW" else "M4"
        f.write(f"{spindle_dir} S{self.machine.spindle_rpm} ; Spindle on\n")

        # Wait for spindle
        if post_processor in ["LINUXCNC", "MACH3"]:
            f.write("G4 P2 ; Wait 2 seconds for spindle\n")

        # Move to safe Z
        f.write(f"G0 Z{self.strategy.safe_z:.4f} ; Safe height\n")
        f.write("\n")

    def _write_toolpath(self, f, path: List[Tuple[float, float, float, float]],
                       post_processor: str):
        """Write toolpath moves"""
        f.write("; Toolpath\n")
        f.write(f"G1 F{self.machine.feed_rate:.1f}\n")

        for i, (x, y, z, a) in enumerate(path):
            if i == 0:
                # Rapid to first point
                f.write(f"G0 X{x:.4f} Y{y:.4f} Z{z:.4f} A{a:.4f} ; Start\n")
            else:
                # Linear cutting move
                f.write(f"G1 X{x:.4f} Y{y:.4f} Z{z:.4f} A{a:.4f}\n")

        f.write("\n")

    def _write_end_code(self, f, post_processor: str):
        """Write end code"""
        f.write("; End code\n")
        f.write(f"G0 Z{self.strategy.safe_z:.4f} ; Retract\n")
        f.write("M5 ; Spindle off\n")

        if post_processor == "GRBL":
            f.write("M2 ; End program\n")
        elif post_processor in ["LINUXCNC", "MACH3"]:
            f.write("M30 ; End program and rewind\n")
        else:
            f.write("M2 ; End program\n")


def load_config_file(config_path: str) -> dict:
    """Load configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description='Standalone 4-Axis G-code Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick generation
  python standalone_4axis_gcode.py

  # Custom parameters
  python standalone_4axis_gcode.py --diameter 50 --length 100 --stepover 5

  # Indexed strategy
  python standalone_4axis_gcode.py --strategy INDEXED --index-count 12

  # From config file
  python standalone_4axis_gcode.py --config config.json

  # Different rotary axis
  python standalone_4axis_gcode.py --axis Y --diameter 80 --length 150
        """
    )

    # Config file
    parser.add_argument('--config', '-c', type=str,
                       help='Load configuration from JSON file')

    # Geometry
    parser.add_argument('--diameter', '-d', type=float, default=50.0,
                       help='Cylinder diameter (mm) [default: 50]')
    parser.add_argument('--length', '-l', type=float, default=100.0,
                       help='Cylinder length (mm) [default: 100]')
    parser.add_argument('--axis', type=str, default='X', choices=['X', 'Y', 'Z'],
                       help='Rotary axis [default: X]')

    # Tool
    parser.add_argument('--tool-diameter', '-t', type=float, default=6.0,
                       help='Tool diameter (mm) [default: 6]')

    # Strategy
    parser.add_argument('--strategy', '-s', type=str, default='HELIX',
                       choices=['HELIX', 'INDEXED', 'SPIRAL'],
                       help='Toolpath strategy [default: HELIX]')
    parser.add_argument('--stepover', type=float, default=5.0,
                       help='Stepover distance (mm) [default: 5]')
    parser.add_argument('--angular-res', type=float, default=10.0,
                       help='Angular resolution (degrees) [default: 10]')
    parser.add_argument('--index-count', type=int, default=8,
                       help='Index positions for INDEXED strategy [default: 8]')

    # Machine
    parser.add_argument('--feed', '-f', type=float, default=500.0,
                       help='Feed rate (mm/min) [default: 500]')
    parser.add_argument('--spindle', type=int, default=12000,
                       help='Spindle RPM [default: 12000]')
    parser.add_argument('--post', '-p', type=str, default='GRBL',
                       choices=['GRBL', 'LINUXCNC', 'FANUC', 'MACH3'],
                       help='Post processor [default: GRBL]')

    # Output
    parser.add_argument('--output', '-o', type=str, default='standalone_4axis.gcode',
                       help='Output G-code file [default: standalone_4axis.gcode]')
    parser.add_argument('--stats', action='store_true',
                       help='Print detailed statistics')

    args = parser.parse_args()

    print("="*60)
    print("Standalone 4-Axis G-code Generator")
    print("="*60)

    # Load config
    if args.config:
        print(f"\n📄 Loading config: {args.config}")
        config_data = load_config_file(args.config)

        # Extract configurations
        geometry = GeometryConfig(**config_data.get('geometry', {}))
        tool = ToolConfig(**config_data.get('tool', {}))
        machine = MachineConfig(**config_data.get('machining', {}))
        strategy = StrategyConfig(**config_data.get('strategy', {}))

        output_file = config_data.get('output', {}).get('filename', args.output)
        post_processor = config_data.get('output', {}).get('post_processor', args.post).upper()

    else:
        # Use command line arguments
        geometry = GeometryConfig(
            diameter=args.diameter,
            length=args.length,
            rotary_axis=args.axis
        )

        tool = ToolConfig(diameter=args.tool_diameter)

        machine = MachineConfig(
            feed_rate=args.feed,
            spindle_rpm=args.spindle
        )

        strategy = StrategyConfig(
            type=args.strategy,
            stepover=args.stepover,
            angular_resolution=args.angular_res,
            index_count=args.index_count
        )

        output_file = args.output
        post_processor = args.post

    # Print configuration
    print(f"\n📐 Configuration:")
    print(f"   Geometry: ⌀{geometry.diameter}mm × {geometry.length}mm")
    print(f"   Rotary Axis: {geometry.rotary_axis}")
    print(f"   Tool: ⌀{tool.diameter}mm")
    print(f"   Strategy: {strategy.type}")
    print(f"   Stepover: {strategy.stepover}mm")
    print(f"   Feed: {machine.feed_rate} mm/min")
    print(f"   Spindle: {machine.spindle_rpm} RPM")
    print(f"   Post: {post_processor}")
    print(f"   Output: {output_file}")

    # Generate toolpath
    print(f"\n⏳ Generating {strategy.type} toolpath...")
    generator = FourAxisGenerator(geometry, tool, machine, strategy)
    path = generator.generate_toolpath()
    print(f"✓ Generated {len(path)} points")

    # Statistics
    if args.stats or path:
        x_coords = [p[0] for p in path]
        y_coords = [p[1] for p in path]
        z_coords = [p[2] for p in path]
        a_coords = [p[3] for p in path]

        print(f"\n📊 Toolpath Statistics:")
        print(f"   X: {min(x_coords):.3f} to {max(x_coords):.3f} mm")
        print(f"   Y: {min(y_coords):.3f} to {max(y_coords):.3f} mm")
        print(f"   Z: {min(z_coords):.3f} to {max(z_coords):.3f} mm")
        print(f"   A: {min(a_coords):.3f} to {max(a_coords):.3f}°")
        print(f"   Total rotation: {max(a_coords):.1f}°")
        print(f"   Revolutions: {max(a_coords)/360:.2f}")

    # Export to G-code
    print(f"\n⏳ Exporting to G-code...")
    exporter = GCodeExporter(machine, strategy)
    success = exporter.export(path, output_file, post_processor)

    if success:
        # File info
        file_size = Path(output_file).stat().st_size
        print(f"✓ Exported: {output_file}")
        print(f"  Size: {file_size:,} bytes")
        print(f"  Lines: {len(path) + 20}")  # Approximate with header/footer

        # Sample output
        print(f"\n📝 Sample G-code (first 5 moves):")
        with open(output_file, 'r') as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith(';')]
            for line in lines[:5]:
                if 'G0' in line or 'G1' in line:
                    print(f"   {line}")

        print("\n✅ Complete!")
        return 0
    else:
        print("\n❌ Export failed")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
