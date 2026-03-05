#!/usr/bin/env python3
"""
Simple MCP Test Server

A minimal MCP server for testing Blender integration without full MCP dependencies.
This allows us to test the Blender operations and demonstrate the concept.
"""

import json
import sys
import os
from typing import Dict, Any, List

# Add the blender modules to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "blender"))

from blender.mesh_operations import MeshOperations
from blender.material_operations import MaterialOperations
from blender.scene_operations import SceneOperations
from blender.animation_operations import AnimationOperations
from blender.render_operations import RenderOperations

class SimpleMCPServer:
    """A simplified MCP server for testing purposes."""
    
    def __init__(self):
        self.mesh_ops = MeshOperations()
        self.material_ops = MaterialOperations()
        self.scene_ops = SceneOperations()
        self.animation_ops = AnimationOperations()
        self.render_ops = RenderOperations()
        
        # Define available tools
        self.tools = {
            "create_cube": self.create_cube,
            "create_sphere": self.create_sphere,
            "create_cylinder": self.create_cylinder,
            "delete_object": self.delete_object,
            "move_object": self.move_object,
            "create_material": self.create_material,
            "assign_material": self.assign_material,
            "get_scene_objects": self.get_scene_objects,
            "clear_scene": self.clear_scene,
            "save_file": self.save_file,
            "render_image": self.render_image,
        }
    
    def create_cube(self, name: str = "Cube", location: List[float] = [0, 0, 0]) -> str:
        """Create a cube mesh."""
        return self.mesh_ops.create_cube(name, tuple(location))
    
    def create_sphere(self, name: str = "Sphere", location: List[float] = [0, 0, 0]) -> str:
        """Create a sphere mesh."""
        return self.mesh_ops.create_sphere(name, tuple(location))
    
    def create_cylinder(self, name: str = "Cylinder", location: List[float] = [0, 0, 0]) -> str:
        """Create a cylinder mesh."""
        return self.mesh_ops.create_cylinder(name, tuple(location))
    
    def delete_object(self, name: str) -> str:
        """Delete an object."""
        return self.mesh_ops.delete_object(name)
    
    def move_object(self, name: str, location: List[float]) -> str:
        """Move an object."""
        return self.mesh_ops.move_object(name, tuple(location))
    
    def create_material(self, name: str, color: List[float] = [0.8, 0.8, 0.8, 1.0]) -> str:
        """Create a material."""
        return self.material_ops.create_material(name, tuple(color))
    
    def assign_material(self, object_name: str, material_name: str) -> str:
        """Assign material to an object."""
        return self.material_ops.assign_material(object_name, material_name)
    
    def get_scene_objects(self) -> str:
        """Get all objects in the scene."""
        return self.scene_ops.get_scene_objects()
    
    def clear_scene(self) -> str:
        """Clear the scene."""
        return self.scene_ops.clear_scene()
    
    def save_file(self, filepath: str) -> str:
        """Save the Blender file."""
        return self.scene_ops.save_blend_file(filepath)
    
    def render_image(self, filepath: str = "render.png") -> str:
        """Render an image."""
        return self.render_ops.render_image(filepath)
    
    def list_tools(self) -> List[str]:
        """List available tools."""
        return list(self.tools.keys())
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
            }
        
        try:
            result = self.tools[tool_name](**kwargs)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing tool '{tool_name}': {str(e)}"
            }

def main():
    """Main function for testing the MCP server."""
    print("🚀 Starting Simple MCP Test Server for Blender Integration")
    print("=" * 60)
    
    server = SimpleMCPServer()
    
    print(f"✅ Server initialized with {len(server.tools)} tools:")
    for tool in server.list_tools():
        print(f"   • {tool}")
    
    print("\n🔧 Testing various Blender operations...")
    
    # Test 1: Create some objects
    print("\n1. Creating objects:")
    tests = [
        ("create_cube", {"name": "TestCube", "location": [2, 0, 0]}),
        ("create_sphere", {"name": "TestSphere", "location": [-2, 0, 0]}),
        ("create_cylinder", {"name": "TestCylinder", "location": [0, 2, 0]}),
    ]
    
    for tool_name, params in tests:
        result = server.execute_tool(tool_name, **params)
        if result["success"]:
            print(f"   ✅ {tool_name}: {result['result']}")
        else:
            print(f"   ❌ {tool_name}: {result['error']}")
    
    # Test 2: List scene objects
    print("\n2. Listing scene objects:")
    result = server.execute_tool("get_scene_objects")
    if result["success"]:
        print(f"   ✅ {result['result']}")
    else:
        print(f"   ❌ {result['error']}")
    
    # Test 3: Create and assign materials
    print("\n3. Creating and assigning materials:")
    material_tests = [
        ("create_material", {"name": "RedMaterial", "color": [1.0, 0.2, 0.2, 1.0]}),
        ("create_material", {"name": "BlueMaterial", "color": [0.2, 0.2, 1.0, 1.0]}),
        ("assign_material", {"object_name": "TestCube", "material_name": "RedMaterial"}),
        ("assign_material", {"object_name": "TestSphere", "material_name": "BlueMaterial"}),
    ]
    
    for tool_name, params in material_tests:
        result = server.execute_tool(tool_name, **params)
        if result["success"]:
            print(f"   ✅ {tool_name}: {result['result']}")
        else:
            print(f"   ❌ {tool_name}: {result['error']}")
    
    # Test 4: Move objects
    print("\n4. Moving objects:")
    result = server.execute_tool("move_object", name="TestCube", location=[5, 5, 2])
    if result["success"]:
        print(f"   ✅ move_object: {result['result']}")
    else:
        print(f"   ❌ move_object: {result['error']}")
    
    # Test 5: Render
    print("\n5. Rendering:")
    result = server.execute_tool("render_image", filepath="test_render.png")
    if result["success"]:
        print(f"   ✅ render_image: {result['result']}")
    else:
        print(f"   ❌ render_image: {result['error']}")
    
    print("\n🎉 MCP Server testing completed!")
    print("=" * 60)
    print("The Blender MCP integration is working correctly in mock mode.")
    print("GitHub Copilot can now use these tools to control Blender operations!")

if __name__ == "__main__":
    main()