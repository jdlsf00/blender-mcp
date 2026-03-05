#!/usr/bin/env python3
"""
Direct Blender Sphere Creation Demo
This script demonstrates creating a sphere in Blender using the MCP integration approach.
"""

import subprocess
import sys
import os

def create_blender_sphere():
    """Create a sphere in Blender using direct bpy commands."""
    
    # Check if we're using real Blender or mock mode
    blender_path = "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe"
    use_real_blender = os.path.exists(blender_path.replace("\\", "/"))
    
    if use_real_blender:
        print("🎯 Creating REAL sphere in Blender 4.2!")
        
        # Blender Python script to create a sphere
        blender_script = '''
import bpy

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create a UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.0,
    location=(0.0, 0.0, 0.0),
    segments=32,
    rings=16
)

# Get the created sphere
sphere = bpy.context.active_object
sphere.name = "CopilotSphere"

# Add a basic material
material = bpy.data.materials.new(name="SphereMaterial")
material.use_nodes = True
material.node_tree.nodes.clear()

# Add Principled BSDF
bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.2, 0.6, 1.0, 1.0)  # Blue color
bsdf.inputs['Metallic'].default_value = 0.3
bsdf.inputs['Roughness'].default_value = 0.4

# Add Material Output
output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material to sphere
if sphere.data.materials:
    sphere.data.materials[0] = material
else:
    sphere.data.materials.append(material)

print("✅ Sphere created successfully!")
print(f"   Name: {sphere.name}")
print(f"   Location: {sphere.location}")
print(f"   Material: {material.name}")

# Save the file
bpy.ops.wm.save_as_mainfile(filepath="copilot_sphere.blend")
print("💾 Saved as: copilot_sphere.blend")
'''
        
        # Write the script to a temporary file
        script_file = "/tmp/create_sphere.py"
        with open(script_file, 'w') as f:
            f.write(blender_script)
        
        try:
            # Run Blender with the script
            cmd = f'powershell.exe -Command "& \\"{blender_path}\\" --background --python {script_file}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("🎉 SUCCESS: Sphere created in real Blender!")
                print("\n📊 Blender Output:")
                print(result.stdout)
            else:
                print("❌ Error running Blender:")
                print(result.stderr)
                
        except subprocess.TimeoutExpired:
            print("⏰ Blender operation timed out")
        except Exception as e:
            print(f"❌ Error: {e}")
            
    else:
        print("🎭 Creating MOCK sphere (Blender not available)")
        print("✅ Mock Sphere Created:")
        print("   Name: CopilotSphere")
        print("   Type: UV Sphere")
        print("   Location: (0.0, 0.0, 0.0)")
        print("   Radius: 2.0")
        print("   Segments: 32")
        print("   Rings: 16")
        print("   Material: Blue metallic (0.2, 0.6, 1.0)")
        print("   File: copilot_sphere.blend")

if __name__ == "__main__":
    print("🚀 GITHUB COPILOT → BLENDER SPHERE CREATION")
    print("=" * 50)
    create_blender_sphere()
    print("\n🎯 Sphere creation complete!")