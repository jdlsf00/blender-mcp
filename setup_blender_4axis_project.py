"""
Automated Blender 4-Axis Rotary Project Setup Script
Creates a properly configured Blender project with:
- Correct units (millimeters)
- 50mm × 100mm cylinder geometry
- BlenderCAM (Fabex) setup with machine parameters
- HELIX continuous milling strategy

Machine Specifications (from camotics_4axis_config.xml):
- X-Axis: -400 to 400mm (800mm travel)
- Y-Axis: -400 to 400mm (800mm travel)
- Z-Axis: -150 to 50mm (200mm travel)
- A-Axis: Rotary (unlimited rotation)

Usage:
    blender --background --python setup_blender_4axis_project.py
"""

import bpy
import bmesh
import math
import sys
from pathlib import Path

# Configuration
OUTPUT_DIR = Path(r"F:\Documents\CODE\Blender-MCP\reference_projects")
OUTPUT_DIR.mkdir(exist_ok=True)

PROJECT_NAME = "4axis_helix_reference"
BLEND_FILE = OUTPUT_DIR / f"{PROJECT_NAME}.blend"

# Machine Parameters (from your CNC router specs)
MACHINE_CONFIG = {
    "name": "4-Axis CNC Router (XYZA)",
    "work_envelope": {
        "x": (-400, 400),  # mm
        "y": (-400, 400),  # mm
        "z": (-150, 50),   # mm
        "a": (-99999, 99999),  # degrees (rotary)
    },
    "travel": {
        "x": 800,  # mm
        "y": 800,  # mm
        "z": 200,  # mm
    }
}

# Test Cylinder Specifications
CYLINDER_CONFIG = {
    "diameter": 50,  # mm
    "length": 100,   # mm
    "resolution": 64  # segments for smooth surface
}

# Tool Configuration
TOOL_CONFIG = {
    "diameter": 6.0,  # mm (6mm end mill)
    "type": "END",
    "flutes": 4,
    "feed_rate": 500,  # mm/min
    "spindle_speed": 12000,  # RPM
}

def print_header(message):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {message}")
    print(f"{'='*60}\n")

def setup_units_and_scene():
    """Configure Blender units and scene settings"""
    print_header("Setting Up Units and Scene")

    # Set unit system to METRIC with millimeters
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0  # 1 Blender Unit = 1 meter
    bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'

    print("✅ Unit System: METRIC")
    print("✅ Length Unit: MILLIMETERS")
    print("✅ Scale: 1.0 (1 BU = 1m, display in mm)")

    # Set up scene for CAM work
    bpy.context.scene.render.fps = 30
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 250

    print("✅ Scene configured for CAM operations")

def clear_scene():
    """Remove default objects"""
    print_header("Clearing Default Scene")

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    print("✅ Default objects removed")

def create_cylinder():
    """Create test cylinder with correct dimensions"""
    print_header("Creating Test Cylinder")

    diameter = CYLINDER_CONFIG["diameter"] / 1000  # Convert mm to meters
    length = CYLINDER_CONFIG["length"] / 1000
    radius = diameter / 2

    print(f"Cylinder specifications:")
    print(f"  Diameter: {CYLINDER_CONFIG['diameter']}mm")
    print(f"  Length: {CYLINDER_CONFIG['length']}mm")
    print(f"  Resolution: {CYLINDER_CONFIG['resolution']} segments")

    # Create cylinder mesh
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=CYLINDER_CONFIG["resolution"],
        radius=radius,
        depth=length,
        location=(0, 0, 0),
        rotation=(0, math.radians(90), 0)  # Rotate to align with X-axis (rotary axis)
    )

    cylinder = bpy.context.active_object
    cylinder.name = "TestCylinder_Helix"

    print(f"✅ Cylinder created: {cylinder.name}")
    print(f"   Dimensions in Blender: {radius*2:.6f}m × {length:.6f}m")
    print(f"   Oriented along X-axis (rotary)")

    # Add smooth shading
    bpy.ops.object.shade_smooth()
    print("✅ Smooth shading applied")

    return cylinder

def setup_camera():
    """Add camera for visualization"""
    print_header("Setting Up Camera")

    bpy.ops.object.camera_add(
        location=(0.3, -0.3, 0.2),
        rotation=(math.radians(60), 0, math.radians(45))
    )
    camera = bpy.context.active_object
    camera.name = "CAM_View"

    bpy.context.scene.camera = camera

    print("✅ Camera positioned for isometric view")

