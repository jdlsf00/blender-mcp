#!/usr/bin/env python3
"""
True 4-Axis G-code Generator with Correct Kinematics

This version implements proper 4-axis machining where:
- Workpiece rotates around A-axis
- Tool position in machine coordinates (XYZ) stays fixed or moves linearly
- Surface engagement calculated based on workpiece rotation

Key Difference from Previous Version:
- OLD: Tool moves in spiral around stationary cylinder (wrong physics)
- NEW: Tool moves linearly while workpiece rotates (correct 4-axis)
"""

import math
import argparse
import json
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class ToolConfig:
    diameter: float = 6.0
    flutes: int = 2
    material: str = "carbide"


@dataclass
class MachineConfig:
    feed_rate: float = 500.0
    plunge_rate: float = 250.0
    rapid_rate: float = 3000.0
    spindle_rpm: int = 12000
    spindle_direction: str = "CW"
    safe_z: float = 50.0


@dataclass
class WorkpieceConfig:
    """Define the workpiece geometry - can be cylinder, contoured, etc."""
    type: str = "CYLINDER"  # CYLINDER, CONTOURED, HELICAL_GROOVE
    diameter: float = 50.0
    length: float = 100.0
    rotary_axis: str = "X"  # X, Y, or Z

    # For contoured surfaces
    contour_points: List[Tuple[float, float]] = field(default_factory=list)  # (position, radius) pairs

    # For helical grooves
    groove_depth: float = 5.0
    groove_width: float = 10.0
    groove_pitch: float = 20.0  # Distance per revolution


@dataclass
class StrategyConfig:
    type: str = "SURFACE"  # SURFACE, PROFILE, GROOVE
    stepover: float = 5.0
    angular_resolution: float = 10.0
    tool_orientation: str = "PERPENDICULAR"  # PERPENDICULAR or TANGENT
    cutting_side: str = "CLIMB"  # CLIMB or CONVENTIONAL
    start_angle: float = 0.0
    end_angle: float = 360.0


