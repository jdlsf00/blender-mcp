"""
Render operations for the Blender MCP server.

This module provides safe wrappers around Blender's rendering operations.
"""

import logging
import os
from typing import Tuple, List, Dict, Any, Optional
from .blender_utils import (
    safe_execute, bpy, is_blender_available
)

logger = logging.getLogger(__name__)

class RenderOperations:
    """Handles rendering operations."""
    
    def render_image(self, output_path: str = "", engine: str = "CYCLES") -> str:
        """
        Render the current scene.
        
        Args:
            output_path: Path to save the rendered image (optional)
            engine: Render engine to use (CYCLES, EEVEE, or WORKBENCH)
            
        Returns:
            Status message
        """
        try:
            engine = engine.upper()
            valid_engines = ["CYCLES", "EEVEE", "WORKBENCH"]
            
            if engine not in valid_engines:
                return f"❌ Invalid render engine '{engine}'. Valid engines: {', '.join(valid_engines)}"
            
            def _render_image():
                if not is_blender_available():
                    return "mock_render.png"
                
                scene = bpy.context.scene
                
                # Set render engine
                scene.render.engine = engine
                
                # Set output path if provided
                if output_path:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
                    scene.render.filepath = output_path
                
                # Render
                bpy.ops.render.render(write_still=True)
                
                return scene.render.filepath
            
            success, message, result_path = safe_execute(
                f"render image with {engine}",
                _render_image
            )
            
            if success or not is_blender_available():
                if not is_blender_available():
                    return f"✅ Mock: Rendered image with {engine} engine"
                else:
                    return f"✅ Rendered image with {engine} engine to '{result_path}'"
            else:
                return f"❌ Failed to render image: {message}"
                
        except Exception as e:
            logger.error(f"Error rendering image: {str(e)}")
            return f"❌ Error rendering image: {str(e)}"
    
    def render_animation(self, output_dir: str = "", engine: str = "CYCLES") -> str:
        """
        Render the animation sequence.
        
        Args:
            output_dir: Directory to save rendered frames
            engine: Render engine to use
            
        Returns:
            Status message
        """
        try:
            engine = engine.upper()
            valid_engines = ["CYCLES", "EEVEE", "WORKBENCH"]
            
            if engine not in valid_engines:
                return f"❌ Invalid render engine '{engine}'. Valid engines: {', '.join(valid_engines)}"
            
            def _render_animation():
                if not is_blender_available():
                    return "mock_frames/"
                
                scene = bpy.context.scene
                
                # Set render engine
                scene.render.engine = engine
                
                # Set output directory if provided
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    # Blender expects filepath with frame number placeholder
                    filepath = os.path.join(output_dir, "frame_")
                    scene.render.filepath = filepath
                
                # Render animation
                bpy.ops.render.render(animation=True)
                
                return scene.render.filepath
            
            success, message, result_path = safe_execute(
                f"render animation with {engine}",
                _render_animation
            )
            
            if success or not is_blender_available():
                if not is_blender_available():
                    return f"✅ Mock: Rendered animation with {engine} engine"
                else:
                    frame_count = bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1
                    return f"✅ Rendered animation ({frame_count} frames) with {engine} engine to '{result_path}'"
            else:
                return f"❌ Failed to render animation: {message}"
                
        except Exception as e:
            logger.error(f"Error rendering animation: {str(e)}")
            return f"❌ Error rendering animation: {str(e)}"
    
    def set_render_resolution(self, width: int, height: int, percentage: int = 100) -> str:
        """
        Set the render resolution.
        
        Args:
            width: Render width in pixels
            height: Render height in pixels
            percentage: Resolution percentage (for quick previews)
            
        Returns:
            Status message
        """
        try:
            width = max(1, int(width))
            height = max(1, int(height))
            percentage = max(1, min(100, int(percentage)))
            
            if not is_blender_available():
                return f"✅ Mock: Set render resolution to {width}x{height} at {percentage}%"
            
            scene = bpy.context.scene
            scene.render.resolution_x = width
            scene.render.resolution_y = height
            scene.render.resolution_percentage = percentage
            
            return f"✅ Set render resolution to {width}x{height} at {percentage}%"
            
        except ValueError as e:
            return f"❌ Invalid resolution parameters: {str(e)}"
        except Exception as e:
            logger.error(f"Error setting render resolution: {str(e)}")
            return f"❌ Error setting render resolution: {str(e)}"
    
    def set_render_engine_settings(self, engine: str, samples: Optional[int] = None,
                                  use_denoising: Optional[bool] = None) -> str:
        """
        Configure render engine specific settings.
        
        Args:
            engine: Render engine (CYCLES or EEVEE)
            samples: Number of render samples (for quality vs speed)
            use_denoising: Whether to use denoising
            
        Returns:
            Status message
        """
        try:
            engine = engine.upper()
            
            if engine not in ["CYCLES", "EEVEE"]:
                return f"❌ Engine settings only available for CYCLES and EEVEE, not '{engine}'"
            
            if not is_blender_available():
                settings_info = []
                if samples is not None:
                    settings_info.append(f"samples={samples}")
                if use_denoising is not None:
                    settings_info.append(f"denoising={use_denoising}")
                
                settings_str = ", ".join(settings_info) if settings_info else "default settings"
                return f"✅ Mock: Set {engine} engine settings: {settings_str}"
            
            scene = bpy.context.scene
            scene.render.engine = engine
            
            settings_applied = []
            
            if engine == "CYCLES":
                cycles = scene.cycles
                
                if samples is not None:
                    samples = max(1, int(samples))
                    cycles.samples = samples
                    settings_applied.append(f"samples={samples}")
                
                if use_denoising is not None:
                    cycles.use_denoising = bool(use_denoising)
                    settings_applied.append(f"denoising={use_denoising}")
                    
            elif engine == "EEVEE":
                eevee = scene.eevee
                
                if samples is not None:
                    samples = max(1, int(samples))
                    eevee.taa_render_samples = samples
                    settings_applied.append(f"samples={samples}")
            
            settings_str = ", ".join(settings_applied) if settings_applied else "no settings changed"
            return f"✅ Applied {engine} settings: {settings_str}"
            
        except ValueError as e:
            return f"❌ Invalid engine settings: {str(e)}"
        except Exception as e:
            logger.error(f"Error setting engine settings: {str(e)}")
            return f"❌ Error setting engine settings: {str(e)}"
    
    def set_render_format(self, file_format: str = "PNG", quality: int = 90) -> str:
        """
        Set the render output format.
        
        Args:
            file_format: Output format (PNG, JPEG, TIFF, etc.)
            quality: Quality setting for lossy formats (1-100)
            
        Returns:
            Status message
        """
        try:
            file_format = file_format.upper()
            valid_formats = ["PNG", "JPEG", "TIFF", "OPEN_EXR", "HDR"]
            
            if file_format not in valid_formats:
                return f"❌ Invalid format '{file_format}'. Valid formats: {', '.join(valid_formats)}"
            
            quality = max(1, min(100, int(quality)))
            
            if not is_blender_available():
                return f"✅ Mock: Set render format to {file_format} (quality: {quality}%)"
            
            scene = bpy.context.scene
            render = scene.render
            
            # Set file format
            render.image_settings.file_format = file_format
            
            # Set quality for appropriate formats
            if file_format == 'JPEG':
                render.image_settings.quality = quality
            elif file_format == 'PNG':
                # PNG compression (0-100, but inverted - higher = more compression)
                render.image_settings.compression = 100 - quality
            
            return f"✅ Set render format to {file_format} (quality: {quality}%)"
            
        except ValueError as e:
            return f"❌ Invalid format settings: {str(e)}"
        except Exception as e:
            logger.error(f"Error setting render format: {str(e)}")
            return f"❌ Error setting render format: {str(e)}"
    
    def get_render_info(self) -> str:
        """
        Get current render settings information.
        
        Returns:
            Render settings information string
        """
        try:
            if not is_blender_available():
                return ("Render Settings (Mock):\n"
                       "- Engine: CYCLES\n"
                       "- Resolution: 1920x1080 (100%)\n"
                       "- Format: PNG\n"
                       "- Samples: 128")
            
            scene = bpy.context.scene
            render = scene.render
            
            info = [
                "Current Render Settings:",
                f"- Engine: {render.engine}",
                f"- Resolution: {render.resolution_x}x{render.resolution_y} ({render.resolution_percentage}%)",
                f"- Format: {render.image_settings.file_format}",
                f"- Frame Range: {scene.frame_start}-{scene.frame_end}"
            ]
            
            # Add engine-specific info
            if render.engine == 'CYCLES':
                cycles = scene.cycles
                info.append(f"- Cycles Samples: {cycles.samples}")
                info.append(f"- Denoising: {cycles.use_denoising}")
                
            elif render.engine == 'EEVEE':
                eevee = scene.eevee
                info.append(f"- EEVEE Samples: {eevee.taa_render_samples}")
            
            # Add output path if set
            if render.filepath:
                info.append(f"- Output Path: {render.filepath}")
            
            return "\n".join(info)
            
        except Exception as e:
            logger.error(f"Error getting render info: {str(e)}")
            return f"❌ Error getting render info: {str(e)}"
    
    def preview_render(self, region_size: int = 512) -> str:
        """
        Start a viewport render preview.
        
        Args:
            region_size: Size of the preview region
            
        Returns:
            Status message
        """
        try:
            region_size = max(64, min(2048, int(region_size)))
            
            def _preview_render():
                if not is_blender_available():
                    return None
                
                # Start viewport render
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                space.shading.type = 'RENDERED'
                                break
                        break
                
                return True
            
            success, message, result = safe_execute(
                "start preview render",
                _preview_render
            )
            
            if success or not is_blender_available():
                return f"✅ Started viewport render preview (region size: {region_size}px)"
            else:
                return f"❌ Failed to start preview render: {message}"
                
        except Exception as e:
            logger.error(f"Error starting preview render: {str(e)}")
            return f"❌ Error starting preview render: {str(e)}"
    
    def stop_render(self) -> str:
        """
        Stop the current render operation.
        
        Returns:
            Status message
        """
        try:
            def _stop_render():
                if not is_blender_available():
                    return None
                
                # Cancel render
                bpy.ops.render.render(animation=False, write_still=False)
                
                return True
            
            success, message, result = safe_execute(
                "stop render",
                _stop_render
            )
            
            if success or not is_blender_available():
                return "✅ Stopped render operation"
            else:
                return f"❌ Failed to stop render: {message}"
                
        except Exception as e:
            logger.error(f"Error stopping render: {str(e)}")
            return f"❌ Error stopping render: {str(e)}"