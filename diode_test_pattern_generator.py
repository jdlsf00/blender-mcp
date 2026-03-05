"""
Diode Laser Test Pattern Generator
Generates power gradation tests (10%, 30%, 50%, 70%, 90%) for organic material parameter discovery
"""

import bpy
import sys
from pathlib import Path
from datetime import datetime


def clear_scene():
    """Remove all default objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def create_gradation_test(
    design_type="star",
    power_levels=[10, 30, 50, 70, 90],  # Percent
    spacing=20.0  # mm between copies
):
    """
    Create power gradation test pattern

    Single design repeated 5 times at different power levels:
    - 10% (very light)
    - 30% (light)
    - 50% (medium)
    - 70% (dark)
    - 90% (very dark)

    Design options: star, text, circle, decorative
    """
    print("\n=== Creating Diode Laser Gradation Test ===")
    print(f"Design: {design_type}")
    print(f"Power levels: {power_levels}%")

    collection = bpy.data.collections.new("Diode_Gradation_Test")
    bpy.context.scene.collection.children.link(collection)

    metadata = {
        "test_type": "diode_power_gradation",
        "generated_date": datetime.now().isoformat(),
        "design_type": design_type,
        "power_levels_percent": power_levels,
        "speed_mm_s": 120,  # Standard for wood
        "focus_offset_mm": -1.0,
        "designs": []
    }

    for i, power in enumerate(power_levels):
        x = i * spacing - (len(power_levels) - 1) * spacing / 2

        if design_type == "star":
            # Create 5-pointed star
            bpy.ops.curve.primitive_bezier_circle_add(location=(x, 0, 0))
            obj = bpy.context.active_object
            obj.name = f"Star_P{power}pct"
            obj.data.resolution_u = 5  # 5 points = star

        elif design_type == "text":
            # Create text "TEST"
            bpy.ops.object.text_add(location=(x, 0, 0))
            obj = bpy.context.active_object
            obj.data.body = "TEST"
            obj.data.size = 10.0
            obj.data.align_x = 'CENTER'
            obj.name = f"Text_P{power}pct"

        elif design_type == "circle":
            # Create circle
            bpy.ops.curve.primitive_bezier_circle_add(location=(x, 0, 0))
            obj = bpy.context.active_object
            obj.name = f"Circle_P{power}pct"
            obj.scale = (5, 5, 5)

        else:  # decorative
            # Create decorative pattern (mandala-style)
            bpy.ops.mesh.primitive_uv_sphere_add(location=(x, 0, 0), segments=8, ring_count=4)
            obj = bpy.context.active_object
            obj.name = f"Decorative_P{power}pct"
            obj.scale = (5, 5, 1)        # Add power label below
        bpy.ops.object.text_add(location=(x, -15, 0))
        label = bpy.context.active_object
        label.data.body = f"{power}%"
        label.data.size = 3.0
        label.data.align_x = 'CENTER'
        label.name = f"Label_{power}pct"

        metadata["designs"].append({
            "power_percent": power,
            "position_mm": {"x": round(x, 2), "y": 0},
            "design_name": obj.name
        })

    print(f"✓ Created {len(power_levels)} gradation test designs")

    return metadata


def export_test_pattern(export_dir):
    """Export test pattern to .blend format"""
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    print("\n=== Exporting Test Pattern ===")

    blend_path = export_dir / "Diode_Gradation_Test.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), copy=True)
    print(f"✓ Exported: {blend_path}")

    return str(blend_path)


def save_metadata(metadata, export_dir):
    """Save test pattern metadata as JSON"""
    import json

    metadata_path = Path(export_dir) / "Diode_Gradation_Test_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Metadata saved: {metadata_path}")


def main():
    """Generate diode laser gradation test"""

    # Parse arguments
    design_type = "star"

    args = sys.argv
    if '--' in args:
        script_args = args[args.index('--') + 1:]
        for i, arg in enumerate(script_args):
            if arg == '--design' and i + 1 < len(script_args):
                design_type = script_args[i + 1].lower()

    export_dir = Path(__file__).parent / "laser_test_patterns"

    print("=" * 80)
    print("Diode Laser Test Pattern Generator")
    print("=" * 80)

    clear_scene()
    metadata = create_gradation_test(design_type=design_type)

    export_test_pattern(export_dir)
    save_metadata(metadata, export_dir)

    print("\n" + "=" * 80)
    print("✓ Diode gradation test generation complete")
    print(f"Output directory: {export_dir}")
    print("\nNext steps:")
    print("1. Open Diode_Gradation_Test.blend in Blender")
    print("2. Export to SVG or use BlenderCAM for G-code")
    print("3. Run on diode laser with wood/leather sample")
    print("4. Record results in material_tests_diode_laser.csv")
    print("=" * 80)


if __name__ == "__main__":
    main()
