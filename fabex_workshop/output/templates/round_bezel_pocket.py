"""Create a round bezel pocket blank in Blender."""

import bpy

outer_diameter = 0.018000
stone_diameter = 0.014000
depth = 0.004500

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=outer_diameter / 2.0, depth=depth)
base = bpy.context.active_object
base.name = "RoundBezelBlank"

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=stone_diameter / 2.0, depth=depth / 2.0)
seat = bpy.context.active_object
seat.name = "RoundBezelSeat"
seat.location.z = depth / 6.0

modifier = base.modifiers.new(name="SeatCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = seat
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(seat, do_unlink=True)

print("Created round bezel pocket")