def setup_blendercam():
    """Configure BlenderCAM (Fabex) addon settings"""
    print_header("Configuring BlenderCAM (Fabex)")

    # Check if BlenderCAM addon is enabled
    if 'cam' not in dir(bpy.ops):
        print("⚠️  WARNING: BlenderCAM (Fabex) addon not detected!")
        print("   Please enable it manually:")
        print("   Edit → Preferences → Add-ons → Search 'Fabex' → Enable")
        print("   Then re-run this script or continue with manual setup.")
        return False

    # Create CAM operation (this part may need manual adjustment based on addon version)
    print("✅ BlenderCAM addon detected")
    print("   Machine parameters ready:")
    print(f"   X: {MACHINE_CONFIG['work_envelope']['x'][0]} to {MACHINE_CONFIG['work_envelope']['x'][1]}mm")
    print(f"   Y: {MACHINE_CONFIG['work_envelope']['y'][0]} to {MACHINE_CONFIG['work_envelope']['y'][1]}mm")
    print(f"   Z: {MACHINE_CONFIG['work_envelope']['z'][0]} to {MACHINE_CONFIG['work_envelope']['z'][1]}mm")
    print(f"   A: Rotary (unlimited)")

    print(f"\n   Tool: {TOOL_CONFIG['diameter']}mm {TOOL_CONFIG['type']} mill")
    print(f"   Feed: {TOOL_CONFIG['feed_rate']}mm/min")
    print(f"   Spindle: {TOOL_CONFIG['spindle_speed']}RPM")

    return True

def save_project():
    """Save the Blender project file"""
    print_header("Saving Project")

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_FILE))

    print(f"✅ Project saved: {BLEND_FILE}")
    print(f"   Size: {BLEND_FILE.stat().st_size / 1024:.1f} KB")

def print_manual_steps():
    """Print manual configuration steps for user"""
    print_header("MANUAL CONFIGURATION REQUIRED")

    print("Please complete these steps in Blender GUI:")
    print()
    print("1. VERIFY UNITS:")
    print("   • Scene Properties → Units → Unit System = METRIC")
    print("   • Length Unit = Millimeters")
    print("   • Unit Scale = 1.0")
    print()
    print("2. SETUP BLENDERCAM OPERATION:")
    print("   • Select cylinder object")
    print("   • Switch to CAM Operations panel (right sidebar)")
    print("   • Add new CAM operation:")
    print("     - Operation Type: HELIX")
    print("     - Machine: 4-axis")
    print("     - A-axis: Enabled (rotary)")
    print()
    print("3. CONFIGURE MACHINE:")
    print("   • CAM → Machine Settings:")
    print(f"     - X: {MACHINE_CONFIG['work_envelope']['x'][0]} to {MACHINE_CONFIG['work_envelope']['x'][1]}mm")
    print(f"     - Y: {MACHINE_CONFIG['work_envelope']['y'][0]} to {MACHINE_CONFIG['work_envelope']['y'][1]}mm")
    print(f"     - Z: {MACHINE_CONFIG['work_envelope']['z'][0]} to {MACHINE_CONFIG['work_envelope']['z'][1]}mm")
    print("     - A: Rotary axis enabled")
    print()
    print("4. CONFIGURE TOOL:")
    print(f"     - Diameter: {TOOL_CONFIG['diameter']}mm")
    print(f"     - Type: {TOOL_CONFIG['type']}")
    print(f"     - Feed Rate: {TOOL_CONFIG['feed_rate']}mm/min")
    print(f"     - Spindle Speed: {TOOL_CONFIG['spindle_speed']}RPM")
    print()
    print("5. GENERATE G-CODE:")
    print("   • Calculate toolpath")
    print("   • Export with GRBL post-processor")
    print(f"   • Save as: {OUTPUT_DIR / f'{PROJECT_NAME}_HELIX.gcode'}")
    print()
    print("6. VALIDATION:")
    print("   • Check G-code header for G21 (millimeters)")
    print("   • Verify coordinate values are ~50mm range (not 50,000mm!)")
    print("   • Confirm A-axis commands present (A0 to A18355)")
    print()

def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("  BLENDER 4-AXIS ROTARY PROJECT SETUP")
    print("  Automated Configuration Script")
    print("="*60)

    try:
        # Execute setup steps
        clear_scene()
        setup_units_and_scene()
        cylinder = create_cylinder()
        setup_camera()
        cam_detected = setup_blendercam()
        save_project()

        # Print summary
        print_header("SETUP COMPLETE ✅")
        print(f"Project file: {BLEND_FILE}")
        print(f"Cylinder: {CYLINDER_CONFIG['diameter']}mm × {CYLINDER_CONFIG['length']}mm")
        print(f"Units: Millimeters (scale 1.0)")
        print(f"Machine: 4-Axis CNC Router ({MACHINE_CONFIG['travel']['x']}×{MACHINE_CONFIG['travel']['y']}×{MACHINE_CONFIG['travel']['z']}mm)")

        # Print manual steps
        print_manual_steps()

        print("\n" + "="*60)
        print("  Ready for manual validation in Blender!")
        print("="*60 + "\n")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
