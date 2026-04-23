"""Create a bezel pocket blank in Blender."""

import bpy

USE_GEOMETRY_NODES = True
GN_SUBDIV_LEVEL = 1

def apply_geometry_nodes_enhancement(target_obj, group_name, subdiv_level=GN_SUBDIV_LEVEL):
    if not USE_GEOMETRY_NODES:
        return
    try:
        geo_mod = target_obj.modifiers.new(name="GNEnhance", type='NODES')
        node_group = bpy.data.node_groups.new(name=group_name, type='GeometryNodeTree')
        geo_mod.node_group = node_group

        node_group.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        node_group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

        nodes = node_group.nodes
        links = node_group.links
        nodes.clear()

        group_input = nodes.new(type='NodeGroupInput')
        group_input.location = (-420, 0)

        subdiv = nodes.new(type='GeometryNodeSubdivisionSurface')
        subdiv.location = (-150, 0)
        subdiv.inputs['Level'].default_value = max(0, int(subdiv_level))

        shade_smooth = nodes.new(type='GeometryNodeSetShadeSmooth')
        shade_smooth.location = (110, 0)
        shade_smooth.inputs['Shade Smooth'].default_value = True

        group_output = nodes.new(type='NodeGroupOutput')
        group_output.location = (360, 0)

        links.new(group_input.outputs['Geometry'], subdiv.inputs['Mesh'])
        links.new(subdiv.outputs['Mesh'], shade_smooth.inputs['Geometry'])
        links.new(shade_smooth.outputs['Geometry'], group_output.inputs['Geometry'])
    except Exception as exc:
        print("Geometry Nodes enhancement skipped:", exc)



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

apply_geometry_nodes_enhancement(base, "BezelPocketGN", subdiv_level=1)

print("Created parametric bezel pocket")
