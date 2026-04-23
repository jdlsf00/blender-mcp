"""Create a gallery ring blank in Blender."""

import bpy

outer_radius = 0.012000
inner_radius = 0.009100
gallery_width = 0.014000
gallery_height = 0.008000
shank_thickness = 0.002400

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=outer_radius, depth=shank_thickness)
ring = bpy.context.active_object
ring.name = "GalleryRingOuter"

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=inner_radius, depth=shank_thickness * 1.2)
inner = bpy.context.active_object
inner.name = "GalleryRingInner"

cut = ring.modifiers.new(name="InnerCut", type='BOOLEAN')
cut.operation = 'DIFFERENCE'
cut.object = inner
bpy.context.view_layer.objects.active = ring
bpy.ops.object.modifier_apply(modifier=cut.name)
bpy.data.objects.remove(inner, do_unlink=True)

bpy.ops.mesh.primitive_cube_add(size=1.0)
gallery = bpy.context.active_object
gallery.name = "GalleryTop"
gallery.scale = (gallery_width / 2.0, shank_thickness / 2.0, gallery_height / 2.0)
gallery.location.y = -outer_radius
gallery.location.z = gallery_height / 2.0

print("Created gallery ring blank")
