"""Create a simple pendant blank in Blender."""

import bpy

width = 0.028000
height = 0.036000
thickness = 0.003000
bail_radius = 0.001500

bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=width / 2.0, depth=thickness)
body = bpy.context.active_object
body.name = "PendantBlank"
body.scale.y = height / width

bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=bail_radius, depth=thickness * 1.4)
bail = bpy.context.active_object
bail.name = "PendantBailHole"
bail.location.y = -(height / 2.0 - bail_radius * 1.8)

modifier = body.modifiers.new(name="BailHole", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = bail
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(bail, do_unlink=True)

print("Created pendant blank")
