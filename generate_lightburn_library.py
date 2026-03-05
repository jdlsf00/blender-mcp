#!/usr/bin/env python3
"""
Generate LightBurn Material Library (.clb) from MOPA settings

Creates a proper material library with scan settings optimized for:
- Stainless steel coloring
- Diffraction/holographic effects
- Anodized aluminum marking
- Brass engraving

User workflow:
1. Import image in LightBurn
2. Select material from library
3. Run - LightBurn scans natively
"""

import json
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xml.dom import minidom

def create_material_library():
    """Create LightBurn material library from MOPA config"""

    # Load MOPA config
    config_path = Path("F:/Documents/CODE/MOPA_Laser_Toolkit/config/laser_settings.json")
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Create library root
    root = Element('MaterialLibrary')
    SubElement(root, 'FormatVersion').text = '1'
    SubElement(root, 'AppVersion').text = '1.6.00'

    # Create materials
    materials = []

    # 1. STAINLESS STEEL 304 - Color Marking
    mat_ss_color = create_material(
        name="Stainless 304 - Color",
        description="Color marking on polished stainless steel 304",
        thickness=0.5,
        cut_settings=[
            {
                "name": "Gold/Yellow",
                "type": "Scan",
                "power": 18.0,
                "speed": 1200,
                "frequency": 45000,
                "pulse_width": 25,
                "interval": 0.05,
                "passes": 1
            },
            {
                "name": "Blue",
                "type": "Scan",
                "power": 20.0,
                "speed": 1000,
                "frequency": 60000,
                "pulse_width": 35,
                "interval": 0.05,
                "passes": 1
            },
            {
                "name": "Red/Brown",
                "type": "Scan",
                "power": 22.0,
                "speed": 900,
                "frequency": 30000,
                "pulse_width": 45,
                "interval": 0.05,
                "passes": 1
            },
            {
                "name": "Purple",
                "type": "Scan",
                "power": 24.0,
                "speed": 800,
                "frequency": 70000,
                "pulse_width": 50,
                "interval": 0.05,
                "passes": 1
            }
        ]
    )
    materials.append(mat_ss_color)

    # 2. STAINLESS STEEL 304 - Diffraction (Rainbow)
    mat_ss_diff = create_material(
        name="Stainless 304 - Rainbow Diffraction",
        description="Holographic rainbow effect on polished stainless (4-pass, change angle each pass)",
        thickness=0.5,
        cut_settings=[
            {
                "name": "Red Diffraction",
                "type": "Scan",
                "power": 20.0,
                "speed": 1000,
                "frequency": 57000,
                "pulse_width": 6,
                "interval": 0.014,
                "scan_angle": 0,
                "passes": 1
            },
            {
                "name": "Yellow Diffraction",
                "type": "Scan",
                "power": 19.5,
                "speed": 1050,
                "frequency": 57000,
                "pulse_width": 6,
                "interval": 0.012,
                "scan_angle": 45,
                "passes": 1
            },
            {
                "name": "Green Diffraction",
                "type": "Scan",
                "power": 19.0,
                "speed": 1100,
                "frequency": 57000,
                "pulse_width": 6,
                "interval": 0.010,
                "scan_angle": 90,
                "passes": 1
            },
            {
                "name": "Blue Diffraction",
                "type": "Scan",
                "power": 22.0,
                "speed": 900,
                "frequency": 60000,
                "pulse_width": 5,
                "interval": 0.007,
                "scan_angle": 135,
                "passes": 1
            }
        ]
    )
    materials.append(mat_ss_diff)

    # 3. ANODIZED ALUMINUM - Deep Black
    mat_ano_black = create_material(
        name="Anodized Aluminum - Deep Black",
        description="Deep black marking on anodized aluminum",
        thickness=1.0,
        cut_settings=[
            {
                "name": "Black Mark",
                "type": "Scan",
                "power": 35.0,
                "speed": 800,
                "frequency": 25000,
                "pulse_width": 150,
                "interval": 0.05,
                "passes": 1
            }
        ]
    )
    materials.append(mat_ano_black)

    # 4. ANODIZED ALUMINUM - Color Removal
    mat_ano_white = create_material(
        name="Anodized Aluminum - White/Color Removal",
        description="Remove anodizing to expose bright aluminum",
        thickness=1.0,
        cut_settings=[
            {
                "name": "White Mark",
                "type": "Scan",
                "power": 15.0,
                "speed": 2000,
                "frequency": 80000,
                "pulse_width": 15,
                "interval": 0.05,
                "passes": 1
            }
        ]
    )
    materials.append(mat_ano_white)

    # 5. BRASS - Deep Engraving
    mat_brass = create_material(
        name="Brass - Deep Engrave",
        description="Deep engraving on brass sheet",
        thickness=0.5,
        cut_settings=[
            {
                "name": "Deep Mark",
                "type": "Scan",
                "power": 50.0,
                "speed": 500,
                "frequency": 30000,
                "pulse_width": 80,
                "interval": 0.05,
                "passes": 2
            }
        ]
    )
    materials.append(mat_brass)

    # Add all materials to root
    for mat in materials:
        root.append(mat)

    return root

