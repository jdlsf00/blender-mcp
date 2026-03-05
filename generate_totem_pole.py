#!/usr/bin/env python3
"""
Totem Pole Generator - Complex Decorative 4-Axis Object

Creates a traditional Pacific Northwest style totem pole with:
- Carved faces and features
- Wings extending from sides
- Geometric patterns
- Multiple stacked characters
- Decorative bands with patterns

This demonstrates complex rotationally symmetric design.
"""

import math
import os


class TotemPoleGenerator:
    """Generate decorative totem pole with multiple sections"""

    def __init__(self):
        self.output_dir = "test_output"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_totem_pole(self):
        """Generate complete totem pole with multiple sections"""
        print("\n" + "="*60)
        print("  TOTEM POLE GENERATOR")
        print("="*60)

        # Profile sections (z_position, radius_mm, description)
        sections = []

        # BASE (0-15mm) - Wide foundation
        sections.extend(self._create_base_section(0, 15))

        # BOTTOM FIGURE (15-35mm) - Large character
        sections.extend(self._create_figure_section(15, 35, scale=1.0, style='bear'))

        # DECORATIVE BAND (35-40mm) - Geometric pattern
        sections.extend(self._create_pattern_band(35, 40, pattern='zigzag'))

        # MIDDLE FIGURE (40-60mm) - Medium character
        sections.extend(self._create_figure_section(40, 60, scale=0.85, style='eagle'))

        # WING SECTION (60-65mm) - Extended wings
        sections.extend(self._create_wing_section(60, 65))

        # TOP FIGURE (65-85mm) - Small character
        sections.extend(self._create_figure_section(65, 85, scale=0.7, style='raven'))

        # DECORATIVE BAND (85-88mm)
        sections.extend(self._create_pattern_band(85, 88, pattern='diamonds'))

        # TOP CAP (88-95mm) - Pointed top
        sections.extend(self._create_cap_section(88, 95))

        # Generate G-code
        gcode_file = self._generate_gcode(sections, "totem_pole.gcode")

        print(f"\n✅ Totem pole generated!")
        print(f"   File: {gcode_file}")
        print(f"   Height: 95mm")
        print(f"   Points: {len(sections)}")
        print(f"   Sections: 8 (base, 3 figures, 2 bands, wings, cap)")

        return gcode_file

    def _create_base_section(self, z_start, z_end):
        """Create wide stable base"""
        sections = []
        z_positions = self._linspace(z_start, z_end, 15)

        for z in z_positions:
            # Taper from 25mm to 22mm radius
            t = (z - z_start) / (z_end - z_start)
            radius = 25.0 - 3.0 * t
            sections.append((z, radius))

        return sections

    def _create_figure_section(self, z_start, z_end, scale=1.0, style='bear'):
        """Create carved figure with varying depth"""
        sections = []
        height = z_end - z_start
        num_points = int(height * 2)  # 2 points per mm

        base_radius = 22.0 * scale

        for i in range(num_points):
            t = i / (num_points - 1)
            z = z_start + t * height

            # Create body profile based on style
            if style == 'bear':
                radius = self._bear_profile(t, base_radius)
            elif style == 'eagle':
                radius = self._eagle_profile(t, base_radius)
            elif style == 'raven':
                radius = self._raven_profile(t, base_radius)
            else:
                radius = base_radius

            sections.append((z, radius))

        return sections

    def _bear_profile(self, t, base_radius):
        """Bear face profile - wide chest, narrow head"""
        # Bottom: wide chest
        # Middle: narrow waist
        # Top: wide head

        if t < 0.3:  # Chest (bottom 30%)
            chest_factor = 1.0 + 0.15 * math.sin(t * math.pi / 0.3)
            return base_radius * chest_factor
        elif t < 0.6:  # Waist (middle 30%)
            return base_radius * 0.85
        else:  # Head (top 40%)
            head_t = (t - 0.6) / 0.4
            head_factor = 0.85 + 0.25 * (1 - (2*head_t - 1)**2)  # Parabolic
            return base_radius * head_factor

    def _eagle_profile(self, t, base_radius):
        """Eagle profile - narrow body, wide beak"""
        # Bottom: talons
        # Middle: narrow body
        # Top: wide beak/head

        if t < 0.25:  # Talons
            return base_radius * 0.7
        elif t < 0.7:  # Body
            body_t = (t - 0.25) / 0.45
            return base_radius * (0.7 + 0.15 * math.sin(body_t * math.pi))
        else:  # Head/Beak
            head_t = (t - 0.7) / 0.3
            return base_radius * (0.85 + 0.3 * head_t)

    def _raven_profile(self, t, base_radius):
        """Raven profile - smooth curves"""
        # Sinusoidal variation
        wave = math.sin(t * math.pi)
        return base_radius * (0.8 + 0.25 * wave)

    def _create_pattern_band(self, z_start, z_end, pattern='zigzag'):
        """Create decorative band with geometric pattern"""
        sections = []
        num_points = int((z_end - z_start) * 3)  # Dense sampling
        base_radius = 20.0

        for i in range(num_points):
            t = i / (num_points - 1)
            z = z_start + t * (z_end - z_start)

            if pattern == 'zigzag':
                # Sharp triangular waves
                wave_freq = 8  # 8 waves across height
                wave_t = (t * wave_freq) % 1.0
                if wave_t < 0.5:
                    depth = wave_t * 2.0  # Rise
                else:
                    depth = 2.0 - wave_t * 2.0  # Fall
                radius = base_radius - 2.0 + depth * 2.0

            elif pattern == 'diamonds':
                # Diamond/rhombus pattern
                wave_freq = 6
                wave_t = (t * wave_freq) % 1.0
                depth = 1.0 - abs(2.0 * wave_t - 1.0)  # Triangle wave
                radius = base_radius - 1.5 + depth * 1.5

            else:
                radius = base_radius

            sections.append((z, radius))

        return sections

    def _create_wing_section(self, z_start, z_end):
        """Create wing section - extensions from body"""
        sections = []
        num_points = int((z_end - z_start) * 3)
        base_radius = 20.0

        for i in range(num_points):
            t = i / (num_points - 1)
            z = z_start + t * (z_end - z_start)

            # Wings extend out then back
            # Parabolic curve for smooth wing shape
            extension = 8.0 * (1.0 - (2*t - 1)**2)  # Max 8mm extension at center
            radius = base_radius + extension

            sections.append((z, radius))

        return sections

    def _create_cap_section(self, z_start, z_end):
        """Create pointed cap at top"""
        sections = []
        num_points = int((z_end - z_start) * 2)

        for i in range(num_points):
            t = i / (num_points - 1)
            z = z_start + t * (z_end - z_start)

            # Taper to point
            radius = 20.0 * (1.0 - t) + 2.0  # From 20mm to 2mm

            sections.append((z, radius))

        return sections

    def _generate_gcode(self, sections, filename):
        """Generate G-code from profile sections"""
        output_file = os.path.join(self.output_dir, filename)

        # Machining parameters
        stepover = 1.0  # mm (fine detail)
        angular_resolution = 3.0  # degrees (smooth curves)
        feed_rate = 500  # mm/min
        spindle_rpm = 12000
        safe_z = 30.0

        with open(output_file, 'w') as f:
            # Header
            f.write(f"; Totem Pole - Decorative 4-Axis Carving\n")
            f.write(f"; Generated with TotemPoleGenerator\n")
            f.write(f"; Total sections: {len(sections)}\n")
            f.write(f"; Stepover: {stepover}mm\n")
            f.write(f"; Angular resolution: {angular_resolution}°\n")
            f.write(f";\n")

            # Initialize
            f.write("G21 ; millimeters\n")
            f.write("G90 ; absolute positioning\n")
            f.write(f"M3 S{spindle_rpm} ; spindle on\n")
            f.write(f"G0 Z{safe_z} ; safe height\n")
            f.write("G0 X0 A0 ; home position\n")
            f.write("\n")

            point_count = 0

            # Generate toolpath
            for angle_deg in self._angle_range(0, 360, angular_resolution):
                angle_rad = math.radians(angle_deg)

                for i, (z, radius) in enumerate(sections):
                    # Convert cylindrical to Cartesian
                    x = z  # X is along rotation axis
                    y = radius  # Y is radial distance
                    z_offset = 0  # Z offset from centerline

                    if i == 0 or angle_deg == 0:
                        # Rapid to start of new pass
                        f.write(f"G0 X{x:.3f} Y{y:.3f} A{angle_deg:.2f}\n")
                    else:
                        # Feed during cutting
                        f.write(f"G1 X{x:.3f} Y{y:.3f} A{angle_deg:.2f} F{feed_rate}\n")

                    point_count += 1

                # Return to safe Z between passes
                if angle_deg < 360:
                    f.write(f"G0 Z{safe_z}\n")

            # Shutdown
            f.write(f"\nG0 Z{safe_z} ; retract\n")
            f.write("G0 X0 A0 ; return to home\n")
            f.write("M5 ; spindle off\n")
            f.write("M30 ; program end\n")

        print(f"✓ Generated {point_count} toolpath points")
        return output_file

    def _linspace(self, start, end, num):
        """Generate evenly spaced values"""
        if num < 2:
            return [start]
        step = (end - start) / (num - 1)
        return [start + i * step for i in range(num)]

    def _angle_range(self, start, end, step):
        """Generate angle range"""
        angles = []
        angle = start
        while angle <= end:
            angles.append(angle)
            angle += step
        return angles


