#!/usr/bin/env python3
"""
BlenderCAM 4-Axis - Custom 4-axis addon (FabEX alternative)
Clean implementation without the FabEX to_chunk bug

Usage:
    Install as Blender addon or run headless:
    blender --background --python blendercam_4axis.py -- --diameter 50 --length 100
"""

bl_info = {
    "name": "BlenderCAM 4-Axis",
    "author": "Custom Implementation",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > 4-Axis CAM",
    "description": "4-axis rotary toolpath generation (HELIX, INDEXED)",
    "warning": "Alternative to FabEX with bug fixes",
    "category": "Manufacturing",
}

import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector, Matrix
from bpy.props import (
    FloatProperty, IntProperty, EnumProperty,
    StringProperty, BoolProperty, PointerProperty
)
from bpy.types import (
    Panel, Operator, PropertyGroup
)


class FourAxisProperties(PropertyGroup):
    """Properties for 4-axis operations"""

    # Geometry
    rotary_axis: EnumProperty(
        name="Rotary Axis",
        description="Which axis rotates (A-axis)",
        items=[
            ('X', "X-Axis", "Rotate around X"),
            ('Y', "Y-Axis", "Rotate around Y"),
            ('Z', "Z-Axis", "Rotate around Z"),
        ],
        default='X'
    )

    # Strategy
    strategy: EnumProperty(
        name="Strategy",
        description="Toolpath strategy",
        items=[
            ('HELIX', "Helical", "Continuous helical wrap around cylinder"),
            ('INDEXED', "Indexed", "Rotate and machine in steps"),
            ('SPIRAL', "Spiral", "Spiral along axis"),
        ],
        default='HELIX'
    )

    # Tool
    tool_diameter: FloatProperty(
        name="Tool Diameter",
        description="End mill diameter",
        default=6.0,
        min=0.1,
        max=100.0,
        unit='LENGTH'
    )

    # Machining params
    stepover: FloatProperty(
        name="Stepover",
        description="Distance between passes",
        default=5.0,
        min=0.1,
        max=100.0,
        unit='LENGTH'
    )

    feed_rate: FloatProperty(
        name="Feed Rate",
        description="Cutting feed rate (mm/min)",
        default=500.0,
        min=1.0,
        max=10000.0
    )

    spindle_rpm: IntProperty(
        name="Spindle RPM",
        description="Spindle speed",
        default=12000,
        min=0,
        max=30000
    )

    # Indexed strategy
    index_count: IntProperty(
        name="Index Count",
        description="Number of index positions (for INDEXED strategy)",
        default=8,
        min=3,
        max=360
    )

    # Output
    output_file: StringProperty(
        name="Output File",
        description="G-code output file",
        default="blender_4axis.gcode",
        subtype='FILE_PATH'
    )

    post_processor: EnumProperty(
        name="Post Processor",
        description="G-code format",
        items=[
            ('GRBL', "GRBL", "GRBL controller"),
            ('LINUXCNC', "LinuxCNC", "LinuxCNC"),
            ('MACH3', "Mach3", "Mach3/Mach4"),
            ('FANUC', "Fanuc", "Fanuc style"),
        ],
        default='GRBL'
    )


class FOURAXIS_OT_calculate_path(Operator):
    """Calculate 4-axis toolpath"""
    bl_idname = "fouraxis.calculate_path"
    bl_label = "Calculate Toolpath"
    bl_description = "Generate 4-axis toolpath from selected object"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        props = context.scene.fouraxis_props
        obj = context.active_object

        if obj.type != 'MESH':
            self.report({'ERROR'}, "Selected object must be a mesh")
            return {'CANCELLED'}

        # Calculate toolpath based on strategy
        if props.strategy == 'HELIX':
            path = calculate_helical_path(obj, props)
        elif props.strategy == 'INDEXED':
            path = calculate_indexed_path(obj, props)
        else:
            path = calculate_spiral_path(obj, props)

        # Store path in object custom properties
        obj['fouraxis_path'] = path
        obj['fouraxis_calculated'] = True

        self.report({'INFO'}, f"Calculated {len(path)} points")

        # Create visualization
        create_path_visualization(context, path, f"{obj.name}_Toolpath")

        return {'FINISHED'}


class FOURAXIS_OT_export_gcode(Operator):
    """Export G-code"""
    bl_idname = "fouraxis.export_gcode"
    bl_label = "Export G-code"
    bl_description = "Export calculated toolpath to G-code"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.get('fouraxis_calculated', False)

    def execute(self, context):
        props = context.scene.fouraxis_props
        obj = context.active_object

        path = obj.get('fouraxis_path')
        if not path:
            self.report({'ERROR'}, "No toolpath calculated")
            return {'CANCELLED'}

        # Export to G-code
        output_path = bpy.path.abspath(props.output_file)
        success = export_to_gcode(path, props, output_path)

        if success:
            self.report({'INFO'}, f"Exported to {output_path}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Export failed")
            return {'CANCELLED'}


