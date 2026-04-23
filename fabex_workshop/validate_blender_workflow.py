#!/usr/bin/env python3
"""Background Blender validation for the Fabex workshop toolkit."""

from __future__ import annotations

import addon_utils
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
PRESETS = OUTPUT / "presets"
TEMPLATES = OUTPUT / "templates"


def enable_fabex() -> None:
    module_name = "bl_ext.user_default.fabex"
    if not addon_utils.check(module_name)[1]:
        addon_utils.enable(module_name, default_set=True)
    if not addon_utils.check(module_name)[1]:
        raise RuntimeError("Fabex extension did not enable in Blender 4.5")


def execute_script(path: Path) -> None:
    namespace = {"__file__": str(path), "__name__": "__main__"}
    code = compile(path.read_text(encoding="utf-8"), str(path), "exec")
    exec(code, namespace, namespace)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def validate_presets() -> None:
    scene = bpy.context.scene
    execute_script(PRESETS / "cam_machines" / "Genmitsu_4040_PRO_GRBL.py")

    bpy.ops.mesh.primitive_cube_add(size=0.03)
    cube = bpy.context.active_object
    cube.name = "PresetValidationCube"

    bpy.ops.scene.cam_operation_add()
    scene.cam_active_operation = len(scene.cam_operations) - 1
    operation = scene.cam_operations[scene.cam_active_operation]
    operation.name = "PresetValidationOperation"
    operation.object_name = cube.name
    operation.geometry_source = "OBJECT"

    execute_script(PRESETS / "cam_cutters" / "flat_3.00mm_2F.py")
    execute_script(PRESETS / "cam_operations" / "Pocket_Roughing_4040_PRO.py")

    if not scene.cam_operations:
        raise RuntimeError("No CAM operations were present after preset execution")

    print("Preset validation passed")
    print(f"Machine post processor: {scene.cam_machine.post_processor}")
    print(f"Operation count: {len(scene.cam_operations)}")


def import_svg(path: Path) -> None:
    if hasattr(bpy.ops.import_curve, "svg"):
        bpy.ops.import_curve.svg(filepath=str(path))
    elif hasattr(bpy.ops.wm, "svg_import"):
        bpy.ops.wm.svg_import(filepath=str(path))
    else:
        raise RuntimeError("No SVG import operator is available in Blender")


def validate_templates() -> None:
    clear_scene()
    execute_script(TEMPLATES / "ring_band_blank.py")
    if "RingBandOuter" not in bpy.data.objects:
        raise RuntimeError("Ring band template did not create the expected object")

    before_names = set(bpy.data.objects.keys())
    import_svg(TEMPLATES / "pendant_blank.svg")
    after_names = set(bpy.data.objects.keys())
    if before_names == after_names:
        raise RuntimeError("SVG import did not create any new objects")

    print("Template validation passed")
    print(f"Object count after template checks: {len(bpy.data.objects)}")


def validate_gcode() -> None:
    required = [
        OUTPUT / "gcode" / "rectangular_pocket.nc",
        OUTPUT / "gcode" / "circular_pocket.nc",
        OUTPUT / "gcode" / "ring_band_profile.nc",
    ]
    for path in required:
        text = path.read_text(encoding="utf-8")
        if "M30" not in text or "M3 S" not in text:
            raise RuntimeError(f"G-code file failed sanity check: {path.name}")
    print("G-code validation passed")


def main() -> None:
    enable_fabex()
    validate_presets()
    validate_templates()
    validate_gcode()
    print("Fabex workshop Blender validation completed successfully")


if __name__ == "__main__":
    main()