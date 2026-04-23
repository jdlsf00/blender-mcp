"""Create an oval bezel pocket blank in Blender."""

import bpy

outer_width = 0.022000
outer_height = 0.028000
depth = 0.005000
stone_width = 0.016000
stone_height = 0.022000

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=outer_width / 2.0, depth=depth)
base = bpy.context.active_object
base.name = "OvalBezelBlank"
base.scale.y = outer_height / outer_width

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=stone_width / 2.0, depth=depth / 2.0)
seat = bpy.context.active_object
seat.name = "OvalBezelSeat"
seat.scale.y = stone_height / stone_width
seat.location.z = depth / 6.0

modifier = base.modifiers.new(name="SeatCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = seat
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(seat, do_unlink=True)

print("Created oval bezel pocket")
