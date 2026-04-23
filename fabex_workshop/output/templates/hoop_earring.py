"""Create a hoop earring pair blank in Blender."""

import bpy

outer_d = 0.022000
wire_d = 0.002000
spacing = 0.030000

for direction in (-1, 1):
    bpy.ops.mesh.primitive_torus_add(major_radius=outer_d / 2.0, minor_radius=wire_d / 2.0, major_segments=96, minor_segments=24)
    hoop = bpy.context.active_object
    hoop.name = f"HoopEarring_{'L' if direction < 0 else 'R'}"
    hoop.location.x = direction * spacing / 2.0

print("Created hoop earring blank pair")
