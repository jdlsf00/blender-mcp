"""Create a toggle bracelet component blank set in Blender."""

import bpy

length = 0.024000
width = 0.004000
thickness = 0.002000
ring_outer = 0.007000
ring_inner = 0.004500

bpy.ops.mesh.primitive_cube_add(size=1.0)
bar = bpy.context.active_object
bar.name = "ToggleBar"
bar.scale = (length / 2.0, width / 2.0, thickness / 2.0)

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=ring_outer, depth=thickness)
ring = bpy.context.active_object
ring.name = "ToggleRingOuter"
ring.location.x = length * 0.95

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=ring_inner, depth=thickness * 1.2)
inner = bpy.context.active_object
inner.name = "ToggleRingInner"
inner.location.x = length * 0.95

cut = ring.modifiers.new(name="InnerCut", type='BOOLEAN')
cut.operation = 'DIFFERENCE'
cut.object = inner
bpy.context.view_layer.objects.active = ring
bpy.ops.object.modifier_apply(modifier=cut.name)
bpy.data.objects.remove(inner, do_unlink=True)

print("Created toggle bracelet blank set")
