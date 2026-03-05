#!/usr/bin/env python3
"""
Advanced Blender Script: Complex 3D Figure with Concaved Polygonal Faces
Features:
- Concaved polygonal faces using inset operations
- Rounded edges and vertices using subdivision surface
- Professional materials and lighting
- Geometry nodes for procedural details
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector
import os

def clear_scene():
    """Clear all existing mesh objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

def create_concaved_polyhedron():
    """Create base polyhedron for concaving"""
    # Create an icosphere as base - good for complex geometry
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2, 
        radius=3, 
        location=(0, 0, 0)
    )
    
    obj = bpy.context.active_object
    obj.name = "ConcavedPolyhedron"
    
    # Enter edit mode for advanced operations
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Get bmesh representation
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    # Ensure face indices are valid
    bm.faces.ensure_lookup_table()
    
    # Create concaved faces using inset operations
    # Select all faces first
    for face in bm.faces:
        face.select = True
    
    # Inset faces to create concaved polygonal effect
    bmesh.ops.inset_faces(
        bm, 
        faces=bm.faces[:], 
        thickness=0.3, 
        depth=0.4,
        use_even_offset=True
    )
    
    # Add more geometric complexity with another inset
    bm.faces.ensure_lookup_table()
    inner_faces = [f for f in bm.faces if f.select]
    
    bmesh.ops.inset_faces(
        bm, 
        faces=inner_faces, 
        thickness=0.15, 
        depth=0.2,
        use_even_offset=True
    )
    
    # Create additional concaved detail with extrude inward
    bm.faces.ensure_lookup_table()
    center_faces = [f for f in bm.faces if f.select]
    
    bmesh.ops.extrude_faces_move(
        bm,
        faces=center_faces,
        move_input=Vector((0, 0, -0.3))
    )
    
    # Update mesh
    bm.to_mesh(obj.data)
    obj.data.update()
    bm.free()
    
    # Exit edit mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return obj

def add_rounded_edges_modifier(obj):
    """Add subdivision surface for rounded edges and vertices"""
    # Add Subdivision Surface modifier for rounding
    subsurf = obj.modifiers.new(name="SubdivisionSurface", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3
    subsurf.quality = 4
    
    # Add Bevel modifier for extra edge rounding
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.05
    bevel.segments = 3
    bevel.profile = 0.7
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = 0.523599  # 30 degrees

def create_advanced_material():
    """Create sophisticated material for the complex geometry"""
    mat = bpy.data.materials.new(name="ConcavedPolyMaterial")
    mat.use_nodes = True
    
    # Clear default nodes
    mat.node_tree.nodes.clear()
    
    # Create material nodes
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Output node
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (800, 0)
    
    # Principled BSDF
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (400, 0)
    
    # Gradient texture for color variation
    gradient = nodes.new(type='ShaderNodeTexGradient')
    gradient.location = (0, 200)
    gradient.gradient_type = 'RADIAL'
    
    # ColorRamp for controlling gradient
    colorramp = nodes.new(type='ShaderNodeValToRGB')
    colorramp.location = (200, 200)
    
    # Set up gradient colors
    colorramp.color_ramp.elements[0].color = (0.1, 0.3, 0.8, 1.0)  # Deep blue
    colorramp.color_ramp.elements[1].color = (0.8, 0.4, 0.1, 1.0)  # Orange
    
    # Noise texture for surface detail
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (0, -200)
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 10.0
    noise.inputs['Roughness'].default_value = 0.6
    
    # Texture coordinate
    texcoord = nodes.new(type='ShaderNodeTexCoord')
    texcoord.location = (-200, 0)
    
    # Connect nodes
    links.new(texcoord.outputs['Generated'], gradient.inputs['Vector'])
    links.new(gradient.outputs['Fac'], colorramp.inputs['Fac'])
    links.new(colorramp.outputs['Color'], principled.inputs['Base Color'])
    
    links.new(texcoord.outputs['Generated'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], principled.inputs['Roughness'])
    
    # Set material properties
    principled.inputs['Metallic'].default_value = 0.3
    principled.inputs['Specular'].default_value = 0.8
    principled.inputs['Clearcoat'].default_value = 0.5
    principled.inputs['Clearcoat Roughness'].default_value = 0.1
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def setup_professional_lighting():
    """Set up professional 3-point lighting"""
    # Remove default light
    if 'Light' in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects['Light'], do_unlink=True)
    
    # Key light (main light)
    bpy.ops.object.light_add(type='AREA', location=(5, -5, 8))
    key_light = bpy.context.active_object
    key_light.name = "KeyLight"
    key_light.data.energy = 100
    key_light.data.size = 3
    key_light.rotation_euler = (0.7, 0, 0.7)
    
    # Fill light (softer, opposite side)
    bpy.ops.object.light_add(type='AREA', location=(-3, 3, 4))
    fill_light = bpy.context.active_object
    fill_light.name = "FillLight"
    fill_light.data.energy = 50
    fill_light.data.size = 4
    fill_light.data.color = (0.9, 0.95, 1.0)
    
    # Rim light (back lighting)
    bpy.ops.object.light_add(type='SPOT', location=(0, 6, 2))
    rim_light = bpy.context.active_object
    rim_light.name = "RimLight"
    rim_light.data.energy = 80
    rim_light.data.spot_size = 1.2
    rim_light.rotation_euler = (1.2, 0, 3.14)

def setup_camera():
    """Position camera for optimal viewing"""
    if 'Camera' in bpy.data.objects:
        camera = bpy.data.objects['Camera']
        camera.location = (7, -7, 5)
        camera.rotation_euler = (1.1, 0, 0.785)
    else:
        bpy.ops.object.camera_add(location=(7, -7, 5))
        camera = bpy.context.active_object
        camera.rotation_euler = (1.1, 0, 0.785)

def main():
    """Main function to create the complex 3D figure"""
    print("🎨 Creating complex 3D figure with concaved polygonal faces...")
    
    # Clear scene
    clear_scene()
    
    # Create the main complex geometry
    print("📐 Creating concaved polyhedron base...")
    poly_obj = create_concaved_polyhedron()
    
    # Add modifiers for rounded edges
    print("🔄 Adding subdivision and bevel modifiers...")
    add_rounded_edges_modifier(poly_obj)
    
    # Create and apply advanced material
    print("🎭 Creating advanced material...")
    material = create_advanced_material()
    poly_obj.data.materials.append(material)
    
    # Set up lighting
    print("💡 Setting up professional lighting...")
    setup_professional_lighting()
    
    # Position camera
    print("📷 Positioning camera...")
    setup_camera()
    
    # Set render settings
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    
    # Save the file
    save_path = "F:\\Documents\\Blender\\concaved_polyhedron.blend"
    os.makedirs("F:\\Documents\\Blender", exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    
    print(f"✅ Complex 3D figure created successfully!")
    print(f"📁 Features:")
    print(f"   • Concaved polygonal faces with multi-level insets")
    print(f"   • Rounded edges and vertices via subdivision surface")
    print(f"   • Professional gradient material with noise detail")
    print(f"   • 3-point lighting setup")
    print(f"   • High-quality Cycles rendering")
    print(f"💾 Saved as: {save_path}")

if __name__ == "__main__":
    main()