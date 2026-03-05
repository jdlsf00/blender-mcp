# BlenderCAM Hardware Testing Workflow

## Overview

Complete end-to-end workflow for transitioning from BlenderCAM software validation to real-world hardware testing with MOPA fiber laser, diode laser, and 4-axis CNC router.

**Status**: Ready for hardware validation phase
**Last Updated**: 2025-11-13

---

## Phase 1: Software Validation ✅ COMPLETE

### 4-Axis Strategy Testing

- **HELIX**: ✅ Production-ready (99.96% A-axis density, 51 revolutions)
- **PARALLELR**: ⚠️ Sparse output (0.002% A-axis density, 1 command)
- **PARALLEL**: ❌ Division by zero error
- **CROSS**: ❌ List index out of range error

### Post-Processor Validation

All 4 post-processors tested and working:

| Post-Processor | File Extension | Format          | Line Numbers    | Status     |
| -------------- | -------------- | --------------- | --------------- | ---------- |
| **GRBL**       | `.gcode`       | Compact spacing | No              | ✅ Working |
| **ISO**        | `.tap`         | Spaced commands | Yes (N1, N2...) | ✅ Working |
| **EMC**        | `.ngc`         | Spaced commands | No              | ✅ Working |
| **MACH3**      | `.tap`         | Spaced commands | No              | ✅ Working |

All produce identical A-axis rotation: 0° → 18,355.233° (~51 revolutions)

### Automation Infrastructure

- ✅ `test_4axis_helix.py` - Multi-strategy testing with progress & CSV export
- ✅ `mcp_blendercam_validation.py` - MCP tool wrapper with JSON metrics
- ✅ `batch_test_runner.py` - Automated matrix testing + reports
- ✅ `BLENDERCAM_4AXIS_VALIDATION.md` - Comprehensive validation documentation

---

## Phase 2: Test Part Library ✅ COMPLETE

### Test Parts Generated

All parts exported to `test_parts/` directory:

#### **Level 1: TestCylinder_001** (Geometry Validation)

- **Dimensions**: 50mm diameter × 100mm length
- **Purpose**: Verify A-axis rotation accuracy, surface finish consistency
- **Recommended Strategy**: HELIX
- **Test Materials**: Scrap wood, aluminum, acrylic
- **Estimated Runtime**: 5-10 minutes
- **Files**: `TestCylinder_001.blend`, `TestCylinder_001_metadata.json`

#### **Level 2: TestCone_001** (Strategy Comparison)

- **Dimensions**: 50mm base → 20mm top × 100mm length
- **Purpose**: Compare HELIX vs PARALLELR on variable diameter
- **Recommended Strategies**: HELIX, PARALLELR
- **Test Materials**: Softwood, brass, HDPE
- **Estimated Runtime**: 8-15 minutes
- **Files**: `TestCone_001.blend`, `TestCone_001_metadata.json`

#### **Level 3: Test3DRelief_001** (Complex Geometry)

- **Dimensions**: 50mm diameter × 80mm length with 2mm displacement
- **Purpose**: Multi-pass depth control, 3D toolpath accuracy
- **Recommended Strategy**: HELIX
- **Test Materials**: Hardwood, stainless steel, leather
- **Estimated Runtime**: 20-45 minutes
- **Files**: `Test3DRelief_001.blend`, `Test3DRelief_001_metadata.json`

### Generation Script

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" `
  --background `
  --python "F:\Documents\CODE\Blender-MCP\test_part_generator_simple.py" `
  -- --part all
