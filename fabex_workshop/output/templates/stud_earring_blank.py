"""Create a stud earring blank pair in Blender."""

import bpy

diameter = 0.010000
thickness = 0.002000
spacing = 0.018000

for direction in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=diameter / 2.0, depth=thickness)
        disc = bpy.context.active_object
        disc.name = f"StudBlank_{'L' if direction < 0 else 'R'}"
        disc.location.x = direction * spacing / 2.0

print("Created stud earring blank pair")
