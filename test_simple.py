#!/usr/bin/env python3
"""
Simple MCP server test within WSL environment
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "blender"))

from blender.mesh_operations import MeshOperations
from blender.material_operations import MaterialOperations
from blender.scene_operations import SceneOperations


def test_blender_operations():
    """Test that our Blender operations work in mock mode"""
    print("🧪 Testing Blender MCP Operations...")
    
    try:
        # Test mesh operations
        print("\n🔧 Testing Mesh Operations:")
        mesh_ops = MeshOperations()
        result = mesh_ops.create_cube("TestCube")
        print(f"  ✅ Create Cube: {result}")
        
        result = mesh_ops.create_sphere("TestSphere", (2, 0, 0))
        print(f"  ✅ Create Sphere: {result}")
        
        # Test material operations  
        print("\n🎨 Testing Material Operations:")
        material_ops = MaterialOperations()
        result = material_ops.create_material("TestMaterial", (1, 0, 0, 1))
        print(f"  ✅ Create Material: {result}")
        
        # Test scene operations
        print("\n🏠 Testing Scene Operations:")
        scene_ops = SceneOperations()
        result = scene_ops.get_scene_objects()
        print(f"  ✅ Scene Objects: {result.split(chr(10))[0]}...")
        
        print("\n✅ All Blender operations work correctly in mock mode!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing operations: {e}")
        return False


def test_mcp_server_import():
    """Test that we can import the MCP server without errors"""
    print("\n🚀 Testing MCP Server Import...")
    
    try:
        # Test importing the server
        sys.path.append(os.path.dirname(__file__))
        import blender_mcp_server
        print("  ✅ MCP server imports successfully")
        
        # Check if server has the expected tools
        if hasattr(blender_mcp_server, 'mcp'):
            print("  ✅ FastMCP server instance found")
            return True
        else:
            print("  ❌ FastMCP server instance not found")
            return False
            
    except Exception as e:
        print(f"  ❌ Error importing MCP server: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🎯 Blender MCP Server Verification Test")
    print("=" * 60)
    
    # Test 1: Blender operations
    operations_ok = test_blender_operations()
    
    # Test 2: MCP server import
    server_ok = test_mcp_server_import()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"  Blender Operations: {'✅ PASS' if operations_ok else '❌ FAIL'}")
    print(f"  MCP Server Import:  {'✅ PASS' if server_ok else '❌ FAIL'}")
    
    if operations_ok and server_ok:
        print("\n🎉 All tests passed! Your MCP server is ready!")
        print("\n💡 Next step: Configure VS Code to detect this server")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    print("=" * 60)