```

---

## Phase 3: Material Testing Database ✅ COMPLETE

### Database Structure

#### **JSON Schema** (`material_test_database.json`)

- Tool configurations (MOPA laser, diode laser, CNC router)
- Material templates with all parameters
- Photo path tracking for visual documentation

#### **CSV Templates** (Ready for data collection)

##### **MOPA Fiber Laser** (`material_tests_mopa_laser.csv`)

- **Pre-populated materials**: Stainless steel 304, Brass C360, Aluminum 6061-T6
- **Parameters**: Power (W), Speed (mm/s), Pulse width (ns), Frequency (kHz), Focus offset (mm)
- **Results**: Edge quality (1-5), Depth (mm), Color, HAZ (mm), Dimensional accuracy (mm), Success rating (1-5)
- **Recommended tests**: Color marking at 280ns pulse width, 20-80W power range

##### **Diode Laser** (`material_tests_diode_laser.csv`)

- **Pre-populated materials**: Pine wood, Oak wood, Acrylic, Leather
- **Parameters**: Power (%), Speed (mm/s), Passes, Focus offset (mm), Air assist
- **Results**: Burn depth (mm), Char width (mm), Edge sharpness (1-5), Smoke level, Dimensional accuracy (mm)
- **Recommended tests**: Focus offset critical (-2mm for acrylic cutting, -1mm for engraving)

##### **4-Axis CNC Router** (`material_tests_cnc_router.csv`)

- **Pre-populated materials**: Pine wood, Oak wood, Birch plywood, HDPE, Acrylic
- **Parameters**: Spindle RPM, Feed rate (mm/min), Plunge rate, Depth per pass, Cutter type/diameter/flutes, Coolant
- **Results**: Surface finish (1-5), Dimensional accuracy (mm), Edge quality (1-5), Chip evacuation, Tool wear
- **Recommended tests**: Start with 12,000-18,000 RPM, 1000-2500 mm/min feed rates

---

## Phase 4: Laser Test Patterns ✅ COMPLETE

### MOPA Fiber Laser Test Grid

#### **Pattern Details** (`MOPA_Test_Grid.blend`)

- **Grid**: 5×5 power/speed matrix = 25 test squares
- **Square Size**: 10mm × 10mm
- **Total Size**: 60mm × 60mm (including 2mm spacing)
- **Serial Numbers**: 1-25 (engraved on each square)
- **Power Range**: 20W, 35W, 50W, 65W, 80W (columns)
- **Speed Range**: 50, 87.5, 125, 162.5, 200 mm/s (rows)
- **Pulse Width**: 280ns (standard for color marking on stainless steel)
- **Frequency**: 30 kHz

#### **Recommended Test Material**

Stainless steel 304 (1.0mm thickness) for color marking exploration

#### **Generation Script**

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" `
  --background `
  --python "F:\Documents\CODE\Blender-MCP\mopa_test_pattern_generator.py"
```

Custom parameters:

```powershell
-- --power-min 20 --power-max 80 --speed-min 50 --speed-max 200
```

#### **Metadata** (`MOPA_Test_Grid_metadata.json`)

Complete grid map with serial numbers, power/speed values, and X/Y positions

---

### Diode Laser Gradation Test

#### **Pattern Details** (`Diode_Gradation_Test.blend`)

- **Design**: Star pattern (also available: text, circle, decorative)
- **Power Levels**: 10%, 30%, 50%, 70%, 90%
- **Spacing**: 20mm between designs
- **Total Width**: 80mm
- **Standard Speed**: 120 mm/s
- **Focus Offset**: -1.0mm (standard for wood engraving)

#### **Recommended Test Materials**

- Wood (pine or oak) - 6mm thickness
- Leather (full grain) - 2mm thickness
- Acrylic (clear) - 3mm thickness (adjust focus to -2mm)

#### **Generation Script**

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" `
  --background `
  --python "F:\Documents\CODE\Blender-MCP\diode_test_pattern_generator.py" `
  -- --design star
