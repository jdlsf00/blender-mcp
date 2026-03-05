"""
Material operations for the Blender MCP server.

This module provides safe wrappers around Blender's material creation and assignment operations.
"""

import logging
from typing import Tuple, List, Dict, Any
from .blender_utils import (
    safe_execute, bpy, validate_color, format_color, 
    get_object_by_name, is_blender_available
)

logger = logging.getLogger(__name__)

class MaterialOperations:
    """Handles material creation and assignment operations."""
    
    def create_material(self, name: str, color: Tuple[float, float, float, float] = (1, 1, 1, 1)) -> str:
        """
        Create a new material.
        
        Args:
            name: Name for the material
            color: RGBA color values (0-1 range)
            
        Returns:
            Status message
        """
        try:
            color = validate_color(color)
            
            # Check if material already exists
            if is_blender_available() and bpy.data.materials.get(name):
                return f"⚠️ Material '{name}' already exists. Use a different name or modify the existing material."
            
            def _create_material():
                if not is_blender_available():
                    return None
                    
                # Create new material
                mat = bpy.data.materials.new(name=name)
                
                # Enable nodes for modern material workflow
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                
                # Clear default nodes
                nodes.clear()
                
                # Add Principled BSDF node
                bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
                bsdf.location = (0, 0)
                
                # Add Material Output node
                output = nodes.new(type='ShaderNodeOutputMaterial')
                output.location = (300, 0)
                
                # Link BSDF to output
                links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
                
                # Set base color (RGB only, alpha handled separately)
                bsdf.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
                
                # If alpha < 1, enable transparency
                if color[3] < 1.0:
                    bsdf.inputs['Alpha'].default_value = color[3]
                    mat.blend_method = 'BLEND'
                
                return mat
                
            success, message, material = safe_execute(
                f"create material '{name}'",
                _create_material
            )
            
            if success or not is_blender_available():
                return f"✅ Created material '{name}' with color {format_color(color)}"
            else:
                return f"❌ Failed to create material '{name}': {message}"
                
        except ValueError as e:
            return f"❌ Invalid parameters for material creation: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error creating material: {str(e)}")
            return f"❌ Unexpected error creating material: {str(e)}"
    
    def assign_material(self, object_name: str, material_name: str) -> str:
        """
        Assign a material to an object.
        
        Args:
            object_name: Name of the object
            material_name: Name of the material
            
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return f"✅ Mock: Assigned material '{material_name}' to object '{object_name}'"
                
            obj = get_object_by_name(object_name)
            if not obj:
                return f"❌ Object '{object_name}' not found"
            
            material = bpy.data.materials.get(material_name)
            if not material:
                return f"❌ Material '{material_name}' not found"
            
            # Ensure object has material slots
            if len(obj.material_slots) == 0:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.material_slot_add()
            
            # Assign material to first slot
            obj.material_slots[0].material = material
            
            return f"✅ Assigned material '{material_name}' to object '{object_name}'"
            
        except Exception as e:
            logger.error(f"Unexpected error assigning material: {str(e)}")
            return f"❌ Unexpected error assigning material: {str(e)}"
    
    def set_material_property(self, material_name: str, property_name: str, value: float) -> str:
        """
        Set a material property.
        
        Args:
            material_name: Name of the material
            property_name: Property to set (metallic, roughness, emission_strength, etc.)
            value: Value to set
            
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return f"✅ Mock: Set {property_name} = {value} on material '{material_name}'"
                
            material = bpy.data.materials.get(material_name)
            if not material:
                return f"❌ Material '{material_name}' not found"
            
            if not material.use_nodes:
                return f"❌ Material '{material_name}' does not use nodes. Cannot set node properties."
            
            # Find the Principled BSDF node
            bsdf_node = None
            for node in material.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    bsdf_node = node
                    break
            
            if not bsdf_node:
                return f"❌ No Principled BSDF node found in material '{material_name}'"
            
            # Map property names to node input names
            property_map = {
                'metallic': 'Metallic',
                'roughness': 'Roughness',
                'emission_strength': 'Emission Strength',
                'ior': 'IOR',
                'alpha': 'Alpha',
                'transmission': 'Transmission',
                'subsurface': 'Subsurface Weight',
                'specular': 'Specular IOR Level'
            }
            
            node_input = property_map.get(property_name.lower())
            if not node_input:
                available = ', '.join(property_map.keys())
                return f"❌ Unknown property '{property_name}'. Available: {available}"
            
            if node_input not in bsdf_node.inputs:
                return f"❌ Property '{property_name}' not available in this material's BSDF node"
            
            # Clamp value to reasonable range for most properties
            if property_name.lower() in ['metallic', 'roughness', 'alpha', 'transmission', 'subsurface']:
                value = max(0.0, min(1.0, float(value)))
            elif property_name.lower() == 'ior':
                value = max(1.0, min(4.0, float(value)))  # Reasonable IOR range
            else:
                value = float(value)
            
            bsdf_node.inputs[node_input].default_value = value
            
            return f"✅ Set '{property_name}' to {value} on material '{material_name}'"
            
        except ValueError as e:
            return f"❌ Invalid value for property: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error setting material property: {str(e)}")
            return f"❌ Unexpected error setting material property: {str(e)}"
    
    def create_emission_material(self, name: str, color: Tuple[float, float, float] = (1, 1, 1), 
                                strength: float = 5.0) -> str:
        """
        Create an emission (glowing) material.
        
        Args:
            name: Name for the material
            color: RGB emission color (0-1 range)
            strength: Emission strength
            
        Returns:
            Status message
        """
        try:
            if len(color) != 3:
                raise ValueError("Emission color must be RGB (3 values)")
            
            color = tuple(max(0.0, min(1.0, float(c))) for c in color)
            strength = max(0.0, float(strength))
            
            # First create basic material
            result = self.create_material(name, (*color, 1.0))
            if "❌" in result:
                return result
            
            if not is_blender_available():
                return f"✅ Mock: Created emission material '{name}' with strength {strength}"
            
            # Modify material to be emissive
            material = bpy.data.materials.get(name)
            if material and material.use_nodes:
                bsdf_node = None
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        bsdf_node = node
                        break
                
                if bsdf_node:
                    bsdf_node.inputs['Emission Color'].default_value = (*color, 1.0)
                    bsdf_node.inputs['Emission Strength'].default_value = strength
            
            return f"✅ Created emission material '{name}' with color {color} and strength {strength}"
            
        except ValueError as e:
            return f"❌ Invalid parameters for emission material: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error creating emission material: {str(e)}")
            return f"❌ Unexpected error creating emission material: {str(e)}"
    
    def get_materials_list(self) -> str:
        """
        Get a list of all materials in the scene.
        
        Returns:
            Formatted string with material information
        """
        try:
            if not is_blender_available():
                return "Mock materials list:\n- DefaultMaterial (Red)\n- TestMaterial (Blue)"
            
            materials = bpy.data.materials
            if not materials:
                return "No materials found in the scene."
            
            material_info = []
            for mat in materials:
                info = f"• {mat.name}"
                
                if mat.use_nodes:
                    # Try to get base color from Principled BSDF
                    for node in mat.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            base_color = node.inputs['Base Color'].default_value
                            info += f" - Color: ({base_color[0]:.2f}, {base_color[1]:.2f}, {base_color[2]:.2f})"
                            
                            metallic = node.inputs['Metallic'].default_value
                            roughness = node.inputs['Roughness'].default_value
                            if metallic > 0:
                                info += f" - Metallic: {metallic:.2f}"
                            if roughness != 0.5:  # Only show if not default
                                info += f" - Roughness: {roughness:.2f}"
                            break
                else:
                    info += " (Legacy material)"
                
                material_info.append(info)
            
            return f"Materials in scene ({len(materials)} total):\n" + "\n".join(material_info)
            
        except Exception as e:
            logger.error(f"Error getting materials list: {str(e)}")
            return f"❌ Error getting materials list: {str(e)}"
    
    def duplicate_material(self, source_name: str, new_name: str) -> str:
        """
        Duplicate an existing material.
        
        Args:
            source_name: Name of the material to duplicate
            new_name: Name for the new material
            
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return f"✅ Mock: Duplicated material '{source_name}' as '{new_name}'"
            
            source_mat = bpy.data.materials.get(source_name)
            if not source_mat:
                return f"❌ Source material '{source_name}' not found"
            
            if bpy.data.materials.get(new_name):
                return f"❌ Material '{new_name}' already exists"
            
            # Create a copy
            new_mat = source_mat.copy()
            new_mat.name = new_name
            
            return f"✅ Duplicated material '{source_name}' as '{new_name}'"
            
        except Exception as e:
            logger.error(f"Unexpected error duplicating material: {str(e)}")
            return f"❌ Unexpected error duplicating material: {str(e)}"