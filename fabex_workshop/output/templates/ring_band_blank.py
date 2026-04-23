"""Create a parametric ring/band blank in Blender."""

import bpy

outer_radius = 0.012000
inner_radius = 0.009100
thickness = 0.006000

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=outer_radius, depth=thickness)
outer_obj = bpy.context.active_object
outer_obj.name = "RingBandOuter"

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=inner_radius, depth=thickness * 1.2)
inner_obj = bpy.context.active_object
inner_obj.name = "RingBandInner"

modifier = outer_obj.modifiers.new(name="InnerCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = inner_obj
bpy.context.view_layer.objects.active = outer_obj
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(inner_obj, do_unlink=True)

print("Created parametric ring/band blank")
