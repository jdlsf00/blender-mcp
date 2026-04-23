"""Create a parametric tray mold blank in Blender."""

import bpy

width = 0.100000
height = 0.070000
depth = 0.010000
pocket_margin = 0.007000
corner_radius = 0.010000

bpy.ops.mesh.primitive_cube_add(size=1.0)
blank = bpy.context.active_object
blank.name = "TrayMoldBlank"
blank.scale = (width / 2.0, height / 2.0, depth / 2.0)

bpy.ops.mesh.primitive_cube_add(size=1.0)
pocket = bpy.context.active_object
pocket.name = "TrayPocket"
pocket.scale = ((width - pocket_margin * 2.0) / 2.0, (height - pocket_margin * 2.0) / 2.0, depth / 2.0)
pocket.location.z = pocket_margin / 2.0

bevel = pocket.modifiers.new(name="CornerRadius", type='BEVEL')
bevel.width = corner_radius
bevel.segments = 8
bpy.context.view_layer.objects.active = pocket
bpy.ops.object.modifier_apply(modifier=bevel.name)

modifier = blank.modifiers.new(name="PocketCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = pocket
bpy.context.view_layer.objects.active = blank
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(pocket, do_unlink=True)

print("Created parametric tray mold blank")
