#!/usr/bin/env python3
"""
MCP Depth Map Generation for Real Project File
Generate depth map from jdls_head_01_v2.blend for CNC carving
"""

import bpy
import bmesh
import os
import sys
from mathutils import Vector, Matrix
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ProjectDepthMapMCP")

def generate_project_depth_map(blend_file_path, direction="top", resolution=1024, 
                              output_path=None, format="PNG", invert=False,
                              depth_range=(0.0, 1.0), camera_distance=15.0):
    """
    Generate depth map from real project file for CNC carving
    """
    try:
        logger.info(f"🎯 Loading project file: {blend_file_path}")
        
        # Load the blend file
        bpy.ops.wm.open_mainfile(filepath=blend_file_path)
        logger.info(f"✅ Loaded: {os.path.basename(blend_file_path)}")
        
        # Find the main mesh object (usually the largest or most complex)
        mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.visible_get()]
        
        if not mesh_objects:
            return {"success": False, "error": "No visible mesh objects found in the file"}
        
        # Select the object with the most vertices (likely the main model)
        target_obj = max(mesh_objects, key=lambda obj: len(obj.data.vertices))
        logger.info(f"✅ Selected main object: {target_obj.name} ({len(target_obj.data.vertices)} vertices)")
        
        # Clear existing selection and select target
        bpy.ops.object.select_all(action='DESELECT')
        target_obj.select_set(True)
        bpy.context.view_layer.objects.active = target_obj
        
        # Get object bounds for camera positioning
        bbox = [target_obj.matrix_world @ Vector(corner) for corner in target_obj.bound_box]
        min_coord = Vector((min(v.x for v in bbox), min(v.y for v in bbox), min(v.z for v in bbox)))
        max_coord = Vector((max(v.x for v in bbox), max(v.y for v in bbox), max(v.z for v in bbox)))
        center = (min_coord + max_coord) / 2
        size = max_coord - min_coord
        
        logger.info(f"📐 Object bounds: center={center}, size={size}")
        
        # Create orthographic camera for depth mapping
        bpy.ops.object.camera_add()
        camera = bpy.context.active_object
        camera.name = "CNC_DepthMapCamera"
        camera.data.type = 'ORTHO'
        
        # Position camera based on direction
        camera_positions = {
            'top': (center.x, center.y, center.z + camera_distance),
            'bottom': (center.x, center.y, center.z - camera_distance),
            'front': (center.x, center.y - camera_distance, center.z),
            'back': (center.x, center.y + camera_distance, center.z),
            'left': (center.x - camera_distance, center.y, center.z),
            'right': (center.x + camera_distance, center.y, center.z)
        }
        
        camera_rotations = {
            'top': (0, 0, 0),
            'bottom': (3.14159, 0, 0),
            'front': (1.5708, 0, 0),
            'back': (-1.5708, 0, 0),
            'left': (1.5708, 0, 1.5708),
            'right': (1.5708, 0, -1.5708)
        }
        
        if direction not in camera_positions:
            return {"success": False, "error": f"Invalid direction: {direction}"}
        
        camera.location = camera_positions[direction]
        camera.rotation_euler = camera_rotations[direction]
        
        # Set orthographic scale based on object size with some padding
        max_dimension = max(size.x, size.y, size.z)
        camera.data.ortho_scale = max_dimension * 1.3  # 30% padding for better framing
        
        logger.info(f"📷 Camera positioned for {direction} view (scale: {camera.data.ortho_scale:.2f})")
        
        # Set camera as active
        bpy.context.scene.camera = camera
        
        # Create professional depth material for CNC
        depth_mat = bpy.data.materials.new(name="CNC_DepthMaterial")
        depth_mat.use_nodes = True
        nodes = depth_mat.node_tree.nodes
        links = depth_mat.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Create nodes for precise depth calculation
        geometry_node = nodes.new(type='ShaderNodeNewGeometry')
        separate_xyz_node = nodes.new(type='ShaderNodeSeparateXYZ')
        
        # Map depth values to grayscale for CNC
        map_range_node = nodes.new(type='ShaderNodeMapRange')
        map_range_node.inputs[1].default_value = min_coord.z  # From Min (lowest point)
        map_range_node.inputs[2].default_value = max_coord.z  # From Max (highest point)
        map_range_node.inputs[3].default_value = 0.0  # To Min (black = deepest)
        map_range_node.inputs[4].default_value = 1.0  # To Max (white = highest)
        
        # Optional inversion for engraving vs relief carving
        if invert:
            invert_node = nodes.new(type='ShaderNodeMath')
            invert_node.operation = 'SUBTRACT'
            invert_node.inputs[0].default_value = 1.0
        
        # Emission shader for rendering
        emission_node = nodes.new(type='ShaderNodeEmission')
        emission_node.inputs['Strength'].default_value = 1.0
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        
        # Link nodes for depth calculation
        links.new(geometry_node.outputs['Position'], separate_xyz_node.inputs['Vector'])
        links.new(separate_xyz_node.outputs['Z'], map_range_node.inputs['Value'])
        
        if invert:
            links.new(map_range_node.outputs['Result'], invert_node.inputs[1])
            links.new(invert_node.outputs['Value'], emission_node.inputs['Color'])
        else:
            links.new(map_range_node.outputs['Result'], emission_node.inputs['Color'])
        
        links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])
        
        # Assign material to target object
        if target_obj.data.materials:
            # Replace first material slot
            target_obj.data.materials[0] = depth_mat
        else:
            # Add new material slot
            target_obj.data.materials.append(depth_mat)
        
        logger.info("🎨 CNC depth material created and assigned")
        
        # Configure render settings for CNC precision
        scene = bpy.context.scene
        scene.render.engine = 'CYCLES'
        scene.render.resolution_x = resolution
        scene.render.resolution_y = resolution
        scene.render.image_settings.file_format = format
        
        # Set bit depth for CNC precision
        if format == 'PNG':
            scene.render.image_settings.color_depth = '16'
            scene.render.image_settings.color_mode = 'BW'  # Grayscale for depth
        elif format == 'TIFF':
            scene.render.image_settings.color_depth = '16'
            scene.render.image_settings.color_mode = 'BW'
        elif format == 'EXR':
            scene.render.image_settings.color_depth = '32'
            scene.render.image_settings.color_mode = 'BW'
        
        # Optimize Cycles for depth mapping
        scene.cycles.samples = 128  # Reduced samples for faster depth maps
        scene.cycles.use_denoising = False  # No denoising needed for depth maps
        
        # Set output path
        if not output_path:
            filename = os.path.splitext(os.path.basename(blend_file_path))[0]
            output_path = f"F:/Documents/Blender/{filename}_depth_map_{direction}_{resolution}.{format.lower()}"
        
        scene.render.filepath = output_path
        
        logger.info(f"🖼️  Rendering CNC depth map at {resolution}x{resolution}")
        logger.info(f"💾 Output: {output_path}")
        
        # Render the depth map
        bpy.ops.render.render(write_still=True)
        
        # Clean up temporary objects
        bpy.data.objects.remove(camera, do_unlink=True)
        bpy.data.materials.remove(depth_mat, do_unlink=True)
        
        # Verify output file
        linux_path = output_path.replace("F:/", "/mnt/f/")
        if os.path.exists(linux_path):
            file_size = os.path.getsize(linux_path)
            logger.info(f"✅ CNC depth map generated successfully")
            
            return {
                "success": True,
                "output_path": output_path,
                "linux_path": linux_path,
                "stats": {
                    "source_file": os.path.basename(blend_file_path),
                    "object_name": target_obj.name,
                    "vertices": len(target_obj.data.vertices),
                    "resolution": f"{resolution}x{resolution}",
                    "format": format,
                    "direction": direction,
                    "file_size": f"{file_size:,} bytes",
                    "inverted": invert,
                    "cnc_ready": True
                }
            }
        else:
            return {"success": False, "error": f"Failed to create output file at {output_path}"}
            
    except Exception as e:
        logger.error(f"❌ Error generating depth map: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Main execution function"""
    print("🎯 MCP Project Depth Map Generation")
    print("=" * 50)
    
    # Generate depth map from the specified project file (use Windows path for Blender)
    result = generate_project_depth_map(
        blend_file_path="F:/Documents/Blender/jdls_head_01_v2.blend",
        direction="top",
        resolution=1024,
        output_path="F:/Documents/Blender/jdls_head_v2_cnc_depth_map_1024.png",
        format="PNG",
        invert=False,
        depth_range=(0.0, 1.0),
        camera_distance=15.0
    )
    
    print("\n🎯 CNC Depth Map Generation Result:")
    print(f"Success: {result.get('success', False)}")
    if result.get('success'):
        print(f"Output: {result.get('output_path', 'None')}")
        print(f"Linux Path: {result.get('linux_path', 'None')}")
        print("Stats:")
        for key, value in result.get('stats', {}).items():
            print(f"   {key}: {value}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print("\n🚀 CNC Project Depth Map Generation Complete!")

if __name__ == "__main__":
    main()