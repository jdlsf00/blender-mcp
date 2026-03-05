#!/usr/bin/env python3
"""
Blender 4-Axis G-code Visualizer

Loads 4-axis G-code and creates an animated visualization in Blender
showing the tool, workpiece, and rotation.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix


def parse_gcode(filepath):
    """Parse G-code file and extract toolpath with A-axis"""
    points = []

    with open(filepath, 'r') as f:
        current_pos = {'X': 0, 'Y': 0, 'Z': 0, 'A': 0}

        for line in f:
            line = line.strip()
            if not line or line.startswith(';') or line.startswith('('):
                continue

            if line.startswith('G0') or line.startswith('G1'):
                parts = line.split()
                for part in parts[1:]:
                    if len(part) < 2:
                        continue
                    axis = part[0].upper()
                    if axis in 'XYZA':
                        try:
                            current_pos[axis] = float(part[1:])
                        except ValueError:
                            pass

                points.append((
                    current_pos['X'],
                    current_pos['Y'],
                    current_pos['Z'],
                    current_pos['A']
                ))

    return points


def create_cylinder_workpiece(diameter, length, name="Workpiece"):
    """Create cylinder workpiece"""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=diameter/2000.0,  # Convert mm to Blender units (meters)
        depth=length/1000.0,
        rotation=(0, math.pi/2, 0),  # Rotate to align with X-axis
        location=(length/2000.0, 0, 0)
    )

    workpiece = bpy.context.active_object
    workpiece.name = name

    # Apply the rotation so the local axes align with global
    # This makes the cylinder's length axis (Z in local space) align with X in global space
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # Add material
    mat = bpy.data.materials.new(name="Workpiece_Material")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.6, 0.4, 1.0)  # Wood color
    mat.node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0.5  # Roughness
    workpiece.data.materials.append(mat)

    return workpiece


def create_tool(diameter, length=50, name="Tool"):
    """Create cutting tool"""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=diameter/2000.0,
        depth=length/1000.0,
        location=(0, 0, 0)
    )

    tool = bpy.context.active_object
    tool.name = name

    # Add material
    mat = bpy.data.materials.new(name="Tool_Material")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.7, 0.7, 0.8, 1.0)  # Metal color
    mat.node_tree.nodes["Principled BSDF"].inputs[6].default_value = 1.0  # Metallic
    mat.node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0.2  # Roughness
    tool.data.materials.append(mat)

    return tool


def create_toolpath_curve(points, name="Toolpath"):
    """Create mesh edges from toolpath points for Blender 4.5+ compatibility"""
    import bmesh

    # Create mesh instead of curve for better Blender 4.5+ compatibility
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()

    # Create vertices and edges
    prev_vert = None
    for x, y, z, a in points:
        # Convert mm to meters and map coordinates
        # G-code: X=along axis, Y=radial distance, Z=centerline offset
        # Blender: X=along axis, Y=centerline offset, Z=radial (up)
        vert = bm.verts.new((x/1000.0, z/1000.0, y/1000.0))
        if prev_vert is not None:
            bm.edges.new([prev_vert, vert])
        prev_vert = vert

    bm.to_mesh(mesh)
    bm.free()

    # Add material - simple red color
    mat = bpy.data.materials.new(name="Toolpath_Material")
    mat.use_nodes = True
    # Find the Principled BSDF node by name
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            # Set Base Color to red
            node.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)
            # Set Emission Color to red
            if 'Emission Color' in node.inputs:
                node.inputs['Emission Color'].default_value = (1.0, 0.0, 0.0, 1.0)
            # Set Emission Strength
            if 'Emission Strength' in node.inputs:
                node.inputs['Emission Strength'].default_value = 2.0
            break
    obj.data.materials.append(mat)

    return obj


def animate_4axis(tool, workpiece, points, frame_step=2):
    """Create animation of 4-axis machining"""
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = len(points) * frame_step

    for i, (x, y, z, a) in enumerate(points):
        frame = i * frame_step + 1

        # Tool position (convert mm to meters)
        # G-code: X=along axis, Y=radial distance, Z=centerline offset
        # Blender (cylinder along X): X=along axis, Y=centerline offset, Z=radial (pointing up)
        # So we map: Blender(X, Y, Z) = GCode(X, Z, Y)
        # Offset tool UP by half its length (25mm) so TIP touches workpiece, not center
        tool_length_offset = 0.025  # 25mm in meters (half of 50mm tool length)
        tool.location = (x/1000.0, z/1000.0, y/1000.0 + tool_length_offset)
        tool.keyframe_insert(data_path="location", frame=frame)

        # Workpiece rotation (A-axis around X-axis - the cylinder's length)
        workpiece.rotation_euler = (math.radians(a), 0, 0)
        workpiece.keyframe_insert(data_path="rotation_euler", frame=frame)

    print(f"✓ Animation created: {len(points)} keyframes")


def setup_scene():
    """Setup Blender scene"""
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Add lighting
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3.0

    # Setup camera
    bpy.ops.object.camera_add(location=(0.3, 0.3, 0.2), rotation=(math.pi/3, 0, math.pi/4))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera

    # Set viewport shading
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'

    return camera


def visualize_gcode(gcode_file, workpiece_diameter=50, workpiece_length=100, tool_diameter=6):
    """Main visualization function"""
    print("\n" + "="*60)
    print("  Blender 4-Axis G-code Visualizer")
    print("="*60)
    print(f"\n📂 Loading: {gcode_file}")

    # Parse G-code
    points = parse_gcode(gcode_file)
    print(f"✓ Loaded {len(points)} toolpath points")

    # Setup scene
    print("\n⏳ Setting up scene...")
    camera = setup_scene()

    # Create objects
    print("⏳ Creating workpiece...")
    workpiece = create_cylinder_workpiece(workpiece_diameter, workpiece_length)

    print("⏳ Creating tool...")
    tool = create_tool(tool_diameter)

    print("⏳ Creating toolpath...")
    toolpath = create_toolpath_curve(points)

    # Animate
    print("⏳ Creating animation...")
    animate_4axis(tool, workpiece, points)

    print("\n✅ Visualization complete!")
    print("\n📺 Controls:")
    print("   - Spacebar: Play/pause animation")
    print("   - Mouse: Rotate view")
    print("   - Scroll: Zoom")
    print("   - Shift+A: Add objects")
    print("\n💾 To render:")
    print("   - F12: Render frame")
    print("   - Ctrl+F12: Render animation")

    return workpiece, tool, toolpath


# Main execution
if __name__ == "__main__":
    import sys
    import os

    # Debug: print all arguments
    print(f"DEBUG: sys.argv = {sys.argv}")
    print(f"DEBUG: len(sys.argv) = {len(sys.argv)}")

    # Find the -- separator and get args after it
    try:
        separator_idx = sys.argv.index('--')
        script_args = sys.argv[separator_idx + 1:]
    except ValueError:
        script_args = []

    print(f"DEBUG: script_args = {script_args}")

    # Get G-code file and output blend file from command line
    if len(script_args) > 0:
        gcode_file = script_args[0]
        output_blend = script_args[1] if len(script_args) > 1 else None
    else:
        # Default file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gcode_file = os.path.join(script_dir, "test_output", "true_4axis_surface.gcode")
        output_blend = None

    if os.path.exists(gcode_file):
        visualize_gcode(gcode_file)

        # Save the .blend file if running in background mode
        if output_blend or bpy.app.background:
            if not output_blend:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                output_blend = os.path.join(script_dir, "4axis_visualization.blend")

            bpy.ops.wm.save_as_mainfile(filepath=output_blend)
            print(f"\n💾 Saved: {output_blend}")
            print(f"   Run 'blender {output_blend}' to view in GUI")
    else:
        print(f"❌ File not found: {gcode_file}")
        print("\nUsage:")
        print("  blender --background --python visualize_4axis_blender.py -- <gcode_file> [output.blend]")
        print("  blender --python visualize_4axis_blender.py -- <gcode_file>  # Opens GUI directly")
