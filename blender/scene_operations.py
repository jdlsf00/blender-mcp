"""
Scene operations for the Blender MCP server.

This module provides safe wrappers around Blender's scene management operations.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from .blender_utils import (
    safe_execute, bpy, get_object_by_name, 
    is_blender_available, validate_color
)

logger = logging.getLogger(__name__)

class SceneOperations:
    """Handles scene management operations."""
    
    def get_scene_objects(self) -> str:
        """
        Get a list of all objects in the current scene.
        
        Returns:
            Formatted string with object information
        """
        try:
            if not is_blender_available():
                return "Mock scene objects:\n• Cube (Mesh) at (0, 0, 0)\n• Light (Light) at (4, 1, 6)\n• Camera (Camera) at (7, -7, 5)"
            
            scene = bpy.context.scene
            if not scene.objects:
                return "No objects found in the current scene."
            
            object_info = []
            for obj in scene.objects:
                location = obj.location
                info = f"• {obj.name} ({obj.type.title()}) at ({location.x:.2f}, {location.y:.2f}, {location.z:.2f})"
                
                # Add additional type-specific info
                if obj.type == 'MESH':
                    mesh_data = obj.data
                    if mesh_data:
                        vertex_count = len(mesh_data.vertices)
                        face_count = len(mesh_data.polygons)
                        info += f" - {vertex_count} verts, {face_count} faces"
                elif obj.type == 'LIGHT':
                    light_data = obj.data
                    if light_data:
                        info += f" - {light_data.type} light, {light_data.energy}W"
                elif obj.type == 'CAMERA':
                    camera_data = obj.data
                    if camera_data:
                        info += f" - {camera_data.lens}mm lens"
                
                # Add material info if present
                if hasattr(obj, 'material_slots') and obj.material_slots:
                    materials = [slot.material.name for slot in obj.material_slots if slot.material]
                    if materials:
                        info += f" - Materials: {', '.join(materials)}"
                
                object_info.append(info)
            
            return f"Scene objects ({len(scene.objects)} total):\n" + "\n".join(object_info)
            
        except Exception as e:
            logger.error(f"Error getting scene objects: {str(e)}")
            return f"❌ Error getting scene objects: {str(e)}"
    
    def clear_scene(self, keep_camera: bool = True, keep_light: bool = True) -> str:
        """
        Clear all objects from the scene.
        
        Args:
            keep_camera: Whether to keep camera objects
            keep_light: Whether to keep light objects
            
        Returns:
            Status message
        """
        try:
            def _clear_scene():
                if not is_blender_available():
                    return 0
                    
                # Select all objects first
                bpy.ops.object.select_all(action='SELECT')
                
                # Deselect objects we want to keep
                objects_to_keep = []
                for obj in bpy.context.scene.objects:
                    should_keep = False
                    
                    if keep_camera and obj.type == 'CAMERA':
                        should_keep = True
                    elif keep_light and obj.type == 'LIGHT':
                        should_keep = True
                    
                    if should_keep:
                        obj.select_set(False)
                        objects_to_keep.append(obj.name)
                
                # Delete selected objects
                deleted_count = len([obj for obj in bpy.context.scene.objects if obj.select_get()])
                bpy.ops.object.delete(use_global=False)
                
                return deleted_count
            
            success, message, deleted_count = safe_execute(
                "clear scene",
                _clear_scene
            )
            
            if success or not is_blender_available():
                kept_types = []
                if keep_camera:
                    kept_types.append("cameras")
                if keep_light:
                    kept_types.append("lights")
                
                kept_info = f" (kept {', '.join(kept_types)})" if kept_types else ""
                
                if not is_blender_available():
                    return f"✅ Mock: Cleared scene{kept_info}"
                else:
                    return f"✅ Cleared scene - deleted {deleted_count} objects{kept_info}"
            else:
                return f"❌ Failed to clear scene: {message}"
                
        except Exception as e:
            logger.error(f"Unexpected error clearing scene: {str(e)}")
            return f"❌ Unexpected error clearing scene: {str(e)}"
    
    def set_camera_location(self, x: float, y: float, z: float, camera_name: str = "Camera") -> str:
        """
        Set the camera location.
        
        Args:
            x, y, z: World coordinates
            camera_name: Name of the camera object
            
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return f"✅ Mock: Moved camera '{camera_name}' to ({x}, {y}, {z})"
            
            camera = get_object_by_name(camera_name)
            if not camera:
                return f"❌ Camera '{camera_name}' not found"
            
            if camera.type != 'CAMERA':
                return f"❌ Object '{camera_name}' is not a camera"
            
            camera.location = (float(x), float(y), float(z))
            
            return f"✅ Moved camera '{camera_name}' to ({x}, {y}, {z})"
            
        except Exception as e:
            logger.error(f"Error setting camera location: {str(e)}")
            return f"❌ Error setting camera location: {str(e)}"
    
    def point_camera_at(self, target_x: float, target_y: float, target_z: float, 
                       camera_name: str = "Camera") -> str:
        """
        Point the camera at a specific location.
        
        Args:
            target_x, target_y, target_z: Target coordinates to look at
            camera_name: Name of the camera object
            
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return f"✅ Mock: Pointed camera '{camera_name}' at ({target_x}, {target_y}, {target_z})"
            
            camera = get_object_by_name(camera_name)
            if not camera:
                return f"❌ Camera '{camera_name}' not found"
            
            if camera.type != 'CAMERA':
                return f"❌ Object '{camera_name}' is not a camera"
            
            # Create a temporary target object
            bpy.ops.object.empty_add(location=(target_x, target_y, target_z))
            target = bpy.context.object
            target.name = "temp_camera_target"
            
            # Select camera and add track-to constraint
            bpy.context.view_layer.objects.active = camera
            camera.select_set(True)
            
            # Add track-to constraint
            constraint = camera.constraints.new(type='TRACK_TO')
            constraint.target = target
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'
            
            # Apply constraint and remove it
            bpy.context.view_layer.update()
            camera.constraints.remove(constraint)
            
            # Delete temporary target
            bpy.ops.object.select_all(action='DESELECT')
            target.select_set(True)
            bpy.ops.object.delete(use_global=False)
            
            return f"✅ Pointed camera '{camera_name}' at ({target_x}, {target_y}, {target_z})"
            
        except Exception as e:
            logger.error(f"Error pointing camera: {str(e)}")
            return f"❌ Error pointing camera: {str(e)}"
    
    def add_light(self, light_type: str = "SUN", location: Tuple[float, float, float] = (5, 5, 10),
                  energy: float = 3.0, name: str = "Light") -> str:
        """
        Add a light to the scene.
        
        Args:
            light_type: Type of light (SUN, POINT, SPOT, AREA)
            location: World coordinates for the light
            energy: Light energy/strength
            name: Name for the light object
            
        Returns:
            Status message
        """
        try:
            valid_types = ["SUN", "POINT", "SPOT", "AREA"]
            light_type = light_type.upper()
            
            if light_type not in valid_types:
                return f"❌ Invalid light type '{light_type}'. Valid types: {', '.join(valid_types)}"
            
            energy = max(0.0, float(energy))
            
            def _add_light():
                if not is_blender_available():
                    return None
                
                # Add light
                bpy.ops.object.light_add(type=light_type, location=location)
                light_obj = bpy.context.object
                light_obj.name = name
                
                # Set energy
                light_obj.data.energy = energy
                
                return light_obj
            
            success, message, light_obj = safe_execute(
                f"add {light_type} light",
                _add_light
            )
            
            if success or not is_blender_available():
                return f"✅ Added {light_type} light '{name}' at {location} with {energy}W energy"
            else:
                return f"❌ Failed to add light: {message}"
                
        except ValueError as e:
            return f"❌ Invalid parameters for light: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error adding light: {str(e)}")
            return f"❌ Unexpected error adding light: {str(e)}"
    
    def save_blend_file(self, filepath: str) -> str:
        """
        Save the current Blender file.
        
        Args:
            filepath: Path to save the file (should end with .blend)
            
        Returns:
            Status message
        """
        try:
            if not filepath.lower().endswith('.blend'):
                filepath += '.blend'
            
            def _save_file():
                if not is_blender_available():
                    return None
                    
                bpy.ops.wm.save_as_mainfile(filepath=filepath)
                return filepath
            
            success, message, result = safe_execute(
                f"save blend file to '{filepath}'",
                _save_file
            )
            
            if success or not is_blender_available():
                return f"✅ Saved Blender file to '{filepath}'"
            else:
                return f"❌ Failed to save file: {message}"
                
        except Exception as e:
            logger.error(f"Error saving blend file: {str(e)}")
            return f"❌ Error saving blend file: {str(e)}"
    
    def load_blend_file(self, filepath: str) -> str:
        """
        Load a Blender file.
        
        Args:
            filepath: Path to the .blend file to load
            
        Returns:
            Status message
        """
        try:
            def _load_file():
                if not is_blender_available():
                    return None
                    
                bpy.ops.wm.open_mainfile(filepath=filepath)
                return filepath
            
            success, message, result = safe_execute(
                f"load blend file from '{filepath}'",
                _load_file
            )
            
            if success or not is_blender_available():
                return f"✅ Loaded Blender file from '{filepath}'"
            else:
                return f"❌ Failed to load file: {message}"
                
        except Exception as e:
            logger.error(f"Error loading blend file: {str(e)}")
            return f"❌ Error loading blend file: {str(e)}"
    
    def new_scene(self, scene_name: str = "NewScene") -> str:
        """
        Create a new scene.
        
        Args:
            scene_name: Name for the new scene
            
        Returns:
            Status message
        """
        try:
            def _new_scene():
                if not is_blender_available():
                    return None
                    
                # Create new scene
                new_scene = bpy.data.scenes.new(name=scene_name)
                bpy.context.window.scene = new_scene
                
                return new_scene
            
            success, message, scene = safe_execute(
                f"create new scene '{scene_name}'",
                _new_scene
            )
            
            if success or not is_blender_available():
                return f"✅ Created new scene '{scene_name}'"
            else:
                return f"❌ Failed to create scene: {message}"
                
        except Exception as e:
            logger.error(f"Error creating new scene: {str(e)}")
            return f"❌ Error creating new scene: {str(e)}"
    
    def get_scene_info(self) -> str:
        """
        Get information about the current scene.
        
        Returns:
            Scene information string
        """
        try:
            if not is_blender_available():
                return ("Current Scene: MockScene\n"
                       "Objects: 3\n"
                       "Frame: 1 / 250\n"
                       "Render Engine: CYCLES")
            
            scene = bpy.context.scene
            object_count = len(scene.objects)
            current_frame = scene.frame_current
            frame_end = scene.frame_end
            render_engine = scene.render.engine
            
            info = [
                f"Current Scene: {scene.name}",
                f"Objects: {object_count}",
                f"Frame: {current_frame} / {frame_end}",
                f"Render Engine: {render_engine}"
            ]
            
            # Add camera info if present
            cameras = [obj for obj in scene.objects if obj.type == 'CAMERA']
            if cameras:
                active_camera = scene.camera
                if active_camera:
                    info.append(f"Active Camera: {active_camera.name}")
                info.append(f"Total Cameras: {len(cameras)}")
            
            # Add light info
            lights = [obj for obj in scene.objects if obj.type == 'LIGHT']
            if lights:
                info.append(f"Total Lights: {len(lights)}")
            
            return "\n".join(info)
            
        except Exception as e:
            logger.error(f"Error getting scene info: {str(e)}")
            return f"❌ Error getting scene info: {str(e)}"