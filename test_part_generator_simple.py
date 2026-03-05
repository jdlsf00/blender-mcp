"""
BlenderCAM Test Part Generator - Simplified Version
Generates test parts for 4-axis CNC validation (Blender .blend format only)
"""

import bpy
import sys
from pathlib import Path
from datetime import datetime
import json


def clear_scene():
    """Remove all default objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def create_test_cylinder(diameter=50, length=100, text="TEST-001"):
    """
    Create Level 1 test part - simple cylinder for geometry validation

    Tests:
    - A-axis rotation accuracy
    - Surface finish consistency
    - Dimensional accuracy
    """
    print("\n=== Creating Test Cylinder ===")
    print(f"Diameter: {diameter}mm, Length: {length}mm")

    # Create cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=diameter/2,
        depth=length,
        location=(0, 0, 0)
    )

    obj = bpy.context.active_object
    obj.name = "TestCylinder_001"
    obj.rotation_euler = (0, 1.5708, 0)  # Rotate for 4-axis

    # Apply modifier for smoothing
    modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    modifier.levels = 2

    print(f"✓ Created: {obj.name}")
    return obj


def create_test_cone(base_diameter=50, top_diameter=20, length=100):
    """
    Create Level 2 test part - tapered cone for strategy testing

    Tests:
    - Variable diameter handling
    - HELIX vs PARALLELR strategies
    - Stepover accuracy on slopes
    """
    print("\n=== Creating Test Cone ===")
    print(f"Base: {base_diameter}mm, Top: {top_diameter}mm, Length: {length}mm")

    # Create cone
    bpy.ops.mesh.primitive_cone_add(
        radius1=base_diameter/2,
        radius2=top_diameter/2,
        depth=length,
        location=(0, 0, 0)
    )

    obj = bpy.context.active_object
    obj.name = "TestCone_001"
    obj.rotation_euler = (0, 1.5708, 0)

    print(f"✓ Created: {obj.name}")
    return obj


def create_test_3d_relief(diameter=50, length=80, relief_type="wave"):
    """
    Create Level 3 test part - 3D relief for complex geometry testing

    Tests:
    - Multi-pass depth control
    - 3D toolpath accuracy
    - Complex strategy behavior
    """
    print("\n=== Creating Test 3D Relief ===")
    print(f"Diameter: {diameter}mm, Length: {length}mm, Pattern: {relief_type}")

    # Create base cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=diameter/2,
        depth=length,
        vertices=128,
        location=(0, 0, 0)
    )

    obj = bpy.context.active_object
    obj.name = "Test3DRelief_001"
    obj.rotation_euler = (0, 1.5708, 0)

    # Add displacement modifier for 3D relief
    modifier = obj.modifiers.new(name="Displace", type='DISPLACE')
    modifier.strength = 2.0  # 2mm depth

    # Create texture for displacement
    texture = bpy.data.textures.new(name="ReliefTexture", type='CLOUDS')
    texture.noise_scale = 0.5
    modifier.texture = texture

    print(f"✓ Created: {obj.name}")
    return obj


def export_part(obj, export_dir):
    """Export test part to Blender .blend format"""
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Exporting {obj.name} ===")

    # Save as .blend file
    export_path = export_dir / f"{obj.name}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(export_path), copy=True)
    print(f"✓ Exported: {export_path}")

    return str(export_path)


def generate_metadata(obj, export_dir):
    """Generate JSON metadata for test part tracking"""

    metadata = {
        "name": obj.name,
        "generated_date": datetime.now().isoformat(),
        "blender_version": bpy.app.version_string,
        "dimensions": {
            "x": round(obj.dimensions.x, 2),
            "y": round(obj.dimensions.y, 2),
            "z": round(obj.dimensions.z, 2)
        },
        "vertices": len(obj.data.vertices) if hasattr(obj.data, 'vertices') else 0,
        "recommended_strategies": [],
        "test_materials": [],
        "notes": ""
    }

    # Auto-classify based on name
    if "Cylinder" in obj.name:
        metadata["complexity_level"] = 1
        metadata["test_purpose"] = "Geometry validation - verify A-axis rotation accuracy"
        metadata["recommended_strategies"] = ["HELIX"]
        metadata["test_materials"] = ["Scrap wood", "Aluminum", "Acrylic"]
        metadata["estimated_runtime"] = "5-10 minutes"

    elif "Cone" in obj.name:
        metadata["complexity_level"] = 2
        metadata["test_purpose"] = "Strategy testing - compare HELIX vs PARALLELR on variable diameter"
        metadata["recommended_strategies"] = ["HELIX", "PARALLELR"]
        metadata["test_materials"] = ["Softwood", "Brass", "HDPE"]
        metadata["estimated_runtime"] = "8-15 minutes"

    elif "Relief" in obj.name:
        metadata["complexity_level"] = 3
        metadata["test_purpose"] = "Complex geometry - multi-pass depth control"
        metadata["recommended_strategies"] = ["HELIX"]
        metadata["test_materials"] = ["Hardwood", "Stainless steel", "Leather"]
        metadata["estimated_runtime"] = "20-45 minutes"

    metadata_path = Path(export_dir) / f"{obj.name}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Metadata saved: {metadata_path}")


def main():
    """Generate test parts based on command-line arguments"""

    # Parse arguments
    part_type = "all"  # Default

    args = sys.argv
    if '--' in args:
        script_args = args[args.index('--') + 1:]
        for i, arg in enumerate(script_args):
            if arg == '--part' and i + 1 < len(script_args):
                part_type = script_args[i + 1].lower()

    # Set export directory
    export_dir = Path(__file__).parent / "test_parts"

    print("=" * 80)
    print("BlenderCAM Test Part Generator")
    print("=" * 80)

    # Generate requested parts
    if part_type == "all":
        parts = ["cylinder", "cone", "relief"]
    else:
        parts = [part_type]

    for part in parts:
        clear_scene()

        if part == "cylinder":
            obj = create_test_cylinder(diameter=50, length=100, text="TEST-001")
        elif part == "cone":
            obj = create_test_cone(base_diameter=50, top_diameter=20, length=100)
        elif part == "relief":
            obj = create_test_3d_relief(diameter=50, length=80, relief_type="wave")
        else:
            print(f"ERROR: Unknown part type '{part}'")
            continue

        export_part(obj, export_dir)
        generate_metadata(obj, export_dir)

    print("\n" + "=" * 80)
    print("✓ Test part generation complete")
    print(f"Output directory: {export_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
