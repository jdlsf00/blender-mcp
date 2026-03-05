"""
Machine Preset: MOPA Fiber Laser (TEMPLATE)
Type: Fiber laser marking/engraving
Work Envelope: NEED YOUR SPECS

TODO: Fill in your actual machine specifications below
Then run in Blender Text Editor (Alt+P)
"""

import bpy

scene = bpy.context.scene

# ============================================================
# CONFIGURE YOUR MACHINE SPECS HERE
# ============================================================

# Work envelope (in mm - will convert to meters)
WORK_AREA_X_MM = 300  # TODO: Replace with your X travel
WORK_AREA_Y_MM = 300  # TODO: Replace with your Y travel
WORK_AREA_Z_MM = 100  # TODO: Replace with your Z focus range

# Marking speeds (in mm/min)
MARKING_SPEED = 100   # TODO: Replace with your marking speed
TRAVEL_SPEED = 1000   # TODO: Replace with your rapid travel speed

# Post-processor
POST_PROCESSOR = 'iso'  # TODO: May need custom laser post-processor

# Controller type
CONTROLLER_TYPE = "Fiber Laser Controller"  # TODO: Your controller name

# ============================================================
# END CONFIGURATION
# ============================================================

if not hasattr(scene, 'cam_machine'):
    print("⚠️ Fabex not properly initialized")
    print("   Make sure Fabex addon is enabled")
else:
    machine = scene.cam_machine

    print("\n" + "="*60)
    print("LOADING: MOPA Fiber Laser Preset")
    print("="*60)

    # Post-processor
    machine.post_processor = POST_PROCESSOR
    print(f"✓ Post-processor: {machine.post_processor}")

    # Work envelope (convert mm to meters)
    machine.working_area.x = WORK_AREA_X_MM / 1000.0
    machine.working_area.y = WORK_AREA_Y_MM / 1000.0
    machine.working_area.z = WORK_AREA_Z_MM / 1000.0
    print(f"✓ Work envelope: {WORK_AREA_X_MM} × {WORK_AREA_Y_MM} × {WORK_AREA_Z_MM} mm")

    # Machine position
    machine.use_position_definitions = True
    machine.starting_position.x = 0.0
    machine.starting_position.y = 0.0
    machine.starting_position.z = WORK_AREA_Z_MM / 2000.0  # Mid-focus height
    print(f"✓ Starting position: Center, Z={WORK_AREA_Z_MM/2:.0f}mm")

    # Laser "spindle" (actually laser power control)
    machine.spindle_default_rpm = 0  # Not applicable for lasers
    print(f"✓ Spindle RPM: N/A (laser power via M3 S parameter)")

    # Feed rates (convert mm/min to m/min)
    machine.feed_default = MARKING_SPEED / 1000.0
    print(f"✓ Marking speed: {MARKING_SPEED} mm/min")

    machine.plunge_default = TRAVEL_SPEED / 1000.0
    print(f"✓ Travel speed: {TRAVEL_SPEED} mm/min")

    print("\n✅ MOPA Fiber Laser preset loaded!")
    print("="*60 + "\n")

    print("⚠️  IMPORTANT: Review and adjust settings above!")
    print("    Update the configuration section with your actual specs.")
    print("\nMachine Specifications:")
    print(f"  • Controller: {CONTROLLER_TYPE}")
    print(f"  • Work area: {WORK_AREA_X_MM} × {WORK_AREA_Y_MM} mm")
    print(f"  • Z focus range: {WORK_AREA_Z_MM} mm")
    print(f"  • Marking speed: {MARKING_SPEED} mm/min")
    print(f"  • Travel speed: {TRAVEL_SPEED} mm/min")
    print(f"  • Post-processor: {POST_PROCESSOR}")
    print("\n💡 Laser power controlled via G-code M3 S value")
    print("   (S0-S1000 or S0-S100 depending on controller)")
    print("")
