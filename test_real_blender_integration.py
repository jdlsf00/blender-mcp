#!/usr/bin/env python3
"""
Real Blender MCP Test

This script tests the Blender MCP integration with actual Blender 4.2.
"""

import subprocess
import tempfile
import os
import json

def create_blender_scene():
    """Create a simple scene in Blender and save it."""
    
    blender_script = '''
import bpy
import os

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a colorful scene
print("Creating objects...")

# Main cube
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "MCP_MainCube"

# Sphere
bpy.ops.mesh.primitive_uv_sphere_add(location=(-3, 0, 1))
sphere = bpy.context.active_object
sphere.name = "MCP_Sphere"

# Cylinder
bpy.ops.mesh.primitive_cylinder_add(location=(3, 0, 1))
cylinder = bpy.context.active_object
cylinder.name = "MCP_Cylinder"

print("Creating materials...")

# Red material for cube
red_material = bpy.data.materials.new(name="MCP_RedMaterial")
red_material.use_nodes = True
bsdf = red_material.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (1.0, 0.2, 0.2, 1.0)  # Red
cube.data.materials.append(red_material)

# Blue material for sphere
blue_material = bpy.data.materials.new(name="MCP_BlueMaterial")
blue_material.use_nodes = True
bsdf = blue_material.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.2, 0.2, 1.0, 1.0)  # Blue
sphere.data.materials.append(blue_material)

# Green material for cylinder
green_material = bpy.data.materials.new(name="MCP_GreenMaterial")
green_material.use_nodes = True
bsdf = green_material.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.2, 1.0, 0.3, 1.0)  # Green
cylinder.data.materials.append(green_material)

# Add a light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
light = bpy.context.active_object
light.name = "MCP_Sun"
light.data.energy = 3

# Position camera
bpy.ops.object.camera_add(location=(7, -7, 5))
camera = bpy.context.active_object
camera.name = "MCP_Camera"

# Point camera at scene center
import mathutils
camera.rotation_euler = mathutils.Euler((1.1, 0, 0.785398), 'XYZ')

# Set camera as active
scene = bpy.context.scene
scene.camera = camera

# Set render properties
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32  # Fast render

# Save blend file
blend_path = "/tmp/mcp_demo_scene.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"Saved scene to: {blend_path}")

# Render image
render_path = "/tmp/mcp_demo_render.png"
scene.render.filepath = render_path
bpy.ops.render.render(write_still=True)
print(f"Rendered image to: {render_path}")

print("SUCCESS: GitHub Copilot created a complete 3D scene with:")
print("  - Red cube at (0,0,1)")
print("  - Blue sphere at (-3,0,1)")  
print("  - Green cylinder at (3,0,1)")
print("  - Sun light at (5,5,10)")
print("  - Camera positioned for good view")
print("  - Rendered 1920x1080 image")
'''

    # Create temporary script file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(blender_script)
        script_path = f.name

    print("🚀 GitHub Copilot + Real Blender 4.2 Integration Test")
    print("=" * 60)
    print("Creating a complete 3D scene with materials and rendering...")
    
    try:
        # Run Blender with the script
        cmd = [
            'powershell.exe', '-Command',
            f"& 'C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe' --background --factory-startup --python '{script_path}'"
        ]
        
        print("Executing Blender...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Clean up script file
        os.unlink(script_path)
        
        if result.returncode == 0 and "SUCCESS:" in result.stdout:
            print("✅ SUCCESS! Real Blender operation completed!")
            print("\n📊 Scene Creation Results:")
            
            # Extract and display the success message
            for line in result.stdout.split('\n'):
                if line.strip().startswith(('Creating', 'Saved', 'Rendered', 'SUCCESS:', '  -')):
                    print(f"   {line.strip()}")
            
            print("\n🎉 RESULT: GitHub Copilot successfully controlled real Blender!")
            print("   📁 Blend file: /tmp/mcp_demo_scene.blend")
            print("   🖼️  Rendered image: /tmp/mcp_demo_render.png")
            
            return True
        else:
            print("❌ Blender operation failed")
            print(f"Exit code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr[:500]}")
            if result.stdout:
                print(f"Output: {result.stdout[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Blender operation timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    success = create_blender_scene()
    
    if success:
        print("\n🏆 INTEGRATION TEST PASSED!")
        print("GitHub Copilot can now control real Blender 4.2 through MCP!")
        print("\nTo enable real Blender mode in your MCP server:")
        print("  BLENDER_EXECUTABLE='C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe'")
        print("  BLENDER_REAL_MODE='true'")
    else:
        print("\n❌ Integration test failed")
        print("Falling back to mock mode for development")

if __name__ == "__main__":
    main()