#!/usr/bin/env python3
"""Analyze generated template SVGs for structural validity and purpose mapping."""

from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT / "output" / "templates"
MANIFEST_PATH = TEMPLATE_DIR / "template_manifest.json"
REPORT_PATH = TEMPLATE_DIR / "template_image_analysis.json"

PURPOSES = {
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

STEM_ALIASES = {
    "ring_band": "ring_band_blank",
}


def parse_viewbox(value: str) -> list[float]:
    numbers = [float(part) for part in value.replace(",", " ").split()]
    if len(numbers) != 4:
        raise ValueError("viewBox must contain four numeric values")
    return numbers


def analyze_one(svg_path: Path) -> dict:
    tree = ET.parse(svg_path)
    root = tree.getroot()
    tag = root.tag.lower()
    if not tag.endswith("svg"):
        raise ValueError("root tag is not <svg>")

    viewbox_raw = root.attrib.get("viewBox", "")
    viewbox = parse_viewbox(viewbox_raw)
    width_ok = viewbox[2] > 0
    height_ok = viewbox[3] > 0

    path_nodes = [node for node in root.iter() if node.tag.lower().endswith("path")]
    path_count = len(path_nodes)
    filled_paths = 0
    for node in path_nodes:
        if node.attrib.get("d", "").strip():
            filled_paths += 1

    return {
        "file": svg_path.name,
        "viewBox": viewbox,
        "width_ok": width_ok,
        "height_ok": height_ok,
        "path_count": path_count,
        "path_data_count": filled_paths,
        "valid": width_ok and height_ok and path_count >= 1 and filled_paths == path_count,
    }


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    stems = sorted(manifest.keys())
    analysis = []

    for stem in stems:
        file_stem = STEM_ALIASES.get(stem, stem)
        svg_path = TEMPLATE_DIR / f"{file_stem}.svg"
        py_path = TEMPLATE_DIR / f"{file_stem}.py"
        if not svg_path.exists() or not py_path.exists():
            analysis.append(
                {
                    "template": stem,
                    "valid": False,
                    "reason": "missing svg or python pair",
                    "svg_exists": svg_path.exists(),
                    "py_exists": py_path.exists(),
                    "purpose": PURPOSES.get(stem, "purpose not documented"),
                }
            )
            continue

        image_report = analyze_one(svg_path)
        analysis.append(
            {
                "template": stem,
                "valid": image_report["valid"],
                "purpose": PURPOSES.get(stem, "purpose not documented"),
                "svg": image_report,
            }
        )

    all_valid = all(item.get("valid", False) for item in analysis)
    report = {
        "template_count": len(analysis),
        "all_valid": all_valid,
        "analysis": analysis,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Analyzed {len(analysis)} template images")
    print(f"All valid: {all_valid}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
