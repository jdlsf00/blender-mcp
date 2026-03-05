#!/usr/bin/env python3
"""
Image to 3D Relief Converter for 4-Axis CNC

Converts a grayscale/color image into a 3D relief mesh suitable for
wrapping around a cylinder and machining with 4-axis CNC.

Process:
1. Load image and convert to grayscale heightmap
2. Map image onto cylinder surface (unwrap/project)
3. Generate 3D mesh with depth from brightness
4. Export as STL for surface_3d_generator.py
"""

import os
import sys
from PIL import Image
import numpy as np


def load_and_prepare_image(image_path, target_width=360, target_height=100):
    """
    Load image and prepare as heightmap

    Args:
        image_path: Path to input image
        target_width: Width in degrees (360 = full wrap)
        target_height: Height in mm along cylinder

    Returns:
        numpy array of normalized heights (0.0 to 1.0)
    """
    print(f"\n📂 Loading image: {image_path}")

    # Load image
    img = Image.open(image_path)
    print(f"   Original size: {img.size[0]}x{img.size[1]} pixels")
    print(f"   Mode: {img.mode}")

    # Convert to grayscale
    if img.mode != 'L':
        img = img.convert('L')
        print(f"   Converted to grayscale")

    # Resize to target dimensions
    img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    print(f"   Resized to: {img_resized.size[0]}x{img_resized.size[1]}")

    # Convert to numpy array and normalize to 0-1
    heightmap = np.array(img_resized, dtype=np.float32) / 255.0

    print(f"   Height range: {heightmap.min():.3f} to {heightmap.max():.3f}")

    return heightmap


def analyze_heightmap(heightmap):
    """Analyze heightmap statistics"""
    print("\n📊 Heightmap Analysis:")
    print(f"   Shape: {heightmap.shape} (height x width)")
    print(f"   Min value: {heightmap.min():.3f}")
    print(f"   Max value: {heightmap.max():.3f}")
    print(f"   Mean value: {heightmap.mean():.3f}")
    print(f"   Std deviation: {heightmap.std():.3f}")

    # Histogram
    hist, bins = np.histogram(heightmap.flatten(), bins=10)
    print(f"\n   Value distribution (10 bins):")
    for i in range(len(hist)):
        bar = '█' * int(hist[i] / hist.max() * 40)
        print(f"   {bins[i]:.2f}-{bins[i+1]:.2f}: {bar} ({hist[i]})")


def generate_cylinder_relief_profile(heightmap, base_radius=20.0, max_relief_depth=5.0):
    """
    Generate profile for each angle position

    Args:
        heightmap: 2D array where rows=height along cylinder, cols=angle positions
        base_radius: Base cylinder radius in mm
        max_relief_depth: Maximum depth of relief carving in mm

    Returns:
        List of (z_position, angle, radius) tuples
    """
    print("\n🔨 Generating 4-axis toolpath profile...")

    height_mm = 100.0  # Total height in mm
    num_height_steps, num_angles = heightmap.shape

    profiles = []

    for angle_idx in range(num_angles):
        angle_deg = (angle_idx / num_angles) * 360.0

        for height_idx in range(num_height_steps):
            z_pos = (height_idx / num_height_steps) * height_mm

            # Get height value (0=deepest cut, 1=no cut)
            height_value = heightmap[height_idx, angle_idx]

            # Convert to radius
            # Black (0.0) = cut deep = smaller radius
            # White (1.0) = no cut = base radius
            radius = base_radius - max_relief_depth * (1.0 - height_value)

            profiles.append((z_pos, angle_deg, radius))

    print(f"   Generated {len(profiles)} profile points")
    print(f"   Height steps: {num_height_steps}")
    print(f"   Angle steps: {num_angles}")
    print(f"   Base radius: {base_radius}mm")
    print(f"   Max relief: {max_relief_depth}mm")
    print(f"   Min radius: {base_radius - max_relief_depth}mm")

    return profiles


