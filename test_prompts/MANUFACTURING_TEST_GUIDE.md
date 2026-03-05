# Manufacturing Test Suite - AI-Generated Sacred Art

**Philosophy:** Hermetic Principles Meet Precision Manufacturing

Generated: 2025-11-14T21:00:03.848651

---

## 🔥 2D Laser Tests

### Test 1: Geometric Calibration

**Difficulty:** basic

**Adobe Firefly Prompt:**
```
Sacred geometry calibration grid, black and white line art, precise circles, squares, hexagons arranged in perfect proportion, golden ratio divisions, minimalist technical drawing style, high contrast, vector-ready
```

**Manufacturing Specs:**
- Material: Brass sheet 0.5mm or cardstock
- Size: 50mm × 50mm
- Mode: MOPA color marking + vector cut

**Validation:** Tests: Line precision, circle roundness, corner sharpness, power consistency

---

### Test 2: Tree Of Life Kabbalah

**Difficulty:** medium

**Adobe Firefly Prompt:**
```
Kabbalistic Tree of Life diagram, ten sephirot connected by 22 paths, mystical Hebrew letters, sacred geometry, black background with golden glowing lines and nodes, esoteric symbolism, ornate border with intricate patterns, occult manuscript style, high detail
```

**Wisdom Theme:** _As above, so below; as below, so above_

**Manufacturing Specs:**
- Material: Anodized aluminum (black) or stainless steel
- Size: 75mm × 110mm
- Mode: MOPA deep engraving + color

**Validation:** Tests: Fine line detail, Hebrew letter legibility, depth consistency, complex pattern fidelity

---

### Test 3: Mandala Holographic

**Difficulty:** advanced

**Adobe Firefly Prompt:**
```
Intricate mandala with concentric circles, sacred lotus petals, Sri Yantra triangles at center, gradient from white center to deep black outer rings, smooth transitions, radial symmetry, 8-fold geometric patterns, meditative spiritual art, ultra detailed
```

**Wisdom Theme:** _Nothing rests; everything moves; everything vibrates_

**Manufacturing Specs:**
- Material: Stainless steel 304 polished
- Size: 80mm diameter circle
- Mode: MOPA diffraction grating

**Validation:** Tests: Gradient smoothness, diffraction color range, pitch accuracy, radial symmetry

---

## 🏔️ 2.5D Relief Tests

### Test 4: Hermetic Philosopher Portrait

**Difficulty:** advanced

**Adobe Firefly Prompt:**
```
Portrait of ancient Hermetic philosopher with long beard, wise eyes, wearing mystical robes covered in alchemical symbols, background with cosmic swirls and sacred geometry, dramatic side lighting casting shadows, Renaissance engraving style, high contrast grayscale for depth mapping, white=raised, black=deep cuts
```

**Key Points:**
- White = raised surface
- Black = deep cuts
- Smooth gradients for depth

**Manufacturing:**
- Material: Basswood, cherry, or MDF for testing
- Settings available in JSON file

---

### Test 5: Flower Of Life 3D Relief

**Difficulty:** medium

**Adobe Firefly Prompt:**
```
Flower of Life sacred geometry in 3D relief, overlapping circles appear to float at different depths, gradient shading from white peaks to gray valleys, subtle embossed effect, monochromatic, soft lighting, dimensional depth map, smooth gradients between circles
```

**Key Points:**
- White = raised surface
- Black = deep cuts
- Smooth gradients for depth

**Manufacturing:**
- Material: Aluminum 6061 or brass sheet
- Max Depth: 2mm
- Tool: Ball end 1/8" or V-bit 30°

---

## 🎡 3D Rotary Tests (4-Axis)

### Test 6: Guardian Totem Unwrapped

**Difficulty:** advanced

**Adobe Firefly Prompt:**
```
Unwrapped cylindrical texture map for totem pole carving, three stacked guardian spirits: eagle at top, bear in middle, raven at bottom, Pacific Northwest indigenous art style, bold black formlines on white background, traditional Haida design, geometric patterns between figures, 360° seamless wrap pattern, rectangular format (360° width × height), grayscale for depth
```

**⚠️ Critical:** Image must wrap seamlessly 360° (left edge = right edge)

**Workflow:**
1. Generate image in Firefly (panoramic aspect ratio)
2. Adjust contrast in Photoshop (black=deep, white=surface)
3. Run: `python image_to_relief.py "guardian_totem_unwrapped.jpg"`
4. Load G-code in OpenBuilds CONTROL
5. Mount cylinder on rotary axis
6. Run air pass (+10mm Z offset)
7. Run real pass

---

### Test 7: Alchemy Symbols Wrap

**Difficulty:** medium

**Adobe Firefly Prompt:**
```
Unwrapped texture for cylinder: alchemical symbols arranged in horizontal bands, mercury/sulfur/salt symbols, planetary glyphs, element symbols (🜂🜃🜁🜄), transmutation stages, medieval manuscript style, gold and black color scheme (gold=surface, black=carved), decorative borders between bands, seamless 360° wrap, grayscale depth map
```

**⚠️ Critical:** Image must wrap seamlessly 360° (left edge = right edge)

**Workflow:**
1. Generate image in Firefly (panoramic aspect ratio)
2. Adjust contrast in Photoshop (black=deep, white=surface)
3. Run: `python image_to_relief.py "your_image.jpg"`
4. Load G-code in OpenBuilds CONTROL
5. Mount cylinder on rotary axis
6. Run air pass (+10mm Z offset)
7. Run real pass

---

## 🚀 Quick Start Workflow

### For Each Test:

1. **Generate Art** (Adobe Firefly)
   - Copy prompt from above
   - Use specified aspect ratio
   - Download highest resolution

2. **Prepare Image** (Photoshop)
   - Convert to grayscale (if relief/rotary)
   - Adjust Levels/Curves for contrast
   - For depth maps: Black=deep, White=surface
   - Save as high-quality JPG or PNG

3. **Convert to G-code** (for CNC/Rotary)
   ```powershell
   python image_to_relief.py "your_image.jpg"
   ```

4. **Load in Software**
   - LightBurn: Import SVG/image, assign layers
   - OpenBuilds CONTROL: Load G-code
   - FreeCAD: Use macro for preview

5. **Test Run**
   - Frame/focus (laser) or air pass (CNC)
   - Run on scrap material first
   - Adjust settings based on results

## 📊 Validation Checklist

For each completed test piece:

- [ ] Dimensional accuracy (measure with caliper)
- [ ] Detail quality (magnifying glass inspection)
- [ ] Surface finish (smoothness, no chatter)
- [ ] Edge quality (clean cuts, no burrs)
- [ ] Depth consistency (if relief)
- [ ] Color/diffraction effect (if MOPA)
- [ ] 360° wrap alignment (if rotary)
- [ ] Photo documentation (before/after)

