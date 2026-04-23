import bpy
from pathlib import Path

bpy.ops.scene.cam_operation_add()

scene = bpy.context.scene
o = scene.cam_operations[scene.cam_active_operation]

o.ambient_behaviour = "ALL"
o.cutter_type = "END"
o.feedrate = 0.900000
o.plunge_feedrate = 0.250000
o.filename = o.name = f"{scene.cam_names.operation_name_full}_{Path(__file__).stem}"
o.movement_type = "MEANDER"
o.skin = 0.000150
o.spindle = 10000.0
o.stepdown = 0.001500
o.strategy = "POCKET"

if hasattr(o, "distance_between_paths"):
    o.distance_between_paths = 0.000400
