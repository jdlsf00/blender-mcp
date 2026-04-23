"""Create a parametric ring/band blank in Blender."""

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



outer_radius = 0.012000
inner_radius = 0.009100
thickness = 0.006000

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=outer_radius, depth=thickness)
outer_obj = bpy.context.active_object
outer_obj.name = "RingBandOuter"

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=inner_radius, depth=thickness * 1.2)
inner_obj = bpy.context.active_object
inner_obj.name = "RingBandInner"

modifier = outer_obj.modifiers.new(name="InnerCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = inner_obj
bpy.context.view_layer.objects.active = outer_obj
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(inner_obj, do_unlink=True)

apply_geometry_nodes_enhancement(outer_obj, "RingBandGN", subdiv_level=1)

print("Created parametric ring/band blank")
