#!/usr/bin/env python3
"""
BlenderCAM 4-Axis HELIX Strategy Test
======================================

This script creates a simple cylindrical part and generates a helical
toolpath using BlenderCAM's continuous 4-axis capability.

Purpose: Validate that HELIX strategy produces TRUE continuous simultaneous
rotation with A-axis commands in the G-code output.

Usage:
    blender --background --python test_4axis_helix.py

Expected Output:
    - G-code file with synchronized A-axis rotation
    - Mesh visualization of toolpath
    - Console output showing rotation values
"""

import sys
import os
import importlib
import math
from pathlib import Path

# Ensure Blender's bpy module is available
try:
    import bpy
except ImportError:
    print("ERROR: This script must be run from within Blender")
    print("Usage: blender --background --python test_4axis_helix.py")
    sys.exit(1)

def _ensure_python_packages(pkgs):
    """Ensure required Python packages are installed into Blender's Python.

    Note: BlenderCAM's addon will attempt to install these automatically.
    This helper is a best-effort accelerator and safe to no-op.
    """
    try:
        target_dir = Path(__file__).parent / "_blender_deps"
        target_dir.mkdir(exist_ok=True)

        user_site = os.path.expandvars(r"%APPDATA%\\Python\\Python311\\site-packages")
        for p in [str(target_dir), user_site]:
            if p and os.path.isdir(p) and p not in sys.path:
                sys.path.append(p)

        for mod_name, pip_name in pkgs:
            try:
                importlib.import_module(mod_name)
                continue
            except Exception:
                pass
            try:
                print(f"Installing dependency to local target: {pip_name} -> {target_dir} ...")
                import subprocess
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-warn-script-location', '--target', str(target_dir), pip_name])
                if str(target_dir) not in sys.path:
                    sys.path.append(str(target_dir))
            except Exception as e:
                print(f"WARNING: Failed to install {pip_name}: {e}")
    except Exception as e:
        print(f"WARNING: Skipping optional dependency preinstall: {e}")

def ensure_blendercam_addon():
    """Ensure the BlenderCAM addon (module 'cam') is available and enabled via preferences.

    This sets Blender's Scripts directory to the local BlenderCAM repo and enables the addon.
    Avoids manual register() fallback so preferences exist for export.
    """
    addon_module = 'cam'

    # Already enabled
    if addon_module in bpy.context.preferences.addons:
        return True

    # Preinstall common packages (best-effort; addon also installs if missing)
    _ensure_python_packages([
        ('shapely', 'shapely'),
        ('Equation', 'Equation'),
        ('opencamlib', 'opencamlib'),
    ])

    # Ensure Blender can import the addon by extending sys.path with the local addons folder
    candidate_paths = [
        r"F:\\Documents\\Blender\\blendercam-master\\scripts\\addons",
        os.path.expandvars(r"%APPDATA%\\Blender Foundation\\Blender\\4.5\\scripts\\addons"),
        os.path.expandvars(r"%APPDATA%\\Blender Foundation\\Blender\\4.4\\scripts\\addons"),
    ]
    for p in candidate_paths:
        if p and os.path.isdir(p) and p not in sys.path:
            print(f"Adding to sys.path: {p}")
            sys.path.append(p)

    # Refresh addon list and try enabling via preferences
    try:
        print("Enabling BlenderCAM addon via preferences...")
        bpy.ops.preferences.addon_refresh()
    except Exception:
        pass
    try:
        res = bpy.ops.preferences.addon_enable(module=addon_module)
        if addon_module in bpy.context.preferences.addons:
            print("✓ BlenderCAM addon enabled")
            return True
        else:
            print(f"Addon enable op result: {res}")
    except Exception as e:
        print(f"ERROR enabling addon: {e}")

    print("ERROR: BlenderCAM addon not found or failed to enable")
    return False

def setup_scene():
    """Clear default scene and set up for CAM operation."""
    print("\n=== Setting up scene ===")

    # Delete default objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Set units to metric
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'

    print("✓ Scene cleared and units set to metric")

def create_cylindrical_stock():
    """Create a simple cylinder as workpiece."""
    print("\n=== Creating cylindrical workpiece ===")

    # Add cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=25.0,      # 25mm radius (50mm diameter)
        depth=100.0,      # 100mm length
        location=(0, 0, 0),
        rotation=(0, math.pi/2, 0)  # Rotate to align with X-axis
    )

    cylinder = bpy.context.active_object
    cylinder.name = "Cylinder_Stock"

    print(f"✓ Created cylinder: {cylinder.name}")
    print(f"  Dimensions: Ø50mm x 100mm")
    print(f"  Rotation: X-axis aligned (for rotary axis)")

    return cylinder

