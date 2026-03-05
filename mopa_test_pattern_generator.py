"""
MOPA Laser Test Pattern Generator
Generates 5x5 power/speed matrix for metal marking/engraving parameter discovery
"""

import bpy
import sys
from pathlib import Path
from datetime import datetime


def clear_scene():
    """Remove all default objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def create_test_grid(
    power_range=(20, 80),      # Watts
    speed_range=(50, 200),      # mm/s
    square_size=10.0,           # mm
    serial_start=1
):
    """
    Create 5x5 grid of squares for power/speed testing

    Grid layout:
    - Columns: 5 power levels (20W, 35W, 50W, 65W, 80W)
    - Rows: 5 speed levels (50, 87.5, 125, 162.5, 200 mm/s)
    - Each square: 10mm × 10mm with engraved serial number
    - Total size: 60mm × 60mm (including 2mm spacing)
    """
    print("\n=== Creating MOPA Test Grid ===")
    print(f"Power range: {power_range[0]}-{power_range[1]}W")
    print(f"Speed range: {speed_range[0]}-{speed_range[1]} mm/s")
    print(f"Grid: 5×5 = 25 test squares")

    # Calculate power/speed steps
    power_min, power_max = power_range
    speed_min, speed_max = speed_range

    power_steps = [power_min + i * (power_max - power_min) / 4 for i in range(5)]
    speed_steps = [speed_min + i * (speed_max - speed_min) / 4 for i in range(5)]

    spacing = 2.0  # mm between squares
    serial = serial_start

    # Create collection for organization
    collection = bpy.data.collections.new("MOPA_Test_Grid")
    bpy.context.scene.collection.children.link(collection)

    metadata = {
        "test_type": "mopa_power_speed_matrix",
        "generated_date": datetime.now().isoformat(),
        "grid_size": "5x5",
        "square_size_mm": square_size,
        "power_range_w": power_range,
        "speed_range_mm_s": speed_range,
        "pulse_width_ns": 280,  # Standard for color marking on SS
        "frequency_khz": 30,
        "squares": []
    }

    for row in range(5):
        for col in range(5):
            power = power_steps[col]
            speed = speed_steps[row]

            # Calculate position (centered at origin)
            x = col * (square_size + spacing) - 2 * (square_size + spacing)
            y = -row * (square_size + spacing) + 2 * (square_size + spacing)

            # Create square
            bpy.ops.mesh.primitive_plane_add(
                size=square_size,
                location=(x, y, 0)
            )

            square = bpy.context.active_object
            square.name = f"Square_{serial:03d}_P{int(power)}W_S{int(speed)}mms"            # Add text annotation (serial number)
            bpy.ops.object.text_add(
                location=(x, y, 0),
                scale=(1, 1, 1)
            )
            text_obj = bpy.context.active_object
            text_obj.data.body = str(serial)
            text_obj.data.size = 3.0
            text_obj.data.align_x = 'CENTER'
            text_obj.data.align_y = 'CENTER'
            text_obj.name = f"Label_{serial:03d}"            # Record metadata
            metadata["squares"].append({
                "serial": serial,
                "power_w": round(power, 1),
                "speed_mm_s": round(speed, 1),
                "position_mm": {"x": round(x, 2), "y": round(y, 2)},
                "row": row,
                "col": col
            })

            serial += 1

    print(f"✓ Created 25 test squares (serials {serial_start} to {serial_start + 24})")

    return metadata


def export_test_grid(export_dir):
    """Export test grid to .blend and SVG formats"""
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    print("\n=== Exporting Test Grid ===")

    # Export .blend
    blend_path = export_dir / "MOPA_Test_Grid.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), copy=True)
    print(f"✓ Exported: {blend_path}")

    return str(blend_path)


def save_metadata(metadata, export_dir):
    """Save test grid metadata as JSON"""
    import json

    metadata_path = Path(export_dir) / "MOPA_Test_Grid_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Metadata saved: {metadata_path}")


def main():
    """Generate MOPA test grid"""

    # Parse arguments
    power_min = 20
    power_max = 80
    speed_min = 50
    speed_max = 200

    args = sys.argv
    if '--' in args:
        script_args = args[args.index('--') + 1:]
        for i, arg in enumerate(script_args):
            if arg == '--power-min' and i + 1 < len(script_args):
                power_min = int(script_args[i + 1])
            elif arg == '--power-max' and i + 1 < len(script_args):
                power_max = int(script_args[i + 1])
            elif arg == '--speed-min' and i + 1 < len(script_args):
                speed_min = int(script_args[i + 1])
            elif arg == '--speed-max' and i + 1 < len(script_args):
                speed_max = int(script_args[i + 1])

    export_dir = Path(__file__).parent / "laser_test_patterns"

    print("=" * 80)
    print("MOPA Laser Test Pattern Generator")
    print("=" * 80)

    clear_scene()
    metadata = create_test_grid(
        power_range=(power_min, power_max),
        speed_range=(speed_min, speed_max)
    )

    export_test_grid(export_dir)
    save_metadata(metadata, export_dir)

    print("\n" + "=" * 80)
    print("✓ MOPA test grid generation complete")
    print(f"Output directory: {export_dir}")
    print("\nNext steps:")
    print("1. Open MOPA_Test_Grid.blend in Blender")
    print("2. Use BlenderCAM to generate G-code")
    print("3. Run on MOPA laser with stainless steel sample")
    print("4. Record results in material_tests_mopa_laser.csv")
    print("=" * 80)


if __name__ == "__main__":
    main()
