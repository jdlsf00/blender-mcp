"""Generated tool preset for 6mm_Flat_Endmill_4F."""

import bpy

scene = bpy.context.scene
if not hasattr(scene, "cam_operations") or not scene.cam_operations:
    raise RuntimeError("Create or select a Fabex CAM operation before loading this preset")

operation = scene.cam_operations[scene.cam_active_operation]
operation.cutter_type = "ENDMILL"
operation.cutter_diameter = 0.006000
operation.cutter_flutes = 4
operation.spindle_rpm = 10000
operation.feedrate = 0.900000
operation.plunge_feedrate = 0.250000
operation.stepover = 0.400000
operation.stepdown = 0.001500

print("Loaded tool preset: 6mm_Flat_Endmill_4F")