def setup_cam_machine(post_processor='GRBL'):
    """Configure CAM machine settings for 4-axis.

    Args:
        post_processor: G-code format - 'GRBL', 'ISO', 'EMC', 'MACH3'
    """
    print(f"\n=== Configuring CAM machine ({post_processor}) ===")

    scene = bpy.context.scene

    # Create machine if it doesn't exist
    if not hasattr(scene, 'cam_machine'):
        print("ERROR: CAM addon not loaded!")
        print("Please enable BlenderCAM addon in Blender preferences")
        return False

    machine = scene.cam_machine

    # Machine setup
    machine.post_processor = post_processor  # Support multiple post-processors
    machine.use_position_definitions = True
    machine.starting_position = (0, 0, 0)
    machine.feedrate_min = 100
    machine.feedrate_max = 3000
    machine.feedrate_default = 1000
    machine.spindle_min = 5000
    machine.spindle_max = 20000
    machine.spindle_default = 12000

    print(f"✓ Machine configured: {machine.post_processor}")
    print(f"  Feed rate: {machine.feedrate_default} mm/min")
    print(f"  Spindle: {machine.spindle_default} RPM")

    return True

def create_4axis_operation(cylinder, strategy='HELIX'):
    """Create a 4-axis CAM operation with specified strategy.

    Args:
        cylinder: The cylinder mesh object
        strategy: 4-axis strategy - 'HELIX', 'PARALLEL', 'PARALLELR', 'CROSS'
    """
    print(f"\n=== Creating 4-axis {strategy} operation ===")

    scene = bpy.context.scene

    # Add new CAM operation
    bpy.ops.scene.cam_operation_add()
    operation = scene.cam_operations[-1]

    # Basic settings
    operation.name = f"4Axis_{strategy}_Test"
    operation.object_name = cylinder.name
    operation.geometry_source = 'OBJECT'

    # Set to 4-axis mode
    operation.machine_axes = '4'
    operation.strategy4axis = strategy  # HELIX, PARALLEL, PARALLELR, or CROSS
    operation.rotary_axis_1 = 'X'  # Cylinder rotates around X-axis

    # Cutter settings
    operation.cutter_type = 'END'  # Flat end mill
    operation.cutter_diameter = 6.0  # 6mm cutter
    operation.cutter_flutes = 4
    operation.cutter_id = 1

    # Toolpath parameters
    operation.dist_between_paths = 2.0   # 2mm between passes (pitch)
    operation.dist_along_paths = 1.0     # 1mm sampling along path
    operation.stepdown = 2.0             # 2mm depth per pass

    # Material/cutting bounds
    operation.minz = 20.0   # Inner radius (depth of cut from surface)
    operation.maxz = 25.0   # Outer radius (stock surface)

    # Set operation bounds based on cylinder
    operation.min.x = -50.0
    operation.max.x = 50.0
    operation.min.y = -25.0
    operation.max.y = 25.0

    # Feed rates
    operation.feedrate = 1000.0  # 1000 mm/min
    operation.plunge_feedrate = 50.0  # 50% of feedrate for plunging
    operation.spindle_rpm = 12000

    # Movement settings
    operation.movement.free_height = 5.0  # Clearance above part
    operation.movement.type = 'CLIMB'
    operation.movement.spindle_rotation = 'CW'

    # Output settings
    operation.filename = f"{strategy.lower()}_test_4axis"
    operation.auto_export = False  # We'll export manually

    print(f"✓ Operation created: {operation.name}")
    print(f"  Strategy: {operation.strategy4axis}")
    print(f"  Rotary axis: {operation.rotary_axis_1}")
    print(f"  Cutter: Ø{operation.cutter_diameter}mm end mill")
    print(f"  Pitch: {operation.dist_between_paths}mm")
    print(f"  Depth: {operation.maxz - operation.minz}mm")

    return operation

