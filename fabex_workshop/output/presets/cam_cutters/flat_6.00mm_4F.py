import bpy

d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

d.cutter_type = "END"
d.cutter_diameter = 0.006000
d.cutter_length = 25.0
d.cutter_tip_angle = 60.0

if hasattr(d, "cutter_flutes"):
    d.cutter_flutes = 4

d.spindle_rpm = 10000
d.feedrate = 0.900000
d.plunge_feedrate = 0.250000
d.stepover = 0.400000
d.stepdown = 0.001500
