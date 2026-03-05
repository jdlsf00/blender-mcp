#!/usr/bin/env python3
"""
Simple test to verify Blender operations work in mock mode
"""

import sys
import os

# Add the blender modules to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "blender"))

try:
    from blender.mesh_operations import MeshOperations
    from blender.material_operations import MaterialOperations
    from blender.scene_operations import SceneOperations
    from blender.animation_operations import AnimationOperations
    from blender.render_operations import RenderOperations
    
    print("✅ Successfully imported all Blender operation modules")
    
    # Test creating instances
    mesh_ops = MeshOperations()
    material_ops = MaterialOperations()
    scene_ops = SceneOperations()
    animation_ops = AnimationOperations()
    render_ops = RenderOperations()
    
    print("✅ Successfully created all operation instances")
    
    # Test a simple operation in mock mode
    result = mesh_ops.create_cube("test_cube", (0, 0, 0))
    print(f"✅ Mesh cube creation result: {result}")
    
    # Test scene operations
    objects = scene_ops.get_scene_objects()
    print(f"✅ Scene objects: {objects}")
    
    # Test material operations
    result = material_ops.create_material("test_material", (1.0, 0.5, 0.3, 1.0))
    print(f"✅ Material creation result: {result}")
    
    print("\n🎉 All basic tests passed! Blender operations are working in mock mode.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error during testing: {e}")
    sys.exit(1)