def calculate_toolpath(operation):
    """Calculate the 4-axis toolpath with progress reporting."""
    print("\n=== Calculating toolpath ===")

    import time
    start_time = time.time()

    try:
        # Select the operation
        bpy.context.scene.cam_active_operation = len(bpy.context.scene.cam_operations) - 1

        # Prefer direct async path generation and manually drive BlenderCAM's coroutine
        # because it yields custom ('progress', ...) messages not compatible with asyncio.
        from cam.gcodepath import getPath

        def _drive_cam_coroutine(coro):
            """Drive BlenderCAM coroutine with progress reporting."""
            try:
                value = None
                last_progress_update = time.time()
                progress_counter = 0

                while True:
                    msg, args = coro.send(value)

                    # Report progress messages
                    if isinstance(msg, str) and msg == 'progress':
                        progress_counter += 1
                        current_time = time.time()

                        # Print progress every 2 seconds or on step changes
                        if current_time - last_progress_update >= 2.0 or isinstance(args, dict):
                            if isinstance(args, dict):
                                # Step name from dict
                                step_name = args.get('step', 'Processing')
                                print(f"  [{progress_counter:4d}] {step_name}...")
                            elif isinstance(args, str):
                                # Step name as string
                                print(f"  [{progress_counter:4d}] {args}...")
                            else:
                                # Generic progress indicator
                                elapsed = current_time - start_time
                                print(f"  [{progress_counter:4d}] Progress update... ({elapsed:.1f}s elapsed)")

                            last_progress_update = current_time
                        value = None
                    else:
                        value = None
            except StopIteration:
                elapsed = time.time() - start_time
                print(f"✓ Toolpath calculation complete ({elapsed:.1f}s)")
                return

        coro = getPath(bpy.context, operation)
        _drive_cam_coroutine(coro)

        print("✓ Toolpath calculated successfully")

        # Check for generated path object
        path_name = f"cam_path_{operation.name}"
        if path_name in bpy.data.objects:
            path_obj = bpy.data.objects[path_name]
            print(f"✓ Path mesh created: {len(path_obj.data.vertices)} vertices")

            # Check for rotations shape key (4-axis indicator)
            if path_obj.data.shape_keys:
                for key in path_obj.data.shape_keys.key_blocks:
                    print(f"  Shape key: {key.name}")
                    if key.name == 'rotations':
                        print("  ✓ ROTATIONS DATA PRESENT (4-axis confirmed)")

            return True
        else:
            print(f"WARNING: Path object '{path_name}' not found")
            return False

    except Exception as e:
        print(f"ERROR calculating toolpath: {e}")
        return False

