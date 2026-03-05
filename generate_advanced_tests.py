#!/usr/bin/env python3
"""
Generate Advanced Manufacturing Test Files

Focuses on the most complex tests:
- Test 3: Mandala Holographic (Diffraction Grating)
- Test 6-7: 4-Axis Rotary G-code

Assumes you have already generated images in Adobe Firefly.
"""

import os
import sys
import subprocess
from pathlib import Path

class AdvancedTestGenerator:
    """Generate advanced test files for MOPA laser and 4-axis CNC"""

    def __init__(self):
        self.mopa_toolkit = Path("F:/Documents/CODE/MOPA_Laser_Toolkit")
        self.test_images = Path("F:/Documents/CODE/Blender-MCP/test_images")
        self.lightburn_output = Path("F:/Documents/Lightburn/generated_tests")
        self.gcode_output = Path("F:/Documents/GCODE/test_suite")

        # Create output directories
        self.lightburn_output.mkdir(parents=True, exist_ok=True)
        self.gcode_output.mkdir(parents=True, exist_ok=True)

    def print_menu(self):
        """Show available advanced tests"""
        print("\n" + "=" * 70)
        print("  ADVANCED MANUFACTURING TESTS")
        print("=" * 70)
        print("\n🌈 Test 3: Mandala Holographic Diffraction")
        print("   Status: MOPA Toolkit ready")
        print("   Requires: mandala.jpg in test_images/")
        print("   Output: .lbrn2 with 8-color diffraction layers")
        print("   Effect: Rainbow holographic colors on stainless steel")
        print()
        print("🎡 Test 6: Guardian Totem (4-Axis Rotary)")
        print("   Status: image_to_relief.py ready")
        print("   Requires: totem.jpg in test_images/")
        print("   Output: .gcode with rotary axis wrapping")
        print()
        print("🎡 Test 7: Alchemy Symbols (4-Axis Rotary)")
        print("   Status: image_to_relief.py ready")
        print("   Requires: alchemy.jpg in test_images/")
        print("   Output: .gcode with rotary axis wrapping")
        print()

    def generate_mandala_diffraction(self, image_path=None):
        """
        Test 3: Mandala Holographic Diffraction
        Uses MOPA toolkit's diffraction mode with 8-color layers
        """
        if image_path is None:
            image_path = self.test_images / "mandala.jpg"

        if not Path(image_path).exists():
            print(f"\n❌ Error: Image not found: {image_path}")
            print("\n📝 To generate this image in Adobe Firefly:")
            print("   Prompt: Intricate mandala sacred geometry, perfectly symmetrical,")
            print("           concentric circles and petals radiating from center, white")
            print("           lines on black background, minimal style, high contrast,")
            print("           precise geometric patterns")
            print("\n   Save as: test_images/mandala.jpg")
            return

        print(f"\n🌈 Generating Test 3: Mandala Holographic Diffraction")
        print(f"   Input: {image_path}")
        print(f"   Processing with MOPA Toolkit...")

        output_file = self.lightburn_output / "test_03_mandala_holographic.lbrn2"

        # MOPA Toolkit command for diffraction mode with 8 colors
        cmd = [
            sys.executable,
            str(self.mopa_toolkit / "main.py"),
            "--mode", "diffraction",
            "--angle-image", str(image_path),  # Use image for grating angles
            str(image_path),  # Color image (same file)
            str(output_file),
            "--color-layers", "8",  # 8-color rainbow diffraction
            "--config", str(self.mopa_toolkit / "config" / "laser_settings.json"),
            "--material", "stainless_304"
        ]

        print(f"\n💻 Command:")
        print(f"   {' '.join(cmd)}")
        print()

        try:
            result = subprocess.run(cmd, cwd=str(self.mopa_toolkit),
                                  capture_output=True, text=True, check=True)
            print(result.stdout)

            print(f"\n✅ Success!")
            print(f"   Output: {output_file}")
            print(f"\n📋 LightBurn Settings:")
            print(f"   • Material: Stainless steel 304 (polished)")
            print(f"   • 8 Layers: Each with different frequency")
            print(f"   • Colors: Red → Orange → Yellow → Green → Cyan → Blue → Purple → Magenta")
            print(f"   • Effect: Changes color based on viewing angle")
            print(f"\n🎯 Import to LightBurn:")
            print(f"   1. Open LightBurn")
            print(f"   2. File → Open → {output_file}")
            print(f"   3. All 8 layers are pre-configured with speeds/powers")
            print(f"   4. Frame to check position")
            print(f"   5. Run test on polished stainless steel")

        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error running MOPA Toolkit:")
            print(e.stderr)
            return

    def generate_rotary_gcode(self, test_name="totem", image_path=None):
        """
        Test 6 or 7: 4-Axis Rotary G-code
        Uses image_to_relief.py for cylindrical wrapping
        """
        if image_path is None:
            image_path = self.test_images / f"{test_name}.jpg"

        if not Path(image_path).exists():
            print(f"\n❌ Error: Image not found: {image_path}")

            if test_name == "totem":
                print("\n📝 To generate Guardian Totem in Adobe Firefly:")
                print("   Prompt: Unwrapped cylindrical texture map for totem pole carving,")
                print("           three stacked guardian spirits: eagle at top, bear in middle,")
                print("           raven at bottom, Pacific Northwest indigenous art style,")
                print("           bold black formlines on white background, 360° seamless wrap")
            else:
                print("\n📝 To generate Alchemy Symbols in Adobe Firefly:")
                print("   Prompt: Alchemical symbols wrapped around cylinder, seven planetary")
                print("           metals vertically stacked, gold Sun at top, silver Moon,")
                print("           copper Venus, iron Mars, tin Jupiter, mercury Mercury,")
                print("           lead Saturn at bottom, seamless 360° wrap")

            print(f"\n   Save as: test_images/{test_name}.jpg")
            print("   ⚠️  CRITICAL: Image must wrap seamlessly (left edge = right edge)")
            return

        test_num = "06" if test_name == "totem" else "07"
        print(f"\n🎡 Generating Test {test_num}: {test_name.title()} (4-Axis Rotary)")
        print(f"   Input: {image_path}")
        print(f"   Processing with image_to_relief.py...")

        # image_to_relief.py generates G-code from image
        cmd = [
            sys.executable,
            "image_to_relief.py",
            str(image_path)
        ]

        print(f"\n💻 Command:")
        print(f"   {' '.join(cmd)}")
        print()

        try:
            result = subprocess.run(cmd, cwd=str(Path.cwd()),
                                  capture_output=True, text=True, check=True)
            print(result.stdout)

            # Find the generated G-code file
            base_name = Path(image_path).stem
            gcode_file = Path(f"{base_name}_relief.gcode")

            if gcode_file.exists():
                # Move to test suite directory
                final_path = self.gcode_output / f"test_{test_num}_{test_name}_rotary.gcode"
                gcode_file.rename(final_path)

                print(f"\n✅ Success!")
                print(f"   Output: {final_path}")
                print(f"\n📋 CNC Settings:")
                print(f"   • Cylinder: 50-60mm diameter (wood, aluminum, or brass)")
                print(f"   • Rotary Axis: A-axis (360° = one revolution)")
                print(f"   • Tool: Ball end 1/8\" or V-bit 30°")
                print(f"   • Speeds: 600 mm/min carving, 2400 mm/min rapids")
                print(f"\n🎯 Run on CNC:")
                print(f"   1. Open OpenBuilds CONTROL")
                print(f"   2. Mount cylinder on rotary axis")
                print(f"   3. Home all axes (including A)")
                print(f"   4. Load: {final_path}")
                print(f"   5. Run air pass first (+10mm Z offset)")
                print(f"   6. Run actual carving pass")

        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error running image_to_relief.py:")
            print(e.stderr)
            return

    def check_test_images(self):
        """Check which test images are ready"""
        print("\n📁 Checking test_images directory...")

        required_images = {
            "mandala.jpg": "Test 3: Mandala Holographic",
            "totem.jpg": "Test 6: Guardian Totem",
            "alchemy.jpg": "Test 7: Alchemy Symbols"
        }

        found = []
        missing = []

        for img, desc in required_images.items():
            img_path = self.test_images / img
            if img_path.exists():
                size_mb = img_path.stat().st_size / (1024 * 1024)
                found.append(f"   ✅ {img} ({size_mb:.2f} MB) - {desc}")
            else:
                missing.append(f"   ❌ {img} - {desc}")

        if found:
            print("\n🎨 Images Found:")
            for item in found:
                print(item)

        if missing:
            print("\n⚠️  Images Missing:")
            for item in missing:
                print(item)
            print("\n💡 Generate these images in Adobe Firefly first")
            print("   Use prompts from MANUFACTURING_TEST_GUIDE.md")

        return len(found), len(missing)

