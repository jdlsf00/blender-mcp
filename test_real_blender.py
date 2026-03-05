#!/usr/bin/env python3
"""
Test Real Blender Integration

This script tests if we can successfully connect to and control the real Blender installation.
"""

import os
import sys
import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_blender_access():
    """Test if Blender is accessible from WSL."""
    
    # Try different possible paths
    blender_paths = [
        "/mnt/c/Program Files/Blender Foundation/Blender 4.2/blender.exe",
        "C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"
    ]
    
    for blender_path in blender_paths:
        print(f"\n🔍 Testing Blender path: {blender_path}")
        
        try:
            # Use cmd.exe to run Windows executable from WSL
            if blender_path.startswith("/mnt/c/"):
                windows_path = blender_path.replace("/mnt/c/", "C:/")
                cmd = ["cmd.exe", "/c", f'"{windows_path}"', "--version"]
            else:
                cmd = [blender_path, "--version"]
            
            print(f"   Command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"   ✅ SUCCESS! Blender found:")
                for line in result.stdout.strip().split('\n')[:3]:  # First 3 lines
                    print(f"      {line}")
                return blender_path
            else:
                print(f"   ❌ Failed (exit code {result.returncode})")
                if result.stderr:
                    print(f"      Error: {result.stderr.strip()}")
                    
        except FileNotFoundError:
            print(f"   ❌ Blender executable not found at path")
        except subprocess.TimeoutExpired:
            print(f"   ❌ Blender command timed out")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def test_simple_blender_operation(blender_path):
    """Test a simple Blender operation."""
    
    print(f"\n🧪 Testing simple Blender operation...")
    
    # Create a simple Python script for Blender
    blender_script = '''
import bpy

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cube
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "MCP_Test_Cube"

# Create a material
material = bpy.data.materials.new(name="MCP_Red_Material")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (1.0, 0.2, 0.2, 1.0)  # Red color

# Assign material to cube
cube.data.materials.append(material)

# Save the file
bpy.ops.wm.save_as_mainfile(filepath="/tmp/mcp_test.blend")

print("SUCCESS: Created cube with red material and saved to /tmp/mcp_test.blend")
'''
    
    try:
        # Write script to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(blender_script)
            script_path = f.name
        
        # Run Blender with the script
        if blender_path.startswith("/mnt/c/"):
            windows_path = blender_path.replace("/mnt/c/", "C:/")
            cmd = ["cmd.exe", "/c", f'"{windows_path}"', "--background", "--factory-startup", "--python", script_path]
        else:
            cmd = [blender_path, "--background", "--factory-startup", "--python", script_path]
        
        print(f"   Executing: {' '.join(cmd[:4])}... (with Python script)")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # Clean up script file
        os.unlink(script_path)
        
        if result.returncode == 0 and "SUCCESS:" in result.stdout:
            print("   ✅ Blender operation completed successfully!")
            print("   📦 Created: Test cube with red material")
            print("   💾 Saved: /tmp/mcp_test.blend")
            return True
        else:
            print(f"   ❌ Blender operation failed (exit code {result.returncode})")
            if result.stderr:
                print(f"      Error output: {result.stderr[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during Blender operation: {e}")
        return False

def main():
    print("🚀 Testing Real Blender Integration")
    print("=" * 50)
    
    # Test 1: Find Blender
    blender_path = test_blender_access()
    
    if not blender_path:
        print("\n❌ RESULT: Could not access Blender")
        print("   Make sure Blender is installed at:")
        print("   C:/Program Files/Blender Foundation/Blender 4.2/blender.exe")
        return False
    
    # Test 2: Simple operation
    success = test_simple_blender_operation(blender_path)
    
    if success:
        print("\n🎉 RESULT: Real Blender integration is working!")
        print("   Ready for MCP integration with actual 3D operations")
        
        # Update environment variable suggestion
        print(f"\n💡 To use real Blender mode, set:")
        print(f"   BLENDER_EXECUTABLE='{blender_path}'")
        print(f"   BLENDER_REAL_MODE='true'")
        
        return True
    else:
        print("\n❌ RESULT: Blender integration test failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)