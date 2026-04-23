"""Create a parametric signet ring blank in Blender."""

import bpy

face_width = 0.016000
face_height = 0.013000
inner_radius = 0.009500
shank_depth = 0.005500

bpy.ops.mesh.primitive_cube_add(size=1.0)
face = bpy.context.active_object
face.name = "SignetFace"
face.scale = (face_width / 2.0, shank_depth / 2.0, face_height / 2.0)
face.location.z = face_height / 2.0

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=inner_radius * 1.4, depth=shank_depth)
band = bpy.context.active_object
band.name = "SignetBand"
band.rotation_euler.x = 1.57079632679

bpy.context.view_layer.objects.active = face
join_result = bpy.ops.object.join()
print(join_result)

print("Created parametric signet blank")
