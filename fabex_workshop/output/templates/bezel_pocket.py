"""Create a bezel pocket blank in Blender."""

import bpy

outer_width = 0.020000
outer_height = 0.016000
depth = 0.005000
stone_width = 0.016000
stone_height = 0.012000

bpy.ops.mesh.primitive_cube_add(size=1.0)
base = bpy.context.active_object
base.name = "BezelBlank"
base.scale = (outer_width / 2.0, outer_height / 2.0, depth / 2.0)

bpy.ops.mesh.primitive_cube_add(size=1.0)
seat = bpy.context.active_object
seat.name = "BezelSeat"
seat.scale = (stone_width / 2.0, stone_height / 2.0, depth / 3.0)
seat.location.z = depth / 6.0

modifier = base.modifiers.new(name="SeatCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = seat
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(seat, do_unlink=True)

print("Created parametric bezel pocket")
