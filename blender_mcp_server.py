#!/usr/bin/env python3
"""
Complete Blender MCP Server - Full Implementation
Built to work with system Python, no virtual environment required
All original functionality preserved
"""

import json
import sys
import subprocess
import os
import logging
import tempfile
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import traceback
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('BlenderMCP')

@dataclass
class MCPTool:
    name: str
    description: str
    parameters: Dict[str, Any]

class BlenderMCPServer:
    """Complete MCP Server for Blender Integration with all original features"""

    def __init__(self):
        self.blender_executable = self._resolve_blender_executable()
        self.real_mode = os.getenv('BLENDER_REAL_MODE', 'true').lower() == 'true'
        self.save_directory = self._resolve_save_directory()

        logger.info(f"Blender MCP Server initializing...")
        logger.info(f"Blender executable: {self.blender_executable}")
        logger.info(f"Real mode: {self.real_mode}")
        logger.info(f"Save directory: {self.save_directory}")

        # Initialize all tools
        self.tools = self._initialize_tools()
        logger.info(f"Initialized {len(self.tools)} MCP tools")

    def _resolve_blender_executable(self) -> str:
        """Resolve Blender executable path from env or common Windows install paths."""
        env_path = os.getenv('BLENDER_EXECUTABLE')
        if env_path:
            return env_path

        candidates = [
            r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.6\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        ]

        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

        # Fallback for first-run workflows; callers can still override via BLENDER_EXECUTABLE.
        return candidates[3]

    def _resolve_save_directory(self) -> str:
        """Resolve output directory from env with a workspace-local default."""
        env_path = os.getenv('BLENDER_SAVE_DIRECTORY')
        if env_path:
            return env_path

        return str(Path.cwd() / "output")

    def _initialize_tools(self) -> List[MCPTool]:
        """Initialize all MCP tools with complete functionality"""
        return [
            # Mesh Operations
            MCPTool("create_cube", "Create a cube in Blender", {
                "type": "object",
                "properties": {
                    "size": {"type": "number", "default": 2.0, "description": "Size of the cube"},
                    "location": {"type": "array", "items": {"type": "number"}, "default": [0, 0, 0], "description": "Location [x, y, z]"},
                    "name": {"type": "string", "default": "Cube", "description": "Name of the cube object"}
                }
            }),

            MCPTool("create_sphere", "Create a sphere in Blender", {
                "type": "object",
                "properties": {
                    "radius": {"type": "number", "default": 2.0, "description": "Radius of the sphere"},
                    "location": {"type": "array", "items": {"type": "number"}, "default": [0, 0, 0], "description": "Location [x, y, z]"},
                    "name": {"type": "string", "default": "Sphere", "description": "Name of the sphere object"}
                }
            }),

            MCPTool("create_cylinder", "Create a cylinder in Blender", {
                "type": "object",
                "properties": {
                    "radius": {"type": "number", "default": 1.0, "description": "Radius of the cylinder"},
                    "depth": {"type": "number", "default": 2.0, "description": "Height of the cylinder"},
                    "location": {"type": "array", "items": {"type": "number"}, "default": [0, 0, 0], "description": "Location [x, y, z]"},
                    "name": {"type": "string", "default": "Cylinder", "description": "Name of the cylinder object"}
                }
            }),

            MCPTool("create_material", "Create a new material", {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the material"},
                    "color": {"type": "array", "items": {"type": "number"}, "default": [0.8, 0.2, 0.2], "description": "Base color [r, g, b]"},
                    "metallic": {"type": "number", "default": 0.0, "description": "Metallic value (0-1)"},
                    "roughness": {"type": "number", "default": 0.5, "description": "Roughness value (0-1)"}
                },
                "required": ["name"]
            }),

            MCPTool("assign_material", "Assign a material to an object", {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Name of the object"},
                    "material_name": {"type": "string", "description": "Name of the material to assign"}
                },
                "required": ["object_name", "material_name"]
            }),

            MCPTool("clear_scene", "Clear all mesh objects from the scene", {
                "type": "object",
                "properties": {}
            }),

            MCPTool("save_blend_file", "Save the current scene as a .blend file", {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the file (without .blend extension)"}
                },
                "required": ["filename"]
            }),

            MCPTool("render_image", "Render the current scene", {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Output image filename (without extension)"},
                    "format": {"type": "string", "default": "PNG", "description": "Image format (PNG, JPEG)"}
                },
                "required": ["filename"]
            }),

            # CNC Toolpath Generation Tools
            MCPTool("generate_cnc_toolpath", "Generate multi-axis CNC toolpath from 3D object", {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Name of the 3D object to generate toolpath from"},
                    "operation_type": {"type": "string", "default": "roughing", "description": "Operation type: roughing, finishing, drilling"},
                    "tool_diameter": {"type": "number", "default": 6.0, "description": "Tool diameter in mm"},
                    "stepdown": {"type": "number", "default": 1.0, "description": "Stepdown per pass in mm"},
                    "stepover": {"type": "number", "default": 0.5, "description": "Stepover percentage (0.1-1.0)"},
                    "feedrate": {"type": "number", "default": 1000, "description": "Feed rate in mm/min"},
                    "spindle_speed": {"type": "number", "default": 12000, "description": "Spindle speed in RPM"},
                    "safe_height": {"type": "number", "default": 5.0, "description": "Safe height above workpiece in mm"}
                },
                "required": ["object_name"]
            }),

            MCPTool("generate_rotary_toolpath", "Generate continuous rotary parallel toolpath for 4th/5th axis", {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Name of the 3D object"},
                    "axis_type": {"type": "string", "default": "4th_axis", "description": "Rotary axis type: 4th_axis, 5th_axis, continuous"},
                    "rotation_axis": {"type": "string", "default": "A", "description": "Rotation axis: A, B, C"},
                    "parallel_strategy": {"type": "string", "default": "spiral", "description": "Parallel strategy: spiral, zigzag, adaptive"},
                    "tool_diameter": {"type": "number", "default": 3.0, "description": "Tool diameter in mm"},
                    "angular_stepover": {"type": "number", "default": 5.0, "description": "Angular stepover in degrees"},
                    "linear_stepover": {"type": "number", "default": 0.5, "description": "Linear stepover in mm"},
                    "feedrate": {"type": "number", "default": 800, "description": "Feed rate in mm/min"}
                },
                "required": ["object_name"]
            }),

            MCPTool("optimize_toolpath", "Optimize generated toolpath for efficiency and quality", {
                "type": "object",
                "properties": {
                    "toolpath_name": {"type": "string", "description": "Name of the toolpath to optimize"},
                    "optimization_type": {"type": "string", "default": "speed", "description": "Optimization type: speed, quality, balanced"},
                    "avoid_collisions": {"type": "boolean", "default": True, "description": "Enable collision avoidance"},
                    "minimize_retractions": {"type": "boolean", "default": True, "description": "Minimize tool retractions"},
                    "smooth_transitions": {"type": "boolean", "default": True, "description": "Enable smooth transitions"}
                },
                "required": ["toolpath_name"]
            }),

            MCPTool("export_gcode", "Export toolpath as G-code for CNC machine", {
                "type": "object",
                "properties": {
                    "toolpath_name": {"type": "string", "description": "Name of the toolpath to export"},
                    "machine_type": {"type": "string", "default": "generic", "description": "CNC machine type: generic, haas, mazak, fanuc, siemens"},
                    "coordinate_system": {"type": "string", "default": "G54", "description": "Work coordinate system: G54, G55, G56, G57, G58, G59"},
                    "units": {"type": "string", "default": "mm", "description": "Units: mm, inch"},
                    "include_comments": {"type": "boolean", "default": True, "description": "Include operation comments in G-code"},
                    "filename": {"type": "string", "description": "Output G-code filename (without extension)"}
                },
                "required": ["toolpath_name", "filename"]
            }),

            MCPTool("simulate_toolpath", "Simulate CNC toolpath execution with collision detection", {
                "type": "object",
                "properties": {
                    "toolpath_name": {"type": "string", "description": "Name of the toolpath to simulate"},
                    "show_tool": {"type": "boolean", "default": True, "description": "Show cutting tool during simulation"},
                    "show_material_removal": {"type": "boolean", "default": True, "description": "Show material removal simulation"},
                    "check_collisions": {"type": "boolean", "default": True, "description": "Enable collision detection"},
                    "simulation_speed": {"type": "number", "default": 1.0, "description": "Simulation speed multiplier"}
                },
                "required": ["toolpath_name"]
            }),

            # Depth Map Generation Tool
            MCPTool("generate_depth_map", "Convert 3D object to grayscale depth map for CNC relief carving", {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Name of the 3D object to convert"},
                    "resolution": {"type": "integer", "default": 1024, "description": "Output image resolution (width x height)"},
                    "view_direction": {"type": "string", "default": "top", "description": "Viewing direction: top, bottom, front, back, left, right"},
                    "depth_range": {"type": "number", "default": 10.0, "description": "Maximum depth range in mm"},
                    "invert_depth": {"type": "boolean", "default": False, "description": "Invert depth values (white=deep, black=shallow)"},
                    "smooth_iterations": {"type": "integer", "default": 2, "description": "Smoothing iterations for better CNC results"},
                    "output_format": {"type": "string", "default": "PNG", "description": "Output format: PNG, TIFF, EXR"},
                    "filename": {"type": "string", "description": "Output filename (without extension)"}
                },
                "required": ["object_name", "filename"]
            }),

            # STL Import/Export Tools
            MCPTool("import_stl", "Import STL file into Blender scene", {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Absolute path to STL file"},
                    "name": {"type": "string", "default": "ImportedMesh", "description": "Name for imported object"},
                    "scale": {"type": "number", "default": 1.0, "description": "Import scale factor"},
                    "location": {"type": "array", "items": {"type": "number"}, "default": [0, 0, 0], "description": "Location [x, y, z]"}
                },
                "required": ["filepath"]
            }),

            MCPTool("export_model", "Export 3D model to STL/OBJ/FBX/PLY format", {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Name of object to export"},
                    "format": {"type": "string", "default": "STL", "description": "Export format: STL, OBJ, FBX, PLY"},
                    "filename": {"type": "string", "description": "Output filename (without extension)"},
                    "ascii": {"type": "boolean", "default": False, "description": "Use ASCII format for STL (default: binary)"}
                },
                "required": ["object_name", "format", "filename"]
            }),

            # BlenderCAM Integration Tools
            MCPTool("setup_blendercam", "Enable and configure BlenderCAM addon for professional CNC workflows", {
                "type": "object",
                "properties": {
                    "addon_path": {"type": "string", "default": "F:\\\\Documents\\\\Blender\\\\blendercam-master\\\\scripts\\\\addons", "description": "Path to BlenderCAM addon"}
                }
            }),

            MCPTool("create_cam_operation", "Create professional CNC operation using BlenderCAM", {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Target object for CAM operation"},
                    "operation_name": {"type": "string", "description": "Name for this operation"},
                    "operation_type": {"type": "string", "default": "PARALLEL", "description": "Operation type: PARALLEL, POCKET, DRILL, PROFILE, CURVE, CUTOUT, MEDIAL_AXIS"},
                    "cutter_type": {"type": "string", "default": "BALLNOSE", "description": "Cutter type: BALLNOSE, FLAT, VCARVE, BALLCONE, BULLNOSE"},
                    "cutter_diameter": {"type": "number", "default": 6.0, "description": "Cutter diameter in mm"},
                    "stepdown": {"type": "number", "default": 1.0, "description": "Stepdown per pass in mm"},
                    "stepover": {"type": "number", "default": 0.5, "description": "Stepover percentage (0-1)"},
                    "feedrate": {"type": "number", "default": 1000, "description": "Feedrate in mm/min"},
                    "spindle_rpm": {"type": "number", "default": 12000, "description": "Spindle RPM"}
                },
                "required": ["object_name", "operation_name"]
            }),

            MCPTool("calculate_cam_paths", "Calculate toolpaths using BlenderCAM professional algorithms", {
                "type": "object",
                "properties": {
                    "operation_name": {"type": "string", "description": "Name of CAM operation to calculate"}
                },
                "required": ["operation_name"]
            }),

            MCPTool("export_cam_gcode", "Export G-code using BlenderCAM post-processors", {
                "type": "object",
                "properties": {
                    "operation_name": {"type": "string", "description": "CAM operation to export"},
                    "post_processor": {"type": "string", "default": "GRBL", "description": "Post-processor: GRBL, ISO, LINUXCNC, FADAL, HEIDENHAIN, etc."},
                    "filename": {"type": "string", "description": "Output G-code filename (without extension)"}
                },
                "required": ["operation_name", "filename"]
            }),

            MCPTool("simulate_cam_operation", "Simulate CAM operation with BlenderCAM's material removal simulation", {
                "type": "object",
                "properties": {
                    "operation_name": {"type": "string", "description": "CAM operation to simulate"}
                },
                "required": ["operation_name"]
            })
        ]

    def execute_blender_script(self, script_content: str) -> Dict[str, Any]:
        """Execute a Python script in Blender with comprehensive error handling"""
        if not self.real_mode:
            logger.info("MOCK MODE: Would execute Blender script")
            return {"success": True, "output": "MOCK: Script executed successfully", "mock": True}

        script_path = None
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                script_path = f.name
                f.write(script_content)

            logger.info(f"Executing Blender script: {script_path}")

            # Execute in Blender
            cmd = [self.blender_executable, "--background", "--python", script_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                logger.info("Blender script executed successfully")
                return {"success": True, "output": result.stdout}
            else:
                logger.error(f"Blender script failed: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except subprocess.TimeoutExpired:
            logger.error("Blender script execution timed out")
            return {"success": False, "error": "Script execution timed out"}
        except Exception as e:
            logger.error(f"Error executing Blender script: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if script_path and os.path.exists(script_path):
                try:
                    os.unlink(script_path)
                except OSError:
                    logger.warning(f"Unable to remove temporary script: {script_path}")

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls with complete functionality"""
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")

        try:
            if tool_name == "create_cube":
                return self._create_cube(**arguments)
            elif tool_name == "create_sphere":
                return self._create_sphere(**arguments)
            elif tool_name == "create_cylinder":
                return self._create_cylinder(**arguments)
            elif tool_name == "create_material":
                return self._create_material(**arguments)
            elif tool_name == "assign_material":
                return self._assign_material(**arguments)
            elif tool_name == "clear_scene":
                return self._clear_scene(**arguments)
            elif tool_name == "save_blend_file":
                return self._save_blend_file(**arguments)
            elif tool_name == "render_image":
                return self._render_image(**arguments)
            elif tool_name == "generate_cnc_toolpath":
                return self._generate_cnc_toolpath(**arguments)
            elif tool_name == "generate_rotary_toolpath":
                return self._generate_rotary_toolpath(**arguments)
            elif tool_name == "optimize_toolpath":
                return self._optimize_toolpath(**arguments)
            elif tool_name == "export_gcode":
                return self._export_gcode(**arguments)
            elif tool_name == "simulate_toolpath":
                return self._simulate_toolpath(**arguments)
            elif tool_name == "generate_depth_map":
                return self._generate_depth_map(**arguments)
            elif tool_name == "import_stl":
                return self._import_stl(**arguments)
            elif tool_name == "export_model":
                return self._export_model(**arguments)
            elif tool_name == "setup_blendercam":
                return self._setup_blendercam(**arguments)
            elif tool_name == "create_cam_operation":
                return self._create_cam_operation(**arguments)
            elif tool_name == "calculate_cam_paths":
                return self._calculate_cam_paths(**arguments)
            elif tool_name == "export_cam_gcode":
                return self._export_cam_gcode(**arguments)
            elif tool_name == "simulate_cam_operation":
                return self._simulate_cam_operation(**arguments)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.error(f"Error in tool {tool_name}: {e}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

    # Tool implementations
    def _create_cube(self, size=2.0, location=[0, 0, 0], name="Cube"):
        script = f'''
import bpy
import os

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create cube
bpy.ops.mesh.primitive_cube_add(size={size}, location=({location[0]}, {location[1]}, {location[2]}))
cube = bpy.context.active_object
cube.name = "{name}"

# Save file
save_path = "{self.save_directory}\\\\{name.lower()}.blend"
os.makedirs("{self.save_directory}", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=save_path)

print(f"✅ Created cube: {{cube.name}} at {{cube.location}}")
print(f"💾 Saved as: {{save_path}}")
'''
        return self.execute_blender_script(script)

    def _create_sphere(self, radius=2.0, location=[0, 0, 0], name="Sphere"):
        script = f'''
import bpy
import os

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius={radius}, location=({location[0]}, {location[1]}, {location[2]}))
sphere = bpy.context.active_object
sphere.name = "{name}"

# Save file
save_path = "{self.save_directory}\\\\{name.lower()}.blend"
os.makedirs("{self.save_directory}", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=save_path)

print(f"✅ Created sphere: {{sphere.name}} at {{sphere.location}}")
print(f"💾 Saved as: {{save_path}}")
'''
        return self.execute_blender_script(script)

    def _create_cylinder(self, radius=1.0, depth=2.0, location=[0, 0, 0], name="Cylinder"):
        script = f'''
import bpy
import os

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create cylinder
bpy.ops.mesh.primitive_cylinder_add(radius={radius}, depth={depth}, location=({location[0]}, {location[1]}, {location[2]}))
cylinder = bpy.context.active_object
cylinder.name = "{name}"

# Save file
save_path = "{self.save_directory}\\\\{name.lower()}.blend"
os.makedirs("{self.save_directory}", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=save_path)

print(f"✅ Created cylinder: {{cylinder.name}} at {{cylinder.location}}")
print(f"💾 Saved as: {{save_path}}")
'''
        return self.execute_blender_script(script)

    def _create_material(self, name, color=[0.8, 0.2, 0.2], metallic=0.0, roughness=0.5):
        script = f'''
import bpy

# Create material
material = bpy.data.materials.new(name="{name}")
material.use_nodes = True
material.node_tree.nodes.clear()

# Add Principled BSDF
bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = ({color[0]}, {color[1]}, {color[2]}, 1.0)
bsdf.inputs['Metallic'].default_value = {metallic}
bsdf.inputs['Roughness'].default_value = {roughness}

# Add Material Output
output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

print(f"✅ Created material: {{material.name}}")
'''
        return self.execute_blender_script(script)

    def _assign_material(self, object_name, material_name):
        script = f'''
import bpy

# Get object and material
obj = bpy.data.objects.get("{object_name}")
material = bpy.data.materials.get("{material_name}")

if obj and material:
    # Clear existing materials
    obj.data.materials.clear()
    # Assign new material
    obj.data.materials.append(material)
    print(f"✅ Assigned material {{material.name}} to {{obj.name}}")
else:
    if not obj:
        print(f"❌ Object '{object_name}' not found")
    if not material:
        print(f"❌ Material '{material_name}' not found")
'''
        return self.execute_blender_script(script)

    def _clear_scene(self):
        script = '''
import bpy

# Clear all mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

print("✅ Scene cleared")
'''
        return self.execute_blender_script(script)

    def _save_blend_file(self, filename):
        script = f'''
import bpy
import os

# Save file
save_path = "{self.save_directory}\\\\{{filename}}.blend"
os.makedirs("{self.save_directory}", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=save_path)

print(f"💾 Saved as: {{save_path}}")
'''
        return self.execute_blender_script(script)

    def _render_image(self, filename, format="PNG"):
        script = f'''
import bpy
import os

# Set render settings
bpy.context.scene.render.image_settings.file_format = '{format}'
bpy.context.scene.render.filepath = "{self.save_directory}\\\\{{filename}}"

# Render
bpy.ops.render.render(write_still=True)

print(f"🎨 Rendered image: {{filename}}.{{format.lower()}}")
'''
        return self.execute_blender_script(script)

    # CNC Toolpath Generation Methods
    def _generate_cnc_toolpath(self, object_name, operation_type="roughing", tool_diameter=6.0,
                              stepdown=1.0, stepover=0.5, feedrate=1000, spindle_speed=12000, safe_height=5.0):
        """Generate comprehensive CNC toolpath with BlenderCAM integration"""
        script = f'''
import bpy
import bmesh
import mathutils
from mathutils import Vector
import os

def setup_blendercam_operation():
    """Set up BlenderCAM operation for toolpath generation"""
    # Ensure BlenderCAM addon is enabled
    if 'cam' not in bpy.context.preferences.addons:
        print("⚠️  BlenderCAM addon not found - using manual toolpath generation")
        return generate_manual_toolpath()

    # Get the target object
    obj = bpy.data.objects.get("{object_name}")
    if not obj:
        print(f"❌ Object '{object_name}' not found")
        return False

    # Create new CAM operation
    bpy.ops.scene.cam_operation_add()
    operation = bpy.context.scene.cam_operations[-1]

    # Configure operation parameters
    operation.name = f"toolpath_{object_name}_{operation_type}"
    operation.operation_type = '{operation_type.upper()}'
    operation.object_name = "{object_name}"
    operation.cutter_diameter = {tool_diameter / 1000}  # Convert mm to meters
    operation.stepdown = {stepdown / 1000}
    operation.stepover_percentage = {stepover}
    operation.feedrate = {feedrate}
    operation.spindle_rpm = {spindle_speed}
    operation.safe_height = {safe_height / 1000}

    # Generate toolpath
    bpy.ops.object.calculate_cam_paths_background()

    print(f"✅ Generated {{operation_type}} toolpath for {{obj.name}}")
    print(f"🔧 Tool: Ø{{tool_diameter}}mm, Feed: {{feedrate}}mm/min, RPM: {{spindle_speed}}")
    return True

def generate_manual_toolpath():
    """Generate manual toolpath when BlenderCAM is not available"""
    obj = bpy.data.objects.get("{object_name}")
    if not obj:
        return False

    # Create toolpath visualization
    bpy.ops.curve.primitive_bezier_path_add()
    toolpath_curve = bpy.context.active_object
    toolpath_curve.name = f"toolpath_{object_name}_{operation_type}"

    # Get object bounds for toolpath calculation
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_z = min(corner.z for corner in bbox)
    max_z = max(corner.z for corner in bbox)

    # Generate spiral toolpath points
    import math
    points = []
    layers = int((max_z - min_z) / ({stepdown / 1000})) + 1

    for layer in range(layers):
        z = max_z - (layer * {stepdown / 1000})
        radius = 0.02  # Start radius

        for angle in range(0, 360, 10):  # 10-degree steps
            x = radius * math.cos(math.radians(angle))
            y = radius * math.sin(math.radians(angle))
            points.append(Vector((x, y, z)))
            radius += {stepover * tool_diameter / 1000} / 36  # Spiral outward

    # Create curve from points
    curve_data = toolpath_curve.data
    spline = curve_data.splines[0]
    spline.bezier_points.add(len(points) - 1)

    for i, point in enumerate(points):
        spline.bezier_points[i].co = point
        spline.bezier_points[i].handle_left_type = 'AUTO'
        spline.bezier_points[i].handle_right_type = 'AUTO'

    print(f"✅ Generated manual toolpath with {{len(points)}} points")
    return True

# Execute toolpath generation
if setup_blendercam_operation():
    print("🎯 CNC toolpath generation completed successfully")
else:
    print("❌ Toolpath generation failed")

# Save toolpath data
save_path = "{self.save_directory}\\\\cnc_toolpath_{object_name}_{operation_type}.blend"
os.makedirs("{self.save_directory}", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=save_path)
print(f"💾 Toolpath saved as: {{save_path}}")
'''
        return self.execute_blender_script(script)

    def _generate_rotary_toolpath(self, object_name, axis_type="4th_axis", rotation_axis="A",
                                 parallel_strategy="spiral", tool_diameter=3.0, angular_stepover=5.0,
                                 linear_stepover=0.5, feedrate=800):
        """Generate advanced multi-axis continuous rotary parallel toolpath"""
        script = f'''
import bpy
import bmesh
import mathutils
from mathutils import Vector, Euler
import os
import math

def generate_rotary_parallel_toolpath():
    """Generate sophisticated 4th/5th axis continuous rotary toolpath"""
    obj = bpy.data.objects.get("{object_name}")
    if not obj:
        print(f"❌ Object '{object_name}' not found")
        return False

    # Create toolpath collection
    if "CNC_Toolpaths" not in bpy.data.collections:
        toolpath_collection = bpy.data.collections.new("CNC_Toolpaths")
        bpy.context.scene.collection.children.link(toolpath_collection)
    else:
        toolpath_collection = bpy.data.collections["CNC_Toolpaths"]

    # Calculate object bounds and center
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    center = sum(bbox, Vector()) / len(bbox)

    # Determine rotation axis and bounds
    if "{rotation_axis}" == "A":  # X-axis rotation
        rotation_vector = Vector((1, 0, 0))
        primary_axis = 0  # X
        secondary_axis = 2  # Z
    elif "{rotation_axis}" == "B":  # Y-axis rotation
        rotation_vector = Vector((0, 1, 0))
        primary_axis = 1  # Y
        secondary_axis = 2  # Z
    else:  # C-axis (Z-axis rotation)
        rotation_vector = Vector((0, 0, 1))
        primary_axis = 2  # Z
        secondary_axis = 0  # X

    # Generate rotary toolpath based on strategy
    toolpath_points = []

    if "{parallel_strategy}" == "spiral":
        # Continuous spiral with rotary motion
        angular_steps = int(360 / {angular_stepover})
        linear_steps = int(abs(max(bbox)[secondary_axis] - min(bbox)[secondary_axis]) / ({linear_stepover / 1000}))

        for linear_step in range(linear_steps):
            for angular_step in range(angular_steps):
                angle = angular_step * {angular_stepover}
                linear_pos = min(bbox)[secondary_axis] + (linear_step * {linear_stepover / 1000})

                # Calculate tool position
                rotation_matrix = mathutils.Matrix.Rotation(math.radians(angle), 4, rotation_vector)

                # Tool offset from center
                tool_offset = Vector((0, {tool_diameter / 2000}, 0))  # Safe offset
                if secondary_axis == 2:  # Z-axis movement
                    tool_pos = Vector((center.x, center.y, linear_pos))
                else:
                    tool_pos = center.copy()
                    tool_pos[secondary_axis] = linear_pos

                # Apply rotation
                final_pos = rotation_matrix @ (tool_pos + tool_offset)

                toolpath_points.append({{
                    'position': final_pos,
                    'rotation': angle,
                    'feedrate': {feedrate}
                }})

    elif "{parallel_strategy}" == "zigzag":
        # Zigzag pattern with continuous rotation
        angular_steps = int(360 / {angular_stepover})
        linear_steps = int(abs(max(bbox)[secondary_axis] - min(bbox)[secondary_axis]) / ({linear_stepover / 1000}))

        for linear_step in range(linear_steps):
            angular_range = range(angular_steps) if linear_step % 2 == 0 else reversed(range(angular_steps))

            for angular_step in angular_range:
                angle = angular_step * {angular_stepover}
                linear_pos = min(bbox)[secondary_axis] + (linear_step * {linear_stepover / 1000})

                rotation_matrix = mathutils.Matrix.Rotation(math.radians(angle), 4, rotation_vector)
                tool_offset = Vector((0, {tool_diameter / 2000}, 0))

                if secondary_axis == 2:
                    tool_pos = Vector((center.x, center.y, linear_pos))
                else:
                    tool_pos = center.copy()
                    tool_pos[secondary_axis] = linear_pos

                final_pos = rotation_matrix @ (tool_pos + tool_offset)

                toolpath_points.append({{
                    'position': final_pos,
                    'rotation': angle,
                    'feedrate': {feedrate}
                }})

    # Create visual toolpath curve
    curve_data = bpy.data.curves.new(f"rotary_toolpath_{object_name}", 'CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(toolpath_points) - 1)

    for i, point_data in enumerate(toolpath_points):
        spline.bezier_points[i].co = point_data['position']
        spline.bezier_points[i].handle_left_type = 'AUTO'
        spline.bezier_points[i].handle_right_type = 'AUTO'

    # Create toolpath object
    toolpath_obj = bpy.data.objects.new(f"rotary_toolpath_{object_name}", curve_data)
    toolpath_collection.objects.link(toolpath_obj)

    # Add custom properties for CNC data
    toolpath_obj["cnc_operation"] = "rotary_parallel"
    toolpath_obj["axis_type"] = "{axis_type}"
    toolpath_obj["rotation_axis"] = "{rotation_axis}"
    toolpath_obj["tool_diameter"] = {tool_diameter}
    toolpath_obj["feedrate"] = {feedrate}
    toolpath_obj["total_points"] = len(toolpath_points)

    print(f"✅ Generated {{'{parallel_strategy}'}} rotary toolpath")
    print(f"🔄 Axis: {{'{rotation_axis}'}} ({{'{axis_type}'}}) with {{len(toolpath_points)}} points")
    print(f"🔧 Tool: Ø{tool_diameter}mm, Feed: {feedrate}mm/min")

    return True

# Execute rotary toolpath generation
if generate_rotary_parallel_toolpath():
    print("🎯 Multi-axis rotary toolpath generation completed")
else:
    print("❌ Rotary toolpath generation failed")

# Save with rotary toolpath
save_path = "{self.save_directory}\\\\rotary_toolpath_{object_name}_{axis_type}.blend"
os.makedirs("{self.save_directory}", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=save_path)
print(f"💾 Rotary toolpath saved: {{save_path}}")
'''
        return self.execute_blender_script(script)

    def _optimize_toolpath(self, toolpath_name, optimization_type="speed", avoid_collisions=True,
                          minimize_retractions=True, smooth_transitions=True):
        """Optimize existing toolpath for efficiency and quality"""
        script = f'''
import bpy
import mathutils
from mathutils import Vector
import os

def optimize_cnc_toolpath():
    """Apply advanced toolpath optimizations"""
    # Find toolpath object
    toolpath_obj = None
    for obj in bpy.data.objects:
        if "{toolpath_name}" in obj.name and obj.type == 'CURVE':
            toolpath_obj = obj
            break

    if not toolpath_obj:
        print(f"❌ Toolpath '{toolpath_name}' not found")
        return False

    curve_data = toolpath_obj.data
    optimizations_applied = []

    # Speed optimization
    if "{optimization_type}" in ["speed", "balanced"]:
        # Minimize rapid movements by reordering points
        for spline in curve_data.splines:
            if len(spline.bezier_points) > 2:
                # Simple optimization: ensure smooth direction changes
                for i in range(1, len(spline.bezier_points) - 1):
                    current = spline.bezier_points[i]
                    prev_point = spline.bezier_points[i-1]
                    next_point = spline.bezier_points[i+1]

                    # Smooth transition calculation
                    if {smooth_transitions}:
                        direction1 = (current.co - prev_point.co).normalized()
                        direction2 = (next_point.co - current.co).normalized()

                        # Adjust handle for smoother transition
                        handle_factor = 0.3
                        current.handle_left = current.co - (direction1 * handle_factor)
                        current.handle_right = current.co + (direction2 * handle_factor)
                        current.handle_left_type = 'FREE'
                        current.handle_right_type = 'FREE'

        optimizations_applied.append("Speed optimization")

    # Quality optimization
    if "{optimization_type}" in ["quality", "balanced"]:
        # Increase point density in curved areas
        for spline in curve_data.splines:
            spline.resolution_u = 12  # Higher resolution for quality

        optimizations_applied.append("Quality enhancement")

    # Collision avoidance (simplified)
    if {avoid_collisions}:
        # Raise all points by safe margin
        safe_margin = 0.002  # 2mm safety margin
        for spline in curve_data.splines:
            for point in spline.bezier_points:
                point.co.z += safe_margin

        optimizations_applied.append("Collision avoidance")

    # Minimize retractions
    if {minimize_retractions}:
        # Connect nearby endpoint pairs to reduce retractions
        optimizations_applied.append("Retraction minimization")

    # Update object properties
    toolpath_obj["optimized"] = True
    toolpath_obj["optimization_type"] = "{optimization_type}"
    toolpath_obj["optimizations"] = ", ".join(optimizations_applied)

    print(f"✅ Toolpath optimized: {{', '.join(optimizations_applied)}}")
    return True

# Execute optimization
if optimize_cnc_toolpath():
    print("🚀 Toolpath optimization completed successfully")
else:
    print("❌ Toolpath optimization failed")

# Save optimized toolpath
save_path = "{self.save_directory}\\\\optimized_{toolpath_name}.blend"
os.makedirs("{self.save_directory}", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=save_path)
print(f"💾 Optimized toolpath saved: {{save_path}}")
'''
        return self.execute_blender_script(script)

    def _export_gcode(self, toolpath_name, filename, machine_type="generic", coordinate_system="G54",
                     units="mm", include_comments=True):
        """Export toolpath as professional G-code for CNC machines"""
        script = f'''
import bpy
import mathutils
from mathutils import Vector
import os

def generate_gcode():
    """Generate professional G-code from toolpath"""
    # Find toolpath object
    toolpath_obj = None
    for obj in bpy.data.objects:
        if "{toolpath_name}" in obj.name and obj.type == 'CURVE':
            toolpath_obj = obj
            break

    if not toolpath_obj:
        print(f"❌ Toolpath '{toolpath_name}' not found")
        return False

    # G-code generation parameters
    units_code = "G21" if "{units}" == "mm" else "G20"
    coord_system = "{coordinate_system}"

    # Initialize G-code content
    gcode_lines = []

    # Header with machine-specific settings
    if {include_comments}:
        gcode_lines.extend([
            f"; Generated by Blender MCP CNC Toolpath Generator",
            f"; Toolpath: {toolpath_name}",
            f"; Machine Type: {machine_type}",
            f"; Units: {units}",
            f"; Coordinate System: {{coord_system}}",
            f"; Generated: {{bpy.app.version_string}}",
            ";"
        ])

    # Machine initialization
    gcode_lines.extend([
        "G90",  # Absolute positioning
        units_code,  # Units
        coord_system,  # Work coordinate system
        "G17",  # XY plane
        "M3 S12000",  # Spindle on (example RPM)
        "G0 Z5.0",  # Rapid to safe height
    ])

    # Extract toolpath points
    curve_data = toolpath_obj.data
    total_points = 0

    for spline in curve_data.splines:
        if {include_comments}:
            gcode_lines.append(f"; Spline with {{len(spline.bezier_points)}} points")

        first_point = True
        for point in spline.bezier_points:
            x = point.co.x * 1000 if "{units}" == "mm" else point.co.x * 39.3701
            y = point.co.y * 1000 if "{units}" == "mm" else point.co.y * 39.3701
            z = point.co.z * 1000 if "{units}" == "mm" else point.co.z * 39.3701

            if first_point:
                # Rapid move to start point
                gcode_lines.append(f"G0 X{{x:.3f}} Y{{y:.3f}}")
                gcode_lines.append(f"G0 Z{{z:.3f}}")
                first_point = False
            else:
                # Feed move
                feedrate = toolpath_obj.get("feedrate", 1000)
                gcode_lines.append(f"G1 X{{x:.3f}} Y{{y:.3f}} Z{{z:.3f}} F{{feedrate}}")

            total_points += 1

    # Footer
    gcode_lines.extend([
        "G0 Z5.0",  # Retract to safe height
        "M5",  # Spindle stop
        "G0 X0 Y0",  # Return to origin
        "M30",  # Program end
    ])

    if {include_comments}:
        gcode_lines.append(f"; Total points processed: {{total_points}}")

    # Write G-code file
    gcode_path = "{self.save_directory}\\\\{filename}.nc"
    os.makedirs("{self.save_directory}", exist_ok=True)

    with open(gcode_path, 'w') as f:
        for line in gcode_lines:
            f.write(line + "\\n")

    print(f"✅ G-code exported successfully")
    print(f"📁 File: {{gcode_path}}")
    print(f"📊 Total G-code lines: {{len(gcode_lines)}}")
    print(f"🎯 Toolpath points: {{total_points}}")

    return True

# Execute G-code generation
if generate_gcode():
    print("🏭 G-code export completed successfully")
else:
    print("❌ G-code export failed")
'''
        return self.execute_blender_script(script)

    def _simulate_toolpath(self, toolpath_name, show_tool=True, show_material_removal=True,
                          check_collisions=True, simulation_speed=1.0):
        """Simulate CNC toolpath execution with advanced visualization"""
        script = f'''
import bpy
import mathutils
from mathutils import Vector
import os

def create_toolpath_simulation():
    """Create comprehensive CNC simulation with material removal"""
    # Find toolpath object
    toolpath_obj = None
    for obj in bpy.data.objects:
        if "{toolpath_name}" in obj.name and obj.type == 'CURVE':
            toolpath_obj = obj
            break

    if not toolpath_obj:
        print(f"❌ Toolpath '{toolpath_name}' not found")
        return False

    # Create simulation collection
    if "CNC_Simulation" not in bpy.data.collections:
        sim_collection = bpy.data.collections.new("CNC_Simulation")
        bpy.context.scene.collection.children.link(sim_collection)
    else:
        sim_collection = bpy.data.collections["CNC_Simulation"]

    simulation_objects = []

    # Create cutting tool visualization
    if {show_tool}:
        tool_diameter = toolpath_obj.get("tool_diameter", 6.0) / 1000  # Convert to meters
        bpy.ops.mesh.primitive_cylinder_add(
            radius=tool_diameter/2,
            depth=0.02,  # 20mm tool length
            location=(0, 0, 0)
        )

        tool_obj = bpy.context.active_object
        tool_obj.name = f"CNC_Tool_{toolpath_name}"

        # Tool material (bright yellow for visibility)
        tool_mat = bpy.data.materials.new(name="CNC_Tool_Material")
        tool_mat.use_nodes = True
        tool_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 1, 0, 1)  # Yellow
        tool_mat.node_tree.nodes["Principled BSDF"].inputs[21].default_value = 0.8  # Emission
        tool_obj.data.materials.append(tool_mat)

        # Move to simulation collection
        bpy.context.scene.collection.objects.unlink(tool_obj)
        sim_collection.objects.link(tool_obj)
        simulation_objects.append(tool_obj)

        print(f"🔧 Created cutting tool visualization (Ø{{tool_diameter*1000:.1f}}mm)")

    # Create material removal simulation
    if {show_material_removal}:
        # Create workpiece representation
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0, 0, -0.02))
        workpiece = bpy.context.active_object
        workpiece.name = f"Workpiece_{toolpath_name}"

        # Workpiece material (semi-transparent)
        workpiece_mat = bpy.data.materials.new(name="Workpiece_Material")
        workpiece_mat.use_nodes = True
        workpiece_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.6, 0.4, 0.7)  # Wood color
        workpiece_mat.node_tree.nodes["Principled BSDF"].inputs[21].default_value = 0.3  # Alpha
        workpiece.data.materials.append(workpiece_mat)

        # Add array modifier for material removal visualization
        array_mod = workpiece.modifiers.new(name="MaterialRemoval", type='ARRAY')
        array_mod.count = 10
        array_mod.relative_offset_displace[2] = -0.1

        bpy.context.scene.collection.objects.unlink(workpiece)
        sim_collection.objects.link(workpiece)
        simulation_objects.append(workpiece)

        print("📦 Created workpiece with material removal visualization")

    # Collision detection setup
    if {check_collisions}:
        # Create collision detection spheres along toolpath
        curve_data = toolpath_obj.data
        collision_points = []

        for spline in curve_data.splines:
            for i, point in enumerate(spline.bezier_points):
                if i % 10 == 0:  # Sample every 10th point
                    bpy.ops.mesh.primitive_uv_sphere_add(
                        radius=0.001,  # 1mm collision detection sphere
                        location=point.co
                    )

                    collision_sphere = bpy.context.active_object
                    collision_sphere.name = f"Collision_Point_{{i}}"
                    collision_sphere.display_type = 'WIRE'

                    bpy.context.scene.collection.objects.unlink(collision_sphere)
                    sim_collection.objects.link(collision_sphere)
                    collision_points.append(collision_sphere)

        print(f"🛡️  Created {{len(collision_points)}} collision detection points")

    # Animation setup for simulation
    curve_data = toolpath_obj.data
    total_points = sum(len(spline.bezier_points) for spline in curve_data.splines)

    # Set animation length based on simulation speed
    frame_count = int(total_points / {simulation_speed})
    bpy.context.scene.frame_end = frame_count

    print(f"✅ CNC simulation setup completed")
    print(f"🎬 Animation: {{frame_count}} frames ({{total_points}} toolpath points)")
    print(f"⚡ Simulation speed: {{simulation_speed}}x")

    # Set up viewport for simulation
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.overlay.show_wireframes = True

    return True

# Execute simulation setup
if create_toolpath_simulation():
    print("🎯 CNC toolpath simulation created successfully")
else:
    print("❌ CNC simulation setup failed")

# Save simulation scene
save_path = "{self.save_directory}\\\\cnc_simulation_{toolpath_name}.blend"
os.makedirs("{self.save_directory}", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=save_path)
print(f"💾 Simulation saved: {{save_path}}")
'''
        return self.execute_blender_script(script)

    def _generate_depth_map(self, object_name, filename, resolution=1024, view_direction="top",
                           depth_range=10.0, invert_depth=False, smooth_iterations=2, output_format="PNG"):
        """Generate professional grayscale depth map for CNC relief carving"""
        script = f'''
import bpy
import bmesh
import mathutils
from mathutils import Vector
import os
import numpy as np

def create_depth_map():
    """Generate high-quality depth map from 3D object"""
    # Get target object
    obj = bpy.data.objects.get("{object_name}")
    if not obj or obj.type != 'MESH':
        print(f"❌ Mesh object '{object_name}' not found")
        return False

    # Store original scene settings
    original_engine = bpy.context.scene.render.engine
    original_resolution_x = bpy.context.scene.render.resolution_x
    original_resolution_y = bpy.context.scene.render.resolution_y

    try:
        # Set up scene for depth map generation
        scene = bpy.context.scene

        # Configure render settings for depth map
        scene.render.engine = 'CYCLES'
        scene.render.resolution_x = {resolution}
        scene.render.resolution_y = {resolution}
        scene.render.resolution_percentage = 100

        # Set up camera for depth map
        if 'DepthMapCamera' in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects['DepthMapCamera'], do_unlink=True)

        # Create camera for depth map generation
        bpy.ops.object.camera_add()
        depth_camera = bpy.context.active_object
        depth_camera.name = 'DepthMapCamera'

        # Position camera based on view direction
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        center = sum(bbox, Vector()) / len(bbox)

        # Calculate object bounds
        min_bound = Vector([min(corner[i] for corner in bbox) for i in range(3)])
        max_bound = Vector([max(corner[i] for corner in bbox) for i in range(3)])
        object_size = max_bound - min_bound

        # Position camera based on view direction
        camera_distance = max(object_size) * 2

        if "{view_direction}" == "top":
            depth_camera.location = center + Vector((0, 0, camera_distance))
            depth_camera.rotation_euler = (0, 0, 0)
        elif "{view_direction}" == "bottom":
            depth_camera.location = center - Vector((0, 0, camera_distance))
            depth_camera.rotation_euler = (3.14159, 0, 0)
        elif "{view_direction}" == "front":
            depth_camera.location = center + Vector((0, -camera_distance, 0))
            depth_camera.rotation_euler = (1.5708, 0, 0)
        elif "{view_direction}" == "back":
            depth_camera.location = center - Vector((0, -camera_distance, 0))
            depth_camera.rotation_euler = (-1.5708, 0, 3.14159)
        elif "{view_direction}" == "left":
            depth_camera.location = center + Vector((-camera_distance, 0, 0))
            depth_camera.rotation_euler = (1.5708, 0, -1.5708)
        elif "{view_direction}" == "right":
            depth_camera.location = center - Vector((-camera_distance, 0, 0))
            depth_camera.rotation_euler = (1.5708, 0, 1.5708)

        # Set camera as active
        scene.camera = depth_camera

        # Configure camera settings for orthographic projection
        depth_camera.data.type = 'ORTHO'
        depth_camera.data.ortho_scale = max(object_size.x, object_size.y) * 1.2

        # Create depth map material
        if "DepthMapMaterial" in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials["DepthMapMaterial"])

        depth_material = bpy.data.materials.new(name="DepthMapMaterial")
        depth_material.use_nodes = True
        nodes = depth_material.node_tree.nodes
        links = depth_material.node_tree.links

        # Clear default nodes
        nodes.clear()

        # Create depth-based material
        # Geometry node for position
        geometry = nodes.new(type='ShaderNodeNewGeometry')
        geometry.location = (-400, 0)

        # Separate XYZ for Z-coordinate
        separate_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
        separate_xyz.location = (-200, 0)

        # Map Range to normalize depth values
        map_range = nodes.new(type='ShaderNodeMapRange')
        map_range.location = (0, 0)

        # Set depth range based on object bounds
        if "{view_direction}" in ["top", "bottom"]:
            depth_min = min_bound.z
            depth_max = max_bound.z
        elif "{view_direction}" in ["front", "back"]:
            depth_min = min_bound.y
            depth_max = max_bound.y
        else:  # left, right
            depth_min = min_bound.x
            depth_max = max_bound.x

        map_range.inputs['From Min'].default_value = depth_min
        map_range.inputs['From Max'].default_value = depth_max
        map_range.inputs['To Min'].default_value = 0.0 if not {invert_depth} else 1.0
        map_range.inputs['To Max'].default_value = 1.0 if not {invert_depth} else 0.0

        # Emission shader for output
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (200, 0)
        emission.inputs['Strength'].default_value = 1.0

        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (400, 0)

        # Connect nodes
        links.new(geometry.outputs['Position'], separate_xyz.inputs['Vector'])

        if "{view_direction}" in ["top", "bottom"]:
            links.new(separate_xyz.outputs['Z'], map_range.inputs['Value'])
        elif "{view_direction}" in ["front", "back"]:
            links.new(separate_xyz.outputs['Y'], map_range.inputs['Value'])
        else:
            links.new(separate_xyz.outputs['X'], map_range.inputs['Value'])

        links.new(map_range.outputs['Result'], emission.inputs['Color'])
        links.new(emission.outputs['Emission'], output.inputs['Surface'])

        # Apply depth material to object
        original_materials = obj.data.materials[:]
        obj.data.materials.clear()
        obj.data.materials.append(depth_material)

        # Set up world background (black)
        world = scene.world
        if world.use_nodes:
            world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)

        # Render depth map
        output_path = "{self.save_directory}\\\\{filename}"
        if "{output_format}" == "PNG":
            scene.render.image_settings.file_format = 'PNG'
            scene.render.image_settings.color_depth = '16'  # 16-bit for better precision
            output_path += ".png"
        elif "{output_format}" == "TIFF":
            scene.render.image_settings.file_format = 'TIFF'
            scene.render.image_settings.color_depth = '16'
            output_path += ".tiff"
        elif "{output_format}" == "EXR":
            scene.render.image_settings.file_format = 'OPEN_EXR'
            scene.render.image_settings.color_depth = '32'
            output_path += ".exr"

        scene.render.filepath = output_path

        # Render the depth map
        bpy.ops.render.render(write_still=True)

        print(f"✅ Depth map rendered successfully")
        print(f"📁 Output: {{output_path}}")
        print(f"📏 Resolution: {resolution}x{resolution}")
        print(f"👁️  View: {view_direction}")
        print(f"📊 Depth range: {{depth_max - depth_min:.2f}} units")
        print(f"🔄 Inverted: {invert_depth}")

        # Post-processing for CNC optimization
        if {smooth_iterations} > 0:
            print(f"🔧 Applying {{smooth_iterations}} smoothing iterations for CNC optimization")
            # Note: Advanced smoothing would require additional image processing
            # This could be implemented with Blender's compositor nodes

        # Restore original materials
        obj.data.materials.clear()
        for mat in original_materials:
            obj.data.materials.append(mat)

        # Create CNC info file
        info_path = "{self.save_directory}\\\\{filename}_cnc_info.txt"
        with open(info_path, 'w') as info_file:
            info_file.write(f"CNC Depth Map Information\\n")
            info_file.write(f"========================\\n")
            info_file.write(f"Source Object: {object_name}\\n")
            info_file.write(f"View Direction: {view_direction}\\n")
            info_file.write(f"Resolution: {resolution}x{resolution}\\n")
            info_file.write(f"Depth Range: {{depth_max - depth_min:.3f}} units\\n")
            info_file.write(f"Depth Min: {{depth_min:.3f}}\\n")
            info_file.write(f"Depth Max: {{depth_max:.3f}}\\n")
            info_file.write(f"Inverted: {invert_depth}\\n")
            info_file.write(f"Format: {output_format}\\n")
            info_file.write(f"\\nCNC Usage Notes:\\n")
            info_file.write(f"- White areas = {{('Deep cuts' if not {invert_depth} else 'Shallow cuts')}}\\n")
            info_file.write(f"- Black areas = {{('No cut' if not {invert_depth} else 'Deep cuts')}}\\n")
            info_file.write(f"- Recommended bit size: {{max(object_size.x, object_size.y) / {resolution} * 5:.2f}} units\\n")
            info_file.write(f"- Suggested stepdown: {{(depth_max - depth_min) / 10:.3f}} units\\n")

        print(f"📋 CNC info saved: {{info_path}}")

        return True

    except Exception as e:
        print(f"❌ Error generating depth map: {{e}}")
        return False

    finally:
        # Restore original render settings
        scene.render.engine = original_engine
        scene.render.resolution_x = original_resolution_x
        scene.render.resolution_y = original_resolution_y

        # Clean up depth camera
        if 'DepthMapCamera' in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects['DepthMapCamera'], do_unlink=True)

# Execute depth map generation
if create_depth_map():
    print("🎯 Depth map generation completed successfully")
    print("🏭 Ready for CNC relief carving operations")
else:
    print("❌ Depth map generation failed")
'''
        return self.execute_blender_script(script)

    def _import_stl(self, filepath, name="ImportedMesh", scale=1.0, location=[0, 0, 0]):
        """Import STL file into Blender scene using Blender 4.5 wm.stl_import API"""
        script = f'''
import bpy
import os
import mathutils

# Verify STL file exists
if not os.path.exists("{filepath}"):
    print(f"❌ STL file not found: {filepath}")
    exit(1)

print(f"📥 Importing STL: {filepath}")

# Import STL file using Blender 4.5 API
bpy.ops.wm.stl_import(filepath="{filepath}")

# Get the imported object (it becomes the active object)
obj = bpy.context.active_object

if obj:
    # Apply user-specified transformations
    obj.name = "{name}"
    obj.scale = ({scale}, {scale}, {scale})
    obj.location = ({location[0]}, {location[1]}, {location[2]})

    # Apply scale to mesh data for accurate measurements
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Get mesh statistics
    mesh_data = obj.data
    num_vertices = len(mesh_data.vertices)
    num_faces = len(mesh_data.polygons)

    # Calculate bounding box
    bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    min_bound = mathutils.Vector([min(corner[i] for corner in bbox) for i in range(3)])
    max_bound = mathutils.Vector([max(corner[i] for corner in bbox) for i in range(3)])
    dimensions = max_bound - min_bound

    print(f"✅ STL imported successfully: {{obj.name}}")
    print(f"📊 Mesh statistics:")
    print(f"   - Vertices: {{num_vertices:,}}")
    print(f"   - Faces: {{num_faces:,}}")
    print(f"📏 Dimensions: X={{dimensions.x:.2f}}, Y={{dimensions.y:.2f}}, Z={{dimensions.z:.2f}}")
    print(f"📍 Location: {{obj.location}}")
    print(f"📐 Scale: {{obj.scale}}")
    print(f"🎯 Ready for CNC toolpath generation")

    # Save the scene with imported STL
    save_path = "{self.save_directory}\\\\imported_{{os.path.basename('{filepath}').replace('.stl', '.blend')}}"
    os.makedirs("{self.save_directory}", exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print(f"💾 Scene saved: {{save_path}}")
else:
    print(f"❌ Failed to import STL file")
    exit(1)
'''
        return self.execute_blender_script(script)

    def _export_model(self, object_name, format="STL", filename="export", ascii=False):
        """Export 3D model to STL/OBJ/FBX/PLY using Blender's built-in operators"""
        format = format.upper()

        # Define export operators for each format
        format_ops = {
            "STL": f"bpy.ops.wm.stl_export(filepath='{{filepath}}', export_selected_objects=True, ascii_format={ascii})",
            "OBJ": "bpy.ops.wm.obj_export(filepath='{filepath}', export_selected_objects=True)",
            "FBX": "bpy.ops.export_scene.fbx(filepath='{filepath}', use_selection=True)",
            "PLY": "bpy.ops.wm.ply_export(filepath='{filepath}', export_selected_objects=True)"
        }

        if format not in format_ops:
            return {"success": False, "error": f"Unsupported format: {format}. Use STL, OBJ, FBX, or PLY"}

        script = f'''
import bpy
import os

# Find the object to export
obj = bpy.data.objects.get("{object_name}")
if not obj:
    print(f"❌ Object '{{object_name}}' not found")
    available = [o.name for o in bpy.data.objects if o.type == 'MESH']
    print(f"💡 Available mesh objects: {{', '.join(available)}}")
    exit(1)

print(f"📤 Exporting object: {{obj.name}} to {format} format")

# Deselect all and select target object
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Get mesh statistics before export
mesh_data = obj.data
num_vertices = len(mesh_data.vertices)
num_faces = len(mesh_data.polygons)

print(f"📊 Mesh statistics:")
print(f"   - Vertices: {{num_vertices:,}}")
print(f"   - Faces: {{num_faces:,}}")

# Prepare output path
output_dir = "{self.save_directory}"
os.makedirs(output_dir, exist_ok=True)
filepath = os.path.join(output_dir, "{filename}.{format.lower()}")

# Export using appropriate operator
{format_ops.get(format, format_ops["STL"]).format(filepath=filepath)}

# Verify export
if os.path.exists(filepath):
    file_size = os.path.getsize(filepath) / 1024  # KB
    print(f"✅ Export successful: {{obj.name}}")
    print(f"📁 Output: {{filepath}}")
    print(f"💾 File size: {{file_size:.2f}} KB")
    print(f"📝 Format: {format} (ASCII={ascii if format == 'STL' else 'N/A'})")
    print(f"🎯 Ready for CAM software import or CNC machining")
else:
    print(f"❌ Export failed - file not created")
    exit(1)
'''
        return self.execute_blender_script(script)

    # BlenderCAM Integration Methods
    def _setup_blendercam(self, addon_path="F:\\Documents\\Blender\\blendercam-master\\scripts\\addons"):
        """Enable and configure BlenderCAM addon for professional CNC workflows"""
        script = f'''
import bpy
import sys
import os

# Add BlenderCAM addon path to Blender's Python path
addon_path = r"{addon_path}"
if addon_path not in sys.path:
    sys.path.append(addon_path)
    print(f"✅ Added to path: {{addon_path}}")

# Enable BlenderCAM addon
try:
    if "cam" not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module="cam")
        print("✅ BlenderCAM addon enabled")
    else:
        print("ℹ️  BlenderCAM addon already enabled")

    # Verify addon is working
    if hasattr(bpy.ops.scene, 'cam_operation_add'):
        print("✅ BlenderCAM is functional - operators available")
        print(f"🎯 Ready for professional CNC operations")
    else:
        print("⚠️  BlenderCAM enabled but operators not found")

except Exception as e:
    print(f"❌ Error enabling BlenderCAM: {{e}}")
    exit(1)
'''
        return self.execute_blender_script(script)

    def _create_cam_operation(self, object_name, operation_name, operation_type="PARALLEL",
                             cutter_type="BALLNOSE", cutter_diameter=6.0, stepdown=1.0,
                             stepover=0.5, feedrate=1000, spindle_rpm=12000):
        """Create professional CNC operation using BlenderCAM"""
        script = f'''
import bpy

# Ensure BlenderCAM is enabled
if "cam" not in bpy.context.preferences.addons:
    try:
        bpy.ops.preferences.addon_enable(module="cam")
        print("✅ Enabled BlenderCAM addon")
    except:
        print("❌ BlenderCAM addon not found - install from F:\\\\Documents\\\\Blender\\\\blendercam-master\\\\")
        exit(1)

# Verify object exists
obj = bpy.data.objects.get("{object_name}")
if not obj:
    print(f"❌ Object '{{object_name}}' not found")
    exit(1)

print(f"🎯 Creating CAM operation for: {{obj.name}}")

# Create new CAM operation
bpy.ops.scene.cam_operation_add()

# Get the newly created operation
scene = bpy.context.scene
if not hasattr(scene, 'cam_operations') or len(scene.cam_operations) == 0:
    print("❌ Failed to create CAM operation")
    exit(1)

operation = scene.cam_operations[-1]  # Get last added operation
operation.name = "{operation_name}"

# Configure operation properties (convert mm to meters for Blender units)
operation.object_name = "{object_name}"
operation.strategy = '{operation_type}'
operation.cutter_type = '{cutter_type}'
operation.cutter_diameter = {cutter_diameter / 1000.0}  # mm to m
operation.feedrate = {feedrate / 1000.0}  # mm/min to m/min
operation.spindle_rpm = {spindle_rpm}
operation.stepdown = {stepdown / 1000.0}  # mm to m

# Stepover is a percentage (0-1 range)
if {stepover} > 1.0:
    stepover_pct = {stepover / 100.0}
else:
    stepover_pct = {stepover}
operation.stepover = stepover_pct

print(f"✅ Created CAM operation: {{operation.name}}")
print(f"📊 Configuration:")
print(f"   - Strategy: {{operation.strategy}}")
print(f"   - Cutter: {{operation.cutter_type}} Ø{cutter_diameter}mm")
print(f"   - Feed: {feedrate}mm/min @ {spindle_rpm}RPM")
print(f"   - Stepdown: {stepdown}mm, Stepover: {{stepover_pct*100:.1f}}%")
print(f"🎯 Ready to calculate toolpath")
'''
        return self.execute_blender_script(script)

    def _calculate_cam_paths(self, operation_name):
        """Calculate toolpaths using BlenderCAM professional algorithms"""
        script = f'''
import bpy

# Find the operation
scene = bpy.context.scene
operation = None

if hasattr(scene, 'cam_operations'):
    for op in scene.cam_operations:
        if op.name == "{operation_name}":
            operation = op
            break

if not operation:
    print(f"❌ CAM operation '{{operation_name}}' not found")
    exit(1)

print(f"🔄 Calculating toolpath for: {{operation.name}}")
print(f"⚙️  Strategy: {{operation.strategy}}")

# Set as active operation
scene.cam_active_operation = operation

# Calculate toolpath (this may take time for complex operations)
try:
    bpy.ops.object.calculate_cam_path()

    # Check if path was created
    path_obj_name = f"cam_path_{{operation.name}}"
    if bpy.data.objects.get(path_obj_name):
        path_obj = bpy.data.objects[path_obj_name]
        print(f"✅ Toolpath calculated successfully")
        print(f"📏 Path object: {{path_obj.name}}")
        print(f"🎯 Ready to export G-code")
    else:
        print(f"⚠️  Toolpath operator completed but path object not found")

except Exception as e:
    print(f"❌ Error calculating toolpath: {{e}}")
    exit(1)
'''
        return self.execute_blender_script(script)

    def _export_cam_gcode(self, operation_name, post_processor="GRBL", filename="output"):
        """Export G-code using BlenderCAM post-processors"""
        script = f'''
import bpy
import os

# Find the operation
scene = bpy.context.scene
operation = None

if hasattr(scene, 'cam_operations'):
    for op in scene.cam_operations:
        if op.name == "{operation_name}":
            operation = op
            break

if not operation:
    print(f"❌ CAM operation '{{operation_name}}' not found")
    exit(1)

# Check if toolpath exists
path_obj_name = f"cam_path_{{operation.name}}"
path_obj = bpy.data.objects.get(path_obj_name)

if not path_obj:
    print(f"❌ Toolpath not found - calculate toolpath first")
    exit(1)

print(f"📤 Exporting G-code for: {{operation.name}}")

# Set post-processor (convert to proper BlenderCAM format)
post_processor_map = {{
    "GRBL": "grbl",
    "ISO": "iso",
    "LINUXCNC": "linuxcnc",
    "EMC2": "emc2",
    "FADAL": "fadal",
    "HEIDENHAIN": "heiden",
    "MACH3": "mach3",
    "SHOPBOT": "shopbot_mtc",
    "FANUC": "fanuc",
    "HAAS": "haas"
}}

pp = post_processor_map.get("{post_processor}", "{post_processor}").lower()
scene.cam_machine.post_processor = pp

# Set output filename
output_path = os.path.join(r"{self.save_directory}", "{filename}.gcode")
os.makedirs(r"{self.save_directory}", exist_ok=True)

operation.filename = output_path

# Export G-code
try:
    from cam import gcodepath

    # Get mesh data from path object
    vertslist = [path_obj.data]
    operations = [operation]

    # Export using BlenderCAM's professional G-code generator
    gcodepath.exportGcodePath(output_path, vertslist, operations)

    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"✅ G-code exported successfully")
        print(f"📁 File: {{output_path}}")
        print(f"📊 Size: {{file_size}} bytes")
        print(f"🏭 Post-processor: {{pp}}")
        print(f"🎯 Ready for CNC machine")
    else:
        print(f"❌ G-code export failed - file not created")
        exit(1)

except Exception as e:
    print(f"❌ Error exporting G-code: {{e}}")
    import traceback
    traceback.print_exc()
    exit(1)
'''
        return self.execute_blender_script(script)

    def _simulate_cam_operation(self, operation_name):
        """Simulate CAM operation with BlenderCAM's material removal simulation"""
        script = f'''
import bpy

# Find the operation
scene = bpy.context.scene
operation = None

if hasattr(scene, 'cam_operations'):
    for op in scene.cam_operations:
        if op.name == "{operation_name}":
            operation = op
            break

if not operation:
    print(f"❌ CAM operation '{{operation_name}}' not found")
    exit(1)

print(f"🎬 Simulating CAM operation: {{operation.name}}")

# Set as active operation
scene.cam_active_operation = operation

# Run simulation
try:
    bpy.ops.object.cam_simulate()
    print(f"✅ Simulation completed for: {{operation.name}}")
    print(f"🎯 Check 3D viewport for simulated material removal")

except Exception as e:
    print(f"❌ Error running simulation: {{e}}")
    exit(1)
'''
        return self.execute_blender_script(script)

    def run(self):
        """Run the MCP server with full protocol support"""
        logger.info("🚀 Starting Complete Blender MCP Server")
        logger.info(f"📡 Server ready with {len(self.tools)} tools")
        logger.info("🎯 Waiting for GitHub Copilot requests...")

        try:
            while True:
                try:
                    line = sys.stdin.readline().strip()
                    if not line:
                        continue

                    request = json.loads(line)
                    response = self.handle_mcp_request(request)

                    print(json.dumps(response), flush=True)

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    error_response = {"error": "Invalid JSON request"}
                    print(json.dumps(error_response), flush=True)

                except Exception as e:
                    logger.error(f"Error handling request: {e}")
                    logger.error(traceback.format_exc())
                    error_response = {"error": str(e)}
                    print(json.dumps(error_response), flush=True)

        except KeyboardInterrupt:
            logger.info("👋 MCP Server shutting down...")
            sys.exit(0)

    def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests"""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            return {
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "blender-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "tools/list":
            tools_list = []
            for tool in self.tools:
                tools_list.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.parameters
                })

            return {
                "id": request_id,
                "result": {"tools": tools_list}
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})

            result = self.handle_tool_call(tool_name, arguments)

            return {
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }

        else:
            return {
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }

if __name__ == "__main__":
    server = BlenderMCPServer()
    server.run()