def create_material(name, description, thickness, cut_settings):
    """Create a material element with cut settings"""
    material = Element('Material')
    SubElement(material, 'FormatVersion').text = '1'
    SubElement(material, 'MaterialName').text = name
    SubElement(material, 'Desc').text = description
    SubElement(material, 'Thickness').text = str(thickness)

    cut_library = SubElement(material, 'CutLibrary')

    for idx, setting in enumerate(cut_settings):
        cut_elem = SubElement(cut_library, 'CutSetting', attrib={'type': setting['type']})
        SubElement(cut_elem, 'index', attrib={'Value': str(idx)})
        SubElement(cut_elem, 'name', attrib={'Value': setting['name']})
        SubElement(cut_elem, 'minPower', attrib={'Value': str(setting['power'])})
        SubElement(cut_elem, 'maxPower', attrib={'Value': str(setting['power'])})
        SubElement(cut_elem, 'maxPower2', attrib={'Value': str(setting['power'])})
        SubElement(cut_elem, 'speed', attrib={'Value': str(setting['speed'])})
        SubElement(cut_elem, 'frequency', attrib={'Value': str(setting['frequency'])})
        SubElement(cut_elem, 'QPulseWidth', attrib={'Value': str(setting.get('pulse_width', 60))})
        SubElement(cut_elem, 'interval', attrib={'Value': str(setting.get('interval', 0.05))})
        SubElement(cut_elem, 'ScanAngle', attrib={'Value': str(setting.get('scan_angle', 0))})
        SubElement(cut_elem, 'NumPasses', attrib={'Value': str(setting.get('passes', 1))})
        SubElement(cut_elem, 'zOffset', attrib={'Value': '0'})
        SubElement(cut_elem, 'enableCrossHatch', attrib={'Value': '0'})
        SubElement(cut_elem, 'overscan', attrib={'Value': '0'})
        SubElement(cut_elem, 'priority', attrib={'Value': str(idx)})

    return material

def save_library(root, output_path):
    """Save library with pretty formatting"""
    xml_string = ElementTree.tostring(root, encoding='utf-8')
    dom = minidom.parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent="  ", encoding='utf-8')

    with open(output_path, 'wb') as f:
        f.write(pretty_xml)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  LIGHTBURN MATERIAL LIBRARY GENERATOR")
    print("=" * 70)

    output_path = Path("F:/Documents/Lightburn/MOPA_Materials_Efficient.clb")

    print("\n📚 Creating material library...")
    root = create_material_library()

    print("💾 Saving library...")
    save_library(root, output_path)

    print(f"\n✅ Library created: {output_path}")
    print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")

    print("\n📋 Materials included:")
    print("   1. Stainless 304 - Color (4 colors)")
    print("   2. Stainless 304 - Rainbow Diffraction (4 angles)")
    print("   3. Anodized Aluminum - Deep Black")
    print("   4. Anodized Aluminum - White/Color Removal")
    print("   5. Brass - Deep Engrave")

    print("\n🎯 How to use:")
    print("   1. LightBurn → Window → Library → Import")
    print("   2. Select: MOPA_Materials_Efficient.clb")
    print("   3. Import ANY image (File → Import)")
    print("   4. Assign layer to material preset")
    print("   5. Run - LightBurn scans natively!")

    print("\n💡 Benefits:")
    print("   ✅ Works with ANY image format")
    print("   ✅ No preprocessing needed")
    print("   ✅ Small file sizes")
    print("   ✅ LightBurn's native scanning")
    print("   ✅ All MOPA parameters optimized")
    print()
