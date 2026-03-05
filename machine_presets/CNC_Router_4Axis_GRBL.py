"""
Machine Preset: CNC Router 4-Axis XYZA
Controller: GRBL
Work Envelope: 800×800×200mm + Rotary A-axis
Spindle: 12000 RPM max
Feed Rate: 500 mm/min standard

To use:
1. In Blender, open Text Editor
2. Load this file
3. Run script (Alt+P)
4. Machine settings applied to scene
"""

import bpy

scene = bpy.context.scene

# Ensure we have a CAM machine property
if not hasattr(scene, 'cam_machine'):
    print("⚠️ Fabex not properly initialized")
    print("   Make sure Fabex addon is enabled")
else:
    machine = scene.cam_machine

    print("\n" + "="*60)
    print("LOADING: CNC Router 4-Axis GRBL Preset")
    print("="*60)

    # Post-processor
    machine.post_processor = 'grbl'
    print(f"✓ Post-processor: {machine.post_processor}")

    # Work envelope (in meters for Blender)
    machine.working_area.x = 0.800  # 800mm
    machine.working_area.y = 0.800  # 800mm
    machine.working_area.z = 0.200  # 200mm
    print(f"✓ Work envelope: {machine.working_area.x*1000:.0f} × {machine.working_area.y*1000:.0f} × {machine.working_area.z*1000:.0f} mm")

    # Machine position limits
    machine.use_position_definitions = True

    # Starting position (home)
    machine.starting_position.x = 0.0
    machine.starting_position.y = 0.0
    machine.starting_position.z = 0.050  # 50mm above table
    print(f"✓ Home position: X{machine.starting_position.x*1000:.0f} Y{machine.starting_position.y*1000:.0f} Z{machine.starting_position.z*1000:.0f}")

    # Rotary axis configuration
    if hasattr(machine, 'rotary_axis_1'):
        machine.rotary_axis_1 = 'X'  # A-axis rotates around X
        print(f"✓ Rotary axis: {machine.rotary_axis_1}-axis")

    # Spindle configuration
    machine.spindle_default_rpm = 12000
    print(f"✓ Default spindle speed: {machine.spindle_default_rpm} RPM")

    # Default feed rates (in meters/min for Blender)
    machine.feed_default = 0.500  # 500 mm/min
    print(f"✓ Default feed rate: {machine.feed_default*1000:.0f} mm/min")

    # Plunge rate
    machine.plunge_default = 0.250  # 250 mm/min
    print(f"✓ Plunge rate: {machine.plunge_default*1000:.0f} mm/min")

    print("\n✅ CNC Router 4-Axis GRBL preset loaded successfully!")
    print("="*60 + "\n")

    print("Machine Specifications:")
    print("  • Controller: GRBL")
    print("  • Axes: X, Y, Z, A (rotary)")
    print("  • X travel: -400 to +400 mm (800mm)")
    print("  • Y travel: -400 to +400 mm (800mm)")
    print("  • Z travel: -150 to +50 mm (200mm)")
    print("  • A-axis: Rotary (unlimited rotation)")
    print("  • Tool: 6mm end mill, 4-flute")
    print("  • Spindle: 12000 RPM")
    print("  • Feed: 500 mm/min")
    print("")