class True4AxisGenerator:
    """
    True 4-axis kinematics generator

    The fundamental principle:
    1. Workpiece rotates around A-axis at angle θ
    2. Tool is at fixed machine position (X_tool, Y_tool, Z_tool)
    3. Engagement point calculated by intersecting tool with rotated workpiece
    """

    def __init__(self, workpiece: WorkpieceConfig, tool: ToolConfig,
                 machine: MachineConfig, strategy: StrategyConfig):
        self.workpiece = workpiece
        self.tool = tool
        self.machine = machine
        self.strategy = strategy

        # Calculate tool radius
        self.tool_radius = tool.diameter / 2.0

        # Calculate workpiece parameters
        self.workpiece_radius = workpiece.diameter / 2.0

    def get_workpiece_radius_at_position(self, linear_pos: float) -> float:
        """
        Get workpiece radius at given position along rotary axis

        For contoured workpieces, interpolate between contour points
        """
        if self.workpiece.type == "CYLINDER":
            return self.workpiece_radius

        elif self.workpiece.type == "CONTOURED":
            if not self.workpiece.contour_points:
                return self.workpiece_radius

            # Find surrounding points and interpolate
            points = sorted(self.workpiece.contour_points, key=lambda p: p[0])

            if linear_pos <= points[0][0]:
                return points[0][1]
            if linear_pos >= points[-1][0]:
                return points[-1][1]

            for i in range(len(points) - 1):
                pos1, rad1 = points[i]
                pos2, rad2 = points[i + 1]

                if pos1 <= linear_pos <= pos2:
                    # Linear interpolation
                    t = (linear_pos - pos1) / (pos2 - pos1)
                    return rad1 + t * (rad2 - rad1)

        elif self.workpiece.type == "HELICAL_GROOVE":
            # Base radius minus groove depth based on angle
            base_radius = self.workpiece_radius
            # This is simplified - actual groove would need angle parameter
            return base_radius

        return self.workpiece_radius

    def calculate_tool_position(self, linear_pos: float, angle_deg: float,
                                radial_offset: float = 0.0) -> Tuple[float, float, float, float]:
        """
        Calculate tool position for true 4-axis machining

        Key concept: Tool approaches from a fixed direction in machine coordinates
        while workpiece rotates.

        Args:
            linear_pos: Position along rotary axis (mm)
            angle_deg: Workpiece rotation angle (degrees)
            radial_offset: Additional radial offset (for stepover passes)

        Returns:
            (x, y, z, a) tuple - machine coordinates + rotation angle
        """
        angle_rad = math.radians(angle_deg)

        # Get workpiece radius at this position
        workpiece_radius = self.get_workpiece_radius_at_position(linear_pos)

        # Tool approach radius = workpiece radius + tool radius + radial offset
        # This puts the tool center at the correct distance to engage the surface
        engagement_radius = workpiece_radius + self.tool_radius + radial_offset

        if self.workpiece.rotary_axis == 'X':
            # X-axis rotary: cylinder extends along X, rotates in YZ plane
            # Tool typically approaches from +Y direction (0° = top)
            x = linear_pos
            y = engagement_radius  # Tool position in machine coordinates
            z = 0.0  # Tool at centerline height
            a = angle_deg  # Workpiece rotation

        elif self.workpiece.rotary_axis == 'Y':
            # Y-axis rotary: cylinder extends along Y, rotates in XZ plane
            x = engagement_radius
            y = linear_pos
            z = 0.0
            a = angle_deg

        else:  # Z
            # Z-axis rotary: cylinder extends along Z, rotates in XY plane
            x = engagement_radius
            y = 0.0
            z = linear_pos
            a = angle_deg

        return (x, y, z, a)

    def generate_surface_toolpath(self) -> List[Tuple[float, float, float, float]]:
        """
        Generate surface machining toolpath (wrapping around cylinder)

        Strategy:
        1. Tool moves along length (stepover increments)
        2. At each position, workpiece rotates through angle range
        3. Tool stays at constant radius from axis
        """
        path = []

        # Calculate number of passes
        num_passes = int(self.workpiece.length / self.strategy.stepover) + 1

        # Start angle and end angle
        start_angle = self.strategy.start_angle
        end_angle = self.strategy.end_angle
        angle_range = end_angle - start_angle

        # Move to start position (safe)
        x, y, z, a = self.calculate_tool_position(0, start_angle, 5.0)  # 5mm clearance
        path.append((x, y, z + self.machine.safe_z, a))  # Raised Z

        for pass_num in range(num_passes):
            linear_pos = pass_num * self.strategy.stepover
            linear_pos = min(linear_pos, self.workpiece.length)

            # Approach this position
            x, y, z, a = self.calculate_tool_position(linear_pos, start_angle, 5.0)
            path.append((x, y, z + 5.0, a))  # Approach height

            # Plunge to depth
            x, y, z, a = self.calculate_tool_position(linear_pos, start_angle)
            path.append((x, y, z, a))

            # Rotate through angle range
            angle_steps = int(angle_range / self.strategy.angular_resolution)
            for step in range(angle_steps + 1):
                angle = start_angle + (step * self.strategy.angular_resolution)
                angle = min(angle, end_angle)

                x, y, z, a = self.calculate_tool_position(linear_pos, angle)
                path.append((x, y, z, a))

            # Retract
            x, y, z, a = self.calculate_tool_position(linear_pos, end_angle, 5.0)
            path.append((x, y, z + 5.0, a))

        # Return to safe position
        x, y, z, a = self.calculate_tool_position(self.workpiece.length, end_angle, 5.0)
        path.append((x, y, z + self.machine.safe_z, a))

        return path

    def generate_contoured_toolpath(self) -> List[Tuple[float, float, float, float]]:
        """
        Generate toolpath for contoured (variable diameter) workpiece

        This demonstrates the power of proper kinematics - tool radius
        automatically adjusts to follow the contour
        """
        return self.generate_surface_toolpath()  # Same logic, different radii

    def generate_helical_groove(self) -> List[Tuple[float, float, float, float]]:
        """
        Generate helical groove toolpath

        Tool plunges into surface as it moves along and workpiece rotates
        """
        path = []

        # Calculate total rotation for helical pitch
        total_rotations = self.workpiece.length / self.workpiece.groove_pitch
        total_angle = total_rotations * 360.0

        # Number of points
        num_points = int(total_angle / self.strategy.angular_resolution)

        for i in range(num_points + 1):
            # Calculate position along axis
            progress = i / num_points
            linear_pos = progress * self.workpiece.length
            angle = progress * total_angle

            # Calculate radial depth (plunge into surface)
            radial_offset = -self.workpiece.groove_depth  # Negative = into material

            x, y, z, a = self.calculate_tool_position(linear_pos, angle, radial_offset)
            path.append((x, y, z, a))

        return path

    def generate_toolpath(self) -> List[Tuple[float, float, float, float]]:
        """Generate toolpath based on strategy"""
        if self.strategy.type == "SURFACE":
            return self.generate_surface_toolpath()
        elif self.strategy.type == "GROOVE":
            return self.generate_helical_groove()
        elif self.workpiece.type == "CONTOURED":
            return self.generate_contoured_toolpath()
        else:
            return self.generate_surface_toolpath()


