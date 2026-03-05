#!/usr/bin/env python3
"""
Generate LightBurn Project Files (.lbrn2) with embedded images and pre-configured layers

Takes any image and creates a ready-to-run LightBurn file with:
- Image embedded as raster
- Multiple layers with different MOPA settings
- Optimized for effects: color, diffraction, deep engrave, etc.

Usage:
    python generate_lightburn_project.py image.jpg --effect color --material stainless_304
    python generate_lightburn_project.py image.jpg --effect diffraction --material stainless_304
"""

import json
import base64
import argparse
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from PIL import Image

class LightBurnProjectGenerator:
    """Generate LightBurn .lbrn2 files with embedded images and configured layers"""

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path("F:/Documents/CODE/MOPA_Laser_Toolkit/config/laser_settings.json")

        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def create_project(self, image_path, output_path, effect="color", material="stainless_304", max_size_mm=100):
        """
        Create LightBurn project with image and layers

        Args:
            image_path: Path to input image
            output_path: Path for output .lbrn2 file
            effect: "color", "diffraction", "engrave", "photo"
            material: Material type from config
            max_size_mm: Maximum dimension in mm
        """

        print(f"\n🎨 Creating LightBurn Project")
        print(f"   Image: {image_path}")
        print(f"   Effect: {effect}")
        print(f"   Material: {material}")

        # Load and process image
        img = Image.open(image_path)
        img_width, img_height = img.size

        # Resize to reasonable resolution for laser (0.1mm per pixel = 1000px per 100mm)
        max_pixels = int(max_size_mm * 10)  # 10 pixels per mm
        if img_width > img_height:
            new_width = min(img_width, max_pixels)
            new_height = int(img_height * (new_width / img_width))
        else:
            new_height = min(img_height, max_pixels)
            new_width = int(img_width * (new_height / img_height))

        print(f"   Resizing: {img_width}×{img_height} → {new_width}×{new_height} px")
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img_width, img_height = img.size

        # Convert to grayscale for processing
        img_gray = img.convert('L')

        # Calculate size in mm (maintain aspect ratio)
        aspect = img_width / img_height
        if aspect > 1:
            width_mm = max_size_mm
            height_mm = max_size_mm / aspect
        else:
            height_mm = max_size_mm
            width_mm = max_size_mm * aspect

        print(f"   Size: {width_mm:.1f} × {height_mm:.1f} mm")

        # Encode image as base64 PNG
        img_bytes = self._image_to_base64(img_gray)

        # Create XML structure
        root = self._create_project_root()

        # Get layer settings based on effect
        layers = self._get_layer_settings(effect, material)

        print(f"   Layers: {len(layers)}")

        # Add cut settings (layers)
        for idx, layer_info in enumerate(layers):
            cut_setting = self._create_cut_setting(idx, layer_info)
            root.append(cut_setting)

        # Add image shape for each layer
        for idx, layer_info in enumerate(layers):
            shape = self._create_image_shape(
                img_bytes,
                width_mm,
                height_mm,
                layer_index=idx,
                layer_name=layer_info['name']
            )
            root.append(shape)

        # Save file
        self._save_project(root, output_path)

        print(f"\n✅ Project saved: {output_path}")
        print(f"\n📋 Usage:")
        print(f"   1. Open in LightBurn")
        print(f"   2. Position on bed")
        print(f"   3. Frame to check")
        print(f"   4. Start (it will process all layers)")
        print(f"\n💡 Each layer scans the image with different MOPA settings")

    def _image_to_base64(self, img):
        """Convert PIL image to base64 PNG"""
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def _create_project_root(self):
        """Create LightBurn project root element"""
        root = Element('LightBurnProject')
        root.set('AppVersion', '1.6.00')
        root.set('FormatVersion', '1')
        root.set('MaterialHeight', '0')
        root.set('MirrorX', 'False')
        root.set('MirrorY', 'False')

        # Add thumbnail placeholder
        SubElement(root, 'Thumbnail', {'Source': ''})

        # Add variable text
        var_text = SubElement(root, 'VariableText')
        SubElement(var_text, 'Start', {'Value': '0'})
        SubElement(var_text, 'End', {'Value': '999'})
        SubElement(var_text, 'Current', {'Value': '0'})
        SubElement(var_text, 'Increment', {'Value': '1'})
        SubElement(var_text, 'AutoAdvance', {'Value': '0'})

        # Add UI prefs
        ui_prefs = SubElement(root, 'UIPrefs')
        SubElement(ui_prefs, 'Optimize_ByLayer', {'Value': '0'})
        SubElement(ui_prefs, 'Optimize_ByGroup', {'Value': '-1'})
        SubElement(ui_prefs, 'Optimize_ByPriority', {'Value': '1'})
        SubElement(ui_prefs, 'Optimize_WhichDirection', {'Value': '0'})
        SubElement(ui_prefs, 'Optimize_InnerToOuter', {'Value': '1'})
        SubElement(ui_prefs, 'Optimize_ByDirection', {'Value': '0'})
        SubElement(ui_prefs, 'Optimize_ReduceTravel', {'Value': '1'})
        SubElement(ui_prefs, 'Optimize_HideBacklash', {'Value': '0'})
        SubElement(ui_prefs, 'Optimize_ReduceDirChanges', {'Value': '0'})
        SubElement(ui_prefs, 'Optimize_ChooseCorners', {'Value': '0'})
        SubElement(ui_prefs, 'Optimize_AllowReverse', {'Value': '1'})
        SubElement(ui_prefs, 'Optimize_RemoveOverlaps', {'Value': '0'})
        SubElement(ui_prefs, 'Optimize_OptimalEntryPoint', {'Value': '1'})
        SubElement(ui_prefs, 'Optimize_OverlapDist', {'Value': '0.025'})

        return root

    def _get_layer_settings(self, effect, material):
        """Get layer settings based on effect and material"""

        if effect == "color" and material == "stainless_304":
            # Multiple passes with different frequencies for color
            return [
                {"name": "Gold", "power": 18, "speed": 1200, "frequency": 45000, "pulse_width": 25, "interval": 0.01},
                {"name": "Blue", "power": 22, "speed": 1000, "frequency": 65000, "pulse_width": 20, "interval": 0.01},
                {"name": "Purple", "power": 25, "speed": 900, "frequency": 80000, "pulse_width": 15, "interval": 0.01},
            ]

        elif effect == "diffraction":
            # Diffraction settings from config
            settings = []
            for key in ['C0', 'C1', 'C2', 'C3']:
                if key in self.config.get('diffraction_grating_settings', {}):
                    layer = self.config['diffraction_grating_settings'][key]
                    settings.append({
                        "name": layer['name'],
                        "power": layer['settings']['power'],
                        "speed": layer['settings']['speed'],
                        "frequency": int(layer['settings']['frequency'] * 1000),  # kHz to Hz
                        "pulse_width": layer['settings']['pulse_width_ns'],
                        "interval": layer['settings']['line_interval_mm']
                    })
            return settings

        elif effect == "engrave":
            # Deep engraving
            return [
                {"name": "Deep", "power": 60, "speed": 400, "frequency": 20000, "pulse_width": 100, "interval": 0.05},
            ]

        elif effect == "photo":
            # Photo engraving on anodized aluminum
            return [
                {"name": "Photo", "power": 30, "speed": 800, "frequency": 40000, "pulse_width": 80, "interval": 0.1},
            ]

        else:
            # Default: simple marking
            return [
                {"name": "Mark", "power": 20, "speed": 1000, "frequency": 35000, "pulse_width": 60, "interval": 0.05},
            ]

    def _create_cut_setting(self, index, layer_info):
        """Create a CutSetting_Img element for image scanning"""
        # For images, use CutSetting_Img instead of CutSetting
        cut_setting = Element('CutSetting_Img', {'type': 'Image'})

        SubElement(cut_setting, 'index', {'Value': str(index)})
        SubElement(cut_setting, 'name', {'Value': layer_info['name']})
        SubElement(cut_setting, 'maxPower', {'Value': str(layer_info['power'])})
        SubElement(cut_setting, 'maxPower2', {'Value': '20'})
        SubElement(cut_setting, 'speed', {'Value': str(layer_info['speed'])})
        SubElement(cut_setting, 'frequency', {'Value': str(layer_info['frequency'])})
        SubElement(cut_setting, 'QPulseWidth', {'Value': str(layer_info['pulse_width'])})
        SubElement(cut_setting, 'runBlower', {'Value': '0'})
        SubElement(cut_setting, 'numPasses', {'Value': '256'})
        SubElement(cut_setting, 'scanOpt', {'Value': 'individual'})
        SubElement(cut_setting, 'interval', {'Value': str(layer_info['interval'])})
        SubElement(cut_setting, 'priority', {'Value': str(index + 2)})
        SubElement(cut_setting, 'doOutput', {'Value': '1'})
        SubElement(cut_setting, 'hide', {'Value': '0'})
        SubElement(cut_setting, 'tabCount', {'Value': '1'})
        SubElement(cut_setting, 'tabCountMax', {'Value': '1'})
        SubElement(cut_setting, 'ditherMode', {'Value': '3dslice'})
        SubElement(cut_setting, 'dpi', {'Value': '1016'})

        return cut_setting

    def _create_image_shape(self, img_base64, width_mm, height_mm, layer_index=0, layer_name="Image"):
        """Create an image shape element"""
        shape = Element('Shape', {'Type': 'Image', 'CutIndex': str(layer_index)})

        # Image data
        SubElement(shape, 'ImageData').text = img_base64

        # Position (centered at origin)
        x_center = 0
        y_center = 0

        # XForm: scale_x rotation_x rotation_y scale_y translate_x translate_y
        # Format: "1 0 0 1 x y" for no rotation/scale, just translation
        xform = SubElement(shape, 'XForm')
        xform.text = f"1 0 0 1 {x_center} {y_center}"

        # Add image width and height
        SubElement(shape, 'ImageWidth', {'Value': str(int(width_mm * 10))})
        SubElement(shape, 'ImageHeight', {'Value': str(int(height_mm * 10))})

        return shape

    def _save_project(self, root, path):
        """Save XML to .lbrn2 file with pretty formatting"""
        xml_string = tostring(root, encoding='utf-8')

        # Pretty print
        dom = minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml(indent="    ", encoding='utf-8')

        with open(path, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            # Skip the XML declaration from minidom
            lines = pretty_xml.split(b'\n')
            for line in lines[1:]:
                if line.strip():
                    f.write(line + b'\n')

def main():
    parser = argparse.ArgumentParser(description="Generate LightBurn project files")
    parser.add_argument("image", help="Input image path")
    parser.add_argument("-o", "--output", help="Output .lbrn2 path")
    parser.add_argument("-e", "--effect",
                       choices=["color", "diffraction", "engrave", "photo"],
                       default="color",
                       help="Effect type")
    parser.add_argument("-m", "--material",
                       default="stainless_304",
                       help="Material type")
    parser.add_argument("-s", "--size", type=float, default=100,
                       help="Maximum dimension in mm")

    args = parser.parse_args()

    # Generate output name if not specified
    if args.output is None:
        img_path = Path(args.image)
        args.output = f"{img_path.stem}_{args.effect}.lbrn2"

    # Generate project
    generator = LightBurnProjectGenerator()
    generator.create_project(
        args.image,
        args.output,
        effect=args.effect,
        material=args.material,
        max_size_mm=args.size
    )

if __name__ == "__main__":
    main()
