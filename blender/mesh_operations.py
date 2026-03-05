"""
Mesh operations for the Blender MCP server.

This module provides safe wrappers around Blender's mesh creation and manipulation operations.
"""

import logging
from typing import Tuple
from .blender_utils import (
    safe_execute, bpy, validate_location, format_location, 
    get_object_by_name, select_object, ensure_object_mode, deselect_all
)

logger = logging.getLogger(__name__)

class MeshOperations:
    """Handles mesh creation and manipulation operations."""
    
    def create_cube(self, name: str = "Cube", location: Tuple[float, float, float] = (0, 0, 0)) -> str:
        """
        Create a cube mesh.
        
        Args:
            name: Name for the cube object
            location: Position in 3D space (x, y, z)
            
        Returns:
            Status message
        """
        try:
            location = validate_location(location)
            
            def _create_cube():
                ensure_object_mode()
                return bpy.ops.mesh.primitive_cube_add(location=location)
                
            success, message, result = safe_execute(
                f"create cube '{name}'",
                _create_cube
            )
            
            if success and bpy.context.active_object:
                bpy.context.active_object.name = name
                return f"✅ Created cube '{name}' at {format_location(location)}"
            else:
                return f"❌ Failed to create cube: {message}"
                
        except ValueError as e:
            return f"❌ Invalid parameters for cube creation: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error creating cube: {str(e)}")
            return f"❌ Unexpected error creating cube: {str(e)}"
    
    def create_sphere(self, name: str = "Sphere", location: Tuple[float, float, float] = (0, 0, 0), 
                     subdivisions: int = 2) -> str:
        """
        Create a sphere mesh.
        
        Args:
            name: Name for the sphere object
            location: Position in 3D space (x, y, z)
            subdivisions: Number of subdivisions for smoothness (1-5 recommended)
            
        Returns:
            Status message
        """
        try:
            location = validate_location(location)
            subdivisions = max(1, min(5, int(subdivisions)))  # Clamp to reasonable range
            
            def _create_sphere():
                ensure_object_mode()
                return bpy.ops.mesh.primitive_uv_sphere_add(
                    location=location,
                    subdivisions=subdivisions
                )
                
            success, message, result = safe_execute(
                f"create sphere '{name}'",
                _create_sphere
            )
            
            if success and bpy.context.active_object:
                bpy.context.active_object.name = name
                return f"✅ Created sphere '{name}' at {format_location(location)} with {subdivisions} subdivisions"
            else:
                return f"❌ Failed to create sphere: {message}"
                
        except ValueError as e:
            return f"❌ Invalid parameters for sphere creation: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error creating sphere: {str(e)}")
            return f"❌ Unexpected error creating sphere: {str(e)}"
    
    def create_cylinder(self, name: str = "Cylinder", location: Tuple[float, float, float] = (0, 0, 0),
                       radius: float = 1.0, depth: float = 2.0) -> str:
        """
        Create a cylinder mesh.
        
        Args:
            name: Name for the cylinder object
            location: Position in 3D space (x, y, z)
            radius: Radius of the cylinder
            depth: Height of the cylinder
            
        Returns:
            Status message
        """
        try:
            location = validate_location(location)
            radius = max(0.1, float(radius))  # Minimum radius
            depth = max(0.1, float(depth))    # Minimum height
            
            def _create_cylinder():
                ensure_object_mode()
                return bpy.ops.mesh.primitive_cylinder_add(
                    location=location,
                    radius=radius,
                    depth=depth
                )
                
            success, message, result = safe_execute(
                f"create cylinder '{name}'",
                _create_cylinder
            )
            
            if success and bpy.context.active_object:
                bpy.context.active_object.name = name
                return f"✅ Created cylinder '{name}' at {format_location(location)} (radius: {radius:.2f}, height: {depth:.2f})"
            else:
                return f"❌ Failed to create cylinder: {message}"
                
        except ValueError as e:
            return f"❌ Invalid parameters for cylinder creation: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error creating cylinder: {str(e)}")
            return f"❌ Unexpected error creating cylinder: {str(e)}"
    
    def delete_object(self, object_name: str) -> str:
        """
        Delete an object from the scene.
        
        Args:
            object_name: Name of the object to delete
            
        Returns:
            Status message
        """
        try:
            obj = get_object_by_name(object_name)
            if not obj:
                return f"❌ Object '{object_name}' not found"
            
            def _delete_object():
                ensure_object_mode()
                deselect_all()
                obj.select_set(True)
                return bpy.ops.object.delete()
                
            success, message, result = safe_execute(
                f"delete object '{object_name}'",
                _delete_object
            )
            
            if success:
                return f"✅ Deleted object '{object_name}'"
            else:
                return f"❌ Failed to delete object '{object_name}': {message}"
                
        except Exception as e:
            logger.error(f"Unexpected error deleting object: {str(e)}")
            return f"❌ Unexpected error deleting object: {str(e)}"
    
    def move_object(self, object_name: str, location: Tuple[float, float, float]) -> str:
        """
        Move an object to a new location.
        
        Args:
            object_name: Name of the object to move
            location: New position in 3D space (x, y, z)
            
        Returns:
            Status message
        """
        try:
            location = validate_location(location)
            obj = get_object_by_name(object_name)
            
            if not obj:
                return f"❌ Object '{object_name}' not found"
            
            old_location = tuple(obj.location)
            obj.location = location
            
            return f"✅ Moved '{object_name}' from {format_location(old_location)} to {format_location(location)}"
            
        except ValueError as e:
            return f"❌ Invalid location for object move: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error moving object: {str(e)}")
            return f"❌ Unexpected error moving object: {str(e)}"
    
    def scale_object(self, object_name: str, scale: Tuple[float, float, float]) -> str:
        """
        Scale an object.
        
        Args:
            object_name: Name of the object to scale
            scale: Scale factors for x, y, z axes
            
        Returns:
            Status message
        """
        try:
            if not isinstance(scale, (tuple, list)) or len(scale) != 3:
                raise ValueError("Scale must be a tuple/list of 3 numbers (x, y, z)")
            
            scale = tuple(max(0.001, float(s)) for s in scale)  # Minimum scale to avoid issues
            obj = get_object_by_name(object_name)
            
            if not obj:
                return f"❌ Object '{object_name}' not found"
            
            old_scale = tuple(obj.scale)
            obj.scale = scale
            
            return f"✅ Scaled '{object_name}' from {format_location(old_scale)} to {format_location(scale)}"
            
        except ValueError as e:
            return f"❌ Invalid scale values: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error scaling object: {str(e)}")
            return f"❌ Unexpected error scaling object: {str(e)}"
    
    def rotate_object(self, object_name: str, rotation: Tuple[float, float, float]) -> str:
        """
        Set the rotation of an object.
        
        Args:
            object_name: Name of the object to rotate
            rotation: Rotation in radians for x, y, z axes
            
        Returns:
            Status message
        """
        try:
            if not isinstance(rotation, (tuple, list)) or len(rotation) != 3:
                raise ValueError("Rotation must be a tuple/list of 3 numbers (x, y, z) in radians")
            
            rotation = tuple(float(r) for r in rotation)
            obj = get_object_by_name(object_name)
            
            if not obj:
                return f"❌ Object '{object_name}' not found"
            
            old_rotation = tuple(obj.rotation_euler)
            obj.rotation_euler = rotation
            
            # Convert to degrees for display
            old_degrees = tuple(r * 57.2958 for r in old_rotation)  # radians to degrees
            new_degrees = tuple(r * 57.2958 for r in rotation)
            
            return f"✅ Rotated '{object_name}' from {format_location(old_degrees)}° to {format_location(new_degrees)}°"
            
        except ValueError as e:
            return f"❌ Invalid rotation values: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error rotating object: {str(e)}")
            return f"❌ Unexpected error rotating object: {str(e)}"