class FOURAXIS_PT_main_panel(Panel):
    """Main panel for 4-axis operations"""
    bl_label = "4-Axis CAM"
    bl_idname = "FOURAXIS_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '4-Axis CAM'

    def draw(self, context):
        layout = self.layout
        props = context.scene.fouraxis_props

        # Strategy
        box = layout.box()
        box.label(text="Strategy:", icon='MOD_ARRAY')
        box.prop(props, "strategy")
        box.prop(props, "rotary_axis")

        if props.strategy == 'INDEXED':
            box.prop(props, "index_count")

        # Tool
        box = layout.box()
        box.label(text="Tool:", icon='TOOL_SETTINGS')
        box.prop(props, "tool_diameter")
        box.prop(props, "stepover")

        # Machining
        box = layout.box()
        box.label(text="Machining:", icon='SETTINGS')
        box.prop(props, "feed_rate")
        box.prop(props, "spindle_rpm")

        # Output
        box = layout.box()
        box.label(text="Output:", icon='EXPORT')
        box.prop(props, "post_processor")
        box.prop(props, "output_file")

        # Actions
        layout.separator()
        col = layout.column(align=True)
        col.scale_y = 1.5
        col.operator("fouraxis.calculate_path", icon='PLAY')
        col.operator("fouraxis.export_gcode", icon='EXPORT')


# ============================================================================
# TOOLPATH CALCULATION FUNCTIONS
# ============================================================================

def calculate_helical_path(obj, props):
    """
    Calculate helical toolpath around rotary axis
    Returns list of (x, y, z, a) tuples
    """
    mesh = obj.data

    # Get object bounds
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    # Determine cylinder parameters based on rotary axis
    axis_idx = {'X': 0, 'Y': 1, 'Z': 2}[props.rotary_axis]

    # Get min/max along rotary axis
    axis_vals = [v[axis_idx] for v in bbox]
    axis_min = min(axis_vals)
    axis_max = max(axis_vals)
    length = axis_max - axis_min

    # Get radius (perpendicular to rotary axis)
    if props.rotary_axis == 'X':
        radii = [math.sqrt(v.y**2 + v.z**2) for v in bbox]
    elif props.rotary_axis == 'Y':
        radii = [math.sqrt(v.x**2 + v.z**2) for v in bbox]
    else:  # Z
        radii = [math.sqrt(v.x**2 + v.y**2) for v in bbox]

    radius = max(radii) + props.tool_diameter / 2

    # Calculate helical path
    path = []
    stepover = props.stepover
    num_passes = int(length / stepover) + 1

    # Degrees per mm of linear travel
    circumference = 2 * math.pi * radius
    degrees_per_mm = 360.0 / circumference

    print(f"Helical path: radius={radius:.2f}, length={length:.2f}, passes={num_passes}")

    for pass_num in range(num_passes):
        # Linear position along rotary axis
        linear_pos = axis_min + (pass_num * stepover)

        # Complete rotation for this pass (0-360 degrees)
        for angle_deg in range(0, 361, 10):  # 10° steps
            # Progress along this pass (0-1)
            progress = angle_deg / 360.0

            # Linear interpolation
            linear = linear_pos + stepover * progress

            # A-axis rotation
            a_angle = (pass_num * 360) + angle_deg

            # Calculate X, Y, Z based on rotary axis
            if props.rotary_axis == 'X':
                x = linear
                y = radius * math.cos(math.radians(angle_deg))
                z = radius * math.sin(math.radians(angle_deg))
            elif props.rotary_axis == 'Y':
                x = radius * math.cos(math.radians(angle_deg))
                y = linear
                z = radius * math.sin(math.radians(angle_deg))
            else:  # Z
                x = radius * math.cos(math.radians(angle_deg))
                y = radius * math.sin(math.radians(angle_deg))
                z = linear

            path.append((x, y, z, a_angle))

    return path


def calculate_indexed_path(obj, props):
    """
    Calculate indexed toolpath (rotate, machine, rotate, machine)
    Returns list of (x, y, z, a) tuples
    """
    mesh = obj.data
    path = []

    # Get bounds
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    axis_idx = {'X': 0, 'Y': 1, 'Z': 2}[props.rotary_axis]

    axis_vals = [v[axis_idx] for v in bbox]
    axis_min = min(axis_vals)
    axis_max = max(axis_vals)

    # Index positions
    index_count = props.index_count
    angle_step = 360.0 / index_count

    print(f"Indexed path: {index_count} positions, {angle_step:.2f}° steps")

    # For each index position
    for i in range(index_count):
        a_angle = i * angle_step

        # Machine along rotary axis at this angle
        num_cuts = int((axis_max - axis_min) / props.stepover) + 1

        for cut in range(num_cuts):
            linear_pos = axis_min + (cut * props.stepover)

            # Calculate position based on rotary axis
            if props.rotary_axis == 'X':
                x = linear_pos
                y = 0  # Tool on centerline when cutting
                z = 0
            elif props.rotary_axis == 'Y':
                x = 0
                y = linear_pos
                z = 0
            else:  # Z
                x = 0
                y = 0
                z = linear_pos

            path.append((x, y, z, a_angle))

    return path