```

Design options: `--design star|text|circle|decorative`

#### **Metadata** (`Diode_Gradation_Test_metadata.json`)

Power levels, positions, and design names for each test copy

---

## Phase 5: G-code Simulation & Verification ✅ COMPLETE

### Installed Simulation Tools

#### **Candle - GRBL Sender & Visualizer** ⭐ RECOMMENDED

**Status**: Already installed at `F:\Documents\Candle\`

**Features**:

- 3D toolpath visualization
- G-code line-by-line preview
- 4-axis (XYZA) support
- Built-in GRBL sender for hardware control
- Free and open-source

**Best For**: Quick local verification of GRBL-formatted G-code

**Usage**:

```powershell
Start-Process "F:\Documents\Candle\Candle.exe"
# File → Open → Select helix_4axis_test_GRBL.gcode
# View → 3D View to see toolpath
```

---

#### **LightBurn - Laser Simulator**

**Status**: Already installed at `F:\Documents\Lightburn\`

**Best For**: MOPA/diode laser test pattern verification

**Usage**:

```powershell
Start-Process "F:\Documents\Lightburn\LightBurn.exe"
# Import MOPA_Test_Grid or Diode_Gradation_Test patterns
```

---

#### **FreeCAD Path Workbench**

**Status**: Already installed at `F:\Documents\FreeCAD\`

**Best For**: Alternative CAM workflow and engineering analysis

---

### Browser-Based Options (No Installation)

#### **NC Viewer** ⭐ FASTEST

**URL**: https://ncviewer.com

**Features**:

- Instant drag-and-drop G-code loading
- 4-axis visualization (A-axis support confirmed)
- Zero setup time
- Works on any device

**Best For**: Quick 30-second verification

---

#### **OpenBuilds CAM & Control**

**URL**: https://cam.openbuilds.com

**Features**:

- CAM + simulation in one tool
- GRBL-optimized

**Note**: Requires account signup

---

### Advanced Option: CAMotics

**Status**: Not currently installed (can be installed if needed)

**Key Features**:

- ✅ **3D material removal simulation** (realistic cutting preview)
- ✅ **Collision detection** (tool vs. workpiece)
- ✅ **STL workpiece import** (simulate on custom stock)
- ✅ **4-axis support** (XYZA rotary configuration)
- ✅ **Free and open-source**

**Installation**:

```powershell
# Download from official site
Start-Process "https://camotics.org/download.html"

# Or use package manager
winget install CAMotics.CAMotics
# or
choco install camotics
```

**When to Install**:

- Need collision detection before expensive material cuts
- Complex parts with tight tolerances
- Safety-critical operations
- Learning material removal mechanics

**Configuration** for 4-axis CNC: See `GCODE_SIMULATION_OPTIONS.md` for machine.xml setup

---

### Recommended Workflow

#### **Step 1: Quick Verification** (2 minutes)

```powershell
# Option A: NC Viewer (browser)
Start-Process "https://ncviewer.com"
# Drag & drop helix_4axis_test_GRBL.gcode

# Option B: Candle (local)
Start-Process "F:\Documents\Candle\Candle.exe"
# File → Open → helix_4axis_test_GRBL.gcode
```

**Verify**:

- ✅ Toolpath loads without errors
- ✅ A-axis rotation visible (0° → 18,355° / 51 revolutions)
- ✅ No obvious path errors

---

#### **Step 2: Material Removal Simulation** (5-10 minutes) - OPTIONAL

**Install CAMotics** if collision detection needed:

```powershell
# Download and install
Start-Process "https://camotics.org/download.html"

