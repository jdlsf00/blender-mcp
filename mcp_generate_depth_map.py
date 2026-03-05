#!/usr/bin/env python3
"""
MCP Depth Map Generation Script
This script is executed by Blender to generate depth maps using our MCP tools
"""

import bpy
import bmesh
import os
import sys
from mathutils import Vector, Matrix
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DepthMapMCP")

def generate_depth_map_direct(object_name, direction="top", resolution=1024, 
                            output_path=None, format="PNG", invert=False,
                            depth_range=(0.0, 1.0), camera_distance=10.0):
    """
    Generate depth map directly in Blender (MCP tool implementation)
    """
    try:
        logger.info(f"🎯 Starting depth map generation for {object_name}")
        
        # Check if object exists
        if object_name not in bpy.data.objects:
            return {"success": False, "error": f"Object '{object_name}' not found"}
        
        target_obj = bpy.data.objects[object_name]
        logger.info(f"✅ Found object: {target_obj.name}")
        
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
        camera.name = "DepthMapCamera"
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
        
        # Set orthographic scale based on object size
        max_dimension = max(size.x, size.y, size.z)
        camera.data.ortho_scale = max_dimension * 1.2
        
        logger.info(f"📷 Camera positioned for {direction} view")
        
        # Set camera as active
        bpy.context.scene.camera = camera
        
        # Create depth material
        depth_mat = bpy.data.materials.new(name="DepthMapMaterial")
        depth_mat.use_nodes = True
        nodes = depth_mat.node_tree.nodes
        links = depth_mat.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Add nodes for depth calculation
        geometry_node = nodes.new(type='ShaderNodeNewGeometry')
        camera_data_node = nodes.new(type='ShaderNodeCameraData')
        vector_math_node = nodes.new(type='ShaderNodeVectorMath')
        vector_math_node.operation = 'DOT_PRODUCT'
        
        separate_xyz_node = nodes.new(type='ShaderNodeSeparateXYZ')
        map_range_node = nodes.new(type='ShaderNodeMapRange')
        map_range_node.inputs[1].default_value = depth_range[0]  # From Min
        map_range_node.inputs[2].default_value = depth_range[1]  # From Max
        map_range_node.inputs[3].default_value = 0.0  # To Min
        map_range_node.inputs[4].default_value = 1.0  # To Max
        
        if invert:
            invert_node = nodes.new(type='ShaderNodeMath')
            invert_node.operation = 'SUBTRACT'
            invert_node.inputs[0].default_value = 1.0
        
        emission_node = nodes.new(type='ShaderNodeEmission')
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        
        # Link nodes
        links.new(geometry_node.outputs['Position'], separate_xyz_node.inputs['Vector'])
        links.new(separate_xyz_node.outputs['Z'], map_range_node.inputs['Value'])
        
        if invert:
            links.new(map_range_node.outputs['Result'], invert_node.inputs[1])
            links.new(invert_node.outputs['Value'], emission_node.inputs['Color'])
        else:
            links.new(map_range_node.outputs['Result'], emission_node.inputs['Color'])
        
        links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])
        
        # Assign material to object
        if target_obj.data.materials:
            target_obj.data.materials[0] = depth_mat
        else:
            target_obj.data.materials.append(depth_mat)
        
        logger.info("🎨 Depth material created and assigned")
        
        # Set up render settings
        scene = bpy.context.scene
        scene.render.engine = 'CYCLES'
        scene.render.resolution_x = resolution
        scene.render.resolution_y = resolution
        scene.render.image_settings.file_format = format
        
        if format == 'PNG':
            scene.render.image_settings.color_depth = '16'
        elif format == 'TIFF':
            scene.render.image_settings.color_depth = '16'
        elif format == 'EXR':
            scene.render.image_settings.color_depth = '32'
        
        # Set output path
        if not output_path:
            output_path = f"F:/Documents/Blender/depth_map_{object_name}_{direction}_{resolution}.{format.lower()}"
        
        scene.render.filepath = output_path
        
        logger.info(f"🖼️  Rendering depth map at {resolution}x{resolution}")
        
        # Render
        bpy.ops.render.render(write_still=True)
        
        # Clean up
        bpy.data.objects.remove(camera, do_unlink=True)
        bpy.data.materials.remove(depth_mat, do_unlink=True)
        
        # Check if file was created
        if os.path.exists(output_path.replace("F:/", "/mnt/f/")):
            file_size = os.path.getsize(output_path.replace("F:/", "/mnt/f/"))
            logger.info(f"✅ Depth map generated successfully")
            
            return {
                "success": True,
                "output_path": output_path,
                "stats": {
                    "resolution": f"{resolution}x{resolution}",
                    "format": format,
                    "direction": direction,
                    "file_size": f"{file_size:,} bytes",
                    "inverted": invert
                }
            }
        else:
            return {"success": False, "error": "Failed to create output file"}
            
    except Exception as e:
        logger.error(f"❌ Error generating depth map: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Main execution function"""
    print("🎯 MCP Depth Map Generation")
    print("=" * 40)
    
    # Load the demo sculpture
    blend_file = "F:/Documents/Blender/depth_map_demo.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_file)
    print(f"📁 Loaded: {blend_file}")
    
    # Generate the requested depth map
    result = generate_depth_map_direct(
        object_name="DemoSculpture",
        direction="top",
        resolution=1024,
        output_path="F:/Documents/Blender/cnc_depth_map_1024.png",
        format="PNG",
        invert=False,
        depth_range=(0.0, 1.0),
        camera_distance=10.0
    )
    
    print("\n🎯 Depth Map Generation Result:")
    print(f"Success: {result.get('success', False)}")
    print(f"Output: {result.get('output_path', 'None')}")
    print(f"Stats: {result.get('stats', {})}")
    if not result.get('success'):
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print("\n🚀 MCP Depth Map Generation Complete!")

if __name__ == "__main__":
    main()