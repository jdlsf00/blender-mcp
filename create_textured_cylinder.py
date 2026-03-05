#!/usr/bin/env python3
"""
Create textured cylinder visualization in Blender from heightmap
Shows the actual relief surface, not just the toolpath
"""

import bpy
import bmesh
import math
from PIL import Image
import numpy as np
import sys
import os

# Parse command line arguments
if "--" in sys.argv:
    argv = sys.argv[sys.argv.index("--") + 1:]
else:
    argv = []

if len(argv) < 1:
    print("Usage: blender --python create_textured_cylinder.py -- <heightmap_image>")
    sys.exit(1)

heightmap_path = argv[0]
output_blend = argv[1] if len(argv) > 1 else "textured_cylinder.blend"

print(f"\n{'='*60}")
print("  TEXTURED CYLINDER GENERATOR")
print(f"{'='*60}")
print(f"Heightmap: {heightmap_path}")
print(f"Output: {output_blend}")

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Load heightmap
print("\n📂 Loading heightmap...")
img = Image.open(heightmap_path).convert('L')
heightmap = np.array(img, dtype=np.float32) / 255.0
height_px, width_px = heightmap.shape
print(f"   Size: {width_px}x{height_px} pixels")

# Parameters
cylinder_radius = 20.0  # mm
cylinder_height = 100.0  # mm
max_relief = 5.0  # mm

print(f"\n⚙️ Cylinder parameters:")
print(f"   Base radius: {cylinder_radius}mm")
print(f"   Height: {cylinder_height}mm")
print(f"   Max relief: {max_relief}mm")

# Create mesh
print("\n🔨 Creating mesh...")
mesh = bpy.data.meshes.new("ReliefCylinder")
obj = bpy.data.objects.new("ReliefCylinder", mesh)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()

# Generate vertices
print("   Generating vertices...")
vertices = []
for h_idx in range(height_px):
    for w_idx in range(width_px):
        # Position along cylinder
        z = (h_idx / height_px) * cylinder_height
        angle = (w_idx / width_px) * 2 * math.pi

        # Get relief height from heightmap
        height_val = heightmap[h_idx, w_idx]

        # Calculate radius (black=deep, white=surface)
        radius = cylinder_radius - max_relief * (1.0 - height_val)

        # Convert to cartesian
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        vert = bm.verts.new((x, y, z))
        vertices.append(vert)

print(f"   Created {len(vertices)} vertices")

# Create faces
print("   Creating faces...")
bm.verts.ensure_lookup_table()
face_count = 0

for h in range(height_px - 1):
    for w in range(width_px - 1):
        # Get vertex indices
        v1 = h * width_px + w
        v2 = h * width_px + (w + 1)
        v3 = (h + 1) * width_px + (w + 1)
        v4 = (h + 1) * width_px + w

        try:
            face = bm.faces.new([
                bm.verts[v1],
                bm.verts[v2],
                bm.verts[v3],
                bm.verts[v4]
            ])
            face_count += 1
        except:
            pass  # Skip if face already exists

print(f"   Created {face_count} faces")

# Update mesh
bm.to_mesh(mesh)
bm.free()

# Smooth shading
print("   Applying smooth shading...")
for face in mesh.polygons:
    face.use_smooth = True

# Create material with texture
print("\n🎨 Creating material...")
mat = bpy.data.materials.new("ReliefMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Add nodes
output = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
img_texture = nodes.new('ShaderNodeTexImage')

# Load texture image
img_texture.image = bpy.data.images.load(heightmap_path)

# Connect nodes
links.new(img_texture.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material
obj.data.materials.append(mat)

print("   Material applied")

# Add camera
print("\n📷 Setting up camera...")
cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam

# Position camera
cam.location = (150, -150, cylinder_height/2)
cam.rotation_euler = (math.radians(90), 0, math.radians(45))

# Add light
print("   Adding light...")
light_data = bpy.data.lights.new("Light", 'SUN')
light_data.energy = 2.0
light = bpy.data.objects.new("Light", light_data)
bpy.context.collection.objects.link(light)
light.location = (50, 50, 100)

# Save
print(f"\n💾 Saving: {output_blend}")
bpy.ops.wm.save_as_mainfile(filepath=output_blend)

print(f"\n{'='*60}")
print("  ✅ COMPLETE")
print(f"{'='*60}")
print(f"\nOpen with:")
print(f'  & "C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe" "{output_blend}"')
print()
