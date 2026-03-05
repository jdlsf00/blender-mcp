#!/usr/bin/env python3
"""
3D Surface 4-Axis Generator

Extends 4-axis machining to handle true 3D surfaces (non-rotationally symmetric).
Imports mesh files (STL/OBJ) and generates adaptive toolpaths that vary
based on surface topology at each angular position.

This enables machining of:
- Relief carvings on cylinders
- Figurines with asymmetric features
- Decorative patterns that wrap around
- Faces, characters, ornamental details
"""

import sys
import os
import math
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from true_4axis_generator import (
    ToolConfig, MachineConfig, StrategyConfig, GCodeExporter
)


@dataclass
class MeshSurface:
    """3D mesh surface for non-uniform machining"""
    vertices: np.ndarray  # Nx3 array of vertex positions
    faces: np.ndarray     # Mx3 array of face vertex indices
    bounds: Tuple[float, float, float, float, float, float]  # xmin, xmax, ymin, ymax, zmin, zmax


class Surface3DGenerator:
    """
    Generate 4-axis toolpaths for true 3D surfaces

    Key difference from rotationally symmetric:
    - Analyzes mesh at each angular position
    - Tool depth varies based on actual surface geometry
    - Supports relief carving, non-uniform features
    """

    def __init__(self, mesh: MeshSurface, tool: ToolConfig,
                 machine: MachineConfig, strategy: StrategyConfig):
        self.mesh = mesh
        self.tool = tool
        self.machine = machine
        self.strategy = strategy
        self.tool_radius = tool.diameter / 2.0

    def load_stl(self, filepath: str) -> MeshSurface:
        """Load STL file and extract mesh data"""
        try:
            import trimesh
            mesh = trimesh.load(filepath)

            bounds = mesh.bounds.flatten().tolist()

            return MeshSurface(
                vertices=mesh.vertices,
                faces=mesh.faces,
                bounds=tuple(bounds)
            )
        except ImportError:
            print("❌ Error: trimesh library required for STL import")
            print("   Install: pip install trimesh")
            return None
        except Exception as e:
            print(f"❌ Error loading STL: {e}")
            return None

    def get_surface_height_at_angle(self, x_pos: float, angle_deg: float) -> float:
        """
        Get surface height (radius from axis) at given X position and rotation angle

        This is where 3D surface analysis happens:
        1. Rotate mesh by angle
        2. Find surface point at (x_pos, 0) after rotation
        3. Return radial distance from rotation axis
        """
        angle_rad = math.radians(angle_deg)

        # For now, implement simple ray casting
        # Cast ray from (x_pos, 0, large_z) downward toward axis
        # Find intersection with mesh

        # TODO: Implement proper mesh intersection
        # For demonstration, return a placeholder

        # This is where you'd:
        # 1. Transform mesh by rotation angle
        # 2. Cast ray at x_pos position
        # 3. Find closest intersection point
        # 4. Calculate distance from rotation axis

        # Placeholder: return uniform radius
        return 25.0  # Will be replaced with actual mesh analysis

    def generate_adaptive_toolpath(self) -> List[Tuple[float, float, float, float]]:
        """
        Generate adaptive toolpath that follows 3D surface

        Unlike rotationally symmetric turning:
        - Tool height changes at each angular position
        - Requires dense sampling to capture surface detail
        - Much larger file sizes
        """
        toolpath = []

        # Extract bounds
        xmin, xmax, ymin, ymax, zmin, zmax = self.mesh.bounds
        length = xmax - xmin

        # Safe Z for rapids
        safe_z = self.machine.safe_z

        # Calculate number of passes along X axis
        num_x_steps = int(length / self.strategy.stepover) + 1

        # Calculate angular steps
        angular_step = self.strategy.angular_resolution
        num_angular_steps = int((self.strategy.end_angle - self.strategy.start_angle) / angular_step) + 1

        print(f"\n📊 Adaptive 3D Toolpath Generation:")
        print(f"   X steps: {num_x_steps}")
        print(f"   Angular steps: {num_angular_steps}")
        print(f"   Total points: {num_x_steps * num_angular_steps}")

        # Add header comment
        toolpath.append((0, 0, safe_z, 0))

        # For each X position
        for x_idx in range(num_x_steps):
            x_pos = xmin + (x_idx * self.strategy.stepover)

            # Move to safe Z if starting new pass
            if x_idx > 0:
                toolpath.append((x_pos, 0, safe_z, self.strategy.start_angle))

            # For each angular position
            for angle_idx in range(num_angular_steps):
                angle = self.strategy.start_angle + (angle_idx * angular_step)

                # Get surface height at this position and angle
                surface_radius = self.get_surface_height_at_angle(x_pos, angle)

                # Calculate tool engagement
                engagement_radius = surface_radius + self.tool_radius

                # Tool position (in machine coordinates before rotation)
                x = x_pos
                y = engagement_radius  # Radial distance from axis
                z = 0.0  # At centerline
                a = angle

                toolpath.append((x, y, z, a))

            # Progress indicator
            if x_idx % 10 == 0:
                progress = (x_idx / num_x_steps) * 100
                print(f"   Progress: {progress:.1f}%", end='\r')

        print(f"\n   ✓ Complete: {len(toolpath)} points generated")

        return toolpath


