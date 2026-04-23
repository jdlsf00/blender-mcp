"""Create a dogtag blank in Blender."""

import bpy

width = 0.028000
height = 0.050000
thickness = 0.002000
hole_radius = 0.001750

bpy.ops.mesh.primitive_cube_add(size=1.0)
body = bpy.context.active_object
body.name = "DogtagBlank"
body.scale = (width / 2.0, height / 2.0, thickness / 2.0)

bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=hole_radius, depth=thickness * 1.4)
hole = bpy.context.active_object
hole.name = "DogtagHole"
hole.location.y = -(height / 2.0 - hole_radius * 2.2)

modifier = body.modifiers.new(name="TopHole", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = hole
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(hole, do_unlink=True)

print("Created dogtag blank")
