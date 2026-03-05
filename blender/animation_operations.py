"""
Animation operations for the Blender MCP server.

This module provides safe wrappers around Blender's animation operations.
"""

import logging
from typing import Tuple, List, Dict, Any, Optional
from .blender_utils import (
    safe_execute, bpy, get_object_by_name, 
    is_blender_available
)

logger = logging.getLogger(__name__)

class AnimationOperations:
    """Handles animation and keyframe operations."""
    
    def set_keyframe(self, object_name: str, frame: int, 
                    property_type: str = "location") -> str:
        """
        Set a keyframe for an object property.
        
        Args:
            object_name: Name of the object
            frame: Frame number to set keyframe
            property_type: Type of property (location, rotation, scale)
            
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return f"✅ Mock: Set {property_type} keyframe for '{object_name}' at frame {frame}"
            
            obj = get_object_by_name(object_name)
            if not obj:
                return f"❌ Object '{object_name}' not found"
            
            # Set current frame
            bpy.context.scene.frame_set(frame)
            
            # Select the object
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            
            # Map property types to data paths
            property_map = {
                'location': 'location',
                'rotation': 'rotation_euler',
                'scale': 'scale'
            }
            
            data_path = property_map.get(property_type.lower())
            if not data_path:
                available = ', '.join(property_map.keys())
                return f"❌ Invalid property type '{property_type}'. Available: {available}"
            
            # Insert keyframe
            obj.keyframe_insert(data_path=data_path, frame=frame)
            
            return f"✅ Set {property_type} keyframe for '{object_name}' at frame {frame}"
            
        except Exception as e:
            logger.error(f"Error setting keyframe: {str(e)}")
            return f"❌ Error setting keyframe: {str(e)}"
    
    def animate_object_movement(self, object_name: str, start_frame: int, end_frame: int,
                               start_location: Tuple[float, float, float],
                               end_location: Tuple[float, float, float]) -> str:
        """
        Animate an object moving from one location to another.
        
        Args:
            object_name: Name of the object to animate
            start_frame: Starting frame
            end_frame: Ending frame
            start_location: Starting position (x, y, z)
            end_location: Ending position (x, y, z)
            
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return f"✅ Mock: Animated '{object_name}' from {start_location} to {end_location} (frames {start_frame}-{end_frame})"
            
            obj = get_object_by_name(object_name)
            if not obj:
                return f"❌ Object '{object_name}' not found"
            
            if start_frame >= end_frame:
                return f"❌ Start frame ({start_frame}) must be less than end frame ({end_frame})"
            
            # Clear existing location keyframes
            obj.animation_data_clear()
            
            # Set starting keyframe
            bpy.context.scene.frame_set(start_frame)
            obj.location = start_location
            obj.keyframe_insert(data_path="location", frame=start_frame)
            
            # Set ending keyframe
            bpy.context.scene.frame_set(end_frame)
            obj.location = end_location
            obj.keyframe_insert(data_path="location", frame=end_frame)
            
            # Set linear interpolation for smooth movement
            if obj.animation_data and obj.animation_data.action:
                for fcurve in obj.animation_data.action.fcurves:
                    if fcurve.data_path == "location":
                        for keyframe in fcurve.keyframe_points:
                            keyframe.interpolation = 'LINEAR'
            
            return f"✅ Animated '{object_name}' from {start_location} to {end_location} (frames {start_frame}-{end_frame})"
            
        except Exception as e:
            logger.error(f"Error animating object movement: {str(e)}")
            return f"❌ Error animating object movement: {str(e)}"
    
    def animate_rotation(self, object_name: str, start_frame: int, end_frame: int,
                        axis: str = "Z", degrees: float = 360) -> str:
        """
        Animate an object rotating around an axis.
        
        Args:
            object_name: Name of the object to animate
            start_frame: Starting frame
            end_frame: Ending frame  
            axis: Rotation axis (X, Y, or Z)
            degrees: Rotation amount in degrees
            
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return f"✅ Mock: Animated '{object_name}' rotation {degrees}° around {axis}-axis (frames {start_frame}-{end_frame})"
            
            obj = get_object_by_name(object_name)
            if not obj:
                return f"❌ Object '{object_name}' not found"
            
            if start_frame >= end_frame:
                return f"❌ Start frame ({start_frame}) must be less than end frame ({end_frame})"
            
            axis = axis.upper()
            if axis not in ['X', 'Y', 'Z']:
                return f"❌ Invalid axis '{axis}'. Use X, Y, or Z"
            
            import math
            radians = math.radians(degrees)
            
            # Get current rotation
            current_rotation = list(obj.rotation_euler)
            axis_index = {'X': 0, 'Y': 1, 'Z': 2}[axis]
            
            # Set starting keyframe (current rotation)
            bpy.context.scene.frame_set(start_frame)
            obj.keyframe_insert(data_path="rotation_euler", frame=start_frame)
            
            # Set ending keyframe (rotated)
            bpy.context.scene.frame_set(end_frame)
            current_rotation[axis_index] += radians
            obj.rotation_euler = current_rotation
            obj.keyframe_insert(data_path="rotation_euler", frame=end_frame)
            
            # Set linear interpolation
            if obj.animation_data and obj.animation_data.action:
                for fcurve in obj.animation_data.action.fcurves:
                    if fcurve.data_path == "rotation_euler":
                        for keyframe in fcurve.keyframe_points:
                            keyframe.interpolation = 'LINEAR'
            
            return f"✅ Animated '{object_name}' rotation {degrees}° around {axis}-axis (frames {start_frame}-{end_frame})"
            
        except Exception as e:
            logger.error(f"Error animating rotation: {str(e)}")
            return f"❌ Error animating rotation: {str(e)}"
    
    def animate_scale(self, object_name: str, start_frame: int, end_frame: int,
                     start_scale: float = 1.0, end_scale: float = 2.0) -> str:
        """
        Animate an object scaling.
        
        Args:
            object_name: Name of the object to animate
            start_frame: Starting frame
            end_frame: Ending frame
            start_scale: Starting scale factor
            end_scale: Ending scale factor
            
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return f"✅ Mock: Animated '{object_name}' scale from {start_scale} to {end_scale} (frames {start_frame}-{end_frame})"
            
            obj = get_object_by_name(object_name)
            if not obj:
                return f"❌ Object '{object_name}' not found"
            
            if start_frame >= end_frame:
                return f"❌ Start frame ({start_frame}) must be less than end frame ({end_frame})"
            
            # Set starting keyframe
            bpy.context.scene.frame_set(start_frame)
            obj.scale = (start_scale, start_scale, start_scale)
            obj.keyframe_insert(data_path="scale", frame=start_frame)
            
            # Set ending keyframe
            bpy.context.scene.frame_set(end_frame)
            obj.scale = (end_scale, end_scale, end_scale)
            obj.keyframe_insert(data_path="scale", frame=end_frame)
            
            # Set linear interpolation
            if obj.animation_data and obj.animation_data.action:
                for fcurve in obj.animation_data.action.fcurves:
                    if fcurve.data_path == "scale":
                        for keyframe in fcurve.keyframe_points:
                            keyframe.interpolation = 'LINEAR'
            
            return f"✅ Animated '{object_name}' scale from {start_scale} to {end_scale} (frames {start_frame}-{end_frame})"
            
        except Exception as e:
            logger.error(f"Error animating scale: {str(e)}")
            return f"❌ Error animating scale: {str(e)}"
    
    def set_frame_range(self, start_frame: int, end_frame: int) -> str:
        """
        Set the animation frame range.
        
        Args:
            start_frame: Starting frame of animation
            end_frame: Ending frame of animation
            
        Returns:
            Status message
        """
        try:
            if start_frame >= end_frame:
                return f"❌ Start frame ({start_frame}) must be less than end frame ({end_frame})"
            
            if not is_blender_available():
                return f"✅ Mock: Set frame range to {start_frame}-{end_frame}"
            
            scene = bpy.context.scene
            scene.frame_start = start_frame
            scene.frame_end = end_frame
            scene.frame_current = start_frame
            
            return f"✅ Set animation frame range to {start_frame}-{end_frame}"
            
        except Exception as e:
            logger.error(f"Error setting frame range: {str(e)}")
            return f"❌ Error setting frame range: {str(e)}"
    
    def play_animation(self) -> str:
        """
        Start playing the animation.
        
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return "✅ Mock: Started animation playback"
            
            # Start animation playback
            bpy.ops.screen.animation_play()
            
            return "✅ Started animation playback"
            
        except Exception as e:
            logger.error(f"Error playing animation: {str(e)}")
            return f"❌ Error playing animation: {str(e)}"
    
    def stop_animation(self) -> str:
        """
        Stop playing the animation.
        
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return "✅ Mock: Stopped animation playback"
            
            # Stop animation playback
            bpy.ops.screen.animation_cancel()
            
            return "✅ Stopped animation playback"
            
        except Exception as e:
            logger.error(f"Error stopping animation: {str(e)}")
            return f"❌ Error stopping animation: {str(e)}"
    
    def goto_frame(self, frame: int) -> str:
        """
        Go to a specific frame.
        
        Args:
            frame: Frame number to go to
            
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return f"✅ Mock: Went to frame {frame}"
            
            scene = bpy.context.scene
            
            # Clamp frame to valid range
            frame = max(scene.frame_start, min(scene.frame_end, frame))
            
            scene.frame_set(frame)
            
            return f"✅ Went to frame {frame}"
            
        except Exception as e:
            logger.error(f"Error going to frame: {str(e)}")
            return f"❌ Error going to frame: {str(e)}"
    
    def clear_animation(self, object_name: str) -> str:
        """
        Clear all animation data from an object.
        
        Args:
            object_name: Name of the object
            
        Returns:
            Status message
        """
        try:
            if not is_blender_available():
                return f"✅ Mock: Cleared animation from '{object_name}'"
            
            obj = get_object_by_name(object_name)
            if not obj:
                return f"❌ Object '{object_name}' not found"
            
            # Clear animation data
            obj.animation_data_clear()
            
            return f"✅ Cleared animation from '{object_name}'"
            
        except Exception as e:
            logger.error(f"Error clearing animation: {str(e)}")
            return f"❌ Error clearing animation: {str(e)}"
    
    def get_animation_info(self, object_name: Optional[str] = None) -> str:
        """
        Get information about animation in the scene or for a specific object.
        
        Args:
            object_name: Optional object name to get specific info
            
        Returns:
            Animation information string
        """
        try:
            if not is_blender_available():
                if object_name:
                    return f"Mock animation info for '{object_name}':\n- Location keyframes: 2\n- Rotation keyframes: 0\n- Scale keyframes: 1"
                else:
                    return "Mock scene animation info:\n- Frame range: 1-250\n- Current frame: 1\n- Animated objects: 1"
            
            scene = bpy.context.scene
            info = []
            
            if object_name:
                # Get info for specific object
                obj = get_object_by_name(object_name)
                if not obj:
                    return f"❌ Object '{object_name}' not found"
                
                info.append(f"Animation info for '{object_name}':")
                
                if obj.animation_data and obj.animation_data.action:
                    action = obj.animation_data.action
                    info.append(f"- Action: {action.name}")
                    
                    # Count keyframes by type
                    location_keyframes = 0
                    rotation_keyframes = 0
                    scale_keyframes = 0
                    
                    for fcurve in action.fcurves:
                        if fcurve.data_path == "location":
                            location_keyframes += len(fcurve.keyframe_points)
                        elif fcurve.data_path == "rotation_euler":
                            rotation_keyframes += len(fcurve.keyframe_points)
                        elif fcurve.data_path == "scale":
                            scale_keyframes += len(fcurve.keyframe_points)
                    
                    info.append(f"- Location keyframes: {location_keyframes}")
                    info.append(f"- Rotation keyframes: {rotation_keyframes}")
                    info.append(f"- Scale keyframes: {scale_keyframes}")
                else:
                    info.append("- No animation data")
            else:
                # Get general scene animation info
                info.append("Scene animation info:")
                info.append(f"- Frame range: {scene.frame_start}-{scene.frame_end}")
                info.append(f"- Current frame: {scene.frame_current}")
                
                # Count animated objects
                animated_objects = 0
                for obj in scene.objects:
                    if obj.animation_data and obj.animation_data.action:
                        animated_objects += 1
                
                info.append(f"- Animated objects: {animated_objects}")
            
            return "\n".join(info)
            
        except Exception as e:
            logger.error(f"Error getting animation info: {str(e)}")
            return f"❌ Error getting animation info: {str(e)}"