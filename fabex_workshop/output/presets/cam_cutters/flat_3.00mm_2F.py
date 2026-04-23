import bpy

d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

d.cutter_type = "END"
d.cutter_diameter = 0.003000
d.cutter_length = 25.0
d.cutter_tip_angle = 60.0

if hasattr(d, "cutter_flutes"):
    d.cutter_flutes = 2

d.spindle_rpm = 12000
d.feedrate = 0.700000
d.plunge_feedrate = 0.180000
d.stepover = 0.350000
d.stepdown = 0.001000
