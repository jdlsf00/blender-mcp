"""Create a flat cuff bracelet blank in Blender."""

import bpy

length = 0.160000
width = 0.028000
thickness = 0.002000

bpy.ops.mesh.primitive_cube_add(size=1.0)
blank = bpy.context.active_object
blank.name = "CuffBlank"
blank.scale = (length / 2.0, width / 2.0, thickness / 2.0)

print("Created cuff bracelet blank")
