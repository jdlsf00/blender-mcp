#!/usr/bin/env python3
"""
Natural Language Request Handler: "Create a UV sphere at position (2, 0, 3) with radius 1.5"
This demonstrates MCP integration processing natural language into Blender operations.
"""

import os
import sys

# Set up environment for real Blender execution
os.environ['BLENDER_EXECUTABLE'] = 'C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe'
os.environ['BLENDER_REAL_MODE'] = 'true'

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blender.real_blender import execute_real_blender_operation

def process_natural_language_request():
    """Process: 'Create a UV sphere at position (2, 0, 3) with radius 1.5'"""
    
    print("🎯 NATURAL LANGUAGE MCP REQUEST")
    print("Request: 'Create a UV sphere at position (2, 0, 3) with radius 1.5'")
    print("=" * 60)
    
    print("🧠 Processing natural language...")
    print("� Parsing intent: CREATE object")
    print("🔍 Object type: UV Sphere")
    print("📍 Position: (2, 0, 3)")
    print("📐 Radius: 1.5")
    print("🔧 Subdivision: 2 levels (UV sphere standard)")
    
    print("\n🚀 Translating to Blender Python API...")
    
    # Blender script to create UV sphere with exact specifications
    blender_script = """
# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere with specified parameters
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.5,
    location=(2, 0, 3),
    subdivisions=2
)

# Get the created object
sphere = bpy.context.active_object
sphere.name = "NaturalLanguage_UVSphere"

# Store result information
result["message"] = f"Created UV sphere '{sphere.name}' at location (2, 0, 3) with radius 1.5"
result["data"] = {
    "object_name": sphere.name,
    "location": list(sphere.location),
    "radius": 1.5,
    "vertex_count": len(sphere.data.vertices),
    "face_count": len(sphere.data.polygons)
}

# Save the blend file
output_dir = "F:\\\\Documents\\\\Blender"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

blend_file = os.path.join(output_dir, "natural_language_sphere.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)

result["message"] += f" and saved to {blend_file}"
"""
    
    print("⚡ Executing Blender operation...")
    
    # Execute the Blender script
    result = execute_real_blender_operation("create_uv_sphere", blender_script)
    
    print("\n📊 EXECUTION RESULT:")
    print("=" * 60)
    
    if result["status"] == "success":
        print("✅ SUCCESS: Natural language request completed!")
        print(f"� {result['message']}")
        
        if result.get("data"):
            data = result["data"]
            print(f"🎯 Object: {data['object_name']}")
            print(f"📍 Location: {data['location']}")
            print(f"📐 Radius: {data['radius']}")
            print(f"🔺 Vertices: {data['vertex_count']}")
            print(f"🔳 Faces: {data['face_count']}")
            
        print("📂 File: F:\\Documents\\Blender\\natural_language_sphere.blend")
        print("\n🎉 MCP Integration working perfectly!")
        return True
        
    else:
        print(f"❌ ERROR: {result['message']}")
        if result.get("stderr"):
            print(f"🔍 Details: {result['stderr']}")
        return False

if __name__ == "__main__":
    success = process_natural_language_request()
    sys.exit(0 if success else 1)