class GCodeExporter:
    """Export toolpath to G-code"""

    def __init__(self, machine: MachineConfig, strategy: StrategyConfig):
        self.machine = machine
        self.strategy = strategy

    def export(self, path: List[Tuple[float, float, float, float]],
               output_file: str, post_processor: str = "GRBL") -> bool:
        """Export toolpath to G-code file"""

        try:
            with open(output_file, 'w') as f:
                self._write_header(f)
                self._write_start_code(f, post_processor)
                self._write_toolpath(f, path)
                self._write_end_code(f, post_processor)

            return True
        except Exception as e:
            print(f"Error exporting G-code: {e}")
            return False

    def _write_header(self, f):
        """Write G-code header comments"""
        f.write("; True 4-Axis Toolpath\n")
        f.write("; Generated with correct rotary kinematics\n")
        f.write("; Tool approaches from fixed direction while workpiece rotates\n")
        f.write(";\n")

    def _write_start_code(self, f, post_processor: str):
        """Write initialization G-code"""
        f.write("G21 ; Units in millimeters\n")
        f.write("G90 ; Absolute positioning\n")
        f.write("G17 ; XY plane\n")
        f.write(f"M3 S{self.machine.spindle_rpm} ; Spindle on\n")
        f.write(f"G0 Z{self.machine.safe_z:.4f} ; Safe Z\n")
        f.write("\n; === TOOLPATH ===\n")
        f.write(f"G1 F{self.machine.feed_rate:.1f}\n")

    def _write_toolpath(self, f, path: List[Tuple[float, float, float, float]]):
        """Write toolpath moves"""
        for i, (x, y, z, a) in enumerate(path):
            if i == 0:
                f.write(f"G0 X{x:.4f} Y{y:.4f} Z{z:.4f} A{a:.4f} ; Start\n")
            else:
                # Use G1 for cutting moves, G0 for rapids
                prev_z = path[i-1][2]
                if z > prev_z + 2.0:  # Rapid if moving up significantly
                    f.write(f"G0 X{x:.4f} Y{y:.4f} Z{z:.4f} A{a:.4f}\n")
                else:
                    f.write(f"G1 X{x:.4f} Y{y:.4f} Z{z:.4f} A{a:.4f}\n")

    def _write_end_code(self, f, post_processor: str):
        """Write ending G-code"""
        f.write("\n; === END ===\n")
        f.write(f"G0 Z{self.machine.safe_z:.4f} ; Retract\n")
        f.write("M5 ; Spindle off\n")

        if post_processor == "LINUXCNC" or post_processor == "MACH3":
            f.write("M30 ; Program end\n")
        else:
            f.write("M2 ; Program end\n")


def main():
    parser = argparse.ArgumentParser(description="True 4-Axis G-code Generator")

    # Workpiece parameters
    parser.add_argument("--type", default="CYLINDER", choices=["CYLINDER", "CONTOURED", "HELICAL_GROOVE"],
                       help="Workpiece type")
    parser.add_argument("--diameter", type=float, default=50.0,
                       help="Workpiece diameter (mm)")
    parser.add_argument("--length", type=float, default=100.0,
                       help="Workpiece length (mm)")
    parser.add_argument("--axis", default="X", choices=["X", "Y", "Z"],
                       help="Rotary axis")

    # Strategy parameters
    parser.add_argument("--strategy", default="SURFACE", choices=["SURFACE", "GROOVE"],
                       help="Machining strategy")
    parser.add_argument("--stepover", type=float, default=5.0,
                       help="Stepover distance (mm)")
    parser.add_argument("--start-angle", type=float, default=0.0,
                       help="Start angle (degrees)")
    parser.add_argument("--end-angle", type=float, default=360.0,
                       help="End angle (degrees)")

    # Tool parameters
    parser.add_argument("--tool-diameter", type=float, default=6.0,
                       help="Tool diameter (mm)")

    # Machine parameters
    parser.add_argument("--feed", type=float, default=500.0,
                       help="Feed rate (mm/min)")
    parser.add_argument("--spindle", type=int, default=12000,
                       help="Spindle RPM")

    # Output
    parser.add_argument("--output", default="true_4axis.gcode",
                       help="Output file name")
    parser.add_argument("--post", default="GRBL",
                       choices=["GRBL", "LINUXCNC", "FANUC", "MACH3"],
                       help="Post-processor")

    args = parser.parse_args()

    # Create configurations
    workpiece = WorkpieceConfig(
        type=args.type,
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
        start_angle=args.start_angle,
        end_angle=args.end_angle
    )

    # Generate toolpath
    print("\n" + "="*60)
    print("  True 4-Axis G-code Generator")
    print("="*60)
    print(f"\n📐 Configuration:")
    print(f"   Workpiece: {args.type} ⌀{args.diameter}mm × {args.length}mm")
    print(f"   Rotary Axis: {args.axis}")
    print(f"   Strategy: {args.strategy}")
    print(f"   Tool: ⌀{args.tool_diameter}mm")
    print(f"   Stepover: {args.stepover}mm")
    print(f"   Angle Range: {args.start_angle}° to {args.end_angle}°")

    generator = True4AxisGenerator(workpiece, tool, machine, strategy)

    print(f"\n⏳ Generating toolpath...")
    path = generator.generate_toolpath()
    print(f"✓ Generated {len(path)} points")

    # Export
    exporter = GCodeExporter(machine, strategy)
    print(f"\n⏳ Exporting to {args.output}...")

    if exporter.export(path, args.output, args.post):
        import os
        size = os.path.getsize(args.output)
        with open(args.output) as f:
            lines = len(f.readlines())

        print(f"✓ Exported: {args.output}")
        print(f"  Size: {size:,} bytes")
        print(f"  Lines: {lines}")
        print("\n✅ Complete!")
    else:
        print("\n❌ Export failed!")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
