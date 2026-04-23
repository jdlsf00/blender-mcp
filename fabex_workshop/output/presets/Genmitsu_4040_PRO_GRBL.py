"""Generated machine preset for Genmitsu_4040_PRO_GRBL."""

import bpy

scene = bpy.context.scene

if not hasattr(scene, "cam_machine"):
    raise RuntimeError("Fabex CAM machine settings are not available in this scene")

machine = scene.cam_machine
machine.post_processor = "grbl"
machine.working_area.x = 0.400000
machine.working_area.y = 0.400000
machine.working_area.z = 0.078000
machine.use_position_definitions = True
machine.starting_position.x = 0.000000
machine.starting_position.y = 0.000000
machine.starting_position.z = 0.015000

if hasattr(machine, "rotary_axis_1"):
    machine.rotary_axis_1 = "X"

machine.spindle_default_rpm = 10000
machine.feed_default = 0.900000
machine.plunge_default = 0.250000

print("Loaded machine preset: Genmitsu_4040_PRO_GRBL")
