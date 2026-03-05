#!/usr/bin/env python3
"""
AI Art Prompt Generator for Manufacturing Test Suite

Combines spiritual wisdom themes with technical manufacturing specifications
to create meaningful test patterns for MOPA laser and CNC router.

Philosophy: "As Above, So Below" - Sacred geometry meets precision manufacturing
"""

import json
import os
from datetime import datetime


class TestPromptGenerator:
    """Generate AI art prompts for manufacturing test pieces"""

    def __init__(self):
        self.output_dir = "test_prompts"
        os.makedirs(self.output_dir, exist_ok=True)

        # Spiritual themes from your wisdom library
        self.hermetic_principles = {
            "mentalism": "THE ALL is MIND; The Universe is Mental",
            "correspondence": "As above, so below; as below, so above",
            "vibration": "Nothing rests; everything moves; everything vibrates",
            "polarity": "Everything is Dual; everything has poles",
            "rhythm": "Everything flows, out and in; everything has its tides",
            "cause_effect": "Every Cause has its Effect; every Effect has its Cause",
            "gender": "Gender is in everything; everything has Masculine and Feminine Principles"
        }

        self.sacred_symbols = [
            "Tree of Life (Kabbalah)", "Flower of Life", "Metatron's Cube",
            "Sri Yantra", "Seed of Life", "Vesica Piscis", "Platonic Solids",
            "Golden Spiral", "Merkaba", "Ouroboros", "Torus", "Mandala"
        ]

        self.tarot_themes = {
            "major_arcana": ["The Fool", "The Magician", "High Priestess", "Empress",
                           "Emperor", "Hierophant", "Lovers", "Chariot", "Strength"],
            "elements": ["Fire (Wands)", "Water (Cups)", "Air (Swords)", "Earth (Pentacles)"]
        }

    def generate_2d_laser_prompts(self):
        """Generate prompts for 2D laser engraving/cutting"""
        prompts = []

        # Test 1: Simple geometric precision (calibration)
        prompts.append({
            "name": "geometric_calibration",
            "type": "2D_laser_engrave_cut",
            "difficulty": "basic",
            "prompt": {
                "adobe_firefly": "Sacred geometry calibration grid, black and white line art, "
                               "precise circles, squares, hexagons arranged in perfect proportion, "
                               "golden ratio divisions, minimalist technical drawing style, "
                               "high contrast, vector-ready",
                "style": "Technical line art, monochrome, precise geometry",
                "resolution": "300 DPI minimum",
                "aspect_ratio": "Square (1:1)"
            },
            "manufacturing": {
                "material": "Brass sheet 0.5mm or cardstock",
                "laser_mode": "MOPA color marking + vector cut",
                "layers": {
                    "blue_engrave": "Fill patterns, fine detail",
                    "red_cut": "Outer perimeter, precise squares/circles"
                },
                "settings": {
                    "engrave_speed": "1200 mm/s",
                    "engrave_power": "18%",
                    "cut_speed": "20 mm/s",
                    "cut_power": "80%",
                    "passes": "2-3 for clean cut"
                },
                "size": "50mm × 50mm"
            },
            "validation": "Tests: Line precision, circle roundness, corner sharpness, power consistency"
        })

        # Test 2: Tree of Life (medium complexity)
        prompts.append({
            "name": "tree_of_life_kabbalah",
            "type": "2D_laser_engrave",
            "difficulty": "medium",
            "prompt": {
                "adobe_firefly": "Kabbalistic Tree of Life diagram, ten sephirot connected by 22 paths, "
                               "mystical Hebrew letters, sacred geometry, black background with golden "
                               "glowing lines and nodes, esoteric symbolism, ornate border with "
                               "intricate patterns, occult manuscript style, high detail",
                "wisdom_theme": self.hermetic_principles["correspondence"],
                "symbols": "10 sephiroth, 22 paths, Hebrew letters (Aleph to Tav)",
                "style": "Mystical illuminated manuscript, gold on black",
                "resolution": "600 DPI",
                "aspect_ratio": "Portrait (2:3)"
            },
            "manufacturing": {
                "material": "Anodized aluminum (black) or stainless steel",
                "laser_mode": "MOPA deep engraving + color",
                "technique": "Remove anodizing to reveal bright metal underneath",
                "settings": {
                    "speed": "900 mm/s",
                    "power": "22%",
                    "frequency": "80 kHz",
                    "passes": "1 (deep engrave)",
                    "grayscale": "Dithered for depth variation"
                },
                "size": "75mm × 110mm",
                "finish": "High contrast: dark background, bright symbols"
            },
            "validation": "Tests: Fine line detail, Hebrew letter legibility, depth consistency, complex pattern fidelity"
        })

        # Test 3: Mandala with diffraction (advanced)
        prompts.append({
            "name": "mandala_holographic",
            "type": "2D_laser_diffraction",
            "difficulty": "advanced",
            "prompt": {
                "adobe_firefly": "Intricate mandala with concentric circles, sacred lotus petals, "
                               "Sri Yantra triangles at center, gradient from white center to deep "
                               "black outer rings, smooth transitions, radial symmetry, 8-fold "
                               "geometric patterns, meditative spiritual art, ultra detailed",
                "wisdom_theme": self.hermetic_principles["vibration"],
                "symbols": "Lotus (8-petals), Sri Yantra center, OM symbol",
                "style": "Spiritual mandala art, smooth gradients, radial symmetry",
                "resolution": "600 DPI",
                "aspect_ratio": "Square (1:1)",
                "color_mode": "Grayscale gradient (for depth/pitch mapping)"
            },
            "manufacturing": {
                "material": "Stainless steel 304 polished",
                "laser_mode": "MOPA diffraction grating",
                "technique": "Gradient = varying line pitch (rainbow effect)",
                "settings": {
                    "speed": "1400-1800 mm/s (pitch controlled)",
                    "power": "15-26%",
                    "frequency": "800-1200 kHz",
                    "line_spacing": "0.8-2.0 microns (gradient mapped)",
                    "angle": "Radial pattern (360° sweep)"
                },
                "size": "80mm diameter circle",
                "effect": "Rainbow holographic colors when viewed at angles",
                "lighting": "Best under direct light source"
            },
            "validation": "Tests: Gradient smoothness, diffraction color range, pitch accuracy, radial symmetry"
        })

        return prompts

    def generate_25d_relief_prompts(self):
        """Generate prompts for 2.5D relief carving (depth maps)"""
        prompts = []

        # Test 4: Portrait relief (CNC depth map)
        prompts.append({
            "name": "hermetic_philosopher_portrait",
            "type": "2.5D_cnc_relief",
            "difficulty": "advanced",
            "prompt": {
                "adobe_firefly": "Portrait of ancient Hermetic philosopher with long beard, wise eyes, "
                               "wearing mystical robes covered in alchemical symbols, background with "
                               "cosmic swirls and sacred geometry, dramatic side lighting casting shadows, "
                               "Renaissance engraving style, high contrast grayscale for depth mapping, "
                               "white=raised, black=deep cuts",
                "wisdom_theme": self.hermetic_principles["mentalism"],
                "mood": "Contemplative wisdom, mystical knowledge",
                "lighting": "45° side lighting for depth definition",
                "style": "Albrecht Dürer engraving style, grayscale depth map",
                "resolution": "1024×1024 minimum",
                "aspect_ratio": "Portrait (3:4)"
            },
            "manufacturing": {
                "material": "Basswood, cherry, or MDF for testing",
                "machine": "CNC router 4-axis (if rotary) or 3-axis (flat)",
                "technique": "Grayscale heightmap → depth carving",
                "tool": "Ball end mill 1/8\" or 1/16\" for detail",
                "settings": {
                    "stepover": "10-20% of tool diameter",
                    "stepdown": "0.5mm max",
                    "feed_rate": "400 mm/min",
                    "max_depth": "5mm from surface to deepest cut",
                    "roughing_pass": "Optional 3mm depth, faster",
                    "finishing_pass": "Full detail, slower"
                },
                "size": "100mm × 133mm (or wrapped on 50mm dia cylinder)",
                "post_process": "Sand 220-grit, seal, optional stain"
            },
            "validation": "Tests: Fine facial detail, depth gradient smoothness, tool path quality, surface finish"
        })

        # Test 5: Flower of Life relief
        prompts.append({
            "name": "flower_of_life_3d_relief",
            "type": "2.5D_cnc_relief",
            "difficulty": "medium",
            "prompt": {
                "adobe_firefly": "Flower of Life sacred geometry in 3D relief, overlapping circles "
                               "appear to float at different depths, gradient shading from white peaks "
                               "to gray valleys, subtle embossed effect, monochromatic, soft lighting, "
                               "dimensional depth map, smooth gradients between circles",
                "wisdom_theme": self.hermetic_principles["correspondence"],
                "symbols": "19 overlapping circles, perfect symmetry",
                "style": "3D embossed relief, grayscale depth map, soft shadows",
                "resolution": "800×800 minimum",
                "aspect_ratio": "Square (1:1)"
            },
            "manufacturing": {
                "material": "Aluminum 6061 or brass sheet",
                "machine": "CNC router or MOPA laser (emboss mode)",
                "technique": "Depth from grayscale values",
                "settings_cnc": {
                    "tool": "Ball end 1/8\" or V-bit 30°",
                    "max_depth": "2mm",
                    "feed": "600 mm/min",
                    "stepover": "0.2mm"
                },
                "settings_mopa": {
                    "mode": "3D embossing layers",
                    "layers": "8-12 depth levels",
                    "power": "20-40% graduated",
                    "speed": "300-800 mm/s per layer"
                },
                "size": "80mm × 80mm",
                "finish": "Polished or brushed metal"
            },
            "validation": "Tests: Depth accuracy, circle intersection quality, gradient smoothness, geometric precision"
        })

        return prompts

    def generate_3d_rotary_prompts(self):
        """Generate prompts for 3D cylindrical (4-axis rotary) objects"""
        prompts = []

        # Test 6: Totem pole with faces
        prompts.append({
            "name": "guardian_totem_unwrapped",
            "type": "3D_rotary_4axis",
            "difficulty": "advanced",
            "prompt": {
                "adobe_firefly": "Unwrapped cylindrical texture map for totem pole carving, "
                               "three stacked guardian spirits: eagle at top, bear in middle, "
                               "raven at bottom, Pacific Northwest indigenous art style, "
                               "bold black formlines on white background, traditional Haida design, "
                               "geometric patterns between figures, 360° seamless wrap pattern, "
                               "rectangular format (360° width × height), grayscale for depth",
                "wisdom_theme": "Spirit guardians, elemental protection",
                "symbols": "Eagle (sky/vision), Bear (strength), Raven (transformation)",
                "style": "Pacific Northwest indigenous, bold formlines, high contrast",
                "resolution": "3600×1000 pixels (360° × 100mm unwrapped)",
                "aspect_ratio": "Panoramic 18:5 (wraps seamlessly)",
                "notes": "Must tile seamlessly left-to-right (360° wrap)"
            },
            "manufacturing": {
                "material": "Wood cylinder (pine, cedar, or basswood) 40mm dia × 100mm",
                "machine": "CNC router with 4-axis rotary",
                "process": "image_to_relief.py converts to G-code",
                "command": 'python image_to_relief.py "guardian_totem_unwrapped.jpg"',
                "settings": {
                    "base_radius": "20mm",
                    "max_relief_depth": "5mm",
                    "angular_resolution": "1° (360 samples)",
                    "height_resolution": "1mm (100 samples)",
                    "feed_rate": "400 mm/min",
                    "spindle": "12000 RPM",
                    "tool": "Ball end 1/8\" or tapered ball"
                },
                "technique": "Black = deep carving, White = surface level",
                "output": "36,000 point toolpath, helical passes",
                "finish": "Sand, stain (dark walnut), seal"
            },
            "validation": "Tests: Cylindrical wrap accuracy, 360° seamless join, face detail, depth variation, rotary axis precision"
        })

        # Test 7: Alchemical symbols cylinder
        prompts.append({
            "name": "alchemy_symbols_wrap",
            "type": "3D_rotary_4axis",
            "difficulty": "medium",
            "prompt": {
                "adobe_firefly": "Unwrapped texture for cylinder: alchemical symbols arranged in "
                               "horizontal bands, mercury/sulfur/salt symbols, planetary glyphs, "
                               "element symbols (🜂🜃🜁🜄), transmutation stages, medieval manuscript "
                               "style, gold and black color scheme (gold=surface, black=carved), "
                               "decorative borders between bands, seamless 360° wrap, grayscale depth map",
                "wisdom_theme": self.hermetic_principles["polarity"] + " + Alchemy",
                "symbols": "7 metals/planets, 4 elements, quintessence, philosopher's stone",
                "style": "Medieval alchemical manuscript, ornate, mystical",
                "resolution": "3600×1200 pixels",
                "aspect_ratio": "Panoramic 3:1",
                "color": "Grayscale or gold/black for depth mapping"
            },
            "manufacturing": {
                "material": "Brass or aluminum cylinder 50mm dia × 120mm",
                "machine": "CNC 4-axis or MOPA laser rotary",
                "technique_cnc": "Image to relief, helical toolpath",
                "technique_mopa": "Rotary deep engraving",
                "settings_cnc": {
                    "depth": "3mm relief",
                    "tool": "1/16\" ball end",
                    "feed": "500 mm/min"
                },
                "settings_mopa": {
                    "power": "35-50%",
                    "speed": "100-300 mm/s",
                    "frequency": "80 kHz",
                    "rotary_mode": "Continuous rotation synchronized"
                },
                "size": "50mm diameter × 120mm height",
                "finish": "Polish brass, apply patina to recessed areas"
            },
            "validation": "Tests: Symbol legibility, band alignment, seamless wrap, depth consistency, rotary synchronization"
        })

        return prompts

    def generate_combined_test_suite(self):
        """Generate complete test suite with all patterns"""

        print("\n" + "="*70)
        print("  AI ART PROMPT GENERATOR FOR MANUFACTURING")
        print("  Sacred Geometry + Precision Engineering")
        print("="*70)

        all_prompts = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "philosophy": "As Above, So Below - Hermetic Principles in Manufacturing",
                "purpose": "Test full capabilities of MOPA laser + CNC router",
                "wisdom_sources": "79,953 embeddings from 67 spiritual books",
                "total_tests": 0
            },
            "hermetic_principles": self.hermetic_principles,
            "test_patterns": {
                "2d_laser": self.generate_2d_laser_prompts(),
                "25d_relief": self.generate_25d_relief_prompts(),
                "3d_rotary": self.generate_3d_rotary_prompts()
            }
        }

        # Count total tests
        total = sum(len(v) for v in all_prompts["test_patterns"].values())
        all_prompts["metadata"]["total_tests"] = total

        # Save as JSON
        output_file = os.path.join(self.output_dir, "manufacturing_test_prompts.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_prompts, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Generated {total} test patterns:")
        print(f"   • 2D Laser: {len(all_prompts['test_patterns']['2d_laser'])}")
        print(f"   • 2.5D Relief: {len(all_prompts['test_patterns']['25d_relief'])}")
        print(f"   • 3D Rotary: {len(all_prompts['test_patterns']['3d_rotary'])}")
        print(f"\n📁 Saved to: {output_file}")

        # Generate markdown guide
        self._generate_markdown_guide(all_prompts)

        return output_file

    def _generate_markdown_guide(self, prompts_data):
        """Generate human-readable markdown guide"""

        md_file = os.path.join(self.output_dir, "MANUFACTURING_TEST_GUIDE.md")

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# Manufacturing Test Suite - AI-Generated Sacred Art\n\n")
            f.write("**Philosophy:** Hermetic Principles Meet Precision Manufacturing\n\n")
            f.write("Generated: " + prompts_data["metadata"]["generated"] + "\n\n")
            f.write("---\n\n")

            # 2D Laser section
            f.write("## 🔥 2D Laser Tests\n\n")
            for i, prompt in enumerate(prompts_data["test_patterns"]["2d_laser"], 1):
                f.write(f"### Test {i}: {prompt['name'].replace('_', ' ').title()}\n\n")
                f.write(f"**Difficulty:** {prompt['difficulty']}\n\n")
                f.write("**Adobe Firefly Prompt:**\n```\n")
                f.write(prompt['prompt']['adobe_firefly'] + "\n```\n\n")

                if 'wisdom_theme' in prompt['prompt']:
                    f.write(f"**Wisdom Theme:** _{prompt['prompt']['wisdom_theme']}_\n\n")

                f.write("**Manufacturing Specs:**\n")
                f.write(f"- Material: {prompt['manufacturing']['material']}\n")
                f.write(f"- Size: {prompt['manufacturing']['size']}\n")
                f.write(f"- Mode: {prompt['manufacturing']['laser_mode']}\n\n")

                f.write(f"**Validation:** {prompt['validation']}\n\n")
                f.write("---\n\n")

            # 2.5D Relief section
            f.write("## 🏔️ 2.5D Relief Tests\n\n")
            for i, prompt in enumerate(prompts_data["test_patterns"]["25d_relief"], 1):
                f.write(f"### Test {i+3}: {prompt['name'].replace('_', ' ').title()}\n\n")
                f.write(f"**Difficulty:** {prompt['difficulty']}\n\n")
                f.write("**Adobe Firefly Prompt:**\n```\n")
                f.write(prompt['prompt']['adobe_firefly'] + "\n```\n\n")

                f.write("**Key Points:**\n")
                f.write("- White = raised surface\n")
                f.write("- Black = deep cuts\n")
                f.write("- Smooth gradients for depth\n\n")

                f.write("**Manufacturing:**\n")
                f.write(f"- Material: {prompt['manufacturing']['material']}\n")
                if 'settings_cnc' in prompt['manufacturing']:
                    f.write(f"- Max Depth: {prompt['manufacturing']['settings_cnc']['max_depth']}\n")
                    f.write(f"- Tool: {prompt['manufacturing']['settings_cnc']['tool']}\n")
                elif 'settings' in prompt['manufacturing']:
                    f.write(f"- Settings available in JSON file\n")
                f.write("\n")

                f.write("---\n\n")

            # 3D Rotary section
            f.write("## 🎡 3D Rotary Tests (4-Axis)\n\n")
            for i, prompt in enumerate(prompts_data["test_patterns"]["3d_rotary"], 1):
                f.write(f"### Test {i+5}: {prompt['name'].replace('_', ' ').title()}\n\n")
                f.write(f"**Difficulty:** {prompt['difficulty']}\n\n")
                f.write("**Adobe Firefly Prompt:**\n```\n")
                f.write(prompt['prompt']['adobe_firefly'] + "\n```\n\n")

                f.write("**⚠️ Critical:** Image must wrap seamlessly 360° (left edge = right edge)\n\n")

                f.write("**Workflow:**\n")
                f.write("1. Generate image in Firefly (panoramic aspect ratio)\n")
                f.write("2. Adjust contrast in Photoshop (black=deep, white=surface)\n")
                if 'command' in prompt['manufacturing']:
                    f.write(f"3. Run: `{prompt['manufacturing']['command']}`\n")
                else:
                    f.write("3. Run: `python image_to_relief.py \"your_image.jpg\"`\n")
                f.write("4. Load G-code in OpenBuilds CONTROL\n")
                f.write("5. Mount cylinder on rotary axis\n")
                f.write("6. Run air pass (+10mm Z offset)\n")
                f.write("7. Run real pass\n\n")

                f.write("---\n\n")

            # Quick reference
            f.write("## 🚀 Quick Start Workflow\n\n")
            f.write("### For Each Test:\n\n")
            f.write("1. **Generate Art** (Adobe Firefly)\n")
            f.write("   - Copy prompt from above\n")
            f.write("   - Use specified aspect ratio\n")
            f.write("   - Download highest resolution\n\n")

            f.write("2. **Prepare Image** (Photoshop)\n")
            f.write("   - Convert to grayscale (if relief/rotary)\n")
            f.write("   - Adjust Levels/Curves for contrast\n")
            f.write("   - For depth maps: Black=deep, White=surface\n")
            f.write("   - Save as high-quality JPG or PNG\n\n")

            f.write("3. **Convert to G-code** (for CNC/Rotary)\n")
            f.write("   ```powershell\n")
            f.write("   python image_to_relief.py \"your_image.jpg\"\n")
            f.write("   ```\n\n")

            f.write("4. **Load in Software**\n")
            f.write("   - LightBurn: Import SVG/image, assign layers\n")
            f.write("   - OpenBuilds CONTROL: Load G-code\n")
            f.write("   - FreeCAD: Use macro for preview\n\n")

            f.write("5. **Test Run**\n")
            f.write("   - Frame/focus (laser) or air pass (CNC)\n")
            f.write("   - Run on scrap material first\n")
            f.write("   - Adjust settings based on results\n\n")

            f.write("## 📊 Validation Checklist\n\n")
            f.write("For each completed test piece:\n\n")
            f.write("- [ ] Dimensional accuracy (measure with caliper)\n")
            f.write("- [ ] Detail quality (magnifying glass inspection)\n")
            f.write("- [ ] Surface finish (smoothness, no chatter)\n")
            f.write("- [ ] Edge quality (clean cuts, no burrs)\n")
            f.write("- [ ] Depth consistency (if relief)\n")
            f.write("- [ ] Color/diffraction effect (if MOPA)\n")
            f.write("- [ ] 360° wrap alignment (if rotary)\n")
            f.write("- [ ] Photo documentation (before/after)\n\n")

        print(f"📄 Guide saved to: {md_file}")

    def print_quick_summary(self):
        """Print quick reference to console"""
        print("\n" + "="*70)
        print("  QUICK REFERENCE - TEST PATTERN WORKFLOW")
        print("="*70)
        print("\n📋 Generated 7 Test Patterns:")
        print("\n2D Laser (3 tests):")
        print("  1. Geometric Calibration - Basic precision test")
        print("  2. Tree of Life - Medium complexity engraving")
        print("  3. Mandala Holographic - Advanced diffraction grating")
        print("\n2.5D Relief (2 tests):")
        print("  4. Hermetic Philosopher Portrait - Detailed depth map")
        print("  5. Flower of Life 3D - Embossed sacred geometry")
        print("\n3D Rotary (2 tests):")
        print("  6. Guardian Totem - Multi-figure cylindrical carving")
        print("  7. Alchemy Symbols - Symbol bands wrapping cylinder")
        print("\n💡 Next Steps:")
        print("  1. Open test_prompts/MANUFACTURING_TEST_GUIDE.md")
        print("  2. Copy first prompt to Adobe Firefly")
        print("  3. Generate image with specified settings")
        print("  4. Follow workflow in guide for your machine")
        print("\n🎨 All prompts combine:")
        print("  • Your spiritual wisdom library (Hermetic, Tarot, Alchemy)")
        print("  • Technical manufacturing specifications")
        print("  • Progressive difficulty (basic → advanced)")
        print("  • Complete validation criteria")
        print()


def main():
    """Generate complete test suite"""
    generator = TestPromptGenerator()
    output_file = generator.generate_combined_test_suite()
    generator.print_quick_summary()

    print("\n✨ Ready to create sacred art with precision manufacturing!")
    print(f"\n📂 All files in: {generator.output_dir}/")
    print("   • manufacturing_test_prompts.json (machine-readable)")
    print("   • MANUFACTURING_TEST_GUIDE.md (human-readable)")
    print()


if __name__ == "__main__":
    main()
