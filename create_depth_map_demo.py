#!/usr/bin/env python3
"""
Practical Depth Map Demo - Create object and generate depth map
This demonstrates the complete workflow from 3D creation to CNC-ready depth map
"""

import bpy
import os

def create_demo_sculpture():
    """Create a complex sculptural object for depth map demonstration"""
    
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    
    # Create base sculpture with multiple elements
    print("🎨 Creating demo sculpture...")
    
    # Main body - UV sphere with deformation
    bpy.ops.mesh.primitive_uv_sphere_add(radius=2, location=(0, 0, 0))
    sculpture = bpy.context.active_object
    sculpture.name = "DemoSculpture"
    
    # Enter edit mode for deformation
    bpy.context.view_layer.objects.active = sculpture
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Add some geometric detail with proportional editing
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.tosphere(value=0.7)
    bpy.ops.mesh.subdivide(number_cuts=2)
    
    # Add displacement for surface detail
    bpy.ops.object.mode_set(mode='OBJECT')
    displace_mod = sculpture.modifiers.new(name="Displacement", type='DISPLACE')
    displace_mod.strength = 0.3
    
    # Add secondary elements
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=3, location=(1.5, 0, 0))
    cylinder = bpy.context.active_object
    cylinder.name = "DetailCylinder"
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.5, 0, 1))
    cube = bpy.context.active_object
    cube.name = "DetailCube"
    
    # Apply boolean union to combine objects
    bool_mod = sculpture.modifiers.new(name="Union1", type='BOOLEAN')
    bool_mod.operation = 'UNION'
    bool_mod.object = cylinder
    
    bool_mod2 = sculpture.modifiers.new(name="Union2", type='BOOLEAN')
    bool_mod2.operation = 'UNION'
    bool_mod2.object = cube
    
    # Apply modifiers
    bpy.context.view_layer.objects.active = sculpture
    bpy.ops.object.modifier_apply(modifier="Displacement")
    bpy.ops.object.modifier_apply(modifier="Union1")
    bpy.ops.object.modifier_apply(modifier="Union2")
    
    # Remove helper objects
    bpy.data.objects.remove(cylinder, do_unlink=True)
    bpy.data.objects.remove(cube, do_unlink=True)
    
    # Add smooth shading
    bpy.ops.object.shade_smooth()
    
    print(f"✅ Created complex sculpture: {sculpture.name}")
    return sculpture.name

def main():
    """Main demonstration function"""
    print("🎯 Depth Map Generation Demo")
    print("=" * 40)
    
    # Create demo sculpture
    sculpture_name = create_demo_sculpture()
    
    # Save the scene
    save_path = "F:\\Documents\\Blender\\depth_map_demo.blend"
    os.makedirs("F:\\Documents\\Blender", exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    
    print(f"📁 Demo sculpture saved: {save_path}")
    print(f"🎨 Sculpture name: {sculpture_name}")
    print()
    print("🚀 Ready for depth map generation!")
    print("📡 Now you can ask GitHub Copilot:")
    print(f"   'Generate a depth map from {sculpture_name} for CNC carving'")
    print(f"   'Create top-view depth map at 1024 resolution'")
    print(f"   'Make inverted depth map for engraving operations'")

if __name__ == "__main__":
    main()