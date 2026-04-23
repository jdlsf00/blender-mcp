"""Generated operation preset for Pocket_Roughing."""

import bpy

scene = bpy.context.scene
if not hasattr(scene, "cam_operations") or not scene.cam_operations:
    raise RuntimeError("Create or select a Fabex CAM operation before loading this preset")

operation = scene.cam_operations[scene.cam_active_operation]
operation.strategy = "POCKET"
operation.cutter_type = "ENDMILL"
operation.spindle_rpm = 10000
operation.feedrate = 0.900000
operation.plunge_feedrate = 0.250000
operation.stepover = 0.400000
operation.stepdown = 0.001500

if hasattr(operation, "skin"):
    operation.skin = 0.000150

print("Loaded operation preset: Pocket_Roughing")
