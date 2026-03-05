import bpy

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create a UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.0,
    location=(0.0, 0.0, 0.0)
)

# Get the created sphere
sphere = bpy.context.active_object
sphere.name = "CopilotSphere"

# Add a basic material
material = bpy.data.materials.new(name="SphereMaterial")
material.use_nodes = True
material.node_tree.nodes.clear()

# Add Principled BSDF
bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.2, 0.6, 1.0, 1.0)  # Blue color
bsdf.inputs['Metallic'].default_value = 0.3
bsdf.inputs['Roughness'].default_value = 0.4

# Add Material Output
output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material to sphere
if sphere.data.materials:
    sphere.data.materials[0] = material
else:
    sphere.data.materials.append(material)

print("✅ Sphere created successfully!")
print(f"   Name: {sphere.name}")
print(f"   Location: {sphere.location}")
print(f"   Material: {material.name}")

# Save the file to the correct directory
import os
save_path = "F:\\Documents\\Blender\\copilot_sphere.blend"
os.makedirs("F:\\Documents\\Blender", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=save_path)
print(f"💾 Saved as: {save_path}")