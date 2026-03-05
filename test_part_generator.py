"""
BlenderCAM Test Part Generator
================================

Generates standardized test parts for validating 4-axis CNC/laser workflows.
Exports to multiple formats for cross-tool compatibility (FreeCAD, Adobe, etc.)

Test Part Library:
- Level 1: Simple Cylinder (geometry validation)
- Level 2: Tapered Cone (strategy testing)
- Level 3: 3D Relief (complex geometry)

Usage:
    blender --background --python test_part_generator.py -- --part cylinder --export-all
    blender --background --python test_part_generator.py -- --part all
"""

import sys
import os
import math
from pathlib import Path

try:
    import bpy
except ImportError:
    print("ERROR: This script must be run from within Blender")
    sys.exit(1)


def clear_scene():
    """Clear all objects from scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Set units to metric
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'


def create_test_cylinder(diameter=50, length=100, text="TEST-001"):
    """
    Level 1 Test Part: Simple Cylinder with Text
    Purpose: Verify A-axis rotation accuracy and basic HELIX strategy

    Args:
        diameter: Cylinder diameter in mm
        length: Cylinder length in mm
        text: Text to engrave (validates toolpath detail)

    Returns:
        Blender object
    """
    print(f"\n=== Creating Test Cylinder ===")
    print(f"Diameter: {diameter}mm, Length: {length}mm")

    clear_scene()

    # Create cylinder aligned to X-axis (rotary axis)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=diameter/2,
        depth=length,
        location=(0, 0, 0),
        rotation=(0, math.pi/2, 0)
    )

    cylinder = bpy.context.active_object
    cylinder.name = "TestCylinder_001"

    # Add text for engraving (optional - for visual reference)
    bpy.ops.object.text_add(location=(0, diameter/2 + 5, 0))
    text_obj = bpy.context.active_object
    text_obj.data.body = text
    text_obj.data.size = 10
    text_obj.name = f"Label_{text}"

    # Convert text to mesh for CAM
    bpy.ops.object.convert(target='MESH')

    print(f"✓ Created: {cylinder.name}")
    return cylinder


def create_test_cone(base_diameter=50, top_diameter=20, length=100):
    """
    Level 2 Test Part: Tapered Cone
    Purpose: Test continuous radius change and variable depth control

    Args:
        base_diameter: Base diameter in mm
        top_diameter: Top diameter in mm
        length: Cone length in mm

    Returns:
        Blender object
    """
    print(f"\n=== Creating Test Cone ===")
    print(f"Base: {base_diameter}mm → Top: {top_diameter}mm, Length: {length}mm")

    clear_scene()

    # Create cone aligned to X-axis
    bpy.ops.mesh.primitive_cone_add(
        radius1=base_diameter/2,
        radius2=top_diameter/2,
        depth=length,
        location=(0, 0, 0),
        rotation=(0, math.pi/2, 0)
    )

    cone = bpy.context.active_object
    cone.name = "TestCone_002"

    # Add spiral groove for visual validation
    bpy.ops.mesh.primitive_torus_add(
        major_radius=base_diameter/2 - 5,
        minor_radius=2,
        location=(0, 0, 0),
        rotation=(0, math.pi/2, 0)
    )

    spiral = bpy.context.active_object
    spiral.name = "SpiralGroove"

    print(f"✓ Created: {cone.name}")
    return cone


def create_test_3d_relief(diameter=50, length=80, relief_type="wave"):
    """
    Level 3 Test Part: 3D Relief on Cylinder
    Purpose: Test complex multi-pass depth control and fine detail

    Args:
        diameter: Base cylinder diameter in mm
        length: Cylinder length in mm
        relief_type: Pattern type - 'wave', 'logo', 'organic'

    Returns:
        Blender object
    """
    print(f"\n=== Creating Test 3D Relief ===")
    print(f"Diameter: {diameter}mm, Length: {length}mm, Pattern: {relief_type}")

    clear_scene()

    # Create base cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=diameter/2,
        depth=length,
        location=(0, 0, 0),
        rotation=(0, math.pi/2, 0),
        vertices=64  # Higher resolution for detail
    )

    cylinder = bpy.context.active_object
    cylinder.name = f"Test3DRelief_{relief_type}_003"

    # Apply subdivision for smooth surface
    bpy.ops.object.modifier_add(type='SUBSURF')
    cylinder.modifiers["Subdivision"].levels = 2

    # Add displacement modifier for relief pattern
    bpy.ops.object.modifier_add(type='DISPLACE')
    displace = cylinder.modifiers["Displace"]

    # Create texture for displacement
    texture = bpy.data.textures.new(name=f"Relief_{relief_type}", type='CLOUDS')
    texture.noise_scale = 0.5
    displace.texture = texture
    displace.strength = 5  # 5mm relief depth

    print(f"✓ Created: {cylinder.name}")
    return cylinder


def export_part(obj, export_dir, formats=['blend', 'stl', 'obj', 'fbx']):
    """
    Export part to multiple formats for cross-tool compatibility.

    Args:
        obj: Blender object to export
        export_dir: Output directory path
        formats: List of export formats

    Exports:
        - .blend: Native Blender (for BlenderCAM)
        - .stl: FreeCAD, CAM software
        - .obj: Adobe Substance, general 3D
        - .fbx: Adobe Mixamo, animation tools
        - .step: FreeCAD Path Workbench (if available)
    """
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    base_name = obj.name

    print(f"\n=== Exporting {base_name} ===")

    # Select only the target object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Blend (native)
    if 'blend' in formats:
        blend_path = export_dir / f"{base_name}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), copy=True)
        print(f"✓ Exported: {blend_path}")

    # STL (CAM standard)
    if 'stl' in formats:
        stl_path = export_dir / f"{base_name}.stl"
        bpy.ops.export_mesh.stl(
            filepath=str(stl_path),
            use_selection=True,
            global_scale=1.0,
            use_mesh_modifiers=True
        )
        print(f"✓ Exported: {stl_path}")

    # OBJ (universal)
    if 'obj' in formats:
        obj_path = export_dir / f"{base_name}.obj"
        bpy.ops.export_scene.obj(
            filepath=str(obj_path),
            use_selection=True,
            use_materials=True,
            use_mesh_modifiers=True,
            global_scale=1.0
        )
        print(f"✓ Exported: {obj_path}")

    # FBX (Adobe ecosystem)
    if 'fbx' in formats:
        fbx_path = export_dir / f"{base_name}.fbx"
        bpy.ops.export_scene.fbx(
            filepath=str(fbx_path),
            use_selection=True,
            global_scale=1.0,
            apply_scale_options='FBX_SCALE_ALL',
            bake_space_transform=True
        )
        print(f"✓ Exported: {fbx_path}")

    print(f"✓ Export complete: {len(formats)} formats")


def generate_metadata(obj, export_dir):
    """
    Generate JSON metadata for test part tracking.

    Includes:
    - Dimensions
    - Complexity level
    - Recommended strategies
    - Material suggestions
    """
    import json
    from datetime import datetime

    metadata = {
        "name": obj.name,
        "generated_date": datetime.now().isoformat(),
        "blender_version": bpy.app.version_string,
        "dimensions": {
            "x": obj.dimensions.x,
            "y": obj.dimensions.y,
            "z": obj.dimensions.z
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
        metadata["test_materials"] = ["Pine dowel", "Painted aluminum scrap", "Cardboard"]
        metadata["estimated_runtime"] = "5-10 minutes"
    elif "Cone" in obj.name:
        metadata["complexity_level"] = 2
        metadata["test_purpose"] = "Strategy testing - continuous radius change"
        metadata["recommended_strategies"] = ["HELIX", "PARALLELR"]
        metadata["test_materials"] = ["Pine", "Brass rod", "Plywood"]
        metadata["estimated_runtime"] = "10-20 minutes"
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
    """Generate test parts based on command-line arguments."""

    # Parse arguments
    part_type = "cylinder"  # Default
    export_all = False

    args = sys.argv
    if '--' in args:
        script_args = args[args.index('--') + 1:]
        for i, arg in enumerate(script_args):
            if arg == '--part' and i + 1 < len(script_args):
                part_type = script_args[i + 1].lower()
            elif arg == '--export-all':
                export_all = True

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
        if part == "cylinder":
            obj = create_test_cylinder(diameter=50, length=100, text="TEST-001")
        elif part == "cone":
            obj = create_test_cone(base_diameter=50, top_diameter=20, length=100)
        elif part == "relief":
            obj = create_test_3d_relief(diameter=50, length=80, relief_type="wave")
        else:
            print(f"ERROR: Unknown part type '{part}'")
            continue

        # Export formats
        formats = ['blend', 'stl', 'obj', 'fbx'] if export_all else ['blend', 'stl']
        export_part(obj, export_dir, formats)
        generate_metadata(obj, export_dir)

    print("\n" + "=" * 80)
    print("✓ Test part generation complete")
    print(f"Output directory: {export_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
