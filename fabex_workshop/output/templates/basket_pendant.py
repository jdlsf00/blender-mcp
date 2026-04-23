"""Create a basket pendant blank in Blender."""

import bpy

outer_radius = 0.012000
seat_radius = 0.008000
thickness = 0.002600
bail_radius = 0.001400

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=outer_radius, depth=thickness)
pendant = bpy.context.active_object
pendant.name = "BasketPendant"

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=seat_radius, depth=thickness * 0.45)
seat = bpy.context.active_object
seat.name = "BasketSeat"
seat.location.z = thickness * 0.2

seat_cut = pendant.modifiers.new(name="SeatCut", type='BOOLEAN')
seat_cut.operation = 'DIFFERENCE'
seat_cut.object = seat
bpy.context.view_layer.objects.active = pendant
bpy.ops.object.modifier_apply(modifier=seat_cut.name)
bpy.data.objects.remove(seat, do_unlink=True)

bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=bail_radius, depth=thickness * 1.5)
bail = bpy.context.active_object
bail.name = "PendantBailHole"
bail.location.y = -(outer_radius + bail_radius * 0.2)

bail_cut = pendant.modifiers.new(name="BailCut", type='BOOLEAN')
bail_cut.operation = 'DIFFERENCE'
bail_cut.object = bail
bpy.context.view_layer.objects.active = pendant
bpy.ops.object.modifier_apply(modifier=bail_cut.name)
bpy.data.objects.remove(bail, do_unlink=True)

print("Created basket pendant blank")