# Configure 4-axis machine profile
# Import G-code and run simulation
```

**Verify**:

- ✅ No tool collisions
- ✅ Material removal matches expected part
- ✅ A-axis rotation smooth

---

#### **Step 3: Laser Pattern Verification** (5 minutes)

```powershell
# For MOPA/Diode patterns
Start-Process "F:\Documents\Lightburn\LightBurn.exe"
# Import test patterns and verify power/speed settings
```

---

#### **Step 4: Air Cutting Test** (10 minutes) - SAFETY CRITICAL

**Before ANY material cutting**:

1. Load verified G-code into machine controller
2. Set Z-axis offset +50mm (tool above workpiece)
3. Run program at 100% speed
4. Visually verify:
   - ✅ No unexpected rapids
   - ✅ A-axis rotates smoothly (51 revolutions)
   - ✅ No machine alarms
   - ✅ Tool doesn't hit fixtures

**Only proceed to material cutting after air test passes.**

---

### Simulation Decision Matrix

| Scenario                      | Recommended Tool       | Reason                            |
| ----------------------------- | ---------------------- | --------------------------------- |
| **Quick 30-second check**     | NC Viewer (browser)    | Zero setup, instant results       |
| **Local verification**        | Candle                 | Already installed, GRBL-optimized |
| **Collision detection**       | CAMotics               | Material removal simulation       |
| **Laser patterns**            | LightBurn              | Laser-specific features           |
| **Before first hardware run** | Candle + Air cutting   | Multi-layer verification          |
| **Before expensive material** | CAMotics + Air cutting | Maximum safety validation         |

---

### Validation Checklist

Before hardware testing:

- [ ] G-code opens without errors in simulator
- [ ] Toolpath visualization correct
- [ ] 4-axis rotation: 0° → 18,355° (~51 revolutions)
- [ ] No collisions detected (if using CAMotics)
- [ ] Tool stays within work envelope
- [ ] Rapids are safe speeds
- [ ] Feed rates reasonable
- [ ] Air cutting test passed
- [ ] Safety equipment ready

---

**For complete simulation guide, see**: `GCODE_SIMULATION_OPTIONS.md`

---

## Phase 6: Next Steps (Ready to Execute)

### 5. Hardware Testing with Real Materials

#### Tasks

- Install CAMotics (free, open-source G-code simulator)
- Import HELIX G-code from `test_4axis_helix.py` output
- Configure 4-axis machine model (XYZA)
- Run simulation and verify:
  - ✅ No collisions between tool and part
  - ✅ Safe rapids (Z-axis clear before X/Y moves)
  - ✅ Correct work offsets (G54/G55)
  - ✅ A-axis rotation matches expected 51 revolutions
- Generate simulation report with screenshots

#### Air Cutting Test

Before running on hardware:

1. Load G-code into CNC controller
2. Set Z-axis offset +50mm (tool stays above stock)
3. Run program at 100% speed
4. Verify A-axis rotation visually
5. Check for unexpected rapids or crashes

---

### 5. FreeCAD Integration Bridge

**Status**: Not started
**Goal**: Compare BlenderCAM vs FreeCAD Path toolpaths

#### Tasks

- Create Python script to import `.blend` test parts into FreeCAD
- Configure FreeCAD Path Workbench for 4-axis
- Generate toolpath using FreeCAD Path operations
- Export FreeCAD G-code
- Side-by-side comparison:
  - Toolpath visualization (BlenderCAM vs FreeCAD)
  - G-code line count
  - A-axis command density
  - Estimated machining time
- Document pros/cons of each CAM system

---

### 6. Adobe Workflow Integration

**Status**: Not started
**Goal**: Streamline design → CAM pipeline using Creative Cloud tools

#### Workflows

##### **Illustrator → Blender (2D designs on cylinders)**

1. Create vector artwork in Illustrator
2. Export as SVG (Illustrator CC 2024 format)
3. Import SVG into Blender (File → Import → Scalable Vector Graphics)
4. Map SVG to cylinder surface (Array modifier + Curve modifier)
5. Generate G-code with BlenderCAM

##### **Photoshop → Blender (Texture mapping for 3D relief)**

1. Create texture/heightmap in Photoshop (grayscale, 16-bit depth)
2. Export as PNG or TIFF
3. Import as image texture in Blender
4. Apply to Displacement modifier on test part
5. Generate multi-pass 3D relief G-code

##### **Substance 3D (Material preview/rendering)**

1. Load test part `.obj` export into Substance 3D Painter
2. Apply wood grain, metal, or leather materials
3. Generate PBR textures (basecolor, normal, roughness)
4. Export to Blender for photorealistic rendering
5. Use renders for documentation and client presentations

---

## Hardware Testing Safety Protocol

### Pre-Flight Checklist (CRITICAL)

- [ ] G-code validated in CAMotics (no collisions)
- [ ] Air cutting test completed successfully (Z+50mm offset)
- [ ] Emergency stop button tested and within reach
- [ ] Work offsets verified (G54 X0 Y0 Z0 A0)
- [ ] Tool/cutter securely mounted (check runout)
- [ ] Stock material secured (clamps, rotary chuck pressure)
- [ ] Safety glasses/face shield worn
- [ ] Fire extinguisher nearby (for laser operations)
- [ ] Ventilation/fume extraction active (for lasers)

### Laser Safety (MOPA & Diode)

- **Never** look at laser reflection or beam path
- Use laser safety glasses (wavelength-specific: 1064nm for MOPA, 445nm for diode)
- Ensure laser enclosure interlocks functional
- Test material flammability in isolation first
- Keep work area clear of flammable materials
- Monitor first pass continuously (watch for smoke/flames)

### CNC Router Safety (4-Axis)

- Verify A-axis rotation direction (CW/CCW)
- Check for tool collisions during simulation
- Start with very conservative feeds/speeds
- Listen for unusual sounds (chatter, squealing)
- Check chip evacuation (avoid chip welding/packing)
- Stop immediately if vibration increases

---

## Material Testing Workflow

### Step 1: Geometry Validation (TestCylinder_001)

**Goal**: Verify A-axis rotation accuracy on cheap material

1. Use scrap wood or cheap plastic
2. Generate G-code with HELIX strategy
3. Run air cutting test (Z+50mm)
4. If safe, lower to stock and run at 50% speed
5. Measure diameter accuracy (±0.1mm tolerance)
6. Inspect surface finish (should be smooth, no chatter)
7. **Record results** in appropriate CSV file

### Step 2: Strategy Comparison (TestCone_001)

**Goal**: Compare HELIX vs PARALLELR on variable diameter

1. Use softwood (pine) or HDPE
2. Generate 2 G-code versions:
   - `TestCone_HELIX.gcode`
   - `TestCone_PARALLELR.gcode`
3. Run both on same material
4. Compare:
   - Surface finish (which is smoother?)
   - Machining time (which is faster?)
   - Dimensional accuracy (measure both diameters)
5. **Record results** with photos

### Step 3: Laser Parameter Discovery

**Goal**: Find optimal power/speed for each material

#### MOPA Laser (Stainless Steel)

1. Mount stainless steel sample (1.0mm thickness)
2. Load `MOPA_Test_Grid.gcode` (generated from .blend file)
3. Run test grid at 280ns pulse width
4. Inspect all 25 squares:
   - Identify color changes (Square #1 = 20W/50mm/s, #25 = 80W/200mm/s)
   - Find "sweet spot" for desired marking style
5. **Record results** with macro photos of grid

#### Diode Laser (Wood/Leather)

1. Mount wood sample (6mm pine)
2. Load `Diode_Gradation_Test.gcode` (generated from .blend file)
3. Run gradation test at 120 mm/s speed
4. Inspect all 5 power levels:
   - 10% (barely visible)
   - 30% (light engraving)
   - 50% (medium depth)
   - 70% (dark engraving)
   - 90% (very deep, possible burn-through)
5. **Record results** with close-up photos

### Step 4: Complex Geometry (Test3DRelief_001)

**Goal**: Validate multi-pass 3D toolpath accuracy

1. Use quality material (hardwood, stainless steel, or leather)
2. Generate G-code with HELIX strategy
3. **Critical**: Set depth per pass conservatively (0.5-1.0mm)
4. Run first pass and inspect:
   - Depth accuracy (measure with calipers)
   - Surface finish (should show wave pattern)
5. Complete all passes if first pass successful
6. **Record results** with before/after photos

---

## Results Documentation

### Photo Guidelines

- Use macro lens or smartphone macro mode
- Include ruler/scale in frame for size reference
- Take multiple angles: top, side, close-up
- Use good lighting (diffused, no harsh shadows)
- Filename format: `MaterialName_TestPart_PowerSpeed_Date.jpg`
  - Example: `SS304_Square12_50W_125mms_2025-01-13.jpg`

### CSV Data Entry

- Fill out CSV templates after each test
- Rate quality on 1-5 scale (1=poor, 5=excellent)
- **Edge Quality**: Sharpness, no burrs, clean transitions
- **Surface Finish**: Smoothness, no chatter marks, consistent texture
- **Success Rating**: Overall result (1=failed, 5=perfect production-ready)
- Include detailed notes (e.g., "slight burn on corners", "perfect mirror finish")

### Material Cost Tracking

- Record supplier and cost per piece
- Track cumulative test costs
- Identify "sweet spot" materials (good results, low cost)

---

## File Organization

```
Blender-MCP/
├── test_parts/                          # ✅ Generated test parts
│   ├── TestCylinder_001.blend
│   ├── TestCylinder_001_metadata.json
│   ├── TestCone_001.blend
│   ├── TestCone_001_metadata.json
│   ├── Test3DRelief_001.blend
│   └── Test3DRelief_001_metadata.json
│
├── laser_test_patterns/                 # ✅ Generated laser patterns
│   ├── MOPA_Test_Grid.blend
│   ├── MOPA_Test_Grid_metadata.json
│   ├── Diode_Gradation_Test.blend
│   └── Diode_Gradation_Test_metadata.json
│
├── material_test_database.json          # ✅ Database schema
├── material_tests_mopa_laser.csv        # ✅ MOPA results tracking
├── material_tests_diode_laser.csv       # ✅ Diode results tracking
├── material_tests_cnc_router.csv        # ✅ CNC results tracking
│
├── test_4axis_helix.py                  # ✅ Multi-strategy testing
├── mcp_blendercam_validation.py         # ✅ MCP wrapper
├── batch_test_runner.py                 # ✅ Automated testing
├── test_part_generator_simple.py        # ✅ Test part generator
├── mopa_test_pattern_generator.py       # ✅ MOPA pattern generator
├── diode_test_pattern_generator.py      # ✅ Diode pattern generator
│
└── BLENDERCAM_4AXIS_VALIDATION.md       # ✅ Software validation report
└── HARDWARE_TESTING_WORKFLOW.md         # ✅ This document
```

---

## Resources & References

### BlenderCAM Documentation

- Fabex fork: https://github.com/vilemduha/blendercam
- 4-axis strategies: HELIX (production-ready), PARALLELR (experimental)

### Simulation Tools

- **CAMotics**: Free G-code simulator (https://camotics.org/)
- **Vericut**: Commercial 5-axis simulator (expensive, but industry-standard)

### Material Testing Resources

- **MOPA Laser**: Material libraries at https://www.raycuslaser.com/material-library/
- **Diode Laser**: Speed/power charts at https://www.lightburnsoftware.com/
- **CNC Router**: Feeds/speeds calculator at https://www.precisebits.com/calc.htm

### Safety Standards

- **Laser Safety**: ANSI Z136.1 (American National Standard for Safe Use of Lasers)
- **CNC Safety**: OSHA 1910 Subpart O (Machinery and Machine Guarding)

---

## Troubleshooting

### CNC Router Issues

**Problem**: Chatter marks on surface
**Solution**: Reduce spindle RPM by 20%, increase feed rate slightly

**Problem**: A-axis not rotating
**Solution**: Check G-code for A-axis commands (`grep "A[0-9]" file.gcode`), verify post-processor

**Problem**: Tool crashes into stock
**Solution**: Re-verify work offsets (G54), run air cutting test first

### MOPA Laser Issues

**Problem**: No visible marking
**Solution**: Increase power or reduce speed, check focus position

**Problem**: Burning through material
**Solution**: Reduce power by 30%, increase speed by 50%

**Problem**: Inconsistent color marking
**Solution**: Verify pulse width at 280ns, clean lens, check material cleanliness

### Diode Laser Issues

**Problem**: Smoke/flames during cutting
**Solution**: Enable air assist, reduce power, increase speed

**Problem**: Uneven engraving depth
**Solution**: Check focus offset (should be -1mm to -2mm), verify material flatness

**Problem**: Burn-through on thin materials
**Solution**: Reduce power to 30-50%, use multiple light passes instead of single heavy pass

---

## Version History

**v1.0** - 2025-11-13

- Initial documentation
- Software validation complete (HELIX strategy production-ready)
- Test part library generated (3 complexity levels)
- Material testing database created (JSON + CSV templates)
- Laser test patterns generated (MOPA 5×5 grid, Diode gradation test)
- Ready for hardware validation phase

---

## Contact & Support

For issues with BlenderCAM or hardware integration, consult:

- BlenderCAM GitHub Issues: https://github.com/vilemduha/blendercam/issues
- CNC Zone 4-axis forum: https://www.cnczone.com/forums/4-axis-cnc-machines/
- Laser engraving communities: r/lasercutting, r/laserengraving

**IMPORTANT**: Always prioritize safety. When in doubt, stop the machine and consult an expert.

---

_"The best machinist is the one who knows when to stop and ask for help."_
