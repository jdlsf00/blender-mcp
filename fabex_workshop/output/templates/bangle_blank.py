"""Create a bangle blank in Blender."""

import bpy

outer_radius = 0.039000
inner_radius = 0.032000
width = 0.018000

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=outer_radius, depth=width)
outer_obj = bpy.context.active_object
outer_obj.name = "BangleBlankOuter"

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=inner_radius, depth=width * 1.2)
inner_obj = bpy.context.active_object
inner_obj.name = "BangleBlankInner"

modifier = outer_obj.modifiers.new(name="InnerCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = inner_obj
bpy.context.view_layer.objects.active = outer_obj
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(inner_obj, do_unlink=True)

print("Created bangle blank")