def export_to_gcode(profiles, output_file, feed_rate=400, spindle_rpm=12000):
    """Export relief profile as G-code"""
    print(f"\n💾 Exporting G-code: {output_file}")

    with open(output_file, 'w') as f:
        # Header
        f.write("; 4-Axis Image Relief Carving\n")
        f.write(f"; Generated from image heightmap\n")
        f.write(f"; Points: {len(profiles)}\n")
        f.write(";\n")

        # Initialize
        f.write("G21 ; millimeters\n")
        f.write("G90 ; absolute positioning\n")
        f.write(f"M3 S{spindle_rpm} ; spindle on\n")
        f.write("G0 Z30 ; safe height\n")
        f.write("G0 X0 A0 ; home\n\n")

        # Generate toolpath
        # Group by angle to create helical passes
        current_angle = None

        for z_pos, angle_deg, radius in profiles:
            x = z_pos  # X along cylinder axis
            y = radius  # Y is radial distance

            if angle_deg != current_angle:
                # New pass - rapid to start
                if current_angle is not None:
                    f.write("G0 Z30 ; retract between passes\n")
                f.write(f"; Pass at A{angle_deg:.1f} deg\n")
                f.write(f"G0 X{x:.3f} Y{y:.3f} A{angle_deg:.2f}\n")
                current_angle = angle_deg
            else:
                # Continue cutting
                f.write(f"G1 X{x:.3f} Y{y:.3f} A{angle_deg:.2f} F{feed_rate}\n")

        # Shutdown
        f.write("\nG0 Z30 ; retract\n")
        f.write("G0 X0 A0 ; home\n")
        f.write("M5 ; spindle off\n")
        f.write("M30 ; program end\n")

    file_size = os.path.getsize(output_file)
    print(f"   ✓ File size: {file_size/1024:.1f} KB")


def create_preview_image(heightmap, output_path):
    """Save preview of the heightmap"""
    print(f"\n🖼️  Creating preview: {output_path}")

    # Convert back to 0-255 range
    img_array = (heightmap * 255).astype(np.uint8)
    img = Image.fromarray(img_array, mode='L')
    img.save(output_path)
    print(f"   ✓ Preview saved")


def main():
    """Main conversion process"""

    if len(sys.argv) < 2:
        print("\n❌ Usage: python image_to_relief.py <image_file>")
        print("\nExample:")
        print('   python image_to_relief.py "F:\\Documents\\JPG\\my_image.jpg"')
        sys.exit(1)

    image_path = sys.argv[1]

    if not os.path.exists(image_path):
        print(f"\n❌ Error: File not found: {image_path}")
        sys.exit(1)

    print("\n" + "="*70)
    print("  IMAGE TO 4-AXIS RELIEF CONVERTER")
    print("="*70)

    # Configuration
    target_width = 360   # 360 degrees around cylinder (1° per pixel)
    target_height = 100  # 100mm tall (1mm per pixel)
    base_radius = 20.0   # mm
    max_relief = 5.0     # mm depth of carving

    print("\n⚙️  Configuration:")
    print(f"   Angular resolution: {target_width}° (1° per sample)")
    print(f"   Height: {target_height}mm (1mm per sample)")
    print(f"   Base radius: {base_radius}mm")
    print(f"   Max relief depth: {max_relief}mm")

    # Load and prepare image
    heightmap = load_and_prepare_image(image_path, target_width, target_height)

    # Analyze
    analyze_heightmap(heightmap)

    # Generate profile
    profiles = generate_cylinder_relief_profile(heightmap, base_radius, max_relief)

    # Export
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    gcode_file = os.path.join(output_dir, f"{base_name}_relief.gcode")
    preview_file = os.path.join(output_dir, f"{base_name}_heightmap_preview.png")

    export_to_gcode(profiles, gcode_file)
    create_preview_image(heightmap, preview_file)

    print("\n" + "="*70)
    print("  ✅ CONVERSION COMPLETE")
    print("="*70)
    print(f"\n📦 Output files:")
    print(f"   G-code: {gcode_file}")
    print(f"   Preview: {preview_file}")

    print("\n🎨 Visualization:")
    print("   FreeCAD:")
    print("   1. Open FreeCAD")
    print("   2. Macro → Execute freecad_4axis_viewer.FCMacro")
    print(f"   3. Select: {gcode_file}")

    print("\n   Blender:")
    print('   & "C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe" `')
    print('     --background --python "visualize_4axis_blender.py" `')
    print(f'     -- "{gcode_file}" "{base_name}_relief_viz.blend"')

    print("\n💡 Tips:")
    print("   • Black areas in image = deeper cuts")
    print("   • White areas = surface level (no cut)")
    print("   • Image will wrap 360° around cylinder")
    print("   • Adjust max_relief_depth for more/less depth")
    print()


if __name__ == "__main__":
    main()
