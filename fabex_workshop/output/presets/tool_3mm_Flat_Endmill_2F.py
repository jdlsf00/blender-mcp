"""Generated tool preset for 3mm_Flat_Endmill_2F."""

import bpy

scene = bpy.context.scene
if not hasattr(scene, "cam_operations") or not scene.cam_operations:
    raise RuntimeError("Create or select a Fabex CAM operation before loading this preset")

operation = scene.cam_operations[scene.cam_active_operation]
operation.cutter_type = "ENDMILL"
operation.cutter_diameter = 0.003000
operation.cutter_flutes = 2
operation.spindle_rpm = 12000
operation.feedrate = 0.700000
operation.plunge_feedrate = 0.180000
operation.stepover = 0.350000
operation.stepdown = 0.001000

print("Loaded tool preset: 3mm_Flat_Endmill_2F")
