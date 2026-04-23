"""Create a pierced bezel ring blank in Blender."""

import bpy

outer_radius = 0.012000
inner_radius = 0.009100
bezel_radius = 0.005000
thickness = 0.002400

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=outer_radius, depth=thickness)
ring = bpy.context.active_object
ring.name = "PiercedBezelRingOuter"

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=inner_radius, depth=thickness * 1.2)
inner = bpy.context.active_object
inner.name = "PiercedBezelRingInner"

cut = ring.modifiers.new(name="InnerCut", type='BOOLEAN')
cut.operation = 'DIFFERENCE'
cut.object = inner
bpy.context.view_layer.objects.active = ring
bpy.ops.object.modifier_apply(modifier=cut.name)
bpy.data.objects.remove(inner, do_unlink=True)

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=bezel_radius, depth=thickness)
bezel = bpy.context.active_object
bezel.name = "PiercedBezelTop"
bezel.location.y = -outer_radius
bezel.location.z = thickness / 2.0

print("Created pierced bezel ring blank")