def generate_decorative_cylinder():
    """Generate decorative cylinder with relief patterns"""
    print("\n" + "="*60)
    print("  DECORATIVE CYLINDER GENERATOR")
    print("="*60)

    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)

    sections = []

    # Create cylinder with carved relief bands
    z_positions = [i * 2.0 for i in range(50)]  # 0 to 98mm in 2mm steps
    base_radius = 20.0

    for z in z_positions:
        # Create repeating relief pattern
        # Divide into 5mm bands, alternating deep/shallow
        band = int(z / 5.0) % 2

        if band == 0:
            # Shallow band - smooth cylinder
            radius = base_radius
        else:
            # Deep band - carved relief
            # Sinusoidal depth variation
            local_z = (z % 5.0) / 5.0  # 0 to 1 within band
            depth = 2.0 * math.sin(local_z * math.pi * 2)  # 2 waves per band
            radius = base_radius - 1.5 + depth

        sections.append((z, radius))

    # Generate G-code
    output_file = os.path.join(output_dir, "decorative_cylinder.gcode")

    with open(output_file, 'w') as f:
        f.write("; Decorative Cylinder with Relief Bands\n")
        f.write("G21 G90\n")
        f.write("M3 S12000\n")
        f.write("G0 Z30\n\n")

        point_count = 0
        for angle in range(0, 361, 3):
            for i, (z, radius) in enumerate(sections):
                x, y = z, radius
                cmd = "G0" if i == 0 else "G1"
                f.write(f"{cmd} X{x:.3f} Y{y:.3f} A{angle:.1f} F500\n")
                point_count += 1

        f.write("\nG0 Z30\nM5\nM30\n")

    print(f"✓ Decorative cylinder generated")
    print(f"   File: {output_file}")
    print(f"   Height: 98mm")
    print(f"   Points: {point_count}")
    print(f"   Pattern: Alternating relief bands\n")

    return output_file


