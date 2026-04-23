"""Generated operation preset for Pocket_Finishing."""

import bpy

scene = bpy.context.scene
if not hasattr(scene, "cam_operations") or not scene.cam_operations:
    raise RuntimeError("Create or select a Fabex CAM operation before loading this preset")

operation = scene.cam_operations[scene.cam_active_operation]
operation.strategy = "PARALLEL"
operation.cutter_type = "BALLNOSE"
operation.spindle_rpm = 12000
operation.feedrate = 0.350000
operation.plunge_feedrate = 0.120000
operation.stepover = 0.120000
operation.stepdown = 0.000250

if hasattr(operation, "skin"):
    operation.skin = 0.000000

print("Loaded operation preset: Pocket_Finishing")