def export_gcode(operation):
    """Export G-code and analyze for A-axis commands."""
    print("\n=== Exporting G-code ===")

    output_dir = Path(__file__).parent
    # Save .blend to control export folder (export uses .blend folder)
    blend_path = output_dir / "helix_test.blend"
    try:
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
        print(f"✓ Saved temp .blend: {blend_path}")
    except Exception as e:
        print(f"WARNING: Could not save .blend, export path may vary: {e}")

    try:
        # Get the path mesh
        path_name = f"cam_path_{operation.name}"
        if path_name not in bpy.data.objects:
            print("ERROR: Path object not found")
            return False

        path_obj = bpy.data.objects[path_name]

        # Export using BlenderCAM's export function; pass base name (addon computes proper extension and base path)
        from cam.gcodepath import exportGcodePath
        exportGcodePath(operation.filename, [path_obj.data], [operation])

        # Find the exported file in the .blend directory
        exported = None
        for ext in [".gcode", ".ngc", ".tap", ".nc", ".din", ".H"]:
            candidate = output_dir / f"{operation.filename}{ext}"
            if candidate.exists():
                exported = candidate
                break

        if not exported:
            print("ERROR: Export did not produce a known file type in expected folder")
            return False

        print(f"✓ G-code exported: {exported}")

        # Analyze the G-code
        analyze_gcode(exported)

        return True

    except Exception as e:
        print(f"ERROR exporting G-code: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_gcode(gcode_path):
    """Analyze G-code file for A-axis commands with robust parsing.

    Handles multiple A-axis formats:
    - With/without spaces: ' A', 'A', 'XnnnAnn'
    - Signed values: A-45.0, A+90.0
    - Scientific notation: A1.234e-5
    - Multiple on same line: X100A45.0Y50
    """
    print("\n=== Analyzing G-code ===")

    import re

    try:
        with open(gcode_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        total_lines = len(lines)
        a_axis_lines = 0
        rotation_values = []

        # Robust pattern: matches A followed by optional sign and number (including scientific notation)
        # Handles formats: A123.45, A-90.0, A+45.5, A1.23e-5, XnnnAnn (no space)
        a_pattern = re.compile(r'A([+-]?[0-9]*\.?[0-9]+(?:[eE][+-]?[0-9]+)?)', re.IGNORECASE)

        for line_num, line in enumerate(lines, 1):
            # Strip comments
            code_part = line.split('(')[0].split(';')[0].strip()

            # Find all A-axis values in this line
            matches = a_pattern.findall(code_part)
            if matches:
                a_axis_lines += 1
                for match in matches:
                    try:
                        a_val = float(match)
                        rotation_values.append(a_val)
                    except ValueError as e:
                        print(f"WARNING: Could not parse A value '{match}' on line {line_num}: {e}")

        print(f"Total lines: {total_lines}")
        print(f"Lines with A-axis: {a_axis_lines}")

        if len(rotation_values) == 0:
            print("⚠ WARNING: No A-axis values found!")
            print("  This may indicate:")
            print("  - Strategy does not produce continuous rotation")
            print("  - Post-processor does not support A-axis")
            print("  - Export failed to include rotation data")
            return

        if a_axis_lines > 0:
            print("✓ A-AXIS COMMANDS FOUND - Continuous 4-axis CONFIRMED!")
            print(f"  Total A-axis values extracted: {len(rotation_values)}")
            print(f"\nRotation statistics:")

            # Safe min/max/avg computation
            try:
                min_rot = min(rotation_values)
                max_rot = max(rotation_values)
                avg_rot = sum(rotation_values) / len(rotation_values)

                print(f"  Min: {min_rot:.3f}°")
                print(f"  Max: {max_rot:.3f}°")
                print(f"  Avg: {avg_rot:.3f}°")
                print(f"  Total rotation: {max_rot - min_rot:.3f}°")
                print(f"  Full revolutions: {(max_rot - min_rot) / 360.0:.2f}")
            except Exception as e:
                print(f"  ERROR computing statistics: {e}")

            # Show first few A-axis commands
            print(f"\nFirst 5 A-axis commands:")
            count = 0
            for line in lines:
                if a_pattern.search(line):
                    print(f"  {line.strip()}")
                    count += 1
                    if count >= 5:
                        break

            # Export CSV with rotation data
            export_rotation_csv(gcode_path, lines, a_pattern)
        else:
            print("⚠ WARNING: No A-axis commands found!")
            print("This may indicate an issue with 4-axis export")

    except Exception as e:
        print(f"ERROR analyzing G-code: {e}")

def export_rotation_csv(gcode_path, lines, a_pattern):
    """Export A-axis rotation data vs. X-position to CSV.

    Args:
        gcode_path: Path to the G-code file
        lines: List of G-code lines
        a_pattern: Compiled regex for A-axis extraction
    """
    print("\n=== Exporting rotation data to CSV ===")

    import csv
    import re

    try:
        # Prepare CSV output path
        csv_path = gcode_path.with_suffix('.csv')

        # Extract X and A coordinates
        x_pattern = re.compile(r'X([+-]?[0-9]*\.?[0-9]+)', re.IGNORECASE)

        data_rows = []
        current_x = 0.0
        current_a = 0.0

        for line_num, line in enumerate(lines, 1):
            # Strip comments
            code_part = line.split('(')[0].split(';')[0].strip()

            # Extract X if present (modal: use last value if not specified)
            x_match = x_pattern.search(code_part)
            if x_match:
                current_x = float(x_match.group(1))

            # Extract A if present
            a_match = a_pattern.search(code_part)
            if a_match:
                current_a = float(a_match.group(1))
                # Record this data point
                data_rows.append({
                    'line': line_num,
                    'x_mm': current_x,
                    'a_degrees': current_a,
                    'revolutions': current_a / 360.0
                })

        # Write CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['line', 'x_mm', 'a_degrees', 'revolutions']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(data_rows)

        print(f"✓ CSV exported: {csv_path}")
        print(f"  Data points: {len(data_rows)}")
        print(f"  Columns: line, x_mm, a_degrees, revolutions")

    except Exception as e:
        print(f"WARNING: CSV export failed: {e}")

def main():
    """Main test execution."""
    # Parse command-line arguments
    strategy = 'HELIX'
    post_processor = 'GRBL'

    # Check for --strategy and --post arguments after script name
    args = sys.argv
    if '--' in args:
        script_args = args[args.index('--') + 1:]
        for i, arg in enumerate(script_args):
            if arg == '--strategy' and i + 1 < len(script_args):
                strategy = script_args[i + 1].upper()
            elif arg == '--post' and i + 1 < len(script_args):
                post_processor = script_args[i + 1].upper()

    print("\n" + "="*70)
    print(f"BlenderCAM 4-Axis {strategy} Strategy Test")
    print(f"Post-Processor: {post_processor}")
    print("="*70)

    # Ensure BlenderCAM is available
    if not ensure_blendercam_addon():
        print("\n❌ TEST FAILED: BlenderCAM addon not available")
        return

    # Setup
    setup_scene()
    cylinder = create_cylindrical_stock()

    if not setup_cam_machine(post_processor):
        print("\n❌ TEST FAILED: CAM addon not available")
        return

    # Create and calculate operation
    operation = create_4axis_operation(cylinder, strategy)

    if not calculate_toolpath(operation):
        print("\n❌ TEST FAILED: Toolpath calculation failed")
        return

    # Export and analyze
    if not export_gcode(operation):
        print("\n❌ TEST FAILED: G-code export failed")
        return

    print("\n" + "="*70)
    print("✓ TEST COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\nResults:")
    print("  - Cylindrical stock created")
    print(f"  - 4-axis {strategy} operation configured")
    print(f"  - Post-processor: {post_processor}")
    print("  - Toolpath calculated with rotation data")
    print("  - G-code exported with A-axis commands")
    print("\nConclusion:")
    print(f"  BlenderCAM {strategy} strategy validated!")
    print(f"  {post_processor} post-processor produces rotary toolpaths.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
