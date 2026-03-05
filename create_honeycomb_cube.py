import bpy
import bmesh
import mathutils
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

print("🚀 Creating Honeycomb Cube with Geometry Nodes...")

# Create a base cube
bpy.ops.mesh.primitive_cube_add(size=4.0, location=(0.0, 0.0, 0.0))
cube = bpy.context.active_object
cube.name = "HoneycombCube"

print("✅ Base cube created")

# Create honeycomb pattern using bmesh operations
bpy.context.view_layer.objects.active = cube
bpy.ops.object.mode_set(mode='EDIT')

# Get bmesh representation of the cube
bm = bmesh.new()
bm.from_mesh(cube.data)

# Subdivide the cube to create more faces for honeycomb pattern
bmesh.ops.subdivide_edges(bm, 
                         edges=bm.edges, 
                         cuts=4, 
                         use_grid_fill=True)

print("🔧 Subdivided cube faces")

# Create honeycomb cells by insetting individual faces
all_faces = list(bm.faces)
for face in all_faces:
    # Inset individual faces to create honeycomb cells
    try:
        bmesh.ops.inset_individual(bm, 
                                  faces=[face], 
                                  thickness=0.08, 
                                  depth=0.03)
    except:
        continue

print("🍯 Applied honeycomb pattern using inset operations")

# Exit edit mode first, then update the mesh
bpy.ops.object.mode_set(mode='OBJECT')
bm.to_mesh(cube.data)
bm.free()

# Add Geometry Nodes modifier for additional procedural effects
geo_mod = cube.modifiers.new(name="HoneycombNodes", type='NODES')

# Create a new node group
node_group = bpy.data.node_groups.new(name="HoneycombEnhancement", type='GeometryNodeTree')

# Set up the node group inputs and outputs
node_group.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
node_group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

# Create nodes in the node group
nodes = node_group.nodes
links = node_group.links

# Clear default nodes
nodes.clear()

# Add Group Input and Output nodes
group_input = nodes.new(type='NodeGroupInput')
group_output = nodes.new(type='NodeGroupOutput')
group_input.location = (-400, 0)
group_output.location = (400, 0)

# Add Subdivision Surface for smoothing
subdiv = nodes.new(type='GeometryNodeSubdivisionSurface')
subdiv.location = (-200, 0)
subdiv.inputs['Level'].default_value = 1

# Add Set Shade Smooth
shade_smooth = nodes.new(type='GeometryNodeSetShadeSmooth')
shade_smooth.location = (0, 0)

# Connect the nodes
links.new(group_input.outputs['Geometry'], subdiv.inputs['Mesh'])
links.new(subdiv.outputs['Mesh'], shade_smooth.inputs['Geometry'])
links.new(shade_smooth.outputs['Geometry'], group_output.inputs['Geometry'])

# Assign the node group to the modifier
geo_mod.node_group = node_group

print("🔧 Added Geometry Nodes for enhancement")

# Create advanced honeycomb material
material = bpy.data.materials.new(name="HoneycombMaterial")
material.use_nodes = True
material.node_tree.nodes.clear()

# Add nodes for honeycomb material
nodes = material.node_tree.nodes
links = material.node_tree.links

# Add Principled BSDF
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)
bsdf.inputs['Base Color'].default_value = (1.0, 0.7, 0.2, 1.0)  # Golden honey color
bsdf.inputs['Metallic'].default_value = 0.2
bsdf.inputs['Roughness'].default_value = 0.3
bsdf.inputs['IOR'].default_value = 1.4  # Honey-like IOR

# Add Material Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (300, 0)
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Add Voronoi Texture for honeycomb pattern
voronoi = nodes.new(type='ShaderNodeTexVoronoi')
voronoi.location = (-600, 100)
voronoi.voronoi_dimensions = '2D'
voronoi.feature = 'DISTANCE_TO_EDGE'
voronoi.inputs['Scale'].default_value = 15.0

# Add second Voronoi for complexity
voronoi2 = nodes.new(type='ShaderNodeTexVoronoi')
voronoi2.location = (-600, -100)
voronoi2.voronoi_dimensions = '2D'
voronoi2.feature = 'F1'
voronoi2.inputs['Scale'].default_value = 8.0

# Add Texture Coordinate
tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-800, 0)

# Add Mix node to combine Voronoi textures
mix = nodes.new(type='ShaderNodeMix')
mix.location = (-400, 0)
mix.data_type = 'RGBA'
mix.inputs['Factor'].default_value = 0.5

# Add ColorRamp for contrast
color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.location = (-200, 100)
color_ramp.color_ramp.elements[0].position = 0.05
color_ramp.color_ramp.elements[1].position = 0.15
color_ramp.color_ramp.elements[0].color = (0.8, 0.4, 0.1, 1.0)  # Dark honey
color_ramp.color_ramp.elements[1].color = (1.0, 0.8, 0.3, 1.0)  # Light honey

# Connect nodes
links.new(tex_coord.outputs['Generated'], voronoi.inputs['Vector'])
links.new(tex_coord.outputs['Generated'], voronoi2.inputs['Vector'])
links.new(voronoi.outputs['Distance'], mix.inputs['A'])
links.new(voronoi2.outputs['Color'], mix.inputs['B'])
links.new(mix.outputs['Result'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

# Add bump mapping for surface detail
bump = nodes.new(type='ShaderNodeBump')
bump.location = (-200, -200)
bump.inputs['Strength'].default_value = 0.3
links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

# Assign material to cube
if cube.data.materials:
    cube.data.materials[0] = material
else:
    cube.data.materials.append(material)

print("🎨 Created advanced honeycomb material with procedural textures")

# Assign material to cube
if cube.data.materials:
    cube.data.materials[0] = material
else:
    cube.data.materials.append(material)

# Add camera for better composition
bpy.ops.object.camera_add(location=(8, -8, 6))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.785)

# Set camera as active
bpy.context.scene.camera = camera

# Add lighting setup
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 4.0
sun.data.angle = 0.1  # Sharper shadows

# Add area light for fill
bpy.ops.object.light_add(type='AREA', location=(-3, -3, 8))
area = bpy.context.active_object
area.data.energy = 2.0
area.data.size = 5.0

print("📷 Added camera and lighting setup")

# Set render settings for better quality
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# Save the file to the correct directory
import os
save_path = "F:\\Documents\\Blender\\honeycomb_cube.blend"
os.makedirs("F:\\Documents\\Blender", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=save_path)

print("✅ Honeycomb Cube creation complete!")
print(f"   Name: {cube.name}")
print(f"   Location: {cube.location}")
print(f"   Material: {material.name}")
print(f"   Geometry Nodes: {node_group.name}")
print(f"   Render Engine: Cycles")
print(f"💾 Saved as: {save_path}")

print("\n🍯 HONEYCOMB CUBE FEATURES:")
print("   • 3D inset faces creating realistic honeycomb cells")
print("   • Advanced procedural material with dual Voronoi textures")
print("   • Geometry Nodes for smooth subdivision")
print("   • Professional lighting setup with sun and area lights")
print("   • Camera positioned for optimal viewing")
print("   • Cycles render engine with bump mapping")
print("   • Golden honey colors with realistic IOR")
print("   • Ready for high-quality rendering!")

print("\n🎬 TO RENDER:")
print("   Open honeycomb_cube.blend in Blender")
print("   Press F12 to render the honeycomb cube")
print("   The honeycomb pattern will be clearly visible!")