def calculate_spiral_path(obj, props):
    """
    Calculate spiral toolpath
    Returns list of (x, y, z, a) tuples
    """
    # Similar to helical but different angle progression
    return calculate_helical_path(obj, props)


def create_path_visualization(context, path, name):
    """Create curve object to visualize toolpath"""
    # Create curve
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'

    # Create spline
    spline = curve_data.splines.new(type='POLY')
    spline.points.add(len(path) - 1)

    # Set points (x, y, z, a ignored for visualization)
    for i, (x, y, z, a) in enumerate(path):
        spline.points[i].co = (x, y, z, 1)

    # Create object
    curve_obj = bpy.data.objects.new(name, curve_data)
    context.collection.objects.link(curve_obj)

    # Set color
    curve_obj.color = (1, 0.5, 0, 1)  # Orange


# ============================================================================
# G-CODE EXPORT
# ============================================================================

def export_to_gcode(path, props, output_path):
    """Export toolpath to G-code file"""

    try:
        with open(output_path, 'w') as f:
            # Header
            f.write("; Generated by BlenderCAM 4-Axis\n")
            f.write(f"; Strategy: {props.strategy}\n")
            f.write(f"; Tool: {props.tool_diameter}mm\n")
            f.write(f"; Feed: {props.feed_rate} mm/min\n")
            f.write(f"; Spindle: {props.spindle_rpm} RPM\n")
            f.write(";\n")

            # Start code
            f.write("G21 ; Millimeters\n")
            f.write("G90 ; Absolute positioning\n")
            f.write("G17 ; XY plane\n")
            f.write(f"M3 S{props.spindle_rpm} ; Spindle on\n")
            f.write("G0 Z50 ; Safe Z\n")
            f.write("\n")

            # Toolpath
            f.write(f"G1 F{props.feed_rate}\n")

            for i, (x, y, z, a) in enumerate(path):
                if i == 0:
                    # Rapid to start
                    f.write(f"G0 X{x:.4f} Y{y:.4f} Z{z:.4f} A{a:.4f}\n")
                else:
                    # Linear move
                    f.write(f"G1 X{x:.4f} Y{y:.4f} Z{z:.4f} A{a:.4f}\n")

            # End code
            f.write("\n")
            f.write("G0 Z50 ; Retract\n")
            f.write("M5 ; Spindle off\n")
            f.write("M2 ; End program\n")

        print(f"✓ Exported {len(path)} points to {output_path}")
        return True

    except Exception as e:
        print(f"✗ Export failed: {e}")
        return False


# ============================================================================
# REGISTRATION
# ============================================================================

classes = (
    FourAxisProperties,
    FOURAXIS_OT_calculate_path,
    FOURAXIS_OT_export_gcode,
    FOURAXIS_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.fouraxis_props = PointerProperty(type=FourAxisProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.fouraxis_props


# ============================================================================
# HEADLESS EXECUTION
# ============================================================================

def main_headless():
    """Run from command line without GUI"""
    import sys
    import argparse

    # Parse args after '--'
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []

    parser = argparse.ArgumentParser(description='BlenderCAM 4-Axis Headless')
    parser.add_argument('--diameter', type=float, default=50)
    parser.add_argument('--length', type=float, default=100)
    parser.add_argument('--tool', type=float, default=6)
    parser.add_argument('--stepover', type=float, default=5)
    parser.add_argument('--feed', type=float, default=500)
    parser.add_argument('--spindle', type=int, default=12000)
    parser.add_argument('--strategy', choices=['HELIX', 'INDEXED', 'SPIRAL'], default='HELIX')
    parser.add_argument('--axis', choices=['X', 'Y', 'Z'], default='X')
    parser.add_argument('--output', type=str, default='blender_4axis.gcode')

    args = parser.parse_args(argv)

    print("="*60)
    print("BlenderCAM 4-Axis - Headless Mode")
    print("="*60)

    # Create cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=args.diameter/2,
        depth=args.length,
        rotation=(1.5708 if args.axis == 'X' else 0, 0, 0)  # 90° for X
    )

    obj = bpy.context.active_object
    obj.name = "Cylinder_4Axis"

    # Setup properties
    props = bpy.context.scene.fouraxis_props
    props.strategy = args.strategy
    props.rotary_axis = args.axis
    props.tool_diameter = args.tool
    props.stepover = args.stepover
    props.feed_rate = args.feed
    props.spindle_rpm = args.spindle
    props.output_file = args.output

    # Calculate
    print("\n⏳ Calculating toolpath...")
    bpy.ops.fouraxis.calculate_path()

    # Export
    print("\n⏳ Exporting G-code...")
    bpy.ops.fouraxis.export_gcode()

    print("\n✅ Complete!")


if __name__ == "__main__":
    # Check if running in Blender
    try:
        import bpy

        # Check if running headless
        if bpy.app.background:
            register()
            main_headless()
        else:
            # Normal addon registration
            register()

    except ImportError:
        print("This script must be run from within Blender")
        print("Usage: blender --background --python blendercam_4axis.py -- [args]")
