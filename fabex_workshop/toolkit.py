#!/usr/bin/env python3
"""Fabex workshop toolkit.

Creates three reusable layers for CNC workflows:
1. Fabex-compatible preset files for machines, tools, and operations.
2. Parametric SVG and Blender script templates for common jobs.
3. Direct G-code for simple pockets and ring/band profiles.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


MM_TO_M = 0.001


@dataclass
class MachineProfile:
    name: str
    post_processor: str
    work_area_x_mm: float
    work_area_y_mm: float
    work_area_z_mm: float
    home_x_mm: float
    home_y_mm: float
    home_z_mm: float
    spindle_rpm: int
    feed_rate_mm_min: float
    plunge_rate_mm_min: float
    rotary_axis: str = "X"
    axis_4: bool = False
    spindle_min_rpm: int = 5000
    spindle_max_rpm: int = 24000
    controller: str = "GRBL"
    spindle_model: str = "Spindle"


@dataclass
class ToolProfile:
    name: str
    cutter_type: str
    diameter_mm: float
    flutes: int
    spindle_rpm: int
    feed_rate_mm_min: float
    plunge_rate_mm_min: float
    stepover_percent: float
    stepdown_mm: float
    cutter_length_mm: float = 25.0
    cutter_tip_angle: float = 60.0


@dataclass
class OperationProfile:
    name: str
    strategy: str
    cutter_type: str
    spindle_rpm: int
    feed_rate_mm_min: float
    plunge_rate_mm_min: float
    stepover_percent: float
    stepdown_mm: float
    skin_mm: float = 0.0
    movement_type: str = "MEANDER"
    ambient_behaviour: str = "ALL"


@dataclass
class MaterialPreset:
    name: str
    spindle_rpm: int
    feed_rate_mm_min: float
    plunge_rate_mm_min: float
    finish_feed_mm_min: float
    stepover_percent: float
    stepdown_mm: float
    notes: str


@dataclass
class PocketJob:
    width_mm: float
    height_mm: float
    depth_mm: float
    tool_diameter_mm: float
    stepover_mm: float
    stepdown_mm: float
    feed_rate_mm_min: float
    plunge_rate_mm_min: float
    spindle_rpm: int
    safe_z_mm: float = 5.0
    floor_z_mm: float = 0.0
    finish_allowance_mm: float = 0.2
    ramp_length_mm: float = 6.0
    finish_pass: bool = True
    material_name: str = "hardwood"


@dataclass
class CircularPocketJob:
    diameter_mm: float
    depth_mm: float
    tool_diameter_mm: float
    stepover_mm: float
    stepdown_mm: float
    feed_rate_mm_min: float
    plunge_rate_mm_min: float
    spindle_rpm: int
    safe_z_mm: float = 5.0
    floor_z_mm: float = 0.0
    segments: int = 96
    finish_allowance_mm: float = 0.15
    ramp_length_mm: float = 4.0
    finish_pass: bool = True
    material_name: str = "wax"


@dataclass
class RingBandJob:
    outer_diameter_mm: float
    inner_diameter_mm: float
    stock_thickness_mm: float
    tool_diameter_mm: float
    depth_mm: float
    stepdown_mm: float
    feed_rate_mm_min: float
    plunge_rate_mm_min: float
    spindle_rpm: int
    safe_z_mm: float = 5.0
    tabs: int = 4
    segments: int = 128
    tab_width_deg: float = 12.0
    tab_height_mm: float = 1.0
    finish_allowance_mm: float = 0.1
    ramp_length_mm: float = 3.0
    material_name: str = "brass"


DEFAULT_MACHINE = MachineProfile(
    name="Genmitsu_4040_PRO_Makita_RT0701C",
    post_processor="GRBL",
    work_area_x_mm=400.0,
    work_area_y_mm=400.0,
    work_area_z_mm=78.0,
    home_x_mm=0.0,
    home_y_mm=0.0,
    home_z_mm=15.0,
    spindle_rpm=18000,
    feed_rate_mm_min=900.0,
    plunge_rate_mm_min=250.0,
    spindle_min_rpm=10000,
    spindle_max_rpm=30000,
    controller="Genmitsu GRBL Controller",
    spindle_model="Makita RT0701C",
)

DEFAULT_TOOLS = [
    ToolProfile(
        name="flat_6.00mm_4F",
        cutter_type="ENDMILL",
        diameter_mm=6.0,
        flutes=4,
        spindle_rpm=10000,
        feed_rate_mm_min=900.0,
        plunge_rate_mm_min=250.0,
        stepover_percent=40.0,
        stepdown_mm=1.5,
    ),
    ToolProfile(
        name="flat_3.00mm_2F",
        cutter_type="ENDMILL",
        diameter_mm=3.0,
        flutes=2,
        spindle_rpm=12000,
        feed_rate_mm_min=700.0,
        plunge_rate_mm_min=180.0,
        stepover_percent=35.0,
        stepdown_mm=1.0,
    ),
    ToolProfile(
        name="ball_0.50mm_tapered",
        cutter_type="BALLNOSE",
        diameter_mm=0.5,
        flutes=2,
        spindle_rpm=12000,
        feed_rate_mm_min=350.0,
        plunge_rate_mm_min=120.0,
        stepover_percent=15.0,
        stepdown_mm=0.25,
    ),
]

DEFAULT_OPERATIONS = [
    OperationProfile(
        name="Pocket_Roughing_4040_PRO",
        strategy="POCKET",
        cutter_type="ENDMILL",
        spindle_rpm=10000,
        feed_rate_mm_min=900.0,
        plunge_rate_mm_min=250.0,
        stepover_percent=40.0,
        stepdown_mm=1.5,
        skin_mm=0.15,
    ),
    OperationProfile(
        name="Pocket_Finishing_4040_PRO",
        strategy="PARALLEL",
        cutter_type="BALLNOSE",
        spindle_rpm=12000,
        feed_rate_mm_min=350.0,
        plunge_rate_mm_min=120.0,
        stepover_percent=12.0,
        stepdown_mm=0.25,
        skin_mm=0.0,
    ),
    OperationProfile(
        name="Profile_Cutout_4040_PRO",
        strategy="CUTOUT",
        cutter_type="ENDMILL",
        spindle_rpm=10000,
        feed_rate_mm_min=800.0,
        plunge_rate_mm_min=220.0,
        stepover_percent=35.0,
        stepdown_mm=1.25,
        skin_mm=0.2,
    ),
]

DEFAULT_MATERIALS = {
    "hardwood": MaterialPreset(
        name="hardwood",
        spindle_rpm=10000,
        feed_rate_mm_min=900.0,
        plunge_rate_mm_min=250.0,
        finish_feed_mm_min=500.0,
        stepover_percent=40.0,
        stepdown_mm=1.5,
        notes="General hardwood setting for Genmitsu 4040-PRO pocket and profile work.",
    ),
    "wax": MaterialPreset(
        name="wax",
        spindle_rpm=12000,
        feed_rate_mm_min=700.0,
        plunge_rate_mm_min=180.0,
        finish_feed_mm_min=320.0,
        stepover_percent=18.0,
        stepdown_mm=0.8,
        notes="Jewelry wax or machinable wax for mold and ring work.",
    ),
    "brass": MaterialPreset(
        name="brass",
        spindle_rpm=9000,
        feed_rate_mm_min=320.0,
        plunge_rate_mm_min=120.0,
        finish_feed_mm_min=180.0,
        stepover_percent=15.0,
        stepdown_mm=0.4,
        notes="Conservative brass baseline. Verify with your spindle rigidity and tooling.",
    ),
}


MAKITA_ROUTER_PROFILE = {
    "model": "Makita RT0701C",
    "power": "120V 6.5A",
    "speed_range_rpm": [10000, 30000],
    "collet": "1/4in (6.35mm)",
    "mount": "Genmitsu 4040-PRO stock router mount",
    "notes": "Speed dial scales to router RPM. Calibrate actual RPM for your dial marks.",
}


# Captured from attached SpeTool tooling labels where legible.
MAKITA_BIT_LIBRARY = [
    {
        "tool_id": "spetool_downcut_1_4in",
        "label": "SP-1/4 Dia1/4 W04019",
        "category": "downcut_endmill",
        "diameter_mm": 6.35,
        "shank_mm": 6.35,
        "flutes": 2,
        "coating": "SPE-X",
    },
    {
        "tool_id": "spetool_downcut_1_8in",
        "label": "SP-1/8 Dia1/4",
        "category": "downcut_endmill",
        "diameter_mm": 3.175,
        "shank_mm": 6.35,
        "flutes": 2,
        "coating": "SPE-X",
    },
    {
        "tool_id": "spetool_vbit_20deg_fine",
        "label": "D1/4-20deg-0.005 W06008",
        "category": "vbit",
        "tip_mm": 0.127,
        "angle_deg": 20.0,
        "shank_mm": 6.35,
        "coating": "SPE-X",
    },
    {
        "tool_id": "spetool_vbit_30deg",
        "label": "ECP4F-D1/4 W06021 30deg",
        "category": "vbit",
        "angle_deg": 30.0,
        "shank_mm": 6.35,
    },
    {
        "tool_id": "spetool_vbit_60deg",
        "label": "ECP4F-D1/4 W06006 60deg",
        "category": "vbit",
        "angle_deg": 60.0,
        "shank_mm": 6.35,
    },
    {
        "tool_id": "spetool_vbit_90deg",
        "label": "ECP4F-D1/4 W06007 90deg",
        "category": "vbit",
        "angle_deg": 90.0,
        "shank_mm": 6.35,
    },
    {
        "tool_id": "spetool_ballnose_r1_32",
        "label": "R1/32 W01015",
        "category": "ballnose",
        "radius_mm": 0.79375,
        "shank_mm": 6.35,
    },
    {
        "tool_id": "spetool_ballnose_r1_16",
        "label": "R1/16 W01014",
        "category": "ballnose",
        "radius_mm": 1.5875,
        "shank_mm": 6.35,
        "coating": "ZrN",
    },
    {
        "tool_id": "spetool_ballnose_r0_25",
        "label": "R0.25 W01005",
        "category": "ballnose",
        "radius_mm": 0.25,
        "shank_mm": 6.35,
        "coating": "H-Si",
    },
    {
        "tool_id": "spetool_ballnose_r0_5",
        "label": "R0.5 W01007",
        "category": "ballnose",
        "radius_mm": 0.5,
        "shank_mm": 6.35,
        "coating": "H-Si",
    },
    {
        "tool_id": "spetool_ballnose_r1_0",
        "label": "R1.0 W01011",
        "category": "ballnose",
        "radius_mm": 1.0,
        "shank_mm": 6.35,
        "coating": "H-Si",
    },
    {
        "tool_id": "spetool_ballnose_r1_5",
        "label": "R1.5 W01013",
        "category": "ballnose",
        "radius_mm": 1.5,
        "shank_mm": 6.35,
        "coating": "H-Si",
    },
    {
        "tool_id": "router_bit_set_1_4in_mixed",
        "label": "1/4in shank woodworking router bit assortment (from photo)",
        "category": "wood_router_bits",
        "shank_mm": 6.35,
        "notes": "Includes profile, roundover, straight, and chamfer styles. Validate geometry before CNC contouring.",
    },
]


FAMILY_CATEGORY_MAP = {
    "ring_band": "rings",
    "signet_blank": "rings",
    "gallery_ring": "rings",
    "pierced_bezel_ring": "rings",
    "bezel_pocket": "bezels",
    "round_bezel_pocket": "bezels",
    "oval_bezel_pocket": "bezels",
    "pendant_blank": "pendants",
    "basket_pendant": "pendants",
    "coin_blank": "pendants",
    "dogtag_blank": "pendants",
    "bangle_blank": "bracelets",
    "cuff_blank": "bracelets",
    "toggle_bracelet_blank": "bracelets",
    "stud_earring_blank": "earrings",
    "hoop_earring": "earrings",
    "tray_mold": "utility",
}


CATEGORY_DEFAULT_MATERIAL = {
    "rings": "wax",
    "bezels": "wax",
    "pendants": "wax",
    "bracelets": "hardwood",
    "earrings": "wax",
    "utility": "hardwood",
}


CATEGORY_TOOL_PRIORITY = {
    "rings": ["spetool_ballnose_r1_32", "spetool_ballnose_r1_16", "spetool_downcut_1_8in"],
    "bezels": ["spetool_ballnose_r1_32", "spetool_vbit_30deg", "spetool_downcut_1_8in"],
    "pendants": ["spetool_downcut_1_8in", "spetool_vbit_60deg", "spetool_ballnose_r1_16"],
    "bracelets": ["spetool_downcut_1_4in", "spetool_downcut_1_8in", "spetool_vbit_90deg"],
    "earrings": ["spetool_ballnose_r1_32", "spetool_downcut_1_8in", "spetool_vbit_20deg_fine"],
    "utility": ["spetool_downcut_1_4in", "spetool_downcut_1_8in", "spetool_vbit_90deg"],
}


CATEGORY_STACK_TEMPLATES = {
    "rings": [
        {"stage": "rough_profile", "strategy": "POCKET", "stepdown_mm": 0.8, "stepover_percent": 35.0},
        {"stage": "detail_contour", "strategy": "PARALLEL", "stepdown_mm": 0.35, "stepover_percent": 16.0},
        {"stage": "finish_wall", "strategy": "CUTOUT", "stepdown_mm": 0.2, "stepover_percent": 10.0},
    ],
    "bezels": [
        {"stage": "rough_seat", "strategy": "POCKET", "stepdown_mm": 0.5, "stepover_percent": 28.0},
        {"stage": "bezel_detail", "strategy": "PARALLEL", "stepdown_mm": 0.2, "stepover_percent": 12.0},
        {"stage": "seat_finish", "strategy": "CUTOUT", "stepdown_mm": 0.15, "stepover_percent": 10.0},
    ],
    "pendants": [
        {"stage": "rough_face", "strategy": "POCKET", "stepdown_mm": 0.8, "stepover_percent": 35.0},
        {"stage": "detail_face", "strategy": "PARALLEL", "stepdown_mm": 0.3, "stepover_percent": 15.0},
        {"stage": "edge_cutout", "strategy": "CUTOUT", "stepdown_mm": 0.4, "stepover_percent": 20.0},
    ],
    "bracelets": [
        {"stage": "rough_shape", "strategy": "POCKET", "stepdown_mm": 1.2, "stepover_percent": 40.0},
        {"stage": "detail_shape", "strategy": "PARALLEL", "stepdown_mm": 0.4, "stepover_percent": 20.0},
        {"stage": "finish_outline", "strategy": "CUTOUT", "stepdown_mm": 0.35, "stepover_percent": 18.0},
    ],
    "earrings": [
        {"stage": "rough_pair", "strategy": "POCKET", "stepdown_mm": 0.5, "stepover_percent": 30.0},
        {"stage": "detail_pair", "strategy": "PARALLEL", "stepdown_mm": 0.2, "stepover_percent": 12.0},
        {"stage": "finish_pair", "strategy": "CUTOUT", "stepdown_mm": 0.15, "stepover_percent": 10.0},
    ],
    "utility": [
        {"stage": "roughing", "strategy": "POCKET", "stepdown_mm": 1.2, "stepover_percent": 40.0},
        {"stage": "finishing", "strategy": "PARALLEL", "stepdown_mm": 0.4, "stepover_percent": 20.0},
        {"stage": "cutout", "strategy": "CUTOUT", "stepdown_mm": 0.35, "stepover_percent": 18.0},
    ],
}


def default_fabex_preset_root() -> Path:
    return Path.home() / "AppData/Roaming/Blender Foundation/Blender/4.5/extensions/user_default/fabex/presets"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def machine_preset_content(profile: MachineProfile) -> str:
    return f'''### {profile.name}.py ###

import bpy

d = bpy.context.scene.cam_machine
s = bpy.context.scene.unit_settings

s.system, s.length_unit = ("METRIC", "MILLIMETERS")

d.post_processor = "{profile.post_processor}"
d.unit_system = "MILLIMETERS"
d.use_position_definitions = True
d.starting_position = ({profile.home_x_mm * MM_TO_M:.6f}, {profile.home_y_mm * MM_TO_M:.6f}, {profile.home_z_mm * MM_TO_M:.6f})
d.mtc_position = ({profile.home_x_mm * MM_TO_M:.6f}, {profile.home_y_mm * MM_TO_M:.6f}, {profile.home_z_mm * MM_TO_M:.6f})
d.ending_position = ({profile.home_x_mm * MM_TO_M:.6f}, {profile.home_y_mm * MM_TO_M:.6f}, {profile.home_z_mm * MM_TO_M:.6f})
d.working_area = ({profile.work_area_x_mm * MM_TO_M:.6f}, {profile.work_area_y_mm * MM_TO_M:.6f}, {profile.work_area_z_mm * MM_TO_M:.6f})
d.feedrate_min = {min(50.0, profile.feed_rate_mm_min) * MM_TO_M:.6f}
d.feedrate_max = {max(profile.feed_rate_mm_min * 2.0, profile.feed_rate_mm_min) * MM_TO_M:.6f}
d.feedrate_default = {profile.feed_rate_mm_min * MM_TO_M:.6f}
d.spindle_min = {profile.spindle_min_rpm}
d.spindle_max = {profile.spindle_max_rpm}
d.spindle_default = {profile.spindle_rpm}
d.axis_4 = {str(profile.axis_4)}
d.axis_5 = False

if hasattr(d, "rotary_axis_1"):
    d.rotary_axis_1 = "{profile.rotary_axis}"

print("Loaded machine preset: {profile.name}")
'''


def tool_preset_content(profile: ToolProfile) -> str:
    cutter_type = "END" if profile.cutter_type == "ENDMILL" else profile.cutter_type
    return f'''import bpy

d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]

d.cutter_type = "{cutter_type}"
d.cutter_diameter = {profile.diameter_mm * MM_TO_M:.6f}
d.cutter_length = {profile.cutter_length_mm:.1f}
d.cutter_tip_angle = {profile.cutter_tip_angle:.1f}

if hasattr(d, "cutter_flutes"):
    d.cutter_flutes = {profile.flutes}

d.spindle_rpm = {profile.spindle_rpm}
d.feedrate = {profile.feed_rate_mm_min * MM_TO_M:.6f}
d.plunge_feedrate = {profile.plunge_rate_mm_min * MM_TO_M:.6f}
d.stepover = {profile.stepover_percent / 100.0:.6f}
d.stepdown = {profile.stepdown_mm * MM_TO_M:.6f}
'''


def operation_preset_content(profile: OperationProfile) -> str:
    cutter_type = "END" if profile.cutter_type == "ENDMILL" else profile.cutter_type
    return f'''import bpy
from pathlib import Path

bpy.ops.scene.cam_operation_add()

scene = bpy.context.scene
o = scene.cam_operations[scene.cam_active_operation]

o.ambient_behaviour = "{profile.ambient_behaviour}"
o.cutter_type = "{cutter_type}"
o.feedrate = {profile.feed_rate_mm_min * MM_TO_M:.6f}
o.plunge_feedrate = {profile.plunge_rate_mm_min * MM_TO_M:.6f}
o.filename = o.name = f"{{scene.cam_names.operation_name_full}}_{{Path(__file__).stem}}"
o.movement_type = "{profile.movement_type}"
o.skin = {profile.skin_mm * MM_TO_M:.6f}
o.spindle = {float(profile.spindle_rpm):.1f}
o.stepdown = {profile.stepdown_mm * MM_TO_M:.6f}
o.strategy = "{profile.strategy}"

if hasattr(o, "distance_between_paths"):
    o.distance_between_paths = {profile.stepover_percent / 100.0 * 0.001:.6f}
'''


def build_presets(output_dir: Path) -> list[Path]:
    preset_root = ensure_dir(output_dir / "presets")
    machine_dir = ensure_dir(preset_root / "cam_machines")
    cutter_dir = ensure_dir(preset_root / "cam_cutters")
    operation_dir = ensure_dir(preset_root / "cam_operations")
    written = []

    machine_path = machine_dir / f"{DEFAULT_MACHINE.name}.py"
    write_text(machine_path, machine_preset_content(DEFAULT_MACHINE))
    written.append(machine_path)

    for tool in DEFAULT_TOOLS:
        path = cutter_dir / f"{tool.name}.py"
        write_text(path, tool_preset_content(tool))
        written.append(path)

    for operation in DEFAULT_OPERATIONS:
        path = operation_dir / f"{operation.name}.py"
        write_text(path, operation_preset_content(operation))
        written.append(path)

    manifest_path = preset_root / "preset_manifest.json"
    manifest = {
        "machine": asdict(DEFAULT_MACHINE),
        "tools": [asdict(tool) for tool in DEFAULT_TOOLS],
        "operations": [asdict(operation) for operation in DEFAULT_OPERATIONS],
        "router": MAKITA_ROUTER_PROFILE,
        "bit_library": MAKITA_BIT_LIBRARY,
    }
    write_text(manifest_path, json.dumps(manifest, indent=2))
    written.append(manifest_path)
    return written


def template_manifest(output_dir: Path) -> dict[str, Any]:
    manifest_path = output_dir / "templates" / "template_manifest.json"
    if not manifest_path.exists():
        build_templates(output_dir)
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def build_full_batch_profiles(output_dir: Path) -> list[Path]:
    written = []
    manifest = template_manifest(output_dir)

    machine_dir = ensure_dir(output_dir / "machine_profiles")
    batch_root = ensure_dir(output_dir / "full_batch")
    stack_dir = ensure_dir(batch_root / "fabex_operation_stacks")
    gcode_profile_dir = ensure_dir(batch_root / "machine_gcode_profiles")

    machine_profile_path = machine_dir / "genmitsu_4040_pro_makita_rt0701c.json"
    machine_profile = {
        "machine": asdict(DEFAULT_MACHINE),
        "router": MAKITA_ROUTER_PROFILE,
        "notes": [
            "Generated for Genmitsu 4040-PRO workflows using Makita RT0701C.",
            "Validate zeroing, workholding, and tool stickout for each job.",
        ],
    }
    write_text(machine_profile_path, json.dumps(machine_profile, indent=2))
    written.append(machine_profile_path)

    bit_library_path = machine_dir / "genmitsu_4040_pro_makita_bits.json"
    bit_profile = {
        "machine_profile": "genmitsu_4040_pro_makita_rt0701c",
        "bit_library": MAKITA_BIT_LIBRARY,
        "source": "User-supplied tool photos and label transcription.",
    }
    write_text(bit_library_path, json.dumps(bit_profile, indent=2))
    written.append(bit_library_path)

    summary = {
        "machine_profile": str(machine_profile_path.name),
        "bit_library": str(bit_library_path.name),
        "families": {},
    }

    for family_name, geometry in manifest.items():
        category = FAMILY_CATEGORY_MAP.get(family_name, "utility")
        material = CATEGORY_DEFAULT_MATERIAL.get(category, "hardwood")
        stack_template = CATEGORY_STACK_TEMPLATES.get(category, CATEGORY_STACK_TEMPLATES["utility"])
        tool_priority = CATEGORY_TOOL_PRIORITY.get(category, CATEGORY_TOOL_PRIORITY["utility"])

        operations = []
        for index, stage in enumerate(stack_template, start=1):
            operation = {
                "operation_name": f"{family_name}_{index:02d}_{stage['stage']}",
                "strategy": stage["strategy"],
                "material": material,
                "recommended_tool_ids": tool_priority,
                "stepdown_mm": stage["stepdown_mm"],
                "stepover_percent": stage["stepover_percent"],
                "spindle_rpm": DEFAULT_MATERIALS[material].spindle_rpm,
                "feed_rate_mm_min": DEFAULT_MATERIALS[material].feed_rate_mm_min,
                "plunge_rate_mm_min": DEFAULT_MATERIALS[material].plunge_rate_mm_min,
                "safe_z_mm": 5.0,
                "entry_style": "ramp",
                "tabs": 4 if "ring" in family_name or "bracelet" in family_name else 0,
            }
            operations.append(operation)

        stack_doc = {
            "family": family_name,
            "category": category,
            "machine_profile": "genmitsu_4040_pro_makita_rt0701c",
            "geometry": geometry,
            "fabex_operation_stack": operations,
        }
        stack_path = stack_dir / f"{family_name}_fabex_stack.json"
        write_text(stack_path, json.dumps(stack_doc, indent=2))
        written.append(stack_path)

        gcode_profile = {
            "family": family_name,
            "category": category,
            "machine_profile": "genmitsu_4040_pro_makita_rt0701c",
            "post_processor": DEFAULT_MACHINE.post_processor,
            "router": MAKITA_ROUTER_PROFILE,
            "default_material": material,
            "recommended_tool_ids": tool_priority,
            "safe_z_mm": 5.0,
            "spindle_rpm": DEFAULT_MATERIALS[material].spindle_rpm,
            "feed_rate_mm_min": DEFAULT_MATERIALS[material].feed_rate_mm_min,
            "plunge_rate_mm_min": DEFAULT_MATERIALS[material].plunge_rate_mm_min,
            "stepdown_mm": DEFAULT_MATERIALS[material].stepdown_mm,
            "stepover_percent": DEFAULT_MATERIALS[material].stepover_percent,
            "finish_feed_mm_min": DEFAULT_MATERIALS[material].finish_feed_mm_min,
            "controller_notes": [
                "Use conservative first-pass depth for new tools/materials.",
                "Confirm Makita dial setting maps to target RPM.",
            ],
        }
        gcode_path = gcode_profile_dir / f"{family_name}_genmitsu4040_makita_profile.json"
        write_text(gcode_path, json.dumps(gcode_profile, indent=2))
        written.append(gcode_path)

        summary["families"][family_name] = {
            "category": category,
            "stack_file": stack_path.name,
            "gcode_profile_file": gcode_path.name,
            "default_material": material,
        }

    summary_path = batch_root / "full_batch_summary.json"
    write_text(summary_path, json.dumps(summary, indent=2))
    written.append(summary_path)
    return written


def install_presets(output_dir: Path, fabex_root: Path) -> list[Path]:
    source_root = output_dir / "presets"
    installed = []
    mapping = {
        source_root / "cam_machines": fabex_root / "cam_machines",
        source_root / "cam_cutters": fabex_root / "cam_cutters",
        source_root / "cam_operations": fabex_root / "cam_operations",
    }
    for source_dir, target_dir in mapping.items():
        ensure_dir(target_dir)
        for source_file in source_dir.glob("*.py"):
            target_path = target_dir / source_file.name
            shutil.copy2(source_file, target_path)
            installed.append(target_path)
    return installed


def circle_points(radius: float, segments: int) -> list[tuple[float, float]]:
    return [
        (
            math.cos((2.0 * math.pi * index) / segments) * radius,
            math.sin((2.0 * math.pi * index) / segments) * radius,
        )
        for index in range(segments + 1)
    ]


def svg_path(points: Iterable[tuple[float, float]], close: bool = True) -> str:
    point_list = list(points)
    head = f"M {point_list[0][0]:.3f},{point_list[0][1]:.3f}"
    body = " ".join(f"L {x:.3f},{y:.3f}" for x, y in point_list[1:])
    tail = " Z" if close else ""
    return f"{head} {body}{tail}".strip()


def rounded_rect_points(width: float, height: float, radius: float, segments: int = 12) -> list[tuple[float, float]]:
    x_half = width / 2.0
    y_half = height / 2.0
    radius = min(radius, x_half, y_half)
    centers = [
        (x_half - radius, y_half - radius, 0.0),
        (-x_half + radius, y_half - radius, math.pi / 2.0),
        (-x_half + radius, -y_half + radius, math.pi),
        (x_half - radius, -y_half + radius, 3.0 * math.pi / 2.0),
    ]
    points: list[tuple[float, float]] = []
    for center_x, center_y, start_angle in centers:
        for index in range(segments + 1):
            angle = start_angle + (index / segments) * (math.pi / 2.0)
            points.append((center_x + math.cos(angle) * radius, center_y + math.sin(angle) * radius))
    return points


def ring_band_svg(outer_diameter_mm: float, inner_diameter_mm: float) -> str:
    outer = svg_path(circle_points(outer_diameter_mm / 2.0, 144))
    inner = svg_path(circle_points(inner_diameter_mm / 2.0, 144))
    size = outer_diameter_mm + 20.0
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-size/2:.1f} {-size/2:.1f} {size:.1f} {size:.1f}">
  <path d="{outer}" fill="none" stroke="black" stroke-width="0.25"/>
  <path d="{inner}" fill="none" stroke="red" stroke-width="0.25"/>
</svg>
'''


def tray_mold_svg(width_mm: float, height_mm: float, corner_radius_mm: float, pocket_margin_mm: float) -> str:
    outer = svg_path(rounded_rect_points(width_mm, height_mm, corner_radius_mm))
    pocket = svg_path(
        rounded_rect_points(
            width_mm - pocket_margin_mm * 2.0,
            height_mm - pocket_margin_mm * 2.0,
            max(corner_radius_mm - pocket_margin_mm, 1.0),
        )
    )
    view_w = width_mm + 20.0
    view_h = height_mm + 20.0
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-view_w/2:.1f} {-view_h/2:.1f} {view_w:.1f} {view_h:.1f}">
  <path d="{outer}" fill="none" stroke="black" stroke-width="0.25"/>
  <path d="{pocket}" fill="none" stroke="blue" stroke-width="0.25"/>
</svg>
'''


def signet_blank_svg(face_width_mm: float, face_height_mm: float, inner_diameter_mm: float) -> str:
    top = svg_path(rounded_rect_points(face_width_mm, face_height_mm, face_height_mm * 0.18))
    inner = svg_path(circle_points(inner_diameter_mm / 2.0, 144))
    size = max(face_width_mm, face_height_mm) + 30.0
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-size/2:.1f} {-size/2:.1f} {size:.1f} {size:.1f}">
  <path d="{top}" fill="none" stroke="black" stroke-width="0.25"/>
  <path d="{inner}" fill="none" stroke="purple" stroke-width="0.25"/>
</svg>
'''


def bezel_pocket_svg(outer_width_mm: float, outer_height_mm: float, stone_width_mm: float, stone_height_mm: float) -> str:
    outer = svg_path(rounded_rect_points(outer_width_mm, outer_height_mm, min(outer_width_mm, outer_height_mm) * 0.12))
    seat = svg_path(rounded_rect_points(stone_width_mm, stone_height_mm, min(stone_width_mm, stone_height_mm) * 0.08))
    view_w = outer_width_mm + 20.0
    view_h = outer_height_mm + 20.0
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-view_w/2:.1f} {-view_h/2:.1f} {view_w:.1f} {view_h:.1f}">
  <path d="{outer}" fill="none" stroke="black" stroke-width="0.25"/>
  <path d="{seat}" fill="none" stroke="green" stroke-width="0.25"/>
</svg>
'''


def pendant_blank_svg(width_mm: float, height_mm: float, bail_hole_mm: float) -> str:
        body = svg_path(rounded_rect_points(width_mm, height_mm, min(width_mm, height_mm) * 0.22))
        bail = svg_path(circle_points(bail_hole_mm / 2.0, 96))
        view_w = width_mm + 18.0
        view_h = height_mm + 18.0
        bail_y = height_mm / 2.0 - bail_hole_mm * 0.9
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-view_w/2:.1f} {-view_h/2:.1f} {view_w:.1f} {view_h:.1f}">
    <path d="{body}" fill="none" stroke="black" stroke-width="0.25"/>
    <g transform="translate(0,-{bail_y:.3f})">
        <path d="{bail}" fill="none" stroke="orange" stroke-width="0.25"/>
    </g>
</svg>
'''


def oval_bezel_pocket_svg(outer_width_mm: float, outer_height_mm: float, stone_width_mm: float, stone_height_mm: float) -> str:
        outer = svg_path(circle_points(outer_width_mm / 2.0, 144), close=True)
        seat = svg_path(circle_points(stone_width_mm / 2.0, 144), close=True)
        scale_outer_y = outer_height_mm / outer_width_mm
        scale_seat_y = stone_height_mm / stone_width_mm
        view_w = outer_width_mm + 18.0
        view_h = outer_height_mm + 18.0
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-view_w/2:.1f} {-view_h/2:.1f} {view_w:.1f} {view_h:.1f}">
    <g transform="scale(1,{scale_outer_y:.6f})">
        <path d="{outer}" fill="none" stroke="black" stroke-width="0.25"/>
    </g>
    <g transform="scale(1,{scale_seat_y:.6f})">
        <path d="{seat}" fill="none" stroke="teal" stroke-width="0.25"/>
    </g>
</svg>
'''


def stud_earring_blank_svg(diameter_mm: float, post_hole_mm: float) -> str:
        outer = svg_path(circle_points(diameter_mm / 2.0, 144))
        post = svg_path(circle_points(post_hole_mm / 2.0, 96))
        pair_offset = diameter_mm * 0.9
        size = diameter_mm * 2.8
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-size/2:.1f} {-size/2:.1f} {size:.1f} {size:.1f}">
    <g transform="translate(-{pair_offset/2:.3f},0)">
        <path d="{outer}" fill="none" stroke="black" stroke-width="0.25"/>
        <path d="{post}" fill="none" stroke="red" stroke-width="0.25"/>
    </g>
    <g transform="translate({pair_offset/2:.3f},0)">
        <path d="{outer}" fill="none" stroke="black" stroke-width="0.25"/>
        <path d="{post}" fill="none" stroke="red" stroke-width="0.25"/>
    </g>
</svg>
'''


def coin_blank_svg(diameter_mm: float) -> str:
        outer = svg_path(circle_points(diameter_mm / 2.0, 144))
        size = diameter_mm + 18.0
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-size/2:.1f} {-size/2:.1f} {size:.1f} {size:.1f}">
    <path d="{outer}" fill="none" stroke="black" stroke-width="0.25"/>
</svg>
'''


def round_bezel_pocket_svg(outer_diameter_mm: float, stone_diameter_mm: float) -> str:
        outer = svg_path(circle_points(outer_diameter_mm / 2.0, 144))
        seat = svg_path(circle_points(stone_diameter_mm / 2.0, 144))
        size = outer_diameter_mm + 18.0
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-size/2:.1f} {-size/2:.1f} {size:.1f} {size:.1f}">
    <path d="{outer}" fill="none" stroke="black" stroke-width="0.25"/>
    <path d="{seat}" fill="none" stroke="forestgreen" stroke-width="0.25"/>
</svg>
'''


def bangle_blank_svg(outer_diameter_mm: float, inner_diameter_mm: float) -> str:
        outer = svg_path(circle_points(outer_diameter_mm / 2.0, 180))
        inner = svg_path(circle_points(inner_diameter_mm / 2.0, 180))
        size = outer_diameter_mm + 24.0
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-size/2:.1f} {-size/2:.1f} {size:.1f} {size:.1f}">
    <path d="{outer}" fill="none" stroke="black" stroke-width="0.25"/>
    <path d="{inner}" fill="none" stroke="sienna" stroke-width="0.25"/>
</svg>
'''


def dogtag_blank_svg(width_mm: float, height_mm: float, corner_radius_mm: float, hole_diameter_mm: float) -> str:
        body = svg_path(rounded_rect_points(width_mm, height_mm, corner_radius_mm))
        hole = svg_path(circle_points(hole_diameter_mm / 2.0, 96))
        view_w = width_mm + 18.0
        view_h = height_mm + 18.0
        hole_y = height_mm / 2.0 - hole_diameter_mm * 1.1
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-view_w/2:.1f} {-view_h/2:.1f} {view_w:.1f} {view_h:.1f}">
    <path d="{body}" fill="none" stroke="black" stroke-width="0.25"/>
    <g transform="translate(0,-{hole_y:.3f})">
        <path d="{hole}" fill="none" stroke="crimson" stroke-width="0.25"/>
    </g>
</svg>
'''


def cuff_blank_svg(length_mm: float, width_mm: float, corner_radius_mm: float) -> str:
        body = svg_path(rounded_rect_points(length_mm, width_mm, corner_radius_mm))
        view_w = length_mm + 18.0
        view_h = width_mm + 18.0
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-view_w/2:.1f} {-view_h/2:.1f} {view_w:.1f} {view_h:.1f}">
    <path d="{body}" fill="none" stroke="black" stroke-width="0.25"/>
</svg>
'''


def gallery_ring_svg(outer_diameter_mm: float, inner_diameter_mm: float, gallery_width_mm: float, gallery_height_mm: float) -> str:
        ring_outer = svg_path(circle_points(outer_diameter_mm / 2.0, 180))
        ring_inner = svg_path(circle_points(inner_diameter_mm / 2.0, 180))
        gallery = svg_path(rounded_rect_points(gallery_width_mm, gallery_height_mm, gallery_height_mm * 0.18))
        size = max(outer_diameter_mm, gallery_width_mm + 12.0) + 18.0
        gallery_y = outer_diameter_mm / 2.0 + gallery_height_mm * 0.55
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-size/2:.1f} {-size/2:.1f} {size:.1f} {size:.1f}">
    <path d="{ring_outer}" fill="none" stroke="black" stroke-width="0.25"/>
    <path d="{ring_inner}" fill="none" stroke="sienna" stroke-width="0.25"/>
    <g transform="translate(0,-{gallery_y:.3f})">
        <path d="{gallery}" fill="none" stroke="indigo" stroke-width="0.25"/>
    </g>
</svg>
'''


def basket_pendant_svg(outer_diameter_mm: float, seat_diameter_mm: float, bail_hole_mm: float) -> str:
        outer = svg_path(circle_points(outer_diameter_mm / 2.0, 180))
        seat = svg_path(circle_points(seat_diameter_mm / 2.0, 144))
        bail = svg_path(circle_points(bail_hole_mm / 2.0, 96))
        size = outer_diameter_mm + 20.0
        bail_y = outer_diameter_mm / 2.0 + bail_hole_mm * 0.2
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-size/2:.1f} {-size/2:.1f} {size:.1f} {size:.1f}">
    <path d="{outer}" fill="none" stroke="black" stroke-width="0.25"/>
    <path d="{seat}" fill="none" stroke="darkgreen" stroke-width="0.25"/>
    <g transform="translate(0,-{bail_y:.3f})">
        <path d="{bail}" fill="none" stroke="orange" stroke-width="0.25"/>
    </g>
</svg>
'''


def pierced_bezel_ring_svg(outer_diameter_mm: float, inner_diameter_mm: float, bezel_diameter_mm: float, pierce_count: int = 10) -> str:
        ring_outer = svg_path(circle_points(outer_diameter_mm / 2.0, 180))
        ring_inner = svg_path(circle_points(inner_diameter_mm / 2.0, 180))
        bezel = svg_path(circle_points(bezel_diameter_mm / 2.0, 144))
        hole = svg_path(circle_points(0.75, 64))
        size = max(outer_diameter_mm, bezel_diameter_mm + 14.0) + 20.0
        bezel_y = outer_diameter_mm / 2.0 + bezel_diameter_mm * 0.45
        hole_radius = bezel_diameter_mm * 0.34
        holes = []
        for index in range(max(pierce_count, 4)):
                angle = (2.0 * math.pi * index) / pierce_count
                x = math.cos(angle) * hole_radius
                y = math.sin(angle) * hole_radius
                holes.append(f'<g transform="translate({x:.3f},{y:.3f})"><path d="{hole}" fill="none" stroke="crimson" stroke-width="0.2"/></g>')
        holes_markup = "\n        ".join(holes)
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-size/2:.1f} {-size/2:.1f} {size:.1f} {size:.1f}">
    <path d="{ring_outer}" fill="none" stroke="black" stroke-width="0.25"/>
    <path d="{ring_inner}" fill="none" stroke="sienna" stroke-width="0.25"/>
    <g transform="translate(0,-{bezel_y:.3f})">
        <path d="{bezel}" fill="none" stroke="darkblue" stroke-width="0.25"/>
        {holes_markup}
    </g>
</svg>
'''


def hoop_earring_svg(outer_diameter_mm: float, wire_diameter_mm: float, pair_spacing_mm: float) -> str:
        inner_diameter_mm = max(outer_diameter_mm - wire_diameter_mm * 2.0, outer_diameter_mm * 0.35)
        outer = svg_path(circle_points(outer_diameter_mm / 2.0, 180))
        inner = svg_path(circle_points(inner_diameter_mm / 2.0, 180))
        size = outer_diameter_mm * 2.0 + pair_spacing_mm
        offset = pair_spacing_mm / 2.0
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-size/2:.1f} {-outer_diameter_mm:.1f} {size:.1f} {outer_diameter_mm * 2.0:.1f}">
    <g transform="translate(-{offset:.3f},0)">
        <path d="{outer}" fill="none" stroke="black" stroke-width="0.25"/>
        <path d="{inner}" fill="none" stroke="gray" stroke-width="0.25"/>
    </g>
    <g transform="translate({offset:.3f},0)">
        <path d="{outer}" fill="none" stroke="black" stroke-width="0.25"/>
        <path d="{inner}" fill="none" stroke="gray" stroke-width="0.25"/>
    </g>
</svg>
'''


def toggle_bracelet_blank_svg(length_mm: float, width_mm: float, ring_outer_mm: float, ring_inner_mm: float) -> str:
        bar = svg_path(rounded_rect_points(length_mm, width_mm, width_mm * 0.35))
        ring_outer = svg_path(circle_points(ring_outer_mm / 2.0, 180))
        ring_inner = svg_path(circle_points(ring_inner_mm / 2.0, 180))
        view_w = max(length_mm + ring_outer_mm + 24.0, length_mm * 1.45)
        view_h = max(width_mm + 20.0, ring_outer_mm + 20.0)
        ring_x = length_mm / 2.0 + ring_outer_mm * 0.6
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-view_w/2:.1f} {-view_h/2:.1f} {view_w:.1f} {view_h:.1f}">
    <path d="{bar}" fill="none" stroke="black" stroke-width="0.25"/>
    <g transform="translate({ring_x:.3f},0)">
        <path d="{ring_outer}" fill="none" stroke="darkslateblue" stroke-width="0.25"/>
        <path d="{ring_inner}" fill="none" stroke="slategray" stroke-width="0.25"/>
    </g>
</svg>
'''


def ring_band_blender_script(outer_diameter_mm: float, inner_diameter_mm: float, thickness_mm: float) -> str:
    return f'''"""Create a parametric ring/band blank in Blender."""

import bpy

outer_radius = {outer_diameter_mm / 2.0 * MM_TO_M:.6f}
inner_radius = {inner_diameter_mm / 2.0 * MM_TO_M:.6f}
thickness = {thickness_mm * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=outer_radius, depth=thickness)
outer_obj = bpy.context.active_object
outer_obj.name = "RingBandOuter"

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=inner_radius, depth=thickness * 1.2)
inner_obj = bpy.context.active_object
inner_obj.name = "RingBandInner"

modifier = outer_obj.modifiers.new(name="InnerCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = inner_obj
bpy.context.view_layer.objects.active = outer_obj
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(inner_obj, do_unlink=True)

print("Created parametric ring/band blank")
'''


def tray_mold_blender_script(width_mm: float, height_mm: float, depth_mm: float, corner_radius_mm: float, pocket_margin_mm: float) -> str:
    return f'''"""Create a parametric tray mold blank in Blender."""

import bpy

width = {width_mm * MM_TO_M:.6f}
height = {height_mm * MM_TO_M:.6f}
depth = {depth_mm * MM_TO_M:.6f}
pocket_margin = {pocket_margin_mm * MM_TO_M:.6f}
corner_radius = {corner_radius_mm * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cube_add(size=1.0)
blank = bpy.context.active_object
blank.name = "TrayMoldBlank"
blank.scale = (width / 2.0, height / 2.0, depth / 2.0)

bpy.ops.mesh.primitive_cube_add(size=1.0)
pocket = bpy.context.active_object
pocket.name = "TrayPocket"
pocket.scale = ((width - pocket_margin * 2.0) / 2.0, (height - pocket_margin * 2.0) / 2.0, depth / 2.0)
pocket.location.z = pocket_margin / 2.0

bevel = pocket.modifiers.new(name="CornerRadius", type='BEVEL')
bevel.width = corner_radius
bevel.segments = 8
bpy.context.view_layer.objects.active = pocket
bpy.ops.object.modifier_apply(modifier=bevel.name)

modifier = blank.modifiers.new(name="PocketCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = pocket
bpy.context.view_layer.objects.active = blank
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(pocket, do_unlink=True)

print("Created parametric tray mold blank")
'''


def signet_blank_blender_script(face_width_mm: float, face_height_mm: float, inner_diameter_mm: float, shank_depth_mm: float) -> str:
    return f'''"""Create a parametric signet ring blank in Blender."""

import bpy

face_width = {face_width_mm * MM_TO_M:.6f}
face_height = {face_height_mm * MM_TO_M:.6f}
inner_radius = {inner_diameter_mm / 2.0 * MM_TO_M:.6f}
shank_depth = {shank_depth_mm * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cube_add(size=1.0)
face = bpy.context.active_object
face.name = "SignetFace"
face.scale = (face_width / 2.0, shank_depth / 2.0, face_height / 2.0)
face.location.z = face_height / 2.0

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=inner_radius * 1.4, depth=shank_depth)
band = bpy.context.active_object
band.name = "SignetBand"
band.rotation_euler.x = 1.57079632679

bpy.context.view_layer.objects.active = face
join_result = bpy.ops.object.join()
print(join_result)

print("Created parametric signet blank")
'''


def bezel_pocket_blender_script(outer_width_mm: float, outer_height_mm: float, depth_mm: float, stone_width_mm: float, stone_height_mm: float) -> str:
    return f'''"""Create a bezel pocket blank in Blender."""

import bpy

outer_width = {outer_width_mm * MM_TO_M:.6f}
outer_height = {outer_height_mm * MM_TO_M:.6f}
depth = {depth_mm * MM_TO_M:.6f}
stone_width = {stone_width_mm * MM_TO_M:.6f}
stone_height = {stone_height_mm * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cube_add(size=1.0)
base = bpy.context.active_object
base.name = "BezelBlank"
base.scale = (outer_width / 2.0, outer_height / 2.0, depth / 2.0)

bpy.ops.mesh.primitive_cube_add(size=1.0)
seat = bpy.context.active_object
seat.name = "BezelSeat"
seat.scale = (stone_width / 2.0, stone_height / 2.0, depth / 3.0)
seat.location.z = depth / 6.0

modifier = base.modifiers.new(name="SeatCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = seat
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(seat, do_unlink=True)

print("Created parametric bezel pocket")
'''


def pendant_blank_blender_script(width_mm: float, height_mm: float, thickness_mm: float, bail_hole_mm: float) -> str:
        return f'''"""Create a simple pendant blank in Blender."""

import bpy

width = {width_mm * MM_TO_M:.6f}
height = {height_mm * MM_TO_M:.6f}
thickness = {thickness_mm * MM_TO_M:.6f}
bail_radius = {bail_hole_mm / 2.0 * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=width / 2.0, depth=thickness)
body = bpy.context.active_object
body.name = "PendantBlank"
body.scale.y = height / width

bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=bail_radius, depth=thickness * 1.4)
bail = bpy.context.active_object
bail.name = "PendantBailHole"
bail.location.y = -(height / 2.0 - bail_radius * 1.8)

modifier = body.modifiers.new(name="BailHole", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = bail
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(bail, do_unlink=True)

print("Created pendant blank")
'''


def oval_bezel_pocket_blender_script(outer_width_mm: float, outer_height_mm: float, depth_mm: float, stone_width_mm: float, stone_height_mm: float) -> str:
        return f'''"""Create an oval bezel pocket blank in Blender."""

import bpy

outer_width = {outer_width_mm * MM_TO_M:.6f}
outer_height = {outer_height_mm * MM_TO_M:.6f}
depth = {depth_mm * MM_TO_M:.6f}
stone_width = {stone_width_mm * MM_TO_M:.6f}
stone_height = {stone_height_mm * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=outer_width / 2.0, depth=depth)
base = bpy.context.active_object
base.name = "OvalBezelBlank"
base.scale.y = outer_height / outer_width

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=stone_width / 2.0, depth=depth / 2.0)
seat = bpy.context.active_object
seat.name = "OvalBezelSeat"
seat.scale.y = stone_height / stone_width
seat.location.z = depth / 6.0

modifier = base.modifiers.new(name="SeatCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = seat
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(seat, do_unlink=True)

print("Created oval bezel pocket")
'''


def stud_earring_blank_blender_script(diameter_mm: float, thickness_mm: float, pair_spacing_mm: float) -> str:
        return f'''"""Create a stud earring blank pair in Blender."""

import bpy

diameter = {diameter_mm * MM_TO_M:.6f}
thickness = {thickness_mm * MM_TO_M:.6f}
spacing = {pair_spacing_mm * MM_TO_M:.6f}

for direction in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=diameter / 2.0, depth=thickness)
        disc = bpy.context.active_object
        disc.name = f"StudBlank_{{'L' if direction < 0 else 'R'}}"
        disc.location.x = direction * spacing / 2.0

print("Created stud earring blank pair")
'''


def coin_blank_blender_script(diameter_mm: float, thickness_mm: float) -> str:
    return f'''"""Create a coin blank in Blender."""

import bpy

diameter = {diameter_mm * MM_TO_M:.6f}
thickness = {thickness_mm * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=diameter / 2.0, depth=thickness)
coin = bpy.context.active_object
coin.name = "CoinBlank"

print("Created coin blank")
'''


def round_bezel_pocket_blender_script(outer_diameter_mm: float, depth_mm: float, stone_diameter_mm: float) -> str:
    return f'''"""Create a round bezel pocket blank in Blender."""

import bpy

outer_diameter = {outer_diameter_mm * MM_TO_M:.6f}
stone_diameter = {stone_diameter_mm * MM_TO_M:.6f}
depth = {depth_mm * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=outer_diameter / 2.0, depth=depth)
base = bpy.context.active_object
base.name = "RoundBezelBlank"

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=stone_diameter / 2.0, depth=depth / 2.0)
seat = bpy.context.active_object
seat.name = "RoundBezelSeat"
seat.location.z = depth / 6.0

modifier = base.modifiers.new(name="SeatCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = seat
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(seat, do_unlink=True)

print("Created round bezel pocket")
'''


def bangle_blank_blender_script(outer_diameter_mm: float, inner_diameter_mm: float, width_mm: float) -> str:
    return f'''"""Create a bangle blank in Blender."""

import bpy

outer_radius = {outer_diameter_mm / 2.0 * MM_TO_M:.6f}
inner_radius = {inner_diameter_mm / 2.0 * MM_TO_M:.6f}
width = {width_mm * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=outer_radius, depth=width)
outer_obj = bpy.context.active_object
outer_obj.name = "BangleBlankOuter"

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=inner_radius, depth=width * 1.2)
inner_obj = bpy.context.active_object
inner_obj.name = "BangleBlankInner"

modifier = outer_obj.modifiers.new(name="InnerCut", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = inner_obj
bpy.context.view_layer.objects.active = outer_obj
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(inner_obj, do_unlink=True)

print("Created bangle blank")
'''


def dogtag_blank_blender_script(width_mm: float, height_mm: float, thickness_mm: float, hole_diameter_mm: float) -> str:
    return f'''"""Create a dogtag blank in Blender."""

import bpy

width = {width_mm * MM_TO_M:.6f}
height = {height_mm * MM_TO_M:.6f}
thickness = {thickness_mm * MM_TO_M:.6f}
hole_radius = {hole_diameter_mm / 2.0 * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cube_add(size=1.0)
body = bpy.context.active_object
body.name = "DogtagBlank"
body.scale = (width / 2.0, height / 2.0, thickness / 2.0)

bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=hole_radius, depth=thickness * 1.4)
hole = bpy.context.active_object
hole.name = "DogtagHole"
hole.location.y = -(height / 2.0 - hole_radius * 2.2)

modifier = body.modifiers.new(name="TopHole", type='BOOLEAN')
modifier.operation = 'DIFFERENCE'
modifier.object = hole
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(hole, do_unlink=True)

print("Created dogtag blank")
'''


def cuff_blank_blender_script(length_mm: float, width_mm: float, thickness_mm: float) -> str:
    return f'''"""Create a flat cuff bracelet blank in Blender."""

import bpy

length = {length_mm * MM_TO_M:.6f}
width = {width_mm * MM_TO_M:.6f}
thickness = {thickness_mm * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cube_add(size=1.0)
blank = bpy.context.active_object
blank.name = "CuffBlank"
blank.scale = (length / 2.0, width / 2.0, thickness / 2.0)

print("Created cuff bracelet blank")
'''


def gallery_ring_blender_script(outer_diameter_mm: float, inner_diameter_mm: float, gallery_width_mm: float, gallery_height_mm: float, shank_thickness_mm: float) -> str:
    return f'''"""Create a gallery ring blank in Blender."""

import bpy

outer_radius = {outer_diameter_mm / 2.0 * MM_TO_M:.6f}
inner_radius = {inner_diameter_mm / 2.0 * MM_TO_M:.6f}
gallery_width = {gallery_width_mm * MM_TO_M:.6f}
gallery_height = {gallery_height_mm * MM_TO_M:.6f}
shank_thickness = {shank_thickness_mm * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=outer_radius, depth=shank_thickness)
ring = bpy.context.active_object
ring.name = "GalleryRingOuter"

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=inner_radius, depth=shank_thickness * 1.2)
inner = bpy.context.active_object
inner.name = "GalleryRingInner"

cut = ring.modifiers.new(name="InnerCut", type='BOOLEAN')
cut.operation = 'DIFFERENCE'
cut.object = inner
bpy.context.view_layer.objects.active = ring
bpy.ops.object.modifier_apply(modifier=cut.name)
bpy.data.objects.remove(inner, do_unlink=True)

bpy.ops.mesh.primitive_cube_add(size=1.0)
gallery = bpy.context.active_object
gallery.name = "GalleryTop"
gallery.scale = (gallery_width / 2.0, shank_thickness / 2.0, gallery_height / 2.0)
gallery.location.y = -outer_radius
gallery.location.z = gallery_height / 2.0

print("Created gallery ring blank")
'''


def basket_pendant_blender_script(outer_diameter_mm: float, seat_diameter_mm: float, thickness_mm: float, bail_hole_mm: float) -> str:
    return f'''"""Create a basket pendant blank in Blender."""

import bpy

outer_radius = {outer_diameter_mm / 2.0 * MM_TO_M:.6f}
seat_radius = {seat_diameter_mm / 2.0 * MM_TO_M:.6f}
thickness = {thickness_mm * MM_TO_M:.6f}
bail_radius = {bail_hole_mm / 2.0 * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=outer_radius, depth=thickness)
pendant = bpy.context.active_object
pendant.name = "BasketPendant"

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=seat_radius, depth=thickness * 0.45)
seat = bpy.context.active_object
seat.name = "BasketSeat"
seat.location.z = thickness * 0.2

seat_cut = pendant.modifiers.new(name="SeatCut", type='BOOLEAN')
seat_cut.operation = 'DIFFERENCE'
seat_cut.object = seat
bpy.context.view_layer.objects.active = pendant
bpy.ops.object.modifier_apply(modifier=seat_cut.name)
bpy.data.objects.remove(seat, do_unlink=True)

bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=bail_radius, depth=thickness * 1.5)
bail = bpy.context.active_object
bail.name = "PendantBailHole"
bail.location.y = -(outer_radius + bail_radius * 0.2)

bail_cut = pendant.modifiers.new(name="BailCut", type='BOOLEAN')
bail_cut.operation = 'DIFFERENCE'
bail_cut.object = bail
bpy.context.view_layer.objects.active = pendant
bpy.ops.object.modifier_apply(modifier=bail_cut.name)
bpy.data.objects.remove(bail, do_unlink=True)

print("Created basket pendant blank")
'''


def pierced_bezel_ring_blender_script(outer_diameter_mm: float, inner_diameter_mm: float, bezel_diameter_mm: float, shank_thickness_mm: float) -> str:
    return f'''"""Create a pierced bezel ring blank in Blender."""

import bpy

outer_radius = {outer_diameter_mm / 2.0 * MM_TO_M:.6f}
inner_radius = {inner_diameter_mm / 2.0 * MM_TO_M:.6f}
bezel_radius = {bezel_diameter_mm / 2.0 * MM_TO_M:.6f}
thickness = {shank_thickness_mm * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=outer_radius, depth=thickness)
ring = bpy.context.active_object
ring.name = "PiercedBezelRingOuter"

bpy.ops.mesh.primitive_cylinder_add(vertices=180, radius=inner_radius, depth=thickness * 1.2)
inner = bpy.context.active_object
inner.name = "PiercedBezelRingInner"

cut = ring.modifiers.new(name="InnerCut", type='BOOLEAN')
cut.operation = 'DIFFERENCE'
cut.object = inner
bpy.context.view_layer.objects.active = ring
bpy.ops.object.modifier_apply(modifier=cut.name)
bpy.data.objects.remove(inner, do_unlink=True)

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=bezel_radius, depth=thickness)
bezel = bpy.context.active_object
bezel.name = "PiercedBezelTop"
bezel.location.y = -outer_radius
bezel.location.z = thickness / 2.0

print("Created pierced bezel ring blank")
'''


def hoop_earring_blender_script(outer_diameter_mm: float, wire_diameter_mm: float, pair_spacing_mm: float) -> str:
    return f'''"""Create a hoop earring pair blank in Blender."""

import bpy

outer_d = {outer_diameter_mm * MM_TO_M:.6f}
wire_d = {wire_diameter_mm * MM_TO_M:.6f}
spacing = {pair_spacing_mm * MM_TO_M:.6f}

for direction in (-1, 1):
    bpy.ops.mesh.primitive_torus_add(major_radius=outer_d / 2.0, minor_radius=wire_d / 2.0, major_segments=96, minor_segments=24)
    hoop = bpy.context.active_object
    hoop.name = f"HoopEarring_{{'L' if direction < 0 else 'R'}}"
    hoop.location.x = direction * spacing / 2.0

print("Created hoop earring blank pair")
'''


def toggle_bracelet_blank_blender_script(length_mm: float, width_mm: float, thickness_mm: float, ring_outer_mm: float, ring_inner_mm: float) -> str:
    return f'''"""Create a toggle bracelet component blank set in Blender."""

import bpy

length = {length_mm * MM_TO_M:.6f}
width = {width_mm * MM_TO_M:.6f}
thickness = {thickness_mm * MM_TO_M:.6f}
ring_outer = {ring_outer_mm / 2.0 * MM_TO_M:.6f}
ring_inner = {ring_inner_mm / 2.0 * MM_TO_M:.6f}

bpy.ops.mesh.primitive_cube_add(size=1.0)
bar = bpy.context.active_object
bar.name = "ToggleBar"
bar.scale = (length / 2.0, width / 2.0, thickness / 2.0)

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=ring_outer, depth=thickness)
ring = bpy.context.active_object
ring.name = "ToggleRingOuter"
ring.location.x = length * 0.95

bpy.ops.mesh.primitive_cylinder_add(vertices=144, radius=ring_inner, depth=thickness * 1.2)
inner = bpy.context.active_object
inner.name = "ToggleRingInner"
inner.location.x = length * 0.95

cut = ring.modifiers.new(name="InnerCut", type='BOOLEAN')
cut.operation = 'DIFFERENCE'
cut.object = inner
bpy.context.view_layer.objects.active = ring
bpy.ops.object.modifier_apply(modifier=cut.name)
bpy.data.objects.remove(inner, do_unlink=True)

print("Created toggle bracelet blank set")
'''


def template_index_html(template_names: list[str]) -> str:
    categories = {
        "Rings": ["ring_band_blank", "signet_blank", "gallery_ring", "pierced_bezel_ring"],
        "Bezels": ["bezel_pocket", "round_bezel_pocket", "oval_bezel_pocket"],
        "Pendants & Tags": ["pendant_blank", "basket_pendant", "coin_blank", "dogtag_blank"],
        "Bracelets": ["bangle_blank", "cuff_blank", "toggle_bracelet_blank"],
        "Earrings": ["stud_earring_blank", "hoop_earring"],
        "Molds & Utility": ["tray_mold"],
    }
    purposes = {
        "ring_band_blank": "Baseline ring shank blank for engraved or stone-set ring work.",
        "signet_blank": "Flat-faced signet starter for crest, monogram, or relief carving.",
        "gallery_ring": "Ring blank with elevated gallery top for settings or decorative seats.",
        "pierced_bezel_ring": "Ring blank with pierced bezel area for openwork and lighter settings.",
        "bezel_pocket": "Rectangular bezel seat pocket for cabochons or faceted stones.",
        "round_bezel_pocket": "Round bezel seat for coin-cut or circular stones.",
        "oval_bezel_pocket": "Oval bezel seat for elongated stones and navette-inspired layouts.",
        "pendant_blank": "General pendant blank with bail hole for medallion-style pieces.",
        "basket_pendant": "Pendant with central basket seat and bail hole for stone-focused designs.",
        "coin_blank": "Coin or medallion blank for engraving and commemorative motifs.",
        "dogtag_blank": "Dog-tag profile blank with top hole for chains and ID-style pendants.",
        "bangle_blank": "Closed circular bracelet blank sized for bangle workflows.",
        "cuff_blank": "Flat cuff strip blank intended for forming and wrist curvature.",
        "toggle_bracelet_blank": "Toggle bar and ring starter geometry for clasp component workflows.",
        "stud_earring_blank": "Paired stud blanks for mirrored earring production.",
        "hoop_earring": "Paired hoop earring profiles with configurable wire thickness.",
        "tray_mold": "Utility tray mold blank for small castable or press-form parts.",
    }

    category_blocks = []
    seen = set()
    for category_name, names in categories.items():
        cards = []
        for name in names:
            if name not in template_names:
                continue
            seen.add(name)
            svg_name = f"{name}.svg"
            py_name = f"{name}.py"
            title = name.replace("_", " ").title()
            purpose = purposes.get(name, "Template family for parametric jewelry blank generation.")
            cards.append(
                f'''<article class="card"><h3>{title}</h3><img src="{svg_name}" alt="{title} preview"><p class="purpose">{purpose}</p><p><a href="{svg_name}">{svg_name}</a><br><a href="{py_name}">{py_name}</a></p></article>'''
            )
        if cards:
            block_cards = "\n        ".join(cards)
            category_blocks.append(
                f'''<section class="category"><h2>{category_name}</h2><div class="grid">{block_cards}</div></section>'''
            )

    uncategorized = [name for name in template_names if name not in seen]
    if uncategorized:
        cards = []
        for name in uncategorized:
            svg_name = f"{name}.svg"
            py_name = f"{name}.py"
            title = name.replace("_", " ").title()
            purpose = purposes.get(name, "Template family for parametric jewelry blank generation.")
            cards.append(
                f'''<article class="card"><h3>{title}</h3><img src="{svg_name}" alt="{title} preview"><p class="purpose">{purpose}</p><p><a href="{svg_name}">{svg_name}</a><br><a href="{py_name}">{py_name}</a></p></article>'''
            )
        category_blocks.append(
            f'''<section class="category"><h2>Other</h2><div class="grid">{' '.join(cards)}</div></section>'''
        )

    body = "\n    ".join(category_blocks)
    return f'''<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Fabex Workshop Template Preview</title>
    <style>
    :root {{ color-scheme: light; --ink:#14213d; --sand:#f6f2e8; --accent:#b5653b; --line:#d6c7a7; --wash:#fffaf0; }}
    body {{ margin:0; font-family:Georgia, "Palatino Linotype", serif; background:linear-gradient(180deg,#f8f3e7,#efe3ca); color:var(--ink); }}
    header {{ padding:24px 32px 6px; }}
    h1 {{ margin:0 0 8px; font-size:32px; }}
    .intro {{ margin:0; max-width:70ch; }}
    main {{ display:grid; gap:20px; padding:8px 32px 32px; }}
    .category {{ background:rgba(255,255,255,0.5); border:1px solid var(--line); border-radius:16px; padding:14px; }}
    .category h2 {{ margin:0 0 10px; font-size:22px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:14px; }}
    .card {{ background:var(--wash); border:1px solid var(--line); border-radius:14px; padding:12px; box-shadow:0 8px 20px rgba(20,33,61,0.06); }}
    .card h3 {{ margin:0 0 8px; font-size:18px; }}
    img {{ width:100%; height:200px; object-fit:contain; background:var(--sand); border-radius:10px; border:1px solid var(--line); }}
    .purpose {{ font-size:14px; line-height:1.35; min-height:54px; }}
    a {{ color:var(--accent); text-decoration:none; }}
    </style>
</head>
<body>
    <header>
    <h1>Fabex Workshop Templates</h1>
    <p class="intro">Preview grouped template families, then open each SVG outline or paired Blender generator script.</p>
    </header>
    <main>
    {body}
    </main>
</body>
</html>
'''


def build_templates(output_dir: Path) -> list[Path]:
    template_dir = ensure_dir(output_dir / "templates")
    written = []

    resources = {
        "ring_band_blank.svg": ring_band_svg(outer_diameter_mm=24.0, inner_diameter_mm=18.2),
        "ring_band_blank.py": ring_band_blender_script(outer_diameter_mm=24.0, inner_diameter_mm=18.2, thickness_mm=6.0),
        "tray_mold.svg": tray_mold_svg(width_mm=100.0, height_mm=70.0, corner_radius_mm=10.0, pocket_margin_mm=7.0),
        "tray_mold.py": tray_mold_blender_script(width_mm=100.0, height_mm=70.0, depth_mm=10.0, corner_radius_mm=10.0, pocket_margin_mm=7.0),
        "signet_blank.svg": signet_blank_svg(face_width_mm=16.0, face_height_mm=13.0, inner_diameter_mm=19.0),
        "signet_blank.py": signet_blank_blender_script(face_width_mm=16.0, face_height_mm=13.0, inner_diameter_mm=19.0, shank_depth_mm=5.5),
        "bezel_pocket.svg": bezel_pocket_svg(outer_width_mm=20.0, outer_height_mm=16.0, stone_width_mm=16.0, stone_height_mm=12.0),
        "bezel_pocket.py": bezel_pocket_blender_script(outer_width_mm=20.0, outer_height_mm=16.0, depth_mm=5.0, stone_width_mm=16.0, stone_height_mm=12.0),
        "pendant_blank.svg": pendant_blank_svg(width_mm=28.0, height_mm=36.0, bail_hole_mm=3.0),
        "pendant_blank.py": pendant_blank_blender_script(width_mm=28.0, height_mm=36.0, thickness_mm=3.0, bail_hole_mm=3.0),
        "oval_bezel_pocket.svg": oval_bezel_pocket_svg(outer_width_mm=22.0, outer_height_mm=28.0, stone_width_mm=16.0, stone_height_mm=22.0),
        "oval_bezel_pocket.py": oval_bezel_pocket_blender_script(outer_width_mm=22.0, outer_height_mm=28.0, depth_mm=5.0, stone_width_mm=16.0, stone_height_mm=22.0),
        "stud_earring_blank.svg": stud_earring_blank_svg(diameter_mm=10.0, post_hole_mm=0.9),
        "stud_earring_blank.py": stud_earring_blank_blender_script(diameter_mm=10.0, thickness_mm=2.0, pair_spacing_mm=18.0),
        "coin_blank.svg": coin_blank_svg(diameter_mm=32.0),
        "coin_blank.py": coin_blank_blender_script(diameter_mm=32.0, thickness_mm=3.0),
        "round_bezel_pocket.svg": round_bezel_pocket_svg(outer_diameter_mm=18.0, stone_diameter_mm=14.0),
        "round_bezel_pocket.py": round_bezel_pocket_blender_script(outer_diameter_mm=18.0, depth_mm=4.5, stone_diameter_mm=14.0),
        "bangle_blank.svg": bangle_blank_svg(outer_diameter_mm=78.0, inner_diameter_mm=64.0),
        "bangle_blank.py": bangle_blank_blender_script(outer_diameter_mm=78.0, inner_diameter_mm=64.0, width_mm=18.0),
        "dogtag_blank.svg": dogtag_blank_svg(width_mm=28.0, height_mm=50.0, corner_radius_mm=6.0, hole_diameter_mm=3.5),
        "dogtag_blank.py": dogtag_blank_blender_script(width_mm=28.0, height_mm=50.0, thickness_mm=2.0, hole_diameter_mm=3.5),
        "cuff_blank.svg": cuff_blank_svg(length_mm=160.0, width_mm=28.0, corner_radius_mm=5.0),
        "cuff_blank.py": cuff_blank_blender_script(length_mm=160.0, width_mm=28.0, thickness_mm=2.0),
        "gallery_ring.svg": gallery_ring_svg(outer_diameter_mm=24.0, inner_diameter_mm=18.2, gallery_width_mm=14.0, gallery_height_mm=8.0),
        "gallery_ring.py": gallery_ring_blender_script(outer_diameter_mm=24.0, inner_diameter_mm=18.2, gallery_width_mm=14.0, gallery_height_mm=8.0, shank_thickness_mm=2.4),
        "basket_pendant.svg": basket_pendant_svg(outer_diameter_mm=24.0, seat_diameter_mm=16.0, bail_hole_mm=2.8),
        "basket_pendant.py": basket_pendant_blender_script(outer_diameter_mm=24.0, seat_diameter_mm=16.0, thickness_mm=2.6, bail_hole_mm=2.8),
        "pierced_bezel_ring.svg": pierced_bezel_ring_svg(outer_diameter_mm=24.0, inner_diameter_mm=18.2, bezel_diameter_mm=10.0, pierce_count=10),
        "pierced_bezel_ring.py": pierced_bezel_ring_blender_script(outer_diameter_mm=24.0, inner_diameter_mm=18.2, bezel_diameter_mm=10.0, shank_thickness_mm=2.4),
        "hoop_earring.svg": hoop_earring_svg(outer_diameter_mm=22.0, wire_diameter_mm=2.0, pair_spacing_mm=30.0),
        "hoop_earring.py": hoop_earring_blender_script(outer_diameter_mm=22.0, wire_diameter_mm=2.0, pair_spacing_mm=30.0),
        "toggle_bracelet_blank.svg": toggle_bracelet_blank_svg(length_mm=24.0, width_mm=4.0, ring_outer_mm=14.0, ring_inner_mm=9.0),
        "toggle_bracelet_blank.py": toggle_bracelet_blank_blender_script(length_mm=24.0, width_mm=4.0, thickness_mm=2.0, ring_outer_mm=14.0, ring_inner_mm=9.0),
    }
    for name, content in resources.items():
        path = template_dir / name
        write_text(path, content)
        written.append(path)

    template_names = sorted({path.stem for path in template_dir.glob("*.svg")})
    index_path = template_dir / "index.html"
    write_text(index_path, template_index_html(template_names))
    written.append(index_path)

    manifest_path = template_dir / "template_manifest.json"
    manifest = {
        "ring_band": {"outer_diameter_mm": 24.0, "inner_diameter_mm": 18.2, "thickness_mm": 6.0, "note": "Starter ring blank near US size 8."},
        "tray_mold": {"width_mm": 100.0, "height_mm": 70.0, "depth_mm": 10.0, "corner_radius_mm": 10.0, "pocket_margin_mm": 7.0},
        "signet_blank": {"face_width_mm": 16.0, "face_height_mm": 13.0, "inner_diameter_mm": 19.0, "shank_depth_mm": 5.5},
        "bezel_pocket": {"outer_width_mm": 20.0, "outer_height_mm": 16.0, "stone_width_mm": 16.0, "stone_height_mm": 12.0, "depth_mm": 5.0},
        "pendant_blank": {"width_mm": 28.0, "height_mm": 36.0, "thickness_mm": 3.0, "bail_hole_mm": 3.0},
        "oval_bezel_pocket": {"outer_width_mm": 22.0, "outer_height_mm": 28.0, "stone_width_mm": 16.0, "stone_height_mm": 22.0, "depth_mm": 5.0},
        "stud_earring_blank": {"diameter_mm": 10.0, "thickness_mm": 2.0, "pair_spacing_mm": 18.0, "post_hole_mm": 0.9},
        "coin_blank": {"diameter_mm": 32.0, "thickness_mm": 3.0},
        "round_bezel_pocket": {"outer_diameter_mm": 18.0, "stone_diameter_mm": 14.0, "depth_mm": 4.5},
        "bangle_blank": {"outer_diameter_mm": 78.0, "inner_diameter_mm": 64.0, "width_mm": 18.0},
        "dogtag_blank": {"width_mm": 28.0, "height_mm": 50.0, "thickness_mm": 2.0, "corner_radius_mm": 6.0, "hole_diameter_mm": 3.5},
        "cuff_blank": {"length_mm": 160.0, "width_mm": 28.0, "thickness_mm": 2.0, "corner_radius_mm": 5.0},
        "gallery_ring": {"outer_diameter_mm": 24.0, "inner_diameter_mm": 18.2, "gallery_width_mm": 14.0, "gallery_height_mm": 8.0, "shank_thickness_mm": 2.4},
        "basket_pendant": {"outer_diameter_mm": 24.0, "seat_diameter_mm": 16.0, "thickness_mm": 2.6, "bail_hole_mm": 2.8},
        "pierced_bezel_ring": {"outer_diameter_mm": 24.0, "inner_diameter_mm": 18.2, "bezel_diameter_mm": 10.0, "shank_thickness_mm": 2.4, "pierce_count": 10},
        "hoop_earring": {"outer_diameter_mm": 22.0, "wire_diameter_mm": 2.0, "pair_spacing_mm": 30.0},
        "toggle_bracelet_blank": {"length_mm": 24.0, "width_mm": 4.0, "thickness_mm": 2.0, "ring_outer_mm": 14.0, "ring_inner_mm": 9.0},
    }
    write_text(manifest_path, json.dumps(manifest, indent=2))
    written.append(manifest_path)
    return written


def gcode_header(spindle_rpm: int, material_name: str) -> list[str]:
    return [
        "(Generated by fabex_workshop.toolkit)",
        f"(Material: {material_name})",
        "G90",
        "G21",
        "G17",
        f"M3 S{spindle_rpm}",
    ]


def gcode_footer(safe_z_mm: float) -> list[str]:
    return [
        f"G0 Z{safe_z_mm:.3f}",
        "M5",
        "G0 X0.000 Y0.000",
        "M30",
    ]


def material_preset(name: str) -> MaterialPreset:
    return DEFAULT_MATERIALS[name]


def rectangular_perimeter(min_x: float, max_x: float, min_y: float, max_y: float) -> list[tuple[float, float]]:
    return [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y), (min_x, min_y)]


def polyline(lines: list[str], points: Iterable[tuple[float, float]], feed: float, z_mm: float | None = None) -> None:
    iterator = iter(points)
    first_x, first_y = next(iterator)
    if z_mm is None:
        lines.append(f"G1 X{first_x:.3f} Y{first_y:.3f} F{feed:.3f}")
    else:
        lines.append(f"G1 X{first_x:.3f} Y{first_y:.3f} Z{z_mm:.3f} F{feed:.3f}")
    for x, y in iterator:
        if z_mm is None:
            lines.append(f"G1 X{x:.3f} Y{y:.3f} F{feed:.3f}")
        else:
            lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z_mm:.3f} F{feed:.3f}")


def ramp_to_depth(lines: list[str], safe_z_mm: float, start_x: float, start_y: float, target_z: float, ramp_length_mm: float, plunge_rate_mm_min: float) -> None:
    ramp_x = start_x - max(ramp_length_mm, 0.5)
    lines.append(f"G0 Z{safe_z_mm:.3f}")
    lines.append(f"G0 X{ramp_x:.3f} Y{start_y:.3f}")
    lines.append(f"G1 X{start_x:.3f} Y{start_y:.3f} Z{target_z:.3f} F{plunge_rate_mm_min:.3f}")


def rectangle_pocket_gcode(job: PocketJob) -> list[str]:
    material = material_preset(job.material_name)
    lines = gcode_header(job.spindle_rpm, job.material_name)
    tool_radius = job.tool_diameter_mm / 2.0
    min_x = -job.width_mm / 2.0 + tool_radius + job.finish_allowance_mm
    max_x = job.width_mm / 2.0 - tool_radius - job.finish_allowance_mm
    min_y = -job.height_mm / 2.0 + tool_radius + job.finish_allowance_mm
    max_y = job.height_mm / 2.0 - tool_radius - job.finish_allowance_mm
    y_positions = []
    current_y = min_y
    while current_y <= max_y + 1e-6:
        y_positions.append(round(current_y, 6))
        current_y += max(job.stepover_mm, 0.1)

    current_depth = 0.0
    direction = 1
    while current_depth > -job.depth_mm + 1e-6:
        current_depth = max(current_depth - job.stepdown_mm, -job.depth_mm)
        ramp_to_depth(lines, job.safe_z_mm, min_x, min_y, current_depth, job.ramp_length_mm, job.plunge_rate_mm_min)
        for y in y_positions:
            x_start, x_end = (min_x, max_x) if direction > 0 else (max_x, min_x)
            lines.append(f"G1 X{x_start:.3f} Y{y:.3f} F{job.feed_rate_mm_min:.3f}")
            lines.append(f"G1 X{x_end:.3f} Y{y:.3f} F{job.feed_rate_mm_min:.3f}")
            direction *= -1

    if job.finish_pass:
        lines.append(f"G0 Z{job.safe_z_mm:.3f}")
        lines.append(f"G0 X{-job.width_mm / 2.0 + tool_radius:.3f} Y{-job.height_mm / 2.0 + tool_radius:.3f}")
        lines.append(f"G1 Z{-job.depth_mm:.3f} F{job.plunge_rate_mm_min:.3f}")
        polyline(
            lines,
            rectangular_perimeter(
                -job.width_mm / 2.0 + tool_radius,
                job.width_mm / 2.0 - tool_radius,
                -job.height_mm / 2.0 + tool_radius,
                job.height_mm / 2.0 - tool_radius,
            ),
            material.finish_feed_mm_min,
        )

    lines.extend(gcode_footer(job.safe_z_mm))
    return lines


def circular_pocket_gcode(job: CircularPocketJob) -> list[str]:
    material = material_preset(job.material_name)
    lines = gcode_header(job.spindle_rpm, job.material_name)
    rough_radius = (job.diameter_mm - job.tool_diameter_mm) / 2.0 - job.finish_allowance_mm
    finish_radius = (job.diameter_mm - job.tool_diameter_mm) / 2.0
    radii = []
    radius = rough_radius
    while radius > 0.0:
        radii.append(radius)
        radius -= max(job.stepover_mm, 0.1)
    if not radii or radii[-1] != 0.0:
        radii.append(0.0)

    current_depth = 0.0
    while current_depth > -job.depth_mm + 1e-6:
        current_depth = max(current_depth - job.stepdown_mm, -job.depth_mm)
        ramp_to_depth(lines, job.safe_z_mm, rough_radius, 0.0, current_depth, job.ramp_length_mm, job.plunge_rate_mm_min)
        for radius in radii:
            if radius <= 0.001:
                continue
            polyline(lines, circle_points(radius, job.segments), job.feed_rate_mm_min)

    if job.finish_pass:
        lines.append(f"G0 Z{job.safe_z_mm:.3f}")
        lines.append(f"G0 X{finish_radius:.3f} Y0.000")
        lines.append(f"G1 Z{-job.depth_mm:.3f} F{job.plunge_rate_mm_min:.3f}")
        polyline(lines, circle_points(finish_radius, job.segments), material.finish_feed_mm_min)

    lines.extend(gcode_footer(job.safe_z_mm))
    return lines


def tab_depth_for_angle(base_depth: float, angle_deg: float, tabs: int, tab_width_deg: float, tab_height_mm: float) -> float:
    if tabs <= 0:
        return base_depth
    spacing = 360.0 / tabs
    for tab_index in range(tabs):
        center = tab_index * spacing
        delta = abs((angle_deg - center + 180.0) % 360.0 - 180.0)
        if delta <= tab_width_deg / 2.0:
            return max(base_depth + tab_height_mm, base_depth)
    return base_depth


def ring_band_profile_gcode(job: RingBandJob) -> list[str]:
    material = material_preset(job.material_name)
    lines = gcode_header(job.spindle_rpm, job.material_name)
    rough_outer = (job.outer_diameter_mm - job.tool_diameter_mm) / 2.0 - job.finish_allowance_mm
    finish_outer = (job.outer_diameter_mm - job.tool_diameter_mm) / 2.0
    rough_inner = (job.inner_diameter_mm + job.tool_diameter_mm) / 2.0 + job.finish_allowance_mm
    finish_inner = (job.inner_diameter_mm + job.tool_diameter_mm) / 2.0
    current_depth = 0.0
    while current_depth > -job.depth_mm + 1e-6:
        current_depth = max(current_depth - job.stepdown_mm, -job.depth_mm)
        ramp_to_depth(lines, job.safe_z_mm, rough_outer, 0.0, current_depth, job.ramp_length_mm, job.plunge_rate_mm_min)
        polyline(lines, circle_points(rough_outer, job.segments), job.feed_rate_mm_min)
        lines.append(f"G0 Z{job.safe_z_mm:.3f}")
        ramp_to_depth(lines, job.safe_z_mm, rough_inner, 0.0, current_depth, job.ramp_length_mm, job.plunge_rate_mm_min)
        polyline(lines, reversed(circle_points(rough_inner, job.segments)), job.feed_rate_mm_min)

    lines.append(f"G0 Z{job.safe_z_mm:.3f}")
    lines.append(f"G0 X{finish_outer:.3f} Y0.000")
    lines.append(f"G1 Z{-job.depth_mm:.3f} F{job.plunge_rate_mm_min:.3f}")
    for index in range(job.segments + 1):
        angle = (360.0 * index) / job.segments
        angle_rad = math.radians(angle)
        target_z = tab_depth_for_angle(-job.depth_mm, angle, job.tabs, job.tab_width_deg, job.tab_height_mm)
        x = math.cos(angle_rad) * finish_outer
        y = math.sin(angle_rad) * finish_outer
        lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{target_z:.3f} F{material.finish_feed_mm_min:.3f}")

    lines.append(f"G0 Z{job.safe_z_mm:.3f}")
    lines.append(f"G0 X{finish_inner:.3f} Y0.000")
    lines.append(f"G1 Z{-job.depth_mm:.3f} F{job.plunge_rate_mm_min:.3f}")
    polyline(lines, reversed(circle_points(finish_inner, job.segments)), material.finish_feed_mm_min)
    lines.extend(gcode_footer(job.safe_z_mm))
    return lines


def build_gcode(output_dir: Path) -> list[Path]:
    gcode_dir = ensure_dir(output_dir / "gcode")
    written = []

    rect = PocketJob(
        width_mm=60.0,
        height_mm=40.0,
        depth_mm=6.0,
        tool_diameter_mm=6.0,
        stepover_mm=2.4,
        stepdown_mm=1.5,
        feed_rate_mm_min=900.0,
        plunge_rate_mm_min=250.0,
        spindle_rpm=10000,
        material_name="hardwood",
    )
    rect_path = gcode_dir / "rectangular_pocket.nc"
    write_text(rect_path, "\n".join(rectangle_pocket_gcode(rect)) + "\n")
    written.append(rect_path)

    circle = CircularPocketJob(
        diameter_mm=30.0,
        depth_mm=4.0,
        tool_diameter_mm=3.0,
        stepover_mm=1.0,
        stepdown_mm=0.8,
        feed_rate_mm_min=700.0,
        plunge_rate_mm_min=180.0,
        spindle_rpm=12000,
        material_name="wax",
    )
    circle_path = gcode_dir / "circular_pocket.nc"
    write_text(circle_path, "\n".join(circular_pocket_gcode(circle)) + "\n")
    written.append(circle_path)

    ring = RingBandJob(
        outer_diameter_mm=30.0,
        inner_diameter_mm=20.0,
        stock_thickness_mm=6.0,
        tool_diameter_mm=2.0,
        depth_mm=6.0,
        stepdown_mm=1.0,
        feed_rate_mm_min=500.0,
        plunge_rate_mm_min=150.0,
        spindle_rpm=12000,
        material_name="brass",
    )
    ring_path = gcode_dir / "ring_band_profile.nc"
    write_text(ring_path, "\n".join(ring_band_profile_gcode(ring)) + "\n")
    written.append(ring_path)

    manifest_path = gcode_dir / "gcode_manifest.json"
    manifest = {
        "materials": {name: asdict(preset) for name, preset in DEFAULT_MATERIALS.items()},
        "rectangular_pocket": asdict(rect),
        "circular_pocket": asdict(circle),
        "ring_band_profile": asdict(ring),
    }
    write_text(manifest_path, json.dumps(manifest, indent=2))
    written.append(manifest_path)
    return written


def bootstrap_all(output_dir: Path) -> list[Path]:
    written = []
    written.extend(build_presets(output_dir))
    written.extend(build_templates(output_dir))
    written.extend(build_gcode(output_dir))
    written.extend(build_full_batch_profiles(output_dir))
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate reusable Fabex workshop resources")
    parser.add_argument(
        "command",
        choices=["presets", "templates", "gcode", "full-batch", "bootstrap-all", "install-presets", "bootstrap-and-install"],
        help="What to generate",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "output"),
        help="Directory to write generated resources",
    )
    parser.add_argument(
        "--fabex-root",
        default=str(default_fabex_preset_root()),
        help="Fabex preset root directory for installation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    fabex_root = Path(args.fabex_root).resolve()
    if args.command == "presets":
        written = build_presets(output_dir)
    elif args.command == "templates":
        written = build_templates(output_dir)
    elif args.command == "gcode":
        written = build_gcode(output_dir)
    elif args.command == "full-batch":
        written = build_full_batch_profiles(output_dir)
    elif args.command == "install-presets":
        build_presets(output_dir)
        written = install_presets(output_dir, fabex_root)
    elif args.command == "bootstrap-and-install":
        written = bootstrap_all(output_dir)
        written.extend(install_presets(output_dir, fabex_root))
    else:
        written = bootstrap_all(output_dir)

    print(f"Generated {len(written)} files in {output_dir}")
    for path in written:
        print(f" - {path}")


if __name__ == "__main__":
    main()