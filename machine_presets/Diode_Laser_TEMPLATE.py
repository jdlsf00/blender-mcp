"""
Machine Preset: Diode Laser (TEMPLATE)
Type: CO2/Diode laser engraving/cutting
Controller: Typically GRBL-based
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
WORK_AREA_X_MM = 400  # TODO: Replace with your X travel
WORK_AREA_Y_MM = 400  # TODO: Replace with your Y travel
WORK_AREA_Z_MM = 50   # TODO: Replace with your Z focus range

# Laser speeds (in mm/min)
ENGRAVING_SPEED = 200   # TODO: Replace with your engraving speed
CUTTING_SPEED = 100     # TODO: Replace with your cutting speed (slower)
TRAVEL_SPEED = 3000     # TODO: Replace with your rapid travel speed

# Laser power range
MAX_LASER_POWER_PERCENT = 100  # Typically 0-100 or 0-1000

# Post-processor
POST_PROCESSOR = 'grbl'  # Most diode lasers use GRBL

# Controller type
CONTROLLER_TYPE = "GRBL 1.1 / LaserGRBL"  # TODO: Your controller name

# ============================================================
# END CONFIGURATION
# ============================================================

if not hasattr(scene, 'cam_machine'):
    print("⚠️ Fabex not properly initialized")
    print("   Make sure Fabex addon is enabled")
else:
    machine = scene.cam_machine

    print("\n" + "="*60)
    print("LOADING: Diode Laser Preset")
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
    machine.starting_position.z = WORK_AREA_Z_MM / 1000.0  # Top of focus range
    print(f"✓ Starting position: X0 Y0 Z{WORK_AREA_Z_MM:.0f}mm")

    # Laser "spindle" (actually laser power control)
    machine.spindle_default_rpm = 0  # Not applicable
    print(f"✓ Spindle RPM: N/A (laser power via M3/M4 S parameter)")

    # Feed rates (convert mm/min to m/min)
    machine.feed_default = ENGRAVING_SPEED / 1000.0
    print(f"✓ Engraving speed: {ENGRAVING_SPEED} mm/min")

    machine.plunge_default = TRAVEL_SPEED / 1000.0
    print(f"✓ Travel speed: {TRAVEL_SPEED} mm/min")

    print("\n✅ Diode Laser preset loaded!")
    print("="*60 + "\n")

    print("⚠️  IMPORTANT: Review and adjust settings above!")
    print("    Update the configuration section with your actual specs.")
    print("\nMachine Specifications:")
    print(f"  • Controller: {CONTROLLER_TYPE}")
    print(f"  • Work area: {WORK_AREA_X_MM} × {WORK_AREA_Y_MM} mm")
    print(f"  • Z focus range: {WORK_AREA_Z_MM} mm")
    print(f"  • Engraving speed: {ENGRAVING_SPEED} mm/min")
    print(f"  • Cutting speed: {CUTTING_SPEED} mm/min")
    print(f"  • Travel speed: {TRAVEL_SPEED} mm/min")
    print(f"  • Post-processor: {POST_PROCESSOR}")
    print(f"  • Laser power: 0-{MAX_LASER_POWER_PERCENT}% (via S parameter)")
    print("\n💡 Laser control:")
    print("   M3 Sxxx = Constant power mode")
    print("   M4 Sxxx = Dynamic power mode (speed-adjusted)")
    print("   M5 = Laser off")
    print("")

    print("📝 Notes for Fabex:")
    print("   • Use 'Engrave' strategy for raster engraving")
    print("   • Use 'Cutout' or 'Profile' for vector cutting")
    print("   • Set 'spindle speed' to desired laser power %")
    print("   • Enable 'Use Modulation' if available")
    print("")
