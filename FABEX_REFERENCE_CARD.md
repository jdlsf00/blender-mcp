# 🎯 Fabex 4-Axis Quick Reference Card

## Project Info

- **File**: 4axis_helix_reference.blend
- **Object**: TestCylinder_Helix (50mm × 100mm)
- **Goal**: Generate corrected G-code with proper scale

---

## ✅ Critical Checks

### 1. Units (Scene Properties)

```
Unit System: Metric ✓
Length: Millimeters ✓
Unit Scale: 1.0 ✓
```

### 2. Fabex Panel Access

```
Press N → Click "Fabex CNC" tab
```

### 3. Machine Settings

```
Post-Processor: grbl
X: -400 to 400 mm
Y: -400 to 400 mm
Z: -150 to 50 mm
A: Rotary (unlimited)
```

### 4. Tool Settings

```
Type: End Mill
Diameter: 6 mm
Flutes: 4
Feed Rate: 500 mm/min
Spindle: 12000 RPM
Plunge: 250 mm/min
```

### 5. Operation Settings

```
Strategy: 4-Axis / Rotary / Helix
Object: TestCylinder_Helix
Step Over: 3 mm
Step Down: 3 mm
Clearance: 10 mm
```

---

## 📋 Workflow

1. ✅ Verify units (CRITICAL!)
2. ✅ Open Fabex panel (Press N)
3. ✅ Add operation
4. ✅ Select strategy (4-axis/rotary)
5. ✅ Select geometry (TestCylinder_Helix)
6. ✅ Configure machine (XYZA limits)
7. ✅ Configure tool (6mm end mill)
8. ✅ Set parameters (step over/down)
9. ✅ Calculate path (wait 30-60s)
10. ✅ Export G-code (save to reference_projects/)
11. ✅ Validate (run validate_gcode.ps1)

---

## 🔍 Expected Output

**File**: blender_helix_reference.gcode

**Coordinates (CORRECT)**:

```gcode
G21              ; Millimeters
G00 X-49.968     ; ~50mm (NOT 50,000mm!)
G01 Y25.000      ; ~25mm radius
G01 A18355.000   ; ~51 rotations
```

**Coordinates (WRONG - like original)**:

```gcode
G00 X-49968.17   ; 50 METERS! ❌
G01 Z8000        ; 8 METERS! ❌
```

---

## 🚨 Validation Command

```powershell
cd F:\Documents\CODE\Blender-MCP
.\validate_gcode.ps1 -GCodePath "reference_projects\blender_helix_reference.gcode"
```

**Expected**: ✅ All checks pass, coordinates ~50mm range

---

## ⚠️ Troubleshooting Quick Fixes

| Issue              | Fix                                            |
| ------------------ | ---------------------------------------------- |
| No "Fabex CNC" tab | Press N, or enable in Preferences → Extensions |
| No 4-axis option   | Try "Rotary" or "Parallel" strategy            |
| Scale still wrong  | Check Scene Properties → Units → Scale = 1.0   |
| Calculation fails  | Check Console (Window → Toggle System Console) |
| No A-axis          | Enable in Machine settings, set Type = Rotary  |

---

## 📞 When You Need Help

**Share with me:**

1. Screenshot of Fabex panel
2. Console errors (Window → Toggle System Console)
3. What step you're stuck on

**Files**: F:\Documents\CODE\Blender-MCP\

- QUICK_START_FABEX.md (detailed guide)
- VALIDATION_CHECKLIST.md (full checklist)
- validate_gcode.ps1 (validation script)

---

**🚀 You've got this! Follow the steps and validate the output.**