def main():
    generator = AdvancedTestGenerator()

    if len(sys.argv) < 2:
        generator.print_menu()

        # Check what images are available
        found, missing = generator.check_test_images()

        print("\n" + "=" * 70)
        print("  COMMANDS")
        print("=" * 70)
        print("\n🌈 Generate Mandala Diffraction:")
        print("   python generate_advanced_tests.py --mandala [image_path]")
        print()
        print("🎡 Generate Totem Rotary G-code:")
        print("   python generate_advanced_tests.py --totem [image_path]")
        print()
        print("🎡 Generate Alchemy Rotary G-code:")
        print("   python generate_advanced_tests.py --alchemy [image_path]")
        print()
        print("🔍 Check Image Status:")
        print("   python generate_advanced_tests.py --check")
        print()
        return

    import argparse
    parser = argparse.ArgumentParser(description="Generate advanced manufacturing test files")
    parser.add_argument("--mandala", nargs='?', const=True,
                       help="Generate mandala diffraction .lbrn2")
    parser.add_argument("--totem", nargs='?', const=True,
                       help="Generate totem rotary G-code")
    parser.add_argument("--alchemy", nargs='?', const=True,
                       help="Generate alchemy rotary G-code")
    parser.add_argument("--check", action="store_true",
                       help="Check which test images are ready")

    args = parser.parse_args()

    if args.check:
        generator.check_test_images()
    elif args.mandala:
        image = args.mandala if isinstance(args.mandala, str) else None
        generator.generate_mandala_diffraction(image)
    elif args.totem:
        image = args.totem if isinstance(args.totem, str) else None
        generator.generate_rotary_gcode("totem", image)
    elif args.alchemy:
        image = args.alchemy if isinstance(args.alchemy, str) else None
        generator.generate_rotary_gcode("alchemy", image)

if __name__ == "__main__":
    main()
