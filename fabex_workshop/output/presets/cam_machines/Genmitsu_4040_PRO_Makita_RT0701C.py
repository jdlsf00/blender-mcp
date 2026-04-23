### Genmitsu_4040_PRO_Makita_RT0701C.py ###

import bpy

d = bpy.context.scene.cam_machine
s = bpy.context.scene.unit_settings

s.system, s.length_unit = ("METRIC", "MILLIMETERS")

d.post_processor = "GRBL"
d.unit_system = "MILLIMETERS"
d.use_position_definitions = True
d.starting_position = (0.000000, 0.000000, 0.015000)
d.mtc_position = (0.000000, 0.000000, 0.015000)
d.ending_position = (0.000000, 0.000000, 0.015000)
d.working_area = (0.400000, 0.400000, 0.078000)
d.feedrate_min = 0.050000
d.feedrate_max = 1.800000
d.feedrate_default = 0.900000
d.spindle_min = 10000
d.spindle_max = 30000
d.spindle_default = 18000
d.axis_4 = False
d.axis_5 = False

if hasattr(d, "rotary_axis_1"):
    d.rotary_axis_1 = "X"

print("Loaded machine preset: Genmitsu_4040_PRO_Makita_RT0701C")
