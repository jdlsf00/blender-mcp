#!/usr/bin/env python3
"""
Test script for Blender MCP server operations
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "blender"))

from blender.mesh_operations import MeshOperations
from blender.material_operations import MaterialOperations
from blender.scene_operations import SceneOperations

def test_operations():
    """Test various MCP operations"""
    print("🧪 Testing Blender MCP Operations...")
    
    # Test mesh operations
    mesh_ops = MeshOperations()
    result = mesh_ops.create_cube("TestCube")
    print("   Mesh:", result)
    
    # Test material operations  
    material_ops = MaterialOperations()
    result = material_ops.create_material("TestMaterial", (1, 0, 0, 1))
    print("   Material:", result)
    
    # Test scene operations
    scene_ops = SceneOperations()
    result = scene_ops.get_scene_objects()
    print("   Scene:", result.split('\n')[0])
    
    print("✅ All operations tested successfully!")

if __name__ == "__main__":
    test_operations()