def main():
    """Generate multiple decorative objects"""
    print("\n" + "="*70)
    print("  DECORATIVE 4-AXIS OBJECT GENERATOR")
    print("="*70)
    print("\nGenerating complex decorative objects for 4-axis machining...\n")

    # Generate totem pole
    generator = TotemPoleGenerator()
    totem_file = generator.generate_totem_pole()

    print("\n" + "-"*60 + "\n")

    # Generate decorative cylinder
    cylinder_file = generate_decorative_cylinder()

    print("\n" + "="*70)
    print("  GENERATION COMPLETE")
    print("="*70)
    print("\n📦 Generated Files:")
    print(f"   1. {totem_file}")
    print(f"      → Totem pole with 3 figures, wings, decorative bands")
    print(f"   2. {cylinder_file}")
    print(f"      → Cylinder with alternating relief pattern bands")

    print("\n🎨 Visualization:")
    print("   Blender:")
    print('   & "C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe" `')
    print('     --background --python "visualize_4axis_blender.py" `')
    print(f'     -- "{totem_file}" "totem_pole_viz.blend"')

    print("\n   FreeCAD:")
    print("   1. Open FreeCAD")
    print("   2. Macro → Macros → Execute freecad_4axis_viewer.FCMacro")
    print(f"   3. Select: {totem_file}")

    print("\n💡 Next Steps:")
    print("   • Visualize in Blender or FreeCAD")
    print("   • Adjust profile functions for different styles")
    print("   • Test on hardware CNC")
    print()


if __name__ == "__main__":
    main()
