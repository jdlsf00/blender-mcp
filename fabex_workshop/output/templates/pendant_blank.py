"""Create a simple pendant blank in Blender."""

import bpy

USE_GEOMETRY_NODES = True
GN_SUBDIV_LEVEL = 2

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



width = 0.028000
height = 0.036000
thickness = 0.003000
bail_radius = 0.001500

bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=width / 2.0, depth=thickness)
body = bpy.context.active_object
body.name = "PendantBlank"
body.scale.y = height / width

bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=bail_radius, depth=thickness * 1.4)
bail = bpy.context.active_object
bail.name = "PendantBailHole"
bail.location.y = -(height / 2.0 - bail_radius * 1.8)

modifier = body.modifiers.new(name="BailHole", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = bail
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(bail, do_unlink=True)

apply_geometry_nodes_enhancement(body, "PendantBlankGN", subdiv_level=2)

print("Created pendant blank")
