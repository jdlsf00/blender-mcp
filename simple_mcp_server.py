#!/usr/bin/env python3
"""
MINIMAL MCP SERVER FOR BLENDER INTEGRATION
Built from scratch - no dependencies, pure Python implementation
"""

import json
import sys
import subprocess
import os
from typing import Dict, Any, List

class SimpleMCPServer:
    """Minimal MCP server that works without external dependencies"""
    
    def __init__(self):
        self.tools = {
            "create_sphere": {
                "description": "Create a sphere in Blender",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "radius": {"type": "number", "default": 2.0},
                        "location": {"type": "array", "items": {"type": "number"}, "default": [0, 0, 0]},
                        "name": {"type": "string", "default": "Sphere"}
                    }
                }
            },
            "create_cube": {
                "description": "Create a cube in Blender",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "size": {"type": "number", "default": 2.0},
                        "location": {"type": "array", "items": {"type": "number"}, "default": [0, 0, 0]},
                        "name": {"type": "string", "default": "Cube"}
                    }
                }
            },
            "create_material": {
                "description": "Create a material and assign it to an object",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "default": "Material"},
                        "color": {"type": "array", "items": {"type": "number"}, "default": [0.8, 0.2, 0.2]},
                        "object_name": {"type": "string", "default": "Cube"}
                    }
                }
            }
        }
    
    def execute_blender_script(self, script_content: str) -> Dict[str, Any]:
        """Execute a Python script in Blender"""
        try:
            # Write script to temporary file
            script_path = "/tmp/blender_temp_script.py"
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Execute in Blender
            blender_path = "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe"
            cmd = f'powershell.exe -Command "& \\"{blender_path}\\" --background --python {script_path}"'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_sphere(self, radius=2.0, location=[0, 0, 0], name="Sphere"):
        """Create a sphere in Blender"""
        script = f'''
import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    radius={radius},
    location=({location[0]}, {location[1]}, {location[2]})
)

sphere = bpy.context.active_object
sphere.name = "{name}"

# Save file
import os
save_path = "F:\\\\Documents\\\\Blender\\\\{name.lower()}.blend"
os.makedirs("F:\\\\Documents\\\\Blender", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=save_path)

print(f"✅ Created {{sphere.name}} at {{sphere.location}}")
print(f"💾 Saved as: {{save_path}}")
'''
        return self.execute_blender_script(script)
    
    def create_cube(self, size=2.0, location=[0, 0, 0], name="Cube"):
        """Create a cube in Blender"""
        script = f'''
import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create cube
bpy.ops.mesh.primitive_cube_add(
    size={size},
    location=({location[0]}, {location[1]}, {location[2]})
)

cube = bpy.context.active_object
cube.name = "{name}"

# Save file
import os
save_path = "F:\\\\Documents\\\\Blender\\\\{name.lower()}.blend"
os.makedirs("F:\\\\Documents\\\\Blender", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=save_path)

print(f"✅ Created {{cube.name}} at {{cube.location}}")
print(f"💾 Saved as: {{save_path}}")
'''
        return self.execute_blender_script(script)
    
    def create_material(self, name="Material", color=[0.8, 0.2, 0.2], object_name="Cube"):
        """Create and assign a material"""
        script = f'''
import bpy

# Find the object
obj = None
for o in bpy.data.objects:
    if o.name == "{object_name}":
        obj = o
        break

if not obj:
    print(f"❌ Object '{object_name}' not found")
else:
    # Create material
    material = bpy.data.materials.new(name="{name}")
    material.use_nodes = True
    material.node_tree.nodes.clear()
    
    # Add Principled BSDF
    bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = ({color[0]}, {color[1]}, {color[2]}, 1.0)
    
    # Add Material Output
    output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign to object
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)
    
    print(f"✅ Applied material '{{material.name}}' to {{obj.name}}")
    
    # Save file
    import os
    save_path = "F:\\\\Documents\\\\Blender\\\\{object_name.lower()}_with_material.blend"
    os.makedirs("F:\\\\Documents\\\\Blender", exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print(f"💾 Saved as: {{save_path}}")
'''
        return self.execute_blender_script(script)
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        method = request.get("method", "")
        params = request.get("params", {})
        
        if method == "tools/list":
            return {
                "tools": [
                    {"name": name, **info} for name, info in self.tools.items()
                ]
            }
        
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            
            if tool_name == "create_sphere":
                result = self.create_sphere(**arguments)
            elif tool_name == "create_cube":
                result = self.create_cube(**arguments)
            elif tool_name == "create_material":
                result = self.create_material(**arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
            
            return {"content": [{"type": "text", "text": str(result)}]}
        
        return {"error": "Unknown method"}
    
    def run(self):
        """Run the MCP server"""
        print("🚀 Starting Simple MCP Server for Blender...")
        print("📡 Ready to receive GitHub Copilot requests!")
        print("🎯 Available tools: create_sphere, create_cube, create_material")
        
        try:
            while True:
                line = input()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = self.handle_request(request)
                    print(json.dumps(response))
                except json.JSONDecodeError:
                    print(json.dumps({"error": "Invalid JSON"}))
                except Exception as e:
                    print(json.dumps({"error": str(e)}))
                    
        except (EOFError, KeyboardInterrupt):
            print("\n👋 MCP Server shutting down...")

if __name__ == "__main__":
    server = SimpleMCPServer()
    server.run()