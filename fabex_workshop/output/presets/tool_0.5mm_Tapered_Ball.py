"""Generated tool preset for 0.5mm_Tapered_Ball."""

import bpy

scene = bpy.context.scene
if not hasattr(scene, "cam_operations") or not scene.cam_operations:
    raise RuntimeError("Create or select a Fabex CAM operation before loading this preset")

operation = scene.cam_operations[scene.cam_active_operation]
operation.cutter_type = "BALLNOSE"
operation.cutter_diameter = 0.000500
operation.cutter_flutes = 2
operation.spindle_rpm = 12000
operation.feedrate = 0.350000
operation.plunge_feedrate = 0.120000
operation.stepover = 0.150000
operation.stepdown = 0.000250

print("Loaded tool preset: 0.5mm_Tapered_Ball")
