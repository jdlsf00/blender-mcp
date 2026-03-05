#!/usr/bin/env python3
"""
Simple Real Blender Test

Test real Blender integration with a simpler approach.
"""

import subprocess
import os

def test_real_blender():
    """Test real Blender with a simple inline script."""
    
    # Simple Blender Python script as a string
    blender_command = """
import bpy

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "MCP_TestCube"

# Create material
material = bpy.data.materials.new(name="MCP_RedMaterial")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (1.0, 0.2, 0.2, 1.0)
cube.data.materials.append(material)

print("SUCCESS: Created red cube with material via GitHub Copilot + MCP")
"""

    print("🧪 Testing Real Blender 4.2 Integration")
    print("=" * 50)
    
    try:
        # Run Blender with inline Python command
        cmd = [
            'powershell.exe', '-Command', 
            f'& "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe" --background --factory-startup --python-expr "{blender_command}"'
        ]
        
        print("Executing Blender with inline Python...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and "SUCCESS:" in result.stdout:
            print("✅ Real Blender integration working!")
            for line in result.stdout.split('\n'):
                if "SUCCESS:" in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ Test failed")
            print(f"Return code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demonstrate_mcp_integration():
    """Show how this integrates with the MCP server."""
    
    print("\n🔗 MCP Integration Summary")  
    print("=" * 50)
    print("✅ Real Blender 4.2 detected and working")
    print("✅ Can execute Python scripts in Blender")
    print("✅ Can create 3D objects and materials")
    print("✅ Ready for MCP server integration")
    
    print("\n🛠️  To enable real Blender mode:")
    print("   1. Set environment variable:")
    print("      BLENDER_EXECUTABLE='C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe'")
    print("      BLENDER_REAL_MODE='true'")
    print("   2. Restart VS Code MCP server")
    print("   3. GitHub Copilot commands will create real 3D objects!")
    
    print("\n🎯 Available MCP Tools (Real Mode):")
    tools = [
        "create_cube → Real cube in Blender",
        "create_sphere → Real sphere in Blender", 
        "create_cylinder → Real cylinder in Blender",
        "create_material → Real PBR material",
        "assign_material → Apply material to object",
        "render_image → Actual rendered image output",
        "save_blend_file → Real .blend file saved"
    ]
    
    for tool in tools:
        print(f"   • {tool}")

def main():
    success = test_real_blender()
    
    if success:
        demonstrate_mcp_integration()
        print("\n🏆 READY FOR REAL BLENDER MCP INTEGRATION!")
    else:
        print("\n❌ Real Blender test failed - using mock mode")

if __name__ == "__main__":
    main()