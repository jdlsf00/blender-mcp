"""
Blender API utilities and safety wrappers.

This module provides safe wrappers around Blender's bpy API with proper error handling,
validation, and logging for use in the MCP server.
"""

import logging
from typing import Optional, Tuple, Any, Dict

logger = logging.getLogger(__name__)

# Global flag to track if we're running inside Blender
_blender_available = False
bpy = None

try:
    import bpy
    import bmesh
    import mathutils
    _blender_available = True
    logger.info("Blender bpy module loaded successfully")
except ImportError:
    logger.warning("Blender bpy module not available - running in mock mode")
    # Create mock objects for development/testing
    class MockBpy:
        class context:
            scene = None
            object = None
            selected_objects = []
            
        class data:
            objects = {}
            materials = {}
            meshes = {}
            cameras = {}
            lights = {}
            
        class ops:
            class mesh:
                @staticmethod
                def primitive_cube_add(**kwargs):
                    return {'FINISHED'}
                    
                @staticmethod
                def primitive_uv_sphere_add(**kwargs):
                    return {'FINISHED'}
                    
                @staticmethod
                def primitive_cylinder_add(**kwargs):
                    return {'FINISHED'}
                    
            class object:
                @staticmethod
                def delete(**kwargs):
                    return {'FINISHED'}
                    
                @staticmethod
                def camera_add(**kwargs):
                    return {'FINISHED'}
                    
                @staticmethod
                def light_add(**kwargs):
                    return {'FINISHED'}
                    
            class render:
                @staticmethod
                def render(**kwargs):
                    return {'FINISHED'}
                    
            class wm:
                @staticmethod
                def save_mainfile(**kwargs):
                    return {'FINISHED'}
                    
                @staticmethod
                def open_mainfile(**kwargs):
                    return {'FINISHED'}
                    
        class types:
            class Object:
                location = [0, 0, 0]
                rotation_euler = [0, 0, 0]
                scale = [1, 1, 1]
                name = "MockObject"
                
    bpy = MockBpy()
    
    class MockBmesh:
        @staticmethod
        def new():
            return None
            
        @staticmethod
        def from_mesh(mesh):
            return None
            
    bmesh = MockBmesh()
    
    class MockMathutils:
        class Vector:
            def __init__(self, vec):
                self.vec = vec
                
    mathutils = MockMathutils()

def is_blender_available() -> bool:
    """Check if we're running inside Blender with bpy available."""
    return _blender_available

def safe_execute(operation_name: str, operation_func, *args, **kwargs) -> Tuple[bool, str, Any]:
    """
    Safely execute a Blender operation with proper error handling.
    
    Args:
        operation_name: Human-readable name of the operation
        operation_func: The Blender operation function to execute
        *args, **kwargs: Arguments to pass to the operation
        
    Returns:
        Tuple of (success: bool, message: str, result: Any)
    """
    try:
        logger.debug(f"Executing {operation_name} with args={args}, kwargs={kwargs}")
        
        if not is_blender_available():
            return True, f"Mock execution of {operation_name} (Blender not available)", None
            
        result = operation_func(*args, **kwargs)
        
        # Check if operation returned a status
        if isinstance(result, set) and 'FINISHED' in result:
            logger.info(f"Successfully executed {operation_name}")
            return True, f"Successfully executed {operation_name}", result
        elif isinstance(result, set) and 'CANCELLED' in result:
            logger.warning(f"Operation {operation_name} was cancelled")
            return False, f"Operation {operation_name} was cancelled", result
        else:
            logger.info(f"Executed {operation_name}")
            return True, f"Executed {operation_name}", result
            
    except Exception as e:
        error_msg = f"Error executing {operation_name}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, None

def get_object_by_name(name: str) -> Optional[Any]:
    """
    Safely get an object by name.
    
    Args:
        name: Name of the object to retrieve
        
    Returns:
        Object if found, None otherwise
    """
    try:
        if not is_blender_available():
            return None
            
        return bpy.data.objects.get(name)
    except Exception as e:
        logger.error(f"Error getting object '{name}': {str(e)}")
        return None

def validate_location(location: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Validate and normalize a 3D location.
    
    Args:
        location: Tuple of (x, y, z) coordinates
        
    Returns:
        Validated location tuple
        
    Raises:
        ValueError: If location is invalid
    """
    if not isinstance(location, (tuple, list)) or len(location) != 3:
        raise ValueError("Location must be a tuple/list of 3 numbers (x, y, z)")
        
    try:
        return (float(location[0]), float(location[1]), float(location[2]))
    except (ValueError, TypeError) as e:
        raise ValueError(f"Location coordinates must be numbers: {str(e)}")

def validate_color(color: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    """
    Validate and normalize an RGBA color.
    
    Args:
        color: Tuple of (r, g, b, a) values
        
    Returns:
        Validated color tuple with values clamped to 0-1 range
        
    Raises:
        ValueError: If color is invalid
    """
    if not isinstance(color, (tuple, list)) or len(color) != 4:
        raise ValueError("Color must be a tuple/list of 4 numbers (r, g, b, a)")
        
    try:
        # Clamp values to 0-1 range
        r = max(0.0, min(1.0, float(color[0])))
        g = max(0.0, min(1.0, float(color[1])))
        b = max(0.0, min(1.0, float(color[2])))
        a = max(0.0, min(1.0, float(color[3])))
        return (r, g, b, a)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Color values must be numbers: {str(e)}")

def ensure_object_mode():
    """Ensure we're in Object mode for operations that require it."""
    if is_blender_available() and bpy.context.mode != 'OBJECT':
        logger.debug("Switching to Object mode")
        bpy.ops.object.mode_set(mode='OBJECT')

def deselect_all():
    """Deselect all objects in the scene."""
    if is_blender_available():
        bpy.ops.object.select_all(action='DESELECT')

def select_object(obj_name: str) -> bool:
    """
    Select an object by name.
    
    Args:
        obj_name: Name of the object to select
        
    Returns:
        True if object was selected, False otherwise
    """
    if not is_blender_available():
        return False
        
    obj = get_object_by_name(obj_name)
    if obj:
        ensure_object_mode()
        deselect_all()
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        logger.debug(f"Selected object '{obj_name}'")
        return True
    else:
        logger.warning(f"Object '{obj_name}' not found")
        return False

def format_location(location: Tuple[float, float, float]) -> str:
    """Format a location tuple as a readable string."""
    return f"({location[0]:.2f}, {location[1]:.2f}, {location[2]:.2f})"

def format_color(color: Tuple[float, float, float, float]) -> str:
    """Format a color tuple as a readable string."""
    return f"RGBA({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f}, {color[3]:.2f})"