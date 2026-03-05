#!/usr/bin/env python3
"""
Generate LightBurn .lbrn2 files from test pattern images

Wraps MOPA_Laser_Toolkit to create ready-to-load LightBurn projects
for the manufacturing test suite.
"""

import os
import sys
import json
import subprocess
from pathlib import Path


class LightBurnTestGenerator:
    """Generate LightBurn files for test patterns"""

    def __init__(self):
        self.mopa_toolkit_dir = Path("F:/Documents/CODE/MOPA_Laser_Toolkit")
        self.test_images_dir = Path("F:/Documents/CODE/Blender-MCP/test_images")
        self.output_dir = Path("F:/Documents/Lightburn/generated_tests")

        # Ensure directories exist
        self.test_images_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_from_test_prompts(self):
        """Generate LightBurn files for all test patterns"""

        print("\n" + "="*70)
        print("  LIGHTBURN TEST FILE GENERATOR")
        print("="*70)

        prompts_file = Path("test_prompts/manufacturing_test_prompts.json")

        if not prompts_file.exists():
            print(f"\n❌ Error: {prompts_file} not found")
            print("   Run: python generate_test_prompts.py first")
            return

        with open(prompts_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"\n📋 Loaded {data['metadata']['total_tests']} test patterns")

        # Instructions for 2D laser tests (need images first)
        print("\n🔥 2D Laser Tests:")
        print("   ⚠️  Generate images in Adobe Firefly first, then run:")
        print("   python generate_lightburn_tests.py --process-images\n")

        for test in data['test_patterns']['2d_laser']:
            print(f"   • {test['name']}: {test['difficulty']}")
            self._show_quick_method(test)

        # 2.5D Relief (use existing image_to_gcode workflow)
        print("\n🏔️ 2.5D Relief Tests:")
        print("   Use image_to_relief.py workflow (outputs G-code, not LightBurn)\n")

        # 3D Rotary (also G-code workflow)
        print("\n🎡 3D Rotary Tests:")
        print("   Use image_to_relief.py workflow (outputs G-code for CNC)\n")

    def _show_quick_method(self, test):
        """Show quick import method for each test type"""

        if test['type'] == '2D_laser_engrave_cut':
            print(f"      → LightBurn: File → Import → Select image → Assign layers")

        elif test['type'] == '2D_laser_engrave':
            print(f"      → LightBurn: Import image → Engrave layer → Dithered")

        elif test['type'] == '2D_laser_diffraction':
            print(f"      → MOPA Toolkit: python main.py diffraction ...")

    def generate_calibration_grid(self):
        """Generate Test 1: Geometric calibration in LightBurn format"""

        print("\n🔷 Generating Test 1: Geometric Calibration Grid")
        print("   Creating programmatic LightBurn file...\n")

        output_file = self.output_dir / "test_01_geometric_calibration.lbrn2"

        # Generate basic geometric shapes using LightBurn XML format
        xml = self._create_lightburn_xml()

        # Add shapes
        shapes_layer = self._add_layer(xml, "Shapes", color="#0000FF", speed=1200, power=18)
        cuts_layer = self._add_layer(xml, "Cuts", color="#FF0000", speed=20, power=80)

        # Golden ratio: 1.618
        phi = 1.618
        center_x, center_y = 25, 25  # 50mm square centered at origin

        # Add circles with golden ratio sizing
        for i, radius in enumerate([5, 5*phi, 5*phi*phi]):
            if radius < 22:  # Keep within 50mm square
                self._add_circle(shapes_layer, center_x, center_y, radius)

        # Add squares
        for i, size in enumerate([8, 8*phi, 8*phi*phi]):
            if size < 40:
                offset = size / 2
                self._add_rect(shapes_layer, center_x - offset, center_y - offset, size, size)

        # Add hexagons (approximated with polygons)
        for i, radius in enumerate([7, 7*phi]):
            if radius < 20:
                self._add_hexagon(shapes_layer, center_x, center_y + 15, radius)

        # Outer cut border
        self._add_rect(cuts_layer, 0, 0, 50, 50)

        # Save file
        self._save_lightburn_file(xml, output_file)

        print(f"✅ Created: {output_file}")
        print(f"   Open in LightBurn → Frame → Test on cardstock")
        print(f"   Blue layer = Engrave (1200mm/s, 18%)")
        print(f"   Red layer = Cut (20mm/s, 80%)\n")

    def _create_lightburn_xml(self):
        """Create basic LightBurn XML structure"""
        from xml.etree.ElementTree import Element, SubElement

        root = Element('LightBurnProject', {
            'AppVersion': '1.4.05',
            'FormatVersion': '1',
            'MaterialHeight': '0',
            'MirrorX': 'False',
            'MirrorY': 'False'
        })

        # Add default settings
        SubElement(root, 'Thumbnail', {
            'Source': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        })

        SubElement(root, 'VariableText')
        SubElement(root, 'UIPrefs')
        SubElement(root, 'CutSetting', {'type': 'Cut'})

        return root

    def _add_layer(self, xml_root, name, color="#0000FF", speed=1000, power=20):
        """Add a cut/engrave layer"""
        from xml.etree.ElementTree import SubElement

        cut_setting = SubElement(xml_root, 'CutSetting', {
            'type': 'Cut'
        })

        SubElement(cut_setting, 'index', {'Value': str(len(xml_root.findall('CutSetting')))})
        SubElement(cut_setting, 'name', {'Value': name})
        SubElement(cut_setting, 'priority', {'Value': '0'})
        SubElement(cut_setting, 'Speed', {'Value': str(speed)})
        SubElement(cut_setting, 'Power', {'Value': str(power)})
        SubElement(cut_setting, 'Color', {'Value': color})

        return cut_setting

    def _add_circle(self, parent, x, y, radius):
        """Add circle shape"""
        from xml.etree.ElementTree import SubElement

        shape = SubElement(parent, 'Shape', {
            'Type': 'Ellipse',
            'CutIndex': '0'
        })
        SubElement(shape, 'XForm', {
            'm11': str(radius*2), 'm12': '0',
            'm21': '0', 'm22': str(radius*2),
            'x': str(x), 'y': str(y)
        })

    def _add_rect(self, parent, x, y, width, height):
        """Add rectangle shape"""
        from xml.etree.ElementTree import SubElement

        shape = SubElement(parent, 'Shape', {
            'Type': 'Rect',
            'CutIndex': '1'
        })
        SubElement(shape, 'XForm', {
            'm11': str(width), 'm12': '0',
            'm21': '0', 'm22': str(height),
            'x': str(x + width/2), 'y': str(y + height/2)
        })

    def _add_hexagon(self, parent, x, y, radius):
        """Add hexagon (6-sided polygon)"""
        from xml.etree.ElementTree import SubElement
        import math

        shape = SubElement(parent, 'Shape', {
            'Type': 'Path',
            'CutIndex': '0'
        })

        # Generate hexagon points
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append(f"{px:.3f},{py:.3f}")

        points.append(points[0])  # Close path

        SubElement(shape, 'V', {'vd': ' '.join(points)})

    def _save_lightburn_file(self, xml_root, filepath):
        """Save XML to .lbrn2 file"""
        from xml.etree import ElementTree as ET
        from xml.dom import minidom

        # Pretty print XML
        rough_string = ET.tostring(xml_root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

    def use_mopa_toolkit_for_diffraction(self, image_path):
        """Use MOPA Toolkit for Test 3: Mandala diffraction"""

        print("\n🌈 Generating Test 3: Mandala Holographic (Diffraction)")

        if not Path(image_path).exists():
            print(f"❌ Image not found: {image_path}")
            print("   Generate mandala in Adobe Firefly first")
            return

        output_file = self.output_dir / "test_03_mandala_holographic.lbrn2"

        # Call MOPA Toolkit
        cmd = [
            "python",
            str(self.mopa_toolkit_dir / "main.py"),
            "diffraction",
            "--angle-map", str(image_path),  # Radial pattern
            "--pitch-map", str(image_path),  # Gradient for pitch
            "--output", str(output_file),
            "--color-layers", "8"
        ]

        print(f"Running: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, cwd=self.mopa_toolkit_dir)

        if result.returncode == 0:
            print(f"\n✅ Created: {output_file}")
            print(f"   Open in LightBurn → Preview rainbow effect")
        else:
            print(f"\n❌ Error generating diffraction file")

    def print_manual_import_guide(self):
        """Print guide for manual LightBurn import"""

        print("\n" + "="*70)
        print("  MANUAL LIGHTBURN IMPORT GUIDE")
        print("="*70)

        print("\n📥 Method 1: Direct Image Import (Easiest)")
        print("   1. LightBurn → File → Import → Select your Firefly image")
        print("   2. Click to place image on workspace")
        print("   3. Select image → Right-click → 'Trace Image' for vectors")
        print("   4. Or use as-is for grayscale dithered engraving")
        print("   5. Assign to layer → Set speed/power")
        print("   6. Preview → Frame → Run test")

        print("\n📐 Method 2: SVG Import (Best for geometric)")
        print("   1. Save Firefly image → Open in Illustrator")
        print("   2. Image Trace → Expand → Clean up paths")
        print("   3. Export as SVG")
        print("   4. LightBurn → File → Import SVG")
        print("   5. Assign layers by color:")
        print("      • Blue (#0000FF) = Engrave")
        print("      • Red (#FF0000) = Cut")

        print("\n🎨 Method 3: MOPA Toolkit (Diffraction/Color)")
        print("   For Test 3 (Mandala Holographic):")
        print("   cd F:\\Documents\\CODE\\MOPA_Laser_Toolkit")
        print("   python main.py diffraction \\")
        print("     --angle-map mandala.jpg \\")
        print("     --pitch-map mandala.jpg \\")
        print("     --output mandala_diffraction.lbrn2")

        print("\n💡 Quick Layer Setup:")
        print("   Test 1 (Calibration):")
        print("     - Blue: 1200mm/s, 18% power (engrave)")
        print("     - Red: 20mm/s, 80% power (cut)")
        print("\n   Test 2 (Tree of Life):")
        print("     - Single layer: 900mm/s, 22% power, 80kHz")
        print("     - Grayscale: Dithered, 256 levels")
        print("\n   Test 3 (Mandala):")
        print("     - Use MOPA Toolkit output (pre-configured)")
        print()


def main():
    """Main entry point"""

    generator = LightBurnTestGenerator()

    if len(sys.argv) > 1 and sys.argv[1] == '--generate-grid':
        # Generate programmatic Test 1
        generator.generate_calibration_grid()

    elif len(sys.argv) > 1 and sys.argv[1] == '--diffraction':
        # Generate Test 3 using MOPA Toolkit
        if len(sys.argv) < 3:
            print("Usage: python generate_lightburn_tests.py --diffraction <image_path>")
        else:
            generator.use_mopa_toolkit_for_diffraction(sys.argv[2])

    else:
        # Show overview and manual import guide
        generator.generate_from_test_prompts()
        generator.print_manual_import_guide()

        print("\n🚀 Quick Commands:")
        print("   Generate geometric grid:")
        print("   python generate_lightburn_tests.py --generate-grid")
        print("\n   Generate mandala diffraction (after Firefly):")
        print("   python generate_lightburn_tests.py --diffraction test_images/mandala.jpg")
        print()


if __name__ == "__main__":
    main()