def demonstrate_3d_surface_capability():
    """
    Demonstrate 3D surface generation capability

    Note: This requires mesh analysis libraries (trimesh, numpy-stl)
    For now, shows the structure needed for true 3D machining
    """
    print("\n" + "="*60)
    print("  3D SURFACE 4-AXIS CAPABILITY")
    print("="*60)

    print("\n📋 Current Status:")
    print("   ✓ Rotationally symmetric parts - WORKING")
    print("   ⏳ True 3D surfaces - FRAMEWORK READY")
    print("   ⏳ Mesh analysis - NEEDS IMPLEMENTATION")

    print("\n🔧 Required for True 3D:")
    print("   1. Mesh intersection/ray casting")
    print("   2. Surface analysis at each angle")
    print("   3. Adaptive depth calculation")
    print("   4. Collision detection")

    print("\n📦 Python Libraries Needed:")
    print("   pip install trimesh")
    print("   pip install numpy-stl")
    print("   pip install scipy")

    print("\n🎯 What This Enables:")
    print("   • Relief carvings on turned parts")
    print("   • Asymmetric figurines")
    print("   • Decorative patterns that wrap")
    print("   • Faces, characters, ornamental work")

    print("\n💡 Next Implementation Steps:")
    print("   1. Load STL/OBJ mesh file")
    print("   2. Implement ray-mesh intersection")
    print("   3. Sample surface at (x, angle) grid")
    print("   4. Generate adaptive toolpath")
    print("   5. Add collision avoidance")

    print("\n" + "="*60)


def create_example_usage():
    """Show example code for when 3D capability is complete"""
    example = '''
# Example: Generate toolpath for 3D relief on cylinder

from surface_3d_generator import Surface3DGenerator, MeshSurface

# Load your 3D model (STL/OBJ)
generator = Surface3DGenerator()
mesh = generator.load_stl("models/dragon_relief.stl")

# Configure machining
tool = ToolConfig(diameter=3.0, flutes=4, material="carbide")
machine = MachineConfig(
    feed_rate=400,
    spindle_rpm=18000,
    safe_z=30
)
strategy = StrategyConfig(
    stepover=0.5,           # Fine 0.5mm for detail
    angular_resolution=2.0,  # Dense 2° sampling
    start_angle=0,
    end_angle=360
)

# Generate adaptive toolpath
generator = Surface3DGenerator(mesh, tool, machine, strategy)
toolpath = generator.generate_adaptive_toolpath()

# Export G-code
exporter = GCodeExporter(machine, strategy)
exporter.export(toolpath, "dragon_relief.gcode", "3D Relief - Dragon")

print(f"✓ Generated: {len(toolpath)} points for full 3D surface")
'''

    return example


def main():
    """Main entry point"""
    demonstrate_3d_surface_capability()

    print("\n" + "="*60)
    print("  EXAMPLE CODE")
    print("="*60)
    print(create_example_usage())

    print("\n" + "="*60)
    print("  CURRENT CAPABILITIES")
    print("="*60)
    print("\n✅ READY NOW - Rotationally Symmetric:")
    print("   • Chess pieces")
    print("   • Vases with smooth profiles")
    print("   • Columns, spindles, balusters")
    print("   • Mathematical curves (Bezier, sine, Fibonacci)")

    print("\n🔮 FUTURE - True 3D Surfaces:")
    print("   • Face carvings")
    print("   • Relief sculptures")
    print("   • Ornamental patterns")
    print("   • Character figurines")

    print("\n💡 Recommendation:")
    print("   Test current symmetric capabilities on hardware first,")
    print("   then implement 3D mesh analysis once basic 4-axis proven.")


if __name__ == "__main__":
    main()
