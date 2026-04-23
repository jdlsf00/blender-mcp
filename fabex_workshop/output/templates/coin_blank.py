"""Create a coin blank in Blender."""

import bpy

diameter = 0.032000
thickness = 0.003000

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=diameter / 2.0, depth=thickness)
coin = bpy.context.active_object
coin.name = "CoinBlank"

print("Created